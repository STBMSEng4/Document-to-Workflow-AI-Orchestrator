import os
import tempfile
import unittest
from unittest import mock

from app.parsers.pdf_inspector_parser import inspect_pdf


class PdfInspectorParserTests(unittest.TestCase):
    def _make_temp_pdf(self) -> str:
        handle = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        handle.write(b"%PDF-1.4\n%mock\n")
        handle.close()
        self.addCleanup(lambda: os.path.exists(handle.name) and os.unlink(handle.name))
        return handle.name

    def test_scanned_pdf_without_ocr_stays_ocr_required(self) -> None:
        pdf_path = self._make_temp_pdf()
        inspector_payload = {
            "pdfType": "Scanned",
            "confidence": 0.95,
            "markdown": "",
            "pagesNeedingOcr": [1],
        }

        with mock.patch("app.parsers.pdf_inspector_parser._run_pdf_inspector", return_value=inspector_payload), \
             mock.patch("app.parsers.pdf_inspector_parser._run_tesseract_ocr", side_effect=RuntimeError("Tesseract missing")):
            result = inspect_pdf(pdf_path)

        self.assertEqual(result["pdf_classification"], "scanned_pdf")
        self.assertTrue(result["ocr_required"])
        self.assertEqual(result["status"], "ocr_required")
        self.assertIn("OCR text is required", " ".join(result["errors"]))

    def test_scanned_pdf_with_ocr_returns_success(self) -> None:
        pdf_path = self._make_temp_pdf()
        inspector_payload = {
            "pdfType": "Scanned",
            "confidence": 0.95,
            "markdown": "",
            "pagesNeedingOcr": [1],
        }
        ocr_text = "RTU-1 supply fan status proof shall be provided."

        with mock.patch("app.parsers.pdf_inspector_parser._run_pdf_inspector", return_value=inspector_payload), \
             mock.patch("app.parsers.pdf_inspector_parser._run_tesseract_ocr", return_value=ocr_text):
            result = inspect_pdf(pdf_path)

        self.assertEqual(result["pdf_classification"], "scanned_pdf")
        self.assertFalse(result["ocr_required"])
        self.assertTrue(result["ocr_applied"])
        self.assertEqual(result["status"], "success")
        self.assertIn("Applied OCR fallback", " ".join(result["errors"]))
        self.assertIn("supply fan status", result["raw_markdown"])

    def test_text_pdf_returns_success(self) -> None:
        pdf_path = self._make_temp_pdf()
        inspector_payload = {
            "pdfType": "TextBased",
            "confidence": 0.99,
            "markdown": "RTU-1 shall provide BACnet/IP to the BAS.",
            "pagesNeedingOcr": [],
        }

        with mock.patch("app.parsers.pdf_inspector_parser._run_pdf_inspector", return_value=inspector_payload):
            result = inspect_pdf(pdf_path)

        self.assertEqual(result["pdf_classification"], "text_pdf")
        self.assertFalse(result["ocr_required"])
        self.assertEqual(result["status"], "success")
        self.assertIn("BACnet/IP", result["raw_markdown"])


if __name__ == "__main__":
    unittest.main()
