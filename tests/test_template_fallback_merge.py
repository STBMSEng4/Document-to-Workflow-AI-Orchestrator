import unittest

from app.extractors.template_fallback_merge import (
    build_template_point_records,
    merge_point_records_with_template_defaults,
)
from app.schemas import EquipmentRecord, PointRecord


class TemplateFallbackMergeTests(unittest.TestCase):
    def test_build_template_point_records_marks_rows_as_template_default(self) -> None:
        equipment = EquipmentRecord(
            equipment_tag="RTU-1",
            equipment_type="RTU",
            source_reference="Equipment Schedule",
            confidence=0.9,
        )

        records = build_template_point_records(equipment)

        self.assertGreater(len(records), 0)
        self.assertTrue(all(r.source_type == "template_default" for r in records))
        self.assertTrue(all(r.review_required for r in records))

    def test_merge_point_records_backfills_only_missing_template_rows(self) -> None:
        equipment = EquipmentRecord(
            equipment_tag="AHU-1",
            equipment_type="AHU",
            source_reference="Equipment Schedule",
            confidence=0.9,
        )
        extracted = [
            PointRecord(
                equipment_tag="AHU-1",
                equipment_type="AHU",
                point_name="Supply Air Temperature",
                point_code="SAT",
                point_type="AI",
                signal_type="analog",
                point_role="sensor",
                source_reference="Controls Points",
                confidence=0.93,
            )
        ]

        merged = merge_point_records_with_template_defaults(extracted, [equipment])

        sat_points = [p for p in merged if p.point_code == "SAT"]
        self.assertEqual(len(sat_points), 1)
        self.assertEqual(sat_points[0].source_type, "source_extracted")
        self.assertGreater(len(merged), len(extracted))
        self.assertTrue(any(p.source_type == "template_default" for p in merged))


if __name__ == "__main__":
    unittest.main()
