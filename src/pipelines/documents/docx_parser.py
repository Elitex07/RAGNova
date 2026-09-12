"""
Best-effort per-page text extraction from DOCX files.

Read ADR-008 (docs/decisions/adr-008-docx-pagination-via-explicit-breaks.md)
before touching this file — "page" here means something narrower than it
does in pdf_parser.py, and that narrowing is a deliberate, documented
decision, not an oversight.

The short version: a .docx file has no stored concept of "this text is on
page 3." Page boundaries in a real, opened-in-Word document are computed at
render time from fonts, margins, and the printer driver — none of which are
in the file. What IS in the file, and what this module actually detects, is
every place a HUMAN explicitly told Word "start a new page here":

  - A manual page break: <w:br w:type="page"/> inside a run (Ctrl+Enter in
    Word, or `document.add_page_break()` in python-docx).
  - A paragraph-level "page break before" property (common on Heading
    styles): <w:pageBreakBefore/>.

Anything Word would additionally break onto a new page purely because a
paragraph ran out of room on the current one — ordinary text reflow — is
invisible to this approach and always reported as still belonging to
whatever page the last explicit break started. See ADR-008 for why
`w:lastRenderedPageBreak` (which sounds like it would solve exactly this)
is investigated and deliberately not used.
"""

from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn


def _run_has_manual_page_break(run) -> bool:
    """True if this run contains an explicit <w:br w:type="page"/>.

    python-docx exposes no high-level property for this — Run objects have
    no `.has_page_break` — so this drops one level down to the run's
    underlying XML element (`run._element`, a documented, stable escape
    hatch for exactly this kind of gap, not a private implementation
    accident) and looks for the raw <w:br> tag itself. Pinning python-docx
    in requirements.txt matters here: this is the one place this project
    depends on lxml/oxml structure that python-docx's own public API
    doesn't promise to keep stable across versions.
    """
    return any(
        br.get(qn("w:type")) == "page"
        for br in run._element.findall(qn("w:br"))
    )


def extract_docx_pages(path: str | Path) -> list[tuple[int, str]]:
    """Return (page_number, raw_text) per detected page, in order.

    Page numbers are 1-indexed, same convention as extract_pdf_pages(), so
    ingest.py can treat both parsers identically. Paragraphs before the
    first detected break are page 1 by construction; a document with zero
    manual breaks anywhere comes back as a single page 1.

    Only top-level body paragraphs are read — text inside tables, headers,
    and footers is out of scope for this chapter (noted in Chapter 6 §2.6,
    not silently dropped without comment).
    """
    document = Document(Path(path))
    pages: list[list[str]] = [[]]
    page_num = 1

    for paragraph in document.paragraphs:
        # Checked first: a heading styled "page break before" starts a new
        # page even if it's otherwise a perfectly ordinary paragraph.
        if paragraph.paragraph_format.page_break_before:
            page_num += 1
            pages.append([])

        if paragraph.text.strip():
            pages[page_num - 1].append(paragraph.text)

        # Checked after appending this paragraph's own text: a manual break
        # (Ctrl+Enter) lives in its own, essentially textless paragraph, so
        # the NEXT paragraph is the first one that actually belongs to the
        # new page — matching how `document.add_page_break()` and Word's
        # own Ctrl+Enter both construct the underlying XML.
        if any(_run_has_manual_page_break(r) for r in paragraph.runs):
            page_num += 1
            pages.append([])

    return [(i + 1, "\n".join(p)) for i, p in enumerate(pages)]


if __name__ == "__main__":
    # `python -m src.pipelines.documents.docx_parser <path>` — prints each
    # detected page's word count, same spirit as pdf_parser's debug entry
    # point.
    if len(sys.argv) != 2:
        print("Usage: python -m src.pipelines.documents.docx_parser <path-to-docx>")
        sys.exit(1)
    for page_num, text in extract_docx_pages(sys.argv[1]):
        print(f"page {page_num}: {len(text.split())} words")
