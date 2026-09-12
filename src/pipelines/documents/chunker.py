"""
The sliding-window chunking algorithm from ADR-006, made real.

Deliberately a pure function: it takes already-normalized text plus two
integers and returns a list of strings. No import of `Chunk`, no import of
`settings` — that keeps it independently unit-testable (Chapter 6 §3 works
through several word counts by hand against this exact function) and reusable
if a later chapter ever needs to chunk something that isn't page text.

Callers (see ingest.py) run this ONCE PER PAGE, never across a whole
multi-page document at once — see Chapter 6 §3.4 for why a chunk must never
span a page boundary: `Chunk.page` is a citation promise ("view page N"),
and that promise breaks the moment a chunk's text starts on one page and
ends on another.
"""

from __future__ import annotations


def chunk_page_text(text: str, size_words: int, overlap_words: int) -> list[str]:
    """Split one page's text into fixed-size, overlapping word windows.

    ADR-006's numbers (300 words, 50-word overlap) come in as parameters,
    not hardcoded defaults — Chapter 12's ablation (150/300/600 words) needs
    to call this same function with different numbers, not a modified copy
    of it.

    Tail-merge rule: if the final window's NEW (non-overlapping) content
    would be smaller than `overlap_words`, it is folded into the previous
    chunk instead of becoming its own near-duplicate sliver. Worked example
    (Chapter 6 §3.3): a 305-word page with size=300/overlap=50 would
    naively produce a second chunk of just 5 new words sitting on top of
    50 duplicated ones — almost pure redundancy. Merging it into chunk one
    instead means a chunk is at most `size_words` + (a short tail) words
    long, and there is no minimum-length threshold to separately tune.

    A page with fewer words than `size_words` needs no special case at
    all: the loop below emits exactly one chunk, because `end == n` on its
    very first pass.
    """
    if overlap_words >= size_words:
        raise ValueError(
            f"CHUNK_OVERLAP_WORDS ({overlap_words}) must be smaller than "
            f"CHUNK_SIZE_WORDS ({size_words}), or the window never advances."
        )

    words = text.split()
    if not words:
        return []

    step = size_words - overlap_words
    n = len(words)

    # [start, end) index pairs. A list of lists, not tuples, so the tail
    # merge below can extend the last range's end in place.
    ranges: list[list[int]] = []
    start = 0
    while True:
        end = min(start + size_words, n)
        # How many words this window adds beyond where the previous chunk
        # already ended. Only meaningful once a previous chunk exists —
        # `ranges and ...` short-circuits before this matters for the first.
        if ranges and (end - ranges[-1][1]) < overlap_words:
            ranges[-1][1] = end  # merge: extend the previous chunk instead
        else:
            ranges.append([start, end])
        if end == n:
            break
        start += step

    return [" ".join(words[s:e]) for s, e in ranges]
