# SpecFlow AI — BMS / ICS / PLC Vocabulary

> Machine-readable vocabulary for SpecFlow AI confidence scoring.
> Format: grouped by `term_type`, sorted by `weight` descending.
> To add a term: add a row to the correct section. The scorer picks it up automatically.
> KB presence alone = confidence 0.00. Source document must confirm every detection.

---

## Term Type Index

| Term Type | Count | Purpose |
|---|---:|---|
| equipment_type | 28 | HVAC and mechanical equipment |
| plc_hardware | 22 | PLC racks, CPUs, I/O modules |
| industrial_sensor | 30 | Process and field sensors |
| panel_component | 18 | Control panel hardware |
| protocol | 16 | Communication protocols |
| platform | 20 | BMS, SCADA, HMI, and software platforms |
| controller_model | 20 | Named controller models |
| manufacturer | 60 | Equipment and device manufacturers |
| io_type | 6 | I/O point types |
| signal_type | 10 | Signal and wiring types |
| eng_unit | 9 | Engineering units |
| doc_signal | 11 | Document and deliverable terms |
| point_name | 30 | Standard BMS point name patterns |
| skip_term | 8 | Terms to suppress from workflow output |

---

## equipment_type

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| ahu | 1.00 | all | air handling unit, air handler, air-handling unit, AHU | Central HVAC air handler |
| fcu | 1.00 | all | fan coil unit, fan-coil, fancoil, FCU | Terminal fan coil |
| rtu | 1.00 | all | rooftop unit, rooftop units, roof top unit, packaged unit, RTU | Packaged rooftop HVAC |
| vav | 1.00 | all | variable air volume, vav box, vav terminal, VAV | Variable volume terminal |
| boiler | 0.90 | all | boiler, BLR, hot water boiler, steam boiler, HWB | Hydronic heating |
| chiller | 0.90 | all | chiller, CHL, centrifugal chiller, scroll chiller, water-cooled chiller | Central cooling plant |
| cooling tower | 0.90 | all | cooling tower, CT, condenser water tower | Condenser heat rejection |
| doas | 0.90 | all | dedicated outdoor air, DOAS, dedicated OA unit | 100% OA ventilation unit |
| exhaust fan | 0.90 | all | exhaust fan, EF, supply fan, SF, return fan, RF | Air movement fan |
| fpb | 0.90 | all | fan powered box, fan-powered terminal, FPB, FTU, PIU | Fan-powered VAV terminal |
| heat pump | 0.90 | all | heat pump, packaged heat pump, HP, ASHP, GSHP, WSHP | Reversible refrigerant system |
| mau | 0.90 | all | makeup air unit, make-up air, make up air, MAU, MUA | Outdoor air conditioning |
| vfd | 0.90 | all | variable frequency drive, VFD, variable speed drive, VSD, drive, inverter | Motor speed control |
| vrf | 0.90 | all | variable refrigerant flow, VRF, variable refrigerant volume, VRV | Multi-split refrigerant system |
| crac | 0.80 | all | computer room air conditioner, CRAC, CRAH, precision cooling | Data center cooling |
| erv | 0.80 | all | energy recovery ventilator, ERV, heat recovery ventilator, HRV | Ventilation with heat recovery |
| pump | 0.80 | all | pump, PMP, circulating pump, condenser pump, chilled water pump, CWP, HWP | Hydronic fluid mover |
| split system | 0.80 | all | split system, mini split, mini-split, ductless, PTAC, PTHP | Ductless AC system |
| unit heater | 0.80 | all | unit heater, UH, cabinet unit heater, CUH | Fin-tube space heater |
| damper | 0.80 | all | damper, OA damper, RA damper, mixing damper, isolation damper, fire damper | Airflow control device |
| valve | 0.80 | all | valve, control valve, CHW valve, HW valve, CW valve, 2-way valve, 3-way valve | Fluid flow control device |
| actuator | 0.75 | all | actuator, damper actuator, valve actuator, spring return, modulating actuator | Mechanical mover |
| humidifier | 0.75 | all | humidifier, steam humidifier, HUM, humidity control | Moisture addition |
| heat exchanger | 0.75 | all | heat exchanger, HX, plate exchanger, shell and tube | Fluid heat transfer |
| motor | 0.70 | all | motor, electric motor, induction motor, NEMA motor | Rotating machine |
| compressor | 0.70 | all | compressor, scroll compressor, screw compressor, reciprocating | Refrigerant compression |
| economizer | 0.70 | all | economizer, economiser, free cooling, OA economizer | OA-based free cooling |
| cooling coil | 0.65 | all | cooling coil, chilled water coil, DX coil, evaporator coil | Air cooling element |

