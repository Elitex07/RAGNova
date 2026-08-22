# Presentation #1 — Slide Plan (Day 2)

> **How to use this.** Each slide below gives a **headline** (type it verbatim onto the slide — every headline is a full assertion, not a topic label), **on-slide content** (the minimum that goes on screen), and **speaker notes** (what you say aloud — never put this on the slide).
>
> The design principles behind these choices are in [Chapter 2 §1.7–1.8](../docs/chapters/ch02-synopsis-and-presentation.md). The short version: **the slide carries the claim and the evidence; your voice carries the explanation.** People cannot read and listen at once — a slide full of prose means your audience reads badly while hearing nothing.
>
> **Rehearse the speaker notes out loud, standing.** Do not read them during the talk; writing them is how you find out whether you actually understand the slide.
>
> **Target: 12 slides, 10 minutes.** If your slot is shorter, cut slides 6 and 10 first — they are the most compressible.

---

## Global settings

| Setting | Value |
|---|---|
| Font | Calibri or Arial (sans-serif) |
| Title size | ≥ 32 pt |
| Body size | ≥ 24 pt |
| Contrast | Dark text on light background, or the reverse — never mid-tones |
| Slide numbers | On, bottom-right |
| Animations / transitions | None |
| Export | `.pptx` **and** `.pdf`, on a pen drive **and** in cloud storage |

---

## Slide 1 — Title

**On slide**
> **RAGNova**
> An Offline Multimodal RAG System for Unified Semantic Retrieval Across Documents, Images, and Speech
>
> ⟨Member 1⟩ · ⟨Member 2⟩ · ⟨Member 3⟩
> B.Tech CSE (AI & ML) · ⟨Department⟩ · ⟨Institution⟩
> Guide: ⟨Name⟩ · ⟨Date⟩

**Speaker notes (Member 1, ~20 s)**
> Good morning. We are presenting RAGNova, an offline multimodal retrieval-augmented generation system. In short: it lets you ask a question in plain language and get an answer drawn from your own documents, images, and voice recordings — with citations, and without any internet connection.

---

## Slide 2 — The problem is real and specific

**Headline:** `Your files hold the answer — but you cannot find it`

**On slide** — three icons or short lines, nothing more:
- 📄 Documents · 🖼️ Screenshots · 🎙️ Recordings — *semantically related, technically fragmented*
- Search is **lexical** — "car" misses "automobile"
- Search is **modality-siloed** — no way to search a photo or a recording
- Semantic tools are **cloud-only** — private data leaves your machine

**Speaker notes (Member 1, ~60 s)**
> Consider a student before an exam. The syllabus is a PDF, the deadline is in a screenshot of an email, and the professor's explanation is in a lecture recording. All three relate to the same topic — but three separate tools are needed, and none of them searches by meaning.
>
> Three specific failures. First, existing search is lexical: it matches characters, so a query for "car" misses a document that says "automobile". Second, it is siloed by modality — images are findable only by filename, and speech is not searchable at all without manual transcription. Third, the tools that *do* understand meaning are cloud services, which means confidential material leaves your machine, you pay per query, and nothing works without connectivity.

---

## Slide 3 — What we are building

**Headline:** `One question box over every file you own, working offline`

**On slide** — four capability lines:
- **Ask** in plain language — typed or spoken
- **Search** by meaning across PDF, DOCX, images, audio
- **Cross-modal** — text finds images; an image finds documents
- **Cited** — every claim links to file, page, or timestamp
- **Offline** — every model runs locally

**Speaker notes (Member 2, ~50 s)**
> Our system provides one interface over all of it. You type or speak a question, or drop in an image, and it searches everything you have indexed — documents, screenshots, recordings — by meaning rather than keyword.
>
> The part we find most interesting is cross-modal search: type "email screenshot" and it returns the actual image, with no tags or captions ever having been written. Upload a screenshot and it finds the documents that discuss it.
>
> Every answer carries numbered citations. Click one and you see the source document and page, or the transcript segment with its timestamp. And all of it runs on a laptop with no internet connection.

---

## Slide 4 — Objectives

**Headline:** `Seven objectives, each independently verifiable`

**On slide** — compress to six lines maximum:
1. Ingest and index PDF, DOCX, images, audio
2. Semantic retrieval — Recall@5 ≥ 0.80
3. Cross-modal retrieval, three directions — Recall@5 ≥ 0.70
4. Grounded generation with numbered citations — faithfulness ≥ 4/5
5. Unified interface: text, file, image, audio, microphone
6. Fully offline, verified by disconnected-network test

