import unittest

from app.schemas import PointRecord


class PointSchemaTests(unittest.TestCase):
    def test_point_record_normalizes_naming_fields(self) -> None:
        record = PointRecord(
            equipment_tag=" AHU-1 ",
            equipment_type="ahu",
            controller_tag=" DDC-AHU-1 ",
            system=" HVAC ",
            location=" Mech Room 1 ",
            point_name=" Supply Air Temperature ",
            point_code=" sat ",
            point_type="AI",
            signal_type="analog",
            point_role="sensor",
            object_type="analogInput",
            object_instance=101,
            protocol=" BACnet/IP ",
            engineering_unit=" °F ",
            range_min=32.0,
            range_max=120.0,
            writable=False,
            alarmed=True,
            trended=True,
            description=" Discharge air temp sensor downstream of coil ",
            source_reference=" Sheet M-501 / Controls Points List ",
            confidence=0.95,
        )

        self.assertEqual(record.equipment_tag, "AHU-1")
        self.assertEqual(record.controller_tag, "DDC-AHU-1")
        self.assertEqual(record.system, "HVAC")
        self.assertEqual(record.location, "Mech Room 1")
        self.assertEqual(record.point_name, "Supply Air Temperature")
        self.assertEqual(record.normalized_point_name, "Supply Air Temperature")
        self.assertEqual(record.point_code, "SAT")
        self.assertEqual(record.protocol, "BACnet/IP")
        self.assertEqual(record.engineering_unit, "°F")
        self.assertEqual(record.object_type, "analogInput")
        self.assertEqual(record.confidence_band, "confirmed")
        self.assertTrue(record.alarmed)
        self.assertTrue(record.trended)
        self.assertFalse(record.review_required)

    def test_point_record_supports_setpoints_and_network_points(self) -> None:
        setpoint = PointRecord(
            equipment_tag="VAV-1",
            equipment_type="vav",
            point_name="Space Temperature Cooling Setpoint",
            normalized_point_name="Zone Cooling Setpoint",
            point_code="CLG-SP",
            point_type="SP",
            signal_type="analog",
            point_role="setpoint",
            engineering_unit="°F",
            default_value="75",
            writable=True,
            commandable=True,
            source_reference="VAV Controls Sequence",
            confidence=0.88,
        )

        network = PointRecord(
            equipment_tag="PLC-1",
            equipment_type="plc",
            point_name="Communication Heartbeat",
            point_code="HB",
            point_type="Network",
            signal_type="network",
            point_role="network",
            protocol="Modbus TCP",
            network_address="40001",
            engineering_unit="ms",
            source_reference="PLC Integration Schedule",
            confidence=0.84,
            source_type="template_default",
        )

        self.assertEqual(setpoint.normalized_point_name, "Zone Cooling Setpoint")
        self.assertEqual(setpoint.point_type, "SP")
        self.assertTrue(setpoint.writable)
        self.assertTrue(setpoint.commandable)
        self.assertEqual(setpoint.confidence_band, "high")
        self.assertFalse(setpoint.review_required)
        self.assertEqual(network.point_type, "Network")
        self.assertEqual(network.signal_type, "network")
        self.assertEqual(network.network_address, "40001")
        self.assertEqual(network.source_type, "template_default")
        self.assertTrue(network.review_required)
        self.assertEqual(network.review_reason, "template fallback row requires source verification")


if __name__ == "__main__":
    unittest.main()
