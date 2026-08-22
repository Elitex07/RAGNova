# Chapter 3B — Reading a Paper & Citation Mechanics

> **Companion to [Chapter 3](ch03-literature-review-and-methodology.md).** Two things that are far easier to learn by seeing than by reading about:
>
> - **Part A** — a fully worked three-pass reading of the CLIP paper, with the actual notes written out.
> - **Part B** — IEEE citation format for every entry type you will need, plus the Zotero workflow that stops your reference list breaking.
>
> Do Part A before reading your own first paper. Do Part B before writing your first citation.

---

# Part A — A worked paper reading

Chapter 3 §1.8 describes the three-pass method. Description is not enough; the output is what teaches. Below is what an actual reading of CLIP produces at each depth.

**The paper:** Radford et al., "Learning Transferable Visual Models From Natural Language Supervision," *ICML*, 2021.

**Why this one:** it is the single most important paper in your review, it is long (48 pages), and it is intimidating. If you can handle this one, the rest are easier.

---

## A.1 Pass 1 — nine minutes

**Read only:** title, abstract, section headings, all figures, conclusion. **Skip:** everything else, especially the mathematics.

### What you actually do

1. **Title (10 s).** "Learning Transferable Visual Models From Natural Language Supervision." Three signals: *transferable* (works on tasks it was not trained for), *visual models*, *from natural language supervision* (text is the training signal, not labels). Already you know the core idea.

2. **Abstract (2 min).** Read twice. The first read gets the shape; the second looks specifically for the last two sentences, which almost always state the contribution.

3. **Section headings (1 min).** Scroll the whole paper reading only headings. You are building a map: Approach → Experiments → Comparison to Human Performance → Data Overlap Analysis → Limitations → Broader Impacts.

4. **Figures (4 min).** In ML papers the figures carry the argument. Figure 1 shows the contrastive pretraining setup and zero-shot classification — that single figure *is* the method.

5. **Conclusion (1 min).**

6. **Skim the Limitations section.** Most students skip this. It is where the authors tell you exactly what to say in your own limitations section, and it is the cheapest source of viva-proof honesty available.

### The Pass 1 note that results

```markdown
**Citation:** Radford et al., "Learning Transferable Visual Models From
              Natural Language Supervision," ICML 2021
**Read to:** Pass 1 · 9 min · Member 2 · ⟨date⟩

**Category:** New technique + large-scale empirical study
**Context:** Vision pretraining; contrastive learning; zero-shot transfer
**Contribution (one sentence):** Training image and text encoders jointly on
  ~400M web image-caption pairs with a contrastive objective produces a shared
  embedding space enabling zero-shot classification and cross-modal retrieval
  without task-specific training data.
**Correctness:** Assumptions look sound; very large-scale empirical evidence
**Clarity:** Well written; Figure 1 is unusually clear

**Decision:** ➜ PASS 2 — this is the foundation of Objective O3
**Questions I now have:**
  - How long can the text input be?          (matters for ADR-003)
  - Are image and text vectors directly comparable in practice?
  - What does the "temperature" parameter do?
```

**Note what happened.** Nine minutes produced a defensible one-sentence contribution, a decision about whether to continue, and three specific questions to answer in Pass 2. **Reading with questions is several times faster than reading without them** — this is the main practical benefit of the pass structure.

**And note the counterfactual.** For roughly 60% of papers, the Pass 1 note ends with `➜ STOP — cite for context only` and you move on. That is the method working, not failing.

---

## A.2 Pass 2 — fifty-five minutes

**Read fully; skip proofs and derivations.** Answer your Pass 1 questions. Take notes *as you go*, not afterwards.

### How to spend the time

| Minutes | What |
|---|---|
| 0–10 | Introduction properly. Find the explicit "our contributions" paragraph |
| 10–30 | The Approach/Method section. Redraw Figure 1 by hand — **this is the step that produces understanding** |
| 30–45 | Results. Read tables using the five questions in Ch 3 §1.8.1 |
| 45–55 | Limitations and Broader Impacts. Write down anything relevant to your own limitations |

**Redrawing the figure by hand is not busywork.** You cannot copy a diagram without discovering the parts you did not understand. It is the fastest way to find the gap between "I read it" and "I know it."

### The Pass 2 note that results

