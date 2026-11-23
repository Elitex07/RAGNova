"""
Per-page text extraction from PDF files, using PyMuPDF.

PyMuPDF's pip package is named "PyMuPDF" (see requirements.txt) but its
import name is `fitz` — a real, common source of "ModuleNotFoundError:
No module named 'fitz'" confusion the first time someone forgets which
name goes where (Chapter 6 §6.3 flags this explicitly).

Optional: OCR fallback for scanned pages (no embedded text layer) using the
existing Tesseract engine from the image pipeline.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import Optional

import fitz
from PIL import Image

# Re-use the image pipeline's Tesseract wrapper — keeps the OCR logic in one place.
# Import is inside the function so the document pipeline doesn't depend on pytesseract
# unless someone actually enables OCR.
def _get_ocr_engine():
    from src.pipelines.images.ocr import TesseractOCREngine
    return TesseractOCREngine()


def extract_pdf_pages(
    path: str | Path,
    ocr_fallback: bool = False,
    ocr_dpi: int = 200,
) -> list[tuple[int, str]]:
    """Return (page_number, raw_text) for every page, in order.

    Page numbers are 1-indexed to match how a human reads a printed page
    (and how `Chunk.page` is documented) — PyMuPDF itself counts pages from
    0, so the +1 below is not a stylistic choice, it's translating between
    two numbering conventions that would otherwise silently disagree.

    Text is returned exactly as PyMuPDF extracts it — un-normalized.
    Normalization (src/core/text_normalize.py) is the caller's job, kept
    separate so this function's output can be inspected and debugged before
    any cleanup is applied to it.

    A page with no extractable text at all (most commonly: a scanned page
    that is really just an image, with no embedded text layer) comes back
    as an empty string here by default. If `ocr_fallback=True`, the page
    is rendered at `ocr_dpi` and passed through Tesseract OCR instead of
    being skipped — the OCR text is then returned for that page.

    Args:
        path: Path to the PDF file.
        ocr_fallback: If True, run OCR on pages that yield no extractable text.
        ocr_dpi: DPI to use when rendering page images for OCR (default 200).
    """
    path = Path(path)
    pages: list[tuple[int, str]] = []
    ocr_engine = _get_ocr_engine() if ocr_fallback else None

    try:
        with fitz.open(path) as doc:
            for page in doc:
                page_num = page.number + 1
                text = page.get_text()
                if not text.strip() and ocr_fallback and ocr_engine and ocr_engine.is_available:
                    # Render the page as an image and run OCR
                    try:
                        mat = fitz.Matrix(ocr_dpi / 72.0, ocr_dpi / 72.0)
                        pix = page.get_pixmap(matrix=mat)
                        img_bytes = pix.tobytes("png")
                        pil_img = Image.open(io.BytesIO(img_bytes))
                        ocr_result = ocr_engine.extract_text(pil_img)
                        text = ocr_result.text
                        if text:
                            print(
                                f"[pdf_parser] OCR fallback on page {page_num}: {ocr_result.words_count} words",
                                file=sys.stderr,
                            )
                    except Exception as exc:
                        print(
                            f"[pdf_parser] WARNING: OCR failed on page {page_num}: {exc}",
                            file=sys.stderr,
                        )
                pages.append((page_num, text))
    except Exception as exc:
        raise ValueError(
            f"Could not read PDF file {path}: {exc}. "
            f"The file may be corrupted, password-protected, or not a valid PDF."
        ) from exc
    return pages


if __name__ == "__main__":
    # Quick manual check: `python -m src.pipelines.documents.pdf_parser <path>`
    # prints each page's extracted word count — handy for eyeballing a real
    # file before writing a test against it.
    if len(sys.argv) != 2:
        print("Usage: python -m src.pipelines.documents.pdf_parser <path-to-pdf>")
        sys.exit(1)
    for page_num, text in extract_pdf_pages(sys.argv[1]):
        print(f"page {page_num}: {len(text.split())} words")
