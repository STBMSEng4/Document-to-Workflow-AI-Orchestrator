# BMS / ICS / PLC Knowledge Base

> SpecFlow AI reference vocabulary. Terms listed here define *possible* detections only.
> The source document must support every detected term. KB presence alone = confidence 0.00.

---

## BMS

**Category:** BMS / BAS
**Definition:** Building Management System. A computer-based control system installed in a building to monitor and manage mechanical and electrical equipment.
**Common aliases:** Building Automation System, BAS, building controls, IBMS
**Related terms:** DDC controller, BACnet, points list, sequence of operation
**BMS/ICS relevance:** Core system term. Triggers generic_bms_controls_review template.
**Agent interpretation rules:** BMS and BAS are interchangeable in most documents. DDC controller alone does not confirm BMS.
**Source-confirmed filtering rules:** Must be stated or clearly implied; "building controls" counts as alias.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20, nearby_technical_context +0.20
**Template trigger threshold:** 0.65
**Example usage:** "The BMS contractor shall provide all programming and graphics."

---

## BAS

**Category:** BMS / BAS
**Definition:** Building Automation System. Functionally equivalent to BMS in most usage.
**Common aliases:** BMS, building controls, direct digital controls system
**Related terms:** BMS, DDC controller, BACnet
**BMS/ICS relevance:** Core system term.
**Agent interpretation rules:** BAS and BMS are treated as aliases. Do not generate separate templates for both.
**Source-confirmed filtering rules:** Must be explicitly stated or alias-matched.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.65
**Example usage:** "The BAS contractor shall perform point-to-point checkout."

---

## DDC Controller

**Category:** Controllers
**Definition:** Direct Digital Controller. A field-level controller that executes sequences of operation for HVAC and other building systems.
**Common aliases:** controller, field controller, unitary controller, application controller
**Related terms:** BMS, BACnet, points list, sequence of operation
**BMS/ICS relevance:** Primary field device in BMS systems.
**Agent interpretation rules:** "Controller" alone is not sufficient — must be paired with a technical qualifier. Do not assume PLC from DDC.
**Source-confirmed filtering rules:** "DDC controller" or "DDC" required; "controller" alone scores inferred only.
**Confidence triggers:** exact_term_match +0.35, nearby_technical_context +0.20
**Template trigger threshold:** 0.65
**Example usage:** "Replace existing DDC controllers with new BACnet/IP controllers."

---

## PLC

**Category:** PLC / ICS
**Definition:** Programmable Logic Controller. Industrial control device used in manufacturing, process, and OT environments.
**Common aliases:** programmable controller, logic controller
**Related terms:** HMI, SCADA, OPC UA, ladder logic, I/O module
**BMS/ICS relevance:** Common in industrial and process systems. Not interchangeable with DDC.
**Agent interpretation rules:** Do not assume PLC from "controller." Must be explicitly named.
**Source-confirmed filtering rules:** "PLC" must appear explicitly. "DDC controller" does not confirm PLC.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.70
**Example usage:** "The PLC shall communicate via OPC UA to the SCADA system."

---

## SCADA

**Category:** SCADA / HMI
**Definition:** Supervisory Control and Data Acquisition. Software system for monitoring and controlling industrial processes.
**Common aliases:** supervisory system, control center
**Related terms:** PLC, HMI, OPC UA, historian
**BMS/ICS relevance:** OT/ICS supervisory layer above PLCs.
**Agent interpretation rules:** SCADA is an OT system term. Do not assume SCADA in standard BMS projects.
**Source-confirmed filtering rules:** Must be explicitly named.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.70
**Example usage:** "The SCADA system shall display all field device statuses."

---

## HMI

**Category:** SCADA / HMI
**Definition:** Human-Machine Interface. Operator interface for SCADA or PLC systems.
**Common aliases:** operator interface, operator panel, touchscreen panel
**Related terms:** SCADA, PLC, historian
**BMS/ICS relevance:** Operator layer in OT/ICS systems.
**Agent interpretation rules:** Do not assume HMI from BMS graphics workstation.
**Source-confirmed filtering rules:** Must be explicitly named.
**Confidence triggers:** exact_term_match +0.35, nearby_technical_context +0.20
**Template trigger threshold:** 0.70
**Example usage:** "The HMI shall provide real-time process visualization."

---

## RTU

