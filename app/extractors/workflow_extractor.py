"""Workflow extraction engine for SpecFlow AI.

Converts source-confirmed scored terms and triggered templates into structured
engineering deliverables: points-list candidates, RFI items, field-verification
checklists, CAD tasks, submittal items, and commissioning checklists.

All output is source-driven — items are generated only when the triggering
equipment or signal term is confirmed in the source document above threshold.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PointCandidate:
    equipment: str
    point_name: str
    abbreviation: str
    io_type: str          # AI / AO / DI / DO / Setpoint / Status
    engineering_unit: str
    description: str
    confidence: float
    source_type: str      # "source_extracted" | "template_default" | "inferred"


@dataclass
class RFIItem:
    equipment: str
    rfi_number: str
    question: str
    priority: str         # High / Medium / Low
    template: str
    confidence: float


@dataclass
class FieldVerificationItem:
    equipment: str
    task: str
    category: str         # Sensor / Wiring / Network / Mechanical / Software
    template: str


@dataclass
class CxItem:
    equipment: str
    test_name: str
    description: str
    category: str         # Functional / Setpoint / Alarm / Trend
    template: str


@dataclass
class WorkflowOutput:
    points: list[PointCandidate] = field(default_factory=list)
    rfis: list[RFIItem] = field(default_factory=list)
    field_verifications: list[FieldVerificationItem] = field(default_factory=list)
    cx_items: list[CxItem] = field(default_factory=list)
    cad_tasks: list[str] = field(default_factory=list)
    submittal_items: list[str] = field(default_factory=list)
    summary: str = ""
    triggered_templates: list[str] = field(default_factory=list)
    source_equipment: list[str] = field(default_factory=list)
    source_protocols: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Equipment template library
# ---------------------------------------------------------------------------

_POINTS: dict[str, list[dict]] = {
    "RTU": [
        {"name": "Supply Air Temperature",         "abbr": "SAT",        "io": "AI",       "unit": "°F",    "desc": "Discharge air temperature sensor"},
        {"name": "Supply Air Temperature Setpoint", "abbr": "SAT-SP",    "io": "SP",       "unit": "°F",    "desc": "Occupied cooling/heating setpoint"},
        {"name": "Return Air Temperature",          "abbr": "RAT",        "io": "AI",       "unit": "°F",    "desc": "Return air plenum sensor"},
        {"name": "Outdoor Air Temperature",         "abbr": "OAT",        "io": "AI",       "unit": "°F",    "desc": "Outdoor ambient sensor"},
        {"name": "Compressor Stage 1 Command",      "abbr": "COMP1-CMD",  "io": "DO",       "unit": "On/Off","desc": "Stage 1 compressor enable"},
        {"name": "Compressor Stage 2 Command",      "abbr": "COMP2-CMD",  "io": "DO",       "unit": "On/Off","desc": "Stage 2 compressor enable"},
        {"name": "Compressor Stage 1 Status",       "abbr": "COMP1-STS",  "io": "DI",       "unit": "On/Off","desc": "Stage 1 run status feedback"},
        {"name": "Compressor Stage 2 Status",       "abbr": "COMP2-STS",  "io": "DI",       "unit": "On/Off","desc": "Stage 2 run status feedback"},
        {"name": "Supply Fan Command",              "abbr": "SF-CMD",     "io": "DO",       "unit": "On/Off","desc": "Supply fan start/stop command"},
        {"name": "Supply Fan Status",               "abbr": "SF-STS",     "io": "DI",       "unit": "On/Off","desc": "Supply fan current status via current switch or VFD"},
        {"name": "Supply Fan VFD Speed",            "abbr": "SF-SPD",     "io": "AO",       "unit": "%",     "desc": "VFD speed reference (0–100%)"},
        {"name": "Heating Stage 1 Command",         "abbr": "HTG1-CMD",   "io": "DO",       "unit": "On/Off","desc": "Heat stage 1 enable"},
        {"name": "Heating Stage 2 Command",         "abbr": "HTG2-CMD",   "io": "DO",       "unit": "On/Off","desc": "Heat stage 2 enable"},
        {"name": "Economizer Damper Position",      "abbr": "ECON-POS",   "io": "AO",       "unit": "%",     "desc": "Economizer actuator output (0–100% open)"},
        {"name": "Mixed Air Temperature",           "abbr": "MAT",        "io": "AI",       "unit": "°F",    "desc": "Mixed air chamber sensor"},
        {"name": "Occupied Mode",                   "abbr": "OCC-MODE",   "io": "SP",       "unit": "On/Off","desc": "Occupied/unoccupied schedule input"},
        {"name": "General Alarm",                   "abbr": "ALM",        "io": "DI",       "unit": "Alarm", "desc": "Unit-level alarm or fault contact"},
    ],
    "AHU": [
        {"name": "Supply Air Temperature",          "abbr": "SAT",        "io": "AI",       "unit": "°F",    "desc": "Discharge sensor after coil"},
        {"name": "Supply Air Temperature Setpoint", "abbr": "SAT-SP",     "io": "SP",       "unit": "°F",    "desc": "Cooling/heating discharge setpoint"},
        {"name": "Return Air Temperature",          "abbr": "RAT",        "io": "AI",       "unit": "°F",    "desc": "Return air sensor"},
        {"name": "Mixed Air Temperature",           "abbr": "MAT",        "io": "AI",       "unit": "°F",    "desc": "Mixed air sensor upstream of coil"},
        {"name": "Outdoor Air Temperature",         "abbr": "OAT",        "io": "AI",       "unit": "°F",    "desc": "Outdoor ambient sensor"},
        {"name": "Supply Air Pressure",             "abbr": "SAP",        "io": "AI",       "unit": "in. WC","desc": "Duct static pressure sensor"},
        {"name": "Supply Air Pressure Setpoint",    "abbr": "SAP-SP",     "io": "SP",       "unit": "in. WC","desc": "Duct static pressure setpoint"},
        {"name": "Return Air Pressure",             "abbr": "RAP",        "io": "AI",       "unit": "in. WC","desc": "Return duct pressure (if applicable)"},
        {"name": "Supply Fan VFD Speed",            "abbr": "SF-SPD",     "io": "AO",       "unit": "%",     "desc": "VFD output to supply fan (0–10 V or 4–20 mA)"},
        {"name": "Supply Fan Status",               "abbr": "SF-STS",     "io": "DI",       "unit": "On/Off","desc": "Fan proving via current switch or VFD"},
        {"name": "Return Fan VFD Speed",            "abbr": "RF-SPD",     "io": "AO",       "unit": "%",     "desc": "VFD output to return fan"},
        {"name": "Return Fan Status",               "abbr": "RF-STS",     "io": "DI",       "unit": "On/Off","desc": "Return fan status"},
        {"name": "Chilled Water Valve Position",    "abbr": "CWV-POS",    "io": "AO",       "unit": "%",     "desc": "Cooling coil valve actuator (0–100%)"},
        {"name": "Heating Water Valve Position",    "abbr": "HWV-POS",    "io": "AO",       "unit": "%",     "desc": "Heating coil valve actuator"},
        {"name": "Outside Air Damper Position",     "abbr": "OAD-POS",    "io": "AO",       "unit": "%",     "desc": "Economizer/OA damper actuator"},
        {"name": "Return Air Damper Position",      "abbr": "RAD-POS",    "io": "AO",       "unit": "%",     "desc": "Return air damper actuator"},
        {"name": "Exhaust Air Damper Position",     "abbr": "EAD-POS",    "io": "AO",       "unit": "%",     "desc": "Exhaust damper actuator"},
        {"name": "Filter Differential Pressure",    "abbr": "FDIFF",      "io": "AI",       "unit": "in. WC","desc": "Dirty filter switch or transducer"},
        {"name": "Freeze Stat Status",              "abbr": "FRZ-STS",    "io": "DI",       "unit": "Alarm", "desc": "Low-limit freeze protection"},
        {"name": "Smoke Detector Status",           "abbr": "SMK-STS",    "io": "DI",       "unit": "Alarm", "desc": "Duct smoke detector status"},
        {"name": "General Alarm",                   "abbr": "ALM",        "io": "DI",       "unit": "Alarm", "desc": "Unit-level fault contact"},
    ],
    "VAV": [
        {"name": "Space Temperature",               "abbr": "SPT",        "io": "AI",       "unit": "°F",    "desc": "Room temperature sensor at thermostat"},
        {"name": "Space Temperature Cooling SP",    "abbr": "CLG-SP",     "io": "SP",       "unit": "°F",    "desc": "Occupied cooling setpoint (default 75°F)"},
        {"name": "Space Temperature Heating SP",    "abbr": "HTG-SP",     "io": "SP",       "unit": "°F",    "desc": "Occupied heating setpoint (default 70°F)"},
        {"name": "Primary Air Flow",                "abbr": "PAF",        "io": "AI",       "unit": "CFM",   "desc": "Flow sensor via pressure differential across damper"},
        {"name": "Primary Air Flow Setpoint",       "abbr": "PAF-SP",     "io": "SP",       "unit": "CFM",   "desc": "Max/min airflow setpoints per schedule"},
        {"name": "Damper Position",                 "abbr": "DMP-POS",    "io": "AO",       "unit": "%",     "desc": "DDC-to-actuator analog output (0–10 V)"},
        {"name": "Reheat Valve Position",           "abbr": "RHV-POS",    "io": "AO",       "unit": "%",     "desc": "Reheat coil valve actuator (if HW reheat)"},
        {"name": "Reheat Stage Command",            "abbr": "RHT-CMD",    "io": "DO",       "unit": "On/Off","desc": "Electric reheat stage enable (if electric reheat)"},
        {"name": "Occupied Mode",                   "abbr": "OCC-MODE",   "io": "SP",       "unit": "On/Off","desc": "Occupancy override from BMS or local button"},
    ],
    "FCU": [
        {"name": "Space Temperature",               "abbr": "SPT",        "io": "AI",       "unit": "°F",    "desc": "Room temperature sensor"},
        {"name": "Space Temperature Setpoint",      "abbr": "SPT-SP",     "io": "SP",       "unit": "°F",    "desc": "Zone setpoint"},
        {"name": "Fan Speed Command",               "abbr": "FAN-SPD",    "io": "AO",       "unit": "Step",  "desc": "Low/Medium/High fan speed output"},
        {"name": "Fan Status",                      "abbr": "FAN-STS",    "io": "DI",       "unit": "On/Off","desc": "Fan run status"},
        {"name": "Chilled Water Valve",             "abbr": "CWV-POS",    "io": "AO",       "unit": "%",     "desc": "Cooling valve actuator"},
        {"name": "Heating Water Valve",             "abbr": "HWV-POS",    "io": "AO",       "unit": "%",     "desc": "Heating valve actuator"},
    ],
    "PLC": [
        {"name": "Digital Input 1",                 "abbr": "DI-01",      "io": "DI",       "unit": "On/Off","desc": "Confirm assignment with controls engineer"},
        {"name": "Digital Output 1",                "abbr": "DO-01",      "io": "DO",       "unit": "On/Off","desc": "Confirm assignment with controls engineer"},
        {"name": "Analog Input 1",                  "abbr": "AI-01",      "io": "AI",       "unit": "4-20mA","desc": "Confirm signal type and range"},
        {"name": "Analog Output 1",                 "abbr": "AO-01",      "io": "AO",       "unit": "4-20mA","desc": "Confirm signal type and scaling"},
        {"name": "Communication Heartbeat",         "abbr": "HB",         "io": "Status",   "unit": "ms",    "desc": "OPC UA / Modbus watchdog timeout point"},
        {"name": "CPU Fault Alarm",                 "abbr": "CPU-ALM",    "io": "DI",       "unit": "Alarm", "desc": "PLC CPU fault relay output to BMS"},
    ],
}

_RFIS: dict[str, list[dict]] = {
    "RTU": [
        {"q": "Confirm total number of compressor cooling stages and rated tonnage per stage.", "priority": "High"},
        {"q": "Confirm whether unit includes an air-side economizer; if yes, specify type (dry-bulb, enthalpy, differential enthalpy).", "priority": "High"},
        {"q": "Confirm DDC controller manufacturer, model, and firmware version.", "priority": "High"},
        {"q": "Confirm BACnet network type (IP or MS/TP) and device instance assignment.", "priority": "Medium"},
        {"q": "Confirm supply fan type and whether VFD is factory-installed or field-provided.", "priority": "Medium"},
        {"q": "Confirm heating source and number of stages (gas heat, electric, heat pump).", "priority": "Medium"},
        {"q": "Confirm occupied/unoccupied schedule override input method (BACnet, dry contact, UI button).", "priority": "Low"},
    ],
    "AHU": [
        {"q": "Confirm chilled water coil valve size, Cv, and actuator manufacturer/model.", "priority": "High"},
        {"q": "Confirm heating coil type (HHW, electric, steam) and valve specification.", "priority": "High"},
        {"q": "Confirm DDC controller manufacturer, model, and I/O count required.", "priority": "High"},
        {"q": "Confirm VFD manufacturer/model for supply and return fans.", "priority": "Medium"},
        {"q": "Confirm duct static pressure sensor location (two-thirds of longest duct run).", "priority": "Medium"},
        {"q": "Confirm economizer/OA damper actuator model and fail position (fail-open or fail-closed).", "priority": "Medium"},
        {"q": "Confirm freeze protection strategy: freeze stat, low-limit, or glycol loop.", "priority": "High"},
        {"q": "Confirm smoke detector interlock requirements per local AHJ.", "priority": "Medium"},
    ],
    "VAV": [
        {"q": "Confirm VAV terminal unit manufacturer and DDC controller (integral or standalone).", "priority": "High"},
        {"q": "Confirm reheat coil type (HHW or electric) and capacity per zone.", "priority": "High"},
        {"q": "Confirm minimum and maximum airflow setpoints (CFM) per VAV schedule.", "priority": "High"},
        {"q": "Confirm BACnet MS/TP wiring topology — daisy-chain or home-run.", "priority": "Medium"},
        {"q": "Confirm zone temperature sensor: wall-mount with display or without.", "priority": "Low"},
    ],
    "BACnet/IP": [
        {"q": "Confirm IP addressing scheme for all BACnet/IP devices (DHCP vs. static).", "priority": "High"},
        {"q": "Confirm BBMD router location and configuration for multi-subnet deployments.", "priority": "High"},
        {"q": "Confirm BACnet device instance range allocation by trade/floor/system.", "priority": "Medium"},
        {"q": "Confirm firewall rules and VLAN assignment for BACnet/IP traffic.", "priority": "Medium"},
    ],
    "BACnet MS/TP": [
        {"q": "Confirm trunk segment length and confirm 120Ω termination resistors at each end.", "priority": "High"},
        {"q": "Confirm MAC address assignments for all MS/TP devices (0–127 range).", "priority": "High"},
        {"q": "Confirm baud rate for each MS/TP trunk (9600 / 19200 / 38400 / 76800).", "priority": "Medium"},
    ],
    "Modbus": [
        {"q": "Confirm Modbus register map version and revision date from equipment manufacturer.", "priority": "High"},
        {"q": "Confirm Modbus slave address assignments (no duplicates on each trunk).", "priority": "High"},
        {"q": "Confirm whether Modbus TCP gateway or native Modbus TCP device is used.", "priority": "Medium"},
    ],
    "PLC": [
        {"q": "Confirm PLC manufacturer and model (Allen-Bradley, Siemens, Schneider, etc.).", "priority": "High"},
        {"q": "Confirm I/O module types and quantity (DI, DO, AI, AO, specialty).", "priority": "High"},
        {"q": "Confirm communication protocol to BMS (OPC UA, Modbus TCP, EtherNet/IP, BACnet).", "priority": "High"},
        {"q": "Confirm rack/chassis quantity and physical location in electrical room.", "priority": "Medium"},
        {"q": "Confirm UL 508A industrial panel certification requirement.", "priority": "Medium"},
        {"q": "Confirm SCADA/HMI integration — is separate HMI required or BMS serves as HMI?", "priority": "Medium"},
    ],
    "VFD": [
        {"q": "Confirm VFD manufacturer, frame size, and HP/kW rating for each drive.", "priority": "High"},
        {"q": "Confirm VFD control input type: 0–10 V, 4–20 mA, or network (BACnet/Modbus).", "priority": "Medium"},
        {"q": "Confirm bypass configuration (manual bypass or auto-transfer).", "priority": "Medium"},
    ],
}

_FIELD_VERIFICATIONS: dict[str, list[dict]] = {
    "RTU": [
        {"task": "Verify supply air temperature sensor location, mounting, and calibration (±1°F)", "category": "Sensor"},
        {"task": "Verify outdoor air temperature sensor is shaded and out of direct solar gain", "category": "Sensor"},
        {"task": "Verify compressor stage 1 and 2 run status feedback with unit energized", "category": "Wiring"},
        {"task": "Verify supply fan current switch calibration (picks up at 15–20% full-load current)", "category": "Sensor"},
        {"task": "Verify BACnet MS/TP wiring polarity (+/-) and 120Ω end-of-line termination", "category": "Network"},
        {"task": "Verify economizer damper actuator strokes full open and full closed from DDC", "category": "Mechanical"},
        {"task": "Verify all points report correctly in BMS graphics before Cx witness", "category": "Software"},
        {"task": "Verify DDC controller power supply voltage (24 VAC ±10%)", "category": "Wiring"},
    ],
    "AHU": [
        {"task": "Verify supply air temperature sensor is installed 3–5 duct diameters downstream of mixing zone", "category": "Sensor"},
        {"task": "Verify mixed air temperature sensor spans full duct width (averaging element)", "category": "Sensor"},
        {"task": "Verify chilled water valve closes tight (zero flow at 0% command)", "category": "Mechanical"},
        {"task": "Verify heating water valve closes tight (zero flow at 0% command)", "category": "Mechanical"},
        {"task": "Verify OA, RA, and EA damper actuators stroke fully from DDC command", "category": "Mechanical"},
        {"task": "Verify supply fan VFD responds to analog output (0 V → 0 Hz, 10 V → 60 Hz)", "category": "Wiring"},
        {"task": "Verify duct static pressure sensor location per design (2/3 longest duct run)", "category": "Sensor"},
        {"task": "Verify freeze stat setpoint calibration (typically 38°F trip point)", "category": "Sensor"},
        {"task": "Verify smoke detector input wiring and smoke alarm interlock shuts down AHU", "category": "Wiring"},
        {"task": "Verify all BACnet objects for this AHU appear on BMS head-end with correct units", "category": "Software"},
    ],
    "VAV": [
        {"task": "Verify VAV airflow sensor differential pressure at design max flow (cross-check with TAB report)", "category": "Sensor"},
        {"task": "Verify damper actuator strokes from 0–100% and holds each position without drift", "category": "Mechanical"},
        {"task": "Verify space temperature sensor is at manufacturer-specified height (5 ft AFF)", "category": "Sensor"},
        {"task": "Verify reheat valve actuator strokes and closes tight at 0% command", "category": "Mechanical"},
        {"task": "Verify BACnet MS/TP MAC address is unique and matches sequence schedule", "category": "Network"},
        {"task": "Verify minimum airflow setpoint is not below AHJ ventilation minimum (ASHRAE 62.1)", "category": "Software"},
    ],
    "PLC": [
        {"task": "Verify I/O wiring to terminal strip matches I/O schedule drawing", "category": "Wiring"},
        {"task": "Verify analog input signal type matches field device output (4–20 mA vs 0–10 V)", "category": "Wiring"},
        {"task": "Verify communication link to BMS is active and heartbeat point is cycling", "category": "Network"},
        {"task": "Verify CPU fault relay output wires to BMS alarm point", "category": "Wiring"},
        {"task": "Verify panel grounding meets NEC 250 requirements", "category": "Wiring"},
        {"task": "Verify UPS or surge suppressor installed on PLC power supply", "category": "Wiring"},
    ],
    "BACnet/IP": [
        {"task": "Verify BACnet/IP device is reachable by BMS head-end via ping and BACnet Who-Is", "category": "Network"},
        {"task": "Verify IP address assignment matches as-built drawings", "category": "Network"},
        {"task": "Verify COV (Change-of-Value) subscriptions are active for critical AI points", "category": "Network"},
    ],
    "BACnet MS/TP": [
        {"task": "Verify trunk termination resistors (120 Ω) are installed at both physical ends only", "category": "Network"},
        {"task": "Verify all MS/TP devices are visible on network sniffer during token pass", "category": "Network"},
        {"task": "Verify trunk length does not exceed 4,000 ft (EIA-485 limit)", "category": "Network"},
    ],
    "Modbus": [
        {"task": "Verify Modbus register reads return expected engineering values vs. nameplate", "category": "Network"},
        {"task": "Verify RS-485 wiring uses shielded twisted pair with shield grounded at one end only", "category": "Wiring"},
        {"task": "Verify slave address assignments are unique — no duplicates on any trunk", "category": "Network"},
    ],
    "VFD": [
        {"task": "Verify VFD acceleration/deceleration ramps match equipment spec (default: 30 s)", "category": "Software"},
        {"task": "Verify VFD minimum Hz is set per motor nameplate (typically 18–20 Hz for HVAC fans)", "category": "Software"},
        {"task": "Verify VFD overload relay trip setpoint matches motor FLA", "category": "Wiring"},
    ],
}

_CX_ITEMS: dict[str, list[dict]] = {
    "RTU": [
        {"name": "Cooling Sequence Functional Test", "desc": "Stage 1 and 2 cooling, verify SAT drops to setpoint within capacity window", "cat": "Functional"},
        {"name": "Heating Sequence Functional Test", "desc": "Stage 1 and 2 heating, verify SAT rises to setpoint", "cat": "Functional"},
        {"name": "Economizer Sequence Functional Test", "desc": "Verify economizer enables at correct OAT setpoint and positions to calculated position", "cat": "Functional"},
        {"name": "Night Setback / Unoccupied Test", "desc": "Verify setback setpoints are enforced during unoccupied period", "cat": "Setpoint"},
        {"name": "High SAT Alarm Test", "desc": "Force SAT above high limit, verify BMS alarm generates within 60 s", "cat": "Alarm"},
        {"name": "Supply Fan Failure Alarm Test", "desc": "Disconnect fan status, verify BMS fan failure alarm within 30 s", "cat": "Alarm"},
        {"name": "Trend Log Verification", "desc": "Verify SAT, RAT, compressor status trend logs are recording at required interval", "cat": "Trend"},
    ],
    "AHU": [
        {"name": "Cooling Mode Functional Test", "desc": "Full-load cooling: chilled water valve to 100%, verify SAT achieves setpoint ±2°F", "cat": "Functional"},
        {"name": "Heating Mode Functional Test", "desc": "Full-load heating: HHW valve to 100%, verify SAT achieves setpoint ±2°F", "cat": "Functional"},
        {"name": "Mixed Air Economizer Test", "desc": "Verify OA damper modulates to maintain MAT setpoint; RA/EA dampers track inversely", "cat": "Functional"},
        {"name": "Supply Fan VFD Control Test", "desc": "Verify fan ramps up/down to maintain duct static pressure setpoint ±0.05 in. WC", "cat": "Functional"},
        {"name": "Freeze Protection Test", "desc": "Force freeze stat — verify AHU shuts down, heating valve opens 100%, alarm generated", "cat": "Alarm"},
        {"name": "Smoke Shutdown Functional Test", "desc": "Trip smoke detector — verify AHU shuts down and BMS generates life-safety alarm", "cat": "Alarm"},
        {"name": "Discharge Air Temperature Alarm", "desc": "Force SAT above high limit setpoint, verify BMS alarm within 60 s", "cat": "Alarm"},
        {"name": "Trend Log Verification", "desc": "Confirm SAT, SAP, valve positions, and fan speed are trending at spec interval", "cat": "Trend"},
    ],
    "VAV": [
        {"name": "Airflow Setpoint Verification", "desc": "Confirm primary airflow at max, min, and deadband setpoints match TAB schedule", "cat": "Setpoint"},
        {"name": "Cooling Mode Test", "desc": "Raise SPT above CLG-SP: verify damper opens to max airflow", "cat": "Functional"},
        {"name": "Deadband Test", "desc": "SPT in deadband (between CLG-SP and HTG-SP): verify damper at minimum flow", "cat": "Functional"},
        {"name": "Heating Mode Test", "desc": "Lower SPT below HTG-SP: verify damper at minimum, reheat activates", "cat": "Functional"},
        {"name": "Temperature Sensor Accuracy Check", "desc": "Verify SPT matches handheld reference thermometer ±1°F", "cat": "Setpoint"},
        {"name": "Trend Log Verification", "desc": "Confirm SPT, PAF, and damper position trends are active at required interval", "cat": "Trend"},
    ],
    "PLC": [
        {"name": "I/O Point-to-Point Functional Test", "desc": "Force each digital input and verify PLC logic reads correctly; verify each analog input scaling", "cat": "Functional"},
        {"name": "Communication Link Test", "desc": "Verify OPC UA / Modbus connection to BMS is stable; simulate link drop — verify BMS alarm", "cat": "Functional"},
        {"name": "Fault Relay Output Test", "desc": "Force CPU fault — verify relay trips and BMS alarm is generated within 30 s", "cat": "Alarm"},
        {"name": "Watchdog / Heartbeat Test", "desc": "Disconnect PLC from network — verify BMS detects communication loss within watchdog window", "cat": "Alarm"},
    ],
    "BACnet/IP": [
        {"name": "Who-Is / I-Am Broadcast Test", "desc": "Issue BACnet Who-Is on network — verify all expected devices respond with I-Am", "cat": "Functional"},
        {"name": "Read Property Test", "desc": "Poll a representative AI, AO, DI, DO from each device — confirm values match BMS graphic", "cat": "Functional"},
        {"name": "Alarm Notification Test", "desc": "Force an alarm on each device — verify BACnet alarm notification reaches BMS head-end", "cat": "Alarm"},
    ],
}

_CAD_TASKS: dict[str, list[str]] = {
    "RTU": [
        "Add DDC controller wiring diagram to E-series electrical drawings",
        "Add RTU BACnet network riser to controls riser diagram",
        "Add supply air temperature sensor detail to mechanical plan",
        "Update RTU sequence of operation on controls drawing (per project-specific settings)",
    ],
    "AHU": [
        "Add AHU DDC panel wiring schematic to electrical package",
        "Add BACnet network riser segment for this AHU",
        "Add chilled water and heating water valve P&ID detail",
        "Add AHU control sequence to sequences drawing sheet",
    ],
    "VAV": [
        "Add VAV wiring detail (24V, BACnet MS/TP bus, thermostat) to typical detail sheet",
        "Add MS/TP trunk riser for this VAV zone group",
    ],
    "PLC": [
        "Add PLC panel general arrangement drawing (door layout, component placement)",
        "Add PLC I/O wiring schematic per I/O schedule",
        "Add communication network connection to controls riser diagram",
        "Add UL 508A panel label detail",
    ],
}

_SUBMITTALS: dict[str, list[str]] = {
    "RTU": [
        "DDC controller submittals (manufacturer, model, I/O count, certifications)",
        "RTU supply air temperature sensor cut sheet",
        "RTU economizer damper actuator cut sheet",
        "BACnet conformance statement for RTU controller",
    ],
    "AHU": [
        "DDC controller submittals (manufacturer, model, memory, certifications)",
        "Chilled water valve and actuator submittals",
        "Heating water valve and actuator submittals",
        "OA/RA/EA damper actuator submittals",
        "VFD submittals (supply fan, return fan if applicable)",
        "Duct static pressure transducer cut sheet",
        "Freeze stat cut sheet and calibration certificate",
    ],
    "VAV": [
        "VAV terminal unit submittals (unit schedule, airflow range, actuator type)",
        "VAV DDC controller submittals",
        "Zone temperature sensor submittals",
        "Reheat coil valve and actuator submittals (if applicable)",
    ],
    "PLC": [
        "PLC hardware submittals (CPU, I/O modules, power supply, rack)",
        "PLC enclosure submittals (NEMA rating, dimensions, UL 508A listing)",
        "Communication module submittals (EtherNet/IP, OPC UA, Modbus TCP card)",
        "HMI submittals (if standalone HMI is specified)",
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _scored_equipment(scored_terms: list, threshold: float = 0.60) -> list[str]:
    """Return list of equipment type terms confirmed above threshold."""
    eq_categories = {"equipment_type", "plc_hardware"}
    return [
        t.normalized_term
        for t in scored_terms
        if t.source_confirmed
        and t.confidence >= threshold
        and t.category in eq_categories
    ]


def _scored_protocols(scored_terms: list, threshold: float = 0.60) -> list[str]:
    return [
        t.normalized_term
        for t in scored_terms
        if t.source_confirmed
        and t.confidence >= threshold
        and t.category in {"protocol"}
    ]


def _scored_components(scored_terms: list, threshold: float = 0.55) -> list[str]:
    """Other confirmed terms (VFD, sensors, controllers, etc.)."""
    return [
        t.normalized_term
        for t in scored_terms
        if t.source_confirmed
        and t.confidence >= threshold
        and t.category in {"panel_component", "controller_model"}
    ]


def _make_points(equip: str, confidence: float) -> list[PointCandidate]:
    pts = _POINTS.get(equip, [])
    return [
        PointCandidate(
            equipment=equip,
            point_name=p["name"],
            abbreviation=p["abbr"],
            io_type=p["io"],
            engineering_unit=p["unit"],
            description=p["desc"],
            confidence=confidence,
            source_type="template_default",
        )
        for p in pts
    ]


def _make_rfis(equip: str, confidence: float, template: str, start_num: int) -> list[RFIItem]:
    qs = _RFIS.get(equip, [])
    items = []
    for i, q in enumerate(qs):
        items.append(RFIItem(
            equipment=equip,
            rfi_number=f"RFI-{start_num + i:03d}",
            question=q["q"],
            priority=q["priority"],
            template=template,
            confidence=confidence,
        ))
    return items


def _make_fv(equip: str, template: str) -> list[FieldVerificationItem]:
    tasks = _FIELD_VERIFICATIONS.get(equip, [])
    return [
        FieldVerificationItem(equipment=equip, task=t["task"], category=t["category"], template=template)
        for t in tasks
    ]


def _make_cx(equip: str, template: str) -> list[CxItem]:
    items = _CX_ITEMS.get(equip, [])
    return [
        CxItem(equipment=equip, test_name=c["name"], description=c["desc"], category=c["cat"], template=template)
        for c in items
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_workflow_items(
    markdown_text: str,
    scored_terms: list | None = None,
    template_decisions: list[dict] | None = None,
) -> dict[str, Any]:
    """Generate structured workflow deliverables from scored source document.

    Parameters
    ----------
    markdown_text:
        Raw/normalised source document text (used for length/summary).
    scored_terms:
        List of ScoredTerm objects from the confidence scorer.
    template_decisions:
        List of template trigger decisions from filter_engine.
    """
    scored_terms = scored_terms or []
    template_decisions = template_decisions or []

    out = WorkflowOutput()
    triggered = [d for d in template_decisions if d.get("triggered")]
    out.triggered_templates = [d["template_name"] for d in triggered]
    out.source_equipment = _scored_equipment(scored_terms)
    out.source_protocols = _scored_protocols(scored_terms)

    rfi_counter = 1

    # Equipment-driven points / RFIs / FV / Cx
    for equip_term in set(out.source_equipment):
        conf = next(
            (t.confidence for t in scored_terms if t.normalized_term == equip_term),
            0.60,
        )
        template = f"{equip_term.lower()}_controls_review"

        pts = _make_points(equip_term, conf)
        out.points.extend(pts)

        rfis = _make_rfis(equip_term, conf, template, rfi_counter)
        out.rfis.extend(rfis)
        rfi_counter += len(rfis)

        out.field_verifications.extend(_make_fv(equip_term, template))
        out.cx_items.extend(_make_cx(equip_term, template))
        out.cad_tasks.extend(_CAD_TASKS.get(equip_term, []))
        out.submittal_items.extend(_SUBMITTALS.get(equip_term, []))

    # Protocol-driven RFIs / FV / Cx (BACnet, Modbus, etc.)
    for proto in set(out.source_protocols):
        conf = next(
            (t.confidence for t in scored_terms if t.normalized_term == proto),
            0.60,
        )
        template = f"{proto.lower().replace('/', '').replace(' ', '_')}_network_review"

        rfis = _make_rfis(proto, conf, template, rfi_counter)
        out.rfis.extend(rfis)
        rfi_counter += len(rfis)

        out.field_verifications.extend(_make_fv(proto, template))
        out.cx_items.extend(_make_cx(proto, template))

    # Component-driven (VFD, etc.)
    extra_terms = _scored_components(scored_terms)
    for comp in set(extra_terms):
        conf = next(
            (t.confidence for t in scored_terms if t.normalized_term == comp),
            0.55,
        )
        rfis = _make_rfis(comp, conf, "component_review", rfi_counter)
        out.rfis.extend(rfis)
        rfi_counter += len(rfis)
        out.field_verifications.extend(_make_fv(comp, "component_review"))
        out.cx_items.extend(_make_cx(comp, "component_review"))

    # Summary
    n_eq = len(out.source_equipment)
    n_pts = len(out.points)
    n_rfi = len(out.rfis)
    n_fv = len(out.field_verifications)
    n_cx = len(out.cx_items)

    if n_eq == 0 and not triggered:
        out.summary = (
            "No source-confirmed equipment detected above threshold. "
            "Upload a controls specification, sequence of operation, or points list for best results."
        )
    else:
        eq_str = ", ".join(out.source_equipment) if out.source_equipment else "general controls scope"
        out.summary = (
            f"Source-confirmed equipment: {eq_str}. "
            f"Generated {n_pts} point candidates, {n_rfi} RFI items, "
            f"{n_fv} field verification tasks, and {n_cx} commissioning tests."
        )

    return {
        "summary": out.summary,
        "triggered_templates": out.triggered_templates,
        "source_equipment": out.source_equipment,
        "source_protocols": out.source_protocols,
        "points": [
            {
                "equipment": p.equipment,
                "point_name": p.point_name,
                "abbreviation": p.abbreviation,
                "io_type": p.io_type,
                "engineering_unit": p.engineering_unit,
                "description": p.description,
                "confidence": p.confidence,
                "source_type": p.source_type,
            }
            for p in out.points
        ],
        "rfis": [
            {
                "rfi_number": r.rfi_number,
                "equipment": r.equipment,
                "question": r.question,
                "priority": r.priority,
                "template": r.template,
                "confidence": r.confidence,
            }
            for r in out.rfis
        ],
        "field_verifications": [
            {
                "equipment": fv.equipment,
                "task": fv.task,
                "category": fv.category,
                "template": fv.template,
            }
            for fv in out.field_verifications
        ],
        "cx_items": [
            {
                "equipment": c.equipment,
                "test_name": c.test_name,
                "description": c.description,
                "category": c.category,
                "template": c.template,
            }
            for c in out.cx_items
        ],
        "cad_tasks": out.cad_tasks,
        "submittal_items": out.submittal_items,
        "source_length_chars": len(markdown_text),
    }
