"""Tests for the SOO extractor."""

import unittest

from app.extractors.soo_extractor import extract_soo_records


class TestSOOExtractorBasic(unittest.TestCase):
    """Core extraction behaviour."""

    def test_returns_empty_for_empty_input(self) -> None:
        self.assertEqual(extract_soo_records(""), [])

    def test_returns_empty_for_non_soo_text(self) -> None:
        text = "This is a general project description with no control sequences."
        self.assertEqual(extract_soo_records(text), [])

    def test_returns_empty_for_table_only_input(self) -> None:
        text = (
            "| Tag | Type | CFM |\n"
            "|---|---|---|\n"
            "| RTU-1 | RTU | 4200 |\n"
        )
        self.assertEqual(extract_soo_records(text), [])

    def test_extracts_record_from_occupied_mode_section(self) -> None:
        text = (
            "## Occupied Mode\n\n"
            "When the space temperature rises above the cooling setpoint, "
            "the DDC controller shall stage the compressor to maintain the "
            "discharge air temperature setpoint of 55°F.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        rec = records[0]
        self.assertEqual(rec.mode, "occupied")
        self.assertIsNotNone(rec.condition)
        self.assertIn("compressor", rec.action.lower())

    def test_detects_setpoint_value_and_unit(self) -> None:
        text = (
            "## Occupied Mode\n\n"
            "The DDC controller shall maintain the discharge air temperature "
            "setpoint of 55°F by modulating the chilled water valve.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        rec = records[0]
        self.assertAlmostEqual(rec.setpoint_value, 55.0)
        self.assertEqual(rec.setpoint_unit, "°F")

    def test_named_setpoint_captured(self) -> None:
        text = (
            "## Cooling Mode\n\n"
            "When the space temperature exceeds the cooling setpoint of 75°F, "
            "the unit shall enable mechanical cooling.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        rec = records[0]
        self.assertIsNotNone(rec.setpoint_name)
        self.assertIn("cooling setpoint", rec.setpoint_name.lower())
        self.assertAlmostEqual(rec.setpoint_value, 75.0)


class TestSOOExtractorModes(unittest.TestCase):
    """Mode detection."""

    def test_unoccupied_mode_detected_from_header(self) -> None:
        text = (
            "## Unoccupied Mode\n\n"
            "The unit shall maintain a night setback heating setpoint of 60°F.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0].mode, "unoccupied")

    def test_heating_mode_detected(self) -> None:
        text = (
            "## Heating Mode\n\n"
            "When the space temperature falls below the heating setpoint of 70°F, "
            "the heating stage 1 shall be enabled.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0].mode, "heating")

    def test_economizer_mode_detected(self) -> None:
        text = (
            "## Economizer Mode\n\n"
            "When the outdoor air temperature is below 65°F, the economizer "
            "damper shall open to provide free cooling.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0].mode, "economizer")

    def test_emergency_mode_from_freeze_protection_header(self) -> None:
        text = (
            "## Freeze Protection\n\n"
            "If the supply air temperature falls below 38°F, the unit shall "
            "shut down immediately and a freeze alarm shall be generated.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0].mode, "emergency")

    def test_morning_warmup_mode(self) -> None:
        text = (
            "## Morning Warmup\n\n"
            "Prior to the occupied period, the unit shall pre-heat the space "
            "to the occupied heating setpoint of 70°F.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0].mode, "morning_warmup")


class TestSOOExtractorSafety(unittest.TestCase):
    """Safety-critical detection."""

    def test_freeze_protection_is_safety_critical(self) -> None:
        text = (
            "## Freeze Protection\n\n"
            "If the supply air temperature falls below 38°F, the unit shall "
            "shut down immediately and a freeze alarm shall be generated.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertTrue(records[0].safety_critical)

    def test_smoke_shutdown_is_safety_critical(self) -> None:
        text = (
            "## Sequence of Operations\n\n"
            "Upon smoke detector activation, the unit shall shut down and a "
            "life safety alarm shall be generated at the BMS.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        safety_records = [r for r in records if r.safety_critical]
        self.assertGreater(len(safety_records), 0)

    def test_normal_step_is_not_safety_critical(self) -> None:
        text = (
            "## Occupied Mode\n\n"
            "When the space temperature rises above the cooling setpoint, "
            "the supply fan shall be enabled at minimum speed.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertFalse(records[0].safety_critical)

    def test_safety_critical_record_requires_review(self) -> None:
        text = (
            "## Freeze Protection\n\n"
            "If the supply air temperature falls below 38°F, the unit shall "
            "shut down and a freeze alarm shall be generated.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertTrue(records[0].review_required)


class TestSOOExtractorEquipmentLinking(unittest.TestCase):
    """Equipment tag and type detection."""

    def test_equipment_tag_detected_inline(self) -> None:
        text = (
            "## Sequence of Operations\n\n"
            "When RTU-1 space temperature exceeds the cooling setpoint, "
            "RTU-1 shall enable mechanical cooling.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0].equipment_tag, "RTU-1")

    def test_equipment_type_detected_from_prose(self) -> None:
        text = (
            "## Sequence of Operations\n\n"
            "When the air handling unit supply air temperature exceeds 60°F, "
            "the chilled water valve shall modulate open to maintain setpoint.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0].equipment_type, "AHU")

    def test_equipment_tag_inherited_from_section_header(self) -> None:
        text = (
            "## RTU-2 — Occupied Mode\n\n"
            "When the space temperature exceeds 75°F, the DDC controller shall "
            "stage the compressor to maintain the discharge air temperature setpoint.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0].equipment_tag, "RTU-2")


class TestSOOExtractorMultipleSteps(unittest.TestCase):
    """Multi-step sequence extraction."""

    def test_multiple_steps_extracted_in_order(self) -> None:
        text = (
            "## Occupied Mode\n\n"
            "When the space temperature exceeds the cooling setpoint of 75°F, "
            "the supply fan shall start and the economizer damper shall open.\n"
            "When the outdoor air temperature is above 65°F, the economizer "
            "shall disable and the compressor stage 1 shall enable.\n"
            "When the cooling load increases further, the compressor stage 2 shall enable.\n"
        )
        records = extract_soo_records(text)
        self.assertGreaterEqual(len(records), 2)
        for i, rec in enumerate(records):
            self.assertEqual(rec.step_index, i + 1)

    def test_multiple_modes_tracked_correctly(self) -> None:
        text = (
            "## Occupied Mode\n\n"
            "When the space temperature rises above the cooling setpoint, "
            "the unit shall enable cooling.\n\n"
            "## Unoccupied Mode\n\n"
            "The unit shall maintain a setback heating setpoint of 60°F "
            "and shall disable mechanical cooling.\n"
        )
        records = extract_soo_records(text)
        modes = [r.mode for r in records]
        self.assertIn("occupied", modes)
        self.assertIn("unoccupied", modes)

    def test_step_indices_are_sequential_across_modes(self) -> None:
        text = (
            "## Occupied Mode\n\n"
            "The supply fan shall start when the occupancy schedule activates.\n\n"
            "## Unoccupied Mode\n\n"
            "The unit shall maintain the setback cooling setpoint of 85°F "
            "and the heating setpoint of 60°F.\n"
        )
        records = extract_soo_records(text)
        indices = [r.step_index for r in records]
        self.assertEqual(indices, list(range(1, len(indices) + 1)))


class TestSOOExtractorConfidence(unittest.TestCase):
    """Confidence and source_type assignment."""

    def test_condition_plus_setpoint_gives_highest_confidence(self) -> None:
        text = (
            "## Cooling Mode\n\n"
            "When the space temperature exceeds the cooling setpoint of 75°F, "
            "the compressor shall be enabled.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertGreaterEqual(records[0].confidence, 0.85)

    def test_action_only_gives_lower_confidence(self) -> None:
        text = (
            "## Sequence of Operations\n\n"
            "The supply fan shall run continuously during the occupied period.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertLess(records[0].confidence, 0.80)

    def test_source_type_extracted_when_condition_present(self) -> None:
        text = (
            "## Occupied Mode\n\n"
            "When the space temperature exceeds the cooling setpoint, "
            "the DDC controller shall enable mechanical cooling.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0].source_type, "source_extracted")

    def test_source_type_inferred_when_action_only(self) -> None:
        text = (
            "## Sequence of Operations\n\n"
            "The supply fan shall start automatically during occupied hours.\n"
        )
        records = extract_soo_records(text)
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0].source_type, "inferred")


if __name__ == "__main__":
    unittest.main()
