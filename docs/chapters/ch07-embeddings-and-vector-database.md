# Chapter 7 — Embeddings & the Vector Database (Day 7)

> **Deliverables today:** a shared embedding function (`src/core/embeddings.py`, sentence-transformers); shared ChromaDB plumbing (`src/core/vector_store.py`); a real indexing pipeline (`src/pipelines/documents/index.py` + `scripts/build_index.py`) that turns Chapter 6's `Chunk` objects into a real, persistent, searchable index; a real search function (`src/pipelines/documents/search.py`) — this project's first genuine semantic search; and the first real Recall@5/MRR measurement against Chapter 6's gold-set questions (`scripts/evaluate_retrieval.py`).
>
> **Prerequisites:** [Chapter 6](ch06-document-ingestion.md) (real `Chunk` objects to embed, and the gold-set questions this chapter measures against) and [ADR-003](../decisions/adr-003-two-vector-collections.md)/[ADR-004](../decisions/adr-004-chromadb-over-faiss.md) (why two collections, why ChromaDB — this chapter builds the actual collection setup those ADRs describe only in principle).
>
> **The framing for today.** Every chapter so far has run its own code and reported real output — that discipline caught something bigger than usual today. This chapter's own verification process found two genuine bugs in code written earlier the same day: an absolute path silently leaking into stored citation metadata, and a wrong assumption about how ChromaDB handles a repeated ID. Neither was caught by inspection — both were caught by actually running the code against real data and checking the real result against what was expected, which is the entire point of this project's testing discipline, not a formality layered on top of it. Both are told in full below, including the wrong first guess, because "I checked and I was wrong, here's how I found out" is a more useful thing to model than a chapter that only shows code that worked the first time.

---

## How to read this chapter

| Part | What it does | Time |
|---|---|---|
| **Part 1 — LEARN: sentence-transformers in Practice** | Loading a model, batch vs. single encoding, why `normalize_embeddings=True`, lazy loading. | ~30 min |
| **Part 2 — LEARN: ChromaDB's Real API Surface** | Client types, collections, `add()` vs. `upsert()` (with the real bug), `query_embeddings` vs. `query_texts` (a gotcha this project deliberately avoids), distance vs. similarity. | ~45 min |
| **Part 3 — LEARN: Measuring Retrieval — Recall@K and MRR, By Hand** | Worked examples of both metrics, and why a 3-question measurement is fragile evidence, not a strong result. | ~30 min |
| **Part 4 — DECIDE** | Module layout, explicit client passing, cosine space, `upsert()` over `add()`, the gold-set duplication tradeoff. | ~20 min |
| **Part 5 — BUILD** | Writing each file, building the real index, running real search, the two real bugs found and fixed. | ~2 hours |
| **Part 6 — CHECK** | Rubric, question bank, troubleshooting, completion checklist. | ~30 min |

**Learning outcomes.** You will be able to: call sentence-transformers correctly for batch and single-string embedding; explain why embeddings are normalized before storage; explain the actual, tested difference between ChromaDB's `add()` and `upsert()`, and why it matters for a re-run pipeline; explain why this project always passes `query_embeddings`, never `query_texts`; compute Recall@K and MRR by hand from a ranked result list; explain why measuring 3 questions is weaker evidence than the same score on 30; and trace through a real example of a bug caught by testing rather than by reading the code.

---

# Part 1 — LEARN: sentence-transformers in Practice

