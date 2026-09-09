# Presentation #2 — Slide Plan (Day 4)

> **How to use this.** Same convention as [`ppt1-slide-plan.md`](ppt1-slide-plan.md): a **headline** goes on the slide verbatim (a full assertion, not a topic label), **on-slide content** is the minimum visual, **speaker notes** are what you say aloud and never appear on screen. Design rationale for all of this is in [Chapter 2 §1.7–1.8](../docs/chapters/ch02-synopsis-and-presentation.md).
>
> **Target: 12 slides, 10 minutes.** If short on time, cut slides 6 and 10 first.

---

## Global settings

Identical to `ppt1-slide-plan.md`: Calibri/Arial, title ≥ 32 pt, body ≥ 24 pt, high contrast, no animations, slides numbered, exported as `.pptx` **and** `.pdf`, on a pen drive **and** in cloud storage.

---

## Slide 1 — Title

**On slide**
> **RAGNova**
> Timeline, Team Split & Module Contracts
>
> ⟨Member 1⟩ · ⟨Member 2⟩ · ⟨Member 3⟩ · Presentation #2 · Day 4

**Speaker notes (Member 1, ~15 s)**
> Three days ago we defined the problem and the approach. Today we show exactly how three people build it in parallel without the pieces colliding on Day 12.

---

## Slide 2 — Bridge from Presentation #1

**Headline:** `Three days defined WHAT to build; today defines HOW three people build it together`

**On slide** — three short lines:
- Day 1–3: problem, objectives, literature, architecture ✅
- Day 4 (today): schedule, module boundaries, interface contract
- Day 5–13: nine days of parallel implementation

**Speaker notes (Member 1, ~30 s)**
> Quick recap: we're building RAGNova, an offline multimodal RAG system, for the reasons and with the architecture we presented on Day 2. Today is not new scope — it's the plan that makes the next nine days actually work as three people instead of one person doing three times the work sequentially.

---

## Slide 3 — Module split, justified

**Headline:** `The system splits by modality — the split that minimises coupling, not the one that's convenient`

**On slide** — the module table:

| Track | Owner | Chapters | Owns |
|---|---|---|---|
| A — Text + RAG core | Member 1 | 6, 7, 10 | Parsing, chunking, embeddings, retrieval, generation, citations |
| B — Vision + audio | Member 2 | 8, 9 | CLIP image search, OCR, Whisper transcription |
| C — Interface | Member 3 | 11, 12 | Streamlit app, wiring, integration, testing |

**Speaker notes (Member 2, ~55 s)**
> We didn't split this three ways arbitrarily. Software engineering has a real vocabulary for what makes a split good: coupling, how much one person's change forces another's, and cohesion, how much what's inside one module actually belongs together. Splitting by modality — text, vision-plus-audio, interface — gives us the lowest coupling of every split we considered, because the only thing any two tracks share is one agreed data shape. Splitting by pipeline stage instead — one person for parsing, one for embedding, one for storage — would force everyone to touch every file type, all the time.

---

## Slide 4 — The interface contract

**Headline:** `One shared schema is the only thing any two tracks must agree on`

**On slide** — the strawman field list, small code block:
```
Chunk: chunk_id, source, modality, text,
       page (docs), start_s/end_s (audio),
       embedding_model
```
*Finalized in Chapter 5 — this is the requirements handoff.*

**Speaker notes (Member 2, ~45 s)**
> Everything inside a track is that person's to change freely — which parser, which chunk size, which model checkpoint. The one thing that isn't free to change unilaterally is the shape of what gets handed to everyone else. We froze the requirements for that shape today; the real implementation lands in Chapter 5. And it isn't just a document — it's backed by an automated contract test that fails the build the moment any track's output stops matching, so drift gets caught the day it happens, not on integration day.

---

## Slide 5 — The critical path

**Headline:** `The schedule is fully critical — there is no natural slack anywhere`

**On slide:** the dependency-graph diagram (from Chapter 4 §5's ASCII diagram), critical path highlighted, both chains shown converging at Day 9.

**Speaker notes (Member 3, ~70 s — the technical core of this talk)**
> We didn't just copy Day 1's rough timeline forward. We built the actual dependency graph and computed a real critical path — which activities have zero room to slip. The finding: both tracks, text-plus-RAG and vision-plus-audio, take exactly four days of real work and converge at the same point. Neither track has spare capacity. That's a more useful thing to know today than a false sense that one side has room to breathe — it tells us exactly where a delay would actually hurt.

---

## Slide 6 — Gantt vs. dependency graph

**Headline:** `A Gantt chart shows WHEN; it doesn't show WHY — and that gap was hiding a real ambiguity`

**On slide** — small before/after: original roadmap's Ch10 at "Day 10–11" next to the corrected "Day 8–9," with one line: *the dependency graph, not the calendar, tells you the true earliest start.*

**Speaker notes (Member 3, ~40 s)**
> Our own Day 1 plan had an unexamined two-day gap in it — a track sitting idle on the calendar with nothing actually forcing that. We only found it by building the dependency graph instead of trusting the bars. That's the general lesson, not just a fix to our own plan: a Gantt chart is a claim about dates, not a proof of them.

*(Cut this slide first if short on time — the finding is still stated on Slide 5.)*

---

## Slide 7 — Why Day 12, not Day 13

**Headline:** `Integration is scheduled with one full day of deliberate buffer before the three tracks converge`

**On slide** — one line, large:
> *A zero-float schedule needs an inserted buffer, not found slack.*

**Speaker notes (Member 3, ~50 s)**
> Because the schedule is fully critical, R6 — the risk that three independent tracks won't fit together — isn't hypothetical. Our mitigation is a deliberate project buffer: one day, held in reserve, positioned exactly before the point where all three tracks have to agree. Scheduling integration for Day 13 instead — finish everything, then integrate — would spend that buffer before it exists, leaving zero recovery time before the report is due the next day.

---

## Slide 8 — Bus factor and documentation

**Headline:** `Every module ships with a README and an automated test — not just comments`

**On slide** — two lines:
- Bus factor per track: **1**
- Requirement: module README (inputs/outputs/how to run) + passing contract test

**Speaker notes (Member 1, ~40 s)**
> Right now, exactly one person understands each track — that's just the arithmetic of three people on three tracks. We're not pretending otherwise. What we can control is whether someone else could pick up a track's work if they had to. That requires two concrete things, written at the point a module ships, not scrambled together during a crisis: a short README, and a test that proves what the module currently does.

---

## Slide 9 — Sync cadence

**Headline:** `Daily async check-ins, plus four checkpoints tied to real dependencies — not a fixed daily meeting`

**On slide** — the four checkpoint days: **Day 5** (schema freeze) · **Day 7** · **Day 9** (both tracks converge) · **Day 12** (integration)

**Speaker notes (Member 1, ~40 s)**
> For a three-person team, a fixed daily standup costs proportionally more than it does for a large team, because there are only three relationships to keep in sync in the first place. So instead: a two-minute written check-in every day, plus real synchronous time on the four days the dependency graph says actually matter.

---

## Slide 10 — The 2-member fallback

**Headline:** `If the team drops to two people, the reassignment is already worked out — not improvised`

**On slide** — small table: Track C dissolves; interface work splits between Track A and Track B; recomputed schedule is tighter, not just thinner.

**Speaker notes (Member 3, ~35 s)**
> This isn't a hedge we're hoping we don't need. We worked out exactly what changes if we're down to two people, and recomputed what that does to the schedule — it gets tighter, not just "the same plan split two ways."

*(Cut this slide second if short on time.)*

---

## Slide 11 — Five more decisions, locked in

**Headline:** `Five more architecture decisions are now recorded as ADRs, each with the alternative we rejected`

**On slide** — compact table:

| Decision | Rejected alternative |
|---|---|
| Local quantized LLM | Cloud API |
| ChromaDB | FAISS / Qdrant |
| Whisper transcription | Native audio embeddings (CLAP) |
| Fixed-size chunking, tuned by ablation | A size taken from literature |
| Rank-based cross-modal merge | Raw-score merge |

**Speaker notes (Member 2, ~40 s)**
> Same discipline as Monday's literature review: every non-obvious choice gets written down with the alternative we said no to, and why. Five more of those landed today, all before a line of pipeline code exists.

---

## Slide 12 — Close

**Headline:** `Nine days, three tracks, one contract, one day of integration buffer`

**On slide** — three lines:
- Modules split by coupling, not convenience
- Schedule is fully critical — the buffer is deliberate, not lucky
- Every module ships documented, so the plan survives an absence

> **Thank you — questions?**

**Speaker notes (Member 1, ~20 s)**
> Nine implementation days, three independently-buildable tracks, one shared contract, and one day of buffer placed exactly where the schedule has none to spare. Thank you — happy to take questions.

---

## Q&A preparation

| Area | Lead | Backup |
|---|---|---|
| Module split, coupling/cohesion, Conway's Law | ⟨Member 2⟩ | ⟨Member 1⟩ |
| Critical path, float, the buffer argument | ⟨Member 3⟩ | ⟨Member 1⟩ |
| Team dynamics, bus factor, 2-member fallback | ⟨Member 1⟩ | ⟨Member 3⟩ |

**Drill [Chapter 4 §6.2](../docs/chapters/ch04-timeline-and-team-split.md)'s full question bank before presenting.** The single question most likely to be pushed on: *"why exactly Day 12, not Day 13?"* — every member must be able to give the buffer argument (Slide 7), not just "to be safe."

If asked something not prepared for:

> ✅ *"We haven't stress-tested that scenario yet — our plan is to check it during the Day 12 integration and we'd expect [reasoned guess]."*

Do not bluff.

---

## Pre-presentation checklist

- [ ] 12 slides or fewer; every headline a full assertion
- [ ] Dependency-graph diagram (Slide 5) and Gantt-vs-graph comparison (Slide 6) legible from the back row
- [ ] All `⟨FILL⟩` placeholders replaced
- [ ] Speaker notes written for every slide
- [ ] Rehearsed twice, out loud, standing, timed
- [ ] Every member can state the Day-12 buffer argument unprompted
- [ ] Exported as PDF **and** pptx, on a pen drive **and** in cloud storage