**Category:** HVAC Equipment
**Definition:** Rooftop Unit. A packaged HVAC unit mounted on the roof providing heating, cooling, and ventilation.
**Common aliases:** packaged unit, rooftop packaged unit, RTU-
**Related terms:** supply fan, economizer, heating stage, cooling stage, discharge air temperature, BACnet
**BMS/ICS relevance:** Primary equipment type in light commercial BMS retrofits.
**Agent interpretation rules:** RTU in the context of HVAC means Rooftop Unit, not Remote Terminal Unit (OT context). Use document context to distinguish.
**Source-confirmed filtering rules:** RTU tag or description must appear. Do not assume from generic "unit."
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20, nearby_technical_context +0.20
**Template trigger threshold:** 0.70
**Example usage:** "RTU-1 shall be provided with BACnet/IP communication."

---

## AHU

**Category:** HVAC Equipment
**Definition:** Air Handling Unit. A large central HVAC unit that conditions and distributes air through ductwork.
**Common aliases:** air handler, central air unit, AHU-
**Related terms:** mixed air, return air, supply air, VFD, chilled water coil, hot water coil, economizer
**BMS/ICS relevance:** Primary equipment in commercial and institutional BMS projects.
**Agent interpretation rules:** Do not assume AHU exists because RTU exists. Do not assume RTU is AHU.
**Source-confirmed filtering rules:** "AHU" or "air handler" must appear explicitly.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.70
**Example usage:** "AHU-2 shall be equipped with a VFD on the supply fan."

---

## VAV

**Category:** HVAC Equipment
**Definition:** Variable Air Volume terminal unit. A terminal device that modulates airflow to a zone.
**Common aliases:** VAV box, VAV terminal, variable volume terminal
**Related terms:** damper, reheat coil, space temperature, duct static pressure, BACnet MS/TP
**BMS/ICS relevance:** Very common in commercial BMS. Typically hundreds per building.
**Agent interpretation rules:** VAV presence implies zone-level points. Do not assume reheat unless stated.
**Source-confirmed filtering rules:** "VAV" or "variable air volume" must appear.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20, nearby_technical_context +0.20
**Template trigger threshold:** 0.70
**Example usage:** "Each VAV shall have a BACnet MS/TP controller with space temperature sensor."

---

## FCU

**Category:** HVAC Equipment
**Definition:** Fan Coil Unit. A terminal HVAC device with a fan and coil, used for zone-level heating/cooling.
**Common aliases:** fan coil, terminal unit
**Related terms:** chilled water valve, hot water valve, space temperature, BACnet
**BMS/ICS relevance:** Common in hotel, multifamily, and commercial buildings.
**Agent interpretation rules:** Do not assume FCU from generic "terminal unit."
**Source-confirmed filtering rules:** "FCU" or "fan coil" must appear.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.70
**Example usage:** "FCU-101 shall be controlled by a BACnet fan coil controller."

---

## Exhaust Fan

**Category:** HVAC Equipment
**Definition:** A fan that exhausts air from a space to the outside.
**Common aliases:** EF, exhaust unit, toilet exhaust, parking exhaust
**Related terms:** fan status, fan command, VFD, occupancy, BMS
**BMS/ICS relevance:** Monitored and commanded by BMS; often interlocked with AHU.
**Agent interpretation rules:** Do not assume VFD unless stated.
**Source-confirmed filtering rules:** "exhaust fan" or "EF-" tag must appear.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.65
**Example usage:** "EF-1 shall be enabled by the BMS occupancy schedule."

---

## Pump

**Category:** HVAC Equipment
**Definition:** A mechanical device that circulates water through hydronic systems.
**Common aliases:** CWP, HWP, chilled water pump, hot water pump, condenser water pump
**Related terms:** VFD, differential pressure, flow sensor, enable command, status
**BMS/ICS relevance:** Common in central plant BMS systems.
**Agent interpretation rules:** Pump type (CWP, HWP) should be inferred from context if not explicit.
**Source-confirmed filtering rules:** "pump" or pump tag must appear.
**Confidence triggers:** exact_term_match +0.35, nearby_technical_context +0.20
**Template trigger threshold:** 0.65
**Example usage:** "CWP-1 shall be commanded by the BMS with status feedback."

---

## Chiller