---

## plc_hardware

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| PLC | 1.00 | all | programmable logic controller, programmable controller, logic controller | Core ICS control device |
| CPU module | 0.90 | all | CPU, processor module, PLC processor, controller CPU | PLC brain |
| I/O module | 0.90 | all | I/O card, input module, output module, analog card, digital card | PLC I/O expansion |
| rack | 0.85 | all | PLC rack, chassis, backplane, mounting rail | PLC mounting hardware |
| power supply module | 0.85 | all | PS module, PLC power supply, 24VDC supply, rack PSU | PLC power feed |
| analog input module | 0.85 | all | AI module, 4-20mA input card, analog input card | PLC analog sensing |
| analog output module | 0.85 | all | AO module, 4-20mA output card, analog output card | PLC analog control |
| digital input module | 0.85 | all | DI module, discrete input card, binary input module | PLC digital sensing |
| digital output module | 0.85 | all | DO module, relay output card, discrete output module | PLC digital control |
| communication module | 0.85 | all | comm module, network card, Ethernet module, EtherNet/IP card, PROFINET card | PLC network interface |
| safety PLC | 0.85 | all | safety controller, fail-safe PLC, SIL controller, safety relay controller | Safety-rated PLC |
| remote I/O | 0.80 | all | remote I/O rack, distributed I/O, RIO, ET200, Point I/O | Distributed PLC I/O |
| HMI panel | 0.80 | all | HMI, operator panel, touchscreen, HMI terminal, operator interface | PLC operator display |
| motion controller | 0.75 | all | servo drive, motion axis, servo controller, drive controller | PLC motion control |
| field panel | 0.75 | all | control panel, MCP, local control panel, field control panel | On-site panel |
| edge controller | 0.70 | all | edge device, IIoT gateway, edge compute, PAC | Edge computing device |
| PAC | 0.70 | all | programmable automation controller, PAC | Advanced PLC form factor |
| DCS | 0.70 | all | distributed control system, process control system | Large-scale process control |
| RTU | 0.70 | ics | remote terminal unit, field RTU, SCADA RTU | Remote data acquisition |
| IED | 0.65 | all | intelligent electronic device, protection relay, IED | Smart field device |
| safety relay | 0.65 | all | safety relay module, E-stop relay, SIL relay | Safety circuit device |
| terminal block | 0.60 | all | terminal strip, DIN rail terminal, screw terminal | Panel wiring connection |

---

