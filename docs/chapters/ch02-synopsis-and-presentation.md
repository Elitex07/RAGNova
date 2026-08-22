# Chapter 2 — Synopsis & Presentation (Day 2)

> **Deliverables today:** a 2–3 page written **synopsis** and a **10–12 slide presentation** delivered to your guide or review panel.
>
> **Prerequisite:** [Chapter 1](ch01-objective-and-problem-identification.md) must be finished — specifically §2.1 (problem), §2.3 (objectives) and §2.4 (scope), because today is mostly *compressing* that material, not inventing new material. If Chapter 1 Part 2 is still blank, go back; you cannot write a synopsis from nothing.
>
> **Nothing gets built today.** That feels wrong when there are only fourteen days. It isn't. Today's document is the contract that stops you from building the wrong thing for nine of them.

---

## How to read this chapter

| Part | What it does | Time |
|---|---|---|
| **Part 1 — LEARN** | What a synopsis is as a genre, who reads it and what they silently check, section-by-section anatomy, academic writing mechanics, and why slides obey completely different rules from documents. | ~60 min |
| **Part 2 — DECIDE** | The judgement calls: the title, how much to promise, which single diagram, what to hold back for Chapter 3. | ~30 min |
| **Part 3 — BUILD** | A time-boxed production plan with the team split, plus two ready-to-edit templates. | ~4 hours |
| **Part 4 — CHECK** | Self-assessment rubric, twenty anticipated questions with answers, and the failure modes that cost marks. | ~45 min |

**Learning outcomes.** You will be able to explain what a synopsis is *for*; write each of its sections to a word budget; apply the tense, voice and hedging conventions of technical writing; write an abstract using a repeatable five-move formula; format IEEE references; design slides that support a spoken argument rather than duplicating it; and answer the questions a panel will actually ask.

---

# Part 1 — LEARN

## 1.1 What a synopsis is, as a genre

A synopsis is **a proposal, not a report.** That one distinction prevents most of the mistakes students make.

A report says *"here is what we did."* A synopsis says *"here is what we intend to do, here is why it is worth doing, and here is the evidence that we can actually do it in the time available."* It is written about work that has not happened yet, and it is judged on **plausibility**, not on results.

It has a second function that matters enormously to you: **it is a contract.** Once approved, it defines what you are obliged to deliver on Day 14 — and, just as importantly, what you are *not* obliged to deliver. A synopsis that mentions video ingestion commits you to video ingestion. A synopsis that explicitly scopes video out protects you from being asked about it. Chapter 1 §2.4 exists precisely so that today's document can be honestly bounded.

Three consequences, which you should feel while writing:

1. **Under-promise deliberately.** Every sentence is a commitment you must defend under questioning. *"The system will support cross-modal retrieval across four formats"* is a promise you can keep. *"The system will achieve state-of-the-art accuracy"* is not.
2. **Specificity is safety.** Vague claims invite the panel to supply their own interpretation, and their interpretation will always be more ambitious than yours. Numbers, named formats and named metrics close that gap.
3. **Feasibility is the hidden criterion.** More synopses are rejected for being unachievable in the time available than for being uninteresting.

## 1.2 Who reads it, and what they are silently checking

Your guide and the panel have read dozens of these. They are not reading for pleasure; they are running a checklist, largely unconsciously. Knowing the checklist lets you write straight to it.

| What they check | What satisfies them | What fails |
|---|---|---|
| **Is the problem real?** | A concrete scenario a human actually faces | "AI is an emerging field" — a topic, not a problem |
| **Is it clearly bounded?** | Explicit in-scope and out-of-scope statements | Open-ended ambition with no edges |
| **Is it feasible in 14 days by 3 beginners?** | Named off-the-shelf tools, no training, no GPU requirement | "We will train a custom multimodal model" |
| **Is there enough technical substance?** | Several non-trivial components with real design decisions | A thin wrapper around one API call |
| **Can they show it works?** | Named metrics with target numbers, and a test corpus | "The system will work well" |
| **Is the work divisible?** | Clean module boundaries with named owners | One person's project with two spectators |
| **Do they understand what they wrote?** | Correct, confident use of terminology | Buzzwords in the wrong places — instantly visible |

