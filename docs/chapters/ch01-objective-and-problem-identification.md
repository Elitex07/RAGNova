# Chapter 1 — Objective & Problem Identification (Day 1)

> **Purpose of this chapter.** By the end of it, every team member should be able to stand in front of a professor and explain — without notes — what we are building, why every component exists, what the alternatives were and why we rejected them, what is deliberately out of scope, and how we will *prove* the system works. This chapter is deliberately long. It is the conceptual foundation for all twelve chapters that follow; if this one is solid, the rest is mostly typing.

---

## ⚠️ Before you start this chapter

> **Have you never installed VS Code, or never opened a terminal? Do [Chapter 0 — Getting Started From Absolute Zero](ch00-getting-started-from-zero.md) first.** It takes about 90 minutes and assumes nothing at all.
>
> Chapter 0 covers: the terminal, installing VS Code and Python, what a neural network actually is, what an API is, and — importantly for §1.5 below — a ten-minute decoder for the maths notation (`Σ`, `‖A‖`, dot products, Big-O). This chapter uses all of it from the first page.
>
> **Already comfortable with Python, pip, and virtual environments?** Skip Chapter 0 and continue here.

## How to read this chapter

| Part | What it does | Time |
|---|---|---|
| **Part 1 — LEARN** | The theory. Every term in the problem statement, taken apart down to the mechanism. | ~2 hours, read carefully |
| **Part 2 — DECIDE** | Turns theory into the formal "Problem Identification" section a report needs: problem, gap analysis, objectives, scope, assumptions, constraints, risks. | ~1 hour, discuss as a team |
| **Part 3 — BUILD** | Day 1 deliverables and hands-on exercises. | ~2 hours |
| **Part 4 — CHECK** | Self-test with an answer key. Viva practice. | ~30 min |

**Learning outcomes.** After this chapter you can explain: next-token prediction, why hallucination is structural rather than a bug, why RAG beats fine-tuning for our use case, what an embedding is and how the geometry works, how a vector database finds neighbours without comparing everything, how CLIP puts pictures and sentences in one space, why speech becomes text before it becomes searchable, and how model quantization is what makes "offline on a laptop" possible at all.

---

# Part 1 — LEARN

Our problem statement, once more:

> *"Design and build a multimodal Retrieval-Augmented Generation (RAG) system leveraging a LLM for OFFLINE mode that can ingest, index, and query diverse data formats such as DOC, PDF, Images, and Voice recordings within a unified semantic retrieval framework."*

Ten loaded terms hide in that sentence: *multimodal, retrieval-augmented, generation, LLM, offline, ingest, index, query, unified, semantic*. We take them one at a time, and we do not stop at the dictionary definition — we go down to the mechanism, because the mechanism is what you will be asked about.

---

## 1.1 What an LLM actually is (mechanically)

### 1.1.1 The one-sentence version, then the unpacking

A Large Language Model is a neural network trained to answer exactly one question, over and over: *given this sequence of text so far, what is the most likely next piece of text?*

