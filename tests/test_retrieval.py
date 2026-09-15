"""
Chapter 7's test suite: real embeddings, a real ChromaDB index built from
the real Chapter 6 corpus, and real semantic search against it.

Run with:  pytest tests/test_retrieval.py -v

Like tests/test_document_ingestion.py, Part 3 below runs against the real
generated files in data/documents/ (via scripts/generate_sample_corpus.py)
rather than hand-written fixtures — but every test here builds its OWN
throwaway ChromaDB index in a pytest tmp_path, never touching the real,
persistent chroma_db/ this repository's own scripts/build_index.py writes
to. A test suite that could corrupt the real index just by being run
would be a genuinely bad test suite.
"""

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.embeddings import embed_text, embed_texts
from src.core.schemas import Chunk, validate_chunk
from src.core.vector_store import add_chunks, get_client, get_text_collection
from src.pipelines.documents.index import index_documents_directory
from src.pipelines.documents.search import search_text

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "documents"

# Mirrors scripts/evaluate_retrieval.py's GOLD_QUESTIONS — see that file's
# own docstring for why this is a manual copy, not a shared import (kept
# here too, deliberately, so a test failure doesn't depend on the eval
# script's own correctness).
GOLD_QUESTIONS = [
    ("If I don't get my system actually running by evaluation day, how many marks am I giving up?",
     "data/documents/notice.pdf", 2),
    ("As an undergrad, how many items can I check out from the library at once, and for how long?",
     "data/documents/library_hours.pdf", 1),
    ("What happens the first time someone gets caught sharing their login with a friend?",
     "data/documents/it_onboarding.docx", 2),
]


# ---------------------------------------------------------------------------
# Part 1 — embeddings.py: properties of the raw vectors, isolated from
# ChromaDB entirely
# ---------------------------------------------------------------------------

def test_embed_text_returns_a_unit_length_384_dim_vector():
    vector = embed_text("The library is open until ten at night.")
    assert len(vector) == 384
    norm = math.sqrt(sum(x * x for x in vector))
    assert norm == pytest.approx(1.0, abs=1e-4)


def test_embed_text_is_deterministic():
    text = "Wireless internet is available through RAGNOVA-STUDENT."
    assert embed_text(text) == embed_text(text)


def test_embed_texts_batch_matches_individual_calls():
    texts = ["First sentence.", "A completely different second sentence."]
    batch = embed_texts(texts)
    individually = [embed_text(t) for t in texts]
    for b, i in zip(batch, individually):
        assert b == pytest.approx(i, abs=1e-5)


def test_semantically_similar_sentences_score_higher_than_unrelated():
    # A genuine semantic check, not just a shape check: two paraphrases of
    # the same fact should be closer in vector space than either is to an
    # unrelated sentence. Vectors are unit-length (normalize_embeddings=True
    # in embeddings.py), so a plain dot product IS cosine similarity.
    a = embed_text("The library is open from 8am to 10pm on working days.")
    b = embed_text("You can visit the library between eight in the morning and ten at night.")
    c = embed_text("The mid-term prototype demonstration carries forty percent of the marks.")

    def cosine(x, y):
        return sum(xi * yi for xi, yi in zip(x, y))

    sim_ab = cosine(a, b)  # paraphrases of the same fact
    sim_ac = cosine(a, c)  # unrelated topic
    assert sim_ab > sim_ac


# ---------------------------------------------------------------------------
# Part 2 — vector_store.py: storing and retrieving REAL embeddings
# (placeholder zero-vectors were fine for Chapter 5's contract test, which
# was only checking storage of text/metadata; here the vectors themselves
# are the thing under test)
# ---------------------------------------------------------------------------

@pytest.fixture
def text_collection(tmp_path):
    client = get_client(persist_dir=tmp_path / "chroma_test")
    return get_text_collection(client)