That final row deserves emphasis. A panel's fastest test of understanding is to pick one technical word from your synopsis and ask you to define it.

> **Rule for today: do not put a word in your synopsis that any team member cannot define.** If "contrastive pretraining" appears in the document, all three of you must be able to explain it. Chapter 1 gave you those definitions — today's job is to use only the ones you actually own.

## 1.3 Anatomy of a synopsis, section by section

Standard structure for a B.Tech project synopsis. **Total 1,000–1,500 words across 2–3 pages.** The word budgets are guidance, but the *proportions* matter: a synopsis with a 400-word introduction and a 100-word methodology tells the panel you have thought about context and not about engineering.

### Section 1 — Title (10–20 words)
Covered in Part 2.1, because it deserves a real decision process.

### Section 2 — Abstract (150–200 words)
A miniature of the entire document. Written **last**. Formula in §1.5.

### Section 3 — Introduction / Background (150–200 words)
Establishes the context a reader needs before the problem makes sense. Move from general to specific in three or four sentences: broad context → the specific setting → why it matters now → what remains unsolved.

Common failure: writing a history of artificial intelligence. Nobody needs it. Reach your specific problem within four sentences.

### Section 4 — Problem Statement (100–150 words)
The single most important paragraph in the document. Compress Chapter 1 §2.1. It must name a **specific deficiency**, not a general area of interest.

> Weak: *"Searching through documents is difficult."*
>
> Strong: *"Existing retrieval tools are lexical, siloed by modality, and cloud-dependent; consequently a user holding the answer inside their own files often cannot retrieve it, and cannot retrieve it at all when the content is an image or a recording."*

The strong version names three specific defects and one concrete consequence. That is what a problem statement is.

### Section 5 — Objectives (100–150 words)
A numbered list from Chapter 1 §2.3, compressed to one line each. Every objective must be **verifiable** — a reader should be able to point at the finished system and say yes or no.

Use verbs describing testable outcomes: *design, implement, integrate, evaluate, demonstrate, achieve.* Avoid verbs describing intentions: *explore, study, look into, try to, understand.* "We will explore multimodal retrieval" cannot be marked. "We will implement text-to-image retrieval and evaluate it at Recall@5 ≥ 0.70" can.

Five to seven objectives is right. Fewer looks thin; more looks unfocused.

### Section 6 — Literature Review (150–200 words)
Chapter 3 does this properly tomorrow. Today you need a compressed version: three to five sentences establishing that you know the foundational work, ending with **the gap your project fills.**

The structure that always works:

> *"X established A [1]. Y extended this to B [2]. However, existing systems do C, leaving D unaddressed. This project addresses D."*

That final move — naming the gap — converts a list of citations into an argument. Without it you have a reading list, not a literature review.

### Section 7 — Proposed Methodology / System Architecture (250–350 words)
The largest section, and the one that proves you can actually build this. **Put the architecture diagram here** — it does more work than any paragraph.

Cover, in order: the ingestion pipeline for each modality; how content becomes searchable (embeddings and the vector store); how retrieval works, including the cross-modal mechanism; how the answer is generated and cited. Chapter 1 §1.3.1's pipeline diagram, simplified, is exactly the right figure.

Be concrete. *"The system uses machine learning to understand documents"* says nothing. *"Documents are parsed with PyMuPDF, split into ~300-word overlapping chunks, embedded with a 384-dimensional sentence-transformer model, and stored in ChromaDB with provenance metadata"* says you have a plan.

### Section 8 — Tools & Technologies (75–100 words)
A compact table grouped by layer, **with the offline justification stated**. It is a differentiator, and the panel will notice its absence. Chapter 1's stack table compresses well here.

### Section 9 — Expected Outcomes (100–150 words)
What exists on Day 14 and how you will demonstrate it. **Include your evaluation metrics with target numbers** (Chapter 1 §1.10). This section separates a serious proposal from an optimistic one, because it commits you to being measured.

