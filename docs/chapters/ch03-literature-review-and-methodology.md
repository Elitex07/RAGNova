# Chapter 3 — Literature Review & Methodology (Day 3)

> **Deliverables today:** a **literature review** (15–20 sources, thematically organised, ending in a defended gap statement) and a **methodology section** (design rationale for every major decision, plus the evaluation protocol). Both feed directly into Day 4's presentation and the Day 14 report.
>
> **Prerequisites:** [Chapter 1](ch01-objective-and-problem-identification.md) (you need the objectives and the stack) and [Chapter 2](ch02-synopsis-and-presentation.md) (you need the academic writing mechanics — this chapter assumes them and does not repeat them).
>
> **Why this day is not optional.** A literature review is not a ritual to satisfy an examiner. It is the day you find out whether your design decisions are defensible. Three of the choices in Chapter 1's stack table are non-obvious, and today is when you learn *why* they are right — or discover they are wrong while it still costs nothing to change them.

---

## How to read this chapter

| Part | What it does | Time |
|---|---|---|
| **Part 1 — LEARN (method)** | What a literature review is for, where to find papers, how to search, how to judge a source, how to read a paper in three passes, how to synthesise rather than summarise, how to find and phrase a gap, and how to cite without plagiarising. | ~75 min |
| **Part 2 — THE SURVEY** | The actual annotated literature for RAGNova: seven themes, ~30 sources, each with *what problem it solved*, *the key idea*, and *what we take from it*. This is your raw material. | ~90 min |
| **Part 3 — LEARN (methodology)** | What "methodology" means in an engineering project, how to write design rationale, Architecture Decision Records, and how to design an evaluation that can actually fail. | ~45 min |
| **Part 4 — DECIDE** | Organising structure, source count, which gap to claim, which decisions to formalise. | ~20 min |
| **Part 5 — BUILD** | Time-boxed day with templates. | ~4 hours |
| **Part 6 — CHECK** | Rubric, twenty-five questions, failure modes. | ~40 min |

**Learning outcomes.** You will be able to: construct a search strategy and log it; snowball a reference list forwards and backwards; judge whether a source is worth citing; read a paper in three passes at increasing depth; build a synthesis matrix; write thematically organised prose that argues rather than lists; phrase a gap statement you can defend; write design rationale that names the alternatives you rejected and why; and design an evaluation protocol capable of showing that you failed.

---

# Part 1 — LEARN: the method

## 1.1 What a literature review is actually for

Students are told to "do a literature review" without being told what it *does*. It does four distinct jobs, and knowing which sentence is doing which job is how you write one that reads as an argument instead of a list.

| Job | What it proves | What it looks like in your text |
|---|---|---|
| **1. Establish the foundation** | You know the field's core ideas and did not reinvent them badly | "Dense retrieval replaced lexical matching following [2], [3]." |
| **2. Justify your choices** | Your design decisions rest on evidence, not on the first tutorial you found | "CLIP [5] is selected because it is trained contrastively across modalities, unlike unimodal encoders." |
| **3. Identify the gap** | Your project is not already done by someone else | "However, existing multimodal RAG systems assume cloud-hosted inference..." |
| **4. Set the evaluation bar** | You know how systems like yours are normally measured | "Retrieval is conventionally evaluated by Recall@k and MRR [21]." |

**Job 2 is the one students skip and examiners care about most.** Every non-obvious choice in Chapter 1's stack table should be traceable to a citation. When a panel asks "why CLIP and not BLIP?", the answer "because [5] and [12] differ in objective, and ours needs a symmetric retrieval space" is worth ten times "because a tutorial used it."

**Job 4 is the one that saves you on Day 14.** If your evaluation metrics come from the literature, nobody can argue you invented favourable ones.

## 1.2 What a literature review is *not*

Three anti-patterns, in ascending order of how common they are.

**❌ An annotated bibliography.** A list of paragraphs, one per paper, each summarising that paper. No connections, no argument. This is the single most common student literature review and it reads as exactly what it is — a reading list with prose formatting.

**❌ A summary chain.** *"Smith et al. did X. Then Jones et al. did Y. Then Patel et al. did Z."* The papers are in order but nothing is compared, contrasted, or judged. The reader learns what exists but not what it means.

**❌ A citation shield.** Sentences padded with references to look rigorous, where the citation does not actually support the claim. Examiners test this by picking one and asking what it says. Do not cite anything you have not at minimum read the abstract and conclusion of.

**✅ What it should be:** an argument, organised by *idea* rather than by *paper*, in which multiple sources appear in a single sentence because they agree, disagree, or build on one another — ending at a gap that your project fills.

The structural test: **if you could reorder your paragraphs without damaging the meaning, you have written a list, not a review.**

## 1.3 Types of review, and which one you are writing

| Type | What it is | Effort | Use when |
|---|---|---|---|
| **Narrative / traditional** | Thematically organised discussion of relevant work, selected by judgement | Days | ✅ **This is yours** — standard for a B.Tech project |
| **Systematic** | Exhaustive search with pre-registered inclusion/exclusion criteria, PRISMA flow diagram, reproducible | Weeks–months | Formal research; overkill here |
| **Scoping** | Maps the breadth of a field without depth | Weeks | Early-stage research direction |
| **Meta-analysis** | Statistical pooling of results across studies | Months | Empirical sciences; not applicable |

You are writing a **narrative review**. But borrow one habit from systematic reviews: **keep a search log** (§1.5.4). It costs nothing, and when a panel asks "how did you find these papers?", the answer "we searched these terms in these databases, and here is the log" is dramatically stronger than "we googled."

## 1.4 Where to find papers — and what each source is good for

Not all sources are equal. Each has a specific strength; using the wrong one wastes hours.

| Source | URL | What it is best at | Watch out for |
|---|---|---|---|
| **Google Scholar** | scholar.google.com | Broad first sweep; **forward citation search** ("Cited by") | Indexes low-quality venues alongside good ones; no quality filter |
| **arXiv** | arxiv.org | Newest ML work, months before publication; free full text | **Not peer-reviewed** — see §1.7.3 |
| **Semantic Scholar** | semanticscholar.org | Citation graph, influential-citation counts, AI-generated TLDRs | TLDRs are convenient but not a substitute for reading |
| **Papers with Code** | paperswithcode.com | Finds papers *with working implementations*; leaderboards | Benchmark-centric; misses systems work |
| **Connected Papers** | connectedpapers.com | Visual graph of a paper's neighbourhood — excellent for discovering what you missed | Free tier limits graphs per month |
| **ACL Anthology** | aclanthology.org | Every NLP paper (ACL, EMNLP, NAACL, TACL), free, authoritative | NLP only |
| **IEEE Xplore / ACM DL** | ieeexplore.ieee.org · dl.acm.org | Peer-reviewed venues; the citation format your report uses | Often paywalled — use your institution's access |
| **Official documentation** | *(project sites)* | The ground truth for tools you actually use | Cite the docs, never a tutorial blog |

**The practical workflow that works:** start on Google Scholar to find the two or three obviously-central papers, read those, then use **Connected Papers** or Semantic Scholar's citation graph on one of them to discover the neighbourhood you did not know existed. That second step is where the non-obvious references come from, and it takes fifteen minutes.

> **Getting paywalled papers legitimately:** try (1) your institution's library proxy, (2) arXiv — most ML papers have a free preprint, (3) the author's personal or lab website, which almost always hosts a PDF, (4) emailing the author, who will nearly always send it and is often pleased to be asked.

