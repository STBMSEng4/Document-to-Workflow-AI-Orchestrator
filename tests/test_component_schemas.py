import unittest

from app.schemas import ActuatorRecord, DamperRecord, SensorRecord, ValveRecord


class ComponentSchemaTests(unittest.TestCase):
    def test_valve_record_normalizes_strings_and_links_to_equipment(self) -> None:
        record = ValveRecord(
            valve_tag=" CHWV-1 ",
            equipment_tag=" AHU-1 ",
            equipment_type="ahu",
            system=" CHW ",
            service=" Cooling Coil ",
            valve_type=" 2-way control valve ",
            size=" 2 in ",
            flow_gpm=48.0,
            flow_coefficient_cv=29.5,
            source_reference=" Sheet M-401 / Valve Schedule ",
            confidence=0.91,
        )

        self.assertEqual(record.valve_tag, "CHWV-1")
        self.assertEqual(record.equipment_tag, "AHU-1")
        self.assertEqual(record.system, "CHW")
        self.assertEqual(record.service, "Cooling Coil")
        self.assertEqual(record.valve_type, "2-way control valve")
        self.assertEqual(record.size, "2 in")
        self.assertEqual(record.flow_gpm, 48.0)
        self.assertEqual(record.flow_coefficient_cv, 29.5)

    def test_damper_record_supports_sizing_and_performance(self) -> None:
        record = DamperRecord(
            damper_tag=" OAD-1 ",
            equipment_tag=" RTU-1 ",
            equipment_type="rtu",
            damper_type=" OA ",
            application=" economizer ",
            size=" 24x18 ",
            airflow_cfm=1800,
            face_velocity_fpm=600,
            leakage_class=" AMCA Class 1 ",
            source_reference=" Sheet M-201 / Damper Schedule ",
            confidence=0.88,
        )

        self.assertEqual(record.damper_tag, "OAD-1")
        self.assertEqual(record.damper_type, "OA")
        self.assertEqual(record.application, "economizer")
        self.assertEqual(record.size, "24x18")
        self.assertEqual(record.airflow_cfm, 1800)
        self.assertEqual(record.face_velocity_fpm, 600)
        self.assertEqual(record.leakage_class, "AMCA Class 1")

    def test_actuator_record_captures_control_characteristics(self) -> None:
        record = ActuatorRecord(
            actuator_tag=" ACT-1 ",
            parent_component_type="damper",
            parent_component_tag=" OAD-1 ",
            equipment_tag=" RTU-1 ",
            equipment_type="rtu",
            manufacturer=" Belimo ",
            model=" NFBUP-SR ",
            actuator_type=" spring return ",
            power_supply=" 24 VAC ",
            control_signal=" 2-10 VDC ",
            torque_in_lb=180,
            source_reference=" Controls Submittal / Damper Actuator Schedule ",
            confidence=0.9,
        )

        self.assertEqual(record.actuator_tag, "ACT-1")
        self.assertEqual(record.parent_component_type, "damper")
        self.assertEqual(record.parent_component_tag, "OAD-1")
        self.assertEqual(record.manufacturer, "Belimo")
        self.assertEqual(record.model, "NFBUP-SR")
        self.assertEqual(record.control_signal, "2-10 VDC")
        self.assertEqual(record.torque_in_lb, 180)

    def test_sensor_record_supports_common_bms_sensor_fields(self) -> None:
        record = SensorRecord(
            sensor_tag=" SAT-1 ",
            equipment_tag=" AHU-1 ",
            equipment_type="ahu",
            sensor_type=" temperature ",
            measured_variable=" supply air temperature ",
            engineering_unit=" F ",
            sensing_range=" 32-120 F ",
            output_signal=" 10k thermistor ",
            installation_location=" supply duct ",
            averaging=True,
            source_reference=" Sheet M-501 / Controls Points ",
            confidence=0.94,
        )

        self.assertEqual(record.sensor_tag, "SAT-1")
        self.assertEqual(record.sensor_type, "temperature")
        self.assertEqual(record.measured_variable, "supply air temperature")
        self.assertEqual(record.engineering_unit, "F")
        self.assertEqual(record.output_signal, "10k thermistor")
        self.assertEqual(record.installation_location, "supply duct")
        self.assertTrue(record.averaging)


if __name__ == "__main__":
    unittest.main()