> **New here?** A *neural network* is simply a very large mathematical function with billions of adjustable numbers ("weights") inside it. Numbers go in, numbers come out. **Training** nudges those weights over billions of examples until the outputs become useful; **inference** is running the finished network with the weights frozen. **We only ever do inference** — we never train anything. Full explanation in [Chapter 0 §B.1](ch00-getting-started-from-zero.md#b1-what-a-neural-network-actually-is).

That is genuinely all it does. Every capability you have seen — answering questions, writing code, summarising — is an emergent consequence of doing next-token prediction extremely well at very large scale. Understanding this is not trivia; it directly explains hallucination (§1.2), and hallucination is the entire reason our project exists.

### 1.1.2 Tokens: the unit LLMs actually read

Models do not read characters, and they do not read words. They read **tokens** — sub-word fragments produced by a tokenizer using an algorithm like Byte-Pair Encoding (BPE).

BPE works by starting from individual characters and repeatedly merging the most frequent adjacent pair, building a fixed vocabulary (typically 32,000–128,000 entries). The result:

```
"Retrieval-Augmented Generation is offline"
   ↓ tokenizer
["Retrie", "val", "-", "Aug", "mented", " Generation", " is", " offline"]
   ↓ vocabulary lookup (each token → an integer ID)
[45231, 831, 12, 9042, 27718, 51002, 374, 18043]
```

Useful rules of thumb: **1 token ≈ 0.75 English words**, so 1,000 tokens ≈ 750 words ≈ 1.5 pages. Common words are single tokens; rare technical words and names split into several. This matters to us in two concrete places: (a) the LLM's context window is measured in tokens, which caps how much retrieved material we can paste into a prompt (Chapter 10); (b) embedding models have a maximum input length in tokens, which caps our chunk size (Chapter 6).

### 1.1.3 From tokens to prediction: embeddings, attention, layers

Inside the model:

1. **Embedding layer.** Each token ID becomes a vector of numbers (e.g. 3072 numbers for a 3B model). This is a lookup table learned during training. *Note this well — the idea of "meaning as a vector" is not something we bolt on later for search; it is how language models represent everything internally. Our search embeddings in §1.5 come from the same family of ideas.*

2. **Transformer blocks (stacked, e.g. 28 of them).** Each block does two things:
   - **Self-attention:** every token computes a relevance score against every other token in the sequence and pulls in a weighted mixture of their information. This is how the model resolves "it" to the right noun, how it connects a question at the end of a prompt to a fact at the start. Cost grows roughly with the square of sequence length — which is why very long prompts are expensive, and why we retrieve a few good chunks instead of pasting entire documents.
   - **Feed-forward network:** a per-token transformation where most of the model's factual "knowledge" is generally believed to be stored.

3. **Output layer.** The final token's vector is projected onto the vocabulary, producing a score for every possible next token, then **softmax** converts scores into a probability distribution summing to 1.

4. **Sampling.** A token is chosen from that distribution. *Temperature* controls the sharpness: temperature 0 always takes the highest-probability token (deterministic, factual); higher temperature flattens the distribution and increases variety (creative, riskier). **In Chapter 10 we set temperature low (0–0.2), because in a citation-grounded system we want faithfulness, not creativity.**

5. **Append and repeat.** The chosen token is appended to the sequence and the whole process runs again for the next token. This loop is why generation is inherently sequential and why long answers take longer.

### 1.1.4 How a model gets from "next word" to "helpful assistant": training stages

| Stage | What happens | Result |
|---|---|---|
| **Pretraining** | Next-token prediction over trillions of tokens of web text, books, code. Costs millions of dollars, months of GPU time. | A **base model**: knows language and facts, but just continues text — ask it a question and it may generate more questions. |
| **Supervised fine-tuning (SFT) / instruction tuning** | Further training on curated (instruction, good response) pairs. | An **instruct model**: follows instructions, answers questions. |
| **Preference optimisation (RLHF / DPO)** | Trained on human comparisons of which of two responses is better. | Helpful, harmless tone; better format adherence. |

**Practical consequence for us:** always download the *instruct* variant (e.g. `llama3.2:3b-instruct`). A base model will ignore our carefully written RAG prompt. We do none of this training ourselves — Chapter 5 downloads an already-instruct-tuned model. Training even the smallest of these is far outside a 14-day student project, and that is a legitimate, defensible scoping decision, not a shortcut.

### 1.1.5 What "3B parameters" means, and the memory arithmetic

**Parameters** are the learned numbers (weights) inside the network. A "3B model" has ~3 billion of them. Memory needed is roughly *parameters × bytes per parameter*:

| Precision | Bytes/param | 3B model | 7B model | Notes |
|---|---|---|---|---|
| FP32 (full) | 4 | ~12 GB | ~28 GB | Training precision. Impossible on our laptops. |
| FP16 (half) | 2 | ~6 GB | ~14 GB | Standard GPU inference. Still too heavy. |
| **INT8** | 1 | ~3 GB | ~7 GB | Minor quality loss. |
| **INT4 (Q4_K_M)** | ~0.55 | **~2 GB** | **~4.4 GB** | Small quality loss. **This is what makes our project possible.** |

This compression is called **quantization** — storing each weight with fewer bits. A weight that was `0.4172358` becomes one of 16 possible values in a small range. Accuracy drops slightly (measurably, a few percent on benchmarks); memory drops 4×–8×. Modern schemes like `Q4_K_M` quantize different layers to different precision, protecting the layers most sensitive to error.

Add to the weights a **KV cache** — memory that stores attention keys/values for tokens already processed, so they need not be recomputed each step. It grows with context length and typically adds a few hundred MB to a couple of GB at our scale. Budget accordingly (full table in §1.9).

**Take-away:** a 3B instruct model quantized to 4-bit occupies about 2 GB and generates roughly 5–15 tokens/second on a modern laptop CPU. That is genuinely usable for our demo. This single fact is what turns "offline RAG" from a research aspiration into a Day-5 task.

---

## 1.2 Why LLMs hallucinate — and why it is structural, not a bug

A **hallucination** is fluent, confident, false output. Three mechanisms cause it, and each one maps to a design decision we make later.

**Mechanism 1 — The model must always output something.** The final softmax always yields a probability distribution over the vocabulary; there is no "null" token meaning *I have no idea*. Even for a question it has never seen, some token has the highest probability, and generation proceeds. Fluency is guaranteed by the architecture; truth is not.

**Mechanism 2 — Parametric memory is lossy compression.** Trillions of tokens of training data are compressed into a few billion parameters. That is compression by orders of magnitude, and it is lossy. The model retains statistical patterns — "papers of this type usually cite an author, a year, a journal" — while the specific true triple may be blurred. So it emits a *plausible-shaped* citation with wrong details. This is exactly why hallucinations look so credible: they are correct in form, wrong in content.

**Mechanism 3 — It cannot know what it does not know.** Fluency and accuracy come from the same next-token machinery, so the model's confidence signal does not reliably separate "I learned this well" from "I am pattern-completing." Calibration research exists, but no small local model gives us a trustworthy "I don't know."

**And a fourth, decisive one for us:** the model was never trained on your files. Your lab report, your lecture recording, your screenshot of an email — none of it was in the training data. There is no amount of prompting that recovers information the model never saw.

**Conclusion.** We must supply the facts at question time and *constrain* the model to use only those facts. That is RAG.

---

## 1.3 The four ways to give an LLM your data — and why we choose RAG

This section matters enormously in a viva. Examiners ask "why not just fine-tune?" You need a real answer.

| Approach | How it works | Fatal problems for us |
|---|---|---|
| **1. Fine-tuning** | Continue training the model on your documents so knowledge enters the weights. | Needs GPUs and hours-to-days per run. Must be redone for every new file. Teaches *style* far more reliably than *facts*. Risks catastrophic forgetting. **Produces no citations** — knowledge dissolves into weights, so you cannot point back to page 4 of a PDF. Still hallucinates. |
| **2. Long-context stuffing** | Paste all documents into every prompt. | Context windows are finite (4k–128k tokens; our 3B model realistically 8k). A 200-file corpus is millions of tokens. Attention cost grows ~quadratically, so it is slow. Documented "lost in the middle" effect: models attend poorly to material buried mid-prompt. |
| **3. Keyword search + manual reading** | Ctrl+F / Elasticsearch, human reads results. | Misses synonyms and paraphrase (§1.4). Cannot search images by description at all. No synthesised answer. |
| **4. RAG** ✅ | At question time, semantically retrieve the few most relevant passages and paste **only those** into the prompt with an instruction to answer from them and cite them. | Requires building a retrieval system — which is precisely the engineering we want to learn. |

**Why RAG wins for RAGNova, stated for the report:**

1. **Adding a file costs seconds, not a training run.** Index once, immediately queryable.
2. **Citations come free.** Every retrieved chunk carries metadata about where it came from, so the answer can point back at `notice.pdf, page 2`. Objective O4 is *only* achievable this way.
3. **Hallucination is measurably reduced.** The prompt says "answer only from the context below; if the context does not contain the answer, say so." A small model constrained to a supplied passage is far more reliable than the same model recalling from memory.
4. **It works with a small model.** RAG shifts the burden from *knowing* to *reading*. Reading and summarising a supplied paragraph is a much easier task than recalling a fact — which is exactly why a 3B model is sufficient. **This is the key insight that makes the offline requirement achievable.**
5. **Modality-agnostic by design.** Retrieval does not care whether a chunk came from a PDF, an OCR'd screenshot, or a Whisper transcript. That property is what lets one architecture satisfy the whole multimodal requirement.

### 1.3.1 The two halves of a RAG system (memorise this diagram)

RAG has an **offline/indexing** phase (slow, run once per file) and an **online/query** phase (fast, runs per question). Confusing them is the most common beginner error.

```
════════ INDEXING (offline, once per file) ════════

 PDF   DOCX   PNG/JPG   WAV/MP3
  │      │       │         │
  │      │       │         └─► Whisper ──► transcript + timestamps
  │      │       └─► CLIP image embedding
  │      │           └─► Tesseract OCR ──► text found inside image
  └──────┴─► PyMuPDF / python-docx ──► raw text
                             │
                             ▼
                   CHUNKING (~300 words, ~50 overlap)
                             │
                             ▼
              EMBEDDING MODEL (text → 384 numbers)
                             │
                             ▼
        ┌────────────── ChromaDB ──────────────┐
        │  vector  +  text  +  metadata:       │
        │  {source, page/timestamp, modality}  │
        └──────────────────────────────────────┘

════════ QUERY (online, per question, target < 10 s) ════════

 User question / uploaded image / spoken query
              │
              ▼
     embed the query (same model family)
              │
              ▼
     nearest-neighbour search in ChromaDB → top-K chunks
              │
              ▼
     build prompt:  [system rules] + [chunk 1..K with IDs] + [question]
              │
              ▼
     local LLM (Ollama) generates answer with [1][2] markers
              │
              ▼
     UI renders answer; citation [1] expands to source + page/timestamp
```

Everything in Chapters 6–9 builds the top half. Chapter 10 builds the bottom half. Chapter 11 wraps it in a UI.

---

## 1.4 "Semantic": why keyword search is not enough

Traditional search — `Ctrl+F`, SQL `LIKE '%car%'`, and even statistical methods like TF-IDF and BM25 — matches **surface strings**. Three failure modes we cannot accept:

1. **Synonymy.** Query "car"; document says "automobile" or "vehicle." Zero matches, despite perfect relevance.
2. **Paraphrase.** Query "how do I make the model stop inventing facts?"; document says "techniques for mitigating hallucination in generative systems." No lexical overlap of substance.
3. **No cross-modal capability at all.** A photograph contains no words. Keyword search over images is structurally impossible without captions.

To be fair to keyword search, it has a genuine strength: **exact matching of rare strings** — an invoice number `INV-88213`, an error code, a specific surname. Embeddings are sometimes weak on these, because a rare alphanumeric string carries little semantic signal. Production systems therefore use **hybrid search**: combine BM25 keyword scores with embedding similarity scores (commonly via Reciprocal Rank Fusion). We note this now and revisit it as an optional enhancement in Chapter 10 — it is an excellent "future work" item for the report, and an honest answer if an examiner asks about the limits of embeddings.

---

## 1.5 Embeddings: meaning as geometry

This is the intellectual core of the entire project. Take your time here.

### 1.5.1 The intuition

An **embedding model** is a neural network that reads text and outputs a fixed-length list of numbers — a **vector** — such that *texts with similar meaning produce vectors that point in similar directions*.

Our model, `all-MiniLM-L6-v2`, outputs **384 numbers** per input:

```
"The cat sat on the mat"   → [ 0.021, -0.153,  0.078, ... ]   (384 values)
"A feline rested on a rug" → [ 0.019, -0.147,  0.081, ... ]   ← very close
"Quarterly revenue rose"   → [-0.204,  0.331, -0.012, ... ]   ← far away
```

The 384 numbers are **not** individually interpretable — dimension 57 is not "animal-ness." Meaning lives in the *overall direction* of the vector, distributed across all dimensions. This is called a **distributed representation**.

### 1.5.2 How this idea developed (useful for the literature review in Chapter 3)

- **One-hot / bag-of-words.** Every word is a vector with a single 1. Any two distinct words are equally dissimilar — "cat" is exactly as far from "kitten" as from "database." No semantics whatsoever.
- **Word2Vec / GloVe (2013–2014).** Built on the *distributional hypothesis*: words appearing in similar contexts have similar meanings. Trained by predicting a word from its neighbours. Produced the famous arithmetic `king − man + woman ≈ queen`, demonstrating that geometric structure encodes semantic relationships. Limitation: one fixed vector per word — "bank" (river) and "bank" (money) collapse into one.
- **Contextual embeddings — BERT (2018).** A transformer produces a *different* vector for a word depending on its sentence. Solves polysemy. But BERT's raw outputs are per-token and, out of the box, poor for sentence-level similarity comparison.
- **Sentence-BERT / sentence-transformers (2019).** Takes a BERT-family model and fine-tunes it specifically so that *whole-sentence* vectors are directly comparable by cosine similarity. Mechanically: run the transformer, then **mean-pool** the token vectors into one sentence vector, then train with a contrastive objective on pairs known to be similar (paraphrases, question–answer pairs, natural-language-inference entailments) versus dissimilar pairs. The training signal literally is: *pull similar pairs together, push dissimilar pairs apart, in vector space.*

This is the model family we use. Understanding that its training objective *is* the geometry we rely on removes the magic entirely.

### 1.5.3 Cosine similarity, worked by hand

> **The formula below looks worse than it is.** If `Σ`, `‖A‖`, or `·` are unfamiliar, spend ten minutes on [Chapter 0 Part C](ch00-getting-started-from-zero.md#part-c--the-maths-you-actually-need-and-the-maths-you-dont) first — it decodes all three with school-level arithmetic. In one line: `Σ` means "add these up" (a `for` loop), `A · B` means "multiply matching positions and add" , and `‖A‖` means "the length of the vector" (Pythagoras). No calculus is used anywhere in this project.

Similarity between vectors **A** and **B**:

```
                    A · B              Σ (Aᵢ × Bᵢ)
cos(θ) = ───────────────────── = ────────────────────────
            ‖A‖ × ‖B‖            √(ΣAᵢ²) × √(ΣBᵢ²)
```

Worked example in 3 dimensions (real vectors have 384; the math is identical):

```
A = [2, 1, 0]     ("cat")
B = [3, 1, 0]     ("kitten")
C = [0, 1, 4]     ("database")

A·B = 2×3 + 1×1 + 0×0 = 7
‖A‖ = √(4+1+0) = √5  ≈ 2.236
‖B‖ = √(9+1+0) = √10 ≈ 3.162
cos(A,B) = 7 / (2.236 × 3.162) = 7 / 7.071 ≈ 0.990   ← nearly identical direction

A·C = 2×0 + 1×1 + 0×4 = 1
‖C‖ = √(0+1+16) = √17 ≈ 4.123
cos(A,C) = 1 / (2.236 × 4.123) = 1 / 9.220 ≈ 0.108   ← almost unrelated
```

Interpretation: **1.0** = same direction/meaning, **0** = unrelated (orthogonal), **−1** = opposite. In practice, embedding similarities cluster in a narrow band (often 0.2–0.9), so what matters is the *ranking* of scores, not their absolute value. A cosine of 0.45 might be an excellent match in one corpus and mediocre in another — a fact that will bite us in Chapter 10 when we try to set a relevance threshold, so remember it now.

**Why cosine and not Euclidean distance?** Cosine ignores vector *length* and compares only direction. Length tends to correlate with things we do not care about, such as text length or word frequency; direction carries the meaning. Also note: if all vectors are **normalized** to length 1 (which sentence-transformers can do for you, and which we will do), then cosine similarity and Euclidean distance produce identical rankings — cosine is just faster to compute as a plain dot product. This is why production vector databases store normalized vectors.

### 1.5.4 The critical practical constraint: maximum sequence length

`all-MiniLM-L6-v2` accepts a maximum of **256 word-piece tokens** (~180–200 English words). Text beyond that is **silently truncated** — no error, no warning, just quietly discarded meaning.

This single fact dictates our chunking strategy in Chapter 6. Feed it a whole 20-page PDF and you have embedded page one and thrown away nineteen pages while believing you indexed the document. **Beginner teams lose days to this.** You now will not.

Also, one vector per chunk means each chunk should ideally cover **one topic**. A chunk spanning two unrelated subjects produces an averaged vector sitting between both, matching neither well — the "semantic smearing" problem. Good chunk boundaries are a genuine engineering concern, not a formality.

---

## 1.6 Vector databases: finding neighbours without checking everyone

### 1.6.1 The naive approach and why it eventually fails

Brute-force search: compute cosine similarity between the query vector and every stored vector, sort, take top-K. Complexity **O(N × d)** for N vectors of d dimensions.

> **Big-O in one line:** it describes how the time *grows* as your data grows, not actual seconds. `O(N × d)` = "check all N items, each costing d work" — like reading a dictionary cover to cover. `O(log N)` = "halve the search each step" — like looking a word up properly. Table of the four you'll meet in [Chapter 0 §C.6](ch00-getting-started-from-zero.md#c6-big-o-notation-on--d-and-olog-n).

For our demo scale this is genuinely fine. 200 files → maybe 5,000 chunks × 384 dims = ~2 million multiply-adds per query, a few milliseconds. **Be honest about this in the report:** at our scale, brute force works. We use a vector database for correctness of engineering, persistence, metadata filtering, and because the system should scale — not because 5,000 vectors are slow.

At 10 million vectors, brute force takes seconds per query. That is where approximate methods become necessary.

### 1.6.2 HNSW — the algorithm ChromaDB actually uses

**HNSW (Hierarchical Navigable Small World)** trades a tiny amount of accuracy for a very large amount of speed, giving roughly **O(log N)** search.

The intuition is a skip-list generalised to a graph, or an airline network:

- Build a **multi-layer graph**. Every vector is a node. The bottom layer contains all nodes, densely connected to their near neighbours. Each higher layer contains a random sample of nodes with long-range links — "international flights."
- **Search:** start at an entry point in the top (sparse) layer, greedily hop to whichever neighbour is closer to the query, until no neighbour improves. Drop to the next layer down and repeat with denser, shorter-range links. At the bottom layer you are refining among genuinely near neighbours.
- Effect: you cross the space in a few long hops, then walk the last mile precisely — instead of visiting every node.

Two parameters you will meet: **M** (links per node — higher means better recall and more memory) and **ef_search** (size of the candidate list during search — higher means better recall and slower queries). ChromaDB's defaults are sensible for us; we simply need to know these exist and what they trade off.

"Approximate" means it can occasionally miss a true nearest neighbour. Typical recall is 95–99% at large speedups — an excellent trade for search, though worth stating openly in the report's limitations.

An alternative family, **IVF (inverted file index)**, clusters vectors with k-means and searches only the nearest few clusters. FAISS is the well-known library here. We mention it in the literature review; ChromaDB's HNSW is what we ship.

### 1.6.3 Why a database and not a pickle file of numpy arrays

1. **Persistence** — index once, restart the app, data is still there.
2. **Metadata storage and filtering** — every vector carries a JSON payload (`source`, `page`, `timestamp`, `modality`). Filtering ("search only audio files") happens inside the database. **This metadata is the mechanism by which citations work** — without it there is no way to trace an answer back to page 2 of a PDF.
3. **Collections** — separate namespaces. We will use this to keep the MiniLM text index and the CLIP index apart (§1.7.4), because vectors of different dimensionality and different spaces must never be mixed.
4. **Incremental updates** — add, update, delete individual documents without rebuilding.

---

## 1.7 Multimodality and the cross-modal problem

### 1.7.1 The naive approach, and precisely why it fails

Obvious idea: embed text with a text model, images with an image model (say ResNet), audio with an audio model. Store all in one collection. Search.

This fails completely, and the reason is worth stating precisely: **the vectors live in unrelated coordinate systems.** A ResNet image vector and a MiniLM text vector are both lists of numbers, but nothing during training ever forced dimension 12 of one to mean anything related to dimension 12 of the other. Cosine similarity between them is arithmetic noise. (They may not even have the same dimensionality, in which case the operation is undefined.)

**Analogy.** Two people rate films 1–10. One rates by acting quality, the other by soundtrack. Both produce "7". The numbers are comparable in *type* but not in *meaning*. Comparing them is meaningless. Same problem, 384 dimensions.

### 1.7.2 CLIP: one shared space for pictures and sentences

**CLIP (Contrastive Language–Image Pretraining, OpenAI, 2021)** solves this by construction.

**Architecture.** Two encoders trained together:
- an **image encoder** (Vision Transformer: split image into patches, treat patches like tokens) → vector,
- a **text encoder** (transformer over the caption) → vector,
- both projected into a **shared** embedding space of the same dimensionality (512 for ViT-B/32).

**Training data.** ~400 million (image, caption) pairs scraped from the web. No manual labels — the caption *is* the label. This is why the model has such broad, open-vocabulary coverage.

**Training objective — contrastive loss, explained concretely.** Take a batch of N image–caption pairs (N is large, e.g. 32,768). Encode all N images and all N captions. Compute the full **N × N similarity matrix** of every image against every caption:

```
              caption₁  caption₂  caption₃  ...
   image₁   [   ✅        ✗        ✗      ]     ✅ = correct pair (diagonal)
   image₂   [   ✗        ✅        ✗      ]     ✗ = mismatched pair
   image₃   [   ✗        ✗        ✅      ]
```

The loss pushes the **diagonal** (true pairs) up and everything **off-diagonal** down — simultaneously in both directions (image→text and text→image). Every other item in the batch acts as a negative example, which is why huge batch sizes matter so much for CLIP. A learnable **temperature** parameter scales the similarities before the softmax, controlling how sharply the model discriminates.

**The consequence we exploit.** After training, the vector for a photo of a dog and the vector for the string "a photo of a dog" are *near each other in the same space*. So:

- **Text → image search:** embed the query "email screenshot" with CLIP's *text* encoder, run nearest-neighbour search over CLIP *image* vectors. The email screenshots come back on top. No captions, no tags, no manual labelling — ever.
- **Image → image search:** embed the uploaded image, find visually/semantically similar stored images.
- **Zero-shot classification** (a bonus capability): embed candidate label strings, see which is closest to the image.

### 1.7.3 Two honest caveats about CLIP that most student projects miss

**Caveat 1 — the 77-token limit.** CLIP's text encoder was trained on short captions and truncates at **77 tokens** (~50 words). It is therefore useless for embedding paragraphs of a research paper. CLIP is a *caption*-level model, not a *document*-level model.

**Caveat 2 — the modality gap.** Empirically, image vectors and text vectors occupy *separate cones* in CLIP space. Text–image cosine similarities cluster around a lower value (often ~0.2–0.3) than text–text similarities (often ~0.5–0.8), even when the match is perfect. Practical consequence: **you cannot simply merge a text-index score list and an image-index score list and sort by raw score** — images would always lose. In Chapter 10 we handle this by ranking each modality separately and merging by *rank* (or by normalising scores within each modality), not by raw score. Getting this right is one of the genuinely non-obvious pieces of engineering in the project, and an excellent point to highlight in the mid-term report.

### 1.7.4 The architectural decision that follows: two indexes, not one

The two caveats above force a design that is worth stating explicitly, because it is the single most important architecture decision in this project:

| Index (ChromaDB collection) | Model | Dimensions | Contains | Serves |
|---|---|---|---|---|
| `text_index` | `all-MiniLM-L6-v2` | 384 | PDF/DOCX chunks, Whisper transcript chunks, OCR text | text query → documents/transcripts |
| `image_index` | OpenCLIP ViT-B/32 | 512 | image embeddings; **also** CLIP-text embeddings for text queries at search time | text query → images; image query → images |

An image query reaching *documents* is handled by a bridge: OCR text and any caption text from the image go into `text_index`, so an uploaded screenshot can be OCR'd and its text used to search documents. Full mechanics in Chapter 8.

Write this table into your report. "One embedding model for everything" is the naive answer; knowing *why* it is wrong is what distinguishes this project.

### 1.7.5 Audio: why we transcribe instead of embedding sound directly

Two possible routes:

- **Route A — native audio embeddings** using a model like **CLAP** (Contrastive Language–Audio Pretraining, the audio analogue of CLIP). Genuinely good at *sounds*: "dog barking," "glass breaking," "jazz piano."
- **Route B — transcribe with Whisper, then treat as text.** ✅ our choice.

Justification, for the report: our audio is **speech** — lectures, voice memos, meetings. The information content is *linguistic*, and CLAP-style models capture acoustic character far better than they capture the semantics of a sentence spoken inside a recording. Transcription converts speech into exactly the representation our text pipeline already handles well, and it delivers three additional wins:

1. **Timestamps.** Whisper emits segments with start/end times, so a citation can say *"lecture3.mp3 @ 14:32"* and the UI can seek there. This directly satisfies the "view full transcript segments" requirement.
2. **Human-readable evidence.** A user can *read* the retrieved transcript to verify the answer. An audio embedding is opaque.
3. **Free reuse of infrastructure.** Transcripts flow through the same chunk → embed → store path as PDFs. No new index, no new model at query time.

Also note the elegant consequence: the **spoken query** feature uses the same Whisper model in reverse direction of the pipeline — record microphone audio → transcribe → it is now an ordinary text query. One model, two features.

### 1.7.6 Whisper, briefly

An encoder–decoder transformer trained on ~680,000 hours of multilingual audio. Audio is converted to a **log-Mel spectrogram** (a picture of frequency energy over time) in 30-second windows; the encoder reads it, the decoder generates text tokens — the same next-token prediction idea as §1.1, conditioned on audio. Sizes range `tiny → base → small → medium → large-v3`, trading accuracy for speed. We use **faster-whisper**, a CTranslate2 reimplementation that is roughly 4× faster with int8 quantization on CPU. Chapter 9 covers model choice and measuring **WER (word error rate)**.

---

## 1.8 Citation transparency: what it really requires

The problem statement asks for numbered citations that expand to the source. This is not a UI feature bolted on at the end — it is a **data-provenance requirement that constrains the entire pipeline**, and it must be designed in from Chapter 6.

Three things must hold:

1. **Every chunk carries its origin, permanently.** At ingestion time we attach metadata and never lose it:
   ```python
   {
     "chunk_id":  "notice_pdf__p2__c003",
     "source":    "data/notice.pdf",
     "modality":  "pdf",          # pdf | docx | image | audio
     "page":      2,              # for documents
     "start_s":   None,           # for audio: 872.4  → "14:32"
     "end_s":     None,
     "bbox":      None,           # optional: region on the page/image
     "text":      "…submission deadline is 21st August…"
   }
   ```
2. **The prompt must number the chunks and instruct the model to cite them.** In Chapter 10 we render context as `[1] …`, `[2] …` and instruct: *answer using only this context; mark every claim with the bracketed number of the chunk it came from.* Small models comply reasonably well when the format is shown explicitly in the prompt.
3. **The UI maps the number back to the metadata.** `[1]` expands to file, page/timestamp, the exact chunk text, and a button to open the source, seek the audio, or show image EXIF metadata.

**A caution we must design around:** the model can still emit a citation number that does not support the claim. Real systems therefore add a *verification* pass. Our practical, cheap mitigation in Chapter 10: (a) validate that every emitted `[n]` refers to a chunk we actually supplied, dropping invalid ones; (b) always display the retrieved chunk text next to the citation so a human can check in one glance. Honest limitation, honestly mitigated — exactly what a report should contain.

---

## 1.9 "Offline" taken seriously

### 1.9.1 What must be downloaded once, and what must never happen again

| Component | One-time download | Runtime network use |
|---|---|---|
| Ollama runtime | ~200 MB installer | none |
| Llama 3.2 3B Instruct (Q4) | ~2.0 GB | none |
| `all-MiniLM-L6-v2` | ~90 MB | none (cached in `~/.cache/huggingface`) |
| OpenCLIP ViT-B/32 | ~600 MB | none |
| faster-whisper `base` | ~150 MB | none |
| Tesseract OCR | ~50 MB installer | none |
| Python packages | ~2 GB (torch dominates) | none |

Total roughly **5 GB**, downloaded once. Plan this: on a hostel connection it is an overnight job, and it is the single most likely cause of a Day 5 delay.

### 1.9.2 RAM budget on an 8 GB laptop

| Consumer | RAM |
|---|---|
| Windows + browser | ~3.0 GB |
| Llama 3.2 3B Q4 weights | ~2.0 GB |
| KV cache (8k context) | ~0.5 GB |
| Embedding + CLIP + Whisper (loaded lazily) | ~1.5 GB |
| Python/Streamlit overhead | ~0.5 GB |
| **Total** | **~7.5 GB** — tight but workable |

Mitigations we will actually implement in Chapter 11: **lazy loading** (load Whisper only when audio is submitted, then release), and running heavy ingestion as a separate step from the chat app so the two never hold peak memory simultaneously. If a machine struggles, fall back to Llama 3.2 **1B** (~0.8 GB) — noticeably weaker, but the pipeline is identical, which is the point of good architecture.

### 1.9.3 The acceptance test for "offline"

State this in the report as a formal criterion, because it is unambiguous and impressive in a demo:

> **After indexing is complete, disable all networking (airplane mode / disconnect Ethernet). The system must ingest a new file, answer a text query, answer an image query, transcribe a spoken query, and render citations — with no functional degradation.**

We will actually run this test in Chapter 12 and record the result. Anyone can *claim* offline; we will demonstrate it.

---

## 1.10 How we will prove it works: evaluation metrics defined up front

Objectives that cannot be measured are not objectives. We define the metrics on Day 1 so that Chapters 7, 10 and 12 have something concrete to hit, and so the mid-term report has real numbers rather than adjectives.

**Retrieval quality** (evaluated on a hand-built set of ~20 questions where we know which chunk *should* be retrieved — we build this in Chapter 7):

| Metric | Definition | Our target |
|---|---|---|
| **Recall@5** | Fraction of questions where the correct chunk appears in the top 5 results. | ≥ 0.80 |
| **MRR** (Mean Reciprocal Rank) | Average of 1/(rank of first correct result). Rewards putting the right answer first. | ≥ 0.65 |
| **Cross-modal Recall@5** | Same, for text→image queries. | ≥ 0.70 |

**Answer quality** (human-rated, 1–5, by team members plus outside testers in Chapter 12):

| Metric | Question asked of the rater |
|---|---|
| **Faithfulness / groundedness** | Is every claim in the answer supported by the cited chunk? |
| **Answer relevance** | Does it actually answer the question asked? |
| **Citation correctness** | Do the `[n]` markers point at the chunks that support the claims? |

**System performance:**

| Metric | Target on our reference laptop |
|---|---|
| Query latency (retrieval only) | < 1 s |
| End-to-end latency (retrieval + generation) | < 15 s |
| Indexing throughput | ≥ 1 page/second for PDFs; ≈ real-time or better for audio with `base` |
| Whisper WER on our test clips | < 15% |

**Rule for the team:** if a number is not measured, it does not go in the report as a claim.

---

## 1.11 Assembling the whole picture

At this point every piece of the problem statement has a mechanism behind it:

| Requirement from the statement | Mechanism | Chapter |
|---|---|---|
| Ingest DOC, PDF | PyMuPDF / python-docx → text → chunks | 6 |
| Ingest images | OpenCLIP embedding + Tesseract OCR | 8 |
| Ingest voice recordings | faster-whisper → timestamped transcript → chunks | 9 |
| Index | ChromaDB, two collections, HNSW, rich metadata | 7 |
| Semantic query | MiniLM embeddings + cosine nearest-neighbour | 7 |
| Text → image | CLIP shared space | 8 |
| Image → text/docs | CLIP image query + OCR bridge into text index | 8 |
| Audio → everything | Whisper transcript used as a text query | 9 |
| Unified interface | Streamlit chat: text box, file upload, drag-drop, mic | 11 |
| Answer generation | Ollama + Llama 3.2 3B Instruct, low temperature | 10 |
| Numbered citations | chunk metadata + numbered prompt context + UI expander | 10, 11 |
| Offline | all models local, verified by airplane-mode test | 5, 12 |

Nothing in this project is magic. It is roughly eight well-understood components wired together carefully — and the *care* is where the marks are.

---

## 1.12 Common misconceptions, cleared now

| Misconception | Reality |
|---|---|
| "RAG means training the model on my documents." | No training occurs. Documents are retrieved and pasted into the prompt at query time. |
| "One embedding model can handle text and images." | Only if it was trained cross-modally (CLIP). A text model and an image model produce incomparable vectors. |
| "Bigger model = better RAG answers." | Beyond a point, no. With good retrieval, the task is reading comprehension over a supplied paragraph, which small models do well. Retrieval quality dominates. |
| "The vector database is where the intelligence lives." | It is a fast nearest-neighbour lookup. The intelligence is in the embedding model that produced the vectors. |
| "Citations guarantee correctness." | They guarantee *traceability*. The user must still be able to check — which is exactly why we display chunk text alongside every citation. |
| "Offline means worse in every way." | Slower and somewhat less capable, yes. But private, free, and always available. For confidential corpora it is the only acceptable option. |
| "Chunk size is a detail." | It is one of the highest-impact parameters in the system. Too large: diluted vectors and wasted context. Too small: fragments lacking the context needed to answer. |

---

# Part 2 — DECIDE: Formal Problem Identification

This is the section that goes, near-verbatim, into the Day 2 synopsis and the Day 14 report. Discuss each subsection as a team and edit the wording until all of you would say it the same way.

## 2.1 Problem statement (our formulation)

> Individuals and organisations accumulate knowledge across heterogeneous formats — text documents, scanned or captured images, and voice recordings. Existing retrieval tools fail this reality on three fronts. First, they are predominantly **lexical**: they match keywords and therefore miss semantically relevant content expressed in different words. Second, they are **siloed by modality**: a text query cannot retrieve an image, an image cannot retrieve a document, and spoken content is not searchable at all without manual transcription. Third, capable semantic and generative tools are **cloud-dependent**, which is unacceptable for confidential data, imposes recurring per-query cost, and fails entirely without connectivity.
>
> Consequently, a user holding the answer to their own question inside their own files often cannot find it. There is no unified, offline system that accepts a natural-language question — typed or spoken — and returns a synthesised, **citation-backed** answer drawn from documents, images, and audio alike.

## 2.2 Gap analysis (what exists, and what it does not do)

| Existing solution | What it does well | Gap relative to our problem |
|---|---|---|
| Windows Search / macOS Spotlight | Fast filename and full-text keyword search | Lexical only; no image understanding; no audio; no synthesised answer; no citations |
| Google Drive / OneDrive search | Some OCR and image labelling | Cloud-only; no synthesised answer over your corpus; no cross-modal query; no audio search |
| ChatGPT / Gemini with file upload | Excellent answer quality and synthesis | Cloud (privacy, cost, connectivity); limited corpus per session; no persistent multimodal index |
| LangChain / LlamaIndex demo RAG apps | Solid text RAG scaffolding | Overwhelmingly text-only; typically default to cloud embeddings and cloud LLMs; multimodal support is add-on and rarely cross-modal |
| Enterprise search (Elasticsearch) | Scale, filtering, hybrid retrieval | Requires infrastructure; no generative answering out of the box; no cross-modal semantics |
| **RAGNova (this project)** | — | Fills all four gaps simultaneously: **offline + multimodal + cross-modal + cited generative answers** |

That intersection is the novelty claim. It is modest and defensible — each individual component exists in prior work; the contribution is a *unified, fully-local integration* with citation transparency. State it exactly that honestly in the report. Overclaiming novelty is the fastest way to lose credibility in a viva.

## 2.3 Objectives (numbered and measurable)

| ID | Objective | Success criterion |
|---|---|---|
| **O1** | Ingest and index heterogeneous formats — PDF, DOCX, PNG/JPG, WAV/MP3 — into a unified vector store with full provenance metadata. | All four formats index without error; every stored chunk carries source, modality, and page/timestamp. |
| **O2** | Provide semantic (meaning-based) retrieval over all indexed content. | Recall@5 ≥ 0.80 and MRR ≥ 0.65 on a 20-question gold set; demonstrably retrieves paraphrased matches that keyword search misses. |
| **O3** | Support cross-modal retrieval: text→image, image→text/documents, audio→all. | Cross-modal Recall@5 ≥ 0.70 on a 10-query image gold set; all three directions demonstrated live. |
| **O4** | Generate answers with a locally-run LLM, constrained to retrieved context, with numbered citations. | Mean human faithfulness rating ≥ 4/5 over 20 questions; 100% of emitted citation markers resolve to a supplied chunk; system says "not found in the provided sources" when the corpus lacks the answer. |
| **O5** | Provide a unified interface accepting typed text, uploaded documents, drag-and-dropped images, attached audio, and microphone speech. | All five input paths functional from a single screen; citations expandable to source, transcript segment, or image metadata. |
| **O6** | Operate fully offline after initial setup. | Passes the airplane-mode acceptance test of §1.9.3 with zero functional degradation. |
| **O7** | Produce documentation sufficient for another student to reproduce and extend the system. | Every module documented; chapter docs cover concept, design rationale, implementation, and verification. |

## 2.4 Scope

**In scope.** The seven objectives; English-language content; a demo corpus of roughly 50–200 files; a single-user desktop application; commodity hardware (8–16 GB RAM, CPU-only).

**Out of scope** — and we say so deliberately, with a reason for each:

| Excluded | Why |
|---|---|
| Video ingestion | Adds keyframe extraction + audio track handling; time budget. Listed as future work. |
| Multi-user server deployment, authentication, access control | Orthogonal to the research question; large engineering surface. |
| Fine-tuning or training any model | Requires GPUs and data we do not have; RAG is explicitly the alternative (§1.3). |
| Real-time streaming transcription | Batch transcription satisfies every stated requirement. |
| Handwriting recognition (HTR) | Tesseract handles printed text; handwriting needs different models. |
| Guaranteed non-English performance | Whisper and CLIP have some multilingual ability; we neither test nor promise it. |
| Scale beyond ~10⁵ chunks | Architecture supports it; we do not test or tune for it. |

Scope discipline is graded. A finished, honest, well-documented system beats an ambitious half-built one every single time.

## 2.5 Assumptions

1. Team machines have ≥ 8 GB RAM and ~15 GB free disk.
2. Internet is available during setup (Chapter 5) for one-time model downloads.
3. Input documents are digital-text PDFs or DOCX; scanned-image PDFs are handled on a best-effort basis via OCR.
4. Audio is reasonably clear speech (a phone voice memo is fine; a noisy 40-person lecture hall is not guaranteed).
5. Users are non-adversarial — no security hardening against malicious file uploads is in scope.

## 2.6 Constraints

| Type | Constraint | Consequence for design |
|---|---|---|
| Hardware | CPU-only, 8 GB RAM typical | Small quantized models; lazy loading; modest corpus |
| Time | 14 days, 9 for implementation | Proven libraries only; no exotic research methods |
| Skill | Team new to RAG/ML | Beginner-friendly stack (ChromaDB, Streamlit, Ollama); heavy documentation |
| Licence | Must be free and open-source | Rules out paid APIs and non-commercial-only weights |
| Requirement | Fully offline | Rules out every hosted embedding/LLM service |

## 2.7 Risk register (identify now, mitigate later)

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Model downloads fail or are too slow | High | High | Start downloads Day 1 night; one member mirrors models to a USB drive for the others |
| R2 | Laptop too weak to run 3B model | Medium | High | Fall back to Llama 3.2 1B; architecture unchanged |
| R3 | Cross-modal search results look poor | Medium | Medium | Modality-gap handling via rank-based merge (§1.7.3); OCR bridge as a second signal |
| R4 | Whisper transcription too slow on long audio | Medium | Medium | Use `base` or `tiny`; keep demo clips under ~5 minutes; transcribe once and cache |
| R5 | Answers hallucinate despite RAG | Medium | High | Low temperature; strict prompt; citation validation; display chunk text |
| R6 | Integration crunch — three tracks don't fit together | Medium | High | Freeze the shared data schema in Chapter 5 *before* parallel work begins; integrate on Day 12, not Day 13 |
| R7 | Team member unavailable | Medium | Medium | Every module documented well enough for another member to continue; no single-owner secrets |
| R8 | Scope creep ("let's add video!") | High | Medium | §2.4 is binding; new ideas go to a `future-work.md` list, not into the sprint |

## 2.8 Stakeholders and use cases

| Stakeholder | Concrete scenario | Which objective it exercises |
|---|---|---|
| Student | "Where in my recorded lectures did the professor explain backpropagation?" → transcript snippet with timestamp | O1, O2, O4 |
| Researcher | 40 papers indexed; "which of these use contrastive learning?" with citations | O2, O4 |
| Professional | "Find the screenshot of the invoice email" → the image itself | O3 |
| Journalist / analyst | Interview recordings + photographs + notes, searched together | O1, O3 |
| Privacy-critical organisation (legal, medical, defence) | All of the above with zero data leaving the machine | O6 |

## 2.9 Expected outcomes and deliverables

1. A working offline multimodal RAG application (source code, documented).
2. Thirteen chapter documents forming a self-contained learning path.
3. Synopsis and two presentations (Days 2 and 4).
4. Evaluation results against the metrics of §1.10.
5. Human feedback log with recorded changes made in response.
6. Mid-term report (Day 14).

---

# Part 3 — BUILD: Day 1 deliverables

### 3.1 Individual work (~2 hours)

- [ ] Read Part 1 in full. Do not skim §1.5 and §1.7 — they are the conceptual core.
- [ ] Look up any unknown term in [GLOSSARY.md](../GLOSSARY.md); if it is missing, **add it** and commit. Growing the glossary is a graded documentation habit.
- [ ] Compute one cosine similarity by hand (use the §1.5.3 example, then invent your own three vectors). It takes five minutes and permanently removes the mystery from vector search.

### 3.2 Team work (~1 hour)

- [ ] **Teach-back round.** Each member explains one topic to the others without notes: (a) why RAG rather than fine-tuning, (b) what an embedding is and why cosine similarity ranks results, (c) how CLIP makes text→image search possible. Teaching is the only reliable test of understanding.
- [ ] **Agree the wording** of §2.1 (problem) and §2.3 (objectives). Edit this file directly — these paragraphs are reused verbatim on Days 2, 4 and 14, so getting them right now saves work three times over.
- [ ] **Review the risk register** (§2.7) and add anything specific to your situation (shared laptop, slow campus wifi, exam clash).

### 3.3 Corpus collection (~1 hour) — do not skip this

A retrieval system is only as demonstrable as its corpus. Build it now so every later chapter has real data.

```
data/
├── documents/     10–15 PDFs (mix: lecture notes, a paper, a scanned notice)
│                  5–8 DOCX (assignments, reports)
├── images/        10–15 images — include 3+ screenshots (an email, a chat,
│                  an error dialog), 3+ photos with visible text (a poster,
│                  a whiteboard), and a few plain photos
└── audio/         3–5 clips, 30 s to 3 min (record on your phone: a summary
                   of a lecture, a to-do list, a short interview)
```

Include deliberate **cross-modal test material** — this is what makes the demo land:
- an image *and* a document about the same topic (proves image→document retrieval),
- an audio clip mentioning a topic that also appears in a PDF (proves audio→document),
- at least one screenshot whose content is described in a document (proves text→image with a real payoff).

Write down, in `data/README.md`, five questions you expect the finished system to answer, and which files hold each answer. **This becomes the gold-standard evaluation set of §1.10.** Building the test set *before* the system is a genuine engineering discipline — it stops you from unconsciously tuning the system to flatter itself.

### 3.4 Setup head start (start tonight)

- [ ] **Every member has completed the [Chapter 0](ch00-getting-started-from-zero.md) checklist** — VS Code installed, Python 3.11 on PATH, `python --version` working. Do not carry this into Day 5; Chapter 5 assumes it is already done.
- [ ] Download and install [Ollama](https://ollama.com/download) on each machine.
- [ ] Run `ollama pull llama3.2:3b` overnight (~2 GB). Chapter 5 will otherwise begin with three hours of waiting.

The full stack is roughly 5 GB of one-time downloads (§1.9.1). On a shared or slow connection, have **one member download everything and copy the model cache to the others by USB** — this is risk R1 in §2.7, and it is the most common cause of a Day 5 delay.

---

# Part 4 — CHECK: Self-test

Answer from memory, then verify against the sections cited.

1. What exactly is an LLM trained to do, and how does that single objective explain hallucination? *(§1.1, §1.2)*
2. Give three reasons fine-tuning is the wrong tool for our problem. *(§1.3)*
3. Draw the RAG pipeline from memory, labelling which parts run at indexing time and which at query time. *(§1.3.1)*
4. What is an embedding? Why does cosine similarity, not Euclidean distance, rank results — and when are the two equivalent? *(§1.5)*
5. `all-MiniLM-L6-v2` truncates at 256 tokens. Why is that fact the reason Chapter 6 exists? *(§1.5.4)*
6. Why can't we compare a ResNet image vector with a MiniLM text vector? *(§1.7.1)*
7. Describe CLIP's training objective using the N×N matrix picture. *(§1.7.2)*
8. What is the modality gap, and what concrete bug does it cause if ignored? *(§1.7.3)*
9. Why do we need two ChromaDB collections rather than one? *(§1.7.4)*
10. Why transcribe audio instead of embedding it natively — and name two capabilities transcription unlocks. *(§1.7.5)*
11. What piece of data makes citations possible, and at which stage of the pipeline must it be created? *(§1.8)*
12. How does 4-bit quantization make offline operation feasible? Give the memory figures for a 3B model at FP16 versus Q4. *(§1.1.5)*
13. Explain HNSW search in two sentences using the airline analogy. *(§1.6.2)*
14. State the airplane-mode acceptance test. *(§1.9.3)*
15. Name the three retrieval metrics we will report, with their targets. *(§1.10)*
16. Name four things explicitly out of scope, with the justification for each. *(§2.4)*

### Answer key (compressed — expand in your own words)

1. Next-token prediction over a probability distribution; it must always emit something, its memory is lossy compression of training data, and it never saw your files → fluent-but-false output is structural.
2. No citations possible; must be redone per file and needs GPUs; teaches style more reliably than facts, and still hallucinates.
3. Indexing: parse → chunk → embed → store with metadata. Query: embed query → nearest-neighbour → build numbered prompt → LLM → cited answer.
4. A vector encoding meaning; cosine compares direction and ignores magnitude (which tracks length/frequency, not meaning); they rank identically once vectors are normalized to unit length.
5. Longer input is silently truncated, so whole documents must be split into chunks that fit — chunking strategy is therefore a first-class design problem.
6. They were trained independently; no objective ever aligned their coordinate systems, so similarity between them is noise.
7. Encode N images and N captions, form the N×N similarity matrix, push the diagonal (true pairs) up and all off-diagonal pairs down, in both directions, scaled by a learned temperature.
8. Image and text vectors sit in separate cones, so text–image scores are systematically lower than text–text scores; naively merging and sorting by raw score buries every image.
9. Different models, different dimensionalities, different spaces — MiniLM (384-d) for document text, CLIP (512-d) for images; mixing them is meaningless.
10. Our audio is speech, whose content is linguistic; transcription reuses the text pipeline and unlocks timestamped citations plus human-readable evidence (and the same model powers spoken queries).
11. Provenance metadata (source, page, timestamp, modality) attached to every chunk — created at ingestion time and never lost.
12. Storing weights in ~4 bits instead of 16 cuts a 3B model from ~6 GB to ~2 GB, fitting laptop RAM with a small accuracy cost.
13. Hop across a sparse top-layer graph using long-range links to get near the target fast, then descend into denser layers to refine locally — like international flights followed by local ones.
14. After indexing, disconnect all networking; the system must still ingest a file, answer text/image/spoken queries, and render citations with no functional loss.
15. Recall@5 ≥ 0.80, MRR ≥ 0.65, cross-modal Recall@5 ≥ 0.70.
16. Video (time budget), multi-user deployment (orthogonal), fine-tuning (no GPUs; RAG is the alternative), handwriting (needs different models), guaranteed multilingual support (untested).

---

**Next:** [Chapter 2 — Synopsis & Presentation](ch02-synopsis-and-presentation.md) — compressing everything above into a 2–3 page synopsis and a slide-by-slide PPT for Day 2.