## 1.5 How to search properly

### 1.5.1 Build the query from concepts, not sentences

Do not type your project title into a search box. Decompose the problem into concepts, list synonyms for each, and combine.

| Concept | Synonyms and near-terms to try |
|---|---|
| Retrieval-augmented generation | RAG · retrieval-augmented LM · knowledge-grounded generation · open-domain QA |
| Semantic search | dense retrieval · vector search · neural information retrieval · embedding-based retrieval |
| Cross-modal | multimodal retrieval · image-text retrieval · vision-language · text-to-image search |
| Speech search | spoken content retrieval · ASR · speech-to-text · spoken document retrieval |
| Offline / local | on-device inference · edge deployment · local LLM · quantized inference · privacy-preserving |
| Citations | attribution · groundedness · provenance · source attribution · faithfulness |

Then combine with boolean operators:

```
("retrieval-augmented generation" OR RAG) AND multimodal AND (offline OR "on-device" OR local)
"cross-modal retrieval" AND (CLIP OR "vision-language") AND "vector database"
"spoken content retrieval" AND embedding
```

Google Scholar supports quotes for exact phrases, `-` for exclusion, and `author:` / `source:` filters. Use the year filter to separate foundations (pre-2021) from current practice (2023+).

### 1.5.2 The three-generation rule

For each core concept, deliberately find:

1. **The foundational paper** — the one that introduced the idea (often 2017–2021, heavily cited)
2. **A significant extension** — what people did next
3. **A recent survey or system paper** (2023–2025) — what the current consensus is

This produces a review with historical depth *and* currency, which reads far better than a pile of papers all from the same eighteen months. It also gives you the "X established A, Y extended it to B, current systems do C" structure that §1.11 needs.

### 1.5.3 Snowballing — where most of your good references come from

Once you have one genuinely central paper, you can walk the citation graph in both directions. This is faster and higher-yield than searching.

**Backward snowballing** — read the paper's *reference list*. What did it build on? This finds foundations. If four papers you already like all cite the same fifth paper, that fifth paper is foundational and you must read it.

**Forward snowballing** — on Google Scholar, click **"Cited by"** under the paper. This finds everything published *since* that builds on it, sorted by citation count. **This is how you find out whether someone has already built your project.**

> **Do this specific search today, seriously:** open the Lewis et al. RAG paper on Google Scholar, click "Cited by", and search within those results for `multimodal` and for `offline`. Whatever you find is either (a) a strong reference, or (b) evidence that your gap statement needs adjusting. Both outcomes are valuable, and finding out on Day 3 is infinitely better than finding out in the viva.

Stop snowballing when you reach **saturation** — when new searches keep returning papers you have already seen. That is the signal you have covered the area, and it usually arrives faster than students expect.

### 1.5.4 Keep a search log

A simple table, maintained as you go. Ten minutes of work, and it converts "we found some papers" into a defensible method.

| Date | Source | Query | Results scanned | Kept | Notes |
|---|---|---|---|---|---|
| ⟨date⟩ | Google Scholar | `"multimodal RAG" offline` | 40 | 3 | Most results cloud-based — supports our gap |
| ⟨date⟩ | Semantic Scholar | Forward citations of Lewis 2020 | 60 | 5 | Found Self-RAG, CRAG |

The template lives in [`reports/literature-matrix.md`](../../reports/literature-matrix.md).

## 1.6 How to judge whether a source is worth citing

Not everything you find deserves a place in your reference list. Five tests, applied in about ninety seconds per paper.

### 1.6.1 Venue

Where it was published is the fastest quality proxy.

| Tier | Examples | Treatment |
|---|---|---|
| **Top ML/NLP conferences** | NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, CVPR, ICCV, ECCV | Cite confidently |
| **Strong journals** | IEEE TPAMI, TACL, JMLR, ACM Computing Surveys | Cite confidently |
| **Reputable secondary venues** | ICASSP, SIGIR, ECIR, WACV, workshop papers at top venues | Fine; note it is a workshop paper if it is |
| **arXiv preprint only** | — | Usable — see §1.6.3 |
| **Unknown journal, high fee, promises fast review** | — | ❌ Predatory. Do not cite |
| **Blog posts, Medium, YouTube** | — | ❌ Not citable as evidence. Useful for *learning*, never as a source |

> **In machine learning specifically, conferences outrank journals.** This surprises students from other disciplines. NeurIPS and ACL papers are fully peer-reviewed and are the primary publication venue for the field. Do not downgrade a paper for being "only" a conference paper.

### 1.6.2 Citations, read correctly

Citation count is a signal, not a verdict, and it must be normalised by age.

- A 2017 paper with 100,000 citations is foundational (Transformer).
- A 2024 paper with 50 citations may be excellent — it has had no time.
- A 2015 paper with 3 citations is probably not worth your attention.

Rough heuristic: **citations per year since publication.** Over ~100/year is a landmark; over ~20/year is solid; under ~5/year needs another justification for inclusion.

### 1.6.3 Preprints: usable, with a caveat

Much of the most important ML work appears on arXiv months or years before formal publication, and some never gets formally published. Refusing to cite preprints would exclude genuinely central work.

**The rule:** cite preprints when the work is clearly influential (high citations, from a known lab, with released code and reproductions), and **always cite the published version if one exists**. Check for it — many papers you find on arXiv were later published at NeurIPS or ACL, and citing the arXiv version when a peer-reviewed version exists looks careless.

### 1.6.4 Primary versus secondary

Always trace a claim to its **primary source** — the paper that actually did the work.

If you learned about CLIP from a survey, cite CLIP, not the survey — *unless* you are citing the survey's own contribution (its taxonomy, its comparative analysis). Citing a survey for a fact the survey itself cites is a signal you did not read the original.

### 1.6.5 The "can I state its contribution in one sentence?" test

Before adding a paper to your reference list, say aloud what it contributed. If you cannot, you have not read it enough to cite it, and a panel question will expose that in ten seconds.

## 1.7 How to read a paper — the three-pass method

You do not read a research paper the way you read a textbook. Reading twenty papers cover-to-cover is impossible in a day and unnecessary; the standard technique is Keshav's **three-pass method**, and it is the single highest-leverage skill in this chapter.

### Pass 1 — Five to ten minutes. Decide whether to continue.

Read only: **title, abstract, introduction, section headings, conclusion, figures**. Skip everything else, including all mathematics.

Answer five questions:
1. **Category** — is this a new technique, a system, an analysis, or a survey?
2. **Context** — what other work does it relate to?
3. **Correctness** — do the assumptions look reasonable?
4. **Contribution** — what is the main claim?
5. **Clarity** — is it well written?

After Pass 1 you should be able to state the paper's contribution in one sentence. **Most papers stop here** — that is the point. Perhaps 60% of what you find will be Pass-1-only, and that is a successful outcome, not a failure.

### Pass 2 — About an hour. Understand the content.

For papers that survive Pass 1 and are directly relevant. Read the whole thing carefully but **skip proofs and detailed derivations**. Pay close attention to figures, tables, and axis labels — in ML papers the figures usually carry the argument.

Extract, in writing:
- The **problem** it solves
- The **key idea** in your own words (this is the test — if you cannot paraphrase it, you have not understood it)
- The **method**, at a level you could explain on a whiteboard
- The **results** and, critically, **what was measured**
- The **limitations** the authors admit to

Mark unread references you now want.

