# Literature Matrix, Search Log & Reading Notes

> Working document for Day 3. Method is in [Chapter 3 Part 1](../docs/chapters/ch03-literature-review-and-methodology.md); the annotated source list is in [Chapter 3 Part 2](../docs/chapters/ch03-literature-review-and-methodology.md).
>
> **This file is not submitted.** It is the raw material you write the review *from*. Keep it messy and honest.

---

## 1. Search log

Fill in as you search. When a panel asks "how did you find these papers?", this is the answer.

| Date | Source | Query | Scanned | Kept | Notes |
|---|---|---|---|---|---|
| ⟨date⟩ | Google Scholar | `"multimodal RAG" AND offline` | | | |
| ⟨date⟩ | Google Scholar | `("retrieval-augmented generation" OR RAG) AND multimodal AND ("on-device" OR local)` | | | |
| ⟨date⟩ | Google Scholar | **Forward citations of Lewis et al. 2020**, filtered `multimodal` | | | ⚠️ mandatory — see Ch 3 §5.3 |
| ⟨date⟩ | Google Scholar | **Forward citations of MuRAG (Chen et al. 2022)** | | | ⚠️ mandatory |
| ⟨date⟩ | ACL Anthology | `cross-modal retrieval citation attribution` | | | |
| ⟨date⟩ | Semantic Scholar | Citation graph of CLIP → filter "modality gap" | | | |
| ⟨date⟩ | arXiv | `spoken content retrieval embedding` | | | |
| ⟨date⟩ | Connected Papers | Graph seeded on Lewis et al. 2020 | | | |

**Saturation reached?** ☐ Yes ☐ No — *(new searches keep returning papers already seen)*

---

## 2. Verification tracker

**Every row must be ticked before the reference enters the report.** An incorrect citation found in the viva taints everything else.

| # | Short name | Authors verified | Venue verified | Year verified | Read to | Verified by |
|---|---|---|---|---|---|---|
| 1 | word2vec | ☐ | ☐ | ☐ | Pass 1 | |
| 2 | Transformer | ☐ | ☐ | ☐ | Pass 1 | |
| 3 | BERT | ☐ | ☐ | ☐ | Pass 1 | |
| 4 | Sentence-BERT | ☐ | ☐ | ☐ | **Pass 2** | |
| 5 | BM25 | ☐ | ☐ | ☐ | Pass 1 | |
| 6 | DPR | ☐ | ☐ | ☐ | **Pass 2** | |
| 7 | HNSW | ☐ | ☐ | ☐ | **Pass 2** | |
| 8 | FAISS | ☐ | ☐ | ☐ | Pass 1 | |
| 9 | Reciprocal Rank Fusion | ☐ | ☐ | ☐ | Pass 1 | |
| 10 | BEIR | ☐ | ☐ | ☐ | Pass 1 | |
| 11 | CLIP | ☐ | ☐ | ☐ | **Pass 3** | |
| 12 | OpenCLIP | ☐ | ☐ | ☐ | Pass 1 | |
| 13 | Modality gap | ☐ | ☐ | ☐ | **Pass 2** | |
| 14 | BLIP | ☐ | ☐ | ☐ | Pass 1 | |
| 15 | SigLIP | ☐ | ☐ | ☐ | Pass 1 | |
| 16 | Whisper | ☐ | ☐ | ☐ | **Pass 2** | |
| 17 | CLAP | ☐ | ☐ | ☐ | Pass 1 | |
| 18 | Tesseract | ☐ | ☐ | ☐ | Pass 1 | |
| 19 | REALM | ☐ | ☐ | ☐ | Pass 1 | |
| 20 | RAG (Lewis) | ☐ | ☐ | ☐ | **Pass 3** | |
| 21 | Fusion-in-Decoder | ☐ | ☐ | ☐ | Pass 1 | |
| 22 | Hallucination survey | ☐ | ☐ | ☐ | Pass 1 | |
| 23 | Lost in the Middle | ☐ | ☐ | ☐ | Pass 1 | |
| 24 | Self-RAG | ☐ | ☐ | ☐ | Pass 1 | |
| 25 | Corrective RAG | ☐ | ☐ | ☐ | Pass 1 | |
| 26 | RAG survey (Gao) | ☐ | ☐ | ☐ | Pass 1 | |
| 27 | MuRAG | ☐ | ☐ | ☐ | **Pass 2** | |
| 28 | LLM.int8() | ☐ | ☐ | ☐ | Pass 1 | |
| 29 | GPTQ | ☐ | ☐ | ☐ | Pass 1 | |
| 30 | AWQ | ☐ | ☐ | ☐ | Pass 1 | |
| 31 | RAGAS | ☐ | ☐ | ☐ | Pass 1 | |

