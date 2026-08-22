# Chapter 3 — Literature Review & Methodology (Day 3)

> **Deliverables today:** a **literature review** (15–20 sources, thematically organised, ending in a defended gap statement) and a **methodology section** (design rationale for every major decision, plus the evaluation protocol). Both feed Day 4's presentation and the Day 14 report.
>
> **Prerequisites:** [Chapter 1](ch01-objective-and-problem-identification.md) for objectives and stack; [Chapter 2](ch02-synopsis-and-presentation.md) for academic writing mechanics — this chapter assumes them and does not repeat them.
>
> **Companion files.** This chapter is the *method*. Two companions hold the material:
> - **[Chapter 3A — Annotated Bibliography](ch03a-annotated-bibliography.md)** — ~60 sources across eleven themes, with twelve deep dives. Your raw material.
> - **[Chapter 3B — Reading a Paper & Citation Mechanics](ch03b-reading-and-citations.md)** — a fully worked three-pass reading of CLIP, plus every IEEE entry type and the reference-manager workflow.

---

## Why this day is not optional

A literature review is not a ritual to satisfy an examiner. It is the day you discover whether your design decisions are defensible.

Consider what happens without it. You choose `all-MiniLM-L6-v2` because a tutorial used it. In the viva someone asks "why that model and not BGE or E5?" and you have nothing. With a literature review you answer: *"MTEB [MTEB] benchmarks embedding models across 56 tasks; MiniLM-L6 sits in the upper band for retrieval at 22M parameters and 384 dimensions, whereas BGE-large is 335M parameters — roughly fifteen times the memory for a few points of benchmark score we cannot exploit under our RAM budget."* That is the same decision, transformed from arbitrary into engineered.

Three of Chapter 1's stack choices are genuinely non-obvious — two vector collections rather than one, transcription rather than native audio embeddings, and rank-based rather than score-based merging. Today is when you learn *why* they are right, or discover they are wrong while changing them still costs nothing.

There is a second, less comfortable reason. **Today is when you find out whether someone has already built your project.** Finding that out on Day 3 is survivable and even useful; finding out in the viva is not.

---

## How to read this chapter

| Part | What it does | Time |
|---|---|---|
| **Part 1 — LEARN: the method** | What a review is for; where and how to search; how to judge a source; how to read a paper; how to manage references; how to synthesise rather than summarise; how to find and phrase a gap; how to cite without plagiarising. | ~120 min |
| **Part 2 — The survey, compressed** | Theme summary, the comparison table, and the assembled gap statement. Full material in [Ch 3A](ch03a-annotated-bibliography.md). | ~30 min |
| **Part 3 — LEARN: methodology** | Design science; design rationale and ADRs; data methodology; evaluation design with formulas and worked examples; threats to validity; reproducibility. | ~90 min |
| **Part 4 — DECIDE** | Structure, source count, gap claim, which decisions to formalise. | ~20 min |
| **Part 5 — BUILD** | Time-boxed day with role assignments. | ~5 hours |
| **Part 6 — CHECK** | Rubric, forty questions with answers, failure modes. | ~50 min |

**Learning outcomes.** You will be able to construct and log a search strategy; snowball a reference list in both directions; judge a source in ninety seconds; read a paper in three passes at increasing depth; extract the right things from an ML results table; manage references so citations never break; write thematically organised prose that argues; phrase a gap you can defend under attack; write design rationale naming rejected alternatives; define retrieval and generation metrics from their formulas; design a human study with blinding and agreement reporting; state what your evidence does *not* prove; and make your results reproducible.

---

# Part 1 — LEARN: the method

## 1.1 What a literature review is actually for

Students are told to "do a literature review" without being told what it *does*. It does four distinct jobs. Knowing which sentence is doing which job is how you write one that reads as an argument rather than a list.

| Job | What it proves | What it looks like in your text |
|---|---|---|
| **1. Establish the foundation** | You know the field's core ideas and did not reinvent them badly | "Dense retrieval displaced lexical matching following [SBERT], [DPR]." |
| **2. Justify your choices** | Your design rests on evidence, not on the first tutorial you found | "CLIP [CLIP] is selected because its contrastive objective produces a shared space, unlike independently trained unimodal encoders." |
| **3. Identify the gap** | Your project is not already done | "However, existing multimodal RAG systems assume cloud-hosted inference..." |
| **4. Set the evaluation bar** | You know how systems like yours are normally measured | "Retrieval is conventionally evaluated by Recall@k and nDCG [BEIR]." |

### 1.1.1 Job 2 is the one that earns marks

**Every non-obvious choice in your stack table should be traceable to a citation.** When a panel asks "why CLIP and not BLIP?", the answer *"because [CLIP] and [BLIP] optimise different objectives, and symmetric retrieval is what we need — BLIP's strength is captioning, which we do not use"* is worth ten times *"because a tutorial used it."*

Build this table as you read. It is the bridge from the review into the methodology section, and it converts reading time into two deliverables at once.

| Decision | Alternatives | Deciding evidence | Source |
|---|---|---|---|
| RAG over fine-tuning | fine-tune; long-context | Fine-tuning injects knowledge poorly and can *increase* hallucination | [FT-vs-RAG], [FT-Halluc] |
| MiniLM-L6 embeddings | BGE, E5, GTE | Benchmark position vs parameter count under a RAM budget | [MTEB] |
| CLIP for images | BLIP, SigLIP | Symmetric retrieval objective; open weights | [CLIP], [OpenCLIP] |
| Rank-based merge | score-based | Modality gap is systematic, not noise | [ModGap] |
| Whisper transcription | CLAP embeddings | Speech content is linguistic; timestamps required for citation | [Whisper], [CLAP] |

### 1.1.2 Job 4 is the one that saves you on Day 14

If your metrics come from the literature, nobody can argue you invented favourable ones. "We report Recall@5 and MRR, following standard retrieval evaluation practice [BEIR]" is unattackable. "We measured how good it felt" is not.

### 1.1.3 How a review is actually graded

Examiners rarely have a formal rubric, but they consistently reward four things, in this order of weight:

1. **Organisation by idea rather than by paper.** Detectable in ten seconds from paragraph shapes.
2. **A gap that follows from what precedes it.** The review must *earn* the gap, not assert it.
3. **Evidence of reading, not just citing.** Tested by asking what one paper says.
4. **Coverage.** Whether the obvious central works are present. Missing CLIP in a cross-modal project is fatal; missing an obscure 2024 paper is not.

Note that *number of references* is nowhere on that list. Twenty sources you can each summarise in one sentence beats forty you cannot.

## 1.2 Five anti-patterns

**❌ 1. The annotated bibliography.** One paragraph per paper, each summarising that paper, no connections. The most common student literature review, and it reads as exactly what it is.

*Diagnostic:* every paragraph begins with an author name.

**❌ 2. The summary chain.** *"Smith did X. Then Jones did Y. Then Patel did Z."* Chronological but uncompared. The reader learns what exists and nothing about what it means.

*Diagnostic:* you could reorder paragraphs without damaging meaning.

**❌ 3. The citation shield.** Sentences padded with references to look rigorous, where the citation does not support the claim. Examiners test this by picking one and asking what it says.

*Diagnostic:* a citation you cannot summarise aloud.

**❌ 4. The funnel that never lands.** Pages of general background — "AI is transforming industries" — that never reach the specific problem.

*Diagnostic:* your first citation specific to your actual problem appears on page two.

**❌ 5. The uncritical review.** Every paper described approvingly; no limitations, no disagreements, no trade-offs named.

*Diagnostic:* the words *however*, *whereas*, *by contrast* and *limitation* do not appear.

**✅ What it should be:** an argument organised by idea, in which multiple sources appear in a single sentence because they agree, disagree, or build on one another, ending at a gap your project fills.

## 1.3 Types of review, and which one you are writing

| Type | What it is | Effort | Use when |
|---|---|---|---|
| **Narrative / traditional** | Thematically organised discussion, sources selected by judgement | Days | ✅ **Yours** |
| **Systematic** | Exhaustive search, pre-registered inclusion criteria, PRISMA flow diagram, reproducible | Weeks–months | Formal research |
| **Scoping** | Maps breadth without depth | Weeks | Early-stage direction-finding |
| **Meta-analysis** | Statistical pooling across studies | Months | Empirical sciences |

You are writing a **narrative review**. Borrow one habit from systematic reviews: **keep a search log** (§1.5.5). When a panel asks "how did you find these papers?", "we searched these terms in these databases and here is the log" is dramatically stronger than "we googled."

## 1.4 Where to find papers — and what each source is uniquely good at

Using the wrong source wastes hours. Each has a specific strength.

