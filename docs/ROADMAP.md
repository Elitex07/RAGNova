# RAGNova — Roadmap: Chapters × 14-Day Timeline

This document is the master plan. It breaks the project into **13 chapters**, maps each to the official timeline, and defines how the team splits work.

---

## The big picture (read this first)

Building a multimodal RAG system sounds intimidating, but it decomposes into five simple questions:

1. **How do we get content out of files?** → *Ingestion* (parse PDFs, DOCX, run OCR on images, transcribe audio)
2. **How do we make content searchable by meaning, not keywords?** → *Embeddings + Vector Database*
3. **How do we search across different media types with one query?** → *Cross-modal embeddings (CLIP) + unified retrieval*
4. **How do we turn retrieved chunks into a cited answer?** → *Local LLM + prompt engineering + citation tracking*
5. **How does a human use it?** → *Chat UI with file upload, mic input, citation viewer*

Every chapter below serves one of these five questions.

```
 Files (PDF/DOCX/IMG/AUDIO)
        │  Chapter 6–9: Ingestion pipelines
        ▼
 Text chunks + image embeddings + transcripts
        │  Chapter 7: Embedding models
        ▼
 Vector Database (ChromaDB) ── stores meaning as numbers
        │  Chapter 10: Retrieval
        ▼
 Top-K relevant chunks ──► Local LLM (Ollama) ──► Answer + [1][2] citations
        │  Chapter 11: UI
        ▼
 Chat interface (Streamlit)
```

---

## Chapter list

### Phase A — Ideation & Planning (Days 1–4)

| Ch | Title | Day | Deliverable |
|----|-------|-----|-------------|
| 1 | Objective & Problem Identification | 1 | Problem statement analysis, objectives, scope document |
| 2 | Synopsis & Presentation | 2 | 2–3 page synopsis + PPT #1 |
| 3 | Literature Review & Methodology | 3 | Survey of existing systems + our chosen methodology |
| 4 | Timeline, Team & Modular Work Split | 4 | PPT #2, Gantt-style timeline, module ownership table |

### Phase B — Implementation (Days 5–13)

| Ch | Title | Days | What we build |
|----|-------|------|---------------|
| 5 | Environment Setup & Offline LLM | 5 | Python env, Ollama + local model running, project skeleton |
| 6 | Document Ingestion (PDF/DOCX) | 6 | Parsers, text extraction, chunking strategy |
| 7 | Embeddings & the Vector Database | 7 | sentence-transformers, ChromaDB, first semantic search |
| 8 | Image Pipeline (CLIP + OCR) | 8–9 | Text→image and image→text search |
| 9 | Audio Pipeline (Whisper) | 9–10 | Speech-to-text, transcript chunking with timestamps |
| 10 | RAG Core: Retrieval + Generation + Citations | 10–11 | The brain — query → retrieve → generate → cite |
| 11 | Unified Query Interface (UI) | 11–12 | Streamlit chat app: text/file/image/audio/mic input |
| 12 | Integration, Testing & Human Feedback | 12–13 | End-to-end tests, feedback forms, bug-fix cycle |

### Phase C — Reporting (Day 14)

| Ch | Title | Day | Deliverable |
|----|-------|-----|-------------|
| 13 | Mid-Term Report | 14 | Formal report: everything documented in Phases A–B |

---

## The offline tech stack (decided in Ch 3, justified there)

All tools below are **free, open-source, and run fully offline** after a one-time download:

| Layer | Tool | Why |
|---|---|---|
| Local LLM | **Ollama** running Llama 3.2 (3B) or similar | Easiest way to run an LLM offline; one command install |
| Text embeddings | **sentence-transformers** (`all-MiniLM-L6-v2`) | Small (80 MB), fast on CPU, excellent quality |
| Cross-modal embeddings | **OpenCLIP** | Maps text AND images into the *same* vector space → cross-modal search |
| Speech-to-text | **faster-whisper** | OpenAI Whisper, optimized; runs on CPU |
| Vector database | **ChromaDB** | Embedded (no server), Python-native, beginner-friendly |
| PDF parsing | **PyMuPDF** | Fast, handles messy PDFs |
| DOCX parsing | **python-docx** | Standard library for Word files |
| OCR (text in images) | **Tesseract** (via pytesseract) | Extracts text from screenshots |
| UI | **Streamlit** | Chat UI in pure Python — no HTML/JS needed |

> **Hardware reality check:** everything above runs on a laptop with 8 GB RAM (16 GB comfortable). No GPU required — CPU is enough for a demo-scale corpus.

---

## Team split (3 members — finalized in Chapter 4)

The architecture splits naturally into three parallel tracks that meet at the vector database:

| Track | Owner | Chapters | Modules |
|---|---|---|---|
| **A: Text pipeline + RAG core** | Member 1 | 6, 7, 10 | Doc parsing, chunking, text embeddings, retrieval, LLM, citations |
| **B: Vision + Audio pipelines** | Member 2 | 8, 9 | CLIP image search, OCR, Whisper transcription |
| **C: UI + Integration + Docs** | Member 3 | 11, 12 | Streamlit app, wiring pipelines together, testing, feedback collection |

Everyone does Chapters 1–5 and 13 **together** — shared foundation, shared report.

With 2 members: merge Track C into A and B (each owns half the UI).

**Interface contract:** tracks stay independent because everything talks through ChromaDB and one shared Python module (`src/core/schemas.py`) defining what a "chunk" looks like. Defined in Chapter 5.

---

## Human testing / feedback loops (built into the plan)

| When | What |
|---|---|
| End of Ch 7 | First demo to friends: "does semantic search feel better than Ctrl+F?" |
| End of Ch 10 | Answer-quality check: 10 test questions, humans rate answers 1–5 |
| Ch 12 | Structured feedback: 3–5 outside users try the app with a feedback form |
| Ongoing | `docs/feedback-log.md` — every piece of feedback recorded + what we changed |

---

## Progress tracker

- [ ] Ch 1 — Objective & Problem Identification
- [ ] Ch 2 — Synopsis & PPT
- [ ] Ch 3 — Literature Review & Methodology
- [ ] Ch 4 — Timeline & Team Split
- [ ] Ch 5 — Environment Setup & Offline LLM
- [ ] Ch 6 — Document Ingestion
- [ ] Ch 7 — Embeddings & Vector DB
- [ ] Ch 8 — Image Pipeline
- [ ] Ch 9 — Audio Pipeline
- [ ] Ch 10 — RAG Core
- [ ] Ch 11 — UI
- [ ] Ch 12 — Integration & Feedback
- [ ] Ch 13 — Mid-Term Report
