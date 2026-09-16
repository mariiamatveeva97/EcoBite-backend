import httpx
from lxml import etree
from fastapi import HTTPException, status

from app.core.config import settings

_NAMESPACE = "http://example.com/energy"  # SOAP_service namespace

_SOAP_NS = {"soap": "http://www.w3.org/2003/05/soap-envelope"}

def calculate_energy_metrics(
    appliance: str,
    cooking_time_minutes: int,
    servings: int,
    temperature_celsius: int = 200,
    power_setting: str = "medium",
) -> dict:
    return _mock_calculate(appliance, cooking_time_minutes, servings, power_setting)

def _mock_calculate(appliance: str, time_minutes: int, servings: int, power: str) -> dict:
    power_factor = {"low": 0.7, "medium": 1.0, "high": 1.4}.get(power, 1.0)
    appliance_kwh_per_minute = {
        "stove": 0.03,
        "oven": 0.05,
        "microwave": 0.02,
    }.get(appliance, 0.03)

    estimated_kwh = round(appliance_kwh_per_minute * time_minutes * power_factor, 2)
    co2_impact_grams = round(estimated_kwh * 400, 1)
    estimated_cost_eur = round(estimated_kwh * 0.30, 2)

    if estimated_kwh < 0.3:
        label = "A"
    elif estimated_kwh < 0.6:
        label = "B"
    elif estimated_kwh < 1.0:
        label = "C"
    elif estimated_kwh < 1.5:
        label = "D"
    else:
        label = "E"

    return {
        "estimated_kwh": estimated_kwh,
        "co2_impact_grams": co2_impact_grams,
        "energy_efficiency_label": label,
        "estimated_cost_eur": estimated_cost_eur,
    }


def _build_request_xml(appliance, time_minutes, temp, power, servings) -> bytes:
    root = etree.Element("EnergyRequest")
    etree.SubElement(root, "kitchen_appliance").text = appliance
    etree.SubElement(root, "cooking_time_minutes").text = str(time_minutes)
    etree.SubElement(root, "temperature_celsius").text = str(temp)
    etree.SubElement(root, "power_setting").text = power
    etree.SubElement(root, "servings").text = str(servings)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8")


def _parse_response_xml(xml_content: bytes) -> dict:
    try:
        root = etree.fromstring(xml_content)
        return {
            "estimated_kwh": float(root.findtext("estimated_kwh")),
            "co2_impact_grams": float(root.findtext("co2_impact_grams")),
            "energy_efficiency_label": root.findtext("energy_efficiency_label"),
            "estimated_cost_eur": float(root.findtext("estimated_cost_eur")),
        }
    except (etree.XMLSyntaxError, TypeError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to parse SOAP response: {str(e)}"
        )

def _check_soap_fault(root: etree._Element) -> None:
    fault = root.find(".//soap:Fault", namespaces=_SOAP_NS)
    if fault is None:
        return

    fault_code = fault.findtext("faultcode") or "Unknown"
    fault_string = fault.findtext("faultstring") or "No details provided"

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"SOAP service returned a fault [{fault_code}]: {fault_string}"
    )