### Section 10 — Timeline (50–75 words plus a figure)
A compact table across the fourteen days with module ownership. Proves the work is divisible and sequenced.

### Section 11 — References (5–10 entries)
IEEE format. See §1.6.

## 1.4 Academic writing mechanics

Conventions signal competence before anyone reads your content, and breaking them is noticed immediately even by readers who could not articulate the rule.

### Tense

| Context | Tense | Example |
|---|---|---|
| Established facts | Present | "Embeddings *represent* semantic similarity as geometric proximity." |
| Prior work | Past | "Lewis et al. *introduced* retrieval-augmented generation [1]." |
| Your proposed work | Future **or** present | "The system *will ingest* four formats." / "The proposed system *ingests* four formats." |
| Your results (Day 14 report) | Past | "The system *achieved* Recall@5 of 0.84." |

Pick future *or* present for proposed work and hold it throughout. Mixing them mid-document is the most common tense error.

### Person and voice

Avoid first person singular entirely. First person plural is increasingly accepted, but the safer register for a B.Tech synopsis is impersonal:

- ✅ "The proposed system integrates four ingestion pipelines."
- ✅ "This work addresses the gap between..."
- ⚠️ "We integrate four ingestion pipelines." — accepted in many departments; ask your guide
- ❌ "I think our system will be really good at..."

On passive voice: the usual advice is "avoid the passive," and as stated it is wrong. Passive is correct when the *action* matters more than the actor — *"Documents are chunked into overlapping segments"* is better than *"We chunk documents,"* because who does the chunking is irrelevant. Use passive for process description and active when a subject genuinely matters. The real rule: never let passive voice hide **who is responsible** or **what actually happens**.

### Hedging versus overclaiming

Both extremes lose marks. Overclaiming gets attacked in the viva; over-hedging reads as a lack of confidence.

- ❌ Overclaim: "The system will completely eliminate hallucination."
- ❌ Over-hedge: "The system might possibly perhaps improve retrieval somewhat, if it works."
- ✅ Calibrated: "Constraining generation to retrieved context substantially reduces unsupported claims; displaying citations alongside answers allows residual errors to be identified by the user."

The calibrated version claims something real, bounds it honestly, and states the mitigation. It is directly defensible because it matches what Chapter 1 §1.8 says the system actually does.

### Precision

Replace every vague quantifier with a number or a name.

| Vague | Precise |
|---|---|
| "various file formats" | "PDF, DOCX, PNG/JPG, and WAV/MP3" |
| "a large number of documents" | "a corpus of 50–200 files" |
| "high accuracy" | "Recall@5 ≥ 0.80" |
| "a lightweight model" | "a 3-billion-parameter model quantized to 4 bits (~2 GB)" |
| "state-of-the-art techniques" | *(delete — it never survives questioning)* |

### Sentence and paragraph discipline

One idea per sentence; one topic per paragraph, announced in its first sentence. Aim for 15–25 words per sentence — anything past 40 contains two sentences. Define every acronym at first use ("Retrieval-Augmented Generation (RAG)") and use the short form thereafter.

## 1.5 The abstract: five moves, written last

The abstract is the hardest 180 words in the document because it must stand alone. Many panel members read only the abstract before your presentation, so it disproportionately shapes their first impression.

It is not a summary of your document's *structure* ("This synopsis discusses..."). It is a compressed version of your document's *argument*:

| Move | Purpose | RAGNova example |
|---|---|---|
| **1. Context** | Orient the reader | "Personal and organisational knowledge is distributed across documents, images, and voice recordings." |
| **2. Problem** | The specific gap | "Existing tools are keyword-based, modality-siloed, and cloud-dependent, making unified retrieval impossible offline." |
| **3. Approach** | What you will build, concretely | "This work proposes RAGNova, an offline multimodal RAG system indexing four formats into a unified vector store using sentence-transformer and CLIP embeddings, with Whisper transcription for speech." |
| **4. Outcome** | What it will do, measurably | "The system answers natural-language queries with numbered citations, supporting text-to-image, image-to-text and audio-to-text retrieval, evaluated by Recall@5 and human faithfulness ratings." |
| **5. Significance** | Why it matters | "All components execute locally, enabling semantic search over confidential corpora without network access." |