## industrial_sensor

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| temperature sensor | 1.00 | all | temp sensor, temperature transmitter, RTD, thermocouple, NTC, thermistor | Temperature measurement |
| pressure sensor | 1.00 | all | pressure transmitter, pressure transducer, PT, pressure switch, gauge | Pressure measurement |
| flow meter | 1.00 | all | flow transmitter, flowmeter, FT, magnetic flowmeter, ultrasonic flow, turbine flow, vortex flow | Flow measurement |
| level sensor | 0.90 | all | level transmitter, LT, level switch, float switch, ultrasonic level | Tank or vessel level |
| CO2 sensor | 0.90 | all | CO2 transmitter, carbon dioxide sensor, IAQ sensor, CO2 meter | Indoor air quality |
| humidity sensor | 0.90 | all | humidity transmitter, RH sensor, humidity/temp sensor, moisture sensor | Relative humidity |
| differential pressure | 0.90 | all | DP transmitter, differential pressure sensor, DP switch, DSP, BSP | Pressure difference |
| current sensor | 0.90 | all | current transformer, CT, current switch, ampere meter, power monitor | Electrical current |
| occupancy sensor | 0.85 | all | occupancy detector, PIR sensor, motion sensor, presence sensor | Occupancy detection |
| CO sensor | 0.85 | all | carbon monoxide sensor, CO transmitter, CO detector | CO detection |
| thermocouple | 0.85 | all | T/C, type K thermocouple, type J, type T, type E | High-temp sensing |
| RTD | 0.85 | all | resistance temperature detector, Pt100, Pt1000, PT100, PT1000 | Precision temperature |
| air quality sensor | 0.85 | all | IAQ sensor, VOC sensor, particulate sensor, PM2.5, air quality monitor | Multi-parameter IAQ |
| liquid temperature | 0.80 | all | pipe temp sensor, immersion sensor, well sensor, pipe strap sensor | Fluid temperature |
| duct sensor | 0.80 | all | duct temperature sensor, duct probe, insertion sensor, averaging element | In-duct measurement |
| outdoor air sensor | 0.80 | all | OA sensor, outdoor temp, ambient sensor, weather station | Outdoor conditions |
| vibration sensor | 0.75 | all | vibration transmitter, accelerometer, vibration switch | Machine health |
| speed sensor | 0.75 | all | RPM sensor, tachometer, encoder, proximity sensor, hall effect | Rotational speed |
| limit switch | 0.75 | all | position switch, end-of-travel switch, valve position switch | Mechanical position |
| condensate sensor | 0.70 | all | condensate pan switch, float switch, overflow sensor | Condensate detection |
| smoke detector | 0.70 | all | smoke sensor, duct smoke detector, air sampling, ionization detector | Smoke detection |
| freeze stat | 0.70 | all | low limit thermostat, coil freeze protection, freeze protection | Freeze protection |
| power meter | 0.70 | all | energy meter, kWh meter, power monitor, demand meter, BTU meter | Energy measurement |
| gas detector | 0.70 | all | refrigerant detector, natural gas sensor, leak detector, gas monitor | Gas leak detection |
| pH sensor | 0.65 | all | pH transmitter, pH probe, water quality | Water chemistry |
| conductivity sensor | 0.65 | all | conductivity transmitter, TDS sensor | Water quality |
| light sensor | 0.65 | all | light level sensor, photocell, lux sensor, daylight sensor | Lighting control |
| door contact | 0.60 | all | door switch, magnetic contact, door status, tamper switch | Access/security |
| water leak sensor | 0.60 | all | leak detection cable, WLD, moisture rope, flood sensor | Water intrusion |
| airflow switch | 0.60 | all | sail switch, airflow sensor, differential pressure switch, paddle switch | Fan proof |

---

## panel_component

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| circuit breaker | 0.90 | all | breaker, MCB, MCCB, branch breaker, thermal magnetic | Overcurrent protection |
| contactor | 0.90 | all | motor contactor, IEC contactor, line contactor, starter contactor | Motor switching |
| relay | 0.85 | all | control relay, SPDT relay, DPDT relay, interlock relay, pilot relay | Signal switching |
| transformer | 0.85 | all | control transformer, 120/24VAC, step-down transformer, multi-tap transformer | Control power |
| power supply | 0.85 | all | 24VDC supply, DC power supply, SMPS, panel power supply | DC power conversion |
| disconnect switch | 0.85 | all | safety switch, motor disconnect, lockout, fusible disconnect | Power isolation |
| fuse | 0.80 | all | control fuse, fuse block, fuse holder, fuse protection | Short circuit protection |
| overload relay | 0.80 | all | motor overload, thermal overload, electronic overload, OL | Motor overload protection |
| soft starter | 0.80 | all | reduced voltage starter, RVS, motor soft start | Motor starting |
| UPS | 0.80 | all | uninterruptible power supply, battery backup, panel UPS, backup power | Power backup |
| surge protector | 0.75 | all | SPD, surge protection device, transient protection, lightning protection | Surge protection |
| enclosure | 0.75 | all | NEMA 1 enclosure, NEMA 4 enclosure, panel box, steel enclosure, Hoffman box | Panel housing |
| DIN rail | 0.70 | all | mounting rail, 35mm DIN, DIN rail mount | Component mounting |
| terminal strip | 0.70 | all | terminal block, screw terminal, field terminal, wiring terminal | Panel termination |
| pilot light | 0.65 | all | indicator light, status light, LED indicator, signal light | Status indication |
| selector switch | 0.65 | all | HOA switch, hand-off-auto, rotary switch, mode switch | Manual override |
| push button | 0.65 | all | E-stop, emergency stop, momentary push button, reset button | Manual control |
| horn strobe | 0.60 | all | alarm horn, audible visual alarm, strobe, AV device | Alarm annunciation |

