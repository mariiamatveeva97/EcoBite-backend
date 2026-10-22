import json

import httpx
import pytest
from fastapi import HTTPException

from app.clients import energy_client
from app.core.config import settings

GOOD_BODY = {
    "estimated_kwh": 1.0,
    "co2_impact_grams": 400.0,
    "energy_efficiency_label": "D",
    "estimated_cost_eur": 0.3,
}


@pytest.fixture(autouse=True)
def workflow_url(monkeypatch):
    monkeypatch.setattr(settings, "ENERGY_WORKFLOW_URL", "https://gateway.test/energy")


def use_handler(monkeypatch, handler):
    """Vervang de echte HTTP-aanroep door een handler: niets verlaat het proces."""
    real_client = httpx.Client
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        energy_client.httpx, "Client", lambda **kw: real_client(transport=transport, **kw)
    )


def test_energy_client_reads_four_fields(monkeypatch):
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json=GOOD_BODY)

    use_handler(monkeypatch, handler)

    result = energy_client.calculate_energy_metrics("oven", 20)

    assert result == GOOD_BODY
    assert seen["body"] == {"appliance": "oven", "time_minutes": 20}


def test_energy_client_429_raises_http_exception(monkeypatch):
    use_handler(monkeypatch, lambda request: httpx.Response(429))

    with pytest.raises(HTTPException) as exc:
        energy_client.calculate_energy_metrics("oven", 20)

    assert exc.value.status_code == 502
    assert "429" in exc.value.detail


def test_energy_client_timeout_raises_504(monkeypatch):
    def handler(request):
        raise httpx.ReadTimeout("timeout", request=request)

    use_handler(monkeypatch, handler)

    with pytest.raises(HTTPException) as exc:
        energy_client.calculate_energy_metrics("oven", 20)

    assert exc.value.status_code == 504


def test_energy_client_missing_field_raises_502(monkeypatch):
    use_handler(monkeypatch, lambda request: httpx.Response(200, json={"estimated_kwh": 1.0}))

    with pytest.raises(HTTPException) as exc:
        energy_client.calculate_energy_metrics("oven", 20)

    assert exc.value.status_code == 502