**Speaker notes (Member 1, ~50 s)**
> Seven objectives, and we have deliberately attached a number to each one that can be checked. Recall@5 of 0.80 means the correct passage appears in the top five results for at least eighty percent of our test questions. Faithfulness of four out of five is a human rating of whether each claim in an answer is genuinely supported by the source it cites.
>
> We wrote the test questions before writing any code, so we cannot tune the system to flatter itself. The offline claim is verified simply: we disconnect the network entirely and run the full workflow.

---

## Slide 5 — Architecture

**Headline:** `Four ingestion pipelines converge on one vector store`

**On slide:** **Figure 1 only.** No bullets. The diagram from Chapter 2 §3.3, filling the slide.

**Speaker notes (Member 2, ~90 s — the longest slide, take your time)**
> This is the whole system. There are two phases.
>
> Indexing, on the left, runs once per file. PDFs and Word documents are parsed to text and split into roughly three-hundred-word overlapping chunks. Audio goes through Whisper, which produces a transcript with timestamps, and those transcripts are chunked the same way. Images take two paths at once: a CLIP vision model produces a semantic embedding of what the image *depicts*, and OCR extracts any literal text inside it, such as an invoice number.
>
> Everything converges on the vector store, where each chunk is stored alongside its provenance — which file, which page, which timestamp. That metadata is what makes citation possible later; it is not something we add at the end.
>
> Querying, on the right, runs per question. The query is embedded, the nearest chunks are retrieved, and those chunks — numbered — are given to a language model running locally, with instructions to answer only from that evidence and to cite it. The answer comes back with bracketed numbers that expand to the original source.

---

## Slide 6 — How meaning becomes searchable

**Headline:** `Embeddings turn meaning into geometry, so similar text sits nearby`

**On slide** — a simple 2D scatter sketch: "cat" and "kitten" close together, "database" far away. Plus one line:
> *Similarity = the angle between two vectors*

**Speaker notes (Member 3, ~45 s)**
> A quick word on the mechanism, because everything else depends on it. An embedding model converts a piece of text into a list of numbers — a vector — such that text with similar meaning produces vectors pointing in similar directions.
>
> So "cat" and "kitten" land close together, while "database" lands far away, even though none of those words share characters. Search then becomes geometry: we embed the question, and return the stored chunks whose vectors point in the most similar direction. That is why this finds paraphrases that keyword search misses entirely.

*(This is the first slide to cut if you are short on time.)*

---

## Slide 7 — Cross-modal search

**Headline:** `CLIP places images and text in one shared space, so text can retrieve images`

**On slide** — the second figure: query text on the left → shared vector space in the middle → retrieved image on the right.

**Speaker notes (Member 2, ~60 s)**
> This is the piece that makes the system genuinely multimodal rather than just multi-format.
>
> Normally a text model and an image model produce vectors in unrelated coordinate systems — comparing them is meaningless. CLIP solves this by training both encoders together on four hundred million image-caption pairs, with a single objective: push each image and its true caption close together in one shared space.
>
> The consequence is that after training, the vector for a photograph of a dog sits near the vector for the words "a photo of a dog". So we can type "email screenshot", embed those words, and find the actual screenshots — without anyone ever having tagged or captioned them.

---

## Slide 8 — Grounding and citations

**Headline:** `Constraining the model to retrieved evidence is what makes citation possible`

**On slide** — a compact before/after:

| Without retrieval | With retrieval |
|---|---|
| Model answers from memory | Model answers from your files |
| Cannot cite — knowledge is in the weights | Cites file, page, timestamp |
| Invents plausible detail | States when evidence is absent |

**Speaker notes (Member 3, ~55 s)**
> Language models hallucinate — they produce fluent, confident, wrong answers. This is structural, not a bug: the model must always emit something, its memory is a lossy compression of its training data, and it has never seen your files at all.
>
> Retrieval fixes all three. We fetch the relevant passages first and instruct the model to answer only from them, and to say so when they do not contain the answer. Because each passage carries its origin, the answer can point back at page two of a specific PDF.
>
> We should be precise: this reduces hallucination substantially, it does not eliminate it. That is why we validate every citation the model emits, and display the retrieved text next to it so a human can verify in one glance.

---

## Slide 9 — Technology stack

**Headline:** `Every component runs locally on commodity hardware`

**On slide** — compact table, five or six rows maximum:

| Layer | Tool | Size |
|---|---|---|
| Local LLM | Ollama · Llama 3.2 3B (4-bit) | ~2 GB |
| Text embeddings | all-MiniLM-L6-v2 | ~90 MB |
| Image + text space | OpenCLIP ViT-B/32 | ~600 MB |
| Speech | faster-whisper | ~150 MB |
| Vector store | ChromaDB | embedded |
| Interface | Streamlit | — |

