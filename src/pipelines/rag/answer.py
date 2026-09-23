"""The RAG core orchestrator: retrieve -> filter -> prompt -> generate ->
cite. This is what Chapter 7's search.py docstring meant by "Chapter 10 is
what orchestrates it into a full answer, not what reimplements it."
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from src.core.config import settings
from src.core.llm import generate
from src.core.schemas import Chunk
from src.pipelines.documents.search import search_text
from src.pipelines.rag.prompt import build_prompt

logger = logging.getLogger(__name__)

_CITATION_RE = re.compile(r"\[(\d+)\]")

NOT_ENOUGH_INFO = (
    "I don't have enough information in the indexed documents to answer that."
)


@dataclass
class RagAnswer:
    """The result of one end-to-end question. `citations` is the retrieved
    chunk list, in the exact order the prompt numbered them — index `n - 1`
    for citation "[n]" in `answer` text. Rendering a "Sources:" list from
    this (real Chunk metadata) rather than from anything the model itself
    wrote is deliberate: it decouples "did the model pick a valid citation
    number" (checked separately, see extract_citation_numbers) from "is the
    displayed source string correct" (always correct, since it never came
    from model output)."""

    query: str
    answer: str
    citations: list[Chunk]
    model: str


def extract_citation_numbers(text: str) -> set[int]:
    """Every bracketed integer the answer text cites, e.g. {1, 2} for
    "... supports this [1], and so does this [2]." Used only to detect and
    warn about a citation number outside the range of chunks actually
    shown to the model — never to build the displayed source list."""
    return {int(n) for n in _CITATION_RE.findall(text)}


def _filter_relevant(chunks: list[Chunk]) -> list[Chunk]:
    """Drop chunks scoring below settings.MIN_RELEVANCE_SCORE (ADR-009).
    A pure function over already-retrieved Chunks, deliberately factored
    out of answer_query() so it's testable without a live ChromaDB/Ollama."""
    return [
        c for c in chunks
        if c.score is not None and c.score >= settings.MIN_RELEVANCE_SCORE
    ]


def answer_query(query: str, top_k: int | None = None, client=None) -> RagAnswer:
    """Answer `query` using only chunks retrieved from text_index.

    Chunks scoring below settings.MIN_RELEVANCE_SCORE are dropped before
    the LLM ever sees them (ADR-009) — Chroma's `.query()` always returns
    `top_k` nearest neighbours regardless of how irrelevant they are, so
    without this filter a negative-control question would still hand the
    model 5 "closest of a bad lot" chunks and no honest way to know they
    don't apply. If nothing survives, generation is skipped entirely and a
    fixed not-enough-information answer is returned — deterministic, and
    doesn't spend an LLM call on context that was never going to help.
    """
    chunks = search_text(query, top_k=top_k, client=client)
    relevant = _filter_relevant(chunks)

    if not relevant:
        return RagAnswer(
            query=query, answer=NOT_ENOUGH_INFO, citations=[], model=settings.OLLAMA_MODEL
        )

    prompt = build_prompt(query, relevant)
    answer_text = generate(prompt)

    cited = extract_citation_numbers(answer_text)
    out_of_range = {n for n in cited if n < 1 or n > len(relevant)}
    if out_of_range:
        logger.warning(
            "answer_query: model cited out-of-range number(s) %s for a "
            "%d-chunk context (query=%r)",
            sorted(out_of_range), len(relevant), query,
        )

    return RagAnswer(
        query=query, answer=answer_text, citations=relevant, model=settings.OLLAMA_MODEL
    )
