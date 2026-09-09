# Chapter 4 — Timeline, Team & Modular Work Split (Day 4)

> **Deliverables today:** **Presentation #2** (recap, finalized timeline, module ownership, risk highlights, interface contract), a **computed critical-path schedule** replacing the informal Day-1 Gantt guesses, a **finalized module ownership table**, an **interface-contract specification**, and **five more Architecture Decision Records** (ADR-002, 004, 005, 006, 007).
>
> **Prerequisites:** [Chapter 1](ch01-objective-and-problem-identification.md) §2.7 (the risk register — you will need R6 and R7 today), and [Chapter 3](ch03-literature-review-and-methodology.md) §3.3 (ADR discipline — you will write five more today).
>
> **Companion file:** [Chapter 4A — Scheduling & Teamwork Sources](ch04a-scheduling-and-teamwork-sources.md) — the literature behind everything in Parts 1–3: coupling and cohesion, Conway's Law, Brooks's Law, critical-path scheduling, Tuckman's stages.
>
> **The framing for today.** It is tempting to treat Day 4 as an administrative chore — "who does what." It is not. Today is about designing **boundaries** precise enough that *who* does *what* stops being able to go wrong. A good boundary is one where three people can work for nine days without talking to each other more than briefly, and still arrive at something that fits together on Day 12. That property does not happen by agreement — it is engineered, and the engineering has a name, a theory, and a set of failure modes you are about to learn to recognise before you hit them.

---

## How to read this chapter

| Part | What it does | Time |
|---|---|---|
| **Part 1 — LEARN: Modular Architecture** | Why splitting files three ways fails; coupling/cohesion; information hiding; Conway's Law; Brooks's Law; contract tests — the mechanism behind the Day-5 schema freeze. | ~70 min |
| **Part 2 — LEARN: Scheduling Theory** | Gantt vs. dependency graph vs. critical path method; a full worked CPM calculation on RAGNova's actual 14-day plan; why R6's mitigation is a *deliberate buffer*, not luck. | ~60 min |
| **Part 3 — LEARN: Team Dynamics** | Brooks's communication-cost formula; Tuckman's stages mapped onto Day 4; sync cadence; bus factor and R7; code review for three people; the 2-member fallback, worked out. | ~50 min |
| **Part 4 — DECIDE** | The finalized module table; the interface-contract requirements; a strawman schema (deferred to Chapter 5); which five decisions become ADRs today. | ~30 min |
| **Part 5 — BUILD** | The corrected schedule, the dependency-graph diagram, the sync-cadence artifact, and delegation to the five ADRs and PPT #2. | ~4 hours |
| **Part 6 — CHECK** | Rubric, question bank, failure modes, completion checklist. | ~40 min |

**Learning outcomes.** You will be able to: score a proposed module split against coupling and cohesion rather than convenience; state Parnas's information-hiding principle and use it to decide what a module owner is allowed to change unilaterally; state Conway's Law and use it (in both directions) to explain why your team structure and your software structure must match; explain why adding a person to a late project can make it later, with the arithmetic; define a contract test and sketch one; build a dependency graph from a set of chapter-day assignments and distinguish it from a Gantt chart; run a full forward-and-backward-pass critical path calculation by hand; explain why a schedule with zero float needs a *deliberately inserted* buffer rather than relying on luck; state Brooks's communication-cost formula and use it to answer "why not just add a fourth person"; name Tuckman's stages and say what "norming" concretely requires; define bus factor and compute it for your own team; and design a sync cadence justified by argument rather than habit.

---

# Part 1 — LEARN: Modular Architecture & Work Decomposition

## 1.1 Why "just split the files three ways" fails

Imagine the naive plan: three people, one Python project, each person "owns" a rough third of the work and edits whatever files that requires. No formal boundaries — just goodwill and Slack messages.

Play this forward nine days. Concretely, here is what breaks, and *why* each failure is not bad luck but a predictable consequence of having no boundary:

1. **Semantic merge conflicts.** Git can auto-merge two edits to different lines of the same file. It cannot merge two *meanings*. If Member 1 changes what a function returns and Member 2 is simultaneously writing code that assumes the old return shape, Git will merge the text cleanly and the program will still be wrong. Git conflict tools catch textual collisions; they are blind to semantic ones.
2. **Silent behavioural coupling.** Member 3's UI code calls a function Member 1 wrote. Member 1 refactors it on Day 8 to fix an unrelated bug, changing an edge case Member 3's code silently depended on. Nothing errors. The UI just occasionally returns wrong answers, discovered — if you are lucky — during Chapter 12's testing, five days later, with no clear link back to Day 8.
3. **One person's bug blocks two others' demos.** Without a boundary, "Track A's code" and "Track B's code" and "Track C's code" are not real categories — they are just informal descriptions of who last touched what. A crash anywhere can prevent anyone from running the whole system to check their own part.
4. **Nobody can work in parallel without constant negotiation.** Every non-trivial change requires asking "does this affect what you're doing?" — which defeats the entire purpose of having three people.

None of this is about skill or discipline. It is what happens, structurally, whenever the boundary between people's work is undefined. **The fix is not "communicate more." It is "design the boundary so most changes don't need to be communicated at all."** That is what the rest of Part 1 is about.

## 1.2 Coupling and cohesion — the formal vocabulary for "will this cause conflicts"

Software engineering has precise vocabulary for exactly the failure modes in §1.1, developed originally by Constantine and Yourdon in the 1970s for structured design, and it remains the right first tool for scoring any proposed module split.

**Coupling** measures how much one module's internals leak into another's — how much a change in module X forces a change in module Y. Lower is better. A simplified taxonomy, worst to best:

| Coupling type | What it means | Example failure |
|---|---|---|
| **Content coupling** | One module directly reads or modifies another's internal state | Track C reaches into Track A's internal dictionary instead of calling a function |
| **Common coupling** | Modules share mutable global state | A shared global `current_model` variable that any track can silently change |
| **Control coupling** | One module passes a flag telling another *how* to do its job internally | `retrieve(query, use_track_b_hack=True)` |
| **Stamp coupling** | Modules share a compound data structure but each only uses part of it | Passing a whole raw file object when only the filename is needed |
| **Data coupling** | Modules communicate only through well-defined parameters and return values | Track C calls `answer_query(text) -> AnswerWithCitations` and nothing else |

**Cohesion** measures how strongly the responsibilities *within* one module belong together. Higher is better. Worst to best: coincidental (grouped by accident — "utils.py"), logical (grouped by category but not by collaboration), temporal (grouped because they run at the same time), procedural, communicational (operate on the same data), sequential (output of one feeds the next), and **functional cohesion** — everything in the module exists to do exactly one well-defined job.