Write the other nine sections first, then assemble the abstract largely from their opening sentences. Far easier than writing it cold, and it guarantees the abstract matches the document.

**Never** put a citation, a figure reference, or an undefined acronym in an abstract.

## 1.6 References, and why they are not decoration

References do three jobs: they show you did not invent your approach in a vacuum, they let a reader verify your claims, and they demonstrate you can read primary sources rather than blog posts.

**IEEE format** is the norm in engineering. Numbered in order of first appearance, cited in text as `[1]`, listed in that same order.

```
[1] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive
    NLP Tasks," in Proc. Advances in Neural Information Processing Systems
    (NeurIPS), 2020.
```

Pattern: `Author initials and surname, "Title in quotes," in Proceedings/Journal, vol., no., pp., year.`

Rules that matter:
- **Cite what you actually read.** A panel may ask what a paper says. Read at least the abstract and conclusion of everything you cite.
- **Prefer primary sources.** Cite the CLIP paper, not a Medium article summarising it.
- **Documentation is citable** for tools (Ollama, ChromaDB) — cite the official docs with an access date, not a tutorial.
- **Five to ten references** is right for a synopsis. Chapter 3 expands this to fifteen or twenty.

A starter reference list appropriate to this project is provided in [`reports/synopsis-draft.md`](../../reports/synopsis-draft.md). **Verify every entry against the actual paper before submitting** — venues and years must be exact, and an incorrect citation is worse than a missing one.

## 1.7 The presentation is a different genre — this is the section people skip

Here is the single most common failure in student presentations: **treating slides as a document to be displayed.**

They are not. A document and a talk have different mechanics:

| | Document | Presentation |
|---|---|---|
| Reader/listener controls pace | Yes — they can re-read | No — you control it |
| Information channel | Text only | Your voice **plus** visuals |
| Density tolerated | High | Very low |
| Failure mode | Too vague | Too dense |

The mechanism behind that last row is worth understanding, because it explains every slide-design rule that follows. **People cannot read and listen at the same time.** Reading and listening compete for the same verbal processing channel. Put a paragraph on screen and your audience will read it — badly — while not hearing a word you say. You have then delivered your content twice, poorly, instead of once, well.

The correct division of labour:

> **The slide carries the claim and the evidence. Your voice carries the explanation.**

This is sometimes called the *assertion–evidence* structure, and it is the most useful slide-design idea you will meet:

- The **headline** is a full sentence stating the point of the slide — not a topic label.
- The **body** is a visual supporting that assertion — diagram, table, screenshot, or three short bullets.
- Everything else you say aloud.

Compare:

| Weak (topic label + prose) | Strong (assertion + evidence) |
|---|---|
| **Title:** "Methodology" <br> Six bullets of full sentences | **Title:** "Four ingestion pipelines converge on one vector store" <br> The architecture diagram, no bullets |
| **Title:** "Results" <br> A paragraph describing numbers | **Title:** "Retrieval reaches Recall@5 of 0.84, above our 0.80 target" <br> A three-row table |

The strong version means that even a distracted panel member who reads only your headlines follows your entire argument.

## 1.8 Slide design rules

These are conventions, not aesthetics. Each one exists for the cognitive reason given.

| Rule | Why |
|---|---|
| **One idea per slide** | If a slide needs "and" in its headline, it is two slides |
| **Maximum ~6 lines of text; ~6 words per line** | Beyond that, the audience reads instead of listening |
| **Never paste paragraphs** | Guaranteed to lose the room |
| **Body text ≥ 24 pt, titles ≥ 32 pt** | Anything smaller is unreadable from the back row |
| **High contrast: dark on light, or light on dark** | Projectors wash out mid-tones badly |
| **Sans-serif font** (Calibri, Arial, Helvetica) | Cleaner at projector resolution |
| **One diagram beats one paragraph** | Visual and verbal channels are separate, so a diagram plus narration uses both |
| **Number every slide** | So the panel can say "go back to slide 7" |
| **No animations, transitions or clip-art** | They consume time and attention and signal padding |
| **Screenshots over descriptions** | Evidence beats claims — even a mockup of the UI helps on Day 2 |