For RAGNova, roughly six to eight papers deserve Pass 2 — the ones directly underpinning your architecture: RAG, Sentence-BERT, CLIP, Whisper, HNSW, and one multimodal RAG paper.

### Pass 3 — Several hours. Reproduce the reasoning.

Attempt to reconstruct the work: challenge every assumption, follow the derivations, ask what you would have done differently. **You need this for at most one or two papers** — probably CLIP and the RAG paper, since those are the two an examiner is most likely to probe.

### What to write down (do this immediately, not later)

For every paper reaching Pass 2, complete this note before moving on. Memory decays fast, and re-reading a paper because you took no notes is the most avoidable time loss of Day 3.

```markdown
**Citation:** Author et al., "Title", Venue, Year
**Theme:** (which of your review's themes it belongs to)
**Problem:** what was broken before this
**Key idea (own words):** ...
**Method:** ...
**Results / what was measured:** ...
**Limitations (stated by authors):** ...
**Relevance to RAGNova:** what we take, what we reject, and why
**Quotable claim + page:** (for a fact you may need to cite precisely)
```

That last field — *relevance to RAGNova* — is what turns reading into a literature review. A note without it is a summary; a note with it is an argument fragment.

## 1.8 The synthesis matrix — the tool that converts notes into prose

The mechanical bridge between "twenty sets of notes" and "an argument organised by theme" is a **synthesis matrix**: papers as rows, themes as columns.

| Paper | Dense retrieval | Cross-modal | Generation & grounding | Efficiency | Offline |
|---|---|---|---|---|---|
| Sentence-BERT [2] | ✅ core | — | — | ✅ small model | — |
| CLIP [5] | — | ✅ core | — | — | ✅ runs locally |
| Lewis RAG [4] | ✅ uses DPR | — | ✅ core | — | ❌ assumes server |
| HNSW [7] | — | — | — | ✅ core | ✅ embedded |

**Read the matrix down a column and you have written a paragraph.** The "Cross-modal" column becomes your cross-modal paragraph, citing everything with a mark in it. This is the concrete technique that prevents the paper-by-paper anti-pattern of §1.2, because you are physically organised by idea rather than by source.

**Read across a row** and you see how one paper contributes to several themes — which is how a single citation ends up appearing in three different paragraphs, exactly as it should.

**A column with only one mark** signals either a thin theme you should merge, or a genuine gap. **A column with no marks in the "Offline" sense** is precisely how you discover your gap statement empirically rather than by assertion.

The template is in [`reports/literature-matrix.md`](../../reports/literature-matrix.md).

## 1.9 Synthesis versus summary — with a worked before/after

This is the difference between a pass and a distinction. Look at the same content written both ways.

**❌ Summary (paper-by-paper):**

> Reimers and Gurevych [2] proposed Sentence-BERT, which modifies BERT to produce sentence embeddings. Karpukhin et al. [3] proposed Dense Passage Retrieval, which uses dense vectors for retrieval. Lewis et al. [4] proposed RAG, which combines retrieval with generation. Radford et al. [5] proposed CLIP, which links images and text.

Four sentences, four papers, zero connections. The reader learns that these things exist and nothing about how they relate. Note also that every sentence has the same shape — a strong smell of the anti-pattern.

**✅ Synthesis (idea-by-idea):**

> The shift from lexical to dense retrieval rests on the observation that semantic similarity can be expressed as geometric proximity. Sentence-BERT [2] made this practical by fine-tuning transformer encoders so that sentence-level vectors are directly comparable under cosine similarity, and Dense Passage Retrieval [3] demonstrated that such representations outperform BM25 on open-domain question answering — establishing dense retrieval as the default for semantic search. Lewis et al. [4] then coupled a dense retriever to a generative model, showing that conditioning generation on retrieved evidence both improves factual accuracy and, crucially for our purposes, renders the evidence available for attribution. This grounding property is what makes citation possible at all; it is a consequence of the architecture rather than a presentation-layer addition.
>
> Extending the same geometric principle across modalities required a shared representation space. CLIP [5] achieved this by training image and text encoders jointly under a contrastive objective over large-scale caption data, such that an image and its description occupy nearby positions in one space. Cross-modal retrieval thereby reduces to the same nearest-neighbour operation as unimodal retrieval — a unification we exploit directly.

The second version has the **same citations** but is organised by *idea*. Each paper appears because it advances the argument. The final sentence of each paragraph does work: it connects the literature to *our* design.

### Five moves that create synthesis

Use these verbs and constructions deliberately:

| Move | Signal phrases | Example |
|---|---|---|
| **Agreement** | "Both [2] and [3] find..." · "Consistent with [4]..." | Groups papers into a position |
| **Contrast** | "Whereas [5] optimises X, [12] targets Y" | Shows you can distinguish, not just list |
| **Chronological development** | "[2] established... subsequently [4] extended..." | Shows a field maturing |
| **Methodological grouping** | "Approaches divide into A [2],[3] and B [5],[6]" | Creates a taxonomy — very strong |
| **Gap identification** | "However, none of [4]–[6] address..." | The move that justifies your project |

**The taxonomy move is the most impressive of the five.** If you can say "existing approaches fall into three families, and here is the trade-off each makes," you have demonstrated genuine command of the area — far more than any amount of individual summarising.

## 1.10 Finding and phrasing the gap

The gap is the load-bearing sentence of your entire review. Everything before it exists to make it credible.

### 1.10.1 Types of gap — pick the honest one

| Gap type | Claim | Risk |
|---|---|---|
| **Nobody has done X** | Genuine novelty | ⚠️ Usually false and easily disproved. Avoid unless certain |
| **X exists but not under constraint C** | ✅ **Ours** — multimodal RAG exists, but not fully offline | Low, and easy to defend |
| **X and Y exist separately but not integrated** | ✅ **Also ours** — cross-modal retrieval and cited RAG rarely combined | Low |
| **X exists but is not accessible/reproducible** | Engineering and documentation contribution | Modest but honest |
| **X has not been evaluated in setting S** | Empirical contribution | Requires solid evaluation |

**Your gap combines rows 2 and 3**, and both are safe because they are *conjunctive* claims about combination rather than absolute claims about novelty. That distinction matters: "nobody has built a multimodal RAG system" is false and will be destroyed in the viva. "Multimodal RAG systems typically assume cloud-hosted inference, and cross-modal retrieval is rarely bidirectional in systems that also provide citation transparency" is true, specific, and defensible.

### 1.10.2 How to phrase it

Four-move formula:

1. **Acknowledge what exists** — "Multimodal RAG has been demonstrated [MuRAG, others]."
2. **Name the specific limitation** — "However, these systems assume cloud-hosted embedding and generation services."
3. **State why it matters** — "This precludes deployment on confidential corpora and in disconnected environments."
4. **State your contribution, modestly** — "This work integrates these components under a strict offline constraint, with citation transparency as a first-class design requirement."

Note what move 4 does *not* say. It does not claim a new algorithm. **Your contribution is integration and constraint satisfaction, and that is a legitimate engineering contribution — say it plainly.** Overclaiming novelty is the fastest way to lose a viva; claiming exactly what you did, and defending it, is the fastest way to win one.

### 1.10.3 Pressure-test your gap before you commit

