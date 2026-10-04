from __future__ import annotations

import hashlib
import math
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.config import settings
from src.core.schemas import Chunk, validate_chunk
from src.core.vector_store import get_client, get_text_collection
from src.pipelines.rag.prompt import format_provenance


def fake_embed_texts(texts: list[str]) -> list[list[float]]:
    vectors = []
    for text in texts:
        vector = [0.0] * 384
        for word in re.findall(r"\w+", text.lower()):
            vector[int(hashlib.md5(word.encode()).hexdigest(), 16) % 384] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        vectors.append([value / norm for value in vector])
    return vectors


def fake_embed_text(text: str) -> list[float]:
    return fake_embed_texts([text])[0]


@pytest.fixture
def fake_text_model(monkeypatch):
    monkeypatch.setattr("src.pipelines.documents.search.embed_text", fake_embed_text)
    monkeypatch.setattr("src.pipelines.audio.index.embed_texts", fake_embed_texts)


class FakeIngestor:
    def __init__(self, embedding_model=settings.TEXT_EMBEDDING_MODEL):
        self.embedding_model = embedding_model

    def process_file(self, path):
        return [
            Chunk(
                chunk_id="talk_wav__t0__c000",
                source=str(path),
                modality="audio",
                text="Welcome  to the library orientation.\nThe fine is five rupees per day.",
                embedding_model=self.embedding_model,
                start_s=0.0,
                end_s=12.5,
            ),
            Chunk(
                chunk_id="talk_wav__t12__c001",
                source=str(path),
                modality="audio",
                text="The wifi password is on the back of your ID card.",
                embedding_model=self.embedding_model,
                start_s=12.5,
                end_s=20.0,
            ),
        ]


def test_audio_is_indexed_into_text_index_and_cited_by_timestamp(
    tmp_path,
    monkeypatch,
    fake_text_model,
):
    from src.pipelines.audio.index import index_audio_file
    from src.pipelines.documents.search import search_text

    monkeypatch.chdir(tmp_path)
    audio = Path("data/audio")
    audio.mkdir(parents=True)
    (audio / "talk.wav").write_bytes(b"RIFF fake")

    client = get_client(persist_dir=tmp_path / "chroma")
    assert index_audio_file(
        (audio / "talk.wav").resolve(),
        client=client,
        ingestor=FakeIngestor(),
    ) == 2

    top = search_text("what is the library fine per day", client=client)[0]
    assert top.modality == "audio"
    assert top.source == "data/audio/talk.wav"
    assert (top.start_s, top.end_s) == (0.0, 12.5)
    assert top.text.startswith("Welcome to the library")
    assert format_provenance(top) == "data/audio/talk.wav, 0s–12s"


def test_audio_chunks_that_break_the_contract_are_refused(tmp_path, fake_text_model):
    from src.pipelines.audio.index import index_audio_file

    client = get_client(persist_dir=tmp_path / "chroma")
    with pytest.raises(ValueError, match="embedding_model"):
        index_audio_file(
            tmp_path / "talk.wav",
            client=client,
            ingestor=FakeIngestor(embedding_model=None),
        )
    assert get_text_collection(client).count() == 0


def test_transcribe_query_joins_segments(tmp_path):
    from src.pipelines.audio.transcribe import transcribe_query

    class FakeWhisper:
        def transcribe(self, path, vad_filter=True):
            segments = [
                SimpleNamespace(text=" How late is "),
                SimpleNamespace(text=""),
                SimpleNamespace(text="the library open? "),
            ]
            return iter(segments), None

    assert transcribe_query(tmp_path / "q.wav", model=FakeWhisper()) == "How late is the library open?"


# ---------------------------------------------------------------------------
# The REAL AudioIngestor, with only Whisper faked.
#
# FakeIngestor above stands in for the whole ingestor, so none of the tests
# before this point ever ran AudioIngestor's own code. That let the same bugs
# come back several times while PR #5 was reviewed: embedding_model resolving
# to None (every chunk then fails validate_chunk), a `metadata=` argument that
# Chunk doesn't accept (TypeError on every chunk), chunk ids that changed when
# Whisper's timestamps jittered, and segments duplicated by a retry. These
# tests build the real AudioIngestor and fake only faster-whisper.
# ---------------------------------------------------------------------------

