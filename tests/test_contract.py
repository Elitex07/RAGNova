"""
The contract test — real implementation of Chapter 4 §1.6 / §4.4.

Run this with:  pytest tests/test_contract.py -v

What this file is NOT: a test of any track's internal logic (which parser,
which chunk size, which model checkpoint — Ch4 §1.3 says that's each track's
own business). It checks exactly one thing, for exactly one reason: does
every real chunk each track produces satisfy the shared schema (Ch4 §4.2)?

Every team member runs this before pushing, and it belongs in whatever CI
step the team sets up (even a manual "run this before you push" habit is
fine for a 9-day sprint — the important thing is that it runs before
integration day, not on it).

Fixtures below are HAND-WRITTEN sample data, not output from a real
pipeline — Chapters 6-9 don't exist yet on Day 5. That is the point: the
fixtures encode what each track has *promised* to produce, agreed today,
so the promise itself is checkable from day one.
"""

import sys
from pathlib import Path

import pytest

# Allow running `pytest tests/test_contract.py` from the project root without
# installing the project as a package first — matches Chapter 0's
# beginner-friendly no-packaging-ceremony approach. (A `pyproject.toml`
# with an editable install is the more "correct" fix; noted as a Chapter 5
# optional-extras item, not required to get started.)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.schemas import Chunk, validate_chunk, TEXT_COLLECTION, IMAGE_COLLECTION


# ---------------------------------------------------------------------------
# The three fixtures — one hand-built example per modality family, per
# Ch4 §4.4's table. Track A owns the text fixture, Track B owns the image
# and audio fixtures. Splitting fixture ownership this way means each
# track is the one asserting, in code, exactly what it intends to emit.
# ---------------------------------------------------------------------------

@pytest.fixture
def text_fixture() -> Chunk:
    """Owner: Track A. What a real PDF-parsing chunk will look like."""
    return Chunk(
        chunk_id="notice_pdf__p2__c003",
        source="data/documents/notice.pdf",
        modality="pdf",
        text="The submission deadline for the project synopsis is 21st August.",
        embedding_model="all-MiniLM-L6-v2",
        page=2,
    )


@pytest.fixture
def image_fixture() -> Chunk:
    """Owner: Track B. What a real CLIP + OCR image record will look like."""
    return Chunk(
        chunk_id="screenshot_png__c001",
        source="data/images/email_screenshot.png",
        modality="image",
        text="Subject: Invoice #4471 — Payment Due",  # OCR'd text, may be ""
        embedding_model="ViT-B-32/laion2b_s34b_b79k",
    )


@pytest.fixture
def audio_fixture() -> Chunk:
    """Owner: Track B. What a real Whisper transcript chunk will look like."""
    return Chunk(
        chunk_id="lecture3_mp3__t872__c001",
        source="data/audio/lecture3.mp3",
        modality="audio",
        text="...and that's why retrieval converts recall into reading comprehension...",
        embedding_model="all-MiniLM-L6-v2",  # transcripts are indexed as text (ADR-005)
        start_s=872.4,
        end_s=891.0,
    )


# ---------------------------------------------------------------------------
# Part 1 — each fixture satisfies the contract
# ---------------------------------------------------------------------------

def test_text_fixture_is_valid(text_fixture):
    errors = validate_chunk(text_fixture)
    assert errors == [], f"Track A's fixture violates the contract: {errors}"


def test_image_fixture_is_valid(image_fixture):
    errors = validate_chunk(image_fixture)
    assert errors == [], f"Track B's image fixture violates the contract: {errors}"


def test_audio_fixture_is_valid(audio_fixture):
    errors = validate_chunk(audio_fixture)
    assert errors == [], f"Track B's audio fixture violates the contract: {errors}"


# ---------------------------------------------------------------------------
# Part 2 — routing: each fixture lands in the collection ADR-003 assigns it
# ---------------------------------------------------------------------------

def test_text_and_audio_route_to_text_collection(text_fixture, audio_fixture):
    assert text_fixture.default_collection() == TEXT_COLLECTION
    assert audio_fixture.default_collection() == TEXT_COLLECTION


