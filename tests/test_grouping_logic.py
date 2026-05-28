import unittest

from app.extractors.grouping import (
    canonicalize_equipment_tag,
    detect_equipment_tags,
    group_equipment_records,
    group_points_by_equipment,
    map_point_to_equipment,
)
from app.schemas import EquipmentRecord, PointRecord


class GroupingLogicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.equipment_records = [
            EquipmentRecord(
                equipment_tag="AHU-1",
                equipment_type="AHU",
                equipment_name="Air Handling Unit 1",
                source_reference="Equipment Schedule",
                confidence=0.95,
            ),
            EquipmentRecord(
                equipment_tag="RTU-2",
                equipment_type="RTU",
                equipment_name="Roof Top Unit 2",
                source_reference="Equipment Schedule",
                confidence=0.92,
            ),
        ]

    def test_detect_equipment_tags_from_free_text(self) -> None:
        tags = detect_equipment_tags("Coordinate controls for AHU-1, RTU 2, and EF_3 before startup.")
        self.assertEqual(tags, ["AHU-1", "RTU-2", "EF-3"])
        self.assertEqual(canonicalize_equipment_tag(" rtu 2 "), "RTU-2")

    def test_group_equipment_records_by_tag(self) -> None:
        grouped = group_equipment_records(self.equipment_records)
        self.assertEqual(set(grouped.keys()), {"AHU-1", "RTU-2"})
        self.assertEqual(grouped["AHU-1"][0].equipment_type, "AHU")

    def test_map_point_to_equipment_uses_text_fallback(self) -> None:
        point = PointRecord(
            point_name="Supply Air Temperature",
            description="Sensor mounted on AHU-1 discharge",
            point_type="AI",
            signal_type="analog",
            point_role="sensor",
            source_reference="Controls Points",
            confidence=0.9,
        )

        equipment_tag, equipment_type = map_point_to_equipment(
            point,
            self.equipment_records,
            source_hint="Sheet M-501 / AHU-1 Controls Points",
        )

        self.assertEqual(equipment_tag, "AHU-1")
        self.assertEqual(equipment_type, "AHU")

    def test_group_points_by_equipment_updates_links(self) -> None:
        points = [
            PointRecord(
                point_name="Supply Air Temperature",
                description="AHU-1 discharge air sensor",
                point_type="AI",
                signal_type="analog",
                point_role="sensor",
                source_reference="Controls Points",
                confidence=0.9,
            ),
            PointRecord(
                equipment_tag="RTU-2",
                point_name="Supply Fan Command",
                point_type="DO",
                signal_type="binary",
                point_role="command",
                source_reference="Controls Points",
                confidence=0.88,
            ),
        ]

        grouped = group_points_by_equipment(points, self.equipment_records)

        self.assertEqual(set(grouped.keys()), {"AHU-1", "RTU-2"})
        self.assertEqual(points[0].equipment_tag, "AHU-1")
        self.assertEqual(points[0].equipment_type, "AHU")
        self.assertEqual(points[1].equipment_type, "RTU")


if __name__ == "__main__":
    unittest.main()