---

## protocol

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| BACnet | 1.00 | all | BACnet/IP, BACnet IP, BACnet MS/TP, BACnet MSTP, bacnet | Primary BAS protocol |
| MS/TP | 1.00 | all | MSTP, MS-TP, mstp, master slave token passing, BACnet serial | BACnet field bus |
| Modbus | 0.90 | all | Modbus TCP, Modbus RTU, Modbus RS-485, modbus | Industrial register protocol |
| EtherNet/IP | 0.90 | all | Ethernet/IP, EIP, CIP, common industrial protocol | Rockwell/Allen-Bradley network |
| PROFINET | 0.90 | all | profinet, PROFINET IO, PN | Siemens industrial Ethernet |
| PROFIBUS | 0.85 | all | profibus, PROFIBUS DP, PROFIBUS PA | Siemens field bus |
| OPC UA | 0.85 | all | OPC-UA, OPC Unified Architecture, OPC server | Secure OT data exchange |
| MQTT | 0.80 | all | MQTT broker, MQTT protocol | IoT messaging protocol |
| DeviceNet | 0.80 | all | device net, CIP DeviceNet | Rockwell field bus |
| LON | 0.80 | all | LonWorks, LON, FTT10, FTT-10, LonTalk | Legacy BAS protocol |
| EtherCAT | 0.75 | all | ethercat, EtherCAT network | High-speed Beckhoff protocol |
| CC-Link | 0.75 | all | CC-Link IE, CC-Link field | Mitsubishi field bus |
| Foundation Fieldbus | 0.75 | all | FF, FOUNDATION fieldbus, H1, HSE | Process industry protocol |
| DNP3 | 0.75 | all | DNP 3.0, Distributed Network Protocol | Utility SCADA protocol |
| KNX | 0.65 | all | KNX, EIB, KNX/IP | Building lighting/HVAC |
| IP | 0.60 | all | Ethernet, TCP/IP, LAN, network, IP network | Network transport layer |

---

## platform

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| BAS | 1.00 | all | building automation system, building management system, BMS, controls system | Core BAS platform |
| DDC | 0.90 | all | direct digital control, digital controls, building automation | DDC control system |
| Niagara | 0.90 | climatec | Niagara Framework, Niagara 4, N4, Tridium Niagara | Tridium standard |
| Metasys | 0.90 | all | Metasys, JCI Metasys, Johnson Controls Metasys | JCI front-end |
| BACtalk | 0.90 | alerton | BACtalk, Alerton BACtalk, VLC, VLCP | Alerton primary platform |
| Studio 5000 | 0.90 | all | Logix 5000, RSLogix 5000, Studio5000, Rockwell Studio | Allen-Bradley PLC software |
| TIA Portal | 0.90 | all | TIA, Siemens TIA, Step 7, STEP 7, TIA Portal V16 | Siemens PLC software |
| FactoryTalk | 0.85 | all | FactoryTalk View, FT View, RSView, Rockwell SCADA | Rockwell SCADA/HMI |
| Ignition | 0.85 | all | Inductive Automation Ignition, Ignition SCADA, Ignition HMI | Modern SCADA platform |
| Wonderware | 0.85 | all | Wonderware InTouch, Wonderware System Platform, AVEVA InTouch | SCADA HMI platform |
| iFIX | 0.80 | all | GE iFIX, Proficy iFIX, HMI/SCADA iFIX | GE SCADA platform |
| Desigo | 0.80 | all | Desigo CC, Desigo Insight, PXC, Siemens Desigo | Siemens BMS platform |
| Compass | 0.80 | alerton | Alerton Compass, Compass software | Alerton front-end |
| WEBs | 0.80 | climatec | WEBs AX, WEBs-AX, Honeywell WEBs | Honeywell Climatec alternate |
| HVAC | 0.80 | all | heating ventilating air conditioning, mechanical system, HVAC system | Mechanical domain |
| OSIsoft PI | 0.75 | all | PI System, AVEVA PI, OSIsoft, PI historian | Data historian platform |
| GX Works | 0.75 | all | GX Works 2, GX Works 3, Mitsubishi GX | Mitsubishi PLC software |
| Sysmac Studio | 0.75 | all | Sysmac, Omron Sysmac, NJ/NX series software | Omron PLC software |
| Unity Pro | 0.75 | all | Unity Pro, EcoStruxure Control Expert, Schneider Unity | Schneider PLC software |
| Citect | 0.70 | all | Citect SCADA, AVEVA Citect, CitectSCADA | SCADA platform |