**Category:** HVAC Equipment
**Definition:** A refrigeration machine that cools water for distribution through a building's cooling system.
**Common aliases:** CH, chiller plant, water-cooled chiller, air-cooled chiller
**Related terms:** chilled water supply, chilled water return, condenser water, CWP, cooling tower, BMS
**BMS/ICS relevance:** Central plant equipment, high-priority BMS integration point.
**Agent interpretation rules:** Do not assume chiller from "cooling" alone.
**Source-confirmed filtering rules:** "chiller" or "CH-" must appear.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.70
**Example usage:** "The chiller shall communicate to the BMS via BACnet/IP."

---

## Boiler

**Category:** HVAC Equipment
**Definition:** A heating device that produces hot water or steam for building heating systems.
**Common aliases:** HW boiler, steam boiler, B-
**Related terms:** hot water supply, hot water return, HWP, condensate, BMS
**BMS/ICS relevance:** Central plant heating equipment.
**Agent interpretation rules:** Do not assume boiler from "heating" alone.
**Source-confirmed filtering rules:** "boiler" or "B-" must appear.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.70
**Example usage:** "B-1 shall be enabled by the BMS heating plant sequence."

---

## VFD

**Category:** Controllers
**Definition:** Variable Frequency Drive. An electronic device that controls motor speed by varying supply frequency.
**Common aliases:** variable speed drive, VSD, inverter, adjustable frequency drive, AFD
**Related terms:** fan speed command, pump speed command, duct static, differential pressure
**BMS/ICS relevance:** Controlled via analog output or BACnet from BMS.
**Agent interpretation rules:** Do not assume VFD from "fan" or "pump" unless explicitly stated.
**Source-confirmed filtering rules:** "VFD" or alias must appear.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.65
**Example usage:** "The VFD shall receive a 0-10V speed command from the DDC controller."

---

## Damper

**Category:** Actuators
**Definition:** A movable plate inside ductwork that controls airflow.
**Common aliases:** OA damper, RA damper, mixing damper, isolation damper
**Related terms:** actuator, damper position, modulating control, on/off control
**BMS/ICS relevance:** Controlled by BMS via analog or digital output.
**Agent interpretation rules:** Do not assume modulating control unless stated — may be two-position.
**Source-confirmed filtering rules:** "damper" must appear.
**Confidence triggers:** exact_term_match +0.35, nearby_technical_context +0.20
**Template trigger threshold:** 0.60
**Example usage:** "The OA damper shall modulate to maintain mixed air setpoint."

---

## Valve

**Category:** Actuators
**Definition:** A device that controls flow of water or steam through a pipe.
**Common aliases:** control valve, CHW valve, HW valve, CW valve, 2-way, 3-way
**Related terms:** actuator, valve position, modulating, on/off, coil
**BMS/ICS relevance:** Controlled by BMS via analog or digital output.
**Agent interpretation rules:** Do not assume modulating unless stated.
**Source-confirmed filtering rules:** "valve" must appear.
**Confidence triggers:** exact_term_match +0.35, nearby_technical_context +0.20
**Template trigger threshold:** 0.60
**Example usage:** "The CHW valve shall modulate to maintain discharge air temperature setpoint."

---

## BACnet/IP

**Category:** Communication Protocols
**Definition:** BACnet over IP networks. The primary protocol for BMS communication over Ethernet/LAN.
**Common aliases:** BACnet IP, BACnet over Ethernet, BACnet/IP network
**Related terms:** BMS, DDC controller, BBMD, network trunk, IP address, subnet
**BMS/ICS relevance:** Primary modern BMS communication protocol.
**Agent interpretation rules:** Do not assume BACnet/IP from "network" or "Ethernet" alone.
**Source-confirmed filtering rules:** "BACnet/IP" must appear explicitly.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.70
**Example usage:** "The controller shall communicate via BACnet/IP to the BAS server."

---

## BACnet MS/TP

**Category:** Communication Protocols
**Definition:** BACnet Master-Slave/Token-Passing. Serial BACnet protocol used for field-level device communication.
**Common aliases:** MS/TP, BACnet serial, RS-485 BACnet
**Related terms:** VAV, FCU, field bus, trunk cable, baud rate
**BMS/ICS relevance:** Used for VAV and FCU controller networks.
**Agent interpretation rules:** Do not assume MS/TP from "serial" or "RS-485" alone.
**Source-confirmed filtering rules:** "BACnet MS/TP" or "MS/TP" must appear.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.70
**Example usage:** "VAV controllers shall communicate via BACnet MS/TP to the floor-level controller."

---

## Modbus TCP

