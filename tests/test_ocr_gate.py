"""Tests for the OCR quality gate."""

import unittest

from app.parsers.ocr_gate import is_blocked, is_warned, ocr_quality, ocr_text_is_usable


def _result(**kwargs) -> dict:
    """Build a minimal parse-result dict for testing."""
    base = {
        "status": "success",
        "ocr_required": False,
        "ocr_applied": False,
        "pdf_classification": "text_pdf",
        "metadata": {"char_count": 5000, "word_count": 800},
    }
    base.update(kwargs)
    return base


class TestOCRGateHelper(unittest.TestCase):
    def test_ocr_text_is_usable_requires_both_thresholds(self) -> None:
        self.assertTrue(ocr_text_is_usable(200, 30))
        self.assertFalse(ocr_text_is_usable(199, 30))
        self.assertFalse(ocr_text_is_usable(200, 29))


class TestOCRGateOK(unittest.TestCase):
    def test_none_result_is_ok(self) -> None:
        level, msg = ocr_quality(None)
        self.assertEqual(level, "ok")
        self.assertEqual(msg, "")

    def test_clean_text_pdf_is_ok(self) -> None:
        level, _ = ocr_quality(_result())
        self.assertEqual(level, "ok")

    def test_ok_means_not_blocked(self) -> None:
        self.assertFalse(is_blocked(_result()))

    def test_ok_means_not_warned(self) -> None:
        self.assertFalse(is_warned(_result()))


class TestOCRGateBlocked(unittest.TestCase):
    def test_failed_status_is_blocked(self) -> None:
        level, msg = ocr_quality(_result(status="failed"))
        self.assertEqual(level, "blocked")
        self.assertIn("failed", msg.lower())

    def test_ocr_required_without_applied_is_blocked(self) -> None:
        level, msg = ocr_quality(_result(ocr_required=True, ocr_applied=False))
        self.assertEqual(level, "blocked")
        self.assertIn("OCR was not available", msg)

    def test_ocr_applied_with_too_few_chars_is_blocked(self) -> None:
        level, msg = ocr_quality(
            _result(
                ocr_applied=True,
                metadata={"char_count": 50, "word_count": 8},
            )
        )
        self.assertEqual(level, "blocked")
        self.assertIn("50 characters", msg)

    def test_ocr_applied_with_too_few_words_is_blocked(self) -> None:
        level, msg = ocr_quality(
            _result(
                ocr_applied=True,
                metadata={"char_count": 500, "word_count": 10},
            )
        )
        self.assertEqual(level, "blocked")
        self.assertIn("10 words", msg)

    def test_is_blocked_helper_true_when_blocked(self) -> None:
        self.assertTrue(is_blocked(_result(status="failed")))

    def test_is_blocked_helper_false_when_ok(self) -> None:
        self.assertFalse(is_blocked(_result()))

    def test_blocked_has_non_empty_message(self) -> None:
        _, msg = ocr_quality(_result(status="failed"))
        self.assertTrue(len(msg) > 0)


class TestOCRGateWarn(unittest.TestCase):
    def test_ocr_applied_with_enough_text_is_warn(self) -> None:
        level, msg = ocr_quality(
            _result(
                ocr_applied=True,
                metadata={"char_count": 3000, "word_count": 500},
            )
        )
        self.assertEqual(level, "warn")
        self.assertIn("OCR was applied", msg)

    def test_surya_ocr_metadata_is_still_warn(self) -> None:
        level, _ = ocr_quality(
            _result(
                ocr_applied=True,
                metadata={"char_count": 3000, "word_count": 500, "ocr_engine": "surya"},
            )
        )
        self.assertEqual(level, "warn")

    def test_mixed_pdf_without_ocr_is_warn(self) -> None:
        level, msg = ocr_quality(_result(pdf_classification="mixed_pdf"))
        self.assertEqual(level, "warn")
        self.assertIn("mix", msg)

    def test_is_warned_helper_true_when_warned(self) -> None:
        self.assertTrue(
            is_warned(
                _result(
                    ocr_applied=True,
                    metadata={"char_count": 3000, "word_count": 500},
                )
            )
        )

    def test_is_warned_helper_false_when_ok(self) -> None:
        self.assertFalse(is_warned(_result()))

    def test_is_warned_helper_false_when_blocked(self) -> None:
        self.assertFalse(is_warned(_result(status="failed")))

    def test_warn_has_non_empty_message(self) -> None:
        _, msg = ocr_quality(
            _result(
                ocr_applied=True,
                metadata={"char_count": 3000, "word_count": 500},
            )
        )
        self.assertTrue(len(msg) > 0)


class TestOCRGateEdgeCases(unittest.TestCase):
    def test_missing_metadata_does_not_raise(self) -> None:
        result = _result(ocr_applied=True)
        result["metadata"] = None
        level, _ = ocr_quality(result)
        self.assertEqual(level, "blocked")

    def test_zero_char_count_without_ocr_is_not_blocked(self) -> None:
        level, _ = ocr_quality(_result(metadata={"char_count": 0, "word_count": 0}))
        self.assertEqual(level, "ok")

    def test_scanned_pdf_requiring_ocr_is_blocked(self) -> None:
        level, _ = ocr_quality(
            _result(
                pdf_classification="scanned_pdf",
                ocr_required=True,
                ocr_applied=False,
            )
        )
        self.assertEqual(level, "blocked")

    def test_image_heavy_pdf_requiring_ocr_is_blocked(self) -> None:
        level, _ = ocr_quality(
            _result(
                pdf_classification="image_heavy_pdf",
                ocr_required=True,
                ocr_applied=False,
            )
        )
        self.assertEqual(level, "blocked")


if __name__ == "__main__":
    unittest.main()
