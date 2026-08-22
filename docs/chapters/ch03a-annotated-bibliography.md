# Chapter 3A — Annotated Bibliography

> **Companion to [Chapter 3](ch03-literature-review-and-methodology.md).** This is your raw material: ~60 sources across eleven themes, each with *what problem it solved*, *the key idea*, and — the field that matters — *what RAGNova takes from it*.
>
> **Twelve sources marked 🔍 get a deep dive** at the end of their theme: mechanism, numbers, limitations, and the exam questions they attract.
>
> ## ⚠️ Read this before using anything here
>
> **Every citation must be independently verified before it enters your report.** Author lists, venue names, volumes and years must be exact. Check on the ACL Anthology, the publisher's site, or arXiv. An incorrect citation discovered in a viva casts doubt on every other number you present.
>
> **This file is not text to paste.** It is material to read, verify, and then write about in your own words using the synthesis techniques in [Chapter 3 §1.11](ch03-literature-review-and-methodology.md). Text you did not write is text you cannot defend.
>
> **Reading depth is marked:** 🔍 = read to Pass 2 or 3 · ▪ = Pass 1 is sufficient · ○ = cite for context, abstract only.

---

## Contents

| Theme | Question it answers |
|---|---|
| [1. Representation](#theme-1--representation-meaning-as-geometry) | How did meaning become numbers? |
| [2. Retrieval](#theme-2--retrieval-from-keywords-to-vectors) | How do we search by meaning, and search fast? |
| [3. Choosing an embedding model](#theme-3--choosing-an-embedding-model-with-evidence) | ⭐ How do we justify *this* model? |
| [4. Cross-modal](#theme-4--cross-modal-one-space-for-images-and-text) | How can text retrieve an image? |
| [5. Speech](#theme-5--speech-making-audio-searchable) | How does spoken content become searchable? |
| [6. Document understanding](#theme-6--document-understanding-three-competing-philosophies) | ⭐ Parse, OCR, or treat the page as an image? |
| [7. Grounding & RAG](#theme-7--grounding-rag-and-its-descendants) | How do we stop the model inventing things? |
| [8. Why not fine-tuning](#theme-8--why-not-fine-tuning-the-empirical-case) | ⭐ Where is the evidence for ADR-001? |
| [9. Attribution & verifiability](#theme-9--attribution-and-verifiability-the-literature-behind-objective-o4) | ⭐ What does research say about citations? |
| [10. Chunking & context](#theme-10--chunking-and-context-where-practice-outruns-research) | How big should a chunk be? |
| [11. Local execution](#theme-11--local-execution-why-offline-is-now-possible) | Why does this fit on a laptop at all? |

---

## Theme 1 — Representation: meaning as geometry

**The argument this theme makes:** meaning can be encoded as position in a vector space, and the granularity of that encoding improved over a decade from words to contexts to sentences. Everything else in the project depends on this working.

| Source | Problem solved | Key idea | What RAGNova takes |
|---|---|---|---|
| ○ Mikolov, Chen, Corrado & Dean, "Efficient Estimation of Word Representations in Vector Space," *ICLR Workshop*, 2013 | One-hot vectors carried no semantic relationships — every word equidistant from every other | Distributional hypothesis: predict a word from its context and semantically similar words acquire nearby vectors. Famous for `king − man + woman ≈ queen` | Historical origin of "meaning as direction". Background citation only |
| ○ Pennington, Socher & Manning, "GloVe: Global Vectors for Word Representation," *EMNLP*, 2014 | Word2Vec used only local context windows | Factorise a global co-occurrence matrix | Alternative formulation; cite alongside word2vec or omit |
| ▪ Vaswani et al., "Attention Is All You Need," *NeurIPS*, 2017 | Recurrent models processed sequences serially, losing long-range dependencies and preventing parallel training | Self-attention: every token attends to every other, weighted by learned relevance. Fully parallelisable | **The architecture beneath every model in this project** — the LLM, the text embedder, CLIP, and Whisper. Cite once, early |
| ▪ Devlin, Chang, Lee & Toutanova, "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding," *NAACL*, 2019 | Word vectors were context-independent — "bank" had one vector for river and money | Bidirectional masked-language-model pretraining yields *contextual* token representations | The encoder family our embedding model descends from |
| 🔍 Reimers & Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," *EMNLP-IJCNLP*, 2019 | BERT's raw outputs are poor for sentence similarity; comparing all pairs with cross-encoding was computationally infeasible | Siamese/triplet fine-tuning plus mean pooling produces sentence vectors directly comparable by cosine similarity | **Direct justification for `all-MiniLM-L6-v2`** and for why cosine similarity is the right operation |

**Synthesis hook.** These form a clean chronological arc: context-free word vectors → contextual token vectors → comparable sentence vectors. That arc is a ready-made opening paragraph, and it lets you use the *development* move from Ch 3 §1.11.1.

### 🔍 Deep dive — Sentence-BERT

**The problem, precisely.** BERT can judge whether two sentences are similar, but only by processing them *together* (cross-encoding). To find the most similar sentence among 10,000, you must run BERT 10,000 times per query. Reimers & Gurevych report that finding the most similar pair in a collection of 10,000 sentences takes roughly 65 hours with BERT cross-encoding. That is not a search system.

**The key idea.** Encode each sentence *independently* into a fixed vector (a *bi-encoder*), so vectors can be precomputed and compared by cosine similarity in microseconds. The problem is that BERT's out-of-the-box outputs are not suited to this — averaging BERT token vectors performs *worse* than averaging GloVe vectors. The contribution is the fine-tuning recipe that fixes it: siamese training on natural-language-inference pairs, with mean pooling over token outputs.

**Why this matters to your architecture.** It is the reason a two-stage design exists in retrieval generally: cheap bi-encoder for the whole corpus, optional expensive cross-encoder for reranking the top few. You are implementing stage one; stage two is your named future work.

**Limitations to acknowledge.** A single fixed vector must compress a whole passage, so a chunk covering two topics produces an averaged vector matching neither — the "semantic smearing" problem that makes chunking a first-class design concern. Bi-encoders are also weaker than cross-encoders on fine-grained relevance, which is exactly why reranking exists.

**Exam questions it attracts.** *Why cosine similarity?* — because the training objective optimised for it. *Why not compare with BERT directly?* — quadratic cost; give the 65-hour figure. *What is mean pooling?* — averaging token vectors into one sentence vector.

---

## Theme 2 — Retrieval: from keywords to vectors

**The argument:** dense retrieval outperforms lexical retrieval on paraphrase, lexical retains an advantage on rare exact strings, and approximate nearest-neighbour search is what makes dense retrieval fast enough to use.

| Source | Problem solved | Key idea | What RAGNova takes |
|---|---|---|---|
| ○ Robertson & Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond," *Foundations and Trends in IR*, vol. 3, no. 4, 2009 | Formalising lexical relevance ranking | Term frequency × inverse document frequency with document-length normalisation | **The baseline we argue against** — and still superior for rare exact strings like invoice numbers |
| 🔍 Karpukhin et al., "Dense Passage Retrieval for Open-Domain Question Answering," *EMNLP*, 2020 | Lexical retrieval fails on paraphrase in QA | Dual-encoder trained on question–passage pairs with in-batch negatives; substantially outperforms BM25 on top-20 retrieval accuracy | **The empirical citation behind Objective O2** — evidence that dense beats keywords |
| ▪ Khattab & Zaharia, "ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT," *SIGIR*, 2020 | Bi-encoders lose token-level detail; cross-encoders are too slow | *Late interaction*: keep per-token vectors, compute MaxSim at query time. Accuracy near cross-encoders at far lower cost | The **third family** in your retrieval taxonomy. Rejected: storage cost is many vectors per passage |
| ▪ Nogueira & Cho, "Passage Re-ranking with BERT," *arXiv*, 2019 | Bi-encoder rankings are imperfect | Cross-encoder reranks the top-k from a cheap first stage | The classic **two-stage** pattern; our named future work |
| 🔍 Malkov & Yashunin, "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs," *IEEE TPAMI*, vol. 42, no. 4, pp. 824–836, 2020 | Exact nearest-neighbour search scales linearly and becomes infeasible | Multi-layer proximity graph; greedy descent through long-range then short-range links; roughly O(log N) | **The algorithm inside ChromaDB.** Cite for scalability |
| ▪ Johnson, Douze & Jégou, "Billion-Scale Similarity Search with GPUs," *IEEE Trans. Big Data*, vol. 7, no. 3, 2021 | Similarity search at industrial scale | IVF + product quantization, GPU-accelerated (FAISS) | **The alternative we rejected** — cite in ADR-004 |
| ▪ Aumüller, Bernhardsson & Faithfull, "ANN-Benchmarks: A Benchmarking Tool for Approximate Nearest Neighbor Algorithms," *Information Systems*, vol. 87, 2020 | ANN methods compared inconsistently | Standardised recall-vs-throughput benchmarking | Evidence for the **recall/speed trade-off** you claim |
| ○ Pan, Wang & Li, "Survey of Vector Database Management Systems," *The VLDB Journal*, vol. 33, 2024 | Vector DBs proliferated without a map | Taxonomy of architectures and query processing | One citation covering the vector-database landscape |
| ▪ Cormack, Clarke & Buettcher, "Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods," *SIGIR*, 2009 | Combining several ranked lists | Fuse by reciprocal rank: `score = Σ 1/(k + rank_i)`, typically k = 60 | ⭐ **Directly applicable to ADR-007** — the principled way to merge your two collections |
| ▪ Thakur, Reimers, Rücklé, Srivastava & Gurevych, "BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models," *NeurIPS Datasets & Benchmarks*, 2021 | Retrieval models evaluated on single datasets and overfitted them | Zero-shot benchmark across 18 datasets; found BM25 a surprisingly strong baseline | **Where your metric definitions come from** — and evidence that keyword search is not obsolete |
| ○ Nguyen et al., "MS MARCO: A Human Generated MAchine Reading Comprehension Dataset," *NIPS Workshop*, 2016 | No large real-query retrieval dataset | ~1M real Bing queries with human answers | The dataset most retrieval models are trained on — context for why they work |
| ○ Kwiatkowski et al., "Natural Questions: A Benchmark for Question Answering Research," *TACL*, vol. 7, 2019 | QA benchmarks used artificial questions | Real Google queries with Wikipedia answers | Context for open-domain QA evaluation |

### 🔍 Deep dive — Dense Passage Retrieval

**The problem.** Open-domain QA retrieves candidate passages then reads them. Retrieval was BM25 — lexical, and blind to paraphrase. A question phrased differently from its answer passage simply fails.

**The key idea.** Two BERT encoders — one for questions, one for passages — trained so that a question's vector lands near its answer passage's vector. The training trick that matters is **in-batch negatives**: within a batch, every *other* passage serves as a negative example, giving many negatives per positive at almost no cost. (Note the structural similarity to CLIP's objective in Theme 4 — a genuinely good *contrast* move for your prose.)

**Results.** DPR outperformed BM25 substantially on top-20 retrieval accuracy across several open-domain QA datasets, and the improvement propagated to end-to-end answer accuracy. **Verify the exact figures before quoting any.**

**Limitations to acknowledge.** DPR is *trained* on question–passage pairs; we use a general-purpose embedding model with no task-specific training, so we should not claim DPR's numbers as ours. And BEIR later showed BM25 remains competitive or better in several zero-shot domains — which is precisely why hybrid search exists and why you should not present dense retrieval as strictly superior.

**Exam questions.** *Why is dense better than keyword search?* — paraphrase and synonymy; cite DPR. *Is it always better?* — **no**; cite BEIR. That second answer, given unprompted, is worth a lot.

### 🔍 Deep dive — HNSW

**The problem.** Comparing a query against N stored vectors costs O(N·d). At 10⁶ vectors this becomes seconds per query.

**The key idea.** Build a layered graph. Every vector is a node. The bottom layer contains all nodes densely connected to near neighbours; each higher layer holds a random sample with long-range links. Search enters at the top, greedily hops toward the query, then descends. Long-range links cross the space quickly — "international flights" — and dense lower layers refine locally.

**Parameters you should be able to name.** `M` — links per node; higher means better recall and more memory. `ef_construction` — candidate list size during build; higher means a better graph and slower indexing. `ef_search` — candidate list size at query time; **the runtime recall/latency dial.**

**The honest caveat for your report.** HNSW is *approximate*: it can miss a true nearest neighbour, typically achieving 95–99% recall at large speedups. State this as a limitation. And state that **at your scale (~10³–10⁴ vectors) exact search would also be fast** — you adopt HNSW for architectural correctness and scalability, not because you measured a need. Claiming a performance benefit you did not observe is the kind of overclaim an examiner enjoys puncturing.

**Exam questions.** *Why is it approximate?* — greedy graph traversal may reach a local optimum. *What would you tune if recall were low?* — `ef_search`, then `M`.

---

## Theme 3 — Choosing an embedding model, with evidence

> ⭐ **Most student projects have nothing here.** They pick a model because a tutorial used it. This theme turns "why that model?" from a dangerous question into a prepared answer.

| Source | Problem solved | Key idea | What RAGNova takes |
|---|---|---|---|
| 🔍 Muennighoff, Tazi, Magne & Reimers, "MTEB: Massive Text Embedding Benchmark," *EACL*, 2023 | Embedding models compared on one or two tasks, so "best" was meaningless | Benchmark across 8 task types and 58 datasets, with a public leaderboard | ⭐ **The evidence base for your model choice.** Cite it and quote the trade-off |
| ▪ Wang et al., "Text Embeddings by Weakly-Supervised Contrastive Pre-training," *arXiv*, 2022 (E5) | Embedding models needed labelled pairs | Weakly supervised contrastive pretraining on large text-pair corpora | A stronger alternative — name it as considered |
| ▪ Xiao, Liu, Zhang & Muennighoff, "C-Pack: Packaged Resources To Advance General Chinese Embedding," *SIGIR*, 2024 (BGE) | Open embedding models lagged proprietary ones | Curated training data and recipe; BGE models topped MTEB on release | The main alternative considered and rejected on size |
| ▪ Li et al., "Towards General Text Embeddings with Multi-stage Contrastive Learning," *arXiv*, 2023 (GTE) | — | Multi-stage contrastive training | Alternative considered |
| ○ Wang et al., "Multilingual E5 Text Embeddings," *arXiv*, 2024 | English-centric embeddings | Multilingual variants | Relevant only if you extend beyond English; cite in future work |

### 🔍 Deep dive — MTEB, and how to actually use it

**The problem.** Before MTEB, papers evaluated embeddings on whichever benchmark flattered them. There was no way to answer "which embedding model should I use?"

**The key idea.** Evaluate every model on the same broad suite — retrieval, semantic similarity, clustering, classification, reranking, summarisation, pair classification, bitext mining — and publish a leaderboard.

**How to use it for your justification.** Do not look only at the top of the leaderboard. Look at the **retrieval** column, then at **model size and embedding dimension**, and reason under your constraint:

| Model | Params | Dims | Approx. size | Notes for us |
|---|---|---|---|---|
| `all-MiniLM-L6-v2` | ~22M | 384 | ~90 MB | ✅ Chosen — small, fast on CPU, strong retrieval for its size |
| `bge-small-en-v1.5` | ~33M | 384 | ~130 MB | Comparable; a reasonable alternative |
| `bge-base-en-v1.5` | ~109M | 768 | ~440 MB | Better scores; 2× dimensions doubles index memory |
| `bge-large-en-v1.5` | ~335M | 1024 | ~1.3 GB | Best scores; **competes with the LLM for RAM** |
| `e5-large-v2` | ~335M | 1024 | ~1.3 GB | Similar trade-off |

**The justification you can now give, in one sentence:** *"MTEB shows larger embedding models achieve higher retrieval scores, but `all-MiniLM-L6-v2` provides most of that quality at roughly one-fifteenth the parameters and half the embedding dimension; under an 8 GB RAM budget shared with a quantized 3B language model, that trade is decisive. The architecture is model-agnostic, so a larger encoder can be substituted if hardware permits."*

That answer does four things at once: cites evidence, names alternatives, states the constraint that decides it, and shows the decision is reversible. **This is what Job 2 from Ch 3 §1.1 looks like in practice.**

**Two caveats to state.** Leaderboards are gameable — some models are trained on data resembling the benchmark. And MTEB is predominantly English, so it says little about the multilingual behaviour you have scoped out anyway.

---

## Theme 4 — Cross-modal: one space for images and text

**The argument:** joint contrastive training produces a shared space that makes cross-modal retrieval an ordinary nearest-neighbour operation — but that space has a documented structural flaw you must design around.

| Source | Problem solved | Key idea | What RAGNova takes |
|---|---|---|---|
| 🔍 Radford et al., "Learning Transferable Visual Models From Natural Language Supervision," *ICML*, 2021 (CLIP) | Vision models needed fixed label sets and manual annotation; image and text vectors were incomparable | Contrastive training on ~400M image–caption pairs; N×N in-batch similarity matrix with the diagonal maximised, producing a **shared** space | **The entire basis of Objective O3.** The most important paper in your review |
| ▪ Cherti et al., "Reproducible Scaling Laws for Contrastive Language-Image Learning," *CVPR*, 2023 (OpenCLIP) | CLIP's training data was not released, so results could not be reproduced | Open reproduction on LAION; released checkpoints and scaling analysis | **The implementation you actually use.** Cite alongside CLIP — and the reason you cite both is itself a good sentence |
| 🔍 Liang, Zhang, Kwon, Yeung & Zou, "Mind the Gap: Understanding the Modality Gap in Multi-modal Contrastive Representation Learning," *NeurIPS*, 2022 | Unexplained: image and text embeddings occupy *separate* regions despite joint training | The gap originates in initialisation and is preserved by the contrastive objective; it is systematic, not noise | ⭐ **Direct justification for ADR-007's rank-based merge.** Converts an implementation hack into a literature-grounded decision |
| ▪ Li, Li, Xiong & Hoi, "BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation," *ICML*, 2022 | CLIP retrieves but cannot caption or answer questions about images | Combines contrastive and generative objectives; caption bootstrapping | **Alternative rejected** — heavier, and we need symmetric retrieval, not captioning |
| ▪ Zhai, Mustafa, Kolesnikov & Beyer, "Sigmoid Loss for Language Image Pre-Training," *ICCV*, 2023 (SigLIP) | CLIP's softmax loss requires very large batches | Pairwise sigmoid loss; better at small batch sizes | **Future-work upgrade path** — shows currency without committing you |
| ○ Jia et al., "Scaling Up Visual and Vision-Language Representation Learning With Noisy Text Supervision," *ICML*, 2021 (ALIGN) | — | Same idea at larger, noisier scale | Corroborates CLIP; optional |

### 🔍 Deep dive — CLIP

**The problem.** A conventional image classifier predicts from a fixed label set; adding a class requires retraining. Separately, an image encoder and a text encoder trained independently produce vectors in unrelated coordinate systems — comparing them is arithmetically possible and semantically meaningless.

**The mechanism, in detail.** Two encoders: a Vision Transformer (image split into patches, patches treated as tokens) and a text transformer. Both project into a shared space. Training takes a batch of N image–caption pairs, encodes all 2N items, and computes the full **N × N** similarity matrix:

```
              caption₁  caption₂  caption₃  ...
   image₁   [   ✅        ✗        ✗      ]     ✅ = true pair (diagonal)
   image₂   [   ✗        ✅        ✗      ]     ✗ = in-batch negative
   image₃   [   ✗        ✗        ✅      ]
```

A symmetric cross-entropy loss pushes the diagonal up and everything off-diagonal down, **in both directions** (image→text and text→image). A learnable **temperature** scales similarities before the softmax, controlling discrimination sharpness. Every other item in the batch is a negative, which is why very large batches (tens of thousands) matter so much.

**Scale.** ~400M image–caption pairs collected from the web. No manual labelling — the caption *is* the supervision. This is why coverage is open-vocabulary rather than restricted to a label set.

**What you exploit.** After training, the vector for a photo of a dog sits near the vector for "a photo of a dog". So text→image search, image→image search, and zero-shot classification all reduce to nearest-neighbour lookup in one space.

**Three limitations you must be able to state:**

1. **77-token text limit.** CLIP's text encoder was trained on captions and truncates at 77 tokens (~50 words). **It cannot embed document-length passages** — this single fact forces ADR-003's two-collection design.
2. **The modality gap.** Image and text vectors occupy separate cones; text-image similarities cluster lower than text-text even for perfect matches. Forces ADR-007.
3. **Prompt sensitivity and bias.** CLIP performs better with prompts like "a photo of a {}" than with bare labels, and the paper itself documents social biases inherited from web data. Worth one sentence in limitations.

**Exam questions.** *How does CLIP make text-to-image search possible?* — joint contrastive training into one space; draw the N×N matrix. *Why can't you use CLIP for your documents too?* — 77-token limit. *What is the temperature parameter?* — learned scaling of similarities before the softmax; distinct from LLM sampling temperature, and confusing the two is a visible error.

### 🔍 Deep dive — The modality gap

**Why this paper is your secret weapon.** Almost no student project cites it. It transforms a line of code — "merge by rank, not score" — into a decision grounded in published evidence.

**The observation.** In CLIP-like models, image embeddings and text embeddings do not intermingle. They occupy *distinct, narrow cones* in the shared space, separated by a consistent offset. Text-text similarities routinely sit around 0.5–0.8 while text-image similarities for correct pairs sit around 0.2–0.3.

**The explanation.** The gap is present at initialisation — random deep networks map different input types to different regions — and the contrastive objective preserves rather than closes it. Crucially, the paper shows the gap is **systematic and structural**, not noise or a training defect.

**The concrete bug it causes in your system.** Retrieve from `text_index` and `image_index`, concatenate the results, sort by raw similarity score. Every text result outscores every image result. Images never appear. **Objective O3 silently fails while every component works correctly** — the worst class of bug, because nothing errors.

**Your mitigations, in order of sophistication:**
1. **Rank-based interleaving** — take the top result from each, alternate. Simple, robust.
2. **Reciprocal Rank Fusion** — `score = Σ 1/(k + rank_i)`, k ≈ 60. Principled, one line, citable to Cormack et al.
3. **Per-modality score normalisation** — z-score within each modality before merging. Requires enough samples to estimate the distribution.

Implement (1) or (2), and **ablate against naive score merging** (Ch 3 §3.6.7). That ablation is the most valuable experiment in your project.

**Exam questions.** *Why can't you compare a text-text score with a text-image score?* — different distributions; cite the paper. *How do you handle it?* — rank fusion, plus the ablation showing it matters in your data.

---

## Theme 5 — Speech: making audio searchable

**The argument:** two routes existed (transcribe-then-index, or embed audio natively); the content type decides, and transcription additionally delivers the timestamps citation requires.

| Source | Problem solved | Key idea | What RAGNova takes |
|---|---|---|---|
| 🔍 Radford, Kim, Xu, Brockman, McLeavey & Sutskever, "Robust Speech Recognition via Large-Scale Weak Supervision," *ICML*, 2023 (Whisper) | ASR was brittle across accents, noise and domains, and needed per-domain fine-tuning | Encoder–decoder transformer trained on ~680k hours of weakly supervised multilingual audio; strong zero-shot robustness | **Objective O1's audio pipeline** and the spoken-query feature. Cite for segment-level timestamps |
| ▪ Bain, Huh, Han & Zisserman, "WhisperX: Time-Accurate Speech Transcription of Long-Form Audio," *Interspeech*, 2023 | Whisper's timestamps are segment-level and can drift | Forced alignment for word-level timestamps; VAD-based batching | **Future work** for precise citation seeking — and evidence you know Whisper's timestamp limitation |
| ▪ Gandhi, von Platen & Rush, "Distil-Whisper: Robust Knowledge Distillation via Large-Scale Pseudo Labelling," *arXiv*, 2023 | Whisper is slow on CPU | Distilled variants, substantially faster with modest WER cost | Fallback if transcription is too slow on team hardware |
| ▪ Elizalde, Deshmukh, Al Ismail & Wang, "CLAP: Learning Audio Concepts from Natural Language Supervision," *ICASSP*, 2023 | Audio had no CLIP-equivalent shared space | Contrastive audio–text pretraining | ⭐ **The alternative rejected in ADR-005** — strong on environmental sound, weaker on speech semantics |
| ○ Baevski, Zhou, Mohamed & Auli, "wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations," *NeurIPS*, 2020 | ASR needed large labelled corpora | Self-supervised pretraining on raw audio | Context for how modern ASR became feasible |
| ○ Gulati et al., "Conformer: Convolution-augmented Transformer for Speech Recognition," *Interspeech*, 2020 | Transformers alone miss local acoustic patterns | Combine convolution with self-attention | Architectural context; optional |

### 🔍 Deep dive — Whisper, and the decision it enables

**The problem.** Previous ASR systems were trained on relatively small curated corpora and were brittle: change the accent, the microphone, or the domain and word error rate degraded sharply. Deployment meant fine-tuning per domain.

**The mechanism.** Audio is converted to a **log-Mel spectrogram** — a two-dimensional representation of frequency energy over time, effectively an image of the sound — in 30-second windows. An encoder reads it; a decoder generates text tokens autoregressively, conditioned on the audio. It is the same next-token prediction as a language model, conditioned differently. Special tokens control language identification, transcription-versus-translation, and timestamp prediction.

**The scale argument.** ~680,000 hours of weakly supervised multilingual audio. The paper's central claim is that scale and diversity of *weak* supervision beat cleanliness of *strong* supervision for robustness. Zero-shot Whisper approaches or beats systems fine-tuned on specific benchmarks.

**Model sizes.** `tiny` → `base` → `small` → `medium` → `large-v3`, trading accuracy for speed. **Report which you used and why** — for a demo corpus on CPU, `base` is usually the right trade, and saying so with the reason is better than omitting it.

**Why this decides ADR-005.** Compare with CLAP:

| | Whisper (transcribe → index text) | CLAP (embed audio directly) |
|---|---|---|
| Strong on | Speech — linguistic content | Environmental sound, music, acoustic events |
| Output | Text + **timestamps** | An opaque vector |
| Citation | "lecture3.mp3 @ 14:32", with readable transcript | Vector similarity only — nothing a human can verify |
| Reuses | The existing text pipeline entirely | Requires a third index and a third model at query time |
| Spoken queries | ✅ Same model, reversed direction | ✗ |

Our corpus is **speech**, where information is linguistic. Transcription matches the content type, delivers the timestamps citation requires, produces human-verifiable evidence, and reuses infrastructure. CLAP would be the right choice for a corpus of sound effects — which is exactly how you should phrase it, because it shows the rejection is contextual rather than dismissive.

**Limitations to state.** Segment-level timestamps can drift (hence WhisperX). Whisper is known to occasionally hallucinate text during silence or noise — **relevant to you, since a hallucinated transcript becomes a retrievable false chunk.** Mention this as a real risk and note that displaying the transcript beside the citation lets a user catch it.

**Exam questions.** *Why not embed audio directly?* — the table above. *What is a log-Mel spectrogram?* — frequency energy over time, read like an image. *What if transcription is wrong?* — retrieval degrades; the transcript is displayed so errors are visible; WER is measured and reported.

---

## Theme 6 — Document understanding: three competing philosophies

> ⭐ **This theme prepares you for the sharpest question available about your architecture.** There are three ways to make a document searchable, you chose the oldest, and you need to know why.

| Source | Problem solved | Key idea | What RAGNova takes |
|---|---|---|---|
| ○ Smith, "An Overview of the Tesseract OCR Engine," *ICDAR*, 2007 | Extracting printed text from images | Classical OCR pipeline | Justifies the **OCR path** complementing CLIP |
| ▪ Xu, Li, Cui, Huang, Wei & Zhou, "LayoutLM: Pre-training of Text and Layout for Document Image Understanding," *KDD*, 2020 | Text extraction discards layout, which carries meaning in forms and tables | Jointly model text, 2-D position, and image features | Evidence that **layout matters** — and a limitation of our plain-text extraction |
| ▪ Kim et al., "OCR-free Document Understanding Transformer," *ECCV*, 2022 (Donut) | OCR errors propagate into every downstream stage | Skip OCR: read the document image end-to-end | The idea that OCR is a lossy intermediate step |
| 🔍 Faysse et al., "ColPali: Efficient Document Retrieval with Vision Language Models," *ICLR*, 2025 | Text-extraction pipelines lose figures, tables and layout, and are fragile | Embed **page screenshots** directly with a vision-language model; late-interaction retrieval over patch embeddings | ⭐ **The alternative you must be able to discuss.** Radically simpler ingestion, higher compute per page |
| ▪ Ma, Lin, Chen & Lin, "Unifying Multimodal Retrieval via Document Screenshot Embedding," *EMNLP*, 2024 (DSE) | Same insight, different formulation | Encode a document screenshot as a single dense vector | Corroborates the screenshot paradigm |
| ○ PyMuPDF and python-docx documentation | — | — | Cite with access dates for implementation specifics |

### 🔍 Deep dive — ColPali, and why you didn't use it

**Read this section before your viva.** It is the question most likely to catch you out, because ColPali is genuinely elegant and it makes your pipeline look old-fashioned.

**The problem it identifies.** The standard pipeline — parse PDF → extract text → chunk → embed — discards a great deal. Tables lose structure. Figures vanish entirely. Multi-column layouts interleave incorrectly. Scanned pages produce nothing without OCR, and OCR introduces its own errors. Every one of these failures is invisible: the pipeline reports success while silently losing content.

**The key idea.** Do not extract anything. **Render each page as an image and embed the image** with a vision-language model, keeping per-patch embeddings and retrieving by late interaction (ColBERT-style MaxSim). A query then matches against what the page *looks like*, including its figures and tables.

**Why it is compelling.** Ingestion becomes trivial — no parser per format, no OCR, no layout heuristics. Figures and tables become retrievable. Scanned and born-digital documents are handled identically.

**Why RAGNova does not use it — the honest answer, with four parts:**

1. **Compute.** A VLM forward pass per page is far heavier than text extraction, and every page produces many patch vectors rather than one. Under a CPU-only, 8 GB budget already shared with an LLM, an embedding model and Whisper, this is the binding constraint.
2. **It solves documents, not audio.** Speech still requires transcription, so we need the text pipeline regardless. ColPali would be an *addition*, not a replacement.
3. **Citation granularity differs.** ColPali cites a page. Our chunks cite a passage *within* a page, and audio to a timestamp. Finer provenance is one of our stated objectives.
4. **Exact-string retrieval.** Our OCR path indexes literal text, so an invoice number is retrievable as a string. A purely visual embedding is weaker at rare exact tokens.

**How to say it in the viva** — this phrasing is defensible and shows judgement rather than ignorance:

> "ColPali is a genuinely better approach for figure- and table-heavy document corpora, and we would adopt it given more compute. We chose parse-then-embed because our constraint is CPU-only execution alongside three other models, because we need a text pipeline for speech regardless, and because passage-level and timestamp-level provenance is one of our objectives, whereas screenshot retrieval is page-level. We list it as our primary future-work direction."

**Exam questions.** *Why not just embed the pages as images?* — the four reasons. *What do you lose by extracting text?* — figures, tables, layout; cite LayoutLM and ColPali. *How would you know if you were losing content?* — a real weakness; the honest answer is that you would compare extracted text length against page content, which is a good thing to propose as a check.

---

## Theme 7 — Grounding: RAG and its descendants

**The argument:** parametric memory is lossy, un-citable and frozen; retrieval fixes all three; the field has since developed a maturity taxonomy that lets you position your own system honestly.

| Source | Problem solved | Key idea | What RAGNova takes |
|---|---|---|---|
| ○ Petroni et al., "Language Models as Knowledge Bases?," *EMNLP*, 2019 | Could LMs replace knowledge bases? | LMs store surprising factual knowledge — but unreliably | Establishes *parametric* knowledge as a concept |
| ○ Roberts, Raffel & Shazeer, "How Much Knowledge Can You Pack Into the Parameters of a Language Model?," *EMNLP*, 2020 | How far can closed-book QA go? | Scales with size, but remains limited and un-citable | Evidence that parametric memory has hard limits |
| ▪ Guu, Lee, Tung, Pasupat & Chang, "REALM: Retrieval-Augmented Language Model Pre-Training," *ICML*, 2020 | Knowledge locked in parameters, un-updatable and un-inspectable | Retrieval integrated into pretraining, jointly learned | Historical predecessor — the idea before RAG named it |
| 🔍 Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," *NeurIPS*, 2020 | LLMs hallucinate, cannot cite, cannot access private or new data | Combine a dense retriever with a seq2seq generator; condition generation on retrieved passages | **The paper your project is named after.** Justifies the architecture and Objective O4 |
| ▪ Izacard & Grave, "Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering," *EACL*, 2021 (FiD) | Combining evidence across many passages | Encode passages independently, fuse in the decoder | Explains **why top-K matters** and how multiple chunks combine |
| ▪ Ji et al., "Survey of Hallucination in Natural Language Generation," *ACM Computing Surveys*, vol. 55, no. 12, 2023 | Hallucination discussed anecdotally | Taxonomy of causes and mitigations | **The citation behind Ch 1 §1.2** — that hallucination is structural |
| ▪ Huang et al., "A Survey on Hallucination in Large Language Models," *ACM TOIS*, 2025 | LLM-specific hallucination taxonomy | Causes across data, training, inference | More recent companion to the above |
| 🔍 Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni & Liang, "Lost in the Middle: How Language Models Use Long Contexts," *TACL*, vol. 12, 2024 | Assumption that longer context is strictly better | Accuracy is highest when relevant information is at the beginning or end; **degrades in the middle** | ⭐ **Justifies retrieving few good chunks rather than stuffing everything** — and informs chunk *ordering* |
| ▪ Asai, Wu, Wang, Sil & Hajishirzi, "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection," *ICLR*, 2024 | Naive RAG retrieves indiscriminately and cannot assess its own output | Reflection tokens decide when to retrieve and whether output is supported | **Future work** — shows you know naive RAG's limits |
| ▪ Yan, Sun, Wang, Chen, Wang, Wu & Wang, "Corrective Retrieval Augmented Generation," *arXiv*, 2024 | Retrieval sometimes returns irrelevant passages | Lightweight evaluator grades retrieval and triggers correction | **Future work** — a concrete improvement path |
| ▪ Gao, Xiong, Gao, Jia, Pan, Bi, Dai, Sun, Wang & Wang, "Retrieval-Augmented Generation for Large Language Models: A Survey," *arXiv*, 2023–2024 | The field fragmented rapidly | Taxonomy: **Naive → Advanced → Modular RAG** | ⭐ **Position your own system using this taxonomy** |
| ▪ Gao, Ma, Lin & Callan, "Precise Zero-Shot Dense Retrieval without Relevance Labels," *ACL*, 2023 (HyDE) | Short queries embed poorly against long passages | Generate a hypothetical answer, embed *that*, retrieve with it | Cheap **future-work** improvement — one extra LLM call |
| ▪ Edge et al., "From Local to Global: A Graph RAG Approach to Query-Focused Summarization," *arXiv*, 2024 | RAG answers local questions but not corpus-wide ones | Build a knowledge graph and community summaries | Future work; explains a limitation you should admit |

### 🔍 Deep dive — RAG (Lewis et al.)

**The problem, stated three ways.** An LLM's knowledge is (1) *lossy* — trillions of training tokens compressed into billions of parameters; (2) *un-citable* — knowledge dissolved into weights cannot be traced to a source; (3) *frozen* — updating requires retraining. Your files are additionally *absent* — never in the training data at all.

**The key idea.** Retrieve relevant passages from a non-parametric memory (a dense index) and condition generation on them. The paper frames this as combining **parametric memory** (the model's weights) with **non-parametric memory** (the retrievable corpus).

**Two variants worth knowing**, because an examiner may ask: **RAG-Sequence** conditions the whole output on one retrieved document; **RAG-Token** may draw different tokens from different documents. Modern practical systems — including yours — mostly do something simpler: concatenate top-K passages into the prompt of an instruction-tuned model. **Say this.** Claiming to implement Lewis et al.'s architecture when you are doing prompt-based retrieval augmentation is a small inaccuracy that a knowledgeable examiner will notice.

**The property you depend on.** Because the evidence is *supplied* rather than recalled, it remains available for attribution. **Citation is a structural consequence of the architecture, not a feature added afterwards.** That sentence is worth memorising — it is the cleanest justification for your entire design.

**Limitations to acknowledge.** Answer quality is bounded by retrieval quality — a bad retrieval yields a confidently wrong answer. The model may still misattribute a claim to the wrong retrieved passage, which is why you validate citation markers. And RAG does not fix reasoning failures, only knowledge failures.

**Exam questions.** *What does RAG stand for and what does each part do?* *Why does RAG enable citations when fine-tuning does not?* *Do you implement Lewis's exact architecture?* — no, and say what you do instead.

### 🔍 Deep dive — Lost in the Middle

**The finding.** Give a model a long context containing one relevant passage, and vary that passage's position. Accuracy is highest when it appears near the **beginning or end**, and lowest in the **middle** — a U-shaped curve. This holds even for models explicitly designed for long contexts.

**Three consequences for your design:**

1. **Retrieve few, good chunks.** More context is not strictly better. This is the empirical answer to "why not just paste everything in?"
2. **Order matters.** Placing the highest-ranked chunk first — or first and last — is a defensible, citable design choice rather than an arbitrary one.
3. **It gives your top-K ablation a hypothesis.** You are not merely trying values; you predict that K = 10 may underperform K = 5 despite containing strictly more information. **Having a prediction before running an experiment is what makes it an experiment.**

**Exam question.** *Why is your top-K only 5?* — cite this paper, then show your ablation.

---

## Theme 8 — Why not fine-tuning: the empirical case

> ⭐ **Most projects justify "RAG not fine-tuning" by assertion.** You can justify it with three empirical papers, one of which found fine-tuning on new knowledge *increases* hallucination. This is the single cheapest upgrade to ADR-001's credibility.

| Source | Problem solved | Key idea | What RAGNova takes |
|---|---|---|---|
| 🔍 Ovadia, Brief, Mishaeli & Elisha, "Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs," *arXiv*, 2023 | Practitioners assumed fine-tuning teaches facts | Head-to-head comparison; **RAG consistently outperformed fine-tuning for knowledge injection** | ⭐ **Direct empirical support for ADR-001** |
| 🔍 Gekhman, Yona, Aharoni, Eyal, Feder, Reichart & Herzig, "Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?," *EMNLP*, 2024 | Does teaching new facts have a cost? | Models learn new facts slowly, and doing so **increases their tendency to hallucinate** on other questions | ⭐ **The strongest single sentence you can say against fine-tuning** |
| ▪ Kandpal, Deng, Roberts, Wallace & Raffel, "Large Language Models Struggle to Learn Long-Tail Knowledge," *ICML*, 2023 | Why do models know some facts and not others? | Accuracy correlates strongly with how often a fact appeared in pretraining | Explains why *your* documents — seen zero times — cannot be recalled |
| ▪ Soudani, Kanoulas & Hasibi, "Fine Tuning vs. Retrieval Augmented Generation for Less Popular Knowledge," *arXiv*, 2024 | Which wins for rare entities? | RAG advantage is largest exactly where knowledge is rare | Your corpus is maximally rare — every file is unique |
| ▪ Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models," *ICLR*, 2022 | Full fine-tuning is prohibitively expensive | Train small low-rank adapters instead | The *cheapest* form of fine-tuning — and still not viable here |
| ▪ Dettmers, Pagnoni, Holtzman & Zettlemoyer, "QLoRA: Efficient Finetuning of Quantized LLMs," *NeurIPS*, 2023 | Even LoRA needs substantial GPU memory | Fine-tune through a 4-bit quantized model | Shows fine-tuning *is* becoming feasible — cite it to show you know, then give the other reasons |

### 🔍 Deep dive — the fine-tuning comparison

**Why this theme exists.** "Why didn't you just fine-tune?" is asked in almost every viva. The weak answer is "we didn't have GPUs." The strong answer has four independent legs, three of them citable:

| Leg | Claim | Evidence |
|---|---|---|
| **1. Citations** | Knowledge absorbed into weights cannot be traced to page 2 of a PDF | Structural — no citation needed, but it alone disqualifies fine-tuning given Objective O4 |
| **2. It works less well for facts** | RAG outperformed fine-tuning for knowledge injection in head-to-head comparison | Ovadia et al. |
| **3. It can make things worse** | Fine-tuning on new knowledge increases hallucination tendency | Gekhman et al. |
| **4. Practical cost** | Requires GPU hours, and must be repeated per file | LoRA/QLoRA reduce but do not remove this |

**Note the rhetorical structure.** Leg 1 is decisive on its own, so lead with it. Legs 2 and 3 pre-empt "but fine-tuning would teach it your data" — and leg 3 is genuinely counter-intuitive, which makes it memorable. Leg 4 is last because it is the weakest: QLoRA makes it cheaper every year, so an argument resting only on cost ages badly.

**The intellectually honest caveat**, which you should volunteer rather than wait to be asked: fine-tuning and RAG are **complementary**, not competing. Fine-tuning teaches *behaviour* — output format, domain style, citation discipline — while RAG supplies *facts*. A production system might do both. Saying this shows you understand the distinction rather than having memorised one side of it.

**Exam questions.** *Why not fine-tune?* — the four legs, leading with citations. *Would fine-tuning help at all?* — yes, for format and style; not for facts. *Is your answer just "we lack GPUs"?* — no, and here is Gekhman.

---

## Theme 9 — Attribution and verifiability: the literature behind Objective O4

> ⭐ **A keyword search for "citations" finds nothing. The field calls this attribution and verifiability.** This theme is where most student projects have a stated objective with zero theoretical grounding, and where yours can have an entire literature.

| Source | Problem solved | Key idea | What RAGNova takes |
|---|---|---|---|
| 🔍 Rashkin, Nikolaev, Lamm, Aroyo, Collins, Das, Petrov, Tomar, Turc & Reitter, "Measuring Attribution in Natural Language Generation Models," *Computational Linguistics*, vol. 49, no. 4, 2023 | "Cited" was not a defined property | **AIS — Attributable to Identified Sources**: a formal, annotatable definition of whether a statement is supported by a cited source | ⭐ **The definition behind your faithfulness metric.** Cite it to show "faithfulness" is not self-invented |
| 🔍 Liu, Zhang & Liang, "Evaluating Verifiability in Generative Search Engines," *EMNLP Findings*, 2023 | Do commercial cited-answer systems actually work? | Human evaluation of generative search engines found a **substantial fraction of citations did not support their claims** | ⭐ **Justifies citation validation and displaying chunk text.** Also excellent slide material |
| ▪ Bohnet et al., "Attributed Question Answering: Evaluation and Modeling for Attributed Large Language Models," *arXiv*, 2022 | Formalising the attributed-QA task | Task definition, metrics, and system comparison | Frames what your system does as a recognised task |
| ▪ Menick et al., "Teaching Language Models to Support Answers with Verified Quotes," *arXiv*, 2022 (GopherCite) | Models assert without evidence | Train the model to quote supporting evidence and abstain when it cannot | Precedent for **abstention** — your "not found in the provided sources" behaviour |
| ▪ Gao, Yen, Yu & Chen, "RARR: Researching and Revising What Language Models Say, Using Language Models," *ACL*, 2023 | Attribution added after the fact | Post-hoc research-and-revise to make outputs attributable | Alternative architecture — contrast with your retrieve-first design |
| ▪ Es, James, Espinosa-Anke & Schockaert, "RAGAS: Automated Evaluation of Retrieval Augmented Generation," *EACL (demo)*, 2024 | RAG evaluation was ad hoc | Metrics for faithfulness, answer relevance, context relevance | **Where your generation metrics come from** |
| ▪ Saad-Falcon, Khattab, Potts & Zaharia, "ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems," *NAACL*, 2024 | Human evaluation does not scale | Trained LLM judges with statistical confidence intervals | Alternative evaluation approach; cite as considered |
| ▪ Buçinca, Malaya & Gajos, "To Trust or to Think: Cognitive Forcing Functions Can Reduce Overreliance on AI," *CSCW*, 2021 | Users over-trust AI output | Interface designs that force engagement reduce blind acceptance | ⭐ **HCI justification for your citation UI** — why showing chunk text matters |
| ○ Nakano et al., "WebGPT: Browser-assisted Question-Answering with Human Feedback," *arXiv*, 2021 | Answers without sources | Model browses and cites while answering | Early precedent for cited generation |

### 🔍 Deep dive — attribution, and why it changes your framing

**The reframing this theme gives you.** Without it, Objective O4 reads as a UI feature: "we show citations." With it, O4 becomes participation in a defined research problem: **attribution** — whether a generated statement is genuinely supported by an identified source — with a formal definition (AIS), an evaluation literature, and a documented failure rate in deployed systems.

**Rashkin et al.'s contribution.** They define AIS: a statement is attributable to a source if a generic reader would agree that the source supports it. Crucially, they make this *annotatable* — a protocol humans can apply consistently. **This is what your faithfulness rating is measuring**, and saying so upgrades your evaluation from "we asked people if it looked right" to "we applied an established attribution criterion."

**Liu et al.'s finding, and why it is your best slide.** They evaluated commercial generative search engines and found that a substantial proportion of generated sentences were not fully supported by their cited sources — while the systems presented them with complete confidence. **Verify the exact figures before quoting them**, but the qualitative finding is robust and it does two things for you:

1. It justifies your design decisions — citation-marker validation, and displaying retrieved chunk text beside every citation — as responses to a *documented, measured* failure mode rather than as defensive over-engineering.
2. It gives you an honest, non-defensive answer to "does your system hallucinate?": *"Reduced, not eliminated. Deployed commercial systems have measurable attribution failure rates; we therefore validate citation markers and display the source text so a user can verify in one glance."*

**The HCI angle, which almost nobody includes.** Buçinca et al. show users over-rely on AI output when it is presented fluently, and that interface designs requiring engagement reduce this. That is a research-grounded justification for the *expandable citation* requirement in your problem statement: the citation is not decoration, it is a cognitive forcing function.

**Exam questions.** *How do you know your citations are correct?* — validation plus human rating against an attribution criterion; cite Rashkin. *Do commercial systems get this right?* — no, measurably; cite Liu. *Why show the source text rather than just a link?* — cite Buçinca. *Is your metric self-invented?* — no; RAGAS and AIS.

---

## Theme 10 — Chunking and context: where practice outruns research

> ⚠️ **This is a genuinely thin literature**, and saying so is a methodological strength (Ch 3 §3.3.2). Most chunking guidance lives in industry documentation, not peer-reviewed venues.

| Source | Problem solved | Key idea | What RAGNova takes |
|---|---|---|---|
| 🔍 Liu et al., "Lost in the Middle," *TACL*, 2024 | *(see Theme 7)* | Position within context affects accuracy | Chunk **ordering** and top-K choice |
| ▪ Sarthi, Abdullah, Tuli, Khanna, Goldie & Manning, "RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval," *ICLR*, 2024 | Flat chunks cannot answer questions needing whole-document context | Recursively cluster and summarise chunks into a tree; retrieve at multiple abstraction levels | **Future work** — and it names a limitation you should admit: your flat chunks answer local questions well and global ones poorly |
| ▪ Günther, Mohr, Williams, Wang & Xiao, "Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models," *arXiv*, 2024 | Chunking before embedding discards cross-chunk context | Embed the long document first, then pool per chunk — so each chunk's vector retains document context | Elegant **future work**; needs a long-context embedding model |
| ▪ Duarte, Thomas, Varma & Camacho-Collados, "LumberChunker: Long-Form Narrative Document Segmentation," *EMNLP Findings*, 2024 | Fixed-size chunking splits mid-idea | Use an LLM to choose semantic boundaries | Evidence that **semantic chunking is a real research direction**, not just a library feature |
| ○ LangChain / LlamaIndex documentation on text splitters | — | Recursive character splitting, token-aware splitting | Cite as *documentation*, with an access date — **never as research evidence** |

**How to write this theme — the honest paragraph:**

> Passage granularity has received comparatively little systematic study relative to its practical impact. Published work addresses hierarchical organisation [RAPTOR], context-preserving embedding [LateChunking] and LLM-guided boundary selection [LumberChunker], but general guidance on segment size remains largely empirical, with much practical knowledge residing in library documentation rather than peer-reviewed literature. Segment size is therefore treated here as a **tunable parameter determined by ablation** (§8.4) rather than adopted from prior work.

**Why this paragraph is worth its space.** It demonstrates you can distinguish where evidence exists from where it does not — a genuine research skill — and it converts an apparent weakness into the justification for running your own experiment. It also pre-empts "what's your evidence for 300 words?" with "our own ablation, because the literature does not settle it."

---

## Theme 11 — Local execution: why offline is now possible

**The argument:** quantization research made models small enough for consumer hardware, which is the technical precondition for the entire project. Without this theme, "offline" looks like a constraint you accepted; with it, "offline" looks like a capability you exploited.

| Source | Problem solved | Key idea | What RAGNova takes |
|---|---|---|---|
| ▪ Dettmers, Lewis, Belkada & Zettlemoyer, "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale," *NeurIPS*, 2022 | Large models exceeded consumer memory | 8-bit inference with outlier-aware decomposition, near-lossless | Establishes that quantization preserves quality |
| 🔍 Frantar, Ashkboos, Hoefler & Alistarh, "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers," *ICLR*, 2023 | 4-bit quantization degraded quality | One-shot post-training quantization using second-order information | **The evidence behind Ch 1 §1.1.5's memory table** — why a 3B model fits in ~2 GB |
| ▪ Lin, Tang, Tang, Yang, Dang, Gan & Han, "AWQ: Activation-aware Weight Quantization for On-Device LLM Compression and Acceleration," *MLSys*, 2024 | Some weights matter far more than others | Protect salient weights identified by activation statistics | Current practice; cite alongside GPTQ |
| ▪ Grattafiori et al. (Llama Team), "The Llama 3 Herd of Models," *arXiv*, 2024 | — | Model family, training, and capabilities | **Cite the model you actually run.** Specify the exact variant and quantization |
| ○ Jiang et al., "Mistral 7B," *arXiv*, 2023 | — | Efficient 7B model | Alternative considered |
| ○ Abdin et al., "Phi-3 Technical Report," *arXiv*, 2024 | Small models were assumed weak | Data-quality-driven small models with strong performance | Evidence that small models are viable — supports your architecture choice |
| ▪ Carlini et al., "Extracting Training Data from Large Language Models," *USENIX Security*, 2021 | Are models a privacy risk? | Training data can be extracted from model outputs | ⭐ **Motivates the offline requirement** with a security citation |
| ▪ Staab, Vero, Balunović & Vechev, "Beyond Memorization: Violating Privacy via Inference with LLMs," *ICLR*, 2024 | Privacy risk beyond memorisation | LLMs infer personal attributes from ordinary text | Strengthens the privacy argument for local execution |
| ○ `ggerganov/llama.cpp` — GitHub repository | — | CPU-efficient inference; GGUF format | Cite the software you depend on, with an access date |
| ○ Ollama, ChromaDB, sentence-transformers, faster-whisper documentation | — | — | Cite with access dates |

### 🔍 Deep dive — quantization, and the sentence it earns you

**The problem.** A model's weights at 16-bit precision need ~2 bytes each. A 3B model is therefore ~6 GB just for weights, before activations and KV cache. That does not fit comfortably in 8 GB alongside an operating system, a browser, and three other models.

**The key idea.** Store weights with fewer bits. Naive rounding to 4 bits destroys quality; GPTQ's contribution is quantizing *layer by layer* using second-order (curvature) information to choose values that minimise output error rather than weight error. AWQ takes a complementary route: identify the small fraction of weights that matter most — via activation statistics — and protect those.

**The numbers you should be able to state:**

| Precision | Bytes/param | 3B model | Quality |
|---|---|---|---|
| FP16 | 2 | ~6 GB | Reference |
| INT8 | 1 | ~3 GB | Near-lossless |
| **INT4 (Q4_K_M)** | ~0.55 | **~2 GB** | Small, measurable degradation |

**The sentence this theme earns you**, which reframes your whole project:

> "Offline operation is not a limitation we accepted; it is a capability recent quantization research made available. A 3-billion-parameter model at 4-bit precision occupies roughly two gigabytes with limited quality loss [GPTQ], [AWQ], which is what permits the entire pipeline to execute on commodity hardware — and retrieval further reduces the burden on the model, since reading a supplied passage is a far easier task than recalling a fact."

**And the privacy citation.** Carlini et al. showed training data can be extracted from model outputs; Staab et al. showed LLMs can infer personal attributes from ordinary text. Together they turn "offline is good for privacy" from an assertion into a cited claim.

**Exam questions.** *How does a 3B model fit in 2 GB?* — 4-bit quantization; give the table. *What do you lose?* — small measurable quality degradation; state it. *Why is a 3B model enough?* — retrieval converts recall into reading comprehension.

---

## Using this bibliography

### Coverage check

Before writing, confirm your review includes at least one source from **every** theme. Themes 3, 6, 8, 9 are the differentiators — they are where a typical project has nothing.

### The twelve deep-dive sources

If you read nothing else to Pass 2, read these:

| # | Source | Why |
|---|---|---|
| 1 | Sentence-BERT | Why your text embeddings work |
| 2 | DPR | Evidence dense beats lexical |
| 3 | HNSW | How the vector DB searches |
| 4 | MTEB | ⭐ Justifies your model choice |
| 5 | CLIP | The cross-modal capability |
| 6 | Modality gap | ⭐ Justifies rank-based merging |
| 7 | Whisper | The audio pipeline |
| 8 | ColPali | ⭐ The alternative you must address |
| 9 | RAG (Lewis) | The architecture |
| 10 | Lost in the Middle | Why top-K is small |
| 11 | Ovadia / Gekhman | ⭐ Evidence against fine-tuning |
| 12 | Rashkin / Liu (verifiability) | ⭐ The attribution literature |

**Split:** Member 1 takes 1, 2, 9, 11 · Member 2 takes 5, 6, 3, 8 · Member 3 takes 7, 10, 12, 4.

### Final reminder

**Verify every citation.** Author lists, venues, volumes, years. Prefer the published version over the preprint. Use the tracker in [`reports/literature-matrix.md`](../../reports/literature-matrix.md).

---

**Back to:** [Chapter 3 — Literature Review & Methodology](ch03-literature-review-and-methodology.md) · **Next:** [Chapter 3B — Reading a Paper & Citation Mechanics](ch03b-reading-and-citations.md)
