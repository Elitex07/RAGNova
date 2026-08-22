# METHODOLOGY — DRAFT

> **⚠️ Rewrite every sentence in your own words.** You will be questioned on all of it. Guidance is in [Chapter 3 Part 3](../docs/chapters/ch03-literature-review-and-methodology.md). `⟨FILL⟩` marks a team-specific detail.
>
> Citation numbers `[n]` refer to the reference list in [`synopsis-draft.md`](synopsis-draft.md), extended with Chapter 3 Part 2's sources. **Renumber in order of first appearance** once the final text is assembled.

---

## 1. Research Approach

This project follows a **design-science methodology**: a software artefact is constructed to address an identified deficiency, and evaluated against functional and performance criteria defined in advance and derived from the literature. It is therefore constructive rather than hypothesis-testing; the claim under evaluation is that the artefact satisfies its stated objectives, not that a general proposition about the world holds.

Development follows an **incremental, modular process**. Three ingestion and retrieval pipelines are developed in parallel against a shared data schema frozen before implementation begins, integrated at a scheduled point rather than at the end of the schedule, and refined through two rounds of human evaluation. Two decisions make parallel development viable:

1. **Schema freeze (Day 5).** A single definition of an indexed segment — its identifier, source, modality, location and text — is fixed before any pipeline is written. Every pipeline emits this structure, so components remain substitutable and integration does not require renegotiation.
2. **Integration on Day 12, not Day 13.** Integration is scheduled with a day of slack. ⟨FILL: state this as a deliberate risk response, referencing your risk register.⟩

## 2. System Architecture

⟨INSERT FIGURE 1 — architecture diagram⟩

The system separates an **indexing phase**, executed once per file, from a **query phase**, executed once per question. This separation is what makes interactive latency achievable: all model-heavy processing of documents occurs ahead of time, leaving only query embedding, nearest-neighbour lookup and generation on the interactive path.

⟨FILL: 3–4 sentences walking through the diagram.⟩

## 3. Ingestion Methodology

### 3.1 Document ingestion
PDF files are parsed with PyMuPDF and DOCX files with python-docx, retaining page numbers for provenance. Extracted text is normalised (whitespace collapsed, control characters removed) before segmentation.

### 3.2 Segmentation
Text is divided into fixed-size overlapping segments of approximately 300 words with 50 words of overlap.

**Justification.** The embedding model accepts a maximum of 256 word-piece tokens; input beyond this is silently truncated, so segments must fit within that bound. Overlap ensures that a sentence spanning a segment boundary appears intact in at least one segment, preventing loss of retrievable content at boundaries. Segment size is treated as a **tunable parameter and validated by ablation** at 150, 300 and 600 words (§8.4) rather than asserted.

**Alternative considered.** Semantic or recursive segmentation, which splits on structural boundaries rather than fixed counts, is expected to produce more topically coherent segments. It is deferred as future work on grounds of implementation complexity within the available schedule. ⟨FILL: adjust if you implement it.⟩

### 3.3 Audio ingestion
Audio is transcribed using faster-whisper, an optimised implementation of Whisper [16], which emits text segments annotated with start and end times. Transcripts are segmented identically to documents, with timestamps carried into segment metadata so that a citation can reference a position within a recording.

**Alternative considered and rejected.** Native audio embeddings via contrastive audio-language pretraining [17] were considered. They were rejected because the corpus consists of speech, whose information content is linguistic rather than acoustic; transcription both matches the content type and preserves the temporal information required for citation. ⟨FILL: cite CLAP correctly.⟩

### 3.4 Image ingestion
Images are processed along two complementary paths. A CLIP vision encoder [11], [12] produces a semantic embedding representing image content. In parallel, Tesseract OCR [18] extracts any literal text present, which is indexed as ordinary text.

**Justification for both paths.** The two capture different information: the visual embedding supports queries describing what an image *depicts*, while OCR supports queries containing text *within* the image, such as an identifier or a name. Neither subsumes the other.

### 3.5 Provenance metadata
Every segment carries, from creation, a record comprising segment identifier, source path, modality, and location (page number for documents, start and end times for audio). This metadata is the mechanism by which citation is possible; it is created at ingestion and never discarded. ⟨FILL: reference your schema definition.⟩

