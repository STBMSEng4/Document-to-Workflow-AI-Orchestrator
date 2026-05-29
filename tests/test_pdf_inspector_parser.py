import os
import tempfile
import unittest
from unittest import mock

from app.parsers.pdf_inspector_parser import inspect_pdf


def _usable_ocr_text() -> str:
    sentence = "RTU-1 supply fan status proof shall be provided for BAS integration."
    return "\n".join(
        [
            "## OCR Page 1",
            "",
            " ".join([sentence] * 6),
        ]
    )


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
             mock.patch("app.parsers.pdf_inspector_parser._run_surya_ocr", side_effect=RuntimeError("Surya missing")), \
             mock.patch("app.parsers.pdf_inspector_parser._run_tesseract_ocr", side_effect=RuntimeError("Tesseract missing")):
            result = inspect_pdf(pdf_path)

        self.assertEqual(result["pdf_classification"], "scanned_pdf")
        self.assertTrue(result["ocr_required"])
        self.assertEqual(result["status"], "ocr_required")
        self.assertIn("Surya OCR error", " ".join(result["errors"]))
        self.assertIn("Tesseract OCR error", " ".join(result["errors"]))
        self.assertIn("OCR text is required", " ".join(result["errors"]))

    def test_scanned_pdf_with_surya_returns_success(self) -> None:
        pdf_path = self._make_temp_pdf()
        inspector_payload = {
            "pdfType": "Scanned",
            "confidence": 0.95,
            "markdown": "",
            "pagesNeedingOcr": [1],
        }
        ocr_text = _usable_ocr_text()

        with mock.patch("app.parsers.pdf_inspector_parser._run_pdf_inspector", return_value=inspector_payload), \
             mock.patch("app.parsers.pdf_inspector_parser._run_surya_ocr", return_value=ocr_text) as surya_mock, \
             mock.patch("app.parsers.pdf_inspector_parser._run_tesseract_ocr") as tesseract_mock:
            result = inspect_pdf(pdf_path)

        self.assertEqual(result["pdf_classification"], "scanned_pdf")
        self.assertFalse(result["ocr_required"])
        self.assertTrue(result["ocr_applied"])
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["metadata"]["ocr_engine"], "surya")
        self.assertIn("Applied OCR fallback via Surya", " ".join(result["errors"]))
        self.assertIn("supply fan status", result["raw_markdown"])
        surya_mock.assert_called_once()
        tesseract_mock.assert_not_called()

    def test_scanned_pdf_with_surya_failure_uses_tesseract(self) -> None:
        pdf_path = self._make_temp_pdf()
        inspector_payload = {
            "pdfType": "Scanned",
            "confidence": 0.95,
            "markdown": "",
            "pagesNeedingOcr": [1],
        }
        ocr_text = _usable_ocr_text()

        with mock.patch("app.parsers.pdf_inspector_parser._run_pdf_inspector", return_value=inspector_payload), \
             mock.patch("app.parsers.pdf_inspector_parser._run_surya_ocr", side_effect=RuntimeError("Surya missing")), \
             mock.patch("app.parsers.pdf_inspector_parser._run_tesseract_ocr", return_value=ocr_text) as tesseract_mock:
            result = inspect_pdf(pdf_path)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["metadata"]["ocr_engine"], "tesseract")
        self.assertIn("Surya OCR error", " ".join(result["errors"]))
        self.assertIn("Applied OCR fallback via Tesseract", " ".join(result["errors"]))
        tesseract_mock.assert_called_once()

    def test_scanned_pdf_with_surya_weak_output_uses_tesseract(self) -> None:
        pdf_path = self._make_temp_pdf()
        inspector_payload = {
            "pdfType": "Scanned",
            "confidence": 0.95,
            "markdown": "",
            "pagesNeedingOcr": [1],
        }
        weak_ocr_text = "## OCR Page 1\n\nRTU-1 status"
        tesseract_text = _usable_ocr_text()

        with mock.patch("app.parsers.pdf_inspector_parser._run_pdf_inspector", return_value=inspector_payload), \
             mock.patch("app.parsers.pdf_inspector_parser._run_surya_ocr", return_value=weak_ocr_text), \
             mock.patch("app.parsers.pdf_inspector_parser._run_tesseract_ocr", return_value=tesseract_text) as tesseract_mock:
            result = inspect_pdf(pdf_path)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["metadata"]["ocr_engine"], "tesseract")
        self.assertIn("Surya OCR returned too little text", " ".join(result["errors"]))
        tesseract_mock.assert_called_once()

    def test_text_pdf_bypasses_ocr_engines(self) -> None:
        pdf_path = self._make_temp_pdf()
        inspector_payload = {
            "pdfType": "TextBased",
            "confidence": 0.99,
            "markdown": "RTU-1 shall provide BACnet/IP to the BAS.",
            "pagesNeedingOcr": [],
        }

        with mock.patch("app.parsers.pdf_inspector_parser._run_pdf_inspector", return_value=inspector_payload), \
             mock.patch("app.parsers.pdf_inspector_parser._run_surya_ocr") as surya_mock, \
             mock.patch("app.parsers.pdf_inspector_parser._run_tesseract_ocr") as tesseract_mock:
            result = inspect_pdf(pdf_path)

        self.assertEqual(result["pdf_classification"], "text_pdf")
        self.assertFalse(result["ocr_required"])
        self.assertFalse(result["ocr_applied"])
        self.assertEqual(result["status"], "success")
        self.assertIn("BACnet/IP", result["raw_markdown"])
        surya_mock.assert_not_called()
        tesseract_mock.assert_not_called()

    def test_mixed_pdf_with_markdown_bypasses_ocr_engines(self) -> None:
        pdf_path = self._make_temp_pdf()
        inspector_payload = {
            "pdfType": "Mixed",
            "confidence": 0.85,
            "markdown": "AHU-1 discharge air temperature setpoint shall be adjustable.",
            "pagesNeedingOcr": [2],
        }

        with mock.patch("app.parsers.pdf_inspector_parser._run_pdf_inspector", return_value=inspector_payload), \
             mock.patch("app.parsers.pdf_inspector_parser._run_surya_ocr") as surya_mock, \
             mock.patch("app.parsers.pdf_inspector_parser._run_tesseract_ocr") as tesseract_mock:
            result = inspect_pdf(pdf_path)

        self.assertEqual(result["pdf_classification"], "mixed_pdf")
        self.assertFalse(result["ocr_applied"])
        self.assertEqual(result["status"], "success")
        surya_mock.assert_not_called()
        tesseract_mock.assert_not_called()

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
             mock.patch("app.parsers.pdf_inspector_parser._run_surya_ocr", return_value=ocr_text) as surya_mock, \
             mock.patch("app.parsers.pdf_inspector_parser._run_tesseract_ocr") as tesseract_mock:
            result = inspect_pdf(pdf_path)

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["ocr_applied"])
        self.assertEqual(result["metadata"]["ocr_engine"], "surya")
        self.assertIn("missed point-list content", " ".join(result["errors"]))
        self.assertIn("OCR Page 1", result["raw_markdown"])
        surya_mock.assert_called_once()
        tesseract_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