| Source | Best at | How to actually use it | Watch out for |
|---|---|---|---|
| **Google Scholar** | Broad first sweep; **forward citation search** | Search, then click **"Cited by"** on anything central. Sort by citations. Use the year filter to separate foundations from current practice. | Indexes predatory venues alongside good ones with no visual distinction |
| **arXiv** | Newest ML work, months before publication; free full text | Browse `cs.CL`, `cs.IR`, `cs.CV`. Use `arxiv-sanity` or the listing by date. | **Not peer-reviewed** (§1.7.3) |
| **Semantic Scholar** | Citation graph; *influential* citation counts; TLDRs | Open a paper → "Citations" tab → filter by "Highly Influential". This surfaces the papers that genuinely built on it, not the ones citing it in passing. | TLDRs are convenient, not a substitute for reading |
| **Papers with Code** | Papers *with working implementations*; leaderboards | Search a task ("Image-Text Retrieval") to see what actually works | Benchmark-centric; misses systems work |
| **Connected Papers** | Visual graph of a paper's neighbourhood | Seed with your most central paper; the graph shows prior and derivative work you missed | Free tier limits graphs per month |
| **MTEB / BEIR leaderboards** | **Choosing an embedding model with evidence** | Filter by model size and retrieval score; this *is* your justification | Leaderboard gaming; check parameter counts |
| **ACL Anthology** | Every NLP paper, free, authoritative | Search by venue and year; BibTeX provided per paper | NLP only |
| **IEEE Xplore / ACM DL** | Peer-reviewed venues, correct citation metadata | Use your institution's proxy | Paywalled |
| **Official documentation** | Ground truth for tools you use | Cite docs with an access date | Never cite a tutorial blog as evidence |

### 1.4.1 The workflow that actually works

1. **Google Scholar** — find the two or three obviously central papers (they will have thousands of citations).
2. **Read those to Pass 1** (§1.8).
3. **Connected Papers or Semantic Scholar** on one of them — this is where the non-obvious references come from. Fifteen minutes, and it is the step that separates a review that looks researched from one that looks googled.
4. **Forward-citation search** on the closest prior work (§1.6.2) — this is where you find out whether your project already exists.
5. **MTEB / Papers with Code** for the specific engineering choices you must justify.

### 1.4.2 Getting paywalled papers legitimately

In order of speed: (1) your institution's library proxy; (2) **arXiv** — most ML papers have a free preprint; (3) the author's personal or lab website, which almost always hosts a PDF; (4) email the author, who will nearly always send it and is often pleased to be asked. Do not use pirate mirrors — it is both a legal problem and, in a submitted report, a citation you cannot properly source.

## 1.5 How to search properly

### 1.5.1 Decompose into concepts, never search a sentence

Do not type your project title into a search box. Break the problem into concepts, list synonyms per concept, then combine.

| Concept | Synonyms and near-terms |
|---|---|
| Retrieval-augmented generation | RAG · retrieval-augmented LM · knowledge-grounded generation · open-domain QA · grounded generation |
| Semantic search | dense retrieval · vector search · neural IR · embedding-based retrieval · dual encoder · bi-encoder |
| Cross-modal | multimodal retrieval · image-text retrieval · vision-language · text-to-image search · joint embedding |
| Speech search | spoken content retrieval · ASR · speech-to-text · spoken document retrieval |
| Offline / local | on-device inference · edge deployment · local LLM · quantized inference · privacy-preserving NLP |
| Citations | attribution · groundedness · provenance · verifiability · source attribution · faithfulness |
| Chunking | passage segmentation · text splitting · document segmentation · passage granularity |

**The synonym list is not optional.** "Citation transparency" returns almost nothing; **"attribution"** and **"verifiability"** return an entire literature (see [Ch 3A Theme 9](ch03a-annotated-bibliography.md)). Missing that literature would be a serious gap in a project whose fourth objective is citations.

### 1.5.2 Boolean operators, per engine

| Operator | Google Scholar | arXiv | Semantic Scholar |
|---|---|---|---|
| Exact phrase | `"dense retrieval"` | `"dense retrieval"` | `"dense retrieval"` |
| AND | space (implicit) | `AND` | space |
| OR | `OR` (capitals required) | `OR` | `OR` |
| Exclude | `-caption` | `ANDNOT` | `-caption` |
| Field-restricted | `author:radford` `source:NeurIPS` | `ti:`, `abs:`, `au:`, `cat:` | filters in UI |
| Date range | UI sidebar | `submittedDate:[...]` | UI sidebar |

### 1.5.3 A worked search session

Do this rather than reading about it. Approximate result counts are indicative — yours will differ.

```
Query 1  "multimodal retrieval-augmented generation"
         → many results, mostly 2023–2025. Scan first 30 titles.
         Keep: MuRAG, RA-CM3, REVEAL, and any survey.

Query 2  "multimodal RAG" AND (offline OR "on-device" OR local)
         → far fewer. THIS THINNESS IS YOUR EVIDENCE.
         Screenshot the result count for your slides.

Query 3  "modality gap" contrastive
         → finds Liang et al. NeurIPS 2022. This single paper
           upgrades your merge policy from a hack to a design decision.

Query 4  Forward citations of Lewis et al. 2020, filtered "multimodal"
         → what people built on RAG. Find Self-RAG, CRAG, surveys.

Query 5  "attribution" OR "verifiability" AND "language model"
         → a whole literature on citations you would otherwise miss:
           Rashkin, Bohnet, Liu (verifiability), Menick (GopherCite).

Query 6  MTEB leaderboard, filter: retrieval, <100M parameters
         → the evidence for your embedding model choice.

Query 7  "document screenshot" retrieval  OR  ColPali
         → the modern alternative to parse-then-embed. You must be
           able to say why you did not do this.
```

**Query 2 deserves comment.** When a search returns very few relevant results, that is not a failed search — it is a finding, and it is exactly the evidence a gap statement needs. Record the count and the date.

### 1.5.4 The three-generation rule

For each core concept, deliberately find:

1. **The foundational paper** — introduced the idea (often 2017–2021, heavily cited)
2. **A significant extension** — what came next
3. **A recent survey or system paper (2023–2025)** — current consensus

This produces historical depth *and* currency, and hands you the "X established A, Y extended it to B, current systems do C" structure that §1.13 needs.

### 1.5.5 The search log

| Date | Source | Query | Scanned | Kept | Notes |
|---|---|---|---|---|---|
| ⟨date⟩ | Scholar | `"multimodal RAG" offline` | 40 | 3 | Almost all cloud-based — **supports gap** |
| ⟨date⟩ | Scholar | Forward cites of Lewis 2020 | 60 | 5 | Found Self-RAG, CRAG |

Template in [`reports/literature-matrix.md`](../../reports/literature-matrix.md). **Stop when you reach saturation** — when new searches keep returning papers you have already seen. That signal usually arrives faster than students expect, and recognising it prevents an open-ended day.

## 1.6 Snowballing — where your best references come from

Searching finds the obvious. Snowballing finds the rest, and it is faster.

### 1.6.1 Backward snowballing

Read a good paper's **reference list**. What did it build on?

**The heuristic that works:** if four papers you already respect all cite the same fifth paper, that fifth paper is foundational and you must read it. This is how you find things nobody's search terms would have surfaced.

### 1.6.2 Forward snowballing — the mandatory one

On Google Scholar, click **"Cited by"** under a paper. Everything published since that builds on it, sortable by citations. Then use the **"Search within citing articles"** box to filter.

> **Do this today, for real.** Open Lewis et al. 2020 → "Cited by" → search within for `multimodal`, then for `offline`, then for `local`. Repeat for MuRAG.
>
> Three outcomes, all valuable:
> - **Nothing close** → your gap is real, and you now have evidence rather than assertion.
> - **Something adjacent** → a strong reference, and a sharper gap.
> - **Something very close** → you must narrow your gap. Finding this on Day 3 costs an hour. Finding it in the viva costs the viva.

### 1.6.3 Citation-graph tools

**Connected Papers** builds a similarity graph from one seed paper — prior work on one side, derivative on the other. **Semantic Scholar's "Highly Influential Citations"** filter distinguishes papers that genuinely built on a work from those that cite it in passing; that distinction is not available on Google Scholar and it is worth the extra click.

## 1.7 Judging whether a source is worth citing

Five tests, ninety seconds per paper.

### 1.7.1 Venue

| Tier | Examples | Treatment |
|---|---|---|
| **Top ML/NLP/CV conferences** | NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, CVPR, ICCV, ECCV, SIGIR | Cite confidently |
| **Strong journals** | IEEE TPAMI, TACL, JMLR, ACM Computing Surveys, VLDB Journal | Cite confidently |
| **Reputable secondary** | ICASSP, Interspeech, ECIR, WACV, EACL, COLING, workshops at top venues | Fine — say "workshop paper" if it is one |
| **arXiv preprint only** | — | Usable, with care (§1.7.3) |
| **Unknown journal, high fee, "fast review"** | — | ❌ Predatory. Never cite |
| **Blogs, Medium, YouTube** | — | ❌ Not evidence. Excellent for *learning* |

> **In machine learning, conferences outrank journals.** This surprises students from other disciplines. NeurIPS and ACL are fully peer-reviewed and are the field's primary venues. Do not downgrade a paper for being "only" a conference paper — and do not describe an ICML paper as "published in a conference, not a journal" in your report.

