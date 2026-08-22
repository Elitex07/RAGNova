# ADR-001: Use retrieval-augmented generation rather than fine-tuning

## Status
Accepted — Day 3

## Context

The system must answer questions about the user's own files — documents, images and
recordings that no pretrained model has ever seen. A language model must therefore be
given access to this content somehow.

Three hard constraints bound the choice:

- **Objective O4 requires numbered citations** resolving to a source file and location.
- **Objective O6 requires fully offline operation** on commodity hardware (CPU-only,
  8–16 GB RAM).
- New files must become queryable **immediately**, not after a batch process measured in
  hours.

## Decision

Retrieve relevant content at query time and supply it in the prompt, instructing the model
to answer only from that evidence. The model's weights are never modified.

## Alternatives considered

1. **Fine-tuning the model on the corpus.** Rejected on four independent grounds, any one
   of which would be sufficient:
   - **No citations are possible.** Once knowledge is absorbed into weights it cannot be
     traced back to page 2 of a specific PDF. This alone disqualifies fine-tuning, because
     citation is an objective, not a nice-to-have.
   - **Requires GPU hardware and hours per run**, which we do not have and which conflicts
     with the offline-on-a-laptop constraint.
   - **Must be repeated for every new file**, so "add a document" becomes a training job.
   - **Teaches style more reliably than facts**, and does not eliminate hallucination —
     the model may still generate fluent, unsupported claims [22].

2. **Long-context stuffing — paste every document into every prompt.** Rejected: the
   corpus (50–200 files) far exceeds any available context window, attention cost grows
   roughly quadratically with prompt length, and accuracy degrades for content positioned
   mid-prompt [23]. It also scales inversely with corpus size, which is the wrong direction.

3. **Keyword search plus manual reading — no generation at all.** Rejected: fails on
   paraphrase and synonymy, cannot search images by description, and produces no synthesised
   answer. It would satisfy none of O2, O3 or O4.

4. **Retrieval-augmented fine-tuning (train the model to use retrieved context better).**
   Rejected as out of scope: it presupposes a working retrieval system, needs GPUs, and the
   benefit over prompting an already instruction-tuned model is not worth the cost at this
   scale. Noted as future work.

## Consequences

**Positive**
+ Adding a file costs seconds — index once, immediately queryable.
+ Provenance metadata survives end to end, making citation a structural property rather
  than a presentation-layer addition.
+ **A small model becomes sufficient.** Retrieval changes the model's task from *recalling*
  facts to *reading* a supplied passage. Reading comprehension over a provided paragraph is
  a much easier task than recall, which is precisely why a 3B model works here — and
  therefore why the offline constraint is satisfiable at all.
+ Modality-agnostic: retrieval does not care whether a segment came from a PDF, an OCR'd
  screenshot, or a transcript, so one architecture serves all four formats.

**Negative**
− Answer quality is now bounded by retrieval quality. A bad retrieval produces a confidently
  wrong or unhelpful answer, so retrieval becomes the component that must be evaluated most
  carefully.
− Requires building and maintaining an indexing pipeline and a vector store — substantially
  more engineering than calling a model.
− Latency includes a retrieval step on every query.
− **Hallucination is reduced, not eliminated.** The model can still misattribute a claim to
  the wrong retrieved segment, which is why citation markers are validated and retrieved
  text is displayed alongside each citation.

**Implications for other components**
- Retrieval quality becomes the primary evaluation target (Recall@5, MRR).
- Every ingestion pipeline must emit provenance metadata (ADR-003, Ch 6).
- The prompt must number context segments and demand citation (Ch 10).

## Revisit if

- Citation ceases to be a requirement **and** the corpus becomes static, at which point
  fine-tuning's inference-time simplicity might win.
- Context windows and attention costs improve enough that whole-corpus prompting becomes
  practical at our scale — currently far from true.

---

*Citations [22] (Ji et al., hallucination survey, ACM Computing Surveys 2023) and [23]
(Liu et al., "Lost in the Middle", TACL 2024). **Verify before use.***
