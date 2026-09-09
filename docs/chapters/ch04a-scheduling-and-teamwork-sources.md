# Chapter 4A — Scheduling & Teamwork Sources

> **Companion to [Chapter 4](ch04-timeline-and-team-split.md).** The literature behind Parts 1–3: coupling and cohesion, information hiding, Conway's Law, Brooks's Law, critical-path scheduling, and Tuckman's stages. Smaller in scope than [Chapter 3A](ch03a-annotated-bibliography.md) — this material is older, more settled in some places and more contested in others, and the honesty required is different: some of these are classic, load-bearing citations, and at least one (Tuckman) needs an explicit caveat about how well it actually holds up.
>
> **⚠️ Verify every citation before use**, exactly as in Chapter 3A. This file is raw material to read and verify, not text to paste.

---

## Cluster 1 — Critical-path scheduling: CPM and PERT

| Source | What it established | What Chapter 4 takes from it |
|---|---|---|
| Kelley Jr. & Walker, "Critical-Path Planning and Scheduling," *Proceedings of the Eastern Joint Computer Conference*, 1959 | Developed the Critical Path Method at DuPont for plant construction and maintenance scheduling — the forward/backward-pass algorithm used in Chapter 4 §2.2–2.3 | The mechanism itself: earliest/latest start and finish, float as the difference |
| Malcolm, Roseboom, Clark & Fazar, "Application of a Technique for Research and Development Program Evaluation (PERT)," *Operations Research*, vol. 7, no. 5, 1959 | Developed PERT independently, for the U.S. Navy's Polaris missile program, adding probabilistic activity-duration estimates on top of the same underlying network model | Historical context: CPM (deterministic durations) and PERT (probabilistic durations) are siblings; Chapter 4 uses the deterministic CPM form since our activity durations are estimates, not distributions |
| Goldratt, *Critical Chain*, North River Press, 1997 | Introduced Critical Chain Project Management, arguing that padding every individual task wastes the padding (via Parkinson's Law and "student syndrome" procrastination) and proposing instead a single project buffer placed before the final deliverable | ⭐ **Direct source for Chapter 4 §2.4's buffer argument** — the justification for "integrate Day 12, not Day 13" |
| Herroelen & Leus, "On the Merits and Pitfalls of Critical Chain Scheduling," *Journal of Operations Management*, vol. 19, no. 5, 2001 | A critical academic assessment of Critical Chain Project Management, noting real benefits alongside overstated claims in Goldratt's original popular treatment | The honest counterweight to citing Goldratt uncritically — cite this alongside Goldratt to show the buffer concept is used with its limitations understood, not taken on faith |

**Note for the report:** Kelley & Walker and Malcolm et al. are the primary historical sources but are difficult to access outside specialised archives; a standard operations-research or project-management textbook treatment of CPM/PERT is an acceptable substitute citation if the originals are not obtainable — say so explicitly if you substitute one, per Chapter 3B's citation-integrity discipline.

---

## Cluster 2 — Conway's Law

| Source | What it established | What Chapter 4 takes from it |
|---|---|---|
| Conway, "How Do Committees Invent?," *Datamation*, vol. 14, no. 5, 1968 | The original statement: organisations that design systems produce designs that mirror their own communication structure | ⭐ The direct source for Chapter 4 §1.4 |
| MacCormack, Rusnak & Baldwin, "Exploring the Duality Between Product and Organizational Architectures: A Test of the Mirroring Hypothesis," *Research Policy*, vol. 41, no. 8, 2012 | A modern empirical test of Conway's Law ("the mirroring hypothesis") across real software products, finding measurable correlation between team structure and code modularity | Evidence that Conway's Law is not just an aphorism — it has been tested and holds up empirically, which is worth citing if a panel questions whether a 1968 magazine article is "real" evidence |
| Skelton & Pais, *Team Topologies*, IT Revolution Press, 2019 | A widely cited modern practitioner treatment of deliberately designing team structure to shape architecture — the "Inverse Conway Maneuver" by name | Source for the term used in Chapter 4 §1.4; a practitioner book rather than peer-reviewed research — cite it as such |

---

## Cluster 3 — Brooks's Law and the mythical man-month

| Source | What it established | What Chapter 4 takes from it |
|---|---|---|
| Brooks, *The Mythical Man-Month: Essays on Software Engineering*, Addison-Wesley, 1975 (anniversary ed. 1995) | "Adding manpower to a late software project makes it later," derived from the OS/360 project; also the source of the communication-overhead argument that pairs grow as `n(n-1)/2` | ⭐ The direct source for both Chapter 4 §1.5 and §3.1 |
| Abdel-Hamid & Madnick, "The Elusive Silver Lining: How We Fail to Learn from Software Development Failures," *Sloan Management Review*, vol. 24, no. 1, 1983 | A systems-dynamics simulation study reproducing and quantifying Brooks's Law's effects | Corroborating evidence beyond Brooks's own anecdotal account of OS/360 |
| Blackburn, Lapré & Van Wassenhove, "Brooks' Law Revisited: Improving Software Productivity by Managing Complexity," working paper, INSEAD, 2007 | A more recent quantitative re-examination, nuancing rather than overturning the original claim — the effect is real but its magnitude depends heavily on task interdependency | The honest caveat: Brooks's Law is not an absolute constant, it is strongest exactly where task coupling is high — which is itself an argument for Chapter 4 Part 1's coupling-reduction work making a late addition *less* costly than it would otherwise be |

---

## Cluster 4 — Tuckman's stages of group development (a genuinely contested model — say so)

| Source | What it established | What Chapter 4 takes from it |
|---|---|---|
| Tuckman, "Developmental Sequence in Small Groups," *Psychological Bulletin*, vol. 63, no. 6, 1965 | The original forming–storming–norming–performing model, synthesised from a review of existing small-group research | ⭐ The direct source for Chapter 4 §3.2 |
| Tuckman & Jensen, "Stages of Small-Group Development Revisited," *Group & Organization Studies*, vol. 2, no. 4, 1977 | Added the fifth stage, "adjourning," and revisited the original model against subsequent studies | Source for the five-stage version some references use |

**⚠️ The honest caveat, worth including in your own review (mirroring the chunking caveat in Chapter 3 §3.3.2):** Tuckman's model is extremely widely taught and used in management practice, but subsequent research has not uniformly confirmed that groups pass through these stages in a fixed linear sequence — some studies find stages recurring, skipped, or running in parallel rather than in order. The model is best treated as a **useful descriptive vocabulary for group behaviour**, not a validated predictive law in the way CPM's mathematics is provable or Brooks's communication-cost formula is simple arithmetic. Chapter 4 §3.2 uses it exactly this way — as a naming tool for "what norming concretely requires," not as a claim that the team will mechanically progress through fixed stages on a fixed schedule. Saying this plainly, rather than citing Tuckman as settled fact, is the same methodological honesty Chapter 3 required for the chunking literature.

---

## Cluster 5 — Small-team practice: coordination cost, contracts, and lightweight process

| Source | What it established | What Chapter 4 takes from it |
|---|---|---|
| Parnas, "On the Criteria to Be Used in Decomposing Systems into Modules," *Communications of the ACM*, vol. 15, no. 12, 1972 | Information hiding: decompose by which design decision is hidden, not by processing sequence — demonstrated on the KWIC-index example | ⭐ The direct source for Chapter 4 §1.3 |
| Constantine & Yourdon, *Structured Design: Fundamentals of a Discipline of Computer Program and Systems Design*, Yourdon Press, 1979 | Formalised the coupling and cohesion taxonomies used to evaluate a module decomposition | ⭐ The direct source for Chapter 4 §1.2's tables |
| Fowler, "Consumer-Driven Contracts: A Service Evolution Pattern," *martinfowler.com*, 2006 | Named and described the "contract test" pattern this project borrows from microservice engineering, where a consumer of a service defines the contract the provider must satisfy | ⭐ The direct source for Chapter 4 §1.6's contract-test design. A practitioner article, not peer-reviewed research — cite it as such, the way Chapter 3A cites library documentation |
| Sutherland & Schwaber, "The Scrum Guide," scrumguides.org, various editions | The standard reference for daily-standup and sprint-checkpoint practice this project deliberately deviates from at small team size | Cited to show the deviation (dependency-pinned checkpoints over fixed daily meetings, Ch4 §3.3) is a considered choice against the mainstream default, not an oversight of it |

---

## Using this bibliography

**Coverage check.** Chapter 4's report material should cite at least one source per cluster — Cluster 4 (Tuckman) specifically needs its caveat stated, not omitted, following the same honesty standard Chapter 3 established for the chunking literature.

**If asked in the viva "is Tuckman's model actually validated?"** — the honest answer, drawn directly from this file: *"It's a widely used descriptive framework, not a strictly validated predictive law — later research finds groups don't always move through the stages linearly. We use it as vocabulary for what 'the team is norming' concretely means, not as a claim about a fixed timeline."* That answer is stronger than either overclaiming the model's rigor or not knowing the caveat existed.

**Split for verification:**

| Member | Clusters |
|---|---|
| ⟨Member 1⟩ | 1 (CPM/PERT), 5 (small-team practice) |
| ⟨Member 2⟩ | 2 (Conway), 3 (Brooks) |
| ⟨Member 3⟩ | 4 (Tuckman) — including writing the caveat paragraph above into your own words |

---

**Back to:** [Chapter 4 — Timeline, Team & Modular Work Split](ch04-timeline-and-team-split.md) · **Next:** [Chapter 5 — Environment Setup & Offline LLM](ch05-environment-setup-and-offline-llm.md)