def test_image_routes_to_image_collection(image_fixture):
    assert image_fixture.default_collection() == IMAGE_COLLECTION


# ---------------------------------------------------------------------------
# Part 3 — the contract test must have teeth: it should REJECT broken chunks,
# not just accept good ones. A test suite that only ever passes is not
# proof the check works — these are the "no schema freeze" counterfactual
# from Ch4 §1.7, made concrete and automated.
# ---------------------------------------------------------------------------

def test_rejects_missing_page_on_document():
    broken = Chunk(
        chunk_id="x", source="data/documents/x.pdf", modality="pdf",
        text="...", embedding_model="all-MiniLM-L6-v2",
        # page intentionally omitted
    )
    errors = validate_chunk(broken)
    assert any("page" in e for e in errors)


def test_rejects_audio_with_end_before_start():
    broken = Chunk(
        chunk_id="x", source="data/audio/x.mp3", modality="audio",
        text="...", embedding_model="all-MiniLM-L6-v2",
        start_s=10.0, end_s=5.0,  # end before start — exactly the kind of
                                   # bug that should fail loudly, not silently
    )
    errors = validate_chunk(broken)
    assert any("end_s" in e for e in errors)


def test_rejects_wrong_modality_string():
    broken = Chunk(
        chunk_id="x", source="data/x.mp3", modality="audioo",  # typo
        text="...", embedding_model="all-MiniLM-L6-v2",
    )
    errors = validate_chunk(broken)
    assert any("modality" in e for e in errors)


def test_rejects_cross_contaminated_fields():
    """A pdf chunk that also carries audio fields — the exact 'wrong field,
    nobody noticed' scenario Ch4 §1.7 warns about."""
    broken = Chunk(
        chunk_id="x", source="data/documents/x.pdf", modality="pdf",
        text="...", embedding_model="all-MiniLM-L6-v2",
        page=1, start_s=5.0, end_s=10.0,  # start_s/end_s don't belong here
    )
    errors = validate_chunk(broken)
    assert any("start_s" in e for e in errors)


# ---------------------------------------------------------------------------
# Part 4 — round-trip through ChromaDB itself, when it's installed.
#
# This is the strongest form of the contract test: it doesn't just check the
# Python object, it proves the object survives the actual storage layer
# (ADR-004) unchanged. It's written to SKIP gracefully rather than fail if
# chromadb isn't installed yet — appropriate for Day 5 morning, before the
# full requirements.txt has necessarily been pip-installed by every member.
# ---------------------------------------------------------------------------

def test_round_trips_through_chromadb(text_fixture, image_fixture, audio_fixture, tmp_path):
    chromadb = pytest.importorskip("chromadb", reason="chromadb not installed yet")

    client = chromadb.PersistentClient(path=str(tmp_path / "chroma_test"))
    text_col = client.get_or_create_collection(TEXT_COLLECTION)
    image_col = client.get_or_create_collection(IMAGE_COLLECTION)

    for chunk, col in [(text_fixture, text_col), (audio_fixture, text_col)]:
        rec = chunk.to_chroma_record()
        # A placeholder embedding — real pipelines supply a real vector;
        # the contract test only cares that storage and retrieval of the
        # TEXT and METADATA survive unchanged.
        col.add(ids=[rec["id"]], documents=[rec["document"]],
                 metadatas=[rec["metadata"]], embeddings=[[0.0] * 384])
        got = col.get(ids=[rec["id"]], include=["documents", "metadatas"])
        assert got["documents"][0] == chunk.text
        assert got["metadatas"][0]["source"] == chunk.source

    rec = image_fixture.to_chroma_record()
    image_col.add(ids=[rec["id"]], documents=[rec["document"]],
                    metadatas=[rec["metadata"]], embeddings=[[0.0] * 512])
    got = image_col.get(ids=[rec["id"]], include=["documents", "metadatas"])
    assert got["metadatas"][0]["modality"] == "image"