**Category:** Communication Protocols
**Definition:** Modbus over TCP/IP. Used for industrial and OT system integration.
**Common aliases:** Modbus/TCP, Modbus over Ethernet
**Related terms:** PLC, VFD, meter, register map, slave address
**BMS/ICS relevance:** Common for VFD, meter, and PLC integration to BMS.
**Agent interpretation rules:** Do not assume Modbus from "TCP" or "network" alone.
**Source-confirmed filtering rules:** "Modbus TCP" must appear explicitly.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.70
**Example usage:** "The VFD shall communicate via Modbus TCP to the BMS gateway."

---

## Modbus RTU

**Category:** Communication Protocols
**Definition:** Modbus over serial RS-485. Used for legacy and industrial device integration.
**Common aliases:** Modbus serial, Modbus RS-485
**Related terms:** RS-485, serial, slave address, register map
**BMS/ICS relevance:** Legacy integration protocol.
**Agent interpretation rules:** Do not assume Modbus RTU from "serial" or "RS-485" alone.
**Source-confirmed filtering rules:** "Modbus RTU" must appear explicitly.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.70
**Example usage:** "The flow meter shall be read via Modbus RTU."

---

## OPC UA

**Category:** Communication Protocols
**Definition:** OPC Unified Architecture. Industrial protocol for secure data exchange between OT systems.
**Common aliases:** OPC-UA, OPC Unified Architecture
**Related terms:** PLC, SCADA, historian, data server
**BMS/ICS relevance:** Used in OT/ICS environments for PLC-to-SCADA integration.
**Agent interpretation rules:** Do not assume OPC UA in standard BMS projects.
**Source-confirmed filtering rules:** "OPC UA" must appear explicitly.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.70
**Example usage:** "The PLC data shall be published via OPC UA to the historian."

---

## MQTT

**Category:** Communication Protocols
**Definition:** Message Queuing Telemetry Transport. Lightweight IoT/OT messaging protocol.
**Common aliases:** MQTT broker
**Related terms:** IoT, edge device, cloud gateway, broker
**BMS/ICS relevance:** Emerging in smart building and IoT edge applications.
**Agent interpretation rules:** Do not assume MQTT in traditional BMS projects.
**Source-confirmed filtering rules:** "MQTT" must appear explicitly.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.70
**Example usage:** "The edge device shall publish sensor data via MQTT."

---

## AI (Analog Input)

**Category:** I/O Types
**Definition:** Analog Input. A BMS/PLC point that reads a continuous signal (e.g., 0-10V, 4-20mA, or resistance).
**Common aliases:** analog input, AI point
**Related terms:** sensor, temperature, pressure, humidity, CO2
**BMS/ICS relevance:** Standard I/O type in all BMS controllers.
**Agent interpretation rules:** "AI" in a points list context means Analog Input, not Artificial Intelligence.
**Source-confirmed filtering rules:** Must appear in a points list or I/O schedule context.
**Confidence triggers:** exact_term_match +0.35, document_section_relevance +0.10
**Template trigger threshold:** 0.65
**Example usage:** "AI-1: Discharge Air Temperature, 10K thermistor"

---

## AO (Analog Output)

**Category:** I/O Types
**Definition:** Analog Output. A BMS/PLC point that sends a continuous control signal to a device.
**Common aliases:** analog output, AO point
**Related terms:** VFD speed command, valve position, damper position
**BMS/ICS relevance:** Standard I/O type.
**Agent interpretation rules:** Used for modulating control of actuators and drives.
**Source-confirmed filtering rules:** Must appear in points list context.
**Confidence triggers:** exact_term_match +0.35, document_section_relevance +0.10
**Template trigger threshold:** 0.65
**Example usage:** "AO-1: Supply Fan Speed Command, 0-10V"

---

## BI (Binary Input)

**Category:** I/O Types
**Definition:** Binary Input. A BMS/PLC point that reads a two-state signal (on/off, open/closed).
**Common aliases:** digital input, DI, binary input, status input
**Related terms:** fan status, pump status, alarm contact, flow switch
**BMS/ICS relevance:** Standard I/O type.
**Agent interpretation rules:** Status points are typically BI.
**Source-confirmed filtering rules:** Must appear in points list context.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.65
**Example usage:** "BI-1: Supply Fan Status, dry contact"

---

## BO (Binary Output)

