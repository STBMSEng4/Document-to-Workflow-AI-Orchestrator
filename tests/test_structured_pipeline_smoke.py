import unittest

from app.extractors.equipment_extractor import extract_equipment_records
from app.extractors.grouping import group_points_by_equipment
from app.extractors.points_list_extractor import extract_point_records
from app.extractors.template_fallback_merge import merge_point_records_with_template_defaults


class StructuredPipelineSmokeTests(unittest.TestCase):
    def test_structured_pipeline_extracts_groups_and_backfills(self) -> None:
        markdown = """## Equipment Schedule

| Tag | Type | Equipment | Manufacturer | Model | Voltage | CFM | Cooling Tons | Compressor Stages | Protocol |
|---|---|---|---|---|---|---:|---:|---:|---|
| AHU-1 | AHU | Air Handling Unit 1 | Daikin | Vision | 480V/3PH | 12000 | 0 | 0 | BACnet/IP |
| RTU-2 | RTU | Roof Top Unit 2 | Trane | Voyager | 480V/3PH | 4200 | 10 | 2 | BACnet/IP |

## AHU-1 Controls Points

| Equipment Tag | Point Name | Abbr | IO Type | Unit | Description |
|---|---|---|---|---|---|
| AHU-1 | Supply Air Temperature | SAT | AI | degF | AHU-1 discharge air sensor |
| AHU-1 | Supply Fan Command | SF-CMD | DO | On/Off | AHU-1 supply fan start command |

## RTU-2 Sequence of Operation

| Point Name | Abbr | IO Type | Unit | Description |
|---|---|---|---|---|
| Space Temperature | ZN-T | AI | degF | RTU-2 space temperature sensor |
"""

        equipment_records = extract_equipment_records(markdown)
        source_points = extract_point_records(markdown, equipment_records=equipment_records)
        grouped_source_points = group_points_by_equipment(source_points, equipment_records)
        merged_points = merge_point_records_with_template_defaults(source_points, equipment_records)
        grouped_merged_points = group_points_by_equipment(merged_points, equipment_records)

        self.assertEqual(len(equipment_records), 2)
        self.assertEqual({record.equipment_tag for record in equipment_records}, {"AHU-1", "RTU-2"})

        self.assertEqual(len(source_points), 3)
        self.assertEqual(set(grouped_source_points.keys()), {"AHU-1", "RTU-2"})

        rtu_context_point = next(point for point in source_points if point.point_code == "ZN-T")
        self.assertEqual(rtu_context_point.equipment_tag, "RTU-2")
        self.assertEqual(rtu_context_point.equipment_type, "RTU")
        self.assertEqual(rtu_context_point.source_type, "inferred")

        self.assertGreater(len(merged_points), len(source_points))
        self.assertIn("AHU-1", grouped_merged_points)
        self.assertIn("RTU-2", grouped_merged_points)
        self.assertTrue(any(point.source_type == "template_default" for point in grouped_merged_points["AHU-1"]))
        self.assertTrue(any(point.source_type == "template_default" for point in grouped_merged_points["RTU-2"]))

        sat_points = [point for point in merged_points if point.equipment_tag == "AHU-1" and point.point_code == "SAT"]
        self.assertEqual(len(sat_points), 1)
        self.assertEqual(sat_points[0].source_type, "source_extracted")

    def test_structured_pipeline_keeps_sparse_equipment_via_template_backfill(self) -> None:
        markdown = """## Equipment Schedule

| Tag | Type | Equipment |
|---|---|---|
| VAV-3 | VAV | VAV Box 3 |
"""

        equipment_records = extract_equipment_records(markdown)
        source_points = extract_point_records(markdown, equipment_records=equipment_records)
        merged_points = merge_point_records_with_template_defaults(source_points, equipment_records)
        grouped_points = group_points_by_equipment(merged_points, equipment_records)

        self.assertEqual(len(source_points), 0)
        self.assertIn("VAV-3", grouped_points)
        self.assertTrue(all(point.source_type == "template_default" for point in grouped_points["VAV-3"]))
        self.assertTrue(all(point.review_required for point in grouped_points["VAV-3"]))


if __name__ == "__main__":
    unittest.main()
