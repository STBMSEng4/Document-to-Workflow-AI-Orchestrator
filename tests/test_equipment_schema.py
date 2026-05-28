import unittest

from app.schemas import EquipmentRecord


class EquipmentSchemaTests(unittest.TestCase):
    def test_equipment_record_supports_nested_attributes(self) -> None:
        record = EquipmentRecord(
            equipment_tag=" RTU-1 ",
            equipment_type="rtu",
            equipment_name=" Roof Top Unit 1 ",
            system=" HVAC ",
            location=" Roof ",
            manufacturer=" Trane ",
            model=" YCD120 ",
            protocol=" BACnet/IP ",
            source_reference=" Sheet M-201 / Equipment Schedule ",
            confidence=0.93,
            attributes={
                "electrical": {
                    "voltage": "480V",
                    "phase": "3",
                    "minimum_circuit_ampacity_amps": 23.5,
                },
                "airflow": {
                    "airflow_cfm": 4200,
                    "external_static_in_wg": 2.0,
                },
                "cooling": {
                    "cooling_capacity_tons": 10.0,
                    "compressor_stages": 2,
                },
                "dampers_and_economizer": {
                    "damper_size": "24x18",
                    "economizer_type": "dry bulb",
                },
                "controls": {
                    "controller_model": "PXC36",
                    "safeties": ["freezestat", "smoke detector shutdown"],
                },
            },
        )

        self.assertEqual(record.equipment_tag, "RTU-1")
        self.assertEqual(record.equipment_name, "Roof Top Unit 1")
        self.assertEqual(record.system, "HVAC")
        self.assertEqual(record.location, "Roof")
        self.assertEqual(record.manufacturer, "Trane")
        self.assertEqual(record.model, "YCD120")
        self.assertEqual(record.protocol, "BACnet/IP")
        self.assertEqual(record.source_reference, "Sheet M-201 / Equipment Schedule")
        self.assertEqual(record.attributes.electrical.voltage, "480V")
        self.assertEqual(record.attributes.airflow.airflow_cfm, 4200)
        self.assertEqual(record.attributes.cooling.compressor_stages, 2)
        self.assertEqual(record.attributes.dampers_and_economizer.damper_size, "24x18")
        self.assertEqual(
            record.attributes.controls.safeties,
            ["freezestat", "smoke detector shutdown"],
        )

    def test_equipment_record_defaults_nested_buckets(self) -> None:
        record = EquipmentRecord(
            equipment_tag="VAV-1",
            equipment_type="vav",
            source_reference="Sheet M-301",
            confidence=0.8,
        )

        self.assertIsNone(record.attributes.airflow.airflow_cfm)
        self.assertEqual(record.attributes.controls.safeties, [])
        self.assertEqual(record.attributes.vrf.indoor_unit_types, [])
        self.assertEqual(record.source_type, "source_extracted")
        self.assertEqual(record.confidence_band, "high")
        self.assertFalse(record.review_required)

    def test_equipment_record_marks_inferred_rows_for_review(self) -> None:
        record = EquipmentRecord(
            equipment_tag="RTU-1",
            equipment_type="RTU",
            source_reference="Sheet M-201",
            confidence=0.68,
            source_type="inferred",
        )

        self.assertEqual(record.confidence_band, "medium")
        self.assertTrue(record.review_required)
        self.assertEqual(record.review_reason, "record contains inferred fields that should be reviewed")


if __name__ == "__main__":
    unittest.main()