**Category:** I/O Types
**Definition:** Binary Output. A BMS/PLC point that sends a two-state command signal.
**Common aliases:** digital output, DO, binary output, relay output
**Related terms:** fan command, pump command, enable, relay
**BMS/ICS relevance:** Standard I/O type.
**Agent interpretation rules:** Enable/command points are typically BO.
**Source-confirmed filtering rules:** Must appear in points list context.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.65
**Example usage:** "BO-1: Supply Fan Enable, 24VAC relay"

---

## UI (Universal Input)

**Category:** I/O Types
**Definition:** Universal Input. A configurable BMS input point that can accept multiple signal types.
**Common aliases:** universal input, configurable input
**Related terms:** sensor, temperature, pressure
**BMS/ICS relevance:** Common on modern DDC controllers.
**Agent interpretation rules:** UI may replace AI/BI depending on controller platform.
**Source-confirmed filtering rules:** Must appear in points list or I/O schedule context.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.65
**Example usage:** "UI-1: Space Temperature, 10K thermistor or 4-20mA"

---

## UO (Universal Output)

**Category:** I/O Types
**Definition:** Universal Output. A configurable BMS output point.
**Common aliases:** universal output, configurable output
**Related terms:** actuator, valve, damper, VFD
**BMS/ICS relevance:** Common on modern DDC controllers.
**Source-confirmed filtering rules:** Must appear in points list or I/O schedule context.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.65
**Example usage:** "UO-1: Heating Valve Position, 0-10V"

---

## Sensor

**Category:** Sensors
**Definition:** A device that measures a physical variable and converts it to an electrical signal.
**Common aliases:** transmitter, transducer, probe
**Related terms:** temperature sensor, pressure sensor, humidity sensor, CO2 sensor, AI point
**BMS/ICS relevance:** Fundamental to all BMS systems.
**Agent interpretation rules:** "Sensor" alone does not confirm a specific type.
**Source-confirmed filtering rules:** Must appear with context to trigger specific point generation.
**Confidence triggers:** exact_term_match +0.35, nearby_technical_context +0.20
**Template trigger threshold:** 0.60
**Example usage:** "Install a new discharge air temperature sensor on RTU-1."

---

## Space Temperature Sensor

**Category:** Sensors
**Definition:** A sensor that measures the air temperature in an occupied zone.
**Common aliases:** room temperature sensor, zone temperature sensor, space temp, SPT
**Related terms:** thermostat, VAV, FCU, setpoint, occupied mode
**BMS/ICS relevance:** One of the most common BMS points.
**Agent interpretation rules:** Implies zone-level control. May also include setpoint adjustment.
**Source-confirmed filtering rules:** Must appear explicitly or as clear alias.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.65
**Example usage:** "Each VAV box shall have a wall-mounted space temperature sensor."

---

## Supply Air Temperature

**Category:** Sensors
**Definition:** The temperature of air leaving a cooling or heating coil, measured in the supply ductwork.
**Common aliases:** discharge air temperature, DAT, SAT, supply air temp
**Related terms:** AHU, RTU, setpoint, cooling coil, heating coil
**BMS/ICS relevance:** Key control variable for AHU and RTU sequences.
**Source-confirmed filtering rules:** Must appear explicitly or as clear alias.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.65
**Example usage:** "The RTU shall maintain a discharge air temperature setpoint of 55°F."

---

## Return Air Temperature

**Category:** Sensors
**Definition:** Temperature of air returning from the conditioned space to the air handler.
**Common aliases:** return air temp, RAT
**Related terms:** AHU, mixed air, economizer, return air humidity
**BMS/ICS relevance:** Used in economizer and mixed air control.
**Source-confirmed filtering rules:** Must appear explicitly or as clear alias.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.65
**Example usage:** "The BMS shall monitor return air temperature at AHU-1."

---

## Mixed Air Temperature

**Category:** Sensors
**Definition:** Temperature of the mixture of outside air and return air before the cooling coil.
**Common aliases:** mixed air temp, MAT
**Related terms:** AHU, economizer, OA damper, RA damper
**BMS/ICS relevance:** Key economizer control variable.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.65
**Example usage:** "The mixed air temperature shall be used for economizer low limit control."

---

## Duct Static Pressure

**Category:** Sensors
**Definition:** The static pressure measured in a supply air duct, used to control VFD speed.
**Common aliases:** static pressure, duct pressure, DSP
**Related terms:** VFD, supply fan, VAV, setpoint
**BMS/ICS relevance:** Primary variable for supply fan VFD control.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.65
**Example usage:** "The supply fan VFD shall maintain duct static pressure setpoint."