---

## 3. Synthesis matrix

Mark ✅ where a paper contributes to a theme. **Read down a column to write that theme's paragraph.**

| Paper | T1 Representation | T2 Retrieval | T3 Cross-modal | T4 Speech | T5 Grounding | T6 Multimodal RAG | T7 Offline |
|---|---|---|---|---|---|---|---|
| [2] Transformer | ✅ | | | | | | |
| [4] Sentence-BERT | ✅ | ✅ | | | | | ✅ small |
| [5] BM25 | | ✅ baseline | | | | | ✅ |
| [6] DPR | | ✅ | | | | | |
| [7] HNSW | | ✅ | | | | | ✅ embedded |
| [9] RRF | | ✅ | ✅ merge | | | | |
| [11] CLIP | ✅ | ✅ | ✅ core | | | ✅ | ✅ |
| [13] Modality gap | | | ✅ critical | | | ✅ | |
| [16] Whisper | | | | ✅ core | | | ✅ |
| [17] CLAP | | | ✅ | ✅ rejected | | | |
| [18] Tesseract | | | ✅ OCR path | | | | ✅ |
| [20] RAG | | ✅ | | | ✅ core | ✅ | ❌ assumes server |
| [22] Hallucination | | | | | ✅ | | |
| [23] Lost in Middle | | ✅ top-K | | | ✅ | | |
| [26] RAG survey | | | | | ✅ taxonomy | ✅ | |
| [27] MuRAG | | | ✅ | | ✅ | ✅ closest | ❌ |
| [29] GPTQ | | | | | | | ✅ core |
| [31] RAGAS | | | | | ✅ eval | | |

**Diagnostic questions:**
- Which column has the fewest marks? → likely a thin theme; merge it or find more sources.
- Which column has **no** system marked ✅ across *all* of T3, T4, T5 **and** T7? → **that is your gap, found empirically.**

---

## 4. Reading notes — Pass 2 papers

Duplicate this block per paper. Complete it *immediately* after reading; memory decays fast.

### 📄 ⟨Short name⟩

- **Citation:** ⟨Authors, "Title," Venue, Year⟩
- **Theme(s):** ⟨T1–T7⟩
- **Read to:** Pass ⟨1/2/3⟩ · **By:** ⟨member⟩ · **Date:** ⟨date⟩

**Problem it solved** *(what was broken before this existed)*
> ⟨…⟩

**Key idea — in your own words** *(if you cannot paraphrase it, you have not understood it)*
> ⟨…⟩

**Method** *(at whiteboard level)*
> ⟨…⟩

**Results — and what was actually measured**
> ⟨…⟩

**Limitations the authors themselves state**
> ⟨…⟩

**Relevance to RAGNova** *(what we take, what we reject, and why — this field is what turns a summary into a review)*
> ⟨…⟩

**Quotable claim + location** *(for anything you may need to cite precisely)*
> ⟨…⟩

---

### Assigned Pass-2 reading

| Member | Papers |
|---|---|
| ⟨Member 1⟩ | [20] RAG · [6] DPR |
| ⟨Member 2⟩ | [11] CLIP · [13] Modality gap |
| ⟨Member 3⟩ | [16] Whisper · [27] MuRAG |

---

## 5. Gap pressure-test

Before committing, answer each. If any answer is weak, narrow the gap.

| Candidate counter-example | Our answer |
|---|---|
| "ChatGPT with file upload already does this" | ⟨…⟩ |
| "LangChain / LlamaIndex has multimodal RAG" | ⟨…⟩ |
| "NotebookLM does documents and audio" | ⟨…⟩ |
| "MuRAG [27] already did multimodal RAG" | ⟨…⟩ |
| ⟨anything found in the forward-citation search⟩ | ⟨…⟩ |

**Final gap statement (our own words, 4 moves):**

> ⟨…⟩
