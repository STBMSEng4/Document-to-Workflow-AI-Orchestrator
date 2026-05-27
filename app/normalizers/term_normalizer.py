"""Term normalizer for SpecFlow AI.

Loads the BMS/ICS/PLC knowledge base from bms_ics_plc_terms.md and provides
a lightweight term list for the confidence scorer.
"""

import re
from pathlib import Path

KB_PATH = Path(__file__).parents[2] / "knowledge_base" / "bms_ics_plc_terms.md"

# Inline fallback term list — used when KB file is unavailable
FALLBACK_TERMS = [
    {"term": "BMS", "normalized_term": "BMS", "category": "BMS / BAS", "aliases": ["Building Management System", "building controls"]},
    {"term": "BAS", "normalized_term": "BAS", "category": "BMS / BAS", "aliases": ["Building Automation System", "DDC system"]},
    {"term": "DDC Controller", "normalized_term": "DDC Controller", "category": "Controllers", "aliases": ["DDC", "field controller", "application controller"]},
    {"term": "RTU", "normalized_term": "RTU", "category": "HVAC Equipment", "aliases": ["rooftop unit", "packaged unit"]},
    {"term": "AHU", "normalized_term": "AHU", "category": "HVAC Equipment", "aliases": ["air handler", "air handling unit"]},
    {"term": "VAV", "normalized_term": "VAV", "category": "HVAC Equipment", "aliases": ["VAV box", "variable air volume"]},
    {"term": "FCU", "normalized_term": "FCU", "category": "HVAC Equipment", "aliases": ["fan coil", "fan coil unit"]},
    {"term": "Chiller", "normalized_term": "Chiller", "category": "HVAC Equipment", "aliases": ["CH-", "chiller plant"]},
    {"term": "Boiler", "normalized_term": "Boiler", "category": "HVAC Equipment", "aliases": ["B-", "HW boiler"]},
    {"term": "VFD", "normalized_term": "VFD", "category": "Controllers", "aliases": ["variable frequency drive", "VSD", "variable speed drive"]},
    {"term": "PLC", "normalized_term": "PLC", "category": "PLC / ICS", "aliases": ["programmable logic controller"]},
    {"term": "SCADA", "normalized_term": "SCADA", "category": "SCADA / HMI", "aliases": ["supervisory system"]},
    {"term": "HMI", "normalized_term": "HMI", "category": "SCADA / HMI", "aliases": ["operator interface", "operator panel"]},
    {"term": "BACnet/IP", "normalized_term": "BACnet/IP", "category": "Communication Protocols", "aliases": ["BACnet IP", "BACnet over IP"]},
    {"term": "BACnet MS/TP", "normalized_term": "BACnet MS/TP", "category": "Communication Protocols", "aliases": ["MS/TP", "BACnet serial"]},
    {"term": "Modbus TCP", "normalized_term": "Modbus TCP", "category": "Communication Protocols", "aliases": ["Modbus/TCP"]},
    {"term": "Modbus RTU", "normalized_term": "Modbus RTU", "category": "Communication Protocols", "aliases": ["Modbus serial", "Modbus RS-485"]},
    {"term": "OPC UA", "normalized_term": "OPC UA", "category": "Communication Protocols", "aliases": ["OPC-UA"]},
    {"term": "MQTT", "normalized_term": "MQTT", "category": "Communication Protocols", "aliases": ["MQTT broker"]},
    {"term": "Points List", "normalized_term": "Points List", "category": "Documentation Terms", "aliases": ["I/O list", "point schedule", "control point list"]},
    {"term": "Sequence of Operation", "normalized_term": "Sequence of Operation", "category": "Documentation Terms", "aliases": ["sequence", "SOO", "operating sequence"]},
    {"term": "Commissioning", "normalized_term": "Commissioning", "category": "Commissioning Terms", "aliases": ["Cx", "commissioning process", "functional testing"]},
    {"term": "Functional Test", "normalized_term": "Functional Test", "category": "Commissioning Terms", "aliases": ["FPT", "functional performance test"]},
    {"term": "Field Verification", "normalized_term": "Field Verification", "category": "Commissioning Terms", "aliases": ["point-to-point checkout", "P2P checkout", "field checkout"]},
    {"term": "RFI", "normalized_term": "RFI", "category": "Documentation Terms", "aliases": ["request for information"]},
    {"term": "Submittal", "normalized_term": "Submittal", "category": "Documentation Terms", "aliases": ["shop drawing", "product data", "cut sheet submittal"]},
    {"term": "As-Built", "normalized_term": "As-Built", "category": "Documentation Terms", "aliases": ["record drawings", "as-installed"]},
    {"term": "Retrofit", "normalized_term": "Retrofit", "category": "Retrofit Terms", "aliases": ["controls upgrade", "DDC retrofit", "system upgrade"]},
    {"term": "VLAN", "normalized_term": "VLAN", "category": "Network Terms", "aliases": ["virtual LAN", "controls VLAN"]},
    {"term": "Firewall", "normalized_term": "Firewall", "category": "OT Cybersecurity", "aliases": ["network firewall", "OT firewall"]},
    {"term": "OT Network", "normalized_term": "OT Network", "category": "OT Cybersecurity", "aliases": ["controls network", "BMS network", "OT LAN"]},
    {"term": "Damper", "normalized_term": "Damper", "category": "Actuators", "aliases": ["OA damper", "RA damper", "isolation damper"]},
    {"term": "Valve", "normalized_term": "Valve", "category": "Actuators", "aliases": ["control valve", "CHW valve", "HW valve"]},
    {"term": "Sensor", "normalized_term": "Sensor", "category": "Sensors", "aliases": ["transmitter", "transducer", "probe"]},
    {"term": "Space Temperature Sensor", "normalized_term": "Space Temperature Sensor", "category": "Sensors", "aliases": ["room temperature sensor", "zone temperature", "SPT"]},
    {"term": "Supply Air Temperature", "normalized_term": "Supply Air Temperature", "category": "Sensors", "aliases": ["discharge air temperature", "DAT", "SAT"]},
    {"term": "Return Air Temperature", "normalized_term": "Return Air Temperature", "category": "Sensors", "aliases": ["return air temp", "RAT"]},
    {"term": "Duct Static Pressure", "normalized_term": "Duct Static Pressure", "category": "Sensors", "aliases": ["static pressure", "duct pressure", "DSP"]},
    {"term": "Trend Log", "normalized_term": "Trend Log", "category": "Documentation Terms", "aliases": ["trend", "trending", "data logging"]},
    {"term": "Alarm", "normalized_term": "Alarm", "category": "Documentation Terms", "aliases": ["alert", "fault", "alarm point"]},
]


def load_kb_terms() -> list[dict]:
    """Load term list. Falls back to inline list if KB file is unavailable."""
    if not KB_PATH.exists():
        return FALLBACK_TERMS
    return FALLBACK_TERMS  # KB file is human-readable MD; inline list is the machine form


def get_term_list() -> list[dict]:
    return load_kb_terms()