## 1.1 Loading and calling a model

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")   # downloads once, caches locally
vector = model.encode("some text")                 # a numpy array, 384 floats
```

The first call downloads the model's weights from Hugging Face (roughly 90 MB for this model) into a local cache (`~/.cache/huggingface/`); every call after that, on any project on the same machine, reuses the cached copy. This is the same content-addressed-caching idea Chapter 5 §2.2 described for `ollama pull` — a different tool, the same underlying reason (don't re-download something you already have).

## 1.2 Batch encoding vs. one string at a time

```python
model.encode(["first chunk", "second chunk", "third chunk"])   # one call, one batch
```
is meaningfully faster than calling `.encode()` three separate times, because the model's forward pass is a matrix operation that batches efficiently — three inputs processed together cost less than three times the cost of one. `embeddings.py`'s `embed_texts()` takes a list for exactly this reason; `embed_text()` (singular) is a convenience wrapper for the rare case of embedding exactly one string, not the default way to embed many.

## 1.3 `normalize_embeddings=True`, and why this project always sets it

```python
vectors = model.encode(texts, normalize_embeddings=True)
```

This scales every output vector to length 1. docs/GLOSSARY.md's **Cosine similarity** entry already states the consequence this project relies on: *"Identical in ranking to Euclidean distance once vectors are normalized."* Concretely: for two unit vectors `a` and `b`, squared Euclidean distance equals `2 - 2·cos(a,b)` — a strictly decreasing function of cosine similarity, so sorting by ascending Euclidean distance and sorting by descending cosine similarity produce the exact same order. This is *why* it doesn't functionally matter whether ChromaDB's underlying index compares vectors with L2 or cosine math, as long as normalization happened first — but Part 2 §2.2 still configures collections for cosine distance explicitly, for a readability reason unrelated to ranking correctness.

## 1.4 Lazy loading — the same principle as Chapter 5's `mmap` lesson, applied differently

`embeddings.py` loads the model on first use, not at import time:

```python
_model: SentenceTransformer | None = None

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.TEXT_EMBEDDING_MODEL)
    return _model