**The rule the taxonomy gives you:** design for low coupling between modules and high cohesion within each one. Applied to RAGNova, this is not abstract — it directly scores your candidate splits:

| Candidate split | Coupling | Cohesion | Verdict |
|---|---|---|---|
| **By pipeline stage** (one person owns "parsing," another "embedding," another "storage" — each touching every file type) | High — every stage-owner must touch PDF code, image code, and audio code; a change to the chunk schema forces edits in all three people's code simultaneously | Low — each person's code has nothing in common except "runs at roughly the same pipeline step" (temporal cohesion) | ❌ Rejected |
| **By person, arbitrarily** (divide files alphabetically or by rough LOC count) | Coupling is essentially random, since it tracks nothing about the actual dependency structure | Cohesion is coincidental | ❌ Rejected |
| **By modality** (Track A: text/documents; Track B: images/audio; Track C: interface) | Low — the only thing tracks share is the schema (data coupling, the best kind) and function signatures | High — everything in Track A's code exists to answer "how do I make text searchable"; everything in Track B's exists to answer the same question for images and audio | ✅ **Chosen** |

This is the argument for the split already sketched in `ROADMAP.md` — not "because three people, three roughly-equal piles of work," but because a by-modality split is the one that minimises coupling and maximises cohesion, which is the property that actually determines how much the tracks will collide over nine days.

## 1.3 Information hiding — deciding *what* the boundary hides (Parnas)

Coupling and cohesion tell you a split is good. They do not tell you *where exactly* to draw the line. For that, the right principle is David Parnas's 1972 paper "On the Criteria to Be Used in Decomposing Systems into Modules," which argues for a specific, non-obvious rule: **decompose by what design decision each module hides, not by the sequence of operations the system performs.**

Parnas's own famous demonstration: given the same program (a KWIC index), a decomposition based on the flowchart of processing steps produces a system where a single design change — say, changing how lines are stored — ripples through nearly every module, because every module implicitly assumed the old storage format. A decomposition based on *hidden decisions* — one module owns "how lines are stored," and everyone else only calls its interface — isolates that same change to one module.

**Applied to RAGNova, this answers a subtler question than §1.2 does: what exactly is each track allowed to change on its own, without asking anyone?**

| Track | What it hides (free to change internally, any day, without asking) | What it must NOT change unilaterally |
|---|---|---|
| **A — Text + RAG core** | Which PDF parser, chunking algorithm, chunk size, embedding model, prompt template, LLM temperature | The shape of the chunk object it emits into the shared index |
| **B — Vision + audio** | Which OCR engine, CLIP checkpoint, Whisper model size, image-embedding batching strategy | The shape of the chunk/record it emits; the collection names |
| **C — Interface** | Streamlit layout, chat rendering, citation-expansion UI, styling | The function signatures it calls into Track A/B's retrieval and ingestion entry points |

**This table is the practical output of information hiding, and it is worth more than the coupling/cohesion table in §1.2**, because it turns a general design principle into a specific, checkable rule each person can consult when they're unsure whether a change is "theirs to make." The rule of thumb: *if the change is only visible by calling your own functions, do it. If the change is visible to someone calling* into *your functions, it needs Part 4's interface contract to change.*

## 1.4 Conway's Law, and using it on purpose

In 1968, Melvin Conway observed: *"organizations which design systems... are constrained to produce designs which are copies of the communication structures of these organizations."* Informally: **your software will end up shaped like your org chart, whether or not you designed it that way.**

**Why this is true, not just a cute observation.** A module boundary that requires two people to have a long conversation every time it's crossed is expensive to cross. Under time pressure, people unconsciously route around expensive boundaries — either by not making the change that requires the conversation, or by quietly merging the two modules back into one, or by adding an informal side-channel (a shared file, a hardcoded shortcut) that bypasses the "official" interface. The result: six months later, the *actual* architecture matches who talks to whom, regardless of what a design document once said.

**The corollary — the "Inverse Conway Maneuver" — is what you do with this on purpose:** design the *team communication structure* you want, and the architecture tends to follow it, because the path of least resistance for busy people is to build things that match how they already talk to each other.

Two applications to RAGNova, right now:

1. **The 3-track, by-modality split (§1.2) only works if it matches how the team actually communicates day-to-day.** If Member 1 and Member 2 end up chatting constantly about implementation details while Member 3 works in isolation, Conway's Law predicts the *real* boundary will drift toward "A+B combined" vs. "C alone" — regardless of what this chapter says the modules are. Watch for this. If it happens, either the communication pattern is telling you something true about a hidden dependency (revisit §1.3's table), or the team needs to consciously restore the intended boundary.
2. **The 2-member fallback (worked out fully in §3.6) is an Inverse Conway Maneuver by construction.** When Track C dissolves, the team is *deliberately* choosing a new communication structure (two people, each absorbing part of a third role) and the module boundaries must be redrawn to match it — not left as three modules now awkwardly owned by two people, which would recreate exactly the ambiguous ownership §1.1 warned about.

## 1.5 Brooks's Law, the staffing half

Frederick Brooks, reflecting on the disastrously late OS/360 project in *The Mythical Man-Month* (1975), stated what is now one of the best-known findings in software engineering: **"Adding manpower to a late software project makes it later."**

The mechanism (the communication-cost half is derived properly with the formula in Part 3 §3.1 — this section previews *why* it matters for decomposition specifically): a new person is not immediately productive. They must be brought up to speed by people who are already busy, so the *existing* team's output temporarily drops before the new person contributes anything. If the project is already late, that temporary dip lands at exactly the worst possible time.

**Why this belongs in the decomposition section, not just the team-dynamics section:** it is the direct argument against the instinctive Day-9 fix of "let's just get a friend to help for two days." A friend joining on Day 9 does not inherit five days of context about the schema, the chunking decisions, or the prompt design — bringing them up to speed consumes exactly the senior time you don't have. **The correct response to a slip is not more people; it is the float and buffer machinery Part 2 builds**, and, failing that, the documentation discipline Part 3 builds so that *existing* team members can absorb the work without a ramp-up cost.

## 1.6 Contract tests — what the Day-5 schema freeze actually buys you

`ROADMAP.md` and `methodology-draft.md` both refer to a "shared data schema frozen before implementation begins" as the thing that lets three tracks develop in parallel. It is worth being precise about *why* a frozen schema is sufficient, and what specifically enforces it — because "we agreed on a schema" and "we have a schema that cannot silently drift" are very different guarantees.

**The concept, borrowed from microservice engineering, is a *contract test* (sometimes "consumer-driven contract").** The idea: instead of one team member reviewing another's code line by line, write an automated test — owned jointly, checked into the repository, run by everyone — that asserts *"whatever this module produces satisfies what its consumers actually need,"* independent of how it's implemented. A contract test does not test correctness of business logic. It tests **shape compatibility.**

