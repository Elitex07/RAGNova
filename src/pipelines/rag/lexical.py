"""
Name and identifier lookups: admit a chunk because the question's distinctive words are literally in it.

Why (2026-10-11): "who is alex morgan?" was refused on the live page although the corpus holds Alex Morgan's
ID card. The card is indexed with its text ("STUDENT ID Alex Morgan | Roll No: 23AIML042 ..."), but

  * CLIP cannot match a name (text-to-image score 0.151 against a 0.2 floor), and
  * MiniLM scores a two-word name against a whole ID-card's text at 0.16 against a 0.30 bar (ADR-011),

so the image gate drops it. Dense search is built for meaning, and a name has none to match. A name is
exactly what an exact-word lookup is good at, so this adds one, as a second way in beside the floors.

THE RULE (fixed before it was measured; scripts/evaluate_entity_questions.py)
  * The question's CONTENT words are its words minus question words, filler and anything shorter than 3
    characters (digits are kept: "302").
  * A content word is DISTINCTIVE when it occurs in 1 to `max_df` indexed FILES (not chunks), UNKNOWN when it occurs in none.
  * Mode "distinctive": a chunk is admitted when it contains EVERY distinctive word, provided the distinctive
    words are at least MIN_COVERAGE (60%) of distinctive + unknown. Mode "all": it must contain every KNOWN
    content word (distinctive or common), with known words at least MIN_COVERAGE of known + unknown; and in both
    modes there must be at least one distinctive word, so a question made only of common words looks nothing up.
    "alex morgan" admits the card; "alex smith" does not (smith is unknown: 1 of 2 = 50%); "alex morgan's blood
    group" does not (no chunk holds alex, morgan AND blood). The two modes differ when a name's first word is
    common: "alex" is in 8 indexed files (paper authors), so in "distinctive" mode only "morgan" has to match.
  * At most LIMIT chunks are admitted, shortest first (the more concentrated chunk), and the caller puts them
    first in their modality's list.

What it does NOT do: it does not judge whether the chunk ANSWERS the question. An admitted chunk is context,
and the model's own refusal rule still decides, as for every image the gate lets through (ADR-011).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.core.schemas import Chunk
from src.pipelines.rag.retrieve import _GENERIC_WORDS

MIN_COVERAGE = 0.6
LIMIT = 3

# Words that open or pad a question and say nothing about its subject, beyond retrieve._GENERIC_WORDS.
_FILLER = frozenset("""
explain describe mean means meaning know known called named name tell more details detail information info
whats hows
""".split())

_POSSESSIVE = re.compile(r"['’]s\b")
# A word, or an identifier that keeps its inner punctuation: lib-884920, vpn.ragnova.edu, final_synopsis_team12.pdf
_TOKEN = re.compile(r"[a-z0-9](?:[a-z0-9._\-]*[a-z0-9])?")


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(_POSSESSIVE.sub("", text.lower()))


def content_tokens(query: str) -> list[str]:
    """The question's content words, in order, without repeats."""
    seen: dict[str, None] = {}
    for token in tokenize(query):
        if token in _GENERIC_WORDS or token in _FILLER:
            continue
        if len(token) < 3 and not any(ch.isdigit() for ch in token):
            continue
        seen.setdefault(token)
    return list(seen)


@dataclass(frozen=True)
class Entry:
    chunk_id: str
    source: str
    collection: str          # "text" or "image": which ChromaDB collection holds the chunk
    tokens: frozenset[str]


class LexicalIndex:
    """Which words occur in which chunks and in how many files. Built from the index's own documents."""

    def __init__(self, rows):
        """`rows`: (chunk_id, source, collection, text) for every chunk."""
        self.entries: list[Entry] = []
        self._files: dict[str, set[str]] = {}
        for chunk_id, source, collection, text in rows:
            tokens = frozenset(tokenize(text))
            self.entries.append(Entry(chunk_id, source, collection, tokens))
            for token in tokens:
                self._files.setdefault(token, set()).add(source)

    def df(self, token: str) -> int:
        """In how many indexed FILES the word occurs."""
        return len(self._files.get(token, ()))


def admit(query: str, index: LexicalIndex, max_df: int = 2, min_coverage: float = MIN_COVERAGE, limit: int = LIMIT,
          mode: str = "distinctive") -> list[Entry]:
    """The chunks the rule above admits for `query`, best first. [] when there is nothing distinctive to look up."""
    if mode not in ("distinctive", "all"):
        raise ValueError(f"unknown lexical mode {mode!r}: use 'distinctive' or 'all'")
    tokens = content_tokens(query)
    distinctive = [t for t in tokens if 1 <= index.df(t) <= max_df]
    known = [t for t in tokens if index.df(t) >= 1]
    unknown = [t for t in tokens if index.df(t) == 0]
    if not distinctive:
        return []
    required = distinctive if mode == "distinctive" else known
    if len(required) / (len(required) + len(unknown)) < min_coverage:
        return []
    matches = [e for e in index.entries if all(t in e.tokens for t in required)]
    matches.sort(key=lambda e: len(e.tokens))
    return matches[:limit]


# ---------------------------------------------------------------------------
# Against the real index
# ---------------------------------------------------------------------------

_cache: dict[tuple, LexicalIndex] = {}


def _index_for(client) -> LexicalIndex:
    """The lexical index of this ChromaDB, rebuilt when the number of chunks in either collection changes (an upload,
    a rebuild). Re-indexing a changed file to the SAME number of chunks is not noticed until the process restarts."""
    from src.core.vector_store import get_image_collection, get_text_collection

    text_collection, image_collection = get_text_collection(client), get_image_collection(client)
    key = (id(client), text_collection.count(), image_collection.count())
    if key not in _cache:
        _cache.clear()
        rows = []
        for collection, name in ((text_collection, "text"), (image_collection, "image")):
            if collection.count():
                got = collection.get(include=["documents", "metadatas"])
                rows += [(i, m["source"], name, d) for i, d, m in zip(got["ids"], got["documents"], got["metadatas"])]
        _cache[key] = LexicalIndex(rows)
    return _cache[key]


def lexical_hits(query: str, client=None, max_df: int = 2, mode: str = "distinctive") -> tuple[list[Chunk], list[Chunk]]:
    """(text chunks, image chunks) the rule admits for `query`, each with no score: they were not ranked by
    similarity, they matched words."""
    from dataclasses import replace

    from src.core.vector_store import get_client, get_image_collection, get_text_collection
    from src.pipelines.documents.search import _chunk_from_result

    client = client or get_client()
    admitted = admit(query, _index_for(client), max_df=max_df, mode=mode)
    text_chunks: list[Chunk] = []
    image_chunks: list[Chunk] = []
    for collection, name, bucket in ((get_text_collection(client), "text", text_chunks), (get_image_collection(client), "image", image_chunks)):
        ids = [e.chunk_id for e in admitted if e.collection == name]
        if not ids:
            continue
        got = collection.get(ids=ids, include=["documents", "metadatas"])
        by_id = {i: (d, m) for i, d, m in zip(got["ids"], got["documents"], got["metadatas"])}
        for chunk_id in ids:                      # keep the rule's order
            text, metadata = by_id[chunk_id]
            bucket.append(replace(_chunk_from_result(chunk_id, text, metadata, 1.0), score=None))
    return text_chunks, image_chunks