**Timing arithmetic.** Roughly **one minute per slide** for technical content. A 10-minute slot means 10–12 slides, no more. If you have 20 slides for a 10-minute slot, you will either rush all of them or be cut off at slide 12 having never reached your results. Cut before you present, not during.

**A fully written speaker-note per slide** is worth the effort even though you will not read it aloud. Writing it forces you to discover whether you actually know what the slide means.

## 1.9 Delivering as a team of three

**Split by section, not by sentence.** Each member owns a contiguous block of slides and speaks for a continuous stretch. Handing the clicker back and forth every two slides looks disorganised and wastes time.

A workable split for a 10-minute slot:

| Member | Slides | Content | Time |
|---|---|---|---|
| 1 | 1–4 | Title, problem, objectives, related work | ~3.5 min |
| 2 | 5–8 | Architecture, methodology, cross-modal mechanism, tools | ~4 min |
| 3 | 9–12 | Expected outcomes, evaluation, timeline and team split, conclusion | ~2.5 min |

**Handover lines** matter more than you would expect. A rehearsed one-liner — *"...and Ananya will take you through the architecture"* — keeps the talk continuous. Silent shuffling reads as unpreparedness.

**During Q&A, all three answer.** A panel notices when only one person can speak to the work; it directly suggests the other two did not contribute. Agree in advance who fields which topic area, and agree that anyone may add to another's answer.

**Handling a question you cannot answer.** Do not bluff — panels detect it instantly and it costs far more than the admission would.

> ✅ *"We haven't tested that case yet. Our plan is to evaluate it in the integration phase on Day 12, and I'd expect the limitation to be X."*
>
> ❌ Inventing a confident answer, or freezing silently.

The good version demonstrates three things: you know the boundary of what you have verified, you have a plan, and you can reason about the likely outcome. That scores better than a wrong confident answer, every time.

---

# Part 2 — DECIDE

Four judgement calls. Make them as a team before writing.

## 2.1 The title

A good technical title is **specific, keyword-rich, and honest about scope.** It should let a reader who sees only the title know roughly what the system does.

Criteria: names the artefact; states the core technique; states the distinguishing constraint; contains the terms someone would search for; is not a question; contains no marketing adjectives ("revolutionary", "cutting-edge", "novel").

| Candidate | Verdict |
|---|---|
| "RAGNova: A Multimodal Search System" | Too vague — omits offline, omits RAG, omits citations |
| "An Offline Multimodal Retrieval-Augmented Generation System for Unified Semantic Search Across Documents, Images, and Speech" | ✅ Precise and complete, but long |
| **"RAGNova: An Offline Multimodal RAG System for Unified Semantic Retrieval Across Documents, Images, and Speech"** | ✅ **Recommended** — names the artefact, the technique, the constraint, and the modalities in 17 words |
| "AI-Powered Next-Generation Smart Document Search Using Deep Learning" | ❌ Buzzwords; says nothing specific; invites hostile questioning |

**Recommendation:** the third. Adjust if your department caps title length.

## 2.2 How much to promise

Return to Chapter 1 §2.4 and make a conscious decision about each boundary, because today you are signing up to it.

**State in-scope explicitly**, with numbers: four formats, three cross-modal directions, 50–200 files, single-user desktop, English.

**State out-of-scope explicitly too.** Students resist this — it feels like admitting weakness. It is the opposite: an examiner reading "video ingestion is excluded as it requires keyframe extraction and is deferred to future work" sees a team that understands the problem well enough to bound it. An examiner reading nothing about video may simply ask why your "multimodal" system ignores the most obvious modality.

