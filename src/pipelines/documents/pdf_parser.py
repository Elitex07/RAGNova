"""
Per-page text extraction from PDF files, using PyMuPDF.

PyMuPDF's pip package is named "PyMuPDF" (see requirements.txt) but its
import name is `fitz` — a real, common source of "ModuleNotFoundError:
No module named 'fitz'" confusion the first time someone forgets which
name goes where (Chapter 6 §6.3 flags this explicitly).
"""

from __future__ import annotations

import sys
from pathlib import Path

import fitz


def extract_pdf_pages(path: str | Path) -> list[tuple[int, str]]:
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
    as an empty string here, same as any other page — it is the caller's
    decision what to do about that (see ingest.py: warn and skip), not this
    function's. This function's only job is "what text is actually in the
    file," not "is that enough."
    """
    path = Path(path)
    pages: list[tuple[int, str]] = []
    with fitz.open(path) as doc:
        for page in doc:
            pages.append((page.number + 1, page.get_text()))
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
