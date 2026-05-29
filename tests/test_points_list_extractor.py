import unittest

from app.extractors.equipment_extractor import extract_equipment_records
from app.extractors.points_list_extractor import extract_point_records


class PointExtractorHeaderAliasTests(unittest.TestCase):
    """Bare 'Equipment' and 'Type' column headers map to the correct fields."""

    _MARKDOWN = (
        "## Points List\n\n"
        "| Equipment | Point Name | Code | Type | Unit |\n"
        "|-----------|------------|------|------|------|\n"
        "| AHU-1 | Supply Air Temperature | SAT | AI | degF |\n"
        "| AHU-1 | Supply Fan Command | SF-CMD | DO | |\n"
        "| RTU-1 | Discharge Air Temp | DAT | AI | degF |\n"
    )

    def _records(self) -> list:
        return extract_point_records(self._MARKDOWN)

    def test_bare_equipment_column_maps_to_equipment_tag(self) -> None:
        records = self._records()
        self.assertTrue(len(records) > 0)
        for rec in records:
            self.assertIsNotNone(rec.equipment_tag)
            self.assertIn(rec.equipment_tag, {"AHU-1", "RTU-1"})

    def test_type_column_ai_maps_to_point_type(self) -> None:
        records = self._records()
        ai_recs = [r for r in records if r.point_name == "Supply Air Temperature"]
        self.assertEqual(len(ai_recs), 1)
        self.assertEqual(ai_recs[0].point_type, "AI")

    def test_type_column_do_maps_to_point_type(self) -> None:
        records = self._records()
        do_recs = [r for r in records if r.point_name == "Supply Fan Command"]
        self.assertEqual(len(do_recs), 1)
        self.assertEqual(do_recs[0].point_type, "DO")

    def test_correct_record_count_no_spurious_entries(self) -> None:
        records = self._records()
        self.assertEqual(len(records), 3)


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

    def test_extract_point_records_from_plain_text_point_list(self) -> None:
        markdown = """## Control Room 102

CONTROL ROOM - CRAC-5 - BAS POINT LIST - DCP-9
POINT NO. POINT DESCRIPTION POINT TYPE FIELD DEVICE TYPE
1 CRAC-5 UNIT ENABLE DO Dry Contact X X X -- 1
2 CRAC-5 COMMON FAILURE ALARM DO Dry Contact X X X -- 1
3 CRAC-5 FAN STATUS DI CS X X X -- 1
4 CRAC-5 SUPPLY AIR TEMPERATURE AI degF Via Integration X X X -- 1
NOTES:
1) Demo note.
"""

        point_records = extract_point_records(markdown)

        self.assertEqual(len(point_records), 4)
        self.assertEqual(point_records[0].equipment_tag, "CRAC-5")
        self.assertEqual(point_records[0].controller_tag, "DCP-9")
        self.assertEqual(point_records[0].point_name, "UNIT ENABLE")
        self.assertEqual(point_records[0].point_type, "DO")
        self.assertEqual(point_records[0].source_type, "inferred")
        self.assertEqual(point_records[3].point_type, "AI")
        self.assertEqual(point_records[3].engineering_unit, "degf")


if __name__ == "__main__":
    unittest.main()