class FakeWhisperModel:
    """Stands in for faster_whisper.WhisperModel. `attempts` has one entry per
    transcribe() call: a list of segments, optionally ending with an Exception
    that is raised after the segments before it have been yielded (a failure
    part-way through a lazy transcription)."""

    def __init__(self, attempts):
        self.attempts = list(attempts)

    def transcribe(self, path, vad_filter=True, vad_parameters=None):
        script = self.attempts.pop(0)

        def generate():
            for item in script:
                if isinstance(item, Exception):
                    raise item
                yield item

        return generate(), SimpleNamespace(duration=20.0)


def _segment(text, start, end):
    return SimpleNamespace(text=text, start=start, end=end)


def _real_ingestor(monkeypatch, attempts):
    from src.pipelines.audio import ingestion

    model = FakeWhisperModel(attempts)
    monkeypatch.setattr(ingestion, "WhisperModel", lambda *args, **kwargs: model)
    monkeypatch.setattr(ingestion.time, "sleep", lambda *_: None)  # skip retry back-off
    return ingestion.AudioIngestor()


def _audio_file(directory, name="lecture.wav", content=b"RIFF fake"):
    path = directory / name
    path.write_bytes(content)
    return path


def test_real_audio_ingestor_chunks_satisfy_the_contract(tmp_path, monkeypatch):
    ingestor = _real_ingestor(monkeypatch, [[
        _segment("Welcome to the library orientation.", 0.0, 4.0),
        _segment("The fine is five rupees per day.", 4.0, 9.0),
    ]])

    chunks = ingestor.process_file(_audio_file(tmp_path))

    assert chunks
    for chunk in chunks:
        assert validate_chunk(chunk) == []
        assert chunk.modality == "audio"
        assert chunk.embedding_model == settings.TEXT_EMBEDDING_MODEL
    assert (chunks[0].start_s, chunks[-1].end_s) == (0.0, 9.0)


def test_real_audio_chunk_ids_ignore_timestamp_jitter_and_differ_per_file(tmp_path, monkeypatch):
    # Whisper's timestamps can shift slightly between two runs over the SAME
    # file; the id must not, or re-indexing adds new chunks instead of
    # replacing the old ones.
    def ids_for(path, start):
        ingestor = _real_ingestor(monkeypatch, [[_segment("Same words every time.", start, start + 3.0)]])
        return [chunk.chunk_id for chunk in ingestor.process_file(path)]

    lecture = _audio_file(tmp_path, "lecture.wav")
    assert ids_for(lecture, 3.99) == ids_for(lecture, 4.02)

    # A different file (here: different folder, same name, different size)
    # must not collide with it.
    other_dir = tmp_path / "other"
    other_dir.mkdir()
    other = _audio_file(other_dir, "lecture.wav", content=b"RIFF a different, longer fake")
    assert ids_for(lecture, 3.99) != ids_for(other, 3.99)


def test_real_audio_ingestor_does_not_duplicate_segments_when_a_retry_restarts_transcription(tmp_path, monkeypatch):
    # Attempt 1 yields two segments, then fails. Attempt 2 starts from the
    # beginning of the file again, so it yields those same two plus a new one.
    first = _segment("Alpha beta gamma.", 0.0, 3.0)
    second = _segment("Delta epsilon zeta.", 3.0, 6.0)
    third = _segment("Eta theta iota.", 6.0, 9.0)
    ingestor = _real_ingestor(monkeypatch, [
        [first, second, RuntimeError("transient failure")],
        [first, second, third],
    ])

    chunks = ingestor.process_file(_audio_file(tmp_path))

    text = " ".join(chunk.text for chunk in chunks)
    for phrase in ("Alpha beta gamma.", "Delta epsilon zeta.", "Eta theta iota."):
        assert text.count(phrase) == 1
