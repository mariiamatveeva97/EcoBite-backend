import logging
import httpx
from lxml import etree
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)

def calculate_energy_metrics(
    appliance: str,
    cooking_time_minutes: int,
    servings: int = 1,
    temperature_celsius: int = 200,
    power_setting: str = "medium",
) -> dict:
    try:
        xml_body = _build_request_xml(appliance, cooking_time_minutes)

        with httpx.Client(timeout=5.0) as client:
            response = client.post(
                settings.SOAP_SERVICE_URL,
                content=xml_body,
                headers={"Content-Type": "text/xml; charset=utf-8"}
            )

        if response.status_code == 200:
            _check_soap_fault(etree.fromstring(response.content))
            return _parse_response_xml(response.content)

        logger.warning(f"SOAP service returned HTTP {response.status_code}. Using fallback mock.")
        return _mock_calculate(appliance, cooking_time_minutes, servings, power_setting)
    except (httpx.RequestError, httpx.TimeoutException) as e:
        logger.warning(f"SOAP network/transport error ({e}). Falling back to mock calculation.")
        return _mock_calculate(appliance, cooking_time_minutes, servings, power_setting)

def _build_request_xml(appliance: str, time_minutes: int) -> bytes:
    envelope = etree.Element(
        "{http://schemas.xmlsoap.org/soap/envelope/}Envelope",
        nsmap={
            "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
            "spy": "ecobite.energy.soap",
        }
    )
    etree.SubElement(envelope, "{http://schemas.xmlsoap.org/soap/envelope/}Header")
    body = etree.SubElement(envelope, "{http://schemas.xmlsoap.org/soap/envelope/}Body")

    calc = etree.SubElement(body, "{ecobite.energy.soap}calculate_energy")
    etree.SubElement(calc, "{ecobite.energy.soap}appliance").text = str(appliance)
    etree.SubElement(calc, "{ecobite.energy.soap}time_minutes").text = str(time_minutes)

    return etree.tostring(envelope, xml_declaration=True, encoding="UTF-8")

def _parse_response_xml(xml_content: bytes) -> dict:
    try:
        root = etree.fromstring(xml_content)
        kwh = float(root.xpath("//*[local-name()='kwh']/text()")[0])
        co2_kg = float(root.xpath("//*[local-name()='co2_kg']/text()")[0])
        cost_eur = float(root.xpath("//*[local-name()='cost_eur']/text()")[0])
        return {
            "estimated_kwh": kwh,
            "co2_impact_grams": round(co2_kg * 1000, 1),
            "energy_efficiency_label": _calculate_label(kwh),
            "estimated_cost_eur": cost_eur,
        }
    except (etree.XMLSyntaxError, IndexError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to parse SOAP response: {str(e)}"
        )

def _check_soap_fault(root: etree._Element) -> None:
    fault = root.xpath("//*[local-name()='Fault']")
    if fault:
        fault_code = root.xpath("//*[local-name()='faultcode']/text()")
        fault_str = root.xpath("//*[local-name()='faultstring']/text()")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SOAP Fault [{fault_code[0] if fault_code else 'Err'}]: {fault_str[0] if fault_str else 'Unknown'}"
        )

def _calculate_label(kwh: float) -> str:
    if kwh < 0.3:
        return "A"
    elif kwh < 0.6:
        return "B"
    elif kwh < 1.0:
        return "C"
    elif kwh < 1.5:
        return "D"
    return "E"

def _mock_calculate(appliance: str, time_minutes: int, servings: int, power: str) -> dict:
    power_factor = {"low": 0.7, "medium": 1.0, "high": 1.4}.get(power, 1.0)
    appliance_kwh_per_minute = {
        "stove": 0.03,
        "oven": 0.05,
        "microwave": 0.02,
        "airfryer": 0.025,
    }.get(appliance, 0.03)
    estimated_kwh = round(appliance_kwh_per_minute * time_minutes * power_factor, 2)
    return {
        "estimated_kwh": estimated_kwh,
        "co2_impact_grams": round(estimated_kwh * 400, 1),
        "energy_efficiency_label": _calculate_label(estimated_kwh),
        "estimated_cost_eur": round(estimated_kwh * 0.30, 2),
    }