> **The rule:** if a reasonable person would expect a feature and you are not building it, name it and give a one-clause reason. Silence is read as an oversight; a stated exclusion is read as judgement.

## 2.3 Which single diagram

You have room for one figure in the synopsis and perhaps two in the deck. Choose the **system architecture pipeline** — Chapter 1 §1.3.1, simplified to fit.

Why that one over the alternatives: it simultaneously shows all four input modalities being handled (proving "multimodal"), the convergence on a single vector store (proving "unified"), the retrieval-then-generate flow (proving you understand RAG), and the citation path (proving the transparency requirement). No other single figure carries that much of your argument.

If you have room for a second figure in the deck, make it the **cross-modal search illustration** — a text query on one side, a retrieved image on the other, with CLIP's shared vector space between them. That is the piece of the project a panel is most likely to find genuinely interesting, and the piece they are least likely to already understand.

## 2.4 What to hold back for Chapter 3

Tomorrow is the full literature review and methodology. **Do not spend it today.** Today's Section 6 needs three to five sentences and about five references. Producing fifteen references today does not earn extra marks now and leaves you with nothing new to present on Day 4.

Similarly, do not put detailed algorithm descriptions in the synopsis. "Chunks are embedded with a sentence-transformer model" is right for today. HNSW parameters, chunk-size ablations and modality-gap handling belong to Chapter 3 and the final report.

---

# Part 3 — BUILD: a time-boxed day

## 3.1 Two templates are already prepared for you

| File | What it is |
|---|---|
| [`reports/synopsis-draft.md`](../../reports/synopsis-draft.md) | The full synopsis, pre-drafted for RAGNova with every section written, plus `⟨FILL⟩` markers where team-specific details go. Edit, do not start from blank. |
| [`reports/ppt1-slide-plan.md`](../../reports/ppt1-slide-plan.md) | A 12-slide plan: headline, body content, and full speaker notes for each slide. |

> **Read this carefully.** The drafts are a *starting point you must rewrite in your own words*, not a document to submit as-is. Two reasons, one practical and one that actually matters. Practical: your department's format, margins and section names may differ. The one that matters: **you will be questioned on every sentence.** Text you did not write is text you cannot defend. Work through the draft line by line, change the phrasing to language you would naturally use, and delete anything you could not explain if interrupted.

## 3.2 Schedule

| Time | Task | Who |
|---|---|---|
| 0:00–0:30 | Read Part 1 of this chapter. Agree the title (§2.1) and the scope boundaries (§2.2). | All three |
| 0:30–2:00 | Draft the synopsis. Split it: Member 1 takes Sections 3–5 (introduction, problem, objectives); Member 2 takes Sections 7–8 (methodology, tools); Member 3 takes Sections 6, 9–11 (literature, outcomes, timeline, references). | Parallel |
| 2:00–2:30 | Merge. **One person does a single editing pass over the whole document** so the voice is consistent — three writing styles in three pages is obvious and looks careless. | One editor |
| 2:30–2:50 | Write the abstract now that the document exists (§1.5). | The editor |
| 2:50–3:00 | Build the architecture diagram. | Member 2 |
| 3:00–4:00 | Build the deck from the slide plan. | Member 3 leads, all contribute |
| 4:00–4:45 | **Rehearse twice, timed, out loud, standing.** | All three |
| 4:45–5:00 | Run the §4.1 rubric and the §4.2 question drill. Fix what fails. | All three |

## 3.3 Making the architecture diagram

Three routes, in ascending order of effort:

1. **draw.io / diagrams.net** (free, browser-based, no account) — boxes and arrows in twenty minutes. Export as PNG at high resolution.
2. **PowerPoint shapes** — perfectly acceptable, and it keeps the figure editable inside the deck.
3. **Hand-drawn, photographed** — acceptable only for internal review, never for the submitted document.

Keep it to the four input types, the processing row, the vector store, the retrieval-and-generation row, and the answer with citations. **Do not draw every library.** A diagram with thirty boxes communicates less than one with eight.

