import unittest

from app.extractors.equipment_extractor import extract_equipment_records


class EquipmentExtractorTests(unittest.TestCase):
    def test_extract_equipment_records_from_markdown_table(self) -> None:
        markdown = """## Sheet: Equipment Schedule

| Tag | Type | Equipment | Manufacturer | Model | Voltage | CFM | Cooling Tons | Compressor Stages | Damper Size | Protocol |
|---|---|---|---|---|---|---:|---:|---:|---|---|
| RTU-1 | RTU | Roof Top Unit 1 | Trane | YCD120 | 480V/3PH | 4200 | 10 | 2 | 24x18 | BACnet/IP |
| AHU-1 | AHU | Air Handling Unit 1 | Daikin | Vision | 480V/3PH | 12000 | 0 | 0 | 48x36 | BACnet/IP |
"""

        records = extract_equipment_records(markdown)

        self.assertEqual(len(records), 2)
        rtu = records[0]
        ahu = records[1]
        self.assertEqual(rtu.equipment_tag, "RTU-1")
        self.assertEqual(rtu.equipment_type, "RTU")
        self.assertEqual(rtu.manufacturer, "Trane")
        self.assertEqual(rtu.attributes.electrical.voltage, "480V/3PH")
        self.assertEqual(rtu.attributes.airflow.airflow_cfm, 4200)
        self.assertEqual(rtu.attributes.cooling.cooling_capacity_tons, 10)
        self.assertEqual(rtu.attributes.cooling.compressor_stages, 2)
        self.assertEqual(rtu.attributes.dampers_and_economizer.damper_size, "24x18")
        self.assertEqual(rtu.source_type, "source_extracted")
        self.assertEqual(ahu.equipment_tag, "AHU-1")
        self.assertEqual(ahu.equipment_type, "AHU")

    def test_extract_equipment_record_marks_inferred_when_type_or_tag_is_derived(self) -> None:
        markdown = """## Sheet: Equipment Schedule

| Equipment | Manufacturer | Model |
|---|---|---|
| RTU-7 Roof Top Unit 7 | Trane | Voyager |
"""

        records = extract_equipment_records(markdown)

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.equipment_tag, "RTU-7")
        self.assertEqual(record.equipment_type, "RTU")
        self.assertEqual(record.source_type, "inferred")
        self.assertIn("equipment_type inferred", record.remarks)


if __name__ == "__main__":
    unittest.main()