### 1.7.2 Citations, read correctly

Normalise by age: **citations per year since publication.**

| Rate | Interpretation |
|---|---|
| > 100/year | Landmark |
| 20–100/year | Solid, influential |
| 5–20/year | Respectable |
| < 5/year, older than 3 years | Needs another justification for inclusion |

A 2024 paper with 50 citations may be excellent — it has had no time. A 2015 paper with 3 citations probably is not worth your attention.

### 1.7.3 Preprints

Much of the most important ML work appears on arXiv months or years before formal publication, and some never appears elsewhere. Refusing preprints would exclude central work.

**The rule:** cite preprints when the work is clearly influential — high citations, known lab, released code, independent reproductions — and **always cite the published version if one exists.** Check: many papers you find on arXiv were later published at NeurIPS or ACL, and citing the preprint when a peer-reviewed version exists reads as carelessness.

### 1.7.4 Predatory venue checklist

If three or more apply, do not cite:

- [ ] Emails you unsolicited inviting submission
- [ ] Promises review in days
- [ ] Publication fee prominent, editorial board vague or unverifiable
- [ ] Journal name closely imitates a well-known one
- [ ] Claims impact factors from organisations you cannot verify
- [ ] Scope absurdly broad ("Journal of Engineering, Medicine and Management")
- [ ] Papers on the site have obvious formatting and language errors

### 1.7.5 Primary versus secondary, and the reproducibility signal

Always trace a claim to its **primary source**. If you learned about CLIP from a survey, cite CLIP — unless you are citing the survey's *own* contribution, such as its taxonomy. Citing a survey for a fact the survey itself cites signals you did not read the original.

Two further positive signals worth noting when choosing between similar papers: **released code and weights**, and **independent reproductions**. OpenCLIP exists because CLIP's training data was not released; that history is itself citable and is why you cite both.

### 1.7.6 The one-sentence test

Before adding a paper to your reference list, say aloud what it contributed. If you cannot, you have not read it enough to cite it, and one panel question will expose that.

## 1.8 How to read a paper — three passes

You do not read a research paper like a textbook. Reading twenty papers cover-to-cover is impossible in a day and unnecessary. The standard technique is Keshav's three-pass method.

> **A fully worked example — an actual Pass 1, Pass 2 and Pass 3 on the CLIP paper, with the notes written out — is in [Chapter 3B](ch03b-reading-and-citations.md).** Read it before doing your own; seeing the output makes the method concrete in a way description cannot.

### Pass 1 — 5–10 minutes. Decide whether to continue.

Read only: **title, abstract, introduction, section headings, conclusion, figures.** Skip all mathematics.

Answer the five Cs: **Category** (technique / system / analysis / survey), **Context** (what it relates to), **Correctness** (do the assumptions look reasonable), **Contribution** (the main claim), **Clarity**.

You should be able to state the contribution in one sentence. **Most papers stop here** — roughly 60% of what you find should be Pass-1-only. That is a successful outcome, not a failure.

### Pass 2 — ~1 hour. Understand the content.

For papers directly underpinning your architecture. Read fully but **skip proofs and derivations**. Pay close attention to figures, tables, and axis labels — in ML papers the figures usually carry the argument.

### Pass 3 — hours. Reconstruct the reasoning.

Challenge every assumption; ask what you would have done differently. **Needed for at most two papers** — for you, CLIP and RAG, since those are what an examiner will probe.

### 1.8.1 Reading an ML paper specifically

ML papers hide their contribution in predictable places. Four skills worth having explicitly:

**Where the contribution actually is.** The abstract's *last two sentences* usually state it. The introduction's final paragraph almost always contains an explicit "our contributions are" list. Read those two places first.

**How to read a results table.** Ask, in this order:
1. What is the **baseline**, and is it a fair one? (A weak baseline makes anything look good.)
2. What is the **metric**, and is higher better?
3. How large is the **gap** — and is it larger than the variation between seeds?
4. What is **bolded**, and did the authors bold their own method by convention rather than by winning?
5. Which datasets are *missing* that you would expect?

**How to read an ablation table.** An ablation removes one component to show it matters. Read it as the authors' own answer to "which parts are load-bearing?" If a component's removal costs almost nothing, that component is not doing much — a fact often more useful to you than the headline result, because it tells you what you can safely omit.

**How to read a claim.** "State of the art" means *on the benchmarks reported, at submission time.* It is a time-stamped, dataset-scoped claim, not a permanent property. Never write "X is the state of the art" in your report without both qualifiers.

### 1.8.2 Reading a paper you do not understand

You will meet papers where the method section is impenetrable. This is normal and not a verdict on you. In order:

1. **Read the figures first.** In ML the architecture diagram often conveys more than three pages of prose.
2. **Find a talk.** Most NeurIPS/ICML/ACL papers have a 5–15 minute author video. Enormously faster than the paper.
3. **Find the blog post.** Author labs usually publish an accessible version. Use it to *understand*, then cite the paper.
4. **Read a survey's description of it** to get the shape, then return.
5. **Accept Pass 1 depth.** You do not need Pass 2 on everything. Knowing what a paper contributed is enough to cite it responsibly.

### 1.8.3 What to write down, immediately

Complete this before moving to the next paper. Memory decays fast, and re-reading because you took no notes is Day 3's most avoidable time loss.

```markdown
**Citation:** Author et al., "Title", Venue, Year
**Theme:** which of your review's themes
**Problem:** what was broken before this
**Key idea (own words):** ...        ← if you cannot paraphrase, you did not understand
**Method:** at whiteboard level
**Results / what was measured:** with numbers
**Limitations (authors' own):** ...
**Relevance to RAGNova:** what we take, what we reject, why   ← the field that matters
**Quotable claim + location:** ...
**Confidence:** did I read this to Pass 1 / 2 / 3?
```

The **Relevance** field is what turns reading into a literature review. A note without it is a summary; a note with it is an argument fragment you can paste almost directly into your prose.

## 1.9 Reference management — set this up before you write

Fifteen minutes now prevents an entire category of failure later: a reference list that does not match the in-text numbers, a citation with the wrong year, or a rebuild of the whole list when you insert one source in the middle.

**Use Zotero** (free, open-source). Install it plus the browser connector. On any paper page, click the connector — it captures authors, title, venue, year, and the PDF. Organise into a collection per theme, matching your review's structure so the collection *is* the outline.

Full setup, BibTeX workflow, and the mapping from Zotero fields to IEEE output are in [Chapter 3B](ch03b-reading-and-citations.md).

**Two rules regardless of tool:**
1. **Capture the reference the moment you decide to cite it**, not at the end. Reconstructing thirty citations on Day 13 is miserable and error-prone.
2. **Verify metadata against the actual paper.** Automatic capture is often wrong about venue — it frequently records the arXiv version when a conference version exists. Zotero saving it does not make it correct.

## 1.10 The synthesis matrix

The mechanical bridge from "twenty sets of notes" to "an argument organised by theme": papers as rows, themes as columns.

| Paper | Representation | Retrieval | Cross-modal | Grounding | Attribution | Offline |
|---|---|---|---|---|---|---|
| Sentence-BERT | ✅ core | ✅ | — | — | — | ✅ small |
| CLIP | ✅ | ✅ | ✅ core | — | — | ✅ |
| Modality gap | — | — | ✅ critical | — | — | — |
| RAG (Lewis) | — | ✅ | — | ✅ core | ⚠️ possible | ❌ assumes server |
| Verifiability (Liu) | — | — | — | ✅ | ✅ core | — |
| HNSW | — | ✅ core | — | — | — | ✅ embedded |

**Read down a column → you have written that paragraph.** The "Cross-modal" column becomes your cross-modal paragraph, citing everything marked in it. This is the concrete technique that prevents the paper-by-paper anti-pattern, because you are physically organised by idea rather than by source.

**Read across a row** → you see how one paper serves several themes, which is how a single citation legitimately appears in three paragraphs.

### 1.10.1 Diagnostics — the matrix tells you things

| Pattern | What it means | What to do |
|---|---|---|
| A column with one mark | Thin theme | Merge it, or find two more sources |
| A column with many marks | Your strongest theme | Lead with it |
| A row with one mark | A paper only tangentially relevant | Consider dropping it |
| **A combination of columns with no system marked across all of them** | **Your gap, found empirically** | This is the finding, not an assertion |
| Every paper marked in every column | Your themes are not distinct | Redefine them |

That fourth row is the important one. Your gap should emerge from the matrix, not be decided in advance and then justified.

## 1.11 Synthesis versus summary

This is the difference between a pass and a distinction.

**❌ Summary (paper-by-paper):**

> Reimers and Gurevych [2] proposed Sentence-BERT, which modifies BERT to produce sentence embeddings. Karpukhin et al. [3] proposed Dense Passage Retrieval, which uses dense vectors for retrieval. Lewis et al. [4] proposed RAG, which combines retrieval with generation. Radford et al. [5] proposed CLIP, which links images and text.

Four sentences, four papers, zero connections — and every sentence has the same shape, which is the smell of the anti-pattern.