---

## Sequence of Operation

**Category:** Documentation Terms
**Definition:** A written description of how a controlled system operates through its various modes.
**Common aliases:** sequence, SOO, controls sequence, operating sequence
**Related terms:** setpoint, mode, alarm, BMS, points list
**BMS/ICS relevance:** Core deliverable for BMS programming.
**Agent interpretation rules:** Implies the document is controls-scope.
**Source-confirmed filtering rules:** Must appear explicitly or as alias.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.60
**Example usage:** "Refer to the sequence of operation for complete control logic."

---

## Points List

**Category:** Documentation Terms
**Definition:** A tabulated list of all BMS input/output points for a system or project.
**Common aliases:** I/O list, point schedule, control point list, points schedule
**Related terms:** AI, AO, BI, BO, UI, UO, controller, BMS
**BMS/ICS relevance:** Primary deliverable for BMS design and programming.
**Agent interpretation rules:** Points list generation requires at least 0.70 confidence on the associated equipment.
**Source-confirmed filtering rules:** Must appear explicitly or be clearly implied by I/O schedule context.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20, document_section_relevance +0.10
**Template trigger threshold:** 0.70
**Example usage:** "The contractor shall submit a points list for Owner review."

---

## Trend Log

**Category:** Documentation Terms
**Definition:** A BMS record of a point's values over time for analysis and diagnostics.
**Common aliases:** trend, trending, data logging, historical data
**Related terms:** BMS, historian, alarm, setpoint
**BMS/ICS relevance:** Common commissioning and diagnostic requirement.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.60
**Example usage:** "The BMS shall trend all critical zone temperatures at 15-minute intervals."

---

## Alarm

**Category:** Documentation Terms
**Definition:** A BMS notification triggered when a monitored point exceeds a defined limit.
**Common aliases:** alert, fault, alarm point
**Related terms:** BMS, trend log, notification, setpoint
**BMS/ICS relevance:** Standard deliverable in all BMS systems.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.55
**Example usage:** "A high-temperature alarm shall be generated when discharge air exceeds 90°F."

---

## Retrofit

**Category:** Retrofit Terms
**Definition:** The replacement or upgrade of existing BMS equipment in an operating building.
**Common aliases:** controls upgrade, DDC retrofit, controller replacement, system upgrade
**Related terms:** controller replacement, as-built, existing controller, network trunk
**BMS/ICS relevance:** Primary project type for SpecFlow AI.
**Agent interpretation rules:** Retrofit context means existing conditions must be verified.
**Source-confirmed filtering rules:** Must appear explicitly or be clearly implied by "existing" + "replace" context.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20, nearby_technical_context +0.20
**Template trigger threshold:** 0.60
**Example usage:** "This project is a BMS retrofit replacing existing pneumatic controls."

---

## Controller Replacement

**Category:** Retrofit Terms
**Definition:** The physical replacement of an existing BMS controller with a new unit.
**Common aliases:** swap, replace controller, new controller, DDC replacement
**Related terms:** retrofit, as-built, field verification, wiring
**BMS/ICS relevance:** Core scope item in retrofit projects.
**Source-confirmed filtering rules:** Must appear explicitly or be implied by "replace existing controllers."
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.65
**Example usage:** "Replace existing controllers with new BACnet/IP DDC controllers."

---

## Commissioning

**Category:** Commissioning Terms
**Definition:** The systematic process of verifying that a BMS system is installed and operating per design intent.
**Common aliases:** Cx, commissioning process, systems commissioning, functional testing
**Related terms:** functional test, field verification, sequence of operation, setpoint verification
**BMS/ICS relevance:** End-of-project deliverable.
**Agent interpretation rules:** Commissioning implies a formal functional test process.
**Source-confirmed filtering rules:** Must appear explicitly or as alias.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.65
**Example usage:** "The BAS contractor shall perform commissioning prior to Owner acceptance."

---

## Functional Test

**Category:** Commissioning Terms
**Definition:** A test that verifies the operation of a controlled system through all modes defined in the sequence of operation.
**Common aliases:** functional performance test, FPT, functional verification
**Related terms:** commissioning, sequence of operation, setpoint, alarm
**BMS/ICS relevance:** Core commissioning deliverable.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.65
**Example usage:** "A functional test shall be performed for each AHU before substantial completion."

---

## Field Verification

