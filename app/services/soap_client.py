import logging
from zeep import Client
from zeep.exceptions import Fault, TransportError

SOAP_WSDL_URL = "http://localhost:8001/?wsdl"

logger = logging.getLogger(__name__)

def calculate_recipe_energy(appliance: str, time_minutes: int) -> dict:
    try:
        client = Client(SOAP_WSDL_URL)
        response = client.service.calculate_energy(
            appliance=appliance,
            time_minutes=time_minutes
        )
        return {
            "kwh": float(response.kwh),
            "co2_kg": float(response.co2_kg),
            "cost_eur": float(response.cost_eur)
        }
    except (TransportError, Fault) as e:
        logger.error(f"SOAP Service error: {e}")
        return {
            "kwh": 0.0,
            "co2_kg": 0.0,
            "cost_eur": 0.0,
            "error": "SOAP service unavailable"
        }