**✅ Synthesis (idea-by-idea):**

> The shift from lexical to dense retrieval rests on the observation that semantic similarity can be expressed as geometric proximity. Sentence-BERT [2] made this practical by fine-tuning transformer encoders so that sentence-level vectors are directly comparable under cosine similarity, and Dense Passage Retrieval [3] demonstrated that such representations substantially outperform BM25 on open-domain question answering — establishing dense retrieval as the default for semantic search. Lewis et al. [4] then coupled a dense retriever to a generative model, showing that conditioning generation on retrieved evidence both improves factual accuracy and, crucially for the present work, leaves the evidence available for attribution. This grounding property is what makes citation possible at all: it is a consequence of the architecture rather than a presentation-layer addition.
>
> Extending the same geometric principle across modalities required a shared representation space. CLIP [5] achieved this by training image and text encoders jointly under a contrastive objective over large-scale caption data, such that an image and its description occupy nearby positions in one space. Cross-modal retrieval thereby reduces to the same nearest-neighbour operation as unimodal retrieval — a unification the present work exploits directly.

Same citations, organised by *idea*. Each paper appears because it advances the argument, and the last sentence of each paragraph connects the literature to *your* design.

### 1.11.1 Five moves that create synthesis

| Move | Signal phrases | Effect |
|---|---|---|
| **Agreement** | "Both [2] and [3] find..." · "Consistent with [4]..." | Groups papers into a position |
| **Contrast** | "Whereas [5] optimises X, [12] targets Y" | Shows you can distinguish, not just list |
| **Development** | "[2] established... subsequently [4] extended..." | Shows a field maturing |
| **Taxonomy** | "Approaches divide into A [2],[3] and B [5],[6]" | ⭐ Strongest move available |
| **Gap** | "However, none of [4]–[6] address..." | Justifies your project |

**The taxonomy move is the most impressive.** If you can say "existing approaches fall into three families, and each makes this trade-off," you demonstrate command of the area far beyond any amount of individual summarising. You have three natural taxonomies available:

- **Retrieval:** lexical / dense / hybrid / late-interaction
- **Document understanding:** parse-then-embed / OCR-then-embed / screenshot-as-image (ColPali-style)
- **RAG maturity:** naive / advanced / modular (using the survey's taxonomy)

Use at least one.

### 1.11.2 Paragraph templates

**Theme paragraph:**
> ⟨Topic sentence naming the idea.⟩ ⟨Foundational work and what it established [n].⟩ ⟨Extension or refinement [n], [n].⟩ ⟨A contrast or limitation [n].⟩ ⟨One sentence connecting this to our design.⟩

**Gap paragraph:**
> ⟨What exists [n], [n].⟩ ⟨However, ⟨specific limitation⟩.⟩ ⟨Why that limitation matters for our setting.⟩ ⟨What this work does about it.⟩

**Opening paragraph of the review** (roadmap — tells the reader the structure):
> ⟨This review examines N themes.⟩ ⟨Sections A and B cover foundations; C and D cover the multimodal extension; E covers attribution.⟩ ⟨The review concludes by identifying the gap this project addresses.⟩

**Closing paragraph** (the pivot into methodology):
> ⟨One sentence summarising what the field provides.⟩ ⟨One sentence naming what remains open.⟩ ⟨One sentence stating what this project therefore does.⟩

### 1.11.3 Transition phrase bank

Because vocabulary is the practical bottleneck when writing synthesis:

| Function | Phrases |
|---|---|
| Adding agreement | *Similarly · Likewise · Consistent with this · Building on this · In the same vein* |
| Contrasting | *However · By contrast · Whereas · Conversely · Nevertheless · While [n] assumes X, [m] instead* |
| Sequencing development | *Subsequently · Building on [n] · This was extended by · More recently* |
| Grouping | *Approaches fall into · Two families · Broadly, methods can be categorised as* |
| Signalling limitation | *A limitation of this approach is · This assumes · [n] does not address · remains an open question* |
| Landing the gap | *However, none of these · These systems assume · remains unaddressed · has received comparatively little attention* |

## 1.12 Finding and phrasing the gap

The gap is the load-bearing sentence of the review. Everything before exists to make it credible.

### 1.12.1 Types of gap — pick the honest one

| Type | Claim | Risk |
|---|---|---|
| **Nobody has done X** | Absolute novelty | ⚠️ Usually false; one counter-example destroys it |
| **X exists but not under constraint C** | ✅ **Yours** — multimodal RAG exists, but not fully offline | Low |
| **X and Y exist separately but not integrated** | ✅ **Also yours** — cross-modal retrieval and attributed RAG rarely combined | Low |
| **X exists but is not accessible or reproducible** | Engineering + documentation contribution | Modest but honest |
| **X has not been evaluated in setting S** | Empirical contribution | Requires solid evaluation |

Your gap combines rows 2 and 3. Both are safe because they are **conjunctive claims about combination**, not absolute claims about novelty. That distinction matters enormously: *"nobody has built a multimodal RAG system"* is false and will be destroyed. *"Multimodal RAG systems typically assume cloud-hosted inference, and cross-modal retrieval is rarely bidirectional in systems that also provide citation transparency"* is true, specific, and defensible.

### 1.12.2 The four-move formula

1. **Acknowledge what exists** — "Multimodal RAG has been demonstrated [MuRAG], [RA-CM3]."
2. **Name the specific limitation** — "However, these systems assume cloud-hosted embedding and generation."
3. **State why it matters** — "This precludes deployment on confidential corpora and in disconnected environments."
4. **State your contribution, modestly** — "This work integrates these components under a strict offline constraint, with attribution as a first-class design requirement."

Move 4 does *not* claim a new algorithm. **Your contribution is integration and constraint satisfaction, which is a legitimate engineering contribution — say it plainly.** Overclaiming novelty is the fastest way to lose a viva; claiming exactly what you did and defending it is the fastest way to win one.

### 1.12.3 Pressure-testing the gap

Prepare an answer for each. If any answer is weak, narrow the gap.

| Challenge | The shape of a good answer |
|---|---|
| *"ChatGPT with file upload does this"* | Cloud-hosted; session-scoped rather than a persistent index; no bidirectional cross-modal retrieval; attribution inconsistent |
| *"LangChain/LlamaIndex has multimodal RAG"* | Frameworks, not systems; multimodal is an add-on; typically default to hosted embeddings; cross-modal rarely bidirectional |
| *"NotebookLM handles documents and audio"* | Cloud; audio is a *generated output*, not a retrievable indexed modality; no image-to-document retrieval |
| *"MuRAG already did multimodal RAG"* | Server-scale infrastructure; image + text only, no speech; attribution not a design goal |
| *"ColPali retrieves documents as images — simpler than your pipeline"* | ⭐ The hardest question. Requires more compute per page; no timestamped audio path; our OCR + text path yields exact-string retrieval it cannot. **Have this answer ready.** |

That last row is the one most likely to catch you out, because it is a genuinely better idea in some respects. Being able to say *"yes, and here is the trade-off we chose and why"* is far stronger than not having heard of it.

## 1.13 Citing without plagiarising

### 1.13.1 The rule

**Cite whenever an idea, a number, a method, or a phrasing is not your own.** Common knowledge in the field ("neural networks consist of layers") needs no citation; anything specific does.

### 1.13.2 Paraphrase versus quote

In engineering writing, direct quotation is rare — reserve it for a definition so precise that rewording would damage it. A real paraphrase changes **both words and structure**:

| | Text |
|---|---|
| **Original** | "We train an image encoder and a text encoder jointly to predict the correct pairings of a batch of (image, text) training examples." |
| ❌ **Patchwriting** *(plagiarism)* | "They train an image encoder and text encoder together to predict the right pairings of a batch of (image, text) examples [5]." |
| ✅ **Genuine paraphrase** | "CLIP's objective is contrastive: within each batch the model must identify which caption belongs to which image, forcing matched pairs into proximity within a shared space [5]." |

**Patchwriting — swapping synonyms while keeping the original sentence structure — counts as plagiarism even with a citation attached.** The reliable technique: read the passage, close it, wait a beat, then write what it means in your own sentence shape. If you are looking back and forth while typing, you are patchwriting.

### 1.13.3 Other integrity issues

| Issue | What it is | Rule |
|---|---|---|
| **Self-plagiarism** | Reusing your own earlier submitted text | Disclose reuse; check your institution's policy |
| **Citation padding** | Citing to look rigorous | Cite only what you read and what supports the claim |
| **Misattribution** | Citing [5] for a claim [5] does not make | Verify the claim is actually in the paper |
| **Figure reuse** | Copying a figure from a paper | Redraw it yourself, or reproduce with "Adapted from [n]" and check permission |
| **AI-assisted writing** | Using an assistant to draft text | Follow your institution's disclosure policy. **In every case, you must be able to explain and defend every sentence you submit** — that requirement is independent of policy |

### 1.13.4 Pre-submission integrity check

- [ ] Every claim about prior work carries a citation
- [ ] Every in-text citation appears in the reference list, and vice versa
- [ ] References numbered in order of first appearance (IEEE)
- [ ] Every reference verified against the actual paper — authors, venue, year
- [ ] Published version cited where one exists, not the preprint
- [ ] Nothing patchwritten
- [ ] Every cited work read to at least abstract + conclusion
- [ ] Figures either original or attributed
- [ ] Similarity checker run, if available

---

# Part 2 — The survey, compressed

> **The full annotated bibliography — ~60 sources across eleven themes, with twelve deep dives — is [Chapter 3A](ch03a-annotated-bibliography.md).** This section gives the shape, the comparison table, and the gap statement.

## 2.1 The eleven themes

| # | Theme | What it establishes | Core sources |
|---|---|---|---|
| 1 | **Representation** | Meaning as geometry: word → contextual → sentence embeddings | Transformer, BERT, Sentence-BERT |
| 2 | **Retrieval** | Dense beats lexical; how to search vectors fast | DPR, HNSW, BM25, RRF, BEIR |
| 3 | **Embedding model selection** | ⭐ *How to justify your model choice with evidence* | MTEB, E5, BGE, GTE |
| 4 | **Cross-modal** | One shared space for images and text — and its known failure mode | CLIP, OpenCLIP, **modality gap**, BLIP, SigLIP |
| 5 | **Speech** | Robust offline transcription with timestamps | Whisper, WhisperX, CLAP, wav2vec 2.0 |
| 6 | **Document understanding** | ⭐ Parse-then-embed vs OCR vs screenshot-as-image | Tesseract, LayoutLM, Donut, **ColPali**, DSE |
| 7 | **Grounding & RAG** | Retrieval as the fix for parametric memory | RAG, REALM, FiD, Self-RAG, CRAG, RAG survey |
| 8 | **Why not fine-tuning** | ⭐ *Empirical evidence for ADR-001* | Ovadia, Gekhman, Kandpal, LoRA, QLoRA |
| 9 | **Attribution & verifiability** | ⭐ *The literature behind Objective O4* | Rashkin, Bohnet, Liu, GopherCite, RARR |
| 10 | **Chunking & context** | Passage granularity; the lost-in-the-middle effect | Lost in the Middle, RAPTOR, late chunking, LumberChunker |
| 11 | **Local execution** | Quantization is why offline is possible | GPTQ, AWQ, LLM.int8(), Llama 3, llama.cpp |

Four themes are starred because they are where a typical student project has *nothing* and yours will have evidence. Theme 3 justifies your embedding model; Theme 6 lets you answer the ColPali question; Theme 8 turns ADR-001 from an opinion into a finding; Theme 9 is an entire literature on citations that a keyword search for "citation" would never surface.

## 2.2 The comparison table

Prose alone will not make the gap visible. This table does the argumentative work of two pages and is the figure most likely to survive into your final report.

| System / approach | Text | Image | Audio | Cross-modal | Generative answer | Attribution | Offline |
|---|---|---|---|---|---|---|---|
| Keyword search (BM25) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Dense retrieval (DPR) | ✅ | ❌ | ❌ | ❌ | ❌ | ⚠️ passages only | ✅ |
| RAG (Lewis) | ✅ | ❌ | ❌ | ❌ | ✅ | ⚠️ possible, not built in | ⚠️ if self-hosted |
| CLIP retrieval | ⚠️ ≤77 tokens | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| ColPali / DSE | ✅ as image | ✅ | ❌ | ✅ | ⚠️ with a VLM | ⚠️ page-level | ⚠️ heavy |
| MuRAG | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| Cloud assistants + upload | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ⚠️ inconsistent | ❌ |
| LangChain / LlamaIndex demos | ✅ | ⚠️ add-on | ⚠️ add-on | ❌ | ✅ | ⚠️ manual | ⚠️ configurable |
| **RAGNova** | ✅ | ✅ | ✅ | ✅ 3 directions | ✅ | ✅ first-class | ✅ verified |

**The empty region in the bottom-right is your gap, made visible.** Note the honest ⚠️ marks — a table of all ✅ for you and all ❌ for everyone else is not credible and invites hostile questioning. Nuance persuades; triumph does not.

## 2.3 The gap statement, assembled

> Multimodal retrieval-augmented generation has been demonstrated over combined image and text corpora [MuRAG], [RA-CM3], and cross-modal retrieval is well established through contrastive vision-language pretraining [CLIP], [OpenCLIP]. Attribution has likewise received attention as an evaluation target [Rashkin], [Verifiability]. However, existing systems exhibit three limitations relative to the setting addressed here. First, they assume cloud-hosted embedding and generation services, precluding deployment on confidential corpora or in disconnected environments — a constraint that quantization research [GPTQ], [AWQ] has recently made unnecessary. Second, speech is rarely integrated as a first-class retrievable modality despite the maturity of robust offline transcription [Whisper]. Third, attribution is typically evaluated post hoc rather than propagated as provenance metadata through ingestion, indexing and generation. This work integrates four modalities under a strict offline constraint, maintains provenance from ingestion through to citation rendering, and evaluates the resulting system using established retrieval [BEIR] and RAG-specific [RAGAS] metrics.

Rewrite in your own words. Note that it claims **integration under a constraint**, names **three specific** limitations rather than one vague one, and cites evidence that the constraint is now satisfiable.

---

# Part 3 — LEARN: methodology

## 3.1 What "methodology" means in an engineering project

Students confuse two things. **Research methodology** describes how you produce and validate knowledge. **Implementation detail** describes what you typed. A methodology section is the first.

Five questions it must answer:

| Question | Section |
|---|---|
| What *kind* of work is this? | §3.2 |
| How is the system designed, and **why this way rather than the alternatives**? | §3.3 |
| What data will it be tested on, and where did that data come from? | §3.5 |
| How will you know whether it worked? | §3.6 |
| What could make your conclusions wrong? | §3.7 |

The word carrying the marks is **why**. "We use ChromaDB" is a parts list. "We use ChromaDB rather than FAISS because embedded operation removes a deployment dependency and metadata filtering is required for provenance, while FAISS's scale advantage is irrelevant below 10⁵ vectors" is methodology.

## 3.2 Naming your research approach

Yours is **Design Science Research (DSR)** — also called constructive or engineering research. You build an *artefact* that addresses a class of problem and evaluate it against defined criteria. It contrasts with *empirical* research (test a hypothesis against data) and *theoretical* research (prove a property).

DSR is conventionally described as two cycles, and naming them shows you understand the shape of your own work:

- **The design cycle** — build, evaluate, refine, repeat. Yours runs Days 5–13.
- **The relevance cycle** — check the artefact against the real problem environment. Yours is the human feedback in Chapter 12.

A third, the **rigour cycle**, connects the work to existing knowledge — which is precisely what today's literature review is.

State it explicitly:

> This project follows a design-science methodology: a software artefact is constructed to address an identified deficiency and evaluated against functional and performance criteria defined in advance and derived from the literature. The work is constructive rather than hypothesis-testing; the claim under evaluation is that the artefact satisfies its stated objectives, not that a general proposition about the world holds.

Then name the **development process**: incremental and modular, with independent pipelines built in parallel against a frozen shared interface, integrated at a scheduled point, then refined against human feedback. Name the two structural decisions that make it work — the schema freeze on Day 5 and integration on Day 12 rather than Day 13 — and say that both are deliberate risk responses.

## 3.3 Design rationale and Architecture Decision Records

For every significant decision, document four things: **the decision, the alternatives considered, the criteria, and the justification.** Missing alternatives is what makes a design section read as arbitrary.

> **An ADR without rejected alternatives is not an ADR — it is a note.** The alternatives are the entire value: they prove the decision was *chosen* rather than defaulted into. Where a rejection rests on evidence from the literature, **cite it** — that single line converts an implementation preference into a defensible design decision.

### 3.3.1 The seven ADRs, with the evidence each needs

| ADR | Decision | Interesting rejected alternative | Evidence to cite |
|---|---|---|---|
| 001 | RAG over fine-tuning | Fine-tuning | ⭐ Ovadia (RAG beats FT for knowledge injection); Gekhman (FT on new knowledge *increases* hallucination); Kandpal (models struggle with long-tail facts) |
| 002 | Local quantized LLM over cloud API | Cloud | GPTQ, AWQ (4-bit is near-lossless); privacy work (Carlini) |
| 003 | Two vector collections | One collection | CLIP's 77-token limit; the modality gap |
| 004 | ChromaDB over FAISS/Qdrant | FAISS | HNSW; ANN-Benchmarks; vector-DB survey |
| 005 | Transcription over native audio embeddings | CLAP | Whisper (timestamps, robustness); CLAP (sound, not speech semantics) |
| 006 | Fixed-size overlapping chunks | Semantic/recursive chunking | ⚠️ *thin published literature* — see §3.3.2 |
| 007 | Rank-based cross-modal merging | Score-based | Modality gap; Reciprocal Rank Fusion |

Note ADR-001. Most student projects justify "RAG not fine-tuning" by assertion. You can justify it with **three empirical papers**, one of which found that fine-tuning on new knowledge actively increases hallucination. That is a materially stronger answer, and it is available for the cost of citing it.

### 3.3.2 When the literature is thin — an honest methodological move

Chunking is a case where **practice outruns published research**. Most guidance lives in industry documentation and blog posts, not peer-reviewed venues. There are exceptions (late chunking, LumberChunker, RAPTOR), but there is no settled answer to "what chunk size should I use?"

The correct response is not to pretend otherwise, and not to cite a blog as though it were research. Write:

> Passage granularity has received comparatively little systematic study relative to its practical impact; published work addresses hierarchical [RAPTOR] and embedding-aware [LateChunking] alternatives, but general guidance remains largely empirical. **Segment size is therefore treated as a tunable parameter and determined by ablation (§8.4) rather than adopted from literature.**

**This is a genuinely strong move.** It demonstrates that you can tell where evidence exists and where it does not — and it converts a weakness into a justification for running your own experiment. Examiners notice this.

### 3.3.3 The ADR format

```markdown
# ADR-003: Use two vector collections rather than one

## Status
Accepted (Day 3)

## Context
Text is embedded with all-MiniLM-L6-v2 (384-d); images with OpenCLIP
ViT-B/32 (512-d). Both must be searchable from one query interface.
CLIP's text encoder truncates at 77 tokens.

## Decision
Maintain two ChromaDB collections, queried independently, merged by rank.

## Alternatives considered
1. One collection, one model — impossible: CLIP truncates at 77 tokens [CLIP],
   so document-length passages cannot be represented.
2. One collection with a learned projection between spaces — requires paired
   training data and validation we cannot perform in the schedule.
3. Two collections merged by raw score — rejected: the modality gap [ModGap]
   makes text-image similarities systematically lower than text-text, so
   images would rank last regardless of relevance.

## Consequences
+ Each modality embedded by the model best suited to it
+ Adding a modality means adding a collection, not redesigning
− Two indexes to maintain; merge policy becomes a tunable parameter
− Scores are not comparable across collections; the UI must never display
  them side by side as though on one scale

## Revisit if
A single encoder handles document-length text and images in one space at a
size viable for local execution.
```

Template and two worked examples are in [`docs/decisions/`](../decisions/).

## 3.4 Structure of the methodology section

| § | Content |
|---|---|
| 1 | Research approach — design science; incremental modular development |
| 2 | System architecture — diagram plus component walkthrough |
| 3 | Ingestion methodology — per modality; chunking parameters justified; metadata schema |
| 4 | Indexing methodology — embedding models with citations; collection design; ANN algorithm |
| 5 | Retrieval methodology — query embedding; top-K; cross-modal merge policy |
| 6 | Generation methodology — prompt construction; temperature; citation format and validation |
| 7 | Data methodology — corpus composition; gold-set construction; annotation protocol |
| 8 | Evaluation methodology — metrics; protocol; human study design; ablations |
| 9 | Threats to validity |
| 10 | Reproducibility |

## 3.5 Data methodology

### 3.5.1 Corpus

**Sampling is purposive, not random** — say this explicitly, using the term. The corpus is constructed to exercise cross-modal capability: it deliberately contains an image and a document on the same topic, and an audio clip discussing a topic also present in a PDF. Random sampling would not guarantee the cross-modal pairs the third objective requires.

Report composition as a table: count and total size per modality, page count for documents, total duration for audio, language, and provenance (created by the team / public domain / licensed).

### 3.5.2 Gold-set construction protocol

Describe this as a *protocol*, because that is what makes it credible:

1. **Written before implementation.** Chapter 1 §3.3. Say so — it prevents unconscious tuning-to-the-test.
2. **Query types deliberately balanced:** direct-lookup, paraphrase (sharing no keywords with the source — these are the ones that prove semantic search), cross-modal, multi-hop if any, and **negative controls** the corpus genuinely cannot answer.
3. **Annotation:** each query labelled with the segment(s) that should be retrieved.
4. **Independent verification:** a second team member confirms each label without seeing the first's answer, and disagreements are resolved by discussion. **Report how many needed resolution** — it is a measure of how well-defined your labels are.
5. **Frozen before evaluation.** Once you begin measuring, the gold set does not change. Adding a question after seeing a failure invalidates the comparison.

### 3.5.3 The bias you must disclose

**The gold set was authored by the same team that built the system.** This risks question phrasing that unconsciously favours your architecture — you will naturally write questions your design handles.

Mitigation: external participants author additional questions in Chapter 12, and **those results are reported separately** from the internal set.

> Stating a limitation and its mitigation is worth more than concealing it. A panel that *discovers* an undisclosed weakness treats everything else you claim with suspicion. A panel that is *told* about one treats you as a careful researcher.

### 3.5.4 Ethics and licensing

Only owned or freely redistributable files; no confidential material in a submitted corpus; note that local execution means no corpus content is transmitted anywhere, which is itself the privacy control the project argues for.

## 3.6 Evaluation methodology

### 3.6.1 The principle

**An evaluation that cannot fail is not an evaluation.** Define metrics, targets and protocol *now*, in writing, before results exist. Metrics chosen after seeing results are worthless and examiners know it.

### 3.6.2 Retrieval metrics — definitions and worked examples

Notation: for query *q*, the system returns a ranked list; *rel(i)* = 1 if the result at rank *i* is relevant.

**Precision@K** — of the K returned, what fraction were relevant?

```
P@K = (number of relevant results in top K) / K
```

**Recall@K** — of the relevant items that exist, what fraction appeared in the top K?

```
R@K = (relevant results in top K) / (total relevant items)
```

In our gold set each query has one correct segment, so Recall@K reduces to a **hit rate**: did it appear in the top K, yes or no? Say this explicitly — otherwise a sharp examiner will ask whether you understand the difference.

**MRR (Mean Reciprocal Rank)** — how highly was the first correct result ranked?

```
MRR = (1/|Q|) · Σ_q  1 / rank_q      (0 if not retrieved)
```

**nDCG@K** — position-discounted gain, supporting graded relevance:

```
DCG@K  = Σ_{i=1..K}  rel(i) / log₂(i + 1)
nDCG@K = DCG@K / IDCG@K        (IDCG = DCG of the ideal ranking)
```

**Worked example.** Five queries; rank at which the correct segment appeared:

| Q | Rank | In top 5? | Reciprocal rank | DCG contribution (1/log₂(rank+1)) |
|---|---|---|---|---|
| 1 | 1 | ✅ | 1.000 | 1/log₂2 = 1.000 |
| 2 | 3 | ✅ | 0.333 | 1/log₂4 = 0.500 |
| 3 | not retrieved | ❌ | 0.000 | 0 |
| 4 | 2 | ✅ | 0.500 | 1/log₂3 = 0.631 |
| 5 | 1 | ✅ | 1.000 | 1.000 |

```
Recall@5  = 4/5 = 0.800
MRR       = (1.000 + 0.333 + 0.000 + 0.500 + 1.000) / 5 = 0.567
nDCG@5    = (1.000 + 0.500 + 0 + 0.631 + 1.000) / 5     = 0.626
```

**The metrics disagree in emphasis, and that is the point.** Recall looks respectable at 0.80 while MRR reveals that query 2's answer sat at rank three. Being able to explain that divergence is a strong viva answer; reporting only the flattering one is the kind of thing examiners probe for.

**Report Recall@5 and MRR.** Both are computable from binary judgements. Mention nDCG only if you actually grade relevance — do not promise it.

### 3.6.3 The statistics caution that will save you

With 20 queries, **one query moves Recall@5 by 0.05.** Worse, the uncertainty is larger than students expect. For a proportion *p* from *n* samples:

```
standard error = √( p(1−p) / n )

For p = 0.80, n = 20:   SE = √(0.8 × 0.2 / 20) = √0.008 ≈ 0.089
95% confidence interval ≈ 0.80 ± 1.96 × 0.089 ≈ 0.80 ± 0.175
                        ≈ [0.62, 0.98]
```

**Report it as `Recall@5 = 0.80 (n = 20, 95% CI ≈ [0.62, 0.98])`.**

Two consequences you must internalise:

1. **Never claim a difference between 0.80 and 0.85 is meaningful at n = 20.** It is one query.
2. If a panel member raises this, **agree immediately.** "You're right — with twenty queries the interval is wide, which is why we report it and why we do not claim significance for small differences" is a much better answer than a defence.

Larger n narrows the interval as √n, so 80 queries would roughly halve it. If you have time, growing the gold set is the single cheapest way to strengthen your results.

### 3.6.4 Generation metrics

**Do not use BLEU or ROUGE.** State why explicitly, because choosing metrics deliberately rather than by default is itself evidence of rigour: overlap metrics penalise a correct answer phrased differently, and reward a fluent but unsupported one. For RAG, phrasing is not the property under test — grounding is.

Use RAGAS-style dimensions, rated 1–5 by humans:

| Dimension | The rater's question | What a failure looks like |
|---|---|---|
| **Faithfulness** | Is every claim supported by the cited segment? | Answer states a fact the segment does not contain |
| **Answer relevance** | Does it address what was asked? | Correct and grounded, but answers a different question |
| **Context relevance** | Were the retrieved segments useful? | Retrieval returned noise; the model coped anyway |
| **Citation correctness** | Do `[n]` markers point at the supporting segments? | Right answer, wrong citation number |

Separating the last two is worth doing: it lets you attribute failure to *retrieval* versus *generation*, which is the diagnostic distinction you need when improving the system.

### 3.6.5 Designing the human study so it is credible

Five design choices, each with a reason:

1. **Raters:** at least three, including at least one external to the team. One rater is an opinion; three is data.
2. **Blinding:** when comparing configurations, raters must not know which produced which answer. Otherwise expectation contaminates the rating. Practically: shuffle outputs and label them A/B.
3. **Written rubric, agreed before rating.** Define each point on the 1–5 scale with an example. Without this, raters drift and scores are not comparable across sessions.
4. **Agreement:** at least two raters score a common subset. Report **percentage agreement**, or Cohen's κ if you want the stronger measure. **Reporting disagreement is what makes the numbers honest** — nobody believes three raters agreed perfectly.
5. **Report mean *and* range.** A mean of 4.0 from {4,4,4} and from {2,5,5} are entirely different findings, and only the range distinguishes them.

**A worked rubric anchor** — write one like this for each dimension:

> **Faithfulness.** 5 = every claim directly supported by the cited segment. 4 = all claims supported, but one is a reasonable inference rather than explicit. 3 = mostly supported, one unsupported minor detail. 2 = a central claim unsupported. 1 = contradicts the cited segment or invents content.

### 3.6.6 System performance

Report on a **stated reference machine** — CPU model, RAM, OS. Numbers without hardware are meaningless and an examiner may say so.

Report **median and worst case**, never best case. A p95 latency matters far more to a user than a best-case one.

| Measure | Target |
|---|---|
| Retrieval latency | < 1 s |
| End-to-end latency | < 15 s |
| PDF indexing | ≥ 1 page/s |
| Whisper WER on test clips | < 15% |
| Peak RSS | < available RAM with headroom |

### 3.6.7 Ablations — the cheapest route to rigour

An ablation removes or varies one component to show it matters. **Change one thing at a time**, hold the corpus and gold set fixed, and report the same metrics.

| Ablation | Variants | What it demonstrates |
|---|---|---|
| Chunk size | 150 / 300 / 600 words | The parameter was chosen, not guessed |
| Top-K | 3 / 5 / 10 | Precision/context trade-off; the lost-in-the-middle effect |
| **Cross-modal merge policy** | rank-based vs score-based | ⭐ That the modality gap is real *in your own data* |
| Overlap | 0 / 50 words | Whether boundary loss is real |
| OCR on/off for images | with / without | Whether the second image path earns its cost |

**The merge-policy ablation is the most valuable experiment in the entire project.** It takes an afternoon, it converts a cited claim into your own empirical finding, and it produces a result no other team will have. Run it in Chapter 12.

## 3.7 Threats to validity

A short subsection that markedly raises perceived rigour, because it shows you know what your evidence does *not* prove.

| Type | The question it asks | Your threat | Mitigation |
|---|---|---|---|
| **Internal** | Is the effect caused by what you claim? | Retrieval quality may reflect corpus properties rather than model capability | Ablations with corpus held fixed |
| **External** | Does it generalise? | 50–200 English files, one hardware configuration; may not hold at 10⁵ files, other languages, or noisier audio | State limits explicitly; claim nothing beyond them |
| **Construct** | Do the metrics measure what matters? | Recall@5 measures retrieval, not usefulness; faithfulness ratings are subjective | Report retrieval *and* answer metrics; publish the rubric |
| **Conclusion** | Is the sample large enough? | n = 20 gives a 95% CI of roughly ±0.175 | Report n and CI beside every figure; claim no small differences |
| **Bias** | Who made the test? | Gold set authored by the system's designers | External questions, reported separately |

## 3.8 Reproducibility

Rarely included in student reports, and it takes twenty minutes. Include it and you look like a researcher.

| What to record | Why |
|---|---|
| Exact model identifiers and versions (`llama3.2:3b`, `all-MiniLM-L6-v2`, `ViT-B-32/laion2b_s34b_b79k`) | "Llama 3.2" alone does not identify a quantization |
| `pip freeze > requirements.txt`, and the Python version | Library versions change behaviour |
| Random seeds; generation temperature | Generation is stochastic unless pinned |
| Hardware: CPU, RAM, OS | Latency numbers are meaningless without it |
| The corpus manifest — filenames with checksums | Proves the same data was used across ablations |
| The frozen gold set, committed to the repository | Proves it was not edited after seeing results |
| Date of every measurement | Models and libraries get updated |

State it in one sentence: *"All evaluation artefacts — corpus manifest, gold set, dependency versions, and configuration — are committed to the project repository at the commit corresponding to each reported result."*

---

# Part 4 — DECIDE

**4.1 Organising structure.** Thematic, using [Ch 3A](ch03a-annotated-bibliography.md)'s themes. If you must compress, merge 1+2 into "semantic representation and retrieval" and 10 into 7. **Never** compress by dropping Theme 9 (attribution) — it is the literature behind your fourth objective and the part most teams lack.

**4.2 How many sources.** 15–20 for the review; 20–25 for the final report. Every theme needs ≥ 2 sources; a theme with one looks like an afterthought.

**4.3 Which gap to claim.** The conjunctive one (§1.12.1 rows 2–3): integration under an offline constraint, speech as a first-class modality, provenance propagated rather than evaluated post hoc. **Do not claim algorithmic novelty.**

**4.4 Which decisions to formalise.** All seven ADRs. Five can cite literature; do so.

**4.5 What to defer.** Ablation *results* (the protocol is fixed today, the numbers come in Ch 12), per-module implementation detail, and the feedback log.

**4.6 The one thing to decide as a team, out loud.** Your answer to *"ColPali retrieves document pages as images — why didn't you do that?"* It is the sharpest question available about your architecture, and it deserves a real answer rather than an improvised one. (§1.12.3, last row.)

---

# Part 5 — BUILD: the day

## 5.1 Templates prepared

| File | Purpose |
|---|---|
| [`reports/literature-matrix.md`](../../reports/literature-matrix.md) | Search log, verification tracker, synthesis matrix, gap pressure-test |
| [`reports/methodology-draft.md`](../../reports/methodology-draft.md) | Full methodology, drafted, with `⟨FILL⟩` markers |
| [`docs/decisions/`](../decisions/) | ADR template plus 001 and 003 written out |
| [Ch 3A](ch03a-annotated-bibliography.md) | The annotated source list |
| [Ch 3B](ch03b-reading-and-citations.md) | Worked paper reading; IEEE reference for every entry type; Zotero workflow |

> **Rewrite everything in your own words.** You will be questioned on every sentence.

## 5.2 Schedule

| Time | Task | Who |
|---|---|---|
| 0:00–0:30 | Read Part 1 §§1.1–1.3, 1.11–1.12. Agree theme structure and gap claim. | All |
| 0:30–0:45 | Set up Zotero; create one collection per theme ([Ch 3B](ch03b-reading-and-citations.md)). | Member 3 |
| 0:45–1:45 | **Verify every citation in [Ch 3A](ch03a-annotated-bibliography.md)** against the actual source. Split three ways. Tick the tracker. | Parallel |
| 1:45–2:15 | ⭐ **Forward-citation search** (§1.6.2) on Lewis, MuRAG and ColPali, filtering `offline`, `local`, `multimodal`, `speech`. Log everything. Adjust the gap if needed. | Member 3 |
| 2:15–3:15 | Pass-2 reading. M1: RAG + Ovadia/Gekhman. M2: CLIP + modality gap. M3: Whisper + Liu verifiability. Write the §1.8.3 note for each. | Parallel |
| 3:15–4:15 | Fill the synthesis matrix. Write the review — one paragraph per theme, using §1.11's moves. **Include at least one taxonomy move.** | M1 leads |
| 4:15–5:15 | Write the methodology draft and the five remaining ADRs. | M2 leads |
| 5:15–5:45 | One editor merges, unifies voice, builds the comparison table. | One editor |
| 5:45–6:15 | Rubric §6.1; drill §6.2 questions. | All |

## 5.3 The two tasks nobody may skip

**The forward-citation search (1:45).** Everything else is recoverable. Discovering in the viva that your system was published in 2024 is not. Fifteen minutes.

**Citation verification (0:45).** One wrong venue found by an examiner casts doubt on every other number in your report. This is the cheapest credibility insurance available.

---

# Part 6 — CHECK

## 6.1 Rubric

Score 0–3. Below 42/60, revise.

| # | Criterion | Score |
|---|---|---|
| 1 | Organised thematically, not paper-by-paper | /3 |
| 2 | Multiple sources compared or contrasted within single sentences | /3 |
| 3 | At least one taxonomy move (§1.11.1) | /3 |
| 4 | Opening roadmap paragraph and closing pivot paragraph present | /3 |
| 5 | Every theme has ≥ 2 sources | /3 |
| 6 | Attribution literature (Theme 9) included | /3 |
| 7 | Embedding model choice justified with benchmark evidence | /3 |
| 8 | ColPali / screenshot-retrieval alternative acknowledged and addressed | /3 |
| 9 | Comparison table present with honest ⚠️ marks | /3 |
| 10 | Gap stated in four moves; conjunctive, not absolute-novelty | /3 |
| 11 | Gap pressure-tested against ≥ 4 counter-examples | /3 |
| 12 | Search log completed; forward-citation search documented | /3 |
| 13 | Every citation verified against the actual source | /3 |
| 14 | Published versions cited where they exist | /3 |
| 15 | Nothing patchwritten | /3 |
| 16 | Methodology names alternatives rejected, with reasons | /3 |
| 17 | ≥ 5 ADRs cite literature | /3 |
| 18 | Metrics defined with formulas and targets, before any results | /3 |
| 19 | Confidence interval or sample-size caution stated | /3 |
| 20 | Human study specifies raters, blinding, rubric, agreement | /3 |
| | **Total** | **/60** |

## 6.2 Forty questions

**On the review**
1. How did you find these papers? → §1.5 search log, snowballing, citation graphs. Show the log.
2. Which paper is most important to your work? → RAG for architecture; CLIP for the cross-modal capability.
3. Has anyone already built this? → MuRAG is closest; name three differences (offline, speech, provenance-as-requirement).
4. What is your gap in one sentence? → §1.12.2 moves 2 + 3.
5. Is your contribution novel? → **Integration under a constraint, not a new algorithm.** Say it plainly.
6. Why cite BM25, from 2009? → It is the baseline we argue against, and still better for rare exact strings.
7. What does the modality-gap paper actually say? → Image and text embeddings occupy separate regions; systematic, not noise; hence rank-based merging.
8. Which paper did you disagree with? → Any honest answer scores. Lost-in-the-Middle versus "just use long context" is a good one.
9. What is the difference between a preprint and a published paper, and why does it matter? → Peer review; cite the published version where one exists.
10. What are the three families of retrieval? → Lexical, dense, late-interaction (plus hybrid). §1.11.1.
11. Which theme was hardest to find literature for? → Chunking. See §3.3.2 — and it is why we ablate instead.

**On design choices**
12. Why RAG and not fine-tuning? → ADR-001, and cite Ovadia and Gekhman rather than asserting.
13. Doesn't fine-tuning teach the model your data? → Poorly, for facts; and Gekhman found fine-tuning on new knowledge can *increase* hallucination.
14. Why `all-MiniLM-L6-v2` and not BGE or E5? → MTEB position against parameter count under an 8 GB RAM budget.
15. Why ChromaDB and not FAISS? → ADR-004: embedded, metadata filtering for provenance; scale advantage irrelevant below 10⁵.
16. Why two collections? → ADR-003: different dimensionality, different spaces, CLIP's 77-token limit.
17. Why CLIP and not BLIP or SigLIP? → Symmetric retrieval objective; open weights; SigLIP noted as a future upgrade.
18. What is the modality gap and what bug does it cause? → Systematically lower text-image scores; naive score merging buries images.
19. Why transcription and not CLAP? → ADR-005: speech content is linguistic; timestamps required for citation.
20. **Why not ColPali — retrieve document pages as images?** → ⭐ Higher compute per page; no timestamped audio path; our OCR path gives exact-string retrieval. A legitimate alternative with a different trade-off.
21. Why 300-word chunks? → Fits the 256-token embedding limit; validated by ablation, not assumed.
22. Why is temperature low? → Faithfulness over variety in a citation-grounded system.
23. Why HNSW rather than exact search? → Architectural correctness and scalability; at our scale exact search would also work, and we say so.

**On evaluation**
24. How will you know it worked? → Recall@5 ≥ 0.80, MRR ≥ 0.65, cross-modal Recall@5 ≥ 0.70, faithfulness ≥ 4/5.
25. Why Recall@5 *and* MRR? → Finding versus ranking. Give the §3.6.2 worked example where they diverge.
26. What is MRR, precisely? → Mean of 1/rank of the first relevant result; 0 if not retrieved.
27. Why not nDCG? → It needs graded relevance judgements; our gold set is binary. We say so rather than promising it.
28. Why not BLEU or ROUGE? → They penalise correct paraphrase and reward fluent unsupported text.
29. Who wrote the test questions — isn't that biased? → Yes, and we disclose it. External questions in Ch 12, reported separately.
30. How many questions, and is that enough? → n = 20; 95% CI ≈ ±0.175. We report the interval and claim no small differences.
31. ⭐ *If asked "0.80 versus 0.85 — is that an improvement?"* → **No.** At n = 20 that is one query, well inside the interval.
32. How do you avoid tuning to the test set? → Gold set written before implementation and frozen before measurement.
33. How do you separate retrieval failure from generation failure? → Context relevance versus faithfulness are rated separately.
34. How many raters, and how do you know they agree? → ≥ 3, one external, blinded, shared subset with agreement reported.
35. What is the single most valuable experiment you will run? → Rank-based versus score-based merging — it tests the modality gap in our own data.

**On honesty and limits**
36. What are the threats to validity? → §3.7's five rows.
37. What is the weakest part of your evaluation? → Small n and self-authored questions; mitigation is external testers.
38. What would make your conclusions wrong? → Corpus-specific effects; hence fixed-corpus ablations.
39. Is your system reproducible? → §3.8 — pinned model versions, `requirements.txt`, seeds, corpus manifest, frozen gold set, all committed.
40. What would you do with three more months? → Advanced RAG: reranking, query rewriting, Self-RAG-style verification, ColPali-style page retrieval, and video.

## 6.3 Failure modes

| Failure | Why it costs | Fix |
|---|---|---|
| Paper-by-paper paragraphs | Reads as a reading list | Synthesis matrix; write down columns (§1.10) |
| No gap statement | The review does not justify the project | Four-move formula (§1.12.2) |
| Gap claims absolute novelty | One counter-example destroys it | Claim integration under constraint |
| Missing the attribution literature | Objective O4 has no theoretical grounding | Theme 9 — search "attribution", not "citation" |
| Embedding model unjustified | "Why this model?" has no answer | MTEB evidence (§1.1.1) |
| Unaware of ColPali/DSE | A sharp examiner finds the alternative you did not consider | §1.12.3 last row |
| Citing surveys for primary facts | Signals you did not read the originals | Trace to primary (§1.7.5) |
| Citing blogs as evidence | Not evidence | Primary sources; docs for tools |
| Preprint cited when published version exists | Reads as careless | Check every one (§1.7.3) |
| Patchwritten paraphrase | Plagiarism even when cited | Close the source, then write (§1.13.2) |
| Methodology as a parts list | No "why", no marks | Alternatives + criteria + justification (§3.3) |
| Metrics chosen after results | Worthless, and detectable | Fix targets today, in writing |
| Claiming 0.85 > 0.80 at n = 20 | Statistically indefensible | Report CIs (§3.6.3) |
| No threats-to-validity section | Suggests you cannot see your own limits | §3.7 |
| No reproducibility statement | Results cannot be checked | §3.8 — twenty minutes |
| Unverified references | One error taints everything | Verify all today (§5.3) |

## 6.4 Day 3 completion checklist

- [ ] Zotero set up; one collection per theme; all sources captured
- [ ] Search log: ≥ 7 distinct queries across ≥ 3 sources, with result counts
- [ ] ⭐ Forward-citation search on Lewis, MuRAG and ColPali completed and logged
- [ ] Every citation verified against the actual source; published versions preferred
- [ ] Six papers read to Pass 2 with §1.8.3 notes completed
- [ ] Synthesis matrix filled; gap identified from the matrix, not assumed
- [ ] Review written thematically, 15–20 sources, ≥ 1 taxonomy move, opening and closing paragraphs present
- [ ] Attribution literature (Theme 9) included
- [ ] Embedding model choice justified with benchmark evidence
- [ ] ColPali answer agreed as a team
- [ ] Comparison table built with honest ⚠️ marks
- [ ] Gap stated in four moves, pressure-tested against ≥ 4 counter-examples
- [ ] Methodology draft: all ten subsections
- [ ] Seven ADRs written; ≥ 5 cite literature
- [ ] Evaluation protocol fixed in writing: formulas, targets, n, CI, rater count, rubric, blinding
- [ ] Threats to validity written
- [ ] Reproducibility statement written
- [ ] One editor has unified the voice
- [ ] Rubric §6.1 ≥ 42/60
- [ ] All forty questions drilled

---

**Next:** [Chapter 4 — Timeline, Team & Modular Work Split](ch04-timeline-and-team-split.md) (Day 4) — Presentation #2, the Gantt chart, module decomposition, interface contracts, and how three people work in parallel without blocking one another.