```markdown
**Citation:** Radford et al., CLIP, ICML 2021
**Theme:** 4 (cross-modal) — also touches 1 (representation)
**Read to:** Pass 2 · 55 min · Member 2 · ⟨date⟩

**PROBLEM**
Two problems, and the paper solves both with one idea:
(a) Conventional vision models predict from a FIXED label set. Adding a class
    means collecting labelled data and retraining.
(b) An image encoder and a text encoder trained separately produce vectors in
    unrelated coordinate systems. Comparing them is arithmetic without meaning.

**KEY IDEA (own words)**
Train both encoders TOGETHER so that an image and its caption end up close in
one shared space. Because the supervision is natural language rather than a
label set, the model can later be pointed at any concept expressible in words.

**METHOD (whiteboard level)**
- Image encoder: Vision Transformer — image split into patches, patches treated
  like tokens. (ResNet variants also tried.)
- Text encoder: transformer over the caption.
- Both project into a shared embedding space; vectors L2-normalised.
- Training: take a batch of N (image, caption) pairs. Encode all 2N items.
  Compute the N x N cosine-similarity matrix. Symmetric cross-entropy loss
  maximises the diagonal (true pairs), minimises off-diagonal.
  Every other item in the batch is a negative → very large batches matter.
- A LEARNED temperature scales similarities before the softmax.

  [redraw the N x N matrix here by hand]

- Zero-shot classification: embed candidate label strings as
  "a photo of a {label}", pick the nearest to the image embedding.

**DATA**
~400M image-caption pairs collected from the internet. No manual labelling —
the caption is the supervision. This is why coverage is open-vocabulary.

**RESULTS / WHAT WAS MEASURED**
- Zero-shot transfer evaluated across a large suite of image classification
  datasets; zero-shot CLIP is competitive with supervised baselines on many.
- Headline result reported: zero-shot CLIP matching a supervised ResNet-50 on
  ImageNet without using any of its labelled training examples.
  ⚠️ VERIFY exact numbers before quoting.
- Also: robustness to distribution shift is markedly better than supervised
  models with similar in-distribution accuracy.

**HOW TO READ THEIR MAIN TABLE (practice, per Ch 3 §1.8.1)**
- Baseline: fully supervised models trained on each dataset. Fair — that is the
  demanding comparison, not a weak one.
- Metric: accuracy, higher better.
- Missing: fine-grained tasks where CLIP does poorly are reported, not hidden —
  a good sign about the paper's honesty.

**LIMITATIONS (authors' own — copy these, they are free honesty for my report)**
- Weak on fine-grained classification, counting, and abstract/systematic tasks.
- Zero-shot performance sensitive to PROMPT WORDING ("prompt engineering").
- Trained on unfiltered web data → inherits social biases; the paper documents
  this at length.
- Not sample-efficient in the few-shot regime.

**ANSWERS TO MY PASS 1 QUESTIONS**
1. Text input limit: 77 tokens. ⭐⭐ CRITICAL FOR US — CLIP CANNOT embed
   document-length passages. This alone forces the two-collection design
   in ADR-003.
2. Comparability: yes within the shared space — but see the modality gap
   paper [Liang 2022], which shows text-image similarities are systematically
   LOWER than text-text. Forces ADR-007 (rank-based merging).
3. Temperature: a learned scalar sharpening the softmax over similarities.
   NOTE: different from LLM sampling temperature. Do not conflate them in
   the report — an examiner will notice.

**RELEVANCE TO RAGNova**
TAKE: the shared embedding space — the entire basis of Objective O3
      (text→image, image→image retrieval with no captions or tags).
TAKE: OpenCLIP weights [Cherti 2023] rather than original CLIP, because the
      original training data was never released. Cite both, and the reason
      for citing both is itself a good sentence about reproducibility.
REJECT: using CLIP for document text — 77-token limit.
DESIGN CONSEQUENCE: two collections (ADR-003); rank-based merge (ADR-007).

**QUOTABLE**
Approach section: the contrastive objective predicts which caption goes with
which image within a batch. (PARAPHRASE — do not copy the sentence.)

**CONFIDENCE:** Pass 2. Method understood well enough to whiteboard.
Have NOT verified the training-detail mathematics — Pass 3 if needed.
```

### What this note is worth

Notice three things about it.

**It answers its own Pass 1 questions**, and the answer to question 1 (77 tokens) is the single fact that determines your entire index architecture. You did not go looking for it as an architecture question — it arrived because you read with a question in hand.

**It copies the authors' own limitations.** Those four bullets are free, authoritative material for your report's limitations section, and quoting a paper's self-identified weaknesses is unimpeachable.

**The RELEVANCE field is already prose.** "Take the shared embedding space; reject CLIP for document text because of the 77-token limit; therefore two collections" is a paragraph of your methodology, written while reading rather than afterwards.

---

## A.3 Pass 3 — when and why

Pass 3 means reconstructing the work: challenging assumptions, following the details, asking what you would have done differently. **You need it for at most two papers** — for this project, CLIP and RAG, because they are what an examiner will probe hardest.