def test_add_chunks_round_trips_real_embeddings(text_collection):
    chunks = [
        Chunk(chunk_id="a__p1__c001", source="data/documents/a.pdf", modality="pdf",
              text="First chunk.", embedding_model="all-MiniLM-L6-v2", page=1),
        Chunk(chunk_id="a__p1__c002", source="data/documents/a.pdf", modality="pdf",
              text="Second chunk.", embedding_model="all-MiniLM-L6-v2", page=1),
    ]
    vectors = embed_texts([c.text for c in chunks])
    add_chunks(text_collection, chunks, vectors)

    got = text_collection.get(ids=[c.chunk_id for c in chunks], include=["documents", "metadatas"])
    assert set(got["documents"]) == {"First chunk.", "Second chunk."}
    assert all(m["source"] == "data/documents/a.pdf" for m in got["metadatas"])


def test_add_chunks_rejects_mismatched_lengths(text_collection):
    chunk = Chunk(chunk_id="x", source="data/documents/x.pdf", modality="pdf",
                  text="...", embedding_model="all-MiniLM-L6-v2", page=1)
    with pytest.raises(ValueError):
        add_chunks(text_collection, [chunk], embeddings=[])


def test_add_chunks_empty_list_is_a_noop(text_collection):
    add_chunks(text_collection, [], [])  # must not raise


def test_add_chunks_re_indexing_the_same_id_replaces_stale_content(text_collection):
    # This is the exact behaviour vector_store.py's docstring investigates:
    # plain ChromaDB add() silently KEEPS old content on a duplicate id
    # (confirmed directly against a real collection while writing this
    # chapter, not assumed) — add_chunks() uses upsert() specifically so
    # this test passes instead of proving the opposite.
    original = Chunk(chunk_id="doc__p1__c001", source="data/documents/doc.pdf",
                      modality="pdf", text="Original text.",
                      embedding_model="all-MiniLM-L6-v2", page=1)
    add_chunks(text_collection, [original], embed_texts([original.text]))

    edited = Chunk(chunk_id="doc__p1__c001", source="data/documents/doc.pdf",
                    modality="pdf", text="Edited text, same chunk_id.",
                    embedding_model="all-MiniLM-L6-v2", page=1)
    add_chunks(text_collection, [edited], embed_texts([edited.text]))

    assert text_collection.count() == 1
    got = text_collection.get(ids=["doc__p1__c001"])
    assert got["documents"][0] == "Edited text, same chunk_id."


# ---------------------------------------------------------------------------
# Part 3 — the actual point of this chapter: index the REAL Chapter 6
# corpus into a real (throwaway) ChromaDB, then run real semantic search
# against it.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def indexed_client(tmp_path_factory):
    """Builds the real corpus's index exactly once for every test in this
    module — embedding + HNSW-indexing 6 chunks is cheap, but there's no
    reason to redo it once per test function either."""
    persist_dir = tmp_path_factory.mktemp("chroma_module")
    client = get_client(persist_dir=persist_dir)
    count = index_documents_directory(DOCS_DIR, client=client)
    assert count > 0, (
        "No chunks were indexed — run `python scripts/generate_sample_corpus.py` first."
    )
    return client


def test_index_documents_directory_indexes_every_chunk_from_all_three_files(indexed_client):
    collection = get_text_collection(indexed_client)
    assert collection.count() == 6  # notice.pdf: 3, library_hours.pdf: 1, it_onboarding.docx: 2


def test_search_text_finds_the_right_chunk_for_every_gold_question(indexed_client):
    for question, expected_source, expected_page in GOLD_QUESTIONS:
        results = search_text(question, top_k=5, client=indexed_client)
        hit = any(c.source == expected_source and c.page == expected_page for c in results)
        assert hit, f"'{question}' did not retrieve {expected_source} page {expected_page} in top 5"


def test_search_results_are_sorted_by_descending_score(indexed_client):
    results = search_text("library borrowing rules", top_k=5, client=indexed_client)
    scores = [c.score for c in results]
    assert scores == sorted(scores, reverse=True)


def test_search_results_satisfy_the_contract(indexed_client):
    # Reconstructed chunks (search.py's _chunk_from_result) must be just as
    # valid as freshly-ingested ones — score is the only field retrieval
    # is allowed to add, per Chapter 5's schema.
    results = search_text("acceptable use policy", top_k=5, client=indexed_client)
    for chunk in results:
        assert validate_chunk(chunk) == []
        assert chunk.score is not None
