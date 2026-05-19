from __future__ import annotations

import unittest

from backend.app.parser import PDF_FALLBACK_MESSAGE, extract_text_from_upload


class ParserExtractionTests(unittest.TestCase):
    def test_extract_text_file_with_korean_encoding(self) -> None:
        text = "신청 기간: 2026-05-01 ~ 2026-05-31\n지원 대상: 서울 거주 청년"
        result = extract_text_from_upload("notice.txt", text.encode("cp949"))

        self.assertIn("신청 기간", result)
        self.assertIn("서울 거주", result)

    def test_extract_text_from_pdf_with_pymupdf(self) -> None:
        try:
            import fitz
        except ImportError as exc:
            self.skipTest(f"PyMuPDF is not installed: {exc}")

        document = fitz.open()
        page = document.new_page()
        page.insert_text(
            (72, 72),
            "DocMate scholarship notice application period is from May first to May thirty first. "
            "Eligible students prepare registration certificate income proof recommendation letter "
            "and submit the online form before the deadline.",
        )
        pdf_bytes = document.write()
        document.close()

        result = extract_text_from_upload("notice.pdf", pdf_bytes)

        self.assertIn("DocMate scholarship notice", result)
        self.assertIn("registration certificate", result)

    def test_corrupt_pdf_falls_back_safely(self) -> None:
        result = extract_text_from_upload("broken.pdf", b"%PDF-1.4\nbroken content")

        self.assertEqual(result, PDF_FALLBACK_MESSAGE)


if __name__ == "__main__":
    unittest.main()
