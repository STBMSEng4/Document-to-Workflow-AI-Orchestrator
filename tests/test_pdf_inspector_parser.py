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
        ocr_text = "\n".join(
            [
                "## OCR Page 1",
                "",
                "RTU-1 supply fan status proof shall be provided for BAS integration.",
                "RTU-1 supply fan status proof shall be provided for BAS integration.",
                "RTU-1 supply fan status proof shall be provided for BAS integration.",
                "RTU-1 supply fan status proof shall be provided for BAS integration.",
                "RTU-1 supply fan status proof shall be provided for BAS integration.",
            ]
        )

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

    def test_mixed_pdf_with_point_list_hints_rescues_with_ocr(self) -> None:
        pdf_path = self._make_temp_pdf()
        inspector_payload = {
            "pdfType": "Mixed",
            "confidence": 0.85,
            "markdown": (
                "## Sequence of Operation\n\n"
                "CONTROL ROOM - CRAC-5 - BAS POINT LIST - DCP-9\n"
                "POINT NO. POINT DESCRIPTION POINT TYPE FIELD DEVICE TYPE\n"
            ),
            "pagesNeedingOcr": [],
        }
        ocr_text = "\n".join(
            [
                "## OCR Page 1",
                "",
                "CONTROL ROOM - CRAC-5 - BAS POINT LIST - DCP-9",
                "1 CRAC-5 UNIT ENABLE DO Dry Contact X X X -- 1",
                "2 CRAC-5 COMMON FAILURE ALARM DO Dry Contact X X X -- 1",
                "3 CRAC-5 FAN STATUS DI Current Status X X X -- 1",
                "4 CRAC-5 SUPPLY AIR TEMPERATURE AI degF Via Integration X X X -- 1",
                "5 CRAC-5 RETURN AIR TEMPERATURE AI degF Via Integration X X X -- 1",
                "6 CRAC-5 LEAK ALARM DI Via Integration X X X -- 1",
            ]
        )

        with mock.patch("app.parsers.pdf_inspector_parser._run_pdf_inspector", return_value=inspector_payload), \
             mock.patch("app.parsers.pdf_inspector_parser._run_tesseract_ocr", return_value=ocr_text) as tesseract_mock:
            result = inspect_pdf(pdf_path)

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["ocr_applied"])
        self.assertEqual(result["metadata"]["ocr_engine"], "tesseract")
        self.assertIn("missed point-list content", " ".join(result["errors"]))
        self.assertIn("OCR Page 1", result["raw_markdown"])
        tesseract_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