---

## controller_model

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| ECY-303 | 1.00 | controlworks | ECY303 | Distech AI=3 DI=3 |
| ECY-S1000 | 1.00 | controlworks | ECY-S1000 3 mod, S1000 3 mod | Distech AI=3 DI=5 AO=5 DO=1 |
| ECY-TU-203 | 1.00 | controlworks | ECY-203 | Distech AI=1 DI=3 AO=2 DO=8 |
| ECY-VAV | 1.00 | controlworks | ECY-VAV com sensor | Distech VAV controller |
| JACE | 1.00 | climatec | JACE-8000, JACE 8000, web supervisor | Tridium supervisory controller |
| ControlLogix | 0.90 | all | CLX, 1756, Allen-Bradley ControlLogix | Rockwell large PLC |
| CompactLogix | 0.90 | all | 1769, Allen-Bradley CompactLogix, CLX compact | Rockwell mid-range PLC |
| MicroLogix | 0.85 | all | MicroLogix 1100, MicroLogix 1400, ML1400 | Rockwell small PLC |
| S7-300 | 0.90 | all | Siemens S7-300, CPU 315, CPU 314 | Siemens mid-range PLC |
| S7-400 | 0.90 | all | Siemens S7-400, CPU 414, CPU 416 | Siemens large PLC |
| S7-1200 | 0.90 | all | Siemens S7-1200, CPU 1212C, CPU 1214C | Siemens compact PLC |
| S7-1500 | 0.90 | all | Siemens S7-1500, CPU 1511, CPU 1516 | Siemens advanced PLC |
| BCM | 0.90 | alerton | BCM-256, BCM-256L, building controller | Alerton building controller |
| Smart Equipment Controller | 0.90 | all | JCI TEC, SEC, SmartEquip, TEC3000 | JCI RTU controller |
| VAVII | 0.90 | alerton | VAV II, VAVII, Alerton VAV | Alerton VAV controller |
| NAE | 0.80 | all | NAE-5500, NAE35, Network Automation Engine | JCI supervisory |
| NCE | 0.80 | all | NCE25, Network Control Engine | JCI field controller |
| VLC | 0.80 | alerton | VLC-850, VLC-1000, Alerton VLC | Alerton VAV controller |
| Q Series | 0.75 | all | Mitsubishi Q Series, QCPU | Mitsubishi large PLC |
| CJ Series | 0.75 | all | Omron CJ2, CJ1, CS1 | Omron mid-range PLC |

---

