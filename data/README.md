# Demo Corpus & Gold-Standard Evaluation Set

This folder holds the files RAGNova will index, plus the test questions we use to *measure* whether retrieval works.

**Fill this file in on Day 1, before writing any code.** Writing the test set before the system is deliberate: it stops us from unconsciously tuning the system to flatter itself. See Chapter 1 §3.3 and §1.10.

---

## Folder layout

```
data/
├── documents/   PDFs and DOCX files
├── images/      PNG / JPG — include screenshots and photos containing text
└── audio/       WAV / MP3 clips, 30 s to 3 min
```

Target: 10–15 PDFs, 5–8 DOCX, 10–15 images (3+ screenshots, 3+ photos with visible text), 3–5 audio clips.

## Deliberate cross-modal test material

Make sure the corpus contains, on purpose:

- [ ] An image **and** a document about the same topic → proves image→document retrieval.
- [ ] An audio clip mentioning a topic that also appears in a PDF → proves audio→document retrieval.
- [ ] A screenshot whose content is described in a document → proves text→image retrieval with a visible payoff.

## File inventory

| File | Modality | What it contains | Notes |
|---|---|---|---|
| `documents/` | | | |
| `images/` | | | |
| `audio/` | | | |

---

## Gold-standard question set

The evaluation set from Chapter 1 §1.10. Start with 5 questions on Day 1; grow to **20 text questions + 10 cross-modal queries** by Chapter 7, when we first measure Recall@5 and MRR.

### Text → text/document queries

| # | Question | Expected source file | Expected page / timestamp | Why it's a good test |
|---|---|---|---|---|
| T1 | | | | |
| T2 | | | | |
| T3 | | | | |
| T4 | | | | |
| T5 | | | | |

> Include at least three questions whose wording shares **no keywords** with the source text (pure paraphrase). Those are the questions that prove semantic search beats Ctrl+F — and they are the ones to demo.

### Text → image queries (cross-modal)

| # | Query text | Expected image | Why it's a good test |
|---|---|---|---|
| I1 | | | |
| I2 | | | |
| I3 | | | |

### Image → document queries (cross-modal)

| # | Query image | Expected document(s) | Why it's a good test |
|---|---|---|---|
| M1 | | | |
| M2 | | | |

### Audio → anything queries

| # | Audio clip (or spoken query) | Expected result | Why it's a good test |
|---|---|---|---|
| A1 | | | |
| A2 | | | |

### Negative controls (should return "not found in the provided sources")

Questions the corpus genuinely cannot answer. These test whether the system **refuses to hallucinate** — objective O4.

| # | Question | Expected behaviour |
|---|---|---|
| N1 | | Refuses / states the sources don't cover it |
| N2 | | Refuses / states the sources don't cover it |

---

## Results log

Fill in as each chapter's evaluation runs. Numbers, not adjectives (Chapter 1 §1.10 rule).

| Date | Chapter | Recall@5 | MRR | Cross-modal Recall@5 | Notes / what changed |
|---|---|---|---|---|---|
| | | | | | |

---

## Licensing / privacy note

Use only files you own or that are freely shareable. Do not commit anything confidential — this folder may end up in the submitted report or a public repository.
