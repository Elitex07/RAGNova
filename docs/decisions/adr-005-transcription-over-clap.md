# ADR-005: Transcribe audio with Whisper rather than embed it natively with CLAP

## Status
Accepted — Day 4

## Context

Audio files (voice recordings, per the problem statement) must become searchable and
citable. Two architectural routes exist, and Track B (Chapter 4 §4.1) needs this decided
before its two chapters (Ch8 image, Ch9 audio) are written, since it determines what the
`text` field of an audio chunk actually contains (Ch4 §4.2's schema requirements).

Two hard requirements from Chapter 1 bound the choice:

- **Objective O4 requires citations to resolve to a specific location** — for audio, a
  timestamp a user can seek to and a transcript segment they can read (Ch1 §1.8).
- The corpus in scope is **spoken content** — voice memos, lecture recordings, meeting
  audio (Ch1 §1.7.5) — not environmental sound or music.

## Decision

Transcribe all audio with faster-whisper, then treat the resulting timestamped text exactly
like any other text chunk, indexed into `text_index` (ADR-004) alongside document text.

## Alternatives considered

1. **Native audio embeddings via CLAP** (Contrastive Language-Audio Pretraining). Rejected:
   CLAP is trained to match audio to descriptive captions of *sound events* — "a dog
   barking," "glass breaking," "jazz piano" — and its contrastive objective optimises for
   acoustic character, not linguistic content [CLAP]. Our corpus is speech, where the
   information that matters is *what was said*, not what the recording sounds like. A CLAP
   embedding of a lecture recording captures "a person's voice speaking," which is close
   to useless for retrieving *which* lecture discussed a given topic.
2. **CLAP as a supplementary signal alongside transcription** (index both). Rejected for
   this project's scope: it would require a third embedding model loaded at query time
   (on top of the LLM, the text embedder, and CLIP — Ch1 §1.9.2's RAM budget is already
   tight), for a capability (searching audio by *how it sounds* rather than *what was said*)
   that is out of scope per the problem statement's focus on voice recordings, not general
   audio or sound-effect libraries.
3. **A dedicated audio-only vector collection**, populated with either CLAP embeddings or a
   custom acoustic feature extractor. Rejected on the same grounds as option 1 — it solves
   a search problem (find audio by acoustic similarity) the project does not actually have.

## Consequences

**Positive**
+ Reuses the entire text pipeline (chunking, embedding, storage, retrieval) built for
  documents — no separate audio-search code path.
+ Whisper's segment-level timestamps map directly onto the citation requirement (Ch1 §1.8)
  and the schema's `start_s`/`end_s` fields (Ch4 §4.3).
+ Produces a human-readable transcript displayed beside every audio citation, letting a
  user verify the system's answer directly — unlike an opaque embedding vector.
+ The same Whisper model, run in the same direction, also transcribes **spoken queries**
  (Ch1 §1.7.5) — one model serves two features.

**Negative**
− Transcription errors propagate directly into retrieval and generation; a mistranscribed
  word is simply absent from the searchable text. Whisper's word error rate (Ch1 §1.10,
  target < 15% on test clips) becomes a real quality ceiling for the audio pipeline.
− Whisper is known to occasionally hallucinate text during silence or background noise
  [Whisper] — a risk specific to this pipeline that must be disclosed in the report's
  limitations, since a hallucinated transcript segment becomes a retrievable false chunk.
− Cannot retrieve audio by acoustic content (a specific sound effect, a musical style) —
  explicitly out of scope, per the alternatives above, but worth stating plainly.

**Implications for other components**
- Fixes what Track B's `ingest_audio()` function must return: a list of text chunks with
  `start_s`/`end_s` populated and `page` absent (Ch4 §4.3's strawman schema).
- Audio chunks are indistinguishable from document chunks to Track A's retrieval code
  except via the `modality` field — retrieval logic does not need a separate audio path.

## Revisit if

The project scope is extended to include non-speech audio (music, sound effects,
environmental recordings), at which point a CLAP-based supplementary index would become the
right tool for that specific, different search problem.

---

*Citations: [CLAP] Elizalde, Deshmukh, Al Ismail and Wang, "CLAP: Learning Audio Concepts
from Natural Language Supervision," ICASSP 2023. [Whisper] Radford, Kim, Xu, Brockman,
McLeavey and Sutskever, "Robust Speech Recognition via Large-Scale Weak Supervision," ICML
2023. **Verify both before use.***