Label the arrows with what flows along them ("text chunks", "384-d vectors", "top-5 chunks"). Unlabelled arrows are the most common flaw in student architecture diagrams — they turn a data-flow diagram into decoration.

## 3.4 Rehearsal protocol — do not skip this

Two full run-throughs, **out loud, standing, timed**. Reading silently is not rehearsal; you will discover neither your pace nor the sentences you cannot actually say.

- **Run 1:** straight through, no stopping, even through mistakes. Record the total time.
- **Between runs:** if you are over the limit, cut *slides*, not speaking pace. Talking faster does not create time; it destroys comprehension.
- **Run 2:** with the handover lines (§1.9) and one person asking two questions at the end.

**Have a backup plan for the technology.** Bring the deck as **both** `.pptx` and `.pdf` on a pen drive, plus a copy in email or cloud storage. PDF is the safe format — fonts and layout cannot shift on someone else's machine. Assume the projector will not cooperate and that you may need to present from a different laptop.

---

# Part 4 — CHECK

## 4.1 Self-assessment rubric

Score honestly out of 3 (0 = absent, 1 = weak, 2 = adequate, 3 = strong). Below 24/33, revise before submitting.

| # | Criterion | Score |
|---|---|---|
| 1 | Title is specific, keyword-rich, and free of buzzwords | /3 |
| 2 | Abstract stands alone and contains all five moves (§1.5) | /3 |
| 3 | Problem statement names a specific deficiency and its consequence | /3 |
| 4 | Every objective is verifiable, with a metric where applicable | /3 |
| 5 | Literature review ends by naming the gap | /3 |
| 6 | Methodology is concrete — named tools, named data flow | /3 |
| 7 | Architecture diagram is present, labelled, and readable | /3 |
| 8 | Scope includes an explicit out-of-scope statement | /3 |
| 9 | Expected outcomes include numeric evaluation targets | /3 |
| 10 | References are IEEE-formatted, primary sources, all actually read | /3 |
| 11 | Every team member can define every technical term used | /3 |
| | **Total** | **/33** |

**Deck check:** 10–12 slides · every headline a full assertion · no slide over ~6 lines · body text ≥ 24 pt · slides numbered · timed under the limit with a minute spare · PDF backup exists.

## 4.2 Twenty questions a panel will ask

Drill these aloud as a team. Every member should be able to answer any of them — rotate who responds. Section references point to where the full answer lives.

**On the problem and scope**

1. *Why is this a problem worth solving? Who suffers from it today?* → Ch 1 §2.8 use cases; lead with the privacy-critical case.
2. *Isn't this just ChatGPT with file upload?* → Ch 1 §2.2 gap table. Theirs is cloud-based, session-limited, and has no persistent cross-modal index.
3. *Why offline? Isn't that a step backwards?* → Ch 1 §1.7: confidentiality, zero recurring cost, no connectivity dependence, data sovereignty.
4. *What are you NOT building?* → Ch 1 §2.4, with a one-clause reason for each exclusion.
5. *Is this achievable in fourteen days by three people?* → Ch 1 §2.6 constraints and the Chapter 4 module split; all components are pretrained and off-the-shelf.

**On the technique**

6. *What is RAG, in one sentence?* → Retrieve relevant passages from the user's own files, insert them into the prompt, and generate an answer constrained to them.
7. *Why not fine-tune the model on the documents instead?* → Ch 1 §1.3: needs GPUs, must be redone per file, teaches style more reliably than facts, and **produces no citations**.
8. *Why not just paste all the documents into the prompt?* → Ch 1 §1.3: finite context window, quadratic attention cost, and the lost-in-the-middle effect.
9. *What is an embedding?* → Ch 1 §1.5: a vector encoding meaning, such that similar meanings point in similar directions.
10. *Why cosine similarity rather than Euclidean distance?* → Ch 1 §1.5.3: cosine compares direction and ignores magnitude; identical rankings once vectors are normalised.
11. *How can a text query possibly retrieve an image?* → Ch 1 §1.7.2: CLIP trains image and text encoders jointly on 400M caption pairs so both land in one shared vector space.
12. *Why not use one embedding model for everything?* → Ch 1 §1.7.3–4: CLIP truncates text at 77 tokens so it cannot handle documents; hence two collections.
13. *Why transcribe audio instead of embedding it directly?* → Ch 1 §1.7.5: our audio is speech, so the content is linguistic; transcription also gives timestamps and human-readable evidence.
14. *How does a vector database search millions of vectors quickly?* → Ch 1 §1.6.2: HNSW, approximately O(log N).