## manufacturer

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| Alerton | 1.00 | alerton | Alerton Technologies | BAS manufacturer |
| Climatec | 1.00 | climatec | Climatec Inc | BAS contractor |
| Johnson Controls | 1.00 | all | JCI, York, Metasys, Johnson Controls Inc | Major BAS/HVAC OEM |
| Siemens | 1.00 | all | Siemens Building Technologies, SBT, Landis & Gyr | Major BAS/PLC OEM |
| Rockwell Automation | 1.00 | all | Allen-Bradley, Allen Bradley, Rockwell, A-B | Major PLC OEM |
| Schneider Electric | 0.95 | all | Schneider, Square D, Modicon, APC, AVEVA | Major PLC/BAS/SCADA OEM |
| Honeywell | 0.90 | all | Honeywell Analytics, Resideo, Honeywell Home | Major BAS/sensor OEM |
| Tridium | 0.90 | climatec | Tridium Inc, Niagara Framework | JACE platform |
| Distech Controls | 0.90 | controlworks | Distech, ECY, ECB, ECL | Controlworks preferred BAS |
| ABB | 0.90 | all | ABB Ltd, ABB drives, ABB robotics | Drives and PLC OEM |
| Mitsubishi Electric | 0.90 | all | Mitsubishi, MELSEC, GOT HMI | Japanese PLC/drive OEM |
| Omron | 0.90 | all | Omron Automation, SYSMAC | Japanese PLC OEM |
| Emerson | 0.90 | all | Emerson Electric, Fisher Controls, DeltaV, Rosemount | Process control OEM |
| Trane | 0.90 | all | Trane Technologies, Trane HVAC | HVAC OEM |
| Carrier | 0.90 | all | Carrier Global, Carrier HVAC | HVAC OEM |
| Daikin | 0.85 | all | Daikin Industries, Daikin Applied | VRF/HVAC OEM |
| Belimo | 0.85 | all | Belimo Aircontrols | Actuator specialist |
| Dwyer | 0.85 | controlworks | Dwyer Instruments | Sensors and instrumentation |
| Setra | 0.85 | controlworks | Setra Systems Inc | Pressure sensors |
| Greystone | 0.85 | controlworks | Greystone Energy Systems | BAS sensors |
| Senva | 0.85 | controlworks | Senva Inc | BAS sensors |
| Veris | 0.85 | controlworks | Veris Industries | Current sensors and meters |
| BAPI | 0.85 | controlworks | Building Automation Products Inc | BAS sensors |
| Mamac | 0.85 | climatec | MAMAC Systems | Sensors and transducers |
| Beckhoff | 0.85 | all | Beckhoff Automation, TwinCAT | PC-based PLC OEM |
| Phoenix Contact | 0.85 | all | Phoenix Contact GmbH | Terminal blocks and I/O |
| Wago | 0.80 | all | WAGO Corporation | Modular I/O |
| AutomationDirect | 0.80 | all | Automation Direct, CLICK PLC, Do-more | Low-cost PLC vendor |
| GE | 0.80 | all | GE Automation, GE Fanuc, Proficy | PLC/HMI/SCADA OEM |
| Keyence | 0.80 | all | Keyence Corp | Sensors and vision |
| Omega | 0.80 | all | Omega Engineering | Sensors and instrumentation |
| Vaisala | 0.80 | all | Vaisala Inc | Humidity/temp sensors |
| Eaton | 0.80 | all | Eaton Corporation | Electrical/power products |
| Danfoss | 0.80 | all | Danfoss Drives | VFDs and refrigeration |
| Yaskawa | 0.80 | all | Yaskawa Electric, Yaskawa drives | VFD and servo OEM |
| Rittal | 0.75 | all | Rittal GmbH | Enclosures |
| Hoffman | 0.75 | climatec | Hoffman Enclosures | Panel enclosures |
| Saginaw Control | 0.75 | climatec | Saginaw Control & Engineering | Panel enclosures |
| Opto 22 | 0.75 | all | Opto22, groov | PAC and I/O OEM |
| Red Lion | 0.75 | all | Red Lion Controls | HMI and protocol gateways |
| Moxa | 0.75 | all | Moxa Technologies | Industrial networking |
| Advantech | 0.75 | all | Advantech Co | Industrial computers |
| Contemporary Controls | 0.75 | controlworks | Contemporary Controls | BACnet routers/gateways |
| Functional Devices | 0.75 | controlworks | Functional Devices Inc, RIB relays | Relay modules |
| Kele | 0.75 | controlworks | Kele Inc | BAS components distributor |
| Onicon | 0.75 | climatec | Onicon Inc | Flow meters |
| DENT | 0.75 | controlworks | Dent Instruments, DENT Instruments | Power meters |
| Ebtron | 0.70 | all | Ebtron Inc | Airflow measurement |
| VFD manufacturer | 0.70 | all | drive manufacturer, inverter manufacturer | Generic VFD reference |
| Loytec | 0.70 | all | Loytec Electronics | BACnet devices |
| Sievert | 0.70 | all | Sievert Larsen | Valve actuators |
| Hays | 0.70 | all | Hays Cleveland | Flow measurement |
| Sage Metering | 0.70 | climatec | Sage Metering Inc | Gas flow meters |
| Sierra Monitor | 0.70 | climatec | Sierra Monitor Corporation | Gas detection |
| Palo Alto Networks | 0.70 | all | Palo Alto | OT network security |
| Cisco | 0.70 | all | Cisco Systems | Network switches/routers |
| Optigo Networks | 0.70 | climatec | Optigo | BACnet network optimization |

