# Chapter 5A — Systems References

> **Companion to [Chapter 5](ch05-environment-setup-and-offline-llm.md).** Unlike Chapters 3A and 4A, this is not an academic literature review — Chapter 5's subject matter (packaging, model-serving, file formats) lives mostly in specifications, official documentation, and source repositories rather than peer-reviewed papers. Cite these the way [Chapter 3B §B.3](ch03b-reading-and-citations.md) cites tools: as documentation, with an access date, not as research findings.
>
> **⚠️ Verify every link and version claim before use** — software documentation moves faster than papers, and a specific claim ("wheels are tagged this way") should be checked against the current spec before it goes in a report.

---

## Cluster 1 — Python packaging (Part 1)

| Source | What it defines | Relevant to |
|---|---|---|
| PEP 427 — "The Wheel Binary Package Format 1.0" | The `.whl` format and its filename convention (`{name}-{version}-{python tag}-{abi tag}-{platform tag}.whl`) | §1.2's wheel filename walkthrough |
| PEP 440 — "Version Identification and Dependency Specification" | The version-string grammar pip's resolver parses (`==`, `>=`, pre-releases, etc.) | §1.3's pinning discussion |
| PEP 517 / PEP 518 — build-system specification | How pip decides whether/how to build a package from source when no wheel matches | §1.1 step 3, §1.4's build-failure table |
| pip documentation — "Dependency Resolution" | pip's own explanation of its backtracking resolver, in plain language | §1.1 |
| Python Packaging Authority, `packaging.python.org` | The general reference for everything above, kept current as PEPs evolve | Use as the first stop when a PEP feels too dense |

## Cluster 2 — Model formats and local serving (Part 2)

| Source | What it defines | Relevant to |
|---|---|---|
| `ggml-org/ggml` and `ggml-org/llama.cpp` GitHub repositories | The GGUF file format specification and the inference engine Ollama builds on | §2.1's format discussion |
| Ollama's own documentation (`github.com/ollama/ollama`, `/docs`) and API reference | The authoritative source for every endpoint in §2.2's table, and for current default parameter values | §2.2–2.3 |
| Grattafiori et al. (Llama Team), "The Llama 3 Herd of Models," arXiv, 2024 | Published architecture details for Llama 3-family models — the primary source to check before quoting exact `num_layers`/`num_kv_heads` figures rather than the approximate ones used in §2.5's worked example | §2.5 |
| Frantar, Ashkboos, Hoefler & Alistarh, "GPTQ," ICLR 2023; Lin et al., "AWQ," MLSys 2024 | Already cited in ADR-002; relevant again here for the specific claim that quantizing the KV cache itself (distinct from quantizing weights) is a further, separate optimisation llama.cpp supports | §2.5's aside on KV-cache quantization |

## Cluster 3 — The dataclass / Pydantic trade-off (Part 3)

| Source | What it defines | Relevant to |
|---|---|---|
| PEP 557 — "Data Classes" | The standard-library `@dataclass` decorator's specification and design rationale | §3.1 |
| Pydantic documentation, `docs.pydantic.dev` | What automatic validation, coercion, and JSON-schema export actually provide, for an honest comparison rather than a strawman | §3.1's trade-off argument |
| Fowler, "Consumer-Driven Contracts," martinfowler.com, 2006 | Already cited in Chapter 4A Cluster 5 — re-cited here because §3.4's "tests that should fail" discussion is the same contract-testing philosophy applied to a concrete file | §3.4 |
| pytest documentation — "Skipping test functions" | The official behaviour of `pytest.importorskip` and the skip/fail distinction | §3.4 |

## Cluster 4 — OCR and the vector database (referenced, not deep-dived, in Part 5)

| Source | What it defines | Relevant to |
|---|---|---|
| Tesseract OCR documentation, `tesseract-ocr.github.io` | Installation and the binary-vs-wrapper distinction §5.3 relies on | §5.3 |
| ChromaDB documentation, `docs.trychroma.com` | The metadata-value type constraint `to_chroma_record()` (schemas.py) works around | §3.2 |

---

## Using this bibliography

Unlike Chapters 3 and 4, most of what you cite from this chapter in your final report will be **documentation with an access date**, not peer-reviewed papers — that is expected and correct for an engineering-setup chapter, not a shortcut. Where a genuine research paper is the right citation (the Llama 3 architecture paper, the quantization papers), use it; where the honest source is "the project's own documentation," cite that plainly rather than dressing it up as something it isn't.

---

**Back to:** [Chapter 5 — Environment Setup & Offline LLM](ch05-environment-setup-and-offline-llm.md) · **Next:** Chapter 6 — Document Ingestion