**Category:** Commissioning Terms
**Definition:** Physical verification of installed equipment, wiring, and network connections in the field.
**Common aliases:** point-to-point checkout, P2P checkout, field checkout, site verification
**Related terms:** commissioning, controller location, wiring verification, network connectivity
**BMS/ICS relevance:** Pre-commissioning activity.
**Source-confirmed filtering rules:** Must appear explicitly or as alias.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.50
**Example usage:** "The BAS contractor shall perform field verification of all points prior to commissioning."

---

## RFI

**Category:** Documentation Terms
**Definition:** Request for Information. A formal question submitted to the design team to clarify scope or design intent.
**Common aliases:** request for information, RFI log, field question
**Related terms:** submittal, clarification, scope gap, design issue
**BMS/ICS relevance:** Common in design-build and retrofit projects.
**Source-confirmed filtering rules:** Must appear explicitly or be implied by ambiguous scope.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.60
**Example usage:** "An RFI shall be submitted regarding the existing controller wiring condition."

---

## Submittal

**Category:** Documentation Terms
**Definition:** Documentation submitted by a contractor for design team review and approval before installation.
**Common aliases:** shop drawing, product data, cut sheet submittal, O&M submittal
**Related terms:** cut sheet, product data, O&M manual, approval
**BMS/ICS relevance:** Required deliverable for all BMS projects.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.60
**Example usage:** "Submit controller product data for Engineer review prior to procurement."

---

## As-Built

**Category:** Documentation Terms
**Definition:** Drawings and documentation that reflect the actual installed conditions after construction.
**Common aliases:** record drawings, as-installed, as-built drawings
**Related terms:** CAD, wiring diagram, points list, controller schedule
**BMS/ICS relevance:** Required closeout deliverable.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.60
**Example usage:** "The contractor shall provide as-built drawings within 30 days of substantial completion."

---

## Network Trunk

**Category:** Communication Protocols
**Definition:** A main communication cable segment connecting BMS controllers on a BACnet MS/TP or similar network.
**Common aliases:** trunk cable, BACnet trunk, field bus trunk, communication trunk
**Related terms:** BACnet MS/TP, controller, field bus, termination
**BMS/ICS relevance:** Physical network infrastructure for field-level BMS.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.60
**Example usage:** "The BACnet MS/TP network trunk shall be home-run to the floor controller."

---

## OT Network

**Category:** OT Cybersecurity
**Definition:** Operational Technology network. The network layer connecting industrial control systems and BMS devices.
**Common aliases:** controls network, BMS network, field network, OT LAN
**Related terms:** VLAN, segmentation, firewall, Purdue Model, BACnet
**BMS/ICS relevance:** Core concept in OT cybersecurity for BMS and ICS.
**Agent interpretation rules:** OT network is distinct from IT network. Do not assume OT segmentation exists unless documented.
**Source-confirmed filtering rules:** Must appear explicitly or be clearly implied by cybersecurity context.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20, nearby_technical_context +0.20
**Template trigger threshold:** 0.65
**Example usage:** "The BMS shall reside on a dedicated OT network segment."

---

## Purdue Model

**Category:** OT Cybersecurity
**Definition:** A reference model for ICS/OT network segmentation that divides systems into hierarchical levels (0-5).
**Common aliases:** ISA-95 model, Purdue reference model, ICS security zones
**Related terms:** OT network, VLAN, segmentation, firewall, DMZ
**BMS/ICS relevance:** Standard OT security architecture reference.
**Agent interpretation rules:** Only relevant in OT cybersecurity or ICS context documents.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.65
**Example usage:** "Controls network design shall follow the Purdue Model segmentation approach."

---

## Segmentation

**Category:** OT Cybersecurity
**Definition:** The division of a network into isolated segments to limit the spread of security threats.
**Common aliases:** network segmentation, zone segmentation, micro-segmentation
**Related terms:** VLAN, firewall, OT network, Purdue Model
**BMS/ICS relevance:** Core OT security practice.
**Source-confirmed filtering rules:** Must appear in a network or cybersecurity context.
**Confidence triggers:** exact_term_match +0.35, nearby_technical_context +0.20
**Template trigger threshold:** 0.65
**Example usage:** "BMS controls network shall be segmented from corporate IT."

---

## VLAN