---

## io_type

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| AI | 1.00 | all | analog input, analogue input | Continuous signal input |
| AO | 1.00 | all | analog output, analogue output | Continuous signal output |
| DI | 1.00 | all | digital input, binary input, discrete input, BI | Two-state input |
| DO | 1.00 | all | digital output, binary output, discrete output, BO, relay output | Two-state output |
| UI | 0.90 | all | universal input | Configurable input (Distech) |
| UO | 0.90 | all | universal output | Configurable output (Distech) |

---

## signal_type

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| 0-10V | 1.00 | all | 0 to 10V, 0-10 VDC, 10V analog | Standard analog voltage |
| 4-20mA | 1.00 | all | 4 to 20mA, 4-20 mA, milliamp, mA loop | Standard industrial current |
| 0-5V | 0.90 | all | 0 to 5V, 0-5 VDC | Low-voltage analog |
| 10K Type II | 0.90 | all | 10K Type 2, 10K thermistor, 10 kilohm | Common BAS temp sensor |
| 10K Type III | 0.90 | all | 10K Type 3 | Alternate thermistor curve |
| NI1000 | 0.90 | distech | NI1000 @ 0C, NI1000 @ 22C, nickel sensor | Distech preferred temp sensor |
| PT1000 | 0.85 | all | PT 1000, platinum RTD, Pt1000 | RTD temperature sensor |
| Digital | 0.80 | all | discrete, dry contact, binary, on/off, 24VAC | Two-state signal |
| Network | 0.80 | all | BACnet object, Modbus register, networked point | Protocol-based signal |
| Resistance | 0.70 | all | resistive input, ohm, thermistor | Resistance-based signal |

---

## eng_unit

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| CFM | 0.90 | all | cubic feet per minute, airflow, air flow | Airflow volume |
| GPM | 0.90 | all | gallons per minute, flow rate | Liquid flow rate |
| Tons | 0.80 | all | refrigeration tons, cooling tons, ton of cooling | Cooling capacity |
| inWC | 0.80 | all | inches water column, in. WC, in WG, static pressure | Duct/pipe pressure |
| kW | 0.80 | all | kilowatt, kilowatts, power, electrical demand | Power |
| psi | 0.80 | all | PSI, pounds per square inch | Pressure |
| °F | 0.80 | all | deg F, degrees fahrenheit, temperature | Temperature |
| % | 0.70 | all | percent, percentage, humidity, RH, position | Percentage |
| kWh | 0.70 | all | kilowatt hour, energy, consumption | Energy |

---

## doc_signal

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| point list | 1.00 | all | points list, IO list, I/O list, point schedule, points schedule | I/O deliverable |
| sequence | 1.00 | all | sequence of operations, sequence of control, control sequence, operating sequence, SOO | Controls narrative |
| submittal | 1.00 | all | submittals, shop drawing, cut sheet, product data, product submittal | Approval deliverable |
| commissioning | 0.90 | all | CX, Cx, functional testing, point-to-point, checkout, startup, P2P | Commissioning deliverable |
| model number | 0.90 | all | model no, model #, catalog number, cat no, part number, manufacturer | Product identification |
| schedule | 0.90 | all | equipment schedule, point schedule, IO schedule, controller schedule | Tabular deliverable |
| specification | 0.90 | all | spec section, division 25, Section 25, controls specification, BAS specification | Design specification |
| riser | 0.80 | all | riser diagram, riser drawing, network riser | Network diagram |
| setpoint | 0.80 | all | set point, control setpoint, operating setpoint, SP | Control reference |
| PID | 0.70 | all | proportional integral derivative, PID loop, feedback control | Control loop type |
| floor plan | 0.70 | all | floor plan, plan view, mechanical plan, HVAC plan | Drawing type |

