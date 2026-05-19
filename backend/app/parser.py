from __future__ import annotations

import io
import os
import re

PDF_FALLBACK_MESSAGE = (
    "PDF text extraction is unavailable without an optional parser. "
    "Use the built-in sample announcement or upload a decodable text export."
)

_TEXT_ENCODINGS = ("utf-8-sig", "cp949", "euc-kr", "utf-16", "latin-1")


def extract_text_from_upload(filename: str, content: bytes) -> str:
    if not content:
        return ""

    extension = os.path.splitext(filename or "")[1].lower()
    if extension == ".pdf":
        return _extract_pdf_text(content)
    return _decode_best_effort(content)


def _extract_pdf_text(content: bytes) -> str:
    if not content.startswith(b"%PDF"):
        return _decode_best_effort(content)

    # Try PyMuPDF first (faster and more reliable)
    extracted = _extract_pdf_text_with_fitz(content)
    if extracted:
        return extracted

    # Fallback to pypdf
    extracted = _extract_pdf_text_with_pypdf(content)
    if extracted:
        return extracted

    # Last resort: regex fallback
    decoded = content.decode("latin-1", errors="ignore")
    readable_runs = re.findall(r"[A-Za-z0-9:/?&=._\- ()\[\],]{8,}", decoded)
    cleaned = _clean_text("\n".join(readable_runs))
    if _is_meaningful_pdf_fallback(cleaned):
        return cleaned
    return PDF_FALLBACK_MESSAGE


def _extract_pdf_text_with_fitz(content: bytes) -> str:
    """Extract text from PDF using PyMuPDF (fitz)."""
    try:
        import fitz
    except ImportError:
        return ""

    try:
        pdf_document = fitz.open(stream=content, filetype="pdf")
        text_parts = []
        for page_num in range(pdf_document.page_count):
            try:
                page = pdf_document[page_num]
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
            except Exception:
                continue
        pdf_document.close()

        full_text = "\n".join(text_parts)
        cleaned = _clean_text(full_text)
        if _has_human_readable_text(cleaned):
            return cleaned
    except Exception:
        pass

    return ""


def _extract_pdf_text_with_pypdf(content: bytes) -> str:
    if b"%%EOF" not in content[-4096:]:
        return ""

    try:
        from pypdf import PdfReader
    except ImportError:
        return ""

    try:
        reader = PdfReader(io.BytesIO(content), strict=False)
    except Exception:
        return ""

    page_texts: list[str] = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""
        if page_text.strip():
            page_texts.append(page_text)

    cleaned = _clean_text("\n".join(page_texts))
    if _has_human_readable_text(cleaned):
        return cleaned
    return ""


def _decode_best_effort(content: bytes) -> str:
    for encoding in _TEXT_ENCODINGS:
        try:
            text = content.decode(encoding)
        except UnicodeDecodeError:
            continue
        if text.count("\x00") > max(1, len(text) // 10):
            continue
        cleaned = _clean_text(text)
        if cleaned:
            return cleaned
    return ""


def _clean_text(text: str) -> str:
    normalized = text.replace("\x00", " ")
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    normalized = "\n".join(line.strip() for line in normalized.splitlines())
    return normalized.strip()


def _has_human_readable_text(text: str) -> bool:
    if len(text) < 80:
        return False
    korean_chars = len(re.findall(r"[가-힣]", text))
    ascii_words = len(re.findall(r"[A-Za-z]{3,}", text))
    return korean_chars >= 20 or ascii_words >= 20


def _is_meaningful_pdf_fallback(text: str) -> bool:
    if not _has_human_readable_text(text):
        return False

    pdf_object_tokens = (
        "/Filter",
        "/FlateDecode",
        "/Length",
        "/Type",
        "/XObject",
        "endobj",
        "stream",
    )
    object_hits = sum(text.count(token) for token in pdf_object_tokens)
    korean_chars = len(re.findall(r"[가-힣]", text))
    if object_hits >= 3 and korean_chars < 20:
        return False
    return True
