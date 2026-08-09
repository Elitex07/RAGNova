# Chapter 1 — Objective & Problem Identification (Day 1)

> **Goal of this chapter:** by the end, every team member can explain — in their own words, to a professor — *what* we are building, *why* it matters, *what exactly the problem is*, and *what we are NOT building*. This chapter produces the Day 1 deliverable and feeds directly into the Day 2 synopsis.

---

## Part 1 — LEARN: Understanding the problem statement, word by word

Our problem statement:

> *"Design and build a multimodal Retrieval-Augmented Generation (RAG) system leveraging a LLM for OFFLINE mode that can ingest, index, and query diverse data formats such as DOC, PDF, Images, and Voice recordings within a unified semantic retrieval framework."*

That is a dense sentence. Let's decompress every term.

### 1.1 What is an LLM?

A **Large Language Model** is a neural network trained on huge amounts of text to predict the next word. That simple objective, at scale, produces a system that can answer questions, summarize, and reason in natural language. ChatGPT, Gemini, and Llama are LLMs.

Two ways to use an LLM:
- **Cloud API** — send your text to a company's server (OpenAI, Google). Powerful, but needs internet, costs money, and your data leaves your machine.
- **Local / offline** — download the model's weights (the learned numbers) and run it on your own computer. Free, private, works with no internet. Smaller models (1B–8B parameters) now run fine on a laptop CPU. **Our project is this one.**

### 1.2 What problem do LLMs have that RAG solves?

An LLM alone has three critical weaknesses:

1. **It doesn't know YOUR data.** Llama was trained on the public internet — it has never seen your lecture notes, your lab reports, your screenshots.
2. **It hallucinates.** When an LLM doesn't know something, it often confidently makes up a plausible-sounding answer. For serious use, that's disqualifying.
3. **Its knowledge is frozen.** Whatever the model learned at training time is all it knows. It can't learn your new files without expensive retraining.

### 1.3 What is RAG (Retrieval-Augmented Generation)?

RAG fixes all three weaknesses with one trick: **before asking the LLM, first go fetch the relevant passages from the user's own files, and paste them into the prompt.**

```
Without RAG:
  User: "What deadline did the professor mention?"
  LLM:  (guesses / hallucinates — it never saw the notice)

With RAG:
  User: "What deadline did the professor mention?"
  Step 1 (RETRIEVE): search user's files → find notice.pdf, page 2:
                     "...submission deadline is 21st August..."
  Step 2 (AUGMENT):  build a prompt: "Using ONLY the context below,
                     answer the question. Context: [page 2 text]..."
  Step 3 (GENERATE): LLM answers: "The deadline is 21st August [1]."
                     — grounded, citable, no hallucination.
```

So: **R**etrieve relevant chunks → **A**ugment the prompt with them → **G**enerate the answer. That's the entire idea. Everything else in this project is engineering around making Retrieve work really well across file types.

### 1.4 What does "semantic" search mean?

Classic search (Ctrl+F, SQL `LIKE`) matches **keywords**. Search "car" — you miss the document that says "automobile."

**Semantic search matches meaning.** It works via **embeddings**: a neural network converts any text into a list of numbers (a *vector*, e.g. 384 numbers) such that **texts with similar meaning get vectors that are close together** in that number space. "car" and "automobile" land near each other; "car" and "banana" land far apart.

Search then becomes geometry: embed the query, embed all documents, return the documents whose vectors are **nearest** to the query's vector (measured by cosine similarity — the angle between vectors).