## 4. Indexing Methodology

Two vector collections are maintained in ChromaDB:

| Collection | Model | Dimensions | Contents |
|---|---|---|---|
| `text_index` | `all-MiniLM-L6-v2` [4] | 384 | Document segments, transcript segments, OCR text |
| `image_index` | OpenCLIP ViT-B/32 [11], [12] | 512 | Image embeddings |

**Justification for separation.** The two models produce vectors of different dimensionality in unrelated spaces, so a single collection is not merely inadvisable but ill-defined. Furthermore, CLIP's text encoder truncates at 77 tokens, making it unsuitable for document-length passages. See ADR-003.

**Approximate nearest-neighbour search.** ChromaDB indexes vectors using hierarchical navigable small-world graphs [7], giving approximately logarithmic search complexity. At the scale of this project (⟨FILL: approximate segment count⟩) exact search would also be tractable; the approximate index is adopted for architectural correctness and scalability rather than present necessity. **This is stated explicitly rather than implied**, since claiming a performance benefit not observed at our scale would be unsupported.

## 5. Retrieval Methodology

A textual query is embedded by both models and used to search both collections. An uploaded image is embedded by the CLIP vision encoder to retrieve similar images, while OCR text extracted from it queries the text collection. A spoken query is transcribed by the same Whisper model and thereafter treated as text.

**Cross-modal result merging.** Text-image similarities produced by CLIP are systematically lower in magnitude than text-text similarities, a documented property of contrastively-trained multimodal encoders known as the modality gap [13]. Merging result lists by raw similarity score would therefore rank images below text results irrespective of relevance. Results are consequently merged by **rank** rather than score, following rank-fusion practice [9]. See ADR-007. ⟨FILL: state your merge policy precisely — e.g. interleaving, or RRF with parameter k.⟩

**Top-K selection.** The K highest-ranked segments are passed to generation, with K = 5 by default. K is validated by ablation at 3, 5 and 10 (§8.4). Larger K supplies more context but degrades attention to mid-prompt content [23] and increases latency.

## 6. Generation Methodology

Retrieved segments are assembled into a numbered context block and supplied to a 4-bit quantized Llama 3.2 model served locally by Ollama. Quantization reduces memory from approximately 6 GB to approximately 2 GB with limited quality loss [29], [30], which is what permits execution on the target hardware.

The prompt instructs the model to answer using only the supplied context, to annotate each claim with the bracketed index of its supporting segment, and to state explicitly when the context does not contain the answer. Sampling temperature is set low (⟨FILL: value⟩) to favour faithfulness over variety.

**Citation validation.** Emitted citation markers are checked against the set of supplied segments; markers not corresponding to a supplied segment are removed before display. Each citation is rendered alongside the retrieved text so that a user can verify support directly. This reduces but does not eliminate unsupported generation [22]; the limitation is stated rather than concealed.

## 7. Data Methodology

**Corpus.** ⟨FILL: N⟩ files spanning PDF, DOCX, PNG/JPG and WAV/MP3. Sampling is **purposive rather than random**: the corpus is constructed to include cross-modal pairs — an image and a document addressing the same subject, and an audio recording discussing a subject also present in a document — so that cross-modal retrieval can be exercised rather than assumed.

**Gold-standard question set.** ⟨FILL: N⟩ text queries, ⟨FILL: N⟩ cross-modal queries and ⟨FILL: N⟩ negative controls were authored **before implementation began**, each annotated with the segment expected to be retrieved. Authoring the evaluation set in advance prevents the system from being tuned, consciously or otherwise, to the questions used to evaluate it.

**Disclosed limitation.** The gold set was authored by the same team that designed the system, which risks question phrasing that unconsciously favours the chosen architecture. Mitigation: external participants author additional questions during the evaluation phase, and results on the external subset are **reported separately** from results on the internal set. ⟨FILL: confirm this happens in Chapter 12.⟩

**Ethics and licensing.** All corpus files are owned by the team or freely redistributable; no confidential material is included in the submitted corpus. Local execution means no corpus content is transmitted to any external service at any stage.

## 8. Evaluation Methodology

Metrics, targets and protocol are fixed in advance of any results.

