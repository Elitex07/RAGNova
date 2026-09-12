"""
Shared text cleanup — applied to raw extracted text before it is chunked.

This lives in src/core/, not in a per-track pipelines/ folder, even though
Chapter 6 (Track A, documents) is its first caller. Ch4 §1.3's rule of thumb
for what belongs in core/ is: "if the change is visible to someone calling
into your functions, it needs the interface contract" — and this function's
output shape (a plain str, whitespace-collapsed) is exactly what Chapter 8's
OCR text and Chapter 9's Whisper transcripts will also need before they're
chunked. Putting it here once means three tracks call one tested function
instead of three tracks writing three slightly-different versions of the
same regex.

Spec comes from reports/methodology-draft.md §3.1: "Extracted text is
normalised (whitespace collapsed, control characters removed) before
segmentation." This module is that sentence, made real and tested.
"""

from __future__ import annotations

import re

# Any run of whitespace — spaces, tabs, newlines, form feeds, vertical tabs —
# collapses to a single space. Doing this FIRST (before stripping control
# characters) matters: a newline between two paragraphs must become a space,
# not disappear outright, or "end of page one" and "start of page two" would
# glue into "end of page onestart of page two".
_WHITESPACE_RUN = re.compile(r"\s+")

# Non-whitespace control characters (NUL and other C0 codes, DEL) that
# sometimes leak into text extracted from malformed PDFs or Office files.
# The five whitespace control characters (tab, LF, VT, FF, CR — \x09-\x0d)
# are deliberately excluded from this set: they were already turned into
# plain spaces by _WHITESPACE_RUN above, so they can never reach this step.
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0e-\x1f\x7f]")


def normalize_text(text: str) -> str:
    """Collapse whitespace and strip stray control characters.

    Safe to call on empty input — returns "" rather than raising, since a
    zero-extractable-text page (Chapter 6 §1.4) is a normal, expected case
    for callers of this function, not an error.
    """
    if not text:
        return ""
    collapsed = _WHITESPACE_RUN.sub(" ", text)
    cleaned = _CONTROL_CHARS.sub("", collapsed)
    return cleaned.strip()