**On rigour**

15. *How will you prove it works?* → Ch 1 §1.10: Recall@5, MRR, cross-modal Recall@5, plus human faithfulness ratings on a pre-built gold set.
16. *How do you prevent hallucination?* → Ch 1 §1.8: constrained prompt, low temperature, citation validation, and chunk text displayed beside each citation. **Reduced, not eliminated** — say so.
17. *What are the limitations of your approach?* → Approximate search may miss neighbours; embeddings are weak on rare exact strings; small models are weaker at synthesis; OCR fails on handwriting. Naming limitations reads as maturity, not weakness.
18. *What happens if the answer is not in the corpus?* → The system states that the sources do not contain it. This is a tested case — negative controls in `data/README.md`.

**On the team**

19. *Who is doing what?* → Chapter 4's module table; answer with specific names and modules.
20. *What is your biggest risk and what will you do about it?* → Ch 1 §2.7 risk register; R1 (downloads) and R6 (integration crunch) are the honest answers.

## 4.3 Failure modes that cost marks

| Failure | Why it costs | Fix |
|---|---|---|
| Slides read aloud verbatim | Audience reads faster than you speak; you become redundant | Slides carry claims; your voice carries explanation (§1.7) |
| Vague objectives ("explore", "study") | Cannot be marked or verified | Testable verbs plus metrics (§1.3 Section 5) |
| No out-of-scope statement | Panel assumes you will do everything, then finds gaps | State exclusions with reasons (§2.2) |
| Buzzwords the team cannot define | One question exposes it, and credibility does not recover | Only use terms all three of you own (§1.2) |
| Uncited claims about prior work | Reads as invention | Cite primary sources; read them (§1.6) |
| Timeline with no owners | Suggests the work is not really divided | Name the owner of each module (§1.3 Section 10) |
| 25 slides for a 10-minute slot | You get cut off before your results | One slide per minute; cut beforehand (§1.8) |
| Three different writing voices | Obvious in three pages; reads as careless | One editor does a full pass (§3.2) |
| Overclaiming ("eliminates hallucination") | Directly attacked in Q&A | Calibrated hedging (§1.4) |
| No presentation backup | Technology fails at exactly the wrong moment | PDF plus pptx, on a pen drive and in the cloud (§3.4) |

## 4.4 Day 2 completion checklist

- [ ] Title agreed and fixed
- [ ] Synopsis complete: all eleven sections, 1,000–1,500 words
- [ ] Every sentence rewritten in the team's own words — nothing left verbatim from the template
- [ ] Abstract written last, contains all five moves, no citations or undefined acronyms
- [ ] Architecture diagram made, arrows labelled, embedded in both synopsis and deck
- [ ] References in IEEE format, 5–10 entries, every one actually read and verified
- [ ] Deck built: 10–12 slides, assertion headlines, slide numbers
- [ ] Speaker notes written for every slide
- [ ] Rehearsed twice, out loud, standing, within the time limit
- [ ] All twenty questions in §4.2 drilled, with every member able to answer any of them
- [ ] Rubric §4.1 scored ≥ 24/33
- [ ] Deck exported as PDF; both formats on a pen drive and in cloud storage
- [ ] Synopsis submitted in the format your guide requires (Word or PDF — ask, do not assume)

---

**Next:** [Chapter 3 — Literature Review & Methodology](ch03-literature-review-and-methodology.md) (Day 3) — how to find, read, and synthesise papers efficiently, and how to write a methodology section that actually justifies your design decisions.
