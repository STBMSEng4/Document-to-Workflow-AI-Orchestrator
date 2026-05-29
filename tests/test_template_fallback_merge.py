import unittest

from app.extractors.template_fallback_merge import (
    EQUIPMENT_TEMPLATE_THRESHOLD,
    build_template_point_records,
    export_point_records,
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


class TemplateFallbackGatingTests(unittest.TestCase):
    def test_low_confidence_equipment_gets_template_only_label(self) -> None:
        """Equipment below the threshold should produce template_only rows."""
        equipment = EquipmentRecord(
            equipment_tag="AHU-1",
            equipment_type="AHU",
            source_reference="inferred context",
            confidence=0.50,  # below 0.70
        )
        merged = merge_point_records_with_template_defaults([], [equipment])
        self.assertGreater(len(merged), 0)
        self.assertTrue(all(r.source_type == "template_only" for r in merged))

    def test_high_confidence_equipment_gets_template_default_label(self) -> None:
        """Equipment above the threshold should produce template_default rows."""
        equipment = EquipmentRecord(
            equipment_tag="AHU-1",
            equipment_type="AHU",
            source_reference="Equipment Schedule",
            confidence=0.90,  # above 0.70
        )
        merged = merge_point_records_with_template_defaults([], [equipment])
        self.assertGreater(len(merged), 0)
        self.assertTrue(all(r.source_type == "template_default" for r in merged))

    def test_exactly_at_threshold_is_template_default(self) -> None:
        """Confidence exactly equal to the threshold should pass (≥ not >)."""
        equipment = EquipmentRecord(
            equipment_tag="RTU-1",
            equipment_type="RTU",
            source_reference="Equipment Schedule",
            confidence=EQUIPMENT_TEMPLATE_THRESHOLD,  # exactly 0.70
        )
        merged = merge_point_records_with_template_defaults([], [equipment])
        self.assertGreater(len(merged), 0)
        self.assertTrue(all(r.source_type == "template_default" for r in merged))

    def test_template_only_rows_require_review(self) -> None:
        """template_only rows should be flagged for review."""
        equipment = EquipmentRecord(
            equipment_tag="FCU-1",
            equipment_type="FCU",
            source_reference="inferred",
            confidence=0.45,
        )
        merged = merge_point_records_with_template_defaults([], [equipment])
        self.assertTrue(all(r.review_required for r in merged))

    def test_mixed_equipment_labels_correctly(self) -> None:
        """Confirmed and unconfirmed equipment in the same call are labelled independently."""
        confirmed = EquipmentRecord(
            equipment_tag="AHU-1", equipment_type="AHU",
            source_reference="doc", confidence=0.85,
        )
        unconfirmed = EquipmentRecord(
            equipment_tag="FCU-1", equipment_type="FCU",
            source_reference="inferred", confidence=0.40,
        )
        merged = merge_point_records_with_template_defaults([], [confirmed, unconfirmed])
        ahu_rows = [r for r in merged if r.equipment_tag == "AHU-1"]
        fcu_rows = [r for r in merged if r.equipment_tag == "FCU-1"]
        self.assertTrue(all(r.source_type == "template_default" for r in ahu_rows))
        self.assertTrue(all(r.source_type == "template_only" for r in fcu_rows))


class ExportPointRecordsTests(unittest.TestCase):
    def _make_point(self, source_type: str) -> PointRecord:
        return PointRecord(
            equipment_tag="AHU-1",
            equipment_type="AHU",
            point_name="Supply Air Temp",
            point_code="SAT",
            point_type="AI",
            signal_type="analog",
            point_role="sensor",
            source_reference="test",
            confidence=0.80,
            source_type=source_type,
        )

    def test_template_only_excluded_from_export(self) -> None:
        records = [
            self._make_point("source_extracted"),
            self._make_point("template_default"),
            self._make_point("template_only"),
        ]
        result = export_point_records(records)
        self.assertEqual(len(result), 2)
        self.assertFalse(any(r.source_type == "template_only" for r in result))

    def test_source_extracted_and_template_default_kept(self) -> None:
        records = [
            self._make_point("source_extracted"),
            self._make_point("template_default"),
        ]
        result = export_point_records(records)
        self.assertEqual(len(result), 2)

    def test_empty_list_returns_empty(self) -> None:
        self.assertEqual(export_point_records([]), [])

    def test_all_template_only_returns_empty(self) -> None:
        records = [self._make_point("template_only") for _ in range(3)]
        self.assertEqual(export_point_records(records), [])


if __name__ == "__main__":
    unittest.main()