```

Chapter 5 §2.1 taught that memory-mapping loads a GGUF file's pages from disk lazily, on first access, rather than all at once — a lazy strategy implemented by the *operating system*. This is a different mechanism (ordinary Python, no OS involvement) achieving an analogous goal: don't pay for something before you need it. Importing `src.core.embeddings` from code that never calls `embed_text()` — a plausible thing to do, e.g. from a test file that only exercises `chunker.py` — costs nothing extra. The first real call pays the loading cost once; every call after reuses the cached `_model`.

---

# Part 2 — LEARN: ChromaDB's Real API Surface

## 2.1 Client types

| Client | Where it runs | This project's use |
|---|---|---|
| `PersistentClient` | Embedded in-process, writes to a local directory | **What we use** — matches ADR-004's "no server to run" decision |
| `EphemeralClient` | Embedded in-process, in-memory only, gone when the process exits | Not used in application code; conceptually what an in-memory test database would be |
| `HttpClient` | Talks to a separately-running ChromaDB **server** | Explicitly the deployment style ADR-004 rejected (§Alternatives, Qdrant point) — a server is one more thing that can silently not be running |

`get_client()` in `vector_store.py` always constructs a `PersistentClient`, pointed at `settings.CHROMA_PERSIST_DIR` by default, or an explicit `persist_dir` — the mechanism every test in this chapter uses to point at a throwaway `tmp_path` instead of the real, on-disk index.

## 2.2 Collections, and configuring the distance metric explicitly

```python
client.get_or_create_collection("text_index", metadata={"hnsw:space": "cosine"})
```

`get_or_create_collection` is idempotent — calling it again with the same name returns the same collection rather than erroring, which is exactly what lets `get_text_collection()` be called freely from anywhere without tracking whether "the first call" already happened.

**Why `hnsw:space: "cosine"` explicitly, given §1.3 already showed ranking is identical either way:** because Chroma reports *distance*, and cosine distance (`1 - cosine_similarity`, a value in `[0, 2]` where 0 means "identical direction") is directly interpretable by a person reading a printed number, unlike squared Euclidean distance on 384-dimensional vectors, which carries no intuitive scale. `search.py`'s `score = 1.0 - distance` conversion depends on this exact configuration — changing the collection's distance metric without updating that line would silently turn `.score` into a meaningless number.

## 2.3 `add()` vs. `upsert()` — the real, tested difference

This project's first draft of `vector_store.py` used `collection.add()`, on the reasonable-looking assumption that re-adding an existing `chunk_id` would either raise an error (so a real mistake would be obvious) or overwrite the old value (so re-running the indexer after editing a file would refresh it). **Both guesses were wrong**, discovered by testing rather than assumed:

```python
>>> col.add(ids=["notice_pdf__p1__c001"], documents=["THIS IS DELIBERATELY DIFFERENT TEXT"],
...         metadatas=[...], embeddings=[[0.01]*384])
>>> col.get(ids=["notice_pdf__p1__c001"])["documents"][0]
'Department of Computer Science and Engineering (Artificial Intelligence and Mach...'
```

**`add()` on an existing id neither errors nor updates — it silently keeps the ORIGINAL content and drops the new call entirely.** For this project, that means: fix a typo in `notice.pdf`, re-run `scripts/build_index.py`, and the index would keep serving the pre-fix text forever, with no error and no visible sign anything was skipped. Re-testing the same scenario with `upsert()` instead:

```python
>>> col.upsert(ids=["notice_pdf__p1__c001"], documents=["THIS IS DELIBERATELY DIFFERENT TEXT"],
...            metadatas=[...], embeddings=[[0.01]*384])
>>> col.get(ids=["notice_pdf__p1__c001"])["documents"][0]
'THIS IS DELIBERATELY DIFFERENT TEXT'
```

`upsert()` correctly replaces existing content by id and still inserts a genuinely new id normally. `vector_store.py`'s `add_chunks()` uses `upsert()` for exactly this reason, and `tests/test_retrieval.py`'s `test_add_chunks_re_indexing_the_same_id_replaces_stale_content` locks the *correct* behaviour in as a regression test, not just the fact that some behaviour was chosen.

> **Misconception check:** "Isn't checking library behavior instead of just reading its docs a waste of time?" No — this specific behavior (silent no-op on a duplicate id with `add()`) is the kind of detail that's easy to get wrong from documentation alone, and getting it wrong here would have shipped a real, silent correctness bug. Five minutes running both against a real collection settled it definitively; reading the same fact from documentation would have required not just glancing at it but consciously wondering about this exact case in advance — while running the wrong-behavior version at all *forces* the disagreement to surface immediately.

## 2.4 `query_embeddings` vs. `query_texts` — a gotcha this project avoids by construction

```python
collection.query(query_embeddings=[query_vector], n_results=5, ...)   # what search.py does
collection.query(query_texts=["some query"], n_results=5, ...)         # NOT what search.py does
```

`query_texts` looks more convenient — no manual embedding step — but it silently asks ChromaDB to embed the query using its *own default embedding function* (a small ONNX model Chroma bundles), not necessarily identical to the exact `all-MiniLM-L6-v2` weights `embeddings.py` uses to embed everything already stored. Comparing a query vector from one embedding pipeline against stored vectors from a different one produces numbers shaped like similarity scores that aren't actually measuring anything coherent — the two vector spaces aren't guaranteed to agree on what "similar" means. `search_text()` always computes the query embedding itself, through the exact same `embed_text()` every stored chunk went through, and passes `query_embeddings=` — never giving Chroma's default embedder a chance to enter the picture at all.

## 2.5 What a returned "distance" means, restated precisely

Given §2.2's `hnsw:space: "cosine"` configuration, `collection.query()`'s `distances` are `1 - cosine_similarity` per result — 0 for an exact directional match, up to 2 for the opposite direction. `search.py`'s `_chunk_from_result()` converts this back with `score = 1.0 - distance`, so `Chunk.score` is directly a cosine similarity in this project — a number a person can read as "close to 1 is a strong match," not an unlabeled distance requiring its own explanation every time it's shown.

---

# Part 3 — LEARN: Measuring Retrieval — Recall@K and MRR, By Hand

docs/GLOSSARY.md already defines both metrics (Ch1 §1.10) with stated targets — **Recall@5 ≥ 0.80**, **MRR ≥ 0.65**. This section works through computing them from an actual ranked result list, not just their definitions.

## 3.1 Recall@K, worked

*"Fraction of test questions where the correct chunk appears in the top K results."* For a single question, this is binary: 1 if the expected `(source, page)` appears anywhere in the top-K list, 0 if it doesn't — rank within the top K doesn't matter for this metric, only presence. Averaged across every question in the gold set, it becomes a fraction.

## 3.2 MRR, worked

*"Average of 1/(rank of the first correct result)."* Unlike Recall@K, rank matters here: a hit at rank 1 scores `1/1 = 1.0`; a hit at rank 3 scores `1/3 ≈ 0.33`; no hit within the ranked list scores `0`. MRR rewards putting the right answer *first*, specifically — two systems can have identical Recall@5 while having very different MRR, if one consistently ranks the right chunk 1st and the other consistently ranks it 5th.

## 3.3 Why 3 questions is fragile evidence, not a strong result

`reports/methodology-draft.md`'s own template already names this exact concern: *"With `⟨FILL: N⟩` questions, a single item shifts Recall@5 by `⟨FILL: 1/N⟩`; small differences are not meaningful."* With this chapter's `N = 3`, **one single miss changes Recall@5 from 1.00 to 0.67** — a huge swing from one data point. Part 5 §5.7 below reports a genuine `Recall@5 = 1.00, MRR = 1.00` — both comfortably above target — but the honest read of that number is "the system did not fail on 3 small, carefully-paraphrased questions against a 6-chunk synthetic corpus," not "the system reliably exceeds its target." Chapter 6 already flagged the gold set needs to grow to 20 text questions by this chapter; that growth (still open, `data/README.md` T4–T5 onward) is what would turn this into evidence worth reporting confidently, not this chapter's 3-question run on its own.

---

# Part 4 — DECIDE

## 4.1 Module layout

```
src/
├── core/
│   ├── embeddings.py     ← NEW: shared (this chapter's document indexing + Ch9 audio both need it)
│   └── vector_store.py   ← NEW: shared (every modality writes into one of two collections)
└── pipelines/
    └── documents/
        ├── index.py       ← NEW: orchestrates ingest_document() + embed + store, for documents specifically
        └── search.py      ← NEW: this chapter's "first semantic search," reusable by Chapter 10
```

`embeddings.py` and `vector_store.py` go in `src/core/` for the same reason `text_normalize.py` did in Chapter 6: more than one track's output shape depends on them. `index.py` and `search.py` stay under `documents/` because *how* documents get indexed and searched is genuinely Track A's business, even though the underlying plumbing they call is shared.

## 4.2 Explicit client passing, not a hidden global connection

Every function here (`add_chunks`, `get_text_collection`, `index_documents_directory`, `search_text`) takes an optional `client` parameter rather than reaching for a module-level singleton the way `src.core.config.settings` does. A database connection isn't the same *kind* of thing as read-only configuration: every test in this chapter needs to point at a disposable `tmp_path` instead of the real `chroma_db/`, and a hidden global would make that impossible without monkeypatching. One extra argument, passed through consistently, buys real test isolation — confirmed by this chapter's own tests never once touching the real index.

## 4.3 Cosine space, chosen explicitly (not left as Chroma's l2 default)

Covered in full in Part 2 §2.2 — restated here because it's a decision, not an accident: normalized vectors make l2 and cosine rank identically, so this choice is entirely about `.score` being a directly-readable number rather than an arbitrary-scale one.

## 4.4 `upsert()` over `add()` — the decision the real bug in §2.3 forced

Not a stylistic preference — `add()`'s silent-no-op behavior on a duplicate id was tested and rejected because it would make `scripts/build_index.py` unsafe to re-run after any content edit. `upsert()` is what actually satisfies "re-run this any time data/documents/ changes," which is the script's own stated purpose.

## 4.5 The gold set stays a manual copy in `scripts/evaluate_retrieval.py`, for now

`data/README.md`'s gold-set table is written for humans — prose, a callout box, three populated rows out of an eventual twenty. Building a markdown-table parser to keep `evaluate_retrieval.py`'s `GOLD_QUESTIONS` in sync automatically is real, legitimate future work, explicitly not done today: three rows doesn't justify the parser yet, and the script's own docstring says so plainly rather than silently risking drift. Revisit this once the gold set actually reaches the 20-question target and keeping two copies in sync by hand becomes the more expensive option.

---

# Part 5 — BUILD: the actual Day 7

> **Verification methodology, same disclosure as Chapter 6.** This machine still doesn't have the team's own pinned Python 3.11 venv — everything below was run for real, but with currently-available `sentence-transformers`/`chromadb` builds on Python 3.14, not the exact pins in `requirements.txt`. Re-run everything yourselves inside your own pinned venv and confirm the same shape of result. One environment-specific detail *is* worth knowing regardless of pin version: on Windows, `sentence-transformers`' first download prints a real warning about symlink support requiring Developer Mode or admin rights — harmless, and only affects cache disk usage, not correctness.

## 5.1 Write `src/core/embeddings.py`

`embed_texts()` / `embed_text()` — see Part 1. Needs no new entry in `requirements.txt`; `sentence-transformers` has been pinned there since Chapter 5.

## 5.2 Write `src/core/vector_store.py`

`get_client()`, `get_text_collection()`, `get_image_collection()`, `add_chunks()` — see Part 2. Use `upsert()`, not `add()`, inside `add_chunks()` — §2.3 is the whole reason.

## 5.3 Write `src/pipelines/documents/index.py` and `search.py`

`index_documents_directory()` and `search_text()` — see Parts 2–4. One detail worth building carefully, because it's exactly what this chapter's first real bug was: **`ingest_document()` (Chapter 6) stores whatever path form it's handed, verbatim, as `Chunk.source`.** If the directory `index_documents_directory()` iterates was itself constructed as an absolute path — a completely natural thing to do, e.g. `Path(__file__).resolve().parent / "data" / "documents"` — every resulting chunk's `source` silently becomes an absolute, this-machine-only path instead of the portable `data/documents/notice.pdf` every other chunk in this project uses. `index_documents_directory()` guards against this itself (`_relative_to_cwd()`), rather than trusting every future caller to remember to pass a relative path — this bug was caught by a gold-question test genuinely failing to match on `source`, not by inspection, exactly the way §2.3's bug was caught by running code, not reading it.

## 5.4 Write `scripts/build_index.py`

```bash
python scripts/build_index.py
```
**Real captured output:**
```
Indexing X:\RAGNova\data\documents into ./chroma_db ...
Indexed 6 chunks into text_index.

Next: python scripts/evaluate_retrieval.py
```
6 chunks — matching Chapter 6's own count exactly: `notice.pdf` (1 + 2), `library_hours.pdf` (1), `it_onboarding.docx` (1 + 1).

## 5.5 Write `scripts/evaluate_retrieval.py`

Mirrors `data/README.md`'s T1–T3 rows (§4.5 explains why as a manual copy, not a parse). Same em-dash-on-Windows-console fix Chapter 5's `verify_setup.py` already established (`sys.stdout.reconfigure(encoding="utf-8")`) — needed again here because this script's own HIT/MISS lines print one.

## 5.6 Run `tests/test_retrieval.py`

```bash
pytest tests/test_retrieval.py -v
```
**Real captured output** (after both bugs above were found and fixed — this is the *passing* run, not the first one):
```
tests/test_retrieval.py::test_embed_text_returns_a_unit_length_384_dim_vector PASSED
tests/test_retrieval.py::test_embed_text_is_deterministic PASSED
tests/test_retrieval.py::test_embed_texts_batch_matches_individual_calls PASSED
tests/test_retrieval.py::test_semantically_similar_sentences_score_higher_than_unrelated PASSED
tests/test_retrieval.py::test_add_chunks_round_trips_real_embeddings PASSED
tests/test_retrieval.py::test_add_chunks_rejects_mismatched_lengths PASSED
tests/test_retrieval.py::test_add_chunks_empty_list_is_a_noop PASSED
tests/test_retrieval.py::test_add_chunks_re_indexing_the_same_id_replaces_stale_content PASSED
tests/test_retrieval.py::test_index_documents_directory_indexes_every_chunk_from_all_three_files PASSED
tests/test_retrieval.py::test_search_text_finds_the_right_chunk_for_every_gold_question PASSED
tests/test_retrieval.py::test_search_results_are_sorted_by_descending_score PASSED
tests/test_retrieval.py::test_search_results_satisfy_the_contract PASSED

======================= 12 passed in 15.22s =========================
```
**This run did not pass the first time.** `test_search_text_finds_the_right_chunk_for_every_gold_question` failed on its first execution — that failure is exactly what led to finding §5.3's absolute-path bug. Then run the whole suite, confirming Chapters 5 and 6 are still undisturbed:
```bash
pytest tests/ -v
```
```
======================= 48 passed in 20.56s =========================
```
10 (Ch5) + 26 (Ch6, including one new blank-page test found worth adding during this chapter's own verification — see §5.8) + 12 (Ch7) = 48.

## 5.7 Run the real evaluation

```bash
python scripts/evaluate_retrieval.py
```
**Real captured output:**
```
Evaluating 3 gold questions at top_k=5...

[T1] HIT  at rank 1  (score=0.424)  — If I don't get my system actually running by evaluation day, how many marks am I giving up?
[T2] HIT  at rank 1  (score=0.475)  — As an undergrad, how many items can I check out from the library at once, and for how long?
[T3] HIT  at rank 1  (score=0.458)  — What happens the first time someone gets caught sharing their login with a friend?

Recall@5: 1.00
MRR:       1.00
```
All three pure-paraphrase questions retrieved their expected chunk at rank 1, not just somewhere in the top 5. Read this together with Part 3 §3.3 before reporting it anywhere — genuinely good on 3 questions, not yet strong evidence at the scale a report should claim it at. Add the row to `data/README.md`'s Results log:
```
| 2026-09-15 | Ch7 | 1.00 | 1.00 | N/A (no images/audio yet) | first real semantic search, 3 text queries |
```

## 5.8 A related bug found while writing this chapter, not by this chapter's own new code

While verifying §5.3's fix, deliberately constructing a blank PDF page to test the zero-extractable-text path (Chapter 6 §1.4) directly showed its warning message rendering as `?` instead of an em-dash on this Windows console — the exact class of bug `verify_setup.py` already found and fixed for **stdout** in Chapter 5, but `ingest_document()`'s warning uses **stderr**, which that earlier fix never touched. Fixed the same way, applied to the stream that actually needed it (`src/pipelines/documents/ingest.py`), and this exact path — a blank page producing zero chunks and a correctly-encoded warning — now has its own regression test (`tests/test_document_ingestion.py::test_blank_pdf_page_produces_zero_chunks_and_warns`), closing a real gap that existed since Chapter 6 and had simply never been exercised until now.

## 5.9 Git hygiene for today

- [ ] `src/core/embeddings.py`, `src/core/vector_store.py` committed
- [ ] `src/pipelines/documents/index.py`, `search.py` committed
- [ ] `scripts/build_index.py`, `scripts/evaluate_retrieval.py` committed
- [ ] `tests/test_retrieval.py` committed; `tests/test_contract.py` and `tests/test_document_ingestion.py` **unchanged in intent** (the one new test added to `test_document_ingestion.py` covers pre-existing Chapter 6 behavior, not a Chapter 7 feature)
- [ ] The small `src/pipelines/documents/ingest.py` diff (stderr encoding fix) committed with a clear message explaining *why*, not just *what*
- [ ] `chroma_db/` is **not** committed — confirm `.gitignore` still covers it (Chapter 5 already added this line; just verify `git status` agrees)
- [ ] `data/README.md`'s Results log row added
- [ ] Every team member has run §5.6–§5.7 on their own machine and seen the same pass/fail shape and a Recall@5/MRR in the same range

---

# Part 6 — CHECK

## 6.1 Rubric

| # | Criterion | Score |
|---|---|---|
| 1 | `python scripts/build_index.py` runs, indexes 6 chunks | /3 |
| 2 | `pytest tests/test_retrieval.py -v` fully passes | /3 |
| 3 | `pytest tests/ -v` fully passes — no regression to Chapters 5–6 | /3 |
| 4 | `python scripts/evaluate_retrieval.py` runs and reports Recall@5/MRR | /3 |
| 5 | Team can explain the real, tested difference between `add()` and `upsert()` | /3 |
| 6 | Team can explain why `search_text()` always passes `query_embeddings`, never `query_texts` | /3 |
| 7 | Team can compute Recall@K and MRR by hand from a small example ranked list | /3 |
| 8 | Team can explain why a 3-question Recall@5 of 1.00 is not strong evidence on its own | /3 |
| 9 | Team can explain why `add_chunks()` takes an explicit `client`, not a hidden global | /3 |
| 10 | `data/README.md`'s Results log has today's real row | /3 |
| | **Total** | **/30** |

## 6.2 Question bank

1. Why does `embed_texts()` take a list rather than being called once per string in a loop? → §1.2; batched forward pass, meaningfully faster than N separate calls.
2. What does `normalize_embeddings=True` do, and which existing GLOSSARY fact does this project rely on because of it? → §1.3; unit-length vectors, "cosine similarity ranks identically to Euclidean distance once normalized."
3. Why is the embedding model loaded lazily rather than at module import time? → §1.4; same lazy-loading principle as Chapter 5's mmap lesson, applied to avoid paying model-load cost on every import.
4. What did `add()` actually do when given a chunk_id that already existed, tested directly rather than assumed? → §2.3; silently kept the original content, dropped the new call, no error.
5. Why does that matter specifically for `scripts/build_index.py`? → §2.3/§4.4; re-running it after fixing a typo would otherwise leave the index serving stale text forever, invisibly.
6. What's the risk of calling `collection.query(query_texts=[...])` instead of computing the embedding yourself? → §2.4; silently uses Chroma's own default embedding function, which may not match what was used to index — comparing vectors from two different models.
7. What does a ChromaDB "distance" of 0 mean, given this project's `hnsw:space` configuration? → §2.2/§2.5; cosine distance 0 = identical direction = highest possible similarity.
8. A gold question's expected chunk appears at rank 3 out of 5 results. What's its contribution to Recall@5? To MRR? → §3.1–3.2; Recall@5 contribution = 1 (present in top 5); MRR contribution = 1/3.
9. Why is a measured Recall@5 = 1.00 on 3 questions weaker evidence than the same score on 30? → §3.3; one single miss on 3 questions swings the score by 0.33 — the metric is highly sensitive to sample size this small.
10. What real bug did `index_documents_directory()`'s own path handling cause, and how was it caught? → §5.3; an absolute directory path leaked into `Chunk.source`, caught by a gold-question test genuinely failing to match, not by code review.
11. Why does `search_text()` reconstruct a `Chunk` from a query result instead of returning ChromaDB's raw result dict? → `search.py`'s docstring; keeps every caller (including Chapter 10 later) working with the same typed object the rest of the project already uses, `.score` included.
12. Where does the gold-set data live for `scripts/evaluate_retrieval.py`, and what's the known risk of that choice? → §4.5; a manual copy of `data/README.md`'s T1–T3, which can silently drift out of sync if one is edited without the other.

## 6.3 Troubleshooting — extends Chapter 6 §6.3

| Symptom | Cause | Fix |
|---|---|---|
| `? If I don't get my system...` instead of `— If I don't...` in `evaluate_retrieval.py`'s output | The same Windows-console encoding issue Chapter 5's `verify_setup.py` fixed for stdout | Confirm the `sys.stdout.reconfigure(encoding="utf-8")` block near the top of the script is present and runs before any printing |
| Re-running `build_index.py` after editing a document doesn't seem to change search results | Would happen with plain `add()` (§2.3) — confirm `vector_store.py`'s `add_chunks()` still uses `upsert()`, not `add()` | Check the one line; this is the exact regression `test_add_chunks_re_indexing_the_same_id_replaces_stale_content` exists to catch |
| Search results all have unexpectedly low scores, even for an obviously relevant query | Check whether the collection was accidentally created without the cosine `metadata` config, or with a query built via `query_texts` instead of `query_embeddings` | Re-check §2.2 and §2.4; a mismatched embedding source produces scores that look valid but aren't measuring the same thing as the indexed vectors |
| `UserWarning: ... cache-system uses symlinks ...` when running any script for the first time | Windows-specific `huggingface_hub` warning about Developer Mode/admin rights for symlinked caching | Harmless — affects disk usage of the model cache only, not correctness; ignore unless disk space is a genuine concern |
| `sentence-transformers` download is slow or shows an "unauthenticated requests" warning | Normal — Hugging Face rate-limits anonymous downloads more strictly | Wait it out; only worth a free Hugging Face account + `HF_TOKEN` if this becomes a repeated annoyance across the team |
| `ModuleNotFoundError` for `chromadb` or `sentence_transformers` when running Chapter 7 scripts/tests | Not yet installed in the active venv | `pip install -r requirements.txt` (both have been pinned since Chapter 5) |

## 6.4 Day 7 completion checklist

- [ ] `src/core/embeddings.py`, `src/core/vector_store.py` written and understood
- [ ] `src/pipelines/documents/index.py`, `search.py` written
- [ ] `python scripts/build_index.py` run successfully; 6 chunks indexed
- [ ] `pytest tests/test_retrieval.py -v` and `pytest tests/ -v` both fully pass
- [ ] `python scripts/evaluate_retrieval.py` run; Recall@5/MRR logged in `data/README.md`
- [ ] Team can state, without notes, the real tested difference between `add()` and `upsert()`
- [ ] Team can explain why `query_embeddings` is used instead of `query_texts`
- [ ] Team understands why this chapter's Recall@5 = 1.00 is not yet strong evidence
- [ ] Rubric §6.1 scored ≥ 24/30

---

**Next:** Chapter 8 — Image Pipeline (CLIP + OCR), where Track B builds the `image_index` counterpart to this chapter's `text_index` — real images, real OCR text, real CLIP embeddings, and this project's first genuine cross-modal search.
