# Demo Corpus & Gold-Standard Evaluation Set

This folder holds the files RAGNova will index, plus the test questions we use to *measure* whether retrieval works.

**Fill this file in on Day 1, before writing any code.** Writing the test set before the system is deliberate: it stops us from unconsciously tuning the system to flatter itself. See Chapter 1 §3.3 and §1.10.

---

## Folder layout

```
data/
├── documents/   PDFs and DOCX files
├── images/      PNG / JPG — include screenshots and photos containing text
└── audio/       WAV / MP3 clips, 30 s to 3 min
```

Target: 10–15 PDFs, 5–8 DOCX, 10–15 images (3+ screenshots, 3+ photos with visible text), 3–5 audio clips.

## Deliberate cross-modal test material

Make sure the corpus contains, on purpose:

- [x] An image **and** a document about the same topic → proves image→document retrieval (`images/screenshot_wifi_setup.png` and `documents/it_onboarding.docx`).
- [x] An audio clip mentioning a topic that also appears in a PDF → proves audio→document retrieval (`audio/hod_project_announcement.wav` and `documents/notice.pdf`).
- [x] A screenshot whose content is described in a document → proves text→image retrieval with a visible payoff (`images/screenshot_synopsis_portal.png` and `documents/notice.pdf`).

## File inventory

> **Corpus status: Multimodal corpus populated.** The documents folder contains the Ch6 validated starter set (preserving contract and retrieval test invariants). `images/` contains 12 images (including screenshots of portals/WiFi dialogs, campus posters with visible OCR text, and architecture diagrams). `audio/` contains 4 spoken speech clips generated via Windows Speech Synthesis matching the campus academic guidelines.

| File | Modality | What it contains | Notes |
|---|---|---|---|
| `documents/notice.pdf` | pdf | 2-page dept notice — synopsis submission process, deadlines, mid-term evaluation weighting | Generated (Ch6). Exercises single & multi-chunk paths. |
| `documents/library_hours.pdf` | pdf | 1-page library policy — hours, borrowing limits, fines | Generated (Ch6). |
| `documents/it_onboarding.docx` | docx | 2-page IT onboarding guide, one explicit page break | Generated (Ch6) — exercises ADR-008's page-break detection. |
| `images/screenshot_portal_login.png` | image | SSO login screen with student email and password fields | Screenshot with OCR-readable authentication guidelines. |
| `images/screenshot_wifi_setup.png` | image | Wi-Fi settings dialog for `RAGNOVA-STUDENT` (WPA2-Enterprise) | Screenshot matching `it_onboarding.docx`. |
| `images/screenshot_error_403.png` | image | 403 Forbidden screen warning against unauthorized downloads | Screenshot matching Acceptable Use Policy in `it_onboarding.docx`. |
| `images/screenshot_synopsis_portal.png` | image | Synopsis portal upload screen with 21st August deadline | Screenshot matching `notice.pdf`. |
| `images/screenshot_vpn_client.png` | image | SecureConnect VPN client connected to remote library gateway | Screenshot for off-campus journal access. |
| `images/notice_seminar_poster.png` | image | Department seminar poster on Multimodal RAG (Auditorium Hall B) | Poster notice with date, venue, topics. |
| `images/notice_library_fines.png` | image | Central Library borrowing rules and overdue fine schedule | Noticeboard graphic (2 Rs/day, 200 Rs cap, 4 books/14 days). |
| `images/notice_lab_rules.png` | image | AIML lab rules and account sharing prohibition | Noticeboard graphic matching IT policy. |
| `images/notice_midterm_schedule.png` | image | Final year project evaluation timetable & marking breakdown | Noticeboard graphic (40% prototype, 35% report, 25% viva). |
| `images/diagram_rag_architecture.png` | image | Architectural block diagram of RAGNova pipeline | System diagram covering PyMuPDF, Whisper, OpenCLIP, ChromaDB. |
| `images/diagram_campus_map.png` | image | Schematic campus map showing Library, IT Centre, AIML Block | Blueprint diagram for cross-modal queries. |
| `images/photo_id_card_sample.png` | image | Sample Student ID Card with barcode and borrowing limits | Photo graphic for student identification. |
| `audio/hod_project_announcement.wav` | audio | Spoken briefing on project evaluation weighting & August 21 deadline | Speech audio matching `notice.pdf` (40% demo, 35% report, 25% viva). |
| `audio/library_orientation_excerpt.wav` | audio | Orientation speech on library hours, 4 books loan, overdue fines | Speech audio matching `library_hours.pdf`. |
| `audio/it_helpdesk_wifi_instructions.wav` | audio | Helpdesk voice guide on connecting to RAGNOVA-STUDENT network | Speech audio matching `it_onboarding.docx`. |
| `audio/lab_assistant_briefing.wav` | audio | Briefing on VPN installation for remote journals & no pirated media | Speech audio matching Acceptable Use Policy. |

