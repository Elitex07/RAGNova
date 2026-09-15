"""
ChromaDB connection and collection management — the shared plumbing both
Track A (documents, audio → text_index) and Track B (images → image_index)
write into (ADR-003, ADR-004).

`tests/test_contract.py` (Chapter 5) already proved a chunk survives a raw
ChromaDB round-trip with placeholder zero-vectors. This module is what
Chapter 4 §4.1 meant by "the storage layer is a shared dependency" —
before today, every piece of code that wanted to talk to ChromaDB had to
know its exact API shape itself; from here on, it calls this module
instead.

A `client` is passed explicitly into every function here, rather than
hidden behind a module-level global the way `src.core.config.settings` is.
A database CONNECTION is not the same kind of thing as read-only
configuration: tests need to point at a throwaway temp directory instead
of the real `chroma_db/`, and a hidden global would make that impossible
without monkeypatching. Explicit is worth the one extra argument.
"""

from __future__ import annotations

from pathlib import Path

import chromadb

from src.core.config import settings
from src.core.schemas import Chunk, IMAGE_COLLECTION, TEXT_COLLECTION

# Both collections are created with cosine distance explicitly, rather than
# accepting Chroma's default (squared Euclidean, "l2"). For UNIT-LENGTH
# vectors the two give identical rankings (see embeddings.py's docstring
# and docs/GLOSSARY.md's Cosine similarity entry) — but cosine distance is
# additionally something a human can read directly: Chroma reports cosine
# distance as `1 - cosine_similarity`, a value in [0, 2] where 0 means
# "identical direction," rather than a raw squared-Euclidean number with
# no such intuitive anchor. `search.py` relies on this exact relationship
# to turn a returned distance back into a similarity score.
_COSINE_SPACE = {"hnsw:space": "cosine"}


def get_client(persist_dir: str | Path | None = None) -> chromadb.ClientAPI:
    """A persistent ChromaDB client. Defaults to settings.CHROMA_PERSIST_DIR
    (the real, on-disk index); pass a `tmp_path`-derived directory in tests
    so nothing ever writes into the real index during a test run."""
    return chromadb.PersistentClient(path=str(persist_dir or settings.CHROMA_PERSIST_DIR))


def get_text_collection(client: chromadb.ClientAPI):
    return client.get_or_create_collection(TEXT_COLLECTION, metadata=_COSINE_SPACE)


def get_image_collection(client: chromadb.ClientAPI):
    return client.get_or_create_collection(IMAGE_COLLECTION, metadata=_COSINE_SPACE)


def add_chunks(collection, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    """Write a batch of chunks and their already-computed embedding vectors
    into one collection.

    Deliberately takes embeddings as a separate, explicit argument rather
    than computing them internally — this function has no opinion about
    *which* model produced them (a text collection gets MiniLM vectors, an
    image collection gets CLIP vectors), it only knows how to store
    whatever it's handed, which is exactly the separation of concerns
    ADR-003 requires between "how a modality is embedded" and "where the
    result is stored."

    Does not call `validate_chunk()` itself — by the time a chunk reaches
    this function it should already have passed that check at ingestion
    time (Chapter 6); re-checking it here would be validating the same
    fact twice for no new information.

    Uses `collection.upsert()`, not `collection.add()` — checked directly
    against a real ChromaDB rather than assumed, because the two behave
    very differently on a chunk_id that already exists: `add()` silently
    KEEPS the original stored content and drops the new call entirely (no
    error, no update — confirmed by writing deliberately different text to
    an existing id and reading back the original, unchanged text).
    `upsert()` correctly replaces it. Since this function's whole purpose
    is "make the index reflect the current state of the files," `add()`'s
    silent-no-op behaviour would mean re-running scripts/build_index.py
    after fixing a typo in a source document leaves the index quietly
    serving the pre-fix text forever — exactly the kind of "looks like it
    worked" failure this project's whole testing philosophy exists to
    catch before it becomes a Day-12 surprise.
    """
    if len(chunks) != len(embeddings):
        raise ValueError(
            f"{len(chunks)} chunks but {len(embeddings)} embeddings — "
            f"these must be the same length and in the same order."
        )
    if not chunks:
        return

    ids, documents, metadatas = [], [], []
    for chunk in chunks:
        record = chunk.to_chroma_record()
        ids.append(record["id"])
        documents.append(record["document"])
        metadatas.append(record["metadata"])

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
