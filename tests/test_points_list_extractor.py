import unittest

from app.extractors.equipment_extractor import extract_equipment_records
from app.extractors.points_list_extractor import extract_point_records


class PointExtractorTests(unittest.TestCase):
    def test_extract_point_records_from_markdown_table(self) -> None:
        markdown = """## Sheet: Equipment Schedule

| Tag | Type | Equipment | Manufacturer | Model |
|---|---|---|---|---|
| AHU-1 | AHU | Air Handling Unit 1 | Daikin | Vision |

## Sheet: Controls Points

| Equipment Tag | Point Name | Abbr | IO Type | Unit | Description | BACnet Instance |
|---|---|---|---|---|---|---:|
| AHU-1 | Supply Air Temperature | SAT | AI | °F | Discharge air temperature sensor | 101 |
| AHU-1 | Supply Fan Command | SF-CMD | DO | On/Off | Supply fan start command | 102 |
| AHU-1 | Supply Air Temperature Setpoint | SAT-SP | SP | °F | Occupied discharge setpoint | 103 |
"""

        equipment_records = extract_equipment_records(markdown)
        point_records = extract_point_records(markdown, equipment_records=equipment_records)

        self.assertEqual(len(point_records), 3)
        sat = point_records[0]
        cmd = point_records[1]
        sp = point_records[2]

        self.assertEqual(sat.equipment_tag, "AHU-1")
        self.assertEqual(sat.equipment_type, "AHU")
        self.assertEqual(sat.point_code, "SAT")
        self.assertEqual(sat.point_type, "AI")
        self.assertEqual(sat.signal_type, "analog")
        self.assertEqual(sat.point_role, "sensor")
        self.assertEqual(sat.object_type, "analogInput")
        self.assertEqual(sat.object_instance, 101)
        self.assertEqual(sat.source_type, "source_extracted")

        self.assertEqual(cmd.point_type, "DO")
        self.assertEqual(cmd.signal_type, "binary")
        self.assertEqual(cmd.point_role, "command")
        self.assertTrue(cmd.commandable)

        self.assertEqual(sp.point_type, "SP")
        self.assertEqual(sp.point_role, "setpoint")
        self.assertTrue(sp.writable)

    def test_extract_point_record_marks_inferred_when_equipment_link_is_contextual(self) -> None:
        markdown = """## Sheet: Equipment Schedule

| Tag | Type | Equipment |
|---|---|---|
| AHU-1 | AHU | Air Handling Unit 1 |

## AHU-1 Sequence of Operation

| Point Name | Abbr | IO Type | Unit | Description |
|---|---|---|---|---|
| Supply Fan Status | SF-STS | DI | On/Off | Prove AHU-1 supply fan operation |
"""

        equipment_records = extract_equipment_records(markdown)
        point_records = extract_point_records(markdown, equipment_records=equipment_records)

        self.assertEqual(len(point_records), 1)
        point = point_records[0]
        self.assertEqual(point.equipment_tag, "AHU-1")
        self.assertEqual(point.equipment_type, "AHU")
        self.assertEqual(point.source_type, "inferred")
        self.assertIn("equipment link inferred", point.remarks)


if __name__ == "__main__":
    unittest.main()
