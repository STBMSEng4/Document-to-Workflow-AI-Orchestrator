"""Tests for the legacy .doc parser."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.parsers.doc_parser import parse_doc_to_markdown, _plain_text_to_markdown

_REQUIRED_KEYS = {
    "source_type", "source_file", "ingestion_engine",
    "pdf_classification", "raw_markdown", "metadata",
    "ocr_required", "status", "errors",
}

_SAMPLE_DOC_TEXT = (
    "SEQUENCE OF OPERATIONS\n\n"
    "The AHU-1 unit shall enable the supply fan when the space is occupied.\n\n"
    "OCCUPIED MODE\n\n"
    "When the outdoor air temperature is below 55°F, the heating coil valve shall open.\n\n"
    "UNOCCUPIED MODE\n\n"
    "The unit shall be disabled unless a freeze condition is detected.\n"
)


def _make_tmp_doc() -> str:
    """Write a temp file with a .doc suffix (content is fake binary)."""
    with tempfile.NamedTemporaryFile(suffix=".doc", delete=False) as f:
        f.write(b"\xd0\xcf\x11\xe0fake-doc-binary")
        return f.name


class TestDocParserFileGuards(unittest.TestCase):
    def test_missing_file_returns_failed(self) -> None:
        result = parse_doc_to_markdown("definitely_not_a_real_file.doc")
        self.assertEqual(result["status"], "failed")
        self.assertIn("not found", result["errors"][0].lower())

    def test_missing_file_result_has_all_keys(self) -> None:
        result = parse_doc_to_markdown("nonexistent.doc")
        self.assertTrue(_REQUIRED_KEYS.issubset(result.keys()))

    def test_antiword_not_installed_returns_failed(self) -> None:
        tmp = _make_tmp_doc()
        try:
            with patch("app.parsers.doc_parser.shutil.which", return_value=None):
                result = parse_doc_to_markdown(tmp)
            self.assertEqual(result["status"], "failed")
            self.assertTrue(any("antiword" in e.lower() for e in result["errors"]))
        finally:
            Path(tmp).unlink(missing_ok=True)

    def test_antiword_not_installed_message_is_actionable(self) -> None:
        tmp = _make_tmp_doc()
        try:
            with patch("app.parsers.doc_parser.shutil.which", return_value=None):
                result = parse_doc_to_markdown(tmp)
            msg = result["errors"][0]
            self.assertIn("apt-get", msg)
            self.assertIn(".docx", msg)
        finally:
            Path(tmp).unlink(missing_ok=True)


class TestDocParserSuccess(unittest.TestCase):
    def _parse_with_mock(self, stdout: str) -> dict:
        tmp = _make_tmp_doc()
        try:
            with patch("app.parsers.doc_parser.shutil.which", return_value="/usr/bin/antiword"), \
                 patch("app.parsers.doc_parser.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0, stdout=stdout, stderr=""
                )
                return parse_doc_to_markdown(tmp)
        finally:
            Path(tmp).unlink(missing_ok=True)

    def test_successful_parse_returns_success_status(self) -> None:
        result = self._parse_with_mock(_SAMPLE_DOC_TEXT)
        self.assertEqual(result["status"], "success")

    def test_successful_parse_has_all_required_keys(self) -> None:
        result = self._parse_with_mock(_SAMPLE_DOC_TEXT)
        self.assertTrue(_REQUIRED_KEYS.issubset(result.keys()))

    def test_source_type_is_doc(self) -> None:
        result = self._parse_with_mock(_SAMPLE_DOC_TEXT)
        self.assertEqual(result["source_type"], "doc")

    def test_ingestion_engine_is_antiword(self) -> None:
        result = self._parse_with_mock(_SAMPLE_DOC_TEXT)
        self.assertEqual(result["ingestion_engine"], "antiword")

    def test_raw_markdown_contains_extracted_text(self) -> None:
        result = self._parse_with_mock(_SAMPLE_DOC_TEXT)
        self.assertIn("AHU-1", result["raw_markdown"])
        self.assertIn("supply fan", result["raw_markdown"])

    def test_ocr_required_is_false(self) -> None:
        result = self._parse_with_mock(_SAMPLE_DOC_TEXT)
        self.assertFalse(result["ocr_required"])

    def test_metadata_has_char_and_word_counts(self) -> None:
        result = self._parse_with_mock(_SAMPLE_DOC_TEXT)
        meta = result["metadata"]
        self.assertIn("char_count", meta)
        self.assertIn("word_count", meta)
        self.assertGreater(meta["char_count"], 0)
        self.assertGreater(meta["word_count"], 0)


class TestDocParserFailure(unittest.TestCase):
    def test_antiword_nonzero_exit_returns_failed(self) -> None:
        tmp = _make_tmp_doc()
        try:
            with patch("app.parsers.doc_parser.shutil.which", return_value="/usr/bin/antiword"), \
                 patch("app.parsers.doc_parser.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=1, stdout="", stderr="corrupt file format"
                )
                result = parse_doc_to_markdown(tmp)
            self.assertEqual(result["status"], "failed")
            self.assertTrue(len(result["errors"]) > 0)
        finally:
            Path(tmp).unlink(missing_ok=True)

    def test_antiword_error_message_included_in_errors(self) -> None:
        tmp = _make_tmp_doc()
        try:
            with patch("app.parsers.doc_parser.shutil.which", return_value="/usr/bin/antiword"), \
                 patch("app.parsers.doc_parser.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=1, stdout="", stderr="corrupt file format"
                )
                result = parse_doc_to_markdown(tmp)
            self.assertTrue(any("corrupt" in e for e in result["errors"]))
        finally:
            Path(tmp).unlink(missing_ok=True)


class TestPlainTextToMarkdown(unittest.TestCase):
    def test_uppercase_short_line_becomes_heading(self) -> None:
        md = _plain_text_to_markdown("SEQUENCE OF OPERATIONS\n\nSome body text here.")
        self.assertIn("## SEQUENCE OF OPERATIONS", md)

    def test_title_case_short_line_becomes_heading(self) -> None:
        md = _plain_text_to_markdown("Occupied Mode\n\nThe unit shall run.")
        self.assertIn("## Occupied Mode", md)

    def test_long_line_not_converted_to_heading(self) -> None:
        long_line = "When the outdoor air temperature drops below 55 degrees Fahrenheit the heating valve opens."
        md = _plain_text_to_markdown(long_line)
        self.assertNotIn("##", md)

    def test_line_ending_with_period_not_heading(self) -> None:
        md = _plain_text_to_markdown("This is a sentence.\n\nMore text.")
        self.assertNotIn("##", md)

    def test_body_text_preserved_as_is(self) -> None:
        body = "The AHU-1 shall enable when occupied mode is active."
        md = _plain_text_to_markdown(body)
        self.assertIn("AHU-1", md)

    def test_consecutive_blank_lines_collapsed(self) -> None:
        md = _plain_text_to_markdown("Line one\n\n\n\nLine two")
        self.assertNotIn("\n\n\n", md)

    def test_empty_input_returns_empty(self) -> None:
        self.assertEqual(_plain_text_to_markdown(""), "")
        self.assertEqual(_plain_text_to_markdown("   \n\n   "), "")


if __name__ == "__main__":
    unittest.main()