A **vector database** (we'll use ChromaDB) is simply a database optimized to store millions of vectors and answer "which stored vectors are nearest to this one?" fast.

### 1.5 What does "multimodal" mean?

A **modality** is a type of data: text, images, audio, video. A *multimodal* system handles several. Ours handles:

| Modality | Example inputs | How we make it searchable |
|---|---|---|
| Text | DOCX, PDF | Extract text → chunk → embed |
| Images | screenshots, photos | CLIP embedding (+ OCR for text inside the image) |
| Audio | voice memos, recordings | Whisper transcription → text → chunk → embed |

### 1.6 The hard part: CROSS-modal search

Multimodal ingestion is easy — the interesting requirement is **cross-modal search**: a *text* query must find *images*; an *image* query must find *documents*.

Problem: a text embedding model and an image classifier normally live in completely different vector spaces — their numbers aren't comparable.

Solution: **CLIP** (Contrastive Language-Image Pretraining, OpenAI 2021). CLIP was trained on 400 million (image, caption) pairs with one objective: *push the image's vector and its caption's vector close together*. Result: **one shared vector space for both text and images.** Embed the text "email screenshot," embed all your images, and the actual email screenshots are literally the nearest vectors. Cross-modal search becomes the same nearest-neighbor lookup as before.

Audio joins the family through a bridge: Whisper converts speech to text, and text is already searchable. (Spoken query → transcript → treat as a text query.)

### 1.7 Why OFFLINE? (This is a feature, not a limitation)

The problem statement insists on offline mode. Reasons this matters in the real world:

1. **Privacy / confidentiality** — medical records, legal files, defense documents can't be sent to a cloud API.
2. **No recurring cost** — cloud LLM APIs charge per token; offline is free after setup.
3. **Works anywhere** — rural areas, air-gapped labs, flights, exam halls without connectivity.
4. **Data sovereignty** — organizations legally required to keep data in-house.

Design consequence: every model we use must be downloadable and runnable on consumer hardware. This rules out GPT-4-class models and forces smart choices about *small* models — which is exactly the engineering skill this project teaches.

---

## Part 2 — DECIDE: Problem identification (the formal exercise)

"Problem identification" in a project report means answering four questions precisely. Here are ours — discuss as a team, edit wording to taste, then this section goes almost verbatim into the synopsis.

### 2.1 The problem (what's broken today?)

> Individuals and organizations accumulate knowledge scattered across heterogeneous formats — documents, images, and voice recordings. Existing search tools are (a) **keyword-based**, missing semantically relevant results; (b) **siloed by modality**, unable to find an image from a text description or a document from an audio clip; and (c) **cloud-dependent**, raising privacy, cost, and connectivity barriers. There is no unified, offline system that lets a user ask a natural-language question and receive a cited answer drawn from all their files regardless of format.

### 2.2 Objectives (measurable — a report needs these numbered)

1. **O1 — Ingestion:** Build pipelines to ingest and index DOCX, PDF, image (PNG/JPG), and audio (WAV/MP3) files into a unified vector store.
2. **O2 — Semantic search:** Enable natural-language querying with meaning-based (not keyword) retrieval over all indexed content.
3. **O3 — Cross-modal retrieval:** Support text→image, image→text/docs, and audio→all retrieval within one framework.
4. **O4 — Grounded generation:** Generate answers using a locally-running LLM, constrained to retrieved context, with numbered citations `[1][2]` linking to sources.
5. **O5 — Unified interface:** Provide a single chat interface accepting typed text, uploaded files, drag-and-drop images, attached audio, and spoken queries.
6. **O6 — Fully offline:** All components (embedding models, LLM, ASR, database) run on a local machine with zero internet calls at query time.

### 2.3 Scope — and equally important, NON-scope

Beginner teams die from scope creep. We write down what we're NOT doing:

**In scope:** the six objectives above, demo corpus of ~50–200 files, single-user local app, English content.

**Out of scope (say this proudly in the viva):**
- Video ingestion (extension idea, mention in "future work")
- Multi-user server deployment / authentication
- Fine-tuning any model (we only use pretrained models)
- Real-time streaming transcription
- Handwriting recognition
- Non-English content (Whisper/CLIP partially support it — bonus if it works, not promised)

### 2.4 Users & use cases (who is this for?)

| User | Scenario |
|---|---|
| Student | "Where in my recorded lectures did the professor explain backpropagation?" — audio→answer with timestamp |
| Researcher | Drops 40 papers in, asks synthesized questions with citations |
| Professional | "Find the screenshot of the invoice email" — text→image |
| Privacy-critical org | All of the above with zero data leaving the machine |

---

## Part 3 — BUILD: Day 1 deliverables checklist

- [ ] Every member reads this chapter fully.
- [ ] Team meeting (30 min): each member explains RAG to the others in their own words — teaching is the test of understanding.
- [ ] Agree on final wording of problem statement (2.1) and objectives (2.2). Edit this file directly.
- [ ] Collect a starter demo corpus into `data/`: ~10 PDFs, ~5 DOCX, ~10 images (include 2–3 screenshots), 2–3 voice memos (record 30-second clips on your phones).
- [ ] Optional but recommended: install [Ollama](https://ollama.com/download) tonight — Chapter 5 needs it and the model download is large (~2 GB); better on hostel wifi overnight.

## Part 4 — CHECK: Self-test (viva practice)

Answer without looking (then verify above):

1. What three weaknesses of a plain LLM does RAG fix?
2. What is an embedding, in one sentence?
3. Why can't we use a normal text embedding model to search images with text? What model solves this, and how was it trained?
4. How does audio become searchable in our system?
5. Give two real-world reasons offline mode matters.
6. Name three things explicitly OUT of scope.

---

**Next chapter:** [Chapter 2 — Synopsis & Presentation](ch02-synopsis-and-presentation.md) (Day 2) — we compress this chapter into a 2–3 page synopsis and a PPT, with a template and slide-by-slide guidance.
