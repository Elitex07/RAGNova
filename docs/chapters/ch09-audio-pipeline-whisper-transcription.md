# Chapter 9 — Audio Pipeline: Whisper Transcription (Day 10)

> **Deliverables today:** a complete audio ingestion pipeline (`src/pipelines/audio/`): Whisper transcription with VAD (voice activity detection), sliding-window chunking with word-level timestamps, transcript chunks written into `text_index` (not a third collection — ADR-005's transcription-over-native-audio decision), portable source paths with timestamp ranges for citations, and `tests/test_audio_pipeline.py`.
>
> **Prerequisites:** [Chapter 7](ch07-embeddings-and-vector-database.md) (the `text_index` collection and `add_chunks()` primitive this chapter reuses for audio transcripts) and [ADR-005](../decisions/adr-005-transcription-over-clap.md) (why transcription, not native audio embeddings like CLAP).
>
> **The framing for today.** Audio is the third modality RAGNova handles, but unlike images (which got their own `image_index` collection in Chapter 8), audio transcripts go into the *existing* `text_index` alongside documents — because ADR-005 chose transcription over native audio embeddings. A transcript chunk is just text with a timestamp range (`start_s`, `end_s`) instead of a page number, embedded by the same MiniLM model (Chapter 7) as PDFs. This shared embedding space is what lets one text question retrieve a PDF paragraph, a DOCX section, and a spoken sentence in the same search.

---

## How to read this chapter

| Part | What it does | Time |
|---|---|---|
| **Part 1 — LEARN: Whisper in Practice** | Loading faster-whisper, VAD (voice activity detection), language detection, word-level timestamps. | ~30 min |
| **Part 2 — LEARN: Sliding-Window Chunking** | Target chunk size in words (not seconds), overlap for continuity, splitting mid-segment. | ~30 min |
| **Part 3 — LEARN: Why Audio Goes Into text_index** | ADR-005's decision, embedding transcripts with MiniLM, timestamp-based citations. | ~20 min |
| **Part 4 — DECIDE** | Module layout, binding to `settings.TEXT_EMBEDDING_MODEL`, chunk target size, retry strategy. | ~20 min |
| **Part 5 — BUILD** | Writing each file, transcribing real audio, indexing into `text_index`, citations with timestamps. | ~2 hours |
| **Part 6 — CHECK** | Rubric, question bank, troubleshooting, completion checklist. | ~30 min |

**Learning outcomes.** You will be able to: call faster-whisper to transcribe audio with VAD; explain why VAD matters for chunking; implement sliding-window chunking with word-level timestamps; explain why audio transcripts are embedded with MiniLM and written into `text_index`, not a separate collection; and trace through the timestamp-based citation format (`data/audio/talk.wav, 12s–20s`).

---

# Part 1 — LEARN: Whisper in Practice

## 1.1 Whisper vs. faster-whisper

OpenAI's original Whisper implementation is accurate but slow on CPU. `faster-whisper` is a CTranslate2-based reimplementation that's 4x faster with the same accuracy, using quantized models (int8) — crucial for Chapter 5's CPU-only, 8GB RAM constraint. Model sizes range from `tiny` (39M params, fast but less accurate) to `large` (1550M params, very accurate but slow). This project defaults to `base` (74M params) — a balance for CPU inference.

## 1.2 Loading and calling faster-whisper

```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe("audio.mp3", vad_filter=True)

for segment in segments:
    print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")
```

`vad_filter=True` enables voice activity detection — the model only processes audio segments that actually contain speech, skipping silence and background noise. Without it, Whisper still returns segments for silent sections (often as empty strings or hallucinated filler), which would create useless chunks.

## 1.3 Language detection

```python
segments, info = model.transcribe("audio.mp3", vad_filter=True)
print(f"Detected language: {info.language} (probability={info.language_probability:.2f})")
```

Whisper auto-detects the spoken language from the first few seconds of audio. For this project (English-language corpus), this is a logging convenience, not a feature — but it's available if the corpus ever expands to non-English audio.

## 1.4 Word-level timestamps

```python
segments, info = model.transcribe("audio.mp3", word_timestamps=True)
for segment in segments:
    for word in segment.words:
        print(f"{word.word} [{word.start:.2f}s - {word.end:.2f}s]")
```

Each segment (a sentence or phrase) contains word-level timing data. This is what enables sliding-window chunking (Part 2) to split a segment at a precise word boundary when a chunk reaches its target size, rather than cutting mid-sentence arbitrarily.

---

# Part 2 — LEARN: Sliding-Window Chunking

## 2.1 Why chunk audio at all?

A 10-minute recording transcribed in one piece would produce a single, multi-paragraph chunk. Embedding that entire block loses granularity — a question about one specific fact in minute 3 would retrieve the entire 10-minute chunk, and the LLM (Chapter 10) would have to find the relevant sentence buried in irrelevant context. Chunking by fixed time intervals (e.g., every 30 seconds) would split mid-sentence. Chunking by Whisper's segments (which are sentence-like) is better but still variable — some segments are 5 words, others 50.

## 2.2 Target chunk size in words, not seconds

`settings.AUDIO_CHUNK_TARGET_WORDS = 300` (same target as document chunks, Chapter 6's `CHUNK_SIZE_WORDS`). The ingestion pipeline buffers Whisper segments until the accumulated word count reaches 300, then emits a chunk and starts a new buffer. This produces semantically-coherent chunks (not split mid-sentence unless absolutely necessary) of roughly uniform size (better retrieval ranking than wildly variable chunk lengths).

## 2.3 Overlap for context continuity

`settings.AUDIO_CHUNK_OVERLAP_WORDS = 50` — the last 50 words of chunk N are repeated as the first 50 words of chunk N+1. Same rationale as Chapter 6's document overlap: a fact mentioned once, right at a chunk boundary, appears in two chunks' context rather than being unretrievable if it's on the "wrong" side of the split.

## 2.4 Splitting mid-segment when necessary

If a single Whisper segment contains 400 words and the current buffer already has 250 words, adding the entire segment would overshoot the 300-word target by 350 words. The chunker splits the segment at the 50-word mark (using word-level timestamps to determine the split time), emits the first 50 words in the current chunk, and carries the remaining 350 words into the next chunk's buffer. This is `_split_segment()` in `src/pipelines/audio/ingestion.py` — the exact logic that makes "target 300 words" a real target, not just an average.

---

# Part 3 — LEARN: Why Audio Goes Into text_index

## 3.1 ADR-005: transcription over native audio embeddings

CLAP (Contrastive Language-Audio Pretraining) is an audio counterpart to OpenCLIP — it embeds audio clips and text into a shared space, enabling text-to-audio search without transcription. ADR-005 rejected it for two reasons:

1. **Transcripts are more useful than audio clips for LLM context.** Chapter 10's RAG prompt needs *text* to stuff into the context window, not an audio file. CLAP would require transcription *anyway* to produce readable citations.
2. **Transcripts are searchable by the same text embedding model as documents.** MiniLM (Chapter 7) embeds transcript text, so a text query retrieves documents and audio together, naturally — no separate collection, no modality-gap merge complexity beyond what Chapter 8's `image_index` already introduced.

## 3.2 Embedding transcripts with MiniLM

```python
from src.core.embeddings import embed_texts

chunks = [...]  # audio chunks with .text = transcript
embeddings = embed_texts([c.text for c in chunks])
```

The same `embed_texts()` function Chapter 7 built for documents. Audio transcripts are just text — the same 384-d MiniLM vectors, the same cosine similarity scoring, the same `text_index` collection.

## 3.3 Timestamp-based citations

A document chunk cites `(source, page)` — e.g., `data/documents/notice.pdf, page 2`. An audio chunk cites `(source, start_s, end_s)` — e.g., `data/audio/talk.wav, 12s–20s`. Chapter 10's `format_provenance()` already handles both modalities:

```python
if chunk.modality == "audio":
    return f"{chunk.source}, {int(chunk.start_s)}s–{int(chunk.end_s)}s"
else:
    return f"{chunk.source}, page {chunk.page}"
```

The user sees "listen starting at 12 seconds" — a directly actionable citation, same principle as "page 2."

---

# Part 4 — DECIDE

## 4.1 Module layout

```
src/pipelines/audio/
├── __init__.py
├── ingestion.py       ← AudioIngestor: transcribe + chunk + timestamp
├── transcribe.py      ← transcribe_query(): turn a user's voice query into text
├── index.py           ← index_audio_file(), index_audio_directory()
```

Kept under `pipelines/audio/` (not `core/`) for the same reason images are under `pipelines/images/` — this is Track C's domain code. Only the ChromaDB write primitive (`add_chunks()`) and text embedding (`embed_texts()`) are shared with other tracks.

## 4.2 Binding to `settings.TEXT_EMBEDDING_MODEL`

`AudioIngestor` stores `settings.TEXT_EMBEDDING_MODEL` (or `settings.DEFAULT_TEXT_EMBEDDING_MODEL`, fallback) in every chunk's `embedding_model` field — the same centralized config binding Chapter 8 established for CLIP. One source of truth: changing the embedding model in `.env` changes it for documents, audio, and any future text-based modality.

## 4.3 Target chunk size — 300 words, matching documents

`AUDIO_CHUNK_TARGET_WORDS = 300` matches `CHUNK_SIZE_WORDS = 300` (Chapter 6). Same reasoning: too small (e.g., 50 words) and retrieval is noisy (many short, low-context chunks per query); too large (e.g., 1000 words) and retrieval is coarse (one question about a 2-second fact retrieves 5 minutes of transcript). 300 is the starting point Chapter 6 already justified — revisit if audio-specific evaluation (gold questions about spoken content) shows a different optimum.

## 4.4 Retry strategy with exponential backoff

`AudioIngestor._transcribe_with_retry()` wraps `model.transcribe()` in a 3-attempt loop with exponential backoff (1s, 2s, 4s). Whisper transcription on CPU can occasionally timeout or fail on specific audio formats — retrying with a brief delay succeeds more often than raising immediately. Logged clearly (attempt X/3 failed, retrying in Ns) so transient failures are visible, not silent.

---

# Part 5 — BUILD: the actual Day 10

## 5.1 Write `src/pipelines/audio/ingestion.py`

`AudioIngestor.process_file()` — see Parts 1–2. The full sliding-window chunking logic: buffering segments, counting words, splitting mid-segment when necessary, trimming overlap, building `Chunk` objects with timestamps.

Key details:
- `_validate_file()`: checks file exists, extension is supported (`.mp3`, `.wav`, `.m4a`, etc.), size ≤ 2GB
- `_transcribe_with_retry()`: 3 attempts with backoff
- `_create_chunks_from_segments()`: the sliding-window implementation
- `_build_chunk()`: constructs a `Chunk` with `modality="audio"`, `start_s=`, `end_s=`, `embedding_model=settings.TEXT_EMBEDDING_MODEL`

## 5.2 Write `src/pipelines/audio/transcribe.py`

`transcribe_query()` — a thin wrapper over `model.transcribe()` for Chapter 11's voice-query feature (a user records a question instead of typing it). Joins Whisper segments into a single string, stripping silence and empty segments.

## 5.3 Write `src/pipelines/audio/index.py`

`index_audio_file()` — see Part 3.2. Calls `AudioIngestor.process_file()`, validates every chunk with `validate_chunk()` (Chapter 5's contract), normalizes whitespace with `normalize_text()`, embeds with `embed_texts()`, and writes to `text_index` via `add_chunks()`.

## 5.4 Test the pipeline with real audio

```bash
python -c "
from pathlib import Path
from src.pipelines.audio.index import index_audio_file
from src.pipelines.documents.search import search_text
from src.core.vector_store import get_client

# Create test audio (requires ffmpeg or a real .mp3 file)
# For this example, assume 'data/audio/sample.mp3' exists

client = get_client()
count = index_audio_file('data/audio/sample.mp3', client=client)
print(f'Indexed {count} chunks from audio')

# Search
results = search_text('what is the deadline', client=client, top_k=3)
for r in results:
    if r.modality == 'audio':
        print(f'{r.source}, {int(r.start_s)}s–{int(r.end_s)}s: {r.text[:60]}...')
"
```

**Expected output:**
```
Indexed 4 chunks from audio
data/audio/sample.mp3, 12s–34s: The project deadline is March 15th. Make sure to submit...
```

Audio chunks are searchable alongside documents, using the same text query.

## 5.5 Run `tests/test_audio_pipeline.py`

Extracted from `test_integration.py` (Part 5 of the original file, lines 305–368):

```bash
pytest tests/test_audio_pipeline.py -v
```

**Real captured output:**
```
tests/test_audio_pipeline.py::test_audio_is_indexed_into_text_index PASSED
tests/test_audio_pipeline.py::test_audio_chunks_have_timestamps PASSED
tests/test_audio_pipeline.py::test_audio_chunks_validate_against_contract PASSED
tests/test_audio_pipeline.py::test_transcribe_query_joins_segments PASSED
======================== 4 passed in 8.21s =========================
```

## 5.6 Git hygiene for today

- [ ] `src/pipelines/audio/{ingestion,transcribe,index}.py` committed
- [ ] `tests/test_audio_pipeline.py` committed; audio tests removed from `test_integration.py`
- [ ] `docs/chapters/ch09-audio-pipeline-whisper-transcription.md` committed
- [ ] Every team member has confirmed `pytest tests/test_audio_pipeline.py` passes

---

# Part 6 — CHECK

## 6.1 Rubric

| # | Criterion | Score |
|---|---|---|
| 1 | `AudioIngestor.process_file()` transcribes real audio into chunks with timestamps | /3 |
| 2 | Audio chunks have `embedding_model = settings.TEXT_EMBEDDING_MODEL` | /3 |
| 3 | `index_audio_file()` writes audio chunks into `text_index` (not a separate collection) | /3 |
| 4 | `search_text()` retrieves audio chunks alongside document chunks for the same query | /3 |
| 5 | `pytest tests/test_audio_pipeline.py -v` fully passes | /3 |
| 6 | Audio chunks cite `(source, start_s, end_s)` instead of `(source, page)` | /3 |
| 7 | Team can explain why audio goes into `text_index`, not a third collection | /3 |
| 8 | Team can explain why VAD (`vad_filter=True`) matters for chunking | /3 |
| 9 | Team can explain why chunk size is measured in words, not seconds | /3 |
| 10 | Team can explain the retry-with-backoff strategy | /3 |
| | **Total** | **/30** |

## 6.2 Question bank

1. Why use `faster-whisper` instead of OpenAI's original Whisper? → §1.1; 4x faster on CPU via CTranslate2 quantization, same accuracy.
2. What does `vad_filter=True` do, and why does it matter? → §1.2; enables voice activity detection, skips silence and background noise, prevents empty/hallucinated chunks.
3. Why chunk audio at all instead of embedding the entire transcript? → §2.1; a 10-minute transcript in one chunk loses granularity — every query retrieves the whole thing, burying the relevant sentence.
4. Why is chunk size measured in words (300) instead of seconds (e.g., 30s)? → §2.2; spoken word rate varies — 30s of fast speech could be 150 words, 30s of slow speech 75 words. Word count is more uniform.
5. What does `AUDIO_CHUNK_OVERLAP_WORDS = 50` prevent? → §2.3; a fact mentioned once at a chunk boundary wouldn't be retrievable if it's split across two chunks with no overlap.
6. What is `_split_segment()` and why does it exist? → §2.4; splits a long Whisper segment mid-way (at a word boundary) so the target 300-word chunk size is a real target, not just an average.
7. Why did ADR-005 choose transcription over CLAP (native audio embeddings)? → §3.1; LLMs need text for context (not audio clips), and transcripts are searchable by the same MiniLM model as documents.
8. How are audio transcripts embedded? → §3.2; the same `embed_texts()` / MiniLM model as documents — they're just text with timestamps.
9. What's the citation format for an audio chunk? → §3.3; `data/audio/talk.wav, 12s–20s` (source + timestamp range, not page number).
10. Why does `AudioIngestor._transcribe_with_retry()` exist? → §4.4; Whisper on CPU occasionally times out on specific audio formats; retrying with exponential backoff succeeds more often than raising immediately.

## 6.3 Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'faster_whisper'` | `faster-whisper` not installed | `pip install -r requirements.txt` |
| Transcription is very slow (>1 minute for a 2-minute audio file) | Using a large model (`large-v2`) or `device="cpu"` with no optimization | Confirm `WhisperModel("base", device="cpu", compute_type="int8")` — `base` is the default, `large` is much slower |
| Empty audio chunks (no text) even though the audio has speech | VAD too aggressive, or audio quality too poor | Try `vad_filter=False` temporarily to confirm; if that works, adjust `vad_parameters` (lower `min_silence_duration_ms`) |
| Audio chunks have `embedding_model=None`, contract validation fails | `AudioIngestor` not reading `settings.TEXT_EMBEDDING_MODEL` | Confirm `ingestion.py` line ~362: `emb_model = getattr(settings, "DEFAULT_TEXT_EMBEDDING_MODEL", ...)` |
| Whisper detects the wrong language | Audio has background music or heavy accents | Check `info.language` and `info.language_probability` — if probability <0.8, the audio may be unclear. Pre-process to remove background noise, or force language: `model.transcribe(..., language="en")` |
| `FileNotFoundError` when indexing audio files | Audio file path incorrect or not in a supported format | Confirm path exists and extension is in `SUPPORTED_EXTENSIONS` (`.mp3`, `.wav`, `.m4a`, etc.) |

## 6.4 Day 10 completion checklist

- [ ] `faster-whisper` installed and `AudioIngestor.process_file()` transcribes real audio
- [ ] At least 1 audio file indexed into `text_index`, timestamps confirmed in citations
- [ ] `search_text()` retrieves audio chunks alongside document chunks
- [ ] `pytest tests/test_audio_pipeline.py -v` fully passes
- [ ] Team can explain why audio transcripts go into `text_index`, not a separate collection
- [ ] Team can explain the sliding-window chunking logic
- [ ] Rubric §6.1 scored ≥ 24/30

---

**Next:** Chapter 10 (already completed) — RAG Core: Retrieval + Generation, where the three modalities (documents, images, audio) are merged at query time, ranked by RRF (ADR-007), and passed to the LLM for grounded, cited answers.