For CLIP, a Pass 3 would ask:

- **Why symmetric loss?** What breaks if you optimise only image→text?
- **Why is batch size so important?** (Because negatives come from within the batch — connect this to DPR's in-batch negatives in Theme 2. Noticing that two papers in different subfields use the same trick is exactly the kind of observation that produces a *taxonomy* move in your prose.)
- **Why is temperature learned rather than fixed?**
- **What would happen with 4M pairs instead of 400M?** (OpenCLIP's scaling-laws paper answers this — which is why the two papers belong together.)

**You do not need to answer all of these.** The value of Pass 3 is that it generates questions you can discuss intelligently. An examiner asking "why does batch size matter for CLIP?" is far more impressed by a reasoned answer about in-batch negatives than by a memorised fact.

---

## A.4 The reading checklist

Use this for each of your six Pass-2 papers.

- [ ] Pass 1 done; contribution stated in one sentence *before* going further
- [ ] Three specific questions written down before Pass 2
- [ ] Main figure redrawn by hand
- [ ] Results table read using the five questions (baseline, metric, gap size, bolding, missing datasets)
- [ ] Authors' own limitations copied down
- [ ] Pass 1 questions explicitly answered
- [ ] **RELEVANCE field completed** — take / reject / design consequence
- [ ] Reading depth recorded honestly (Pass 1 / 2 / 3)
- [ ] Citation captured in Zotero and verified against the paper

---

# Part B — Citation mechanics

## B.1 Why this matters more than it seems

A broken reference list is one of the few things that makes an examiner doubt everything else, because it is *checkable*. If reference [7] has the wrong year, the natural next thought is "what else did they not check?"

The good news: fifteen minutes of setup eliminates the entire failure class.

## B.2 Zotero setup

**Install:** Zotero desktop from `zotero.org` plus the browser connector extension. Free, open-source, no account needed for local use (an account syncs across your team's machines, which is worth it for a group project).

**Capture:** on any paper page — arXiv, ACL Anthology, IEEE Xplore, Google Scholar — click the connector icon. Zotero pulls authors, title, venue, year, DOI, and usually the PDF.

**Organise:** create one collection per theme, matching Chapter 3A's eleven themes. **Your collection structure then *is* your review outline**, and moving a paper between collections is how you decide where it belongs in your prose.

**Tag:** add tags for reading depth (`pass-1`, `pass-2`, `pass-3`) and status (`verified`, `needs-check`). Filtering by `needs-check` on Day 13 takes two seconds.

**Notes:** attach your Chapter 3 §1.8.3 reading note directly to the Zotero item. Everything about a paper then lives in one place.

### B.2.1 The verification step Zotero cannot do for you

**Automatic capture is frequently wrong about venue.** The most common error: it records the arXiv preprint when a peer-reviewed conference version exists. Zotero saving it does not make it correct.

For every entry, check three fields against the actual paper:

| Field | Common error |
|---|---|
| **Venue** | arXiv recorded instead of the conference/journal |
| **Year** | Preprint year instead of publication year |
| **Authors** | Truncated with "et al." in the stored record, or initials wrong |

For a paper you found on arXiv, search its exact title in Google Scholar. If a conference version exists, **cite that one.**

## B.3 IEEE format — every entry type you need

IEEE style: numbered in **order of first appearance**, cited in text as `[1]`, listed in that order. Not alphabetical.

### Conference paper — the most common in ML

```
[1] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal,
    H. Küttler, M. Lewis, W. Yih, T. Rocktäschel, S. Riedel, and D. Kiela,
    "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in
    Proc. Advances in Neural Information Processing Systems (NeurIPS), 2020,
    pp. 9459–9474.
```

Pattern: `Author initials and surnames, "Title in quotes," in Proc. Conference Name (ABBREV), Year, pp. X–Y.`

> **Author lists:** IEEE permits listing up to six authors and then "et al." Many departments prefer all authors listed. **Ask your guide, then be consistent** — inconsistency is more noticeable than either choice.

### Journal article

```
[2] Y. A. Malkov and D. A. Yashunin, "Efficient and Robust Approximate Nearest
    Neighbor Search Using Hierarchical Navigable Small World Graphs," IEEE
    Trans. Pattern Analysis and Machine Intelligence, vol. 42, no. 4,
    pp. 824–836, Apr. 2020.
```

Pattern: `Authors, "Title," Journal Name, vol. V, no. N, pp. X–Y, Month Year.`

Note: journal names are abbreviated in strict IEEE style (`IEEE Trans. Pattern Anal. Mach. Intell.`). Full names are widely accepted in student reports — pick one convention and hold it.

### Preprint (only when no published version exists)

```
[3] S. Ovadia, M. Brief, M. Mishaeli, and O. Elisha, "Fine-Tuning or Retrieval?
    Comparing Knowledge Injection in LLMs," arXiv:2312.05934, 2023.
```

Pattern: `Authors, "Title," arXiv:XXXX.XXXXX, Year.`

**Check first** whether a published version exists. If it does, cite that instead.

### Book

```
[4] C. D. Manning, P. Raghavan, and H. Schütze, Introduction to Information
    Retrieval. Cambridge, U.K.: Cambridge Univ. Press, 2008.
```

Book titles are *italicised*, not quoted.

### Book chapter

```
[5] A. Author, "Chapter title," in Book Title, B. Editor, Ed. City: Publisher,
    Year, pp. X–Y.
```

### Thesis

```
[6] A. Author, "Title of thesis," Ph.D. dissertation, Dept. of Computer Science,
    University Name, City, Country, Year.
```

### Website / online documentation

```
[7] Chroma, "Chroma Documentation." [Online]. Available:
    https://docs.trychroma.com [Accessed: 15-Aug-2026].
```

**The access date is mandatory** for online sources — web content changes. This is the correct way to cite the tools you use.

### Software / code repository

```
[8] G. Gerganov, "llama.cpp," GitHub repository, 2023. [Online]. Available:
    https://github.com/ggerganov/llama.cpp [Accessed: 15-Aug-2026].
```

**Cite the software you depend on.** Most student reports do not, and it is a visible sign of thoroughness. Where a project provides a preferred citation (a `CITATION.cff` file or a "how to cite" section), use theirs.

### Dataset

```
[9] T. Nguyen, M. Rosenberg, X. Song, J. Gao, S. Tiwary, R. Majumder, and
    L. Deng, "MS MARCO: A Human Generated MAchine Reading Comprehension
    Dataset," in Proc. NIPS Workshop on Cognitive Computation, 2016.
```

### Standard

```
[10] Information technology — Document management — Portable document format,
     ISO 32000-2:2020, 2020.
```

## B.4 In-text citation conventions

| Situation | Form |
|---|---|
| Single | `Dense retrieval outperforms lexical matching [6].` |
| Multiple | `Several studies confirm this [4], [6], [11].` |
| Range | `Recent surveys [12]–[15] cover this.` |
| Author as subject | `Karpukhin et al. [6] demonstrated that...` |
| Specific location | `The 77-token limit [11, §2.1] constrains...` |

**Rules:**
- The citation goes **before** the full stop: `...as shown [6].` not `...as shown. [6]`
- `et al.` is used in text for three or more authors; two authors are both named: `Reimers and Gurevych [4]`
- A citation number is not a noun. Write "Karpukhin et al. [6] showed", not "[6] showed"
- Number in **order of first appearance**. If you insert a citation mid-document, everything after shifts — which is exactly why you use a reference manager rather than typing numbers by hand

## B.5 If you use LaTeX

```latex
\documentclass[conference]{IEEEtran}
\bibliographystyle{IEEEtran}
...
Dense retrieval outperforms lexical matching \cite{karpukhin2020dense}.
...
\bibliography{references}
```

Export your Zotero library as `references.bib` (right-click collection → Export Collection → BibTeX). Numbering, ordering and formatting are then handled automatically, and inserting a citation mid-document costs nothing.

**If you use Word:** install the Zotero Word plugin. Insert citations through it, then "Add/Edit Bibliography" generates the list. Choose the **IEEE** style in Zotero's preferences. Do not type reference numbers manually — a single inserted source would otherwise require renumbering the entire document by hand.

## B.6 Final verification pass

Run this the day before submission, not the hour before.

- [ ] Every in-text `[n]` has a matching reference-list entry
- [ ] Every reference-list entry is cited at least once in the text
- [ ] Numbering follows order of first appearance
- [ ] Every venue, year and author list checked against the actual paper
- [ ] Published version cited wherever one exists
- [ ] All online sources carry access dates
- [ ] Author-list convention (full vs *et al.*) consistent throughout
- [ ] Journal-name convention (full vs abbreviated) consistent throughout
- [ ] Book titles italicised; paper titles in quotes
- [ ] Every cited work read to at least abstract + conclusion
- [ ] Every cited work can be summarised aloud in one sentence by at least one team member

That last box is the one that matters in the viva. **A reference you cannot summarise is a liability, not an asset.**

---

**Back to:** [Chapter 3 — Literature Review & Methodology](ch03-literature-review-and-methodology.md) · [Chapter 3A — Annotated Bibliography](ch03a-annotated-bibliography.md)