Ask, as a team:
- If a panel member says "but system Z does this" — what is our answer? (Have one for the obvious candidates: ChatGPT with file upload, LangChain demos, NotebookLM.)
- Did we actually search for prior work that closes our gap? (§1.5.3's forward-citation search is the evidence.)
- Is our gap *narrow enough to be true* and *broad enough to be interesting*?

## 1.11 Citing without plagiarising

### 1.11.1 The rule

**Cite whenever an idea, a number, a method, or a phrasing is not your own.** Common knowledge in the field ("neural networks consist of layers") does not need a citation; anything specific does.

### 1.11.2 Paraphrase versus quote

In engineering writing, **direct quotation is rare** — reserve it for a definition so precise that rewording would damage it. Paraphrase everything else.

A real paraphrase changes both **words and structure**, not just words:

| | Text |
|---|---|
| **Original** | "We train an image encoder and a text encoder jointly to predict the correct pairings of a batch of (image, text) training examples." |
| ❌ **Patchwriting** *(this is plagiarism)* | "They train an image encoder and text encoder together to predict the right pairings of a batch of (image, text) examples [5]." |
| ✅ **Genuine paraphrase** | "CLIP's training objective is contrastive: within each batch, the model must identify which caption belongs to which image, which forces matched pairs into proximity within a shared space [5]." |

Patchwriting — swapping a few synonyms while retaining the original sentence structure — **counts as plagiarism** even with a citation attached. The reliable technique: read the passage, close it, wait a moment, then write what it means from memory in your own sentence shape. If you find yourself looking back and forth while typing, you are patchwriting.

### 1.11.3 Self-check before submission

- [ ] Every claim about prior work carries a citation
- [ ] Every citation in the text appears in the reference list, and vice versa
- [ ] References are numbered in **order of first appearance** (IEEE)
- [ ] Every reference verified against the actual paper — exact venue, year, author list
- [ ] Nothing is patchwritten
- [ ] You have read at least abstract + conclusion of everything cited
- [ ] Run through your institution's similarity checker if one is available

---

# Part 2 — THE SURVEY: RAGNova's literature, annotated

> **How to use this part.** This is *raw material*, not text to paste. Each entry gives the citation, the problem it solved, its key idea, and — the field that matters — **what RAGNova takes from it**. Your job today is to read the ones marked **[Pass 2]**, verify every citation, and write your own synthesis using the techniques in §1.9.
>
> **⚠️ Verify every entry independently.** Venue names, years and author lists must be exact. Check on the ACL Anthology, the publisher's site, or arXiv before it enters your reference list. An incorrect citation is worse than a missing one.

## Theme 1 — Representation: how meaning became geometry

| # | Source | Problem it solved | Key idea | What RAGNova takes |
|---|---|---|---|---|
| 1 | Mikolov et al., "Efficient Estimation of Word Representations in Vector Space," ICLR Workshop, 2013 | Words as one-hot vectors carried no semantic relationships | Distributional hypothesis: predict a word from its context, and semantically similar words acquire nearby vectors | The historical origin of "meaning as direction." Cite for background only |
| 2 | Vaswani et al., "Attention Is All You Need," NeurIPS, 2017 | Recurrent models processed sequences serially and lost long-range dependencies | Self-attention lets every token attend to every other; fully parallel | The architecture beneath *every* model we use — LLM, embedder, CLIP, Whisper |
| 3 | Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding," NAACL, 2019 | Word vectors were context-independent — "bank" had one vector | Bidirectional pretraining yields context-dependent token representations | The encoder family our embedding model descends from |
| 4 | **Reimers & Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," EMNLP-IJCNLP, 2019** **[Pass 2]** | BERT's raw outputs are poor for sentence similarity; comparing all pairs was computationally infeasible | Siamese/triplet fine-tuning plus mean pooling produces sentence vectors directly comparable by cosine similarity | **Direct justification for `all-MiniLM-L6-v2`.** Cite when explaining why our text embeddings work |

**Synthesis hook for your prose:** entries 1→4 form a clean chronological arc — from context-free word vectors, to contextual token vectors, to comparable sentence vectors. That arc is a ready-made opening paragraph.

## Theme 2 — Retrieval: from keywords to vectors

| # | Source | Problem it solved | Key idea | What RAGNova takes |
|---|---|---|---|---|
| 5 | Robertson & Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond," *Foundations and Trends in IR*, 2009 | Formalising lexical relevance ranking | Term frequency and inverse document frequency with length normalisation | The **baseline we argue against** — and the method still superior for rare exact strings |
| 6 | **Karpukhin et al., "Dense Passage Retrieval for Open-Domain Question Answering," EMNLP, 2020** **[Pass 2]** | Lexical retrieval fails on paraphrase in QA | Dual-encoder trained on question–passage pairs; dense vectors beat BM25 substantially | Empirical evidence that dense retrieval outperforms keywords — **the citation behind Objective O2** |
| 7 | **Malkov & Yashunin, "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs," IEEE TPAMI, vol. 42, no. 4, 2020** **[Pass 2]** | Exact nearest-neighbour search scales linearly and becomes infeasible | Multi-layer proximity graph; greedy descent through long-range then short-range links; ~O(log N) | **The algorithm inside ChromaDB.** Cite when discussing scalability |
| 8 | Johnson, Douze & Jégou, "Billion-Scale Similarity Search with GPUs," *IEEE Trans. Big Data*, 2021 | Similarity search at industrial scale | IVF and product quantization, GPU-accelerated (FAISS) | The **alternative we rejected** — cite when justifying ChromaDB over FAISS |
| 9 | Cormack, Clarke & Buettcher, "Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods," SIGIR, 2009 | Combining several ranked lists into one | Fuse by reciprocal rank rather than raw score | **Directly relevant to our modality-gap problem** (§Theme 3) and to optional hybrid search |
| 10 | Thakur et al., "BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models," NeurIPS Datasets & Benchmarks, 2021 | Retrieval models were evaluated on single datasets and overfit them | Standardised zero-shot benchmark across 18 datasets | Where our **metric definitions** (Recall@k, nDCG) come from |

## Theme 3 — Cross-modal: one space for pictures and words

| # | Source | Problem it solved | Key idea | What RAGNova takes |
|---|---|---|---|---|
| 11 | **Radford et al., "Learning Transferable Visual Models From Natural Language Supervision," ICML, 2021 (CLIP)** **[Pass 2 + Pass 3]** | Vision models needed fixed label sets and manual annotation; image and text vectors were incomparable | Contrastive training on ~400M image–caption pairs; N×N in-batch similarity matrix with the diagonal maximised, producing a **shared** embedding space | **The entire basis of Objective O3.** The most important paper in your review — expect questions |
| 12 | Cherti et al., "Reproducible Scaling Laws for Contrastive Language-Image Learning," CVPR, 2023 (OpenCLIP) | CLIP's weights and training data were not fully open | Open reproduction on LAION; released checkpoints | **The implementation we actually use.** Cite alongside [11] |
| 13 | **Liang et al., "Mind the Gap: Understanding the Modality Gap in Multi-modal Contrastive Representation Learning," NeurIPS, 2022** **[Pass 2]** | Unexplained: image and text embeddings occupy *separate* regions despite joint training | The gap arises from initialisation and is preserved by the contrastive objective; it is systematic, not noise | **Direct justification for our rank-based merge** (Ch 1 §1.7.3). This citation converts an implementation hack into a literature-grounded design decision — one of the strongest moves available to you |
| 14 | Li et al., "BLIP: Bootstrapping Language-Image Pre-training," ICML, 2022 | CLIP retrieves but cannot generate captions or answer about images | Combines contrastive and generative objectives; caption bootstrapping | The **alternative we rejected** — heavier, and we need symmetric retrieval, not captioning |
| 15 | Zhai et al., "Sigmoid Loss for Language Image Pre-Training," ICCV, 2023 (SigLIP) | CLIP's softmax loss requires very large batches | Pairwise sigmoid loss; better at small batch sizes | Note as a **future-work upgrade path** — shows currency without committing you |

**Why Theme 3 is the strongest part of your review.** Most student multimodal projects cite CLIP and stop. Citing [13] as well proves you understand a *known failure mode* of the technique you adopted and designed around it deliberately. Make sure this appears in your review and your Day 4 slides.

## Theme 4 — Speech: making audio searchable

| # | Source | Problem it solved | Key idea | What RAGNova takes |
|---|---|---|---|---|
| 16 | **Radford et al., "Robust Speech Recognition via Large-Scale Weak Supervision," ICML, 2023 (Whisper)** **[Pass 2]** | ASR systems were brittle across accents, noise and domains, and needed per-domain fine-tuning | Encoder–decoder transformer trained on ~680k hours of weakly supervised multilingual audio; zero-shot robustness | **Objective O1's audio pipeline** and the spoken-query feature. Cite for timestamped segment output |
| 17 | Elizalde et al., "CLAP: Learning Audio Concepts from Natural Language Supervision," ICASSP, 2023 | Audio had no CLIP-equivalent shared space | Contrastive audio–text pretraining | **The alternative we rejected.** Excellent for environmental sound, weaker for the semantics of speech — cite to justify the transcription bridge |
| 18 | Smith, "An Overview of the Tesseract OCR Engine," ICDAR, 2007 | Extracting printed text from images | Classical OCR pipeline | Justifies the **OCR path** complementing CLIP: CLIP knows an image *looks like* an invoice; OCR reads the invoice number |

**The argument this theme must make:** we had two routes for audio, we chose transcription over native audio embeddings, and [16] versus [17] is the evidence. That is Job 2 from §1.1 executed properly.

## Theme 5 — Grounding: RAG and its descendants

| # | Source | Problem it solved | Key idea | What RAGNova takes |
|---|---|---|---|---|
| 19 | Guu et al., "REALM: Retrieval-Augmented Language Model Pre-Training," ICML, 2020 | Knowledge locked in parameters, un-updatable and un-inspectable | Retrieval integrated into pretraining, jointly learned | Historical predecessor — establishes the idea before RAG named it |
| 20 | **Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," NeurIPS, 2020** **[Pass 2 + Pass 3]** | LLMs hallucinate, cannot cite, and cannot access private or new data | Combine a dense retriever with a seq2seq generator; condition generation on retrieved passages | **The paper your project is named after.** Justifies the whole architecture and Objective O4 |
| 21 | Izacard & Grave, "Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering," EACL, 2021 (Fusion-in-Decoder) | Combining evidence from many passages | Encode passages independently, fuse in the decoder | Explains **why top-K matters** and how multiple chunks combine |
| 22 | Ji et al., "Survey of Hallucination in Natural Language Generation," *ACM Computing Surveys*, 2023 | Hallucination discussed anecdotally, not systematically | Taxonomy of causes and mitigations | **The citation behind Ch 1 §1.2.** Use it when you claim hallucination is structural |
| 23 | Liu et al., "Lost in the Middle: How Language Models Use Long Contexts," *TACL*, 2024 | Assumption that longer context is strictly better | Accuracy degrades for information positioned mid-prompt | **Justifies retrieving few good chunks rather than stuffing everything** — Ch 1 §1.3 |
| 24 | Asai et al., "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection," ICLR, 2024 | Naive RAG retrieves indiscriminately and cannot assess its own output | Model emits reflection tokens deciding when to retrieve and whether output is supported | **Future work.** Shows you know naive RAG's limits |
| 25 | Yan et al., "Corrective Retrieval Augmented Generation," arXiv, 2024 | Retrieval sometimes returns irrelevant passages | Lightweight evaluator grades retrieval and triggers correction | **Future work** — a concrete improvement path for the report's final section |
| 26 | Gao et al., "Retrieval-Augmented Generation for Large Language Models: A Survey," arXiv, 2023–24 | The field fragmented rapidly | Taxonomy: Naive → Advanced → Modular RAG | **Use its taxonomy to position your system honestly** — "RAGNova implements Naive RAG extended to multiple modalities" is a defensible, precise self-description |

> **A high-value move:** explicitly classify your own system using [26]'s taxonomy. Saying "ours is Naive RAG with multimodal ingestion; Advanced RAG techniques such as query rewriting and reranking are future work" demonstrates that you know where you sit in the field. Panels respond very well to this, and it pre-empts "why didn't you do reranking?"

## Theme 6 — Multimodal RAG specifically (this is where your gap lives)

| # | Source | Problem it solved | Key idea | What RAGNova takes |
|---|---|---|---|---|
| 27 | **Chen et al., "MuRAG: Multimodal Retrieval-Augmented Generator for Open Question Answering over Images and Text," EMNLP, 2022** **[Pass 2]** | RAG was text-only | Retrieves from a multimodal memory of image–text pairs to answer questions | **Closest prior work.** Read it carefully and be ready to state precisely how you differ — offline execution, four modalities including speech, and citation transparency |

**This row is the most important in the entire survey**, because a strong panel member will find this paper. You must be able to say what MuRAG does, what it assumes (server-scale infrastructure, no speech modality, attribution not a design goal), and therefore what remains open. Do the forward-citation search of §1.5.3 on this paper today.

## Theme 7 — Making it run offline

| # | Source | Problem it solved | Key idea | What RAGNova takes |
|---|---|---|---|---|
| 28 | Dettmers et al., "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale," NeurIPS, 2022 | Large models exceeded consumer memory | 8-bit inference with outlier handling, near-lossless | Establishes that quantization preserves quality |
| 29 | Frantar et al., "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers," ICLR, 2023 | 4-bit quantization degraded quality | One-shot weight quantization using second-order information | **The evidence behind Ch 1 §1.1.5's memory table** — the reason a 3B model fits in ~2 GB |
| 30 | Lin et al., "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration," MLSys, 2024 | Some weights matter far more than others | Protect salient weights identified by activation statistics | Current practice; cite alongside [29] |
| 31 | Es et al., "RAGAS: Automated Evaluation of Retrieval Augmented Generation," EACL (demo), 2024 | RAG evaluation was ad hoc | Metrics for faithfulness, answer relevance, context relevance | **Where our faithfulness metric comes from** — Ch 1 §1.10. Cite so your evaluation is not self-invented |
| 32 | Official documentation: Ollama · ChromaDB · sentence-transformers · faster-whisper | — | — | Cite with access dates for implementation specifics |

## The comparison table your review needs

Prose alone will not make the gap visible. **Include this table** — it does the argumentative work of two pages, and it is the single figure most likely to survive into your final report.

| System / approach | Text | Image | Audio | Cross-modal | Generative answer | Citations | Offline |
|---|---|---|---|---|---|---|---|
| Keyword search (BM25 [5]) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Dense retrieval (DPR [6]) | ✅ | ❌ | ❌ | ❌ | ❌ | ⚠️ passages only | ✅ |
| RAG [20] | ✅ | ❌ | ❌ | ❌ | ✅ | ⚠️ possible, not built in | ⚠️ if self-hosted |
| CLIP retrieval [11] | ⚠️ ≤77 tokens | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| MuRAG [27] | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| Cloud assistants with file upload | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ⚠️ inconsistent | ❌ |
| LangChain/LlamaIndex demo RAG | ✅ | ⚠️ add-on | ⚠️ add-on | ❌ | ✅ | ⚠️ manual | ⚠️ configurable |
| **RAGNova** | ✅ | ✅ | ✅ | ✅ 3 directions | ✅ | ✅ first-class | ✅ verified |

**The empty region in the bottom-right of this table is your gap, made visible.** Note the honest use of ⚠️ — a table of all ✅ for your system and all ❌ for everyone else is not credible and invites hostile questioning. Nuance is more persuasive than triumph.

## The gap statement, assembled

Putting §1.10.2's four moves together with the survey above:

> Multimodal retrieval-augmented generation has been demonstrated over combined image and text corpora [27], and cross-modal retrieval is well established through contrastive vision-language pretraining [11], [12]. However, existing systems exhibit three limitations relative to the setting addressed here. First, they assume cloud-hosted embedding and generation services, precluding deployment on confidential corpora or in disconnected environments. Second, speech is rarely integrated as a first-class retrievable modality despite the maturity of robust offline transcription [16]. Third, source attribution is typically treated as a presentation-layer concern rather than a design requirement propagated through ingestion, indexing, and generation. This work integrates four modalities under a strict offline constraint, with provenance metadata maintained from ingestion through to citation rendering, and evaluates the resulting system using established retrieval [10] and RAG-specific [31] metrics.

Rewrite this in your own words. Note that it claims **integration under a constraint**, not algorithmic novelty — and that it names three specific limitations rather than one vague one.

---

# Part 3 — LEARN: methodology

## 3.1 What "methodology" means in an engineering project

Students confuse two things. **Research methodology** describes how you produce and validate knowledge. **Implementation detail** describes what you typed. A methodology section is the first, not the second.

Your methodology must answer five questions:

| Question | Section |
|---|---|
| What *kind* of work is this? | §3.2 Research approach |
| How is the system designed, and **why this way rather than the alternatives**? | §3.3 Design rationale |
| What data will it be tested on, and where does that data come from? | §3.5 Data methodology |
| How will you know whether it worked? | §3.6 Evaluation methodology |
| What could make your conclusions wrong? | §3.7 Threats to validity |

The word carrying the marks is **why**. A methodology section that says "we use ChromaDB" is a parts list. One that says "we use ChromaDB rather than FAISS because embedded operation removes a deployment dependency, and metadata filtering is required for citation provenance; FAISS's scale advantage is irrelevant below 10⁵ vectors" is methodology.

## 3.2 Naming your research approach

Use the correct term — it signals you know what kind of work you are doing.

Yours is **Design Science Research** (also called constructive or engineering research): you build an *artefact* that solves a class of problem, and you evaluate it against defined criteria. It contrasts with *empirical research* (test a hypothesis on data) and *theoretical research* (prove a property).

State it explicitly:

> This project follows a design-science methodology: a software artefact is constructed to address an identified deficiency, and is evaluated against predefined functional and performance criteria derived from the literature.

Then name the development process. Yours is **incremental and modular**: independent pipelines built in parallel against a frozen shared interface, integrated at a planned point, then evaluated and refined against human feedback. Say that, and note the two structural decisions that make it work — the schema freeze on Day 5, and integration on Day 12 rather than Day 13.

## 3.3 Design rationale: the technique that earns marks

For every significant decision, document four things: **the decision, the alternatives considered, the criteria, and the justification.** Missing alternatives is what makes a design section read as arbitrary.

The format below is an **Architecture Decision Record (ADR)** — a lightweight industry practice that maps perfectly onto what a methodology section needs.

```markdown
# ADR-003: Use two vector collections rather than one

## Status
Accepted (Day 3)

## Context
Text chunks are embedded with all-MiniLM-L6-v2 (384-d); images with
OpenCLIP ViT-B/32 (512-d). Both must be searchable from one query interface.

## Decision
Maintain two separate ChromaDB collections, queried independently and
merged by rank.

## Alternatives considered
1. Single collection, one model for both — impossible: CLIP's text encoder
   truncates at 77 tokens [11], so it cannot represent document-length passages.
2. Single collection, projecting one space into the other — requires training
   a projection layer; out of scope and unvalidated.
3. Two collections, merged by raw similarity score — rejected: the modality
   gap [13] makes text-image similarities systematically lower than
   text-text, so images would be systematically ranked last.

## Consequences
+ Each modality is embedded by the model best suited to it
+ Rank-based merging is robust to the modality gap
− Two indexes to maintain; merge policy becomes a tunable parameter
− Absolute cross-modal scores are not comparable to text scores; the UI must
  not display them side by side as if they were
```

Note what makes this strong: **alternative 3 is rejected with a citation.** That single line converts an implementation choice into a literature-grounded design decision. Do this for your non-obvious decisions.

**Write ADRs for these seven**, which are the ones a panel will probe:

| ADR | Decision | The interesting alternative you rejected |
|---|---|---|
| 001 | RAG rather than fine-tuning | Fine-tuning — no citations, per-file retraining, needs GPUs |
| 002 | Local quantized LLM rather than a cloud API | Cloud — violates the offline objective |
| 003 | Two vector collections | One collection — CLIP's 77-token limit |
| 004 | ChromaDB rather than FAISS or Qdrant | FAISS — no metadata, no persistence layer, scale irrelevant here |
| 005 | Transcription rather than native audio embeddings | CLAP — weaker on speech semantics; loses timestamps |
| 006 | Fixed-size overlapping chunks | Semantic/recursive chunking — better, but more moving parts; note as future work |
| 007 | Rank-based cross-modal merging | Score-based merging — defeated by the modality gap |

A folder is prepared at [`docs/decisions/`](../decisions/) with the template and ADR-003 written out as a worked example.

## 3.4 The methodology section's structure

| Section | Content |
|---|---|
| 3.1 Research approach | Design science; incremental modular development (§3.2) |
| 3.2 System architecture | The pipeline diagram plus a component walkthrough |
| 3.3 Ingestion methodology | Per-modality: parsing, chunking parameters and their justification, metadata schema |
| 3.4 Indexing methodology | Embedding models with citations, collection design, ANN algorithm |
| 3.5 Retrieval methodology | Query embedding, top-K selection, cross-modal merge policy |
| 3.6 Generation methodology | Prompt construction, temperature, citation format and validation |
| 3.7 Data methodology | Corpus composition, gold-set construction (§3.5) |
| 3.8 Evaluation methodology | Metrics, protocol, human study design (§3.6) |
| 3.9 Threats to validity | §3.7 |

## 3.5 Data methodology

Say where your data came from and why it is adequate. Three points:

**Composition.** 50–200 files across four formats, deliberately including cross-modal pairs — an image and a document on the same topic, an audio clip discussing a topic also in a PDF. State that this is *purposive* sampling, not random: the corpus is constructed to exercise the cross-modal capability specifically.

**Gold-set construction, and the honest disclosure.** Your evaluation questions were written **before** the system existed (Ch 1 §3.3). Say so explicitly — it is a genuine methodological strength that prevents unconscious tuning-to-the-test.

But also disclose the limitation plainly: **the gold set was authored by the same team that built the system**, which introduces bias in question phrasing (you will unconsciously write questions your architecture handles well). The mitigation — have the Chapter 12 external testers write additional questions, and report those results separately. **Stating a limitation and its mitigation is worth more than hiding it**; a panel that discovers an undisclosed weakness treats everything else with suspicion.

**Ethics and licensing.** Only owned or freely-shareable files; no confidential material in a submitted corpus; note that offline operation is itself the privacy control.

## 3.6 Evaluation methodology

### 3.6.1 The principle

**An evaluation that cannot fail is not an evaluation.** Define your metrics, targets, and protocol *now*, before results exist. Metrics chosen after seeing results are worthless, and examiners know this.

### 3.6.2 Retrieval metrics — what each actually measures

| Metric | Definition | What it captures | Weakness |
|---|---|---|---|
| **Recall@K** | Fraction of queries where a correct chunk appears in the top K | "Did we find it at all?" | Ignores position within the top K |
| **MRR** | Mean of 1/(rank of first correct result) | "Did we rank it first?" | Only considers the first correct result |
| **nDCG@K** | Position-discounted gain over graded relevance | Handles multiple relevant results with degrees of relevance | Requires graded judgements — more labelling |

**Report Recall@5 and MRR.** They answer different questions and are cheap to compute from binary judgements. Mention nDCG as applicable if you later grade relevance — but do not promise it.

**Worked example, so you can actually compute these.** Five questions; the rank at which the correct chunk appeared:

| Q | Rank of correct chunk | In top 5? | Reciprocal rank |
|---|---|---|---|
| 1 | 1 | ✅ | 1.00 |
| 2 | 3 | ✅ | 0.33 |
| 3 | not retrieved | ❌ | 0.00 |
| 4 | 2 | ✅ | 0.50 |
| 5 | 1 | ✅ | 1.00 |

```
Recall@5 = 4/5 = 0.80
MRR      = (1.00 + 0.33 + 0.00 + 0.50 + 1.00) / 5 = 0.566
```

Notice the two metrics disagree in emphasis: recall looks respectable while MRR reveals that question 2 was ranked third. **That disagreement is exactly why you report both** — and being able to explain it is a strong viva answer.

### 3.6.3 Generation metrics

Automatic text-overlap metrics (BLEU, ROUGE) are **inappropriate** for RAG answers — a correct answer phrased differently scores badly, and a fluent wrong answer can score well. Say this explicitly; it demonstrates you chose metrics deliberately rather than defaulting.

Use the RAGAS-style dimensions [31], rated by humans on a 1–5 scale:

| Dimension | The rater's question |
|---|---|
| **Faithfulness** | Is every claim supported by the cited chunk? |
| **Answer relevance** | Does it address what was actually asked? |
| **Context relevance** | Were the retrieved chunks actually useful? |
| **Citation correctness** | Do the `[n]` markers point at the chunks that support each claim? |

### 3.6.4 Designing the human study so it is credible

Four design choices, each with a reason:

1. **Number of raters:** at least three, including at least one person outside the team. One rater is an opinion; three is data.
2. **Blinding:** raters should not know which configuration produced which answer when you compare configurations (for example, chunk size 200 versus 400). Otherwise expectation contaminates the rating.
3. **Written rubric:** define what each point on the 1–5 scale means, before rating. Without this, raters drift and scores are not comparable across sessions.
4. **Agreement:** have at least two raters score the same subset and report how often they agree. Perfect agreement is unnecessary; **reporting the disagreement is what makes the numbers honest.**

Report **mean and range**, not just the mean. A mean of 4.0 from scores {4,4,4} and from {2,5,5} are very different findings.

### 3.6.5 System performance

Report on a stated reference machine (specify CPU and RAM — numbers without hardware are meaningless): indexing throughput per modality, retrieval latency, end-to-end latency, and peak memory. Report the **median and the worst case**, not the best case.

### 3.6.6 Ablations — the cheapest way to look rigorous

An ablation removes or varies one component to show it matters. Three that cost almost nothing here and produce real findings:

| Ablation | What it demonstrates |
|---|---|
| Chunk size 150 vs 300 vs 600 | That your chunking parameter was chosen, not guessed |
| Top-K = 3 vs 5 vs 10 | The precision/context trade-off, and the lost-in-the-middle effect [23] |
| Rank-based vs score-based cross-modal merge | That the modality gap [13] is real **in your own data** |

**The third one is the most valuable experiment in your entire project.** It takes an afternoon, it converts a cited claim into your own empirical finding, and it produces a result no other team will have. Do it in Chapter 12.

## 3.7 Threats to validity

A short subsection that dramatically raises perceived rigour, because it shows you know what your evidence does *not* prove.

| Threat | In your project | Mitigation |
|---|---|---|
| **Internal** — is the effect caused by what you claim? | Retrieval improvements might come from corpus properties rather than the embedding model | Ablations (§3.6.6); fixed corpus across comparisons |
| **External** — does it generalise? | 50–200 English files on one hardware configuration; results may not hold at 10⁵ files or in other languages | State the limit explicitly; do not extrapolate |
| **Construct** — do the metrics measure what matters? | Recall@5 does not measure answer usefulness; hence the human ratings | Report both retrieval and answer metrics |
| **Conclusion** — is the sample big enough? | 20 questions is small; a single question shifts Recall@5 by 0.05 | Report the sample size beside every number; avoid claiming small differences are significant |

That last row is worth internalising. With 20 questions, **a difference between 0.80 and 0.85 is one question.** Do not build an argument on it, and if a panel member points this out, agreeing immediately is a much better answer than defending it.

---

# Part 4 — DECIDE

**4.1 Organising structure.** Thematic, using the seven themes of Part 2. Chronological ordering makes contribution invisible; a paper-by-paper structure is the anti-pattern of §1.2. If you compress, merge Themes 1 and 2 into "semantic representation and retrieval."

**4.2 How many sources.** 15–20 for the review; 20–25 for the final report. Quality over count — twenty sources you can each summarise in one sentence beats forty you cannot. Ensure coverage of every theme; a theme with one citation looks like an afterthought.

**4.3 Which gap to claim.** The conjunctive one from §1.10.1 rows 2–3: integration under an offline constraint, with speech as a first-class modality and citations as a design requirement. Do **not** claim algorithmic novelty.

**4.4 Which decisions to formalise as ADRs.** The seven in §3.3. Three of them (003, 005, 007) carry citations, which is what makes them methodology rather than preference.

**4.5 What to defer to the report.** Full ablation results, per-module implementation detail, the feedback log. Today establishes the *protocol*; Chapters 7–12 produce the numbers.

---

# Part 5 — BUILD: the day

## 5.1 Templates prepared for you

| File | Purpose |
|---|---|
| [`reports/literature-matrix.md`](../../reports/literature-matrix.md) | Search log, per-paper note template, and the synthesis matrix pre-populated with Part 2's sources |
| [`reports/methodology-draft.md`](../../reports/methodology-draft.md) | The full methodology section, drafted, with `⟨FILL⟩` markers |
| [`docs/decisions/`](../decisions/) | ADR template plus ADR-003 as a worked example |

> Same warning as Chapter 2: **rewrite everything in your own words.** You will be questioned on every sentence, and text you did not write is text you cannot defend.

## 5.2 Schedule

| Time | Task | Who |
|---|---|---|
| 0:00–0:30 | Read Part 1. Agree the theme structure and the gap claim. | All |
| 0:30–1:30 | **Verify every citation in Part 2** against the actual source. Split the list three ways. Fix errors in the matrix as you go. | Parallel |
| 1:30–2:30 | Pass-2 reading. Member 1: RAG [20] + DPR [6]. Member 2: CLIP [11] + modality gap [13]. Member 3: Whisper [16] + MuRAG [27]. Write the §1.7 note for each. | Parallel |
| 2:30–3:00 | **Forward-citation search** (§1.5.3) on Lewis [20] and MuRAG [27], filtering for `offline`, `local`, `multimodal`. Log results. Adjust the gap statement if needed. | Member 3 |
| 3:00–4:00 | Fill the synthesis matrix. Write the review: one paragraph per theme, using the §1.9 moves. | Member 1 leads |
| 4:00–5:00 | Write the methodology draft and the seven ADRs. | Member 2 leads |
| 5:00–5:30 | One editor merges and unifies voice. Build the comparison table. | One editor |
| 5:30–6:00 | Run the §6.1 rubric and drill the §6.2 questions. | All |

## 5.3 The one task nobody should skip

**The forward-citation search at 2:30.** Everything else can be recovered later; discovering in the viva that someone published exactly your system in 2024 cannot. Fifteen minutes, and it either strengthens your gap statement with evidence or tells you to narrow it while narrowing is still free.

---

# Part 6 — CHECK

## 6.1 Rubric

Score 0–3 each. Below 30/42, revise.

| # | Criterion | Score |
|---|---|---|
| 1 | Organised thematically, not paper-by-paper | /3 |
| 2 | Multiple sources appear in single sentences, compared or contrasted | /3 |
| 3 | At least one taxonomy or grouping move (§1.9) | /3 |
| 4 | Every theme has ≥ 2 sources | /3 |
| 5 | Comparison table present, with honest ⚠️ marks | /3 |
| 6 | Gap stated in four moves; conjunctive, not absolute-novelty | /3 |
| 7 | Gap pressure-tested against ≥ 3 candidate counter-examples | /3 |
| 8 | Every citation verified against the actual source | /3 |
| 9 | Nothing patchwritten; paraphrases restructure, not just re-word | /3 |
| 10 | Methodology names alternatives rejected, with reasons | /3 |
| 11 | ≥ 3 ADRs cite literature | /3 |
| 12 | Metrics defined with targets **before** any results exist | /3 |
| 13 | Human study design specifies raters, blinding, rubric, agreement | /3 |
| 14 | Threats to validity section present and honest | /3 |
| | **Total** | **/42** |

## 6.2 Twenty-five questions a panel will ask

**On the review**
1. How did you find these papers? → §1.5 search log + snowballing. Show the log.
2. Which is the most important paper for your work, and why? → Lewis [20] for architecture; CLIP [11] for the cross-modal capability.
3. Has anyone already built this? → MuRAG [27] is closest; name the three differences (offline, speech, citation-as-requirement).
4. What is your gap in one sentence? → §1.10.2 move 2 + 3.
5. Is your contribution novel? → **Integration under a constraint, not a new algorithm.** Say it plainly and do not overclaim.
6. Why cite a 2009 paper (BM25) in a 2026 project? → It is the baseline we argue against, and still superior for rare exact strings.
7. What does [13] (modality gap) actually say, and why does it matter to you? → Image and text embeddings occupy separate regions; hence rank-based merging.
8. Which paper did you disagree with, or find a limitation in? → Any honest answer scores well. Lost-in-the-Middle [23] versus the "just use long context" position is a good one.

**On methodology**
9. What research methodology is this? → Design science: construct an artefact, evaluate against predefined criteria.
10. Why RAG and not fine-tuning? → ADR-001: no citations, per-file retraining, GPU requirement.
11. Why ChromaDB and not FAISS? → ADR-004: embedded operation, metadata filtering for provenance; scale advantage irrelevant below 10⁵ vectors.
12. Why two collections? → ADR-003: 512-d vs 384-d, different spaces, CLIP's 77-token limit.
13. Why 300-word chunks? → Fits the 256-token embedding limit; ablation at 150/300/600 will validate it.
14. Why transcription rather than CLAP? → ADR-005: speech content is linguistic; transcription gives timestamps and readable evidence.
15. Why is your temperature low? → Faithfulness over creativity in a citation-grounded system.

**On evaluation**
16. How will you know it worked? → Recall@5 ≥ 0.80, MRR ≥ 0.65, cross-modal Recall@5 ≥ 0.70, faithfulness ≥ 4/5.
17. Why Recall@5 *and* MRR? → They measure different things — finding versus ranking. Give the §3.6.2 worked example.
18. Why not BLEU or ROUGE? → Overlap metrics penalise correct paraphrase and reward fluent wrong answers.
19. Who writes the test questions, and isn't that biased? → We do, before implementation; the bias is real, and external testers add questions in Chapter 12.
20. How many test questions? Is that enough? → 20; with 20 questions one item moves Recall@5 by 0.05, so we do not claim small differences.
21. How do you prevent tuning to the test set? → Gold set written before implementation; parameters chosen by ablation, reported honestly.
22. What are the threats to validity? → §3.7's four rows.
23. What ablation would most strengthen your claims? → Rank-based versus score-based merging — it tests the modality gap in our own data.

**On honesty**
24. What is the weakest part of your evaluation? → Small sample and self-authored questions. Say so; the mitigation is external testers.
25. What would you do with three more months? → Advanced RAG [26]: reranking, query rewriting, Self-RAG-style verification [24], and video.

## 6.3 Failure modes

| Failure | Why it costs | Fix |
|---|---|---|
| Paper-by-paper paragraphs | Reads as a reading list; no argument | Synthesis matrix (§1.8) — write down columns |
| No gap statement | The review does not justify the project | Four-move formula (§1.10.2) |
| Gap claims absolute novelty | One counter-example destroys it | Claim integration under constraint |
| Citing surveys for primary facts | Signals you did not read originals | Trace to the primary source (§1.6.4) |
| Citing blogs or Medium | Not evidence | Primary sources only (§1.6.1) |
| Patchwritten paraphrase | Plagiarism, even when cited | Close the source, then write from memory (§1.11.2) |
| Methodology as a parts list | No "why", so no marks | Alternatives + criteria + justification (§3.3) |
| Metrics chosen after results | Worthless — and examiners know | Define targets today, in writing |
| No threats-to-validity section | Suggests you cannot see your own limits | §3.7 — four rows is enough |
| Unverified references | An error found in the viva taints everything | Verify all today (§5.2, 0:30–1:30) |

## 6.4 Day 3 completion checklist

- [ ] Search log completed with at least six distinct queries across ≥ 3 sources
- [ ] Forward-citation search on Lewis [20] and MuRAG [27] done and logged
- [ ] Every citation in the reference list verified against the actual source
- [ ] Six papers read to Pass 2, with the §1.7 note completed for each
- [ ] Synthesis matrix filled in
- [ ] Literature review written thematically, 15–20 sources, ≥ 1 taxonomy move
- [ ] Comparison table built, with honest ⚠️ marks
- [ ] Gap stated in four moves and pressure-tested against three counter-examples
- [ ] Methodology draft covering all nine subsections
- [ ] Seven ADRs written; at least three cite literature
- [ ] Evaluation protocol fixed in writing: metrics, targets, rater count, rubric, blinding
- [ ] Threats-to-validity section written
- [ ] One editor has unified the voice
- [ ] Rubric §6.1 scored ≥ 30/42
- [ ] All twenty-five questions in §6.2 drilled

---

**Next:** [Chapter 4 — Timeline, Team & Modular Work Split](ch04-timeline-and-team-split.md) (Day 4) — Presentation #2, the Gantt chart, module decomposition, interface contracts, and how three people work in parallel without blocking each other.
