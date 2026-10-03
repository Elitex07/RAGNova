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
from src.core.schemas import Chunk
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
