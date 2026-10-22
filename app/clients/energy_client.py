import logging
from typing import Optional

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)

# Een eerste aanroep van een Consumption-workflow kan traag starten, en de gateway zit
# ertussen. Ruim boven 5 s, maar ver onder de 120 s van het platform.
TIMEOUT_SECONDS = 30.0


def calculate_energy_metrics(
    appliance: str,
    cooking_time_minutes: int,
    power_setting: Optional[str] = None,
) -> dict:
    if not settings.ENERGY_WORKFLOW_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ENERGY_WORKFLOW_URL is not configured",
        )

    payload = {"appliance": appliance, "time_minutes": cooking_time_minutes}
    if power_setting:
        payload["power_setting"] = power_setting

    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response = client.post(settings.ENERGY_WORKFLOW_URL, json=payload)
    except httpx.TimeoutException as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Energy workflow timed out ({type(e).__name__})",
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Energy workflow unreachable ({type(e).__name__})",
        )

    if response.status_code != 200:
        # Bijvoorbeeld 429 van de gateway, of 400/502 van de workflow.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Energy workflow returned HTTP {response.status_code}",
        )

    return _parse_response(response)


def _parse_response(response: httpx.Response) -> dict:
    try:
        data = response.json()
        return {
            "estimated_kwh": float(data["estimated_kwh"]),
            "co2_impact_grams": float(data["co2_impact_grams"]),
            "energy_efficiency_label": str(data["energy_efficiency_label"]),
            "estimated_cost_eur": float(data["estimated_cost_eur"]),
        }
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid energy workflow response ({type(e).__name__})",
        )