**Why this is the real enforcement mechanism, and a schema document alone is not:** a markdown page describing a schema is a promise. Nothing stops Track B's code from silently emitting a chunk missing the `page` field, or with `start_s` as a string instead of a float, three days after everyone agreed it wouldn't. A contract test *fails the build* the moment that happens — on the day it happens, not on Day 12 when Track C tries to render a citation and gets a crash nobody can immediately explain.

**A worked sketch** (pseudocode — the real implementation belongs to Chapter 5, which owns the actual schema; this shows what the test checks, not how it's coded):

```
FUNCTION test_chunk_contract(chunk):
    ASSERT chunk.chunk_id is a non-empty string
    ASSERT chunk.source is a non-empty string (a valid file path)
    ASSERT chunk.modality is one of {"pdf", "docx", "image", "audio"}
    ASSERT chunk.text is a non-empty string
    IF chunk.modality in {"pdf", "docx"}:
        ASSERT chunk.page is an integer >= 1
    IF chunk.modality == "audio":
        ASSERT chunk.start_s is a float >= 0
        ASSERT chunk.end_s > chunk.start_s
    ASSERT chunk round-trips: store it in ChromaDB, retrieve it, all fields unchanged

FIXTURES (one minimal example per track, owned by that track, checked in Day 5):
    text_fixture  = { one real chunk Track A's parser actually produces }
    image_fixture = { one real record Track B's CLIP pipeline actually produces }
    audio_fixture = { one real chunk Track B's Whisper pipeline actually produces }

RUN test_chunk_contract on all three fixtures, on every commit.
```

**The property this buys you:** any track can change its internal implementation freely (§1.3) as long as its fixture still passes. The moment a change breaks the contract, the test fails *immediately, locally, on that person's own machine*, days before it would otherwise surface as a mysterious Day-12 integration bug. This is the single cheapest piece of insurance the whole schedule has, and Part 5 asks the team to write the actual fixture stub today.

## 1.7 What if there is no schema freeze — the counterfactual, played out

Worth spelling out once, so the cost is concrete rather than abstract. No frozen schema, no contract test. Each track builds against their own best guess of what a "chunk" should look like, because nobody stopped them to agree.

Day 12 arrives. Track A's chunks are Python dataclasses with a `page: int` field. Track B's image records are plain dictionaries with a `page_number: str` field (a different name, a different type — nobody decided, so nobody matched). Track C's rendering code, written against yet a third guess, crashes on both.

**The actual cost is not "rename a field" — it's the compounding cost of discovering three independent, undocumented assumptions on the one day the schedule has the least slack.** Whoever discovers the mismatch first has to reverse-engineer two other people's undocumented decisions before they can even *propose* a fix, and — per Brooks's Law (§1.5) — the person best positioned to fix it fast is whoever wrote the offending code, who is now needed on two fronts at once. This is R6 from Chapter 1's risk register, stated in full rather than as a one-line summary, and it is the reason §1.6's ten-line pseudocode test is worth writing today rather than "whenever there's time."

---

# Part 2 — LEARN: Project Scheduling Theory

## 2.1 Three ways to represent a plan, and what each one cannot tell you

**A Gantt chart** — the horizontal-bar chart everyone associates with "project timeline" — shows *when* each activity happens on a calendar. It is excellent at giving a quick visual sense of overlap and duration. **It is bad at showing *why* an activity starts when it does.** A bar starting on Day 10 looks exactly the same whether Day 10 was chosen because of a hard dependency or because someone typed a date into a spreadsheet. `ROADMAP.md`'s own chapter table is, structurally, a Gantt chart — and §2.3 below will show exactly what that hides.

**A dependency graph** shows *why*: which activities must finish before which others can start, with no calendar attached. It is excellent at exposing the true structure of a plan. It is bad at telling you, on its own, *when* anything actually happens in real dates, or how much slack exists.

**The Critical Path Method (CPM)**, developed independently at DuPont (Kelley and Walker) and in the PERT technique used for the U.S. Navy's Polaris program in the late 1950s, fuses the two: take the dependency graph, attach a duration to each activity, and compute the actual calendar the dependencies force. CPM answers the two questions neither chart alone can: **which activities have zero room to slip (the critical path), and exactly how much room does everything else have (float)?**

## 2.2 CPM mechanics, on a toy example first

Before touching RAGNova's real schedule, work the mechanism on four abstract activities so the *procedure* is understood independently of the specific numbers that follow.

```
Activity  Duration   Depends on
   X         2 days      —
   Y         3 days      X
   Z         1 day       X
   W         2 days      Y, Z
```

**Forward pass** — compute earliest start (ES) and earliest finish (EF = ES + duration) for each activity, in dependency order:

```
X: ES=0, EF=2
Y: ES=EF(X)=2, EF=5
Z: ES=EF(X)=2, EF=3
W: ES=max(EF(Y), EF(Z))=max(5,3)=5, EF=7
```

**Backward pass** — starting from the project's required finish (here, simply EF(W)=7, since nothing forces an earlier deadline), compute latest finish (LF) and latest start (LS = LF − duration) working backward:

```
W: LF=7, LS=5
Y: LF=LS(W)=5, LS=2
Z: LF=LS(W)=5, LS=4
X: LF=min(LS(Y), LS(Z))=min(2,4)=2, LS=0
```

**Float = LS − ES** for each activity:

```
X: 0−0 = 0   → critical
Y: 2−2 = 0   → critical
Z: 4−2 = 2   → 2 days of float — Z can slip up to 2 days without delaying the project
W: 5−5 = 0   → critical
```

**The critical path is X → Y → W** (the chain of zero-float activities). Z is *not* on the critical path — it could start up to two days late and the project would still finish on day 7. This is the entire mechanism. Everything in §2.3 is this same four-step procedure (forward pass, set the deadline, backward pass, subtract) applied to fourteen real days instead of seven abstract ones.

## 2.3 The worked example — RAGNova's actual critical path

`ROADMAP.md`'s chapter table, read as a Gantt chart, gives day-ranges: Ch6 "Day 6," Ch7 "Day 7," Ch10 "Day 10–11," Ch8 "Day 8–9," Ch9 "Day 9–10," Ch11 "Day 11–12," Ch12 "Day 12–13," Ch13 "Day 14." That is a calendar. It is not a dependency graph, and — this is the finding worth sitting with — **reading it as a calendar hides a real ambiguity: Ch11 is shown starting Day 11 while Ch10 doesn't finish until the *end* of Day 11.** Either that overlap is intentional (Track C starting against a nearly-finished Track A on its last day) or it is an artifact of writing day-ranges loosely on Day 1, before anyone had reason to compute them precisely. Today is when that gets resolved, by building the dependency graph the Gantt bars were standing in for and computing real dates from it.

**Step 1 — state the dependencies explicitly** (this is the step a Gantt chart skips entirely):

| Activity | Duration | Depends on | Reasoning |
|---|---|---|---|
| **P** — Foundation (Ch 0–5, all-hands) | 5 days | — | Hard sequential prefix; nothing else can start before the schema freezes at the end of Day 5 |
| **A1** — Ch6, doc parsing | 1 day | P | |
| **A2** — Ch7, embeddings + vector store | 1 day | A1 | |
| **A3** — Ch10, RAG core | 2 days | A2 | Needs Track A's own embedding pipeline; does **not** need Track B's outputs to be *built* against the frozen contract — only for full cross-modal testing, which happens at Ch12 |
| **B1** — Ch8, image pipeline | 2 days | P | Only needs the frozen schema, same as A1 |
| **B2** — Ch9, audio pipeline | 2 days | B1 | Same person (Track B); sequential |
| **C1** — Ch11, interface | 2 days | A3 **and** B2 | Needs a real, working `answer_query()` from Track A and real ingestion entry points from Track B to wire the chat app to |
| **D1** — Ch12, integration & testing | 2 days | C1 | The three-way join: full cross-modal testing needs all three tracks' real (not stubbed) output |
| **E1** — Ch13, mid-term report | 1 day | D1 | |

**Step 2 — forward pass** (earliest start/finish, day 0 = start of Day 1):

```
P:  ES=0,  EF=5                         (end of Day 5)
A1: ES=5,  EF=6      B1: ES=5,  EF=7
A2: ES=6,  EF=7      B2: ES=7,  EF=9
A3: ES=7,  EF=9
C1: ES=max(EF(A3), EF(B2)) = max(9,9) = 9,   EF=11
D1: ES=11, EF=13
E1: ES=13, EF=14                        (end of Day 14 — exactly the deadline)
```

**Step 3 — backward pass** (from the fixed 14-day deadline):

```
E1: LF=14, LS=13
D1: LF=LS(E1)=13, LS=11
C1: LF=LS(D1)=11, LS=9
A3: LF=LS(C1)=9,  LS=7      B2: LF=LS(C1)=9,  LS=7
A2: LF=LS(A3)=7,  LS=6      B1: LF=LS(B2)=7,  LS=5
A1: LF=LS(A2)=6,  LS=5
P:  LF=min(LS(A1),LS(B1))=5, LS=0
```

**Step 4 — float** (LS − ES) for every activity:

| Activity | ES | LS | Float | Critical? |
|---|---|---|---|---|
| P | 0 | 0 | 0 | ✅ |
| A1 (Ch6) | 5 | 5 | 0 | ✅ |
| A2 (Ch7) | 6 | 6 | 0 | ✅ |
| A3 (Ch10) | 7 | 7 | 0 | ✅ |
| B1 (Ch8) | 5 | 5 | 0 | ✅ |
| B2 (Ch9) | 7 | 7 | 0 | ✅ |
| C1 (Ch11) | 9 | 9 | 0 | ✅ |
| D1 (Ch12) | 11 | 11 | 0 | ✅ |
| E1 (Ch13) | 13 | 13 | 0 | ✅ |

**The finding, and it is a genuinely important one: every activity is critical.** Track A's chain (Ch6+Ch7+Ch10 = 1+1+2 = 4 days) and Track B's chain (Ch8+Ch9 = 2+2 = 4 days) are exactly the same length, so they converge at C1 with **zero slack on either side.** This is not the comforting "one track has spare capacity" story a quick glance might suggest — it is the opposite, and it is the more useful thing to know on Day 4.

**What this recomputation corrects versus the original roadmap table.** In the *as-written* Gantt bars, Ch10 sits at Day 10–11 — two days later than the dependency graph says it could start (Day 8–9), because nothing in the roadmap's calendar actually explains why Track A should sit idle on Days 8–9 while Track B works. Closing that gap — starting Ch10 right after Ch7, as the dependency graph demands — pulls the entire back half of the schedule forward by one day: Ch11 can run Day 10–11 instead of Day 11–12, finishing a full day before Ch12 was ever scheduled to start (Day 12, unchanged from the original roadmap).

## 2.4 Why R6's mitigation is a *deliberate buffer*, not natural slack — and the sentence that resolves the methodology FILL

Because §2.3 found **zero float anywhere**, the comforting version of R6's mitigation — "there's spare capacity somewhere that absorbs a slip" — is false for this plan. There is no spare capacity. A schedule with zero float is *fragile*: any single-day delay on any activity delays the entire 14-day deadline by exactly one day, with nothing to absorb it.

This is precisely the condition under which project-scheduling practice recommends a **deliberately inserted buffer** rather than relying on found slack — a technique formalised by Eliyahu Goldratt's Critical Chain Project Management (1997) as a *project buffer*: a block of time placed immediately before a project's final deliverable, sized to absorb variability accumulated along the way, rather than padding every individual task (which tends to be wasted through student-syndrome procrastination and Parkinson's-Law expansion — both are worth a sentence in your report if you want to show depth).

**Applying this to §2.3's corrected numbers is exactly what resolves the risk-register mitigation and the `methodology-draft.md` FILL marker.** The corrected schedule shows Track C (Ch11) could finish by end of Day 11 if the whole chain ran at its theoretical minimum. The original roadmap already schedules Ch12 to start Day 12 regardless — which means the roadmap, whether by accident or design, already banks **one full day of margin** between the earliest the inputs to integration *could* be ready and the day integration is actually scheduled to begin.

**The sentence, written to be dropped directly into the methodology's FILL:**

> *Because the critical-path analysis shows a fully critical, zero-float schedule (§2.3), integration is deliberately scheduled to begin on Day 12 rather than the theoretical earliest possible start — reserving one day as a project buffer, in the sense of Goldratt's Critical Chain Method, positioned immediately before the point where all three tracks must converge. Scheduling integration for Day 13 instead, as a naive reading of "finish everything, then integrate" might suggest, would consume this buffer before it exists, leaving zero recovery time between discovering an integration failure and the Day 14 report deadline — precisely the convergence risk risk R6 identifies.*

This is the difference between citing R6 as a platitude ("we'll try to integrate early, to be safe") and citing it as a *computed* consequence of the schedule's own structure.

## 2.5 What if — Member 2 unavailable on Day 9 (two layers)

**Layer 1 — within the buffer.** Suppose Member 2 (Track B) is unavailable for one day, specifically Day 9, the last day of B2 (Ch9). B2's finish slips from Day 9 to Day 10. Recompute forward from there: C1's start becomes `max(EF(A3)=9, EF(B2)=10) = 10`, so C1 now runs Day 10–11 → wait, C1 needs 2 days, so Day 11–12 instead of Day 10–11 — a one-day slip is inherited exactly. **But** Ch12 is still scheduled to start Day 12 per §2.4's buffer — and C1 finishing Day 12 instead of Day 11 exactly consumes that one-day buffer, leaving Ch12 able to start on time. **The single-day absence is absorbed, not because of luck, but because a buffer was deliberately placed exactly where this kind of slip lands.**

**Layer 2 — past the buffer.** Now suppose the absence is two or more days, or Track B hits an unrelated technical problem on top of it. The buffer computed in §2.4 is exactly one day; it has none left to give. At this point, **scheduling theory has nothing further to offer** — CPM tells you precisely how much margin exists and precisely when it runs out, but it cannot manufacture more. This is not a flaw in the method; it is the method being honest about its limits, and it is exactly the moment where the problem stops being a scheduling problem and becomes a team-dynamics and documentation problem: can *someone else* pick up Track B's remaining work without Member 2 walking them through it? That question is answered in Part 3 §3.4 and resolved fully as a worked example in §3.7.

---

# Part 3 — LEARN: Team Dynamics & Distributed-Work Practice

## 3.1 Brooks's Law, the communication half — with the arithmetic

Part 1 §1.5 introduced Brooks's Law informally. Here is the arithmetic that makes "why not just add a person" a computed answer instead of an assertion.

**The number of communication pairs in a team of *n* people is `n(n−1)/2`.** Every pair is a potential point of miscommunication, and — more concretely for a 9-day sprint — a potential synchronisation cost: information one pair has agreed on has to separately reach every other pair.

```
n = 3 (current team):  3×2/2 = 3 pairs
n = 4 (add one person): 4×3/2 = 6 pairs   → doubled, from one added person
n = 5:                  5×4/2 = 10 pairs
```

**Adding a fourth person on Day 9 does not add "25% more capacity" (1 person to 4) — it doubles the number of communication relationships that must independently stay in sync (3 pairs to 6), on top of the new person needing to be brought up to speed on five days of decisions they missed (Brooks's ramp-up cost, §1.5), which itself consumes time from the people who are already the bottleneck.** This is why "just get help" is close to never the right response to a mid-sprint slip for a team this size — the arithmetic actively works against it. It is also why the team should resist the instinct in the *other* direction under stress: don't invent ad hoc extra communication channels (a new group chat, a new shared document) without asking whether the existing three pairs already cover it — each new *channel*, not just each new person, has a coordination cost.

## 3.2 Tuckman's stages, mapped onto Day 4

Bruce Tuckman's 1965 model of small-group development names four (later five) stages: **forming** (polite, unclear roles), **storming** (real disagreement surfaces — about scope, about ownership, about approach), **norming** (the group settles into working agreements), **performing** (the group executes with minimal friction), and **adjourning** (wind-down).

**Where is this team on Day 4?** Plausibly at the forming/storming boundary — and that is not a warning sign. Three people who have spent three days on shared ideation (Chapters 1–3) but have not yet had to commit to who owns what, and who now must argue concretely about module boundaries (Part 1) and schedule risk (Part 2), are *supposed* to have some friction today. A team that reaches Day 4 with zero disagreement about ownership has probably not engaged with the decisions seriously enough yet.

**The useful, concrete move is this: "norming" is not a mood the team waits to arrive at. It is exactly three artifacts, each of which either exists by the end of today or doesn't:**

1. **The frozen schema requirements** (Part 4 §4.2–4.3) — settled today, implemented Day 5.
2. **An agreed sync cadence** (§3.3 below) — settled today, in writing.
3. **An agreed code-review norm** (§3.5 below) — settled today, in writing.

If all three exist by the end of Day 4, the team has *operationally* reached norming, whatever the mood in the room. If any is missing, the team is still storming — which is fine on Day 4 and a real risk if it's still true on Day 9.

## 3.3 Sync-cadence design — for three people, not thirty

The standard advice — "hold a daily standup" — is calibrated for teams where the coordination cost of *not* syncing daily exceeds the cost of the meeting. For three people, per §3.1's pair-count arithmetic, a fixed daily meeting is comparatively expensive: three people's daily meeting costs each person the same fifteen minutes a thirty-person team's would, for a fraction of the coordination benefit, because there are only three pairs to keep in sync in the first place, not 435.

**The design that fits this team's actual dependency structure (from §2.3's graph, not the calendar):**

- **A short daily async written check-in** — three lines each, posted once a day, no meeting required: *what shipped, what's blocked, what's next.* This is cheap (two minutes to write, thirty seconds to read each teammate's) and catches drift before it compounds.
- **Synchronous checkpoints pinned to the schedule's real dependency-graph events, not to the calendar** — a short call at each of: **Day 5** (schema freeze — everyone present, everyone signs off on the fixtures from §1.6), **Day 7** (Track A's Ch7 and Track B's Ch8 both due — cross-check assumptions before A3/B2 build on top of them), **Day 9** (A3 and B2 both due — the point §2.3 identified as fully critical; a missed sync here is the most expensive possible missed sync), **Day 12** (integration begins — everyone present for the whole day, not a check-in).

This is the direct, justified application of §3.1: fewer, well-placed synchronous moments beat a fixed daily meeting, because the checkpoints are chosen from the dependency graph (where a miscommunication is actually expensive) rather than from the clock (where it's merely routine).

## 3.4 Bus factor, and what R7 concretely requires

**Bus factor**: the minimum number of people who would need to become unavailable before the project stalls. A module with exactly one person who understands it has a bus factor of 1 for that module — the least resilient possible state.

**RAGNova's current bus factor, computed honestly:** each of the three tracks has exactly one owner and (so far) nothing else. **Bus factor = 1, per track.** This is not a criticism — a 3-person team genuinely cannot afford full redundancy on every module, that would defeat the purpose of splitting the work at all — but it means R7 ("team member unavailable... every module documented so another can continue") cannot be satisfied by "write some comments." It needs a specific, checkable artifact.

**The concrete requirement, satisfying R7 for real:** every module ships, by the time its owner considers it "done," with:

1. **A short module-level README** stating: what it does, in one paragraph; its inputs and outputs (referencing the shared schema); how to run it standalone (one command, with sample input); its known failure modes and rough edges.
2. **The contract test itself** (§1.6), which is executable documentation — it demonstrates, by running, exactly what the module is supposed to produce, in a way a written description can drift out of sync with but a passing test cannot.

**Neither of these is optional, and neither is "for later."** They are written *as the module is finished*, not retrofitted after a Day-9 absence makes them suddenly necessary — by then it is too late for the person who would have written them to still be the one writing them.

## 3.5 Code review norms for three people

With three people, no one can be a dedicated reviewer without starving their own track — a review policy copied from a larger team ("every PR needs two approvals") would silently stall the whole schedule. The right-sized norm:

> **A change is reviewed by whichever teammate is next available, and the review answers exactly one question: does this satisfy the interface contract (Part 4)? Not "is this the best possible implementation."**

This keeps review cost bounded and matches Part 1's information-hiding boundary precisely: a reviewer from a *different* track has no useful opinion on Track A's internal chunking algorithm (§1.3 says that's hidden and none of their business), but every right to check that what Track A *emits* still satisfies what they, as a consumer, depend on. This is also, not coincidentally, exactly what the contract test automates — the human review is a second check on the same boundary the test already enforces, not a separate, open-ended code-quality audit.

## 3.6 The 2-member fallback, worked out concretely

`ROADMAP.md` already states the fallback in one line: *"With 2 members: merge Track C into A and B (each owns half the UI)."* Here is the actual reassignment, plus what changes in the schedule.

**Reassignment:**

| | 3-member plan | 2-member fallback |
|---|---|---|
| Track A | Ch 6, 7, 10 | Ch 6, 7, 10, **+ chat interface core (half of Ch 11)** |
| Track B | Ch 8, 9 | Ch 8, 9, **+ upload/citation-rendering UI (half of Ch 11)** |
| Track C | Ch 11, 12 (owner) | **dissolved** — Ch 12 becomes a joint effort of A and B, same as it already was in the 3-member plan's all-hands convention |

**The informal CPM recomputation.** Each remaining member now has one more chapter's worth of work appended to their existing critical-path chain. Track A's chain becomes Ch6+Ch7+Ch10+half-Ch11 ≈ 1+1+2+1 = 5 days; Track B's becomes Ch8+Ch9+half-Ch11 ≈ 2+2+1 = 5 days — now genuinely symmetric and genuinely both critical, with **less** slack available than the 3-member plan had (which, per §2.3, already had none). **This is the finding worth stating plainly to the team: the 2-member fallback does not mean "the same plan, thinner." It means a measurably tighter schedule with even less room for the Day-9-absence scenario to be absorbed — which is exactly why §1.4 called this an Inverse Conway Maneuver rather than a minor tweak: the module boundaries genuinely have to be redrawn, not just relabeled.**

## 3.7 Worked example, resolved — Member 2 unavailable on Day 9

This ties Part 2 and Part 3 together, and it is the chapter's central worked scenario.

**The question:** Member 2 (Track B, owns Ch8–Ch9) is unavailable on Day 9.

**Step 1 — check the schedule (Part 2 §2.5, Layer 1).** Day 9 is B2's last scheduled day. A one-day absence slips B2's finish to Day 10, which cascades to C1 finishing Day 12 instead of Day 11 — which exactly consumes the one-day buffer identified in §2.4, without threatening Ch12's Day-12 start. **Verdict: absorbed by the schedule alone, provided this is the only slip.**

**Step 2 — check whether the absence exceeds the buffer.** Suppose instead it is three days, not one. The buffer (one day) is exhausted after day one of the absence; days two and three have nothing left to absorb them within the schedule as designed. At this point the question stops being "does the schedule survive" (no, not without help) and becomes "can someone else finish Ch9's remaining work."

**Step 3 — check the bus factor (§3.4).** Can Member 1 or Member 3 pick up Track B's remaining work? Only if Track B shipped a module README and a passing contract test for whatever was completed before the absence (§3.4's requirement) — in which case another member can read the README, run the contract test to confirm the current state, and continue from a known-good point without needing Member 2 to explain it. **If that documentation does not exist, the honest answer is that the team cannot safely proceed without Member 2, and must instead accept the schedule slip and consider which lower-priority scope (per Chapter 1 §2.4's out-of-scope list) gets cut to protect the Day-14 deadline.**

**This is the chapter's complete answer, delivered honestly rather than reassuringly: scheduling theory absorbs small slips automatically if a buffer was deliberately placed (§2.4); team-dynamics practice absorbs larger ones only if the documentation discipline in §3.4 was actually followed *in advance*; and beyond that, the only remaining lever is deliberately cutting scope, which is precisely why Chapter 1 wrote an out-of-scope list before this problem ever arose.**

---

# Part 4 — DECIDE: RAGNova's Module Boundaries & Interface Contract

## 4.1 Finalized module ownership table

Extending `ROADMAP.md`'s table with what each track **produces** (emits into the shared system) and **consumes** (depends on from elsewhere) — the concrete expression of Part 1's coupling analysis — and resolving the Days 8–9 scheduling question from Part 2 §2.3.

| Track | Owner | Chapters | Produces | Consumes |
|---|---|---|---|---|
| **A — Text + RAG core** | Member 1 | 6, 7, 10 (Days 6–9, corrected) | Text chunks in `text_index`; `answer_query(text) -> AnswerWithCitations` | The frozen schema (Day 5) |
| **B — Vision + audio** | Member 2 | 8, 9 (Days 6–9, corrected) | Image records in `image_index`; audio chunks in `text_index`; `ingest_image(file)`, `ingest_audio(file)` | The frozen schema (Day 5) |
| **C — Interface** | Member 3 | 11, 12 (Days 10–13) | The Streamlit app | `answer_query()` from A; `ingest_image()`/`ingest_audio()` from B |

**The Days 8–9 resolution.** Part 2's corrected schedule moves Ch10 to Days 8–9 (from the roadmap's original, dependency-unjustified Day 10–11). Track A works Days 6–9 continuously; there is no idle gap to reassign. If, in practice, Track A's Ch10 work finishes early within those two days, the recovered time is spent **validating the contract test against Track B's actual (not stubbed) output as soon as it's available (end of Day 7 for B1, end of Day 9 for B2)** — turning slack, if any exists in practice, into early integration risk-reduction rather than idle time.

## 4.2 Interface-contract requirements, per track's perspective

Before sketching a schema, state what each track actually *needs* from it — this is the requirements-gathering step a schema design should follow, not precede.

| Requirement | Needed by | Why |
|---|---|---|
| A stable, unique identifier per indexed segment | C (citations), A (dedup) | A citation must resolve back to exactly one segment |
| The source file path | C (citation "open original document") | Ch1 §1.8's citation-transparency requirement |
| Which modality produced it | A, C | Determines which collection it lives in (Ch1 §1.7.4) and how the UI renders its citation |
| Page number, for documents | C (citation "view page N") | |
| Start/end timestamp, for audio | C (citation "view transcript segment," seek-to-timestamp) | |
| The actual text content | A (retrieval, prompt construction), C (display) | |
| Which embedding model + dimension produced its vector | A, B (so retrieval code never accidentally compares incompatible vectors — Ch1 ADR-003) | |

## 4.3 Strawman schema — explicitly not final

A sketch only, to make §4.2's requirements concrete enough to discuss today. **Chapter 5 owns the real implementation, field types, and validation logic — this is the requirements handoff, not the deliverable.**

```python
# STRAWMAN — sketched Day 4, finalized in Chapter 5. Do not treat as final.
@dataclass
class Chunk:
    chunk_id: str          # unique, e.g. "notice_pdf__p2__c003"
    source: str             # file path
    modality: str            # "pdf" | "docx" | "image" | "audio"
    text: str               # the retrievable/displayable content
    page: int | None = None       # documents only
    start_s: float | None = None    # audio only
    end_s: float | None = None      # audio only
    embedding_model: str = ""      # which model produced this chunk's vector
```

This matches, and is not meant to replace, the `@dataclass` sketch already previewed in [Chapter 0 §A.6.16](ch00-getting-started-from-zero.md#a616-classes--enough-to-read-them-plus-the-one-we-write) — Chapter 5's job is to take this requirements sketch, validate it against §4.2's full table, and produce the actual `src/core/schemas.py` every track codes against, plus the real contract test from §1.6.

## 4.4 Contract-test specification, concretized

From §1.6's general pseudocode to the three specific fixtures RAGNova needs, owned as follows:

| Fixture | Owner | Must demonstrate |
|---|---|---|
| One real text chunk | Track A | `page` populated, `start_s`/`end_s` absent, round-trips through ChromaDB |
| One real image record | Track B | `modality="image"`, correct embedding dimension for the image collection |
| One real audio chunk | Track B | `start_s < end_s`, both populated, `page` absent |

All three checked into the repository by end of Day 5, run automatically thereafter.

## 4.5 Which decisions become ADRs today

Five architecture decisions, all made before any pipeline code exists — the same timing precedent as ADR-001 and ADR-003 from Day 3. Full write-ups in `docs/decisions/`; summarised here for the record:

| ADR | Decision | Why it belongs to Day 4 |
|---|---|---|
| **002** | Local quantized LLM (Ollama, Llama 3.2 3B) over a cloud API | Fixes the deployment target before Chapter 5's environment setup |
| **004** | ChromaDB over FAISS/Qdrant | Fixes the storage layer both Track A and Track B code against |
| **005** | Whisper transcription over native audio embeddings (CLAP) | Fixes what Track B's audio pipeline actually produces — directly shapes §4.2's schema requirements |
| **006** | Fixed-size overlapping chunks, size set by ablation | Fixes what Track A's chunker produces — directly shapes the `text` field's granularity |
| **007** | Rank-based cross-modal merging | Fixes how Track A's retrieval code combines Track A's and Track B's collections — the clearest possible example of a decision that must be settled *before* two tracks build against it independently |

---

# Part 5 — BUILD: the day

## 5.1 Templates prepared

| File | Purpose |
|---|---|
| [`reports/ppt2-slide-plan.md`](../../reports/ppt2-slide-plan.md) | Presentation #2, full slide-by-slide plan |
| [`docs/decisions/adr-002-local-llm-over-cloud.md`](../decisions/adr-002-local-llm-over-cloud.md) through [`adr-007-rank-based-merge.md`](../decisions/adr-007-rank-based-merge.md) | The five ADRs from §4.5 |
| [Chapter 4A](ch04a-scheduling-and-teamwork-sources.md) | The literature behind Parts 1–3 |

## 5.2 Schedule

| Time | Task | Who |
|---|---|---|
| 0:00–0:40 | Read Parts 1–3. Discuss the coupling/cohesion table (§1.2) and the module table (§4.1) as a team — this is where forming/storming (§3.2) should actually happen. | All |
| 0:40–1:20 | Work through the CPM calculation (§2.3) by hand, together, on paper or a whiteboard, before reading the chapter's version — verify your own numbers match. | All |
| 1:20–1:40 | Agree the sync cadence (§3.3) and code-review norm (§3.5) in writing. | All |
| 1:40–2:10 | Write the three contract-test fixtures (§4.4) — real sample data from each track, even if the pipelines don't exist yet (hand-construct one example chunk of each type). | Split by track |
| 2:10–3:30 | Write the five ADRs (§4.5), following `docs/decisions/adr-template.md` exactly. | Split, ~25 min each |
| 3:30–4:15 | Build PPT #2 from `reports/ppt2-slide-plan.md`. | All |
| 4:15–4:45 | Rehearse. | All |
| 4:45–5:15 | Run the §6.1 rubric and drill §6.2. | All |

## 5.3 The two things nobody may skip

**Resolving the R6/FILL sentence out loud, as a team (§2.4).** It is the one sentence most likely to be quoted back at you in a viva — everyone needs to be able to say it in their own words, not just read it off a slide.

**Writing the contract-test fixture stub (§4.4).** Ten minutes now, and it is the cheapest insurance the whole nine-day implementation phase has. A team that skips this because "the pipelines don't exist yet" has missed the point — the fixtures are hand-written sample data, not pipeline output; they exist specifically so the *shape* is agreed before any pipeline is built against it.

---

# Part 6 — CHECK

## 6.1 Rubric

Score 0–3 each. Below 38/54, revise.

| # | Criterion | Score |
|---|---|---|
| 1 | Module split justified via coupling/cohesion, not headcount | /3 |
| 2 | Information-hiding table (§1.3) states what each track may change unilaterally | /3 |
| 3 | Conway's Law correctly applied to both the 3-track split and the 2-member fallback | /3 |
| 4 | Contract test defined with a concrete fixture example | /3 |
| 5 | The Gantt-vs-dependency-graph limitation demonstrated on the real roadmap, not asserted abstractly | /3 |
| 6 | Critical path correctly identified with a full forward/backward pass shown | /3 |
| 7 | Float correctly computed and correctly interpreted (zero float everywhere, not "Track B has slack") | /3 |
| 8 | R6 explicitly tied to the buffer-insertion finding, with the resolved FILL sentence | /3 |
| 9 | Brooks's communication formula stated and applied to "why not add a 4th person" | /3 |
| 10 | Tuckman stage correctly identified with three concrete norming artifacts named | /3 |
| 11 | Sync cadence is concrete (frequency, format, and *why these specific checkpoints*), not "we'll communicate" | /3 |
| 12 | Bus factor defined and computed per track; R7 made concrete via the README + contract-test requirement | /3 |
| 13 | Code review norm defined and scoped to the interface contract | /3 |
| 14 | 2-member fallback worked out with explicit reassignment and a recomputed (informal) schedule | /3 |
| 15 | The Day-9 scenario resolved through both layers (buffer, then documentation), not asserted safe | /3 |
| 16 | Module ownership table includes produces/consumes columns | /3 |
| 17 | All 5 ADRs written, each with rejected alternatives | /3 |
| 18 | Strawman schema explicitly deferred to Chapter 5, not presented as final | /3 |
| | **Total** | **/54** |

## 6.2 Question bank

**On decomposition**
1. Why split by modality instead of by pipeline stage? → §1.2's coupling/cohesion table.
2. What does information hiding say a module owner may change without asking anyone? → §1.3's table; the shape emitted is not theirs to change unilaterally.
3. What exactly does a contract test check that a unit test doesn't? → shape/interface compatibility across module boundaries, not internal correctness.
4. What happens on Day 12 with no contract test? → §1.7's counterfactual — three independent undocumented guesses collide on the day with the least slack.
5. State Conway's Law. → org communication structure predicts software structure.
6. What is the Inverse Conway Maneuver, and where does this chapter use it? → design the team structure on purpose; the 2-member fallback (§3.6).

**On scheduling**
7. Draw the dependency graph from memory. → §2.3's table.
8. What does a Gantt chart hide that a dependency graph reveals? → the Day 10–11 vs. Day 11 overlap ambiguity in the original roadmap (§2.3's opening).
9. Which track is actually critical? → both — the schedule is fully critical, zero float on either chain.
10. Why is that a more useful (and more alarming) finding than "one track has slack"? → it means there is no natural room to absorb any slip.
11. Why integrate Day 12, not Day 13 — give the argument, not "for safety." → §2.4's buffer argument, quote the resolved sentence.
12. What is a Goldratt project buffer? → deliberately placed slack before a convergence point, sized to absorb accumulated variability.
13. Recompute the schedule if Ch7 slips one day. → the whole downstream chain shifts one day; since float is zero, this consumes the Day-12 buffer entirely on its own.

**On team dynamics**
14. State Brooks's Law and the pair-count formula. → §3.1; `n(n-1)/2`.
15. Why not add a 4th person if behind schedule? → doubles pairs (3→6) and imposes a ramp-up cost exactly when least affordable.
16. What Tuckman stage is the team in on Day 4, and what does reaching "norming" require? → forming/storming boundary; three concrete artifacts (§3.2).
17. Define bus factor and state RAGNova's number per track. → minimum people whose absence stalls the project; 1, per track.
18. What does R7 require beyond "add comments"? → a module README plus a passing contract test, per §3.4.
19. What is the code-review norm and why is it scoped that way? → reviews check contract compliance only, sized to a 3-person team's capacity (§3.5).

**On the interface contract**
20. Why is the schema the only thing tracks must agree on? → §1.3; everything else is hidden.
21. What's in the strawman sketch vs. deferred to Chapter 5? → field list and requirements here; types, validation, and the real implementation in Ch5.
22. "Isn't a shared schema just a fancy word for talking to each other?" → no — it's a *specific*, *enforced* (via the contract test) agreement that replaces open-ended talking with a pass/fail check.

**On honesty and limits**
23. What could still go wrong despite this plan? → any slip exceeding one day on the critical path, per §2.4's buffer size.
24. What's the honest answer to "what if Member 2 is unavailable for a week, not a day"? → the buffer is exhausted immediately; without prior documentation (§3.4), the team cannot safely proceed without them, and scope must be cut per Chapter 1 §2.4.
25. What would you do differently with 4 people instead of 3? → not simply "go faster" — apply §3.1's communication-cost argument in reverse and explain what a 4th track would need to hide (§1.3) to be worth its coordination cost.

## 6.3 Failure modes

| Failure | Why it costs | Fix |
|---|---|---|
| Module split chosen by headcount, not coupling | Constant cross-track merge conflicts | Redo with §1.2's table |
| Gantt bars read as the real schedule | The Day 10–11/Day 11 overlap goes unnoticed until it causes a real collision | Build the dependency graph (§2.3), not just bars |
| Schema "agreed" only verbally | Silent drift, Day-12 breakage | Contract test (§1.6, §4.4), checked in by Day 5 |
| "We'll just talk" as the sync plan | Drift undetected until integration | §3.3's checkpoint table, tied to real dependency events |
| Claiming "Track B has slack" | False comfort; the real schedule has none | §2.3's corrected float table — everything is critical |
| R6 justified as a platitude ("to be safe") | Doesn't survive a "why exactly Day 12" question | §2.4's buffer-sizing argument |
| Documentation deferred to "later" | R7 unmitigated in practice | Module README + fixture required at the point of shipping, not Day 12 |
| 2-member fallback treated as "the same plan, thinner" | Underestimates the tighter schedule it actually produces | §3.6's recomputation |
| "Add a person" as the Day-9 fix | Brooks's Law — ramp-up cost lands exactly when least affordable | §1.5, §3.1's arithmetic |

## 6.4 Day 4 completion checklist

- [ ] Coupling/cohesion table completed for the chosen module split
- [ ] Information-hiding table states what each track may change unilaterally
- [ ] Conway's Law applied to both the 3-track split and the 2-member fallback
- [ ] Dependency graph built from the roadmap's chapter table (not copied from the calendar)
- [ ] Full forward and backward CPM pass computed by hand and checked against §2.3
- [ ] Float correctly interpreted (zero everywhere) — not the "one track has slack" misreading
- [ ] R6/FILL sentence written, understood, and defensible by every member without notes
- [ ] Brooks's communication formula stated and applied to "why not add a 4th person"
- [ ] Tuckman stage named; three norming artifacts (schema requirements, sync cadence, review norm) all exist in writing
- [ ] Sync cadence written: async daily format + specific checkpoint days, with reasons
- [ ] Bus factor computed per track; module README + contract-test requirement stated
- [ ] 2-member fallback reassignment table completed
- [ ] Module ownership table finalized with produces/consumes columns
- [ ] Three contract-test fixtures written (hand-constructed sample data, one per modality)
- [ ] All 5 ADRs (002, 004, 005, 006, 007) written with rejected alternatives
- [ ] Strawman schema sketched and explicitly marked non-final
- [ ] PPT #2 built and rehearsed
- [ ] Rubric §6.1 scored ≥ 38/54

---

**Next:** [Chapter 5 — Environment Setup & Offline LLM](ch05-environment-setup-and-offline-llm.md) (Day 5) — where the strawman schema from §4.3 becomes the real, frozen `src/core/schemas.py` contract every track codes against, and where the contract test from §1.6/§4.4 gets its first real implementation.