---

## Gold-standard question set

The evaluation set from Chapter 1 §1.10. Start with 5 questions on Day 1; grow to **20 text questions + 10 cross-modal queries** by Chapter 7, when we first measure Recall@5 and MRR.

### Text → text/document queries

| # | Question | Expected source file | Expected page / timestamp | Why it's a good test |
|---|---|---|---|---|
| T1 | If I don't get my system actually running by evaluation day, how many marks am I giving up? | `documents/notice.pdf` | page 2 | Pure paraphrase — shares no words with "the working prototype... will carry forty percent." Answer: 40%. |
| T2 | As an undergrad, how many items can I check out from the library at once, and for how long? | `documents/library_hours.pdf` | page 1 | Paraphrase — shares no words with "borrow up to four books... fourteen days." Answer: 4 books, 14 days. |
| T3 | What happens the first time someone gets caught sharing their login with a friend? | `documents/it_onboarding.docx` | page 2 | Paraphrase — shares no words with "network access will be suspended for a period of two weeks." |
| T4 | What software must students set up if they want to read digital journals from home? | `documents/it_onboarding.docx` | page 1 | Paraphrase — refers to the institute virtual private network client (VPN). |
| T5 | Where will the guide allotment list be announced? | `documents/notice.pdf` | page 1 | Paraphrase — department noticeboard and student portal. |

> Include at least three questions whose wording shares **no keywords** with the source text (pure paraphrase). Those are the questions that prove semantic search beats Ctrl+F — and they are the ones to demo.

### Text → image queries (cross-modal)

| # | Query text | Expected image | Why it's a good test |
|---|---|---|---|
| I1 | Where can I see the Wi-Fi authentication screen for campus wireless? | `images/screenshot_wifi_setup.png` | Semantic text query retrieving the wireless configuration screenshot. |
| I2 | Find the diagram showing how ChromaDB and OpenCLIP connect together | `images/diagram_rag_architecture.png` | Conceptual query matching the system architecture diagram. |
| I3 | What poster shows the upcoming AI and Machine Learning seminar venue? | `images/notice_seminar_poster.png` | Text search retrieving the guest lecture seminar poster. |

### Image → document queries (cross-modal)

| # | Query image | Expected document(s) | Why it's a good test |
|---|---|---|---|
| M1 | `images/screenshot_synopsis_portal.png` | `documents/notice.pdf` | Screenshot of the portal links directly to the written notice guidelines. |
| M2 | `images/screenshot_wifi_setup.png` | `documents/it_onboarding.docx` | Wi-Fi dialog screenshot links to the onboarding guide explaining SSID and login steps. |

### Audio → anything queries

| # | Audio clip (or spoken query) | Expected result | Why it's a good test |
|---|---|---|---|
| A1 | `audio/hod_project_announcement.wav` | `documents/notice.pdf` / `images/notice_midterm_schedule.png` | Spoken announcement retrieves the written evaluation weighting guidelines. |
| A2 | `audio/library_orientation_excerpt.wav` | `documents/library_hours.pdf` / `images/notice_library_fines.png` | Spoken orientation retrieves the library hours and fine policies. |

### Negative controls (should return "not found in the provided sources")

Questions the corpus genuinely cannot answer. These test whether the system **refuses to hallucinate** — objective O4.

| # | Question | Expected behaviour |
|---|---|---|
| N1 | What is the hostel mess menu for Wednesday lunch? | Refuses / states the sources don't cover it |
| N2 | How do I apply for a refund on tuition fees? | Refuses / states the sources don't cover it |

---

## Results log

Fill in as each chapter's evaluation runs. Numbers, not adjectives (Chapter 1 §1.10 rule).

| Date | Chapter | Recall@5 | MRR | Cross-modal Recall@5 | Notes / what changed |
|---|---|---|---|---|---|
| 2026-09-15 | Ch7 | 1.00 | 1.00 | N/A (no images/audio yet) | First real semantic search, 3 text queries (T1–T3) against the 6-chunk Ch6 starter corpus. All 3 hit at rank 1. Read alongside Ch7 §3.3: with only 3 questions, one miss would swing Recall@5 to 0.67 — promising, not yet strong evidence. Grow the gold set (T4 onward) before trusting this number in a report. |

---

## Licensing / privacy note

Use only files you own or that are freely shareable. Do not commit anything confidential — this folder may end up in the submitted report or a public repository.
