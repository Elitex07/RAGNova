"""
The first real semantic search this project can run: embed a query string
with the same model and normalization used at ingestion, ask ChromaDB's
text_index for the nearest chunks, and hand back real Chunk objects with
`.score` populated.

This function is deliberately built to be reusable, not a one-off demo —
scripts/evaluate_retrieval.py calls it to measure Recall@5/MRR against
Chapter 6's gold-set rows, and Chapter 10's RAG core will call this same
function as its retrieval step, then add generation and citation
formatting on top. Chapter 5's schemas.py docstring says "Chapter 10's
retrieval code attaches [score]" — this IS that retrieval code; Chapter 10
is what orchestrates it into a full answer, not what reimplements it.
"""

from __future__ import annotations

from src.core.config import settings
from src.core.embeddings import embed_text
from src.core.schemas import Chunk
from src.core.vector_store import get_client, get_text_collection


def only_sources(sources: list[str] | None) -> dict | None:
    """The ChromaDB `where` filter that limits a query to these `source` paths
    (None = no limit). Shared by every search that takes a `sources` scope."""
    return {"source": {"$in": list(sources)}} if sources is not None else None


def search_text(
    query: str, top_k: int | None = None, client=None, sources: list[str] | None = None,
    bm25_index=None,
) -> list[Chunk]:
    """Return the `top_k` chunks in text_index most similar to `query`,
    best match first.

    `sources` limits the search to those files (their `source` paths, as stored
    in the index); None searches everything, which is what every caller before
    2026-10-10 did. An empty list matches nothing.

    `top_k` defaults to settings.TOP_K (Chapter 1 §1.10 / .env), so every
    caller doesn't have to independently decide and hardcode a number.

    Passes `query_embeddings=`, never `query_texts=`, to ChromaDB's
    `.query()`. This distinction matters more than it looks: `query_texts`
    would silently ask Chroma to embed the query with ITS OWN default
    embedding function (not necessarily the same model, or even the same
    weights of the same model, as embeddings.py uses) — comparing a query
    vector from one model against stored vectors from another produces
    numbers that look like similarity scores but aren't measuring anything
    coherent. Always embedding the query ourselves is what keeps every
    vector in this comparison coming from the same model (Chapter 7 §2.3's
    misconception check works through this failure mode concretely).

    When `bm25_index` is supplied and settings.HYBRID_BM25_DENSE is True, the
    dense results are re-scored with a blend of MiniLM cosine and BM25
    (settings.HYBRID_ALPHA controls the mix). The BM25 index is built once by
    scripts/build_index.py and passed in; it must have been built over the
    same corpus the ChromaDB collection holds, otherwise the blend mixes
    vectors from two different worlds.
    """
    top_k = top_k or settings.TOP_K
    client = client or get_client()
    collection = get_text_collection(client)

    if sources is not None and not sources:
        return []

    query_vector = embed_text(query)
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
        where=only_sources(sources),
    )

    chunks = []
    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    for chunk_id, text, metadata, distance in zip(ids, documents, metadatas, distances):
        chunks.append(_chunk_from_result(chunk_id, text, metadata, distance))

    if bm25_index is not None and settings.HYBRID_BM25_DENSE and chunks:
        chunks = _apply_hybrid_blend(chunks, query, settings.HYBRID_ALPHA)

    return chunks


def _apply_hybrid_blend(
    chunks: list[Chunk], query: str, alpha: float, bm25_index=None
) -> list[Chunk]:
    """Re-score `chunks` by `alpha * dense + (1 - alpha) * bm25_normalized`,
    best first. Both scores are normalized to [0, 1] across the result set
    before blending, so the two scales (cosine similarity vs raw BM25) are
    comparable; a raw BM25 of 12.4 and a cosine of 0.62 would otherwise mean
    the BM25 term always wins. Pure over the list it is given — the stored
    vectors are untouched, only the ordering and the returned `.score` change.

    BM25 is scored over the retrieved chunks themselves, never by position
    against a separately built corpus index. ChromaDB's result order is not
    corpus order, so matching a corpus-wide BM25 index by result position
    would score the wrong document and silently re-rank chunks against the
    wrong evidence. If a `bm25_index` is supplied it is ignored for scoring;
    build the blend over exactly these chunks instead.
    """
    from src.core.bm25 import BM25, tokenize
    from dataclasses import replace

    query_tokens = tokenize(query)
    bm25 = BM25([tokenize(chunk.text) for chunk in chunks])
    bm25_scores = bm25.scores(query_tokens)

    # Handle empty or uniform scores gracefully
    dense_scores = [c.score or 0.0 for c in chunks]

    def _norm(vals: list[float]) -> list[float]:
        lo, hi = min(vals), max(vals)
        if hi == lo:
            return [0.5] * len(vals)
        # Add epsilon to denominator to avoid division by zero
        eps = 1e-8
        return [(v - lo) / (hi - lo + eps) for v in vals]

    dense_n = _norm(dense_scores)
    bm25_n = _norm(bm25_scores)
    blended = [
        alpha * d + (1 - alpha) * b
        for d, b in zip(dense_n, bm25_n)
    ]

    reranked = [
        replace(chunk, score=round(score, 6))
        for chunk, score in zip(chunks, blended)
    ]
    reranked.sort(key=lambda c: c.score or 0.0, reverse=True)
    return reranked


def _chunk_from_result(chunk_id: str, text: str, metadata: dict, distance: float) -> Chunk:
    """Rebuild a Chunk from one row of a ChromaDB query result.

    The inverse of Chunk.to_chroma_record(): that method omits a
    modality-specific field entirely when it's None (ChromaDB's metadata
    can't store None), so reconstruction here must use `.get()` with a
    None default for every optional field, not a plain `metadata[...]`
    lookup — a text chunk's metadata genuinely has no "start_s" key at
    all, not a "start_s": None entry.

    `score` is cosine similarity, `1 - distance` — the exact inverse of
    the `hnsw:space: "cosine"` configuration vector_store.py sets when the
    collection is created (see that module's docstring for why cosine
    distance specifically was chosen).
    """
    bbox = metadata.get("bbox")
    return Chunk(
        chunk_id=chunk_id,
        source=metadata["source"],
        modality=metadata["modality"],
        text=text,
        embedding_model=metadata["embedding_model"],
        page=metadata.get("page"),
        start_s=metadata.get("start_s"),
        end_s=metadata.get("end_s"),
        bbox=tuple(bbox) if bbox is not None else None,
        score=1.0 - distance,
    )