**Category:** Network Terms
**Definition:** Virtual Local Area Network. A logical subdivision of a physical network.
**Common aliases:** virtual LAN, network VLAN, controls VLAN
**Related terms:** OT network, segmentation, switch, firewall, BACnet/IP
**BMS/ICS relevance:** Used to isolate BMS traffic from IT traffic.
**Agent interpretation rules:** Do not assume VLAN from "network" alone.
**Source-confirmed filtering rules:** "VLAN" must appear explicitly.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.65
**Example usage:** "Assign all BMS controllers to VLAN 100."

---

## Firewall

**Category:** OT Cybersecurity
**Definition:** A network device that controls traffic between network zones based on defined rules.
**Common aliases:** network firewall, OT firewall, DMZ firewall, perimeter firewall
**Related terms:** VLAN, segmentation, OT network, remote access
**BMS/ICS relevance:** Required at the IT/OT boundary for secure BMS architectures.
**Source-confirmed filtering rules:** "Firewall" must appear explicitly.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.65
**Example usage:** "A firewall shall be installed between the BMS VLAN and the corporate network."

---

## Remote Access

**Category:** OT Cybersecurity
**Definition:** The ability to connect to a BMS or OT system from outside the local network.
**Common aliases:** remote connection, VPN access, remote monitoring, remote support
**Related terms:** VPN, firewall, OT network, service account
**BMS/ICS relevance:** Common in BMS service contracts. Major OT security risk if uncontrolled.
**Agent interpretation rules:** Remote access implies need for VPN and access control review.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35, nearby_technical_context +0.20
**Template trigger threshold:** 0.60
**Example usage:** "Remote access to the BMS shall be restricted to authorized personnel via VPN."

---

## Service Account

**Category:** OT Cybersecurity
**Definition:** A non-personal account used by software services or automated systems to access resources.
**Common aliases:** system account, application account, service user
**Related terms:** remote access, firewall, least privilege, BMS, SCADA
**BMS/ICS relevance:** OT security practice — service accounts should follow least privilege.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.60
**Example usage:** "BMS service accounts shall follow least privilege access principles."

---

## Least Privilege

**Category:** OT Cybersecurity
**Definition:** A security principle that limits user and system accounts to only the access required for their function.
**Common aliases:** minimum necessary access, principle of least privilege
**Related terms:** service account, remote access, firewall, OT network
**BMS/ICS relevance:** Core OT cybersecurity requirement for BMS and ICS.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.60
**Example usage:** "All BMS user accounts shall adhere to least privilege access controls."

---

## Actuator

**Category:** Actuators
**Definition:** A device that receives a control signal and moves a mechanical component such as a damper or valve.
**Common aliases:** motor actuator, valve actuator, damper actuator, spring return actuator
**Related terms:** damper, valve, AO, UO, modulating, on/off
**BMS/ICS relevance:** Physical output device in BMS systems.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35, nearby_technical_context +0.20
**Template trigger threshold:** 0.60
**Example usage:** "Provide a modulating actuator on the chilled water valve."

---

## Relay

**Category:** Electrical/Control Panel Terms
**Definition:** An electrically operated switch used to control a load circuit from a control signal.
**Common aliases:** interlock relay, control relay, pilot relay
**Related terms:** BO, binary output, fan command, enable circuit
**BMS/ICS relevance:** Used in control panels for binary output isolation.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.55
**Example usage:** "A relay shall be provided in the control panel for fan enable isolation."

---

## Transformer

**Category:** Electrical/Control Panel Terms
**Definition:** An electrical device that changes voltage levels. Common in BMS for 24VAC control power.
**Common aliases:** control transformer, 120/24V transformer, step-down transformer
**Related terms:** control panel, 24VAC, power supply, BMS
**BMS/ICS relevance:** Standard component in DDC control panels.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35
**Template trigger threshold:** 0.55
**Example usage:** "A 120/24VAC transformer shall power the DDC controller."

---

## Thermostat

**Category:** Sensors
**Definition:** A wall-mounted device that senses space temperature and may include setpoint adjustment and occupancy override.
**Common aliases:** room thermostat, digital thermostat, programmable thermostat
**Related terms:** space temperature sensor, setpoint, occupied mode, FCU, VAV
**BMS/ICS relevance:** May be standalone or integrated with BMS.
**Agent interpretation rules:** Traditional thermostat is not a DDC controller — do not assume BACnet from thermostat.
**Source-confirmed filtering rules:** Must appear explicitly.
**Confidence triggers:** exact_term_match +0.35, alias_synonym_match +0.20
**Template trigger threshold:** 0.60
**Example usage:** "Replace existing thermostats with BACnet-enabled communicating thermostats."