---

## point_name

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| DaTmp | 0.90 | controlworks | discharge air temp, DAT | Discharge air temperature |
| SFCmd | 0.90 | controlworks | supply fan command, SF enable | Supply fan on/off command |
| SFSts | 0.90 | controlworks | supply fan status, SF status | Supply fan run status |
| ZnTmp | 0.90 | controlworks | zone temp, space temp, ZT | Zone temperature |
| OadPos | 0.90 | controlworks | OA damper position, OAD | Outdoor air damper position |
| HVSig | 0.85 | controlworks | heating valve signal, HV signal | Heating valve control |
| CVSig | 0.85 | controlworks | cooling valve signal, CV signal | Cooling valve control |
| DSP | 0.85 | controlworks | duct static pressure | Duct static pressure |
| BSP | 0.85 | controlworks | building static pressure | Building static pressure |
| MaTmp | 0.85 | controlworks | mixed air temp, MAT | Mixed air temperature |
| RaTmp | 0.85 | controlworks | return air temp, RAT | Return air temperature |
| EFCmd | 0.85 | controlworks | exhaust fan command, EF enable | Exhaust fan command |
| EFSts | 0.85 | controlworks | exhaust fan status | Exhaust fan status |
| FltDP | 0.80 | controlworks | filter differential pressure, filter DP | Filter dirty status |
| SFanDP | 0.80 | controlworks | supply fan differential pressure | Fan pressure differential |
| HwvSig | 0.80 | controlworks | hot water valve signal | Hot water valve control |
| OaFlow | 0.80 | controlworks | outdoor airflow, OA CFM | Outdoor airflow |
| DaSmk | 0.80 | controlworks | discharge air smoke, DA smoke | Duct smoke detector |
| ZnCO2 | 0.80 | controlworks | zone CO2, space CO2 | Zone CO2 |
| Smoke | 0.80 | controlworks | smoke detector, smoke alarm | Smoke detection |
| LoLim | 0.75 | controlworks | low limit, freeze protection | Low limit thermostat |
| OaAlm | 0.75 | controlworks | outdoor air alarm | OA quality alarm |
| EF1Spd | 0.75 | controlworks | exhaust fan speed, EF speed | EF VFD speed |
| SF1Spd | 0.75 | controlworks | supply fan speed, SF speed | SF VFD speed command |
| CCDaTmp | 0.75 | controlworks | chilled water discharge air temp | Cooling coil discharge |
| HCRTmp | 0.75 | controlworks | heating coil return temp | Heating coil return |
| CVPos | 0.70 | controlworks | cooling valve position feedback | Cooling valve feedback |
| HVPos | 0.70 | controlworks | heating valve position feedback | Heating valve feedback |
| Zone Temp | 0.70 | controlworks | zone temperature, space temperature | Generic zone temp |
| Airflow | 0.70 | controlworks | airflow CFM, zone airflow | Zone airflow |

---

## skip_term

| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| estimate | 1.00 | all | job estimate, project estimate, cost estimate, budget estimate | Financial — skip |
| takeoff | 1.00 | all | material takeoff, quantity takeoff, QTO | Estimating — skip |
| JSF | 0.90 | all | job summary form, job summary | Internal form — skip |
| budget | 0.80 | all | budgetary, budget price, ROM | Financial — skip |
| invoice | 0.70 | all | billing, payment, accounts payable | Billing — skip |
| purchase order | 0.70 | all | PO, P.O., purchase order number | Procurement — skip |
| warranty | 0.60 | all | warranty period, warranty claim | Legal — skip |
| insurance | 0.60 | all | liability insurance, certificate of insurance | Legal — skip |
