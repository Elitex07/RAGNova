# ADR-002: Use a local quantized LLM rather than a cloud API

## Status
Accepted — Day 4

## Context

The system needs a language model to generate answers from retrieved context (Chapter 1
§1.3.1). Two deployment options exist: call a hosted API (OpenAI, Anthropic, Google), or
run a model's weights directly on team hardware.

Three hard constraints bound the choice:

- **Objective O6 requires the system to function with zero network calls at query time,**
  verified by the airplane-mode acceptance test (Ch1 §1.9.3).
- Team hardware is CPU-only laptops with 8–16 GB RAM (Ch1 §1.9.2).
- The project has no budget for recurring API costs across a semester's worth of testing
  and demonstration.

## Decision

Run a 4-bit quantized Llama 3.2 3B Instruct model locally via Ollama, which serves it over
a local HTTP API (`http://localhost:11434`) that never leaves the machine.

## Alternatives considered

1. **A cloud LLM API (GPT-4-class, Claude, Gemini).** Rejected outright: violates Objective
   O6 by construction — any API call requires network access, and any document content
   sent to a third-party service violates the confidentiality motivation stated in Chapter 1
   §1.7. This is not a close call.
2. **A full-precision (FP16) local model.** Rejected on hardware grounds: a 3B model at
   FP16 requires roughly 6 GB of memory for weights alone [GPTQ], which does not comfortably
   coexist with an embedding model, CLIP, Whisper, and the operating system within an 8 GB
   budget (Ch1 §1.9.2's RAM table).
3. **A larger local model (7B–13B), full or quantized.** Rejected for this team's hardware:
   even quantized, a 7B model roughly doubles the memory and halves the throughput of the
   3B model, with retrieval quality gains that are not the bottleneck here — Chapter 1
   §1.3's core argument is that RAG converts the task from *recall* to *reading
   comprehension over a supplied passage*, a task a 3B model handles adequately.
4. **A cloud API with a "self-hosted mode" fallback for offline demos only.** Rejected:
   maintaining two code paths (cloud and local) doubles implementation and testing effort
   for a 9-day sprint, for a capability (cloud mode) that would never actually be
   demonstrated or graded.

## Consequences

**Positive**
+ Zero recurring cost; unlimited local testing during development.
+ Genuinely verifiable offline operation — the airplane-mode test has real teeth.
+ No API rate limits during the heaviest testing days (Ch10, Ch12).

**Negative**
− Noticeably weaker generation quality than a frontier hosted model — must be disclosed
  honestly in the report's limitations section, not hidden.
− Generation latency is CPU-bound and slower than a hosted API; the < 15 s end-to-end
  target (Ch1 §1.10) is a real engineering constraint, not a formality.
− The whole team must complete the ~2 GB model download before Day 5 (Ch1 §3.4) — a
  dependency on early, reliable internet access that a fully cloud-based design would not
  have.

**Implications for other components**
- Fixes the deployment target Chapter 5's environment setup builds against.
- Fixes the prompt-length budget (Ch1 §1.9.2's context-window discussion) that Chapter 10's
  top-K selection must respect.

## Revisit if

Team hardware is upgraded with a discrete GPU capable of running a larger model within the
same latency budget, or the offline requirement is relaxed for a future extension of the
project.

---

*Citation [GPTQ]: Frantar, Ashkboos, Hoefler and Alistarh, "GPTQ: Accurate Post-Training
Quantization for Generative Pre-trained Transformers," ICLR 2023. **Verify before use.***