### 8.1 Retrieval

| Metric | Definition | Target |
|---|---|---|
| **Recall@5** | Proportion of queries for which a correct segment appears in the top 5 | ≥ 0.80 |
| **MRR** | Mean of the reciprocal rank of the first correct segment | ≥ 0.65 |
| **Cross-modal Recall@5** | Recall@5 restricted to text-to-image queries | ≥ 0.70 |

Both Recall@5 and MRR are reported because they measure different properties: whether a relevant segment was found at all, and how highly it was ranked. Definitions follow standard retrieval evaluation practice [10].

### 8.2 Generation

Automatic overlap metrics such as BLEU and ROUGE are **not** used: a correct answer expressed in different wording is penalised, while a fluent but unsupported answer may score well. Answers are instead rated by humans on four dimensions following RAG evaluation practice [31]:

| Dimension | Rater's question |
|---|---|
| Faithfulness | Is every claim supported by the cited segment? |
| Answer relevance | Does the answer address the question asked? |
| Context relevance | Were the retrieved segments actually useful? |
| Citation correctness | Do citation markers point to segments that support the claims? |

Target: mean faithfulness ≥ 4/5.

**Rating protocol.** ⟨FILL: N ≥ 3⟩ raters, of whom at least one is external to the team. A written rubric defining each point on the 1–5 scale is agreed before rating begins. When configurations are compared, raters are not told which configuration produced which answer. At least ⟨FILL: N⟩ items are rated by two raters, and inter-rater agreement is reported. Results are reported as mean **and range**, since identical means can conceal very different distributions.

### 8.3 System performance

Measured on ⟨FILL: exact reference machine — CPU model, RAM, OS⟩. Reported: indexing throughput per modality, retrieval latency, end-to-end latency, and peak memory. **Median and worst case** are reported rather than best case.

| Measure | Target |
|---|---|
| Retrieval latency | < 1 s |
| End-to-end latency | < 15 s |
| PDF indexing | ≥ 1 page/s |
| Whisper WER on test clips | < 15% |

### 8.4 Ablation studies

| Ablation | Variants | Question answered |
|---|---|---|
| Segment size | 150 / 300 / 600 words | Was the segmentation parameter chosen or guessed? |
| Top-K | 3 / 5 / 10 | Does additional context help or dilute? [23] |
| Cross-modal merge policy | Rank-based vs score-based | Does the modality gap [13] affect *our* corpus measurably? |

### 8.5 Offline verification

After indexing completes, all network interfaces are disabled. The system must then ingest a new file, answer a text query, answer an image query, transcribe and answer a spoken query, and render citations, with no functional degradation. The result of this test is reported as a pass/fail criterion for Objective O6.

## 9. Threats to Validity

| Type | Threat | Mitigation |
|---|---|---|
| **Internal** | Observed retrieval quality may reflect corpus properties rather than model capability | Ablations (§8.4) with the corpus held fixed across comparisons |
| **External** | Results obtained on ⟨FILL: N⟩ English files on one hardware configuration may not generalise to larger, multilingual or noisier corpora | Scope limits stated explicitly; no extrapolation claimed |
| **Construct** | Recall@5 measures retrieval, not answer usefulness | Both retrieval metrics and human answer ratings reported |
| **Conclusion** | With ⟨FILL: N⟩ questions, a single item shifts Recall@5 by ⟨FILL: 1/N⟩; small differences are not meaningful | Sample size reported beside every figure; no claims made on differences within one item's width |
| **Bias** | Gold set authored by the system's designers | External participants author additional questions; those results reported separately (§7) |

---

## Pre-submission checklist

- [ ] Every `⟨FILL⟩` replaced
- [ ] Every section rewritten in the team's own words
- [ ] Every design decision names the alternatives considered and the reason for rejection
- [ ] At least three decisions cite literature
- [ ] All seven ADRs written in [`docs/decisions/`](../docs/decisions/)
- [ ] Metrics and targets fixed **before** any results were collected
- [ ] Human rating protocol specifies rater count, external participation, written rubric, blinding, and agreement reporting
- [ ] Threats-to-validity section present and honest
- [ ] Citation numbers renumbered in order of first appearance
- [ ] Every citation verified against the actual source