**Speaker notes (Member 2, ~45 s)**
> All open-source, all local. The point worth drawing out is the language model size. A three-billion-parameter model at full precision needs about six gigabytes of memory. Quantized to four bits it needs about two, which fits comfortably on a normal laptop with no graphics card.
>
> That is what makes the offline requirement achievable rather than aspirational — and it works because retrieval changes the model's job. It no longer has to *know* things; it only has to read a paragraph we hand it and answer from it. A small model does that well.

---

## Slide 10 — Scope

**Headline:** `Bounded deliberately: four formats, one user, English, 200 files`

**On slide** — two columns:

| In scope | Out of scope |
|---|---|
| PDF, DOCX, PNG/JPG, WAV/MP3 | Video — deferred to future work |
| Three cross-modal directions | Multi-user deployment |
| 50–200 file corpus | Any model training or fine-tuning |
| Single-user desktop, English | Handwriting recognition |

**Speaker notes (Member 3, ~35 s)**
> We have bounded this deliberately. Video is excluded because it requires keyframe extraction on top of everything else, and we would rather deliver four modalities properly than five partially. We train no models — every model is pretrained and downloaded, which is what makes the timeline realistic. Handwriting needs different models than printed-text OCR, so it is out.

*(Cut this slide second if short on time — but keep the exclusions in the synopsis regardless.)*

---

## Slide 11 — Timeline and team

**Headline:** `Three parallel tracks, decoupled by a shared schema, integrating on Day 12`

**On slide** — compact Gantt-style bar chart or table:

| Days | Work | Owner |
|---|---|---|
| 1–4 | Ideation, synopsis, literature, planning | All |
| 5 | Environment setup, **shared schema frozen** | All |
| 6–7, 10–11 | Text pipeline + RAG core | ⟨Member 1⟩ |
| 8–10 | Vision + audio pipelines | ⟨Member 2⟩ |
| 11–12 | Interface and integration | ⟨Member 3⟩ |
| 12–13 | Testing and user feedback | All |
| 14 | Mid-term report | All |

**Speaker notes (Member 3, ~45 s)**
> Nine days for implementation, split into three tracks that can genuinely run in parallel.
>
> The thing that makes parallel work possible is on Day 5: we freeze a shared chunk schema — a single definition of what an indexed piece of content looks like — before anyone starts their pipeline. Each track then produces data in that shape, so the pieces fit when we integrate.
>
> We integrate on Day 12, not Day 13, deliberately. Leaving integration to the last day is how student projects fail, and we have listed it as a named risk.

---

## Slide 12 — Close

**Headline:** `An offline system that searches meaning across every format you own`

**On slide** — three lines only:
- Unified semantic retrieval across documents, images, and speech
- Cross-modal: text finds images, images find documents
- Cited, grounded answers — entirely offline

> **Thank you — questions?**

**Speaker notes (Member 1, ~25 s)**
> To summarise: one interface, four formats, searched by meaning; cross-modal retrieval so a text query can find an image; answers grounded in your own files with citations you can open; and all of it running with the network switched off.
>
> Thank you. We are happy to take questions.

---

## Q&A preparation

**All three members answer** — a panel notices when only one person can speak to the work, and reads it as the other two not having contributed. Agree in advance who leads on which area, and that anyone may add.

| Area | Lead | Backup |
|---|---|---|
| Problem, scope, motivation | ⟨Member 1⟩ | ⟨Member 3⟩ |
| Architecture, embeddings, CLIP | ⟨Member 2⟩ | ⟨Member 1⟩ |
| Evaluation, timeline, team split | ⟨Member 3⟩ | ⟨Member 2⟩ |

**Drill all twenty questions in [Chapter 2 §4.2](../docs/chapters/ch02-synopsis-and-presentation.md) before presenting.** Rotate who answers so nobody is caught out.

**If you do not know an answer**, say so and give your reasoning:

> ✅ *"We haven't tested that case yet. We plan to evaluate it during integration on Day 12, and I would expect the limitation to be X."*

Do not bluff. Panels detect it immediately, and it costs far more than the admission would.

---

## Pre-presentation checklist

- [ ] 12 slides or fewer; every headline is a full assertion, not a topic label
- [ ] No slide exceeds ~6 lines; body text ≥ 24 pt
- [ ] Figure 1 (architecture) and Figure 2 (cross-modal) inserted and readable from the back row
- [ ] Slide numbers on
- [ ] All `⟨FILL⟩` placeholders replaced
- [ ] Speaker notes written for every slide
- [ ] Rehearsed twice, out loud, standing, timed — finishing with a minute to spare
- [ ] Handover lines between members rehearsed
- [ ] All twenty Q&A questions drilled, every member able to answer any
- [ ] Exported as PDF **and** pptx; on a pen drive **and** in cloud storage
- [ ] Checked on a second machine, or at least in PDF, to confirm fonts and layout hold
