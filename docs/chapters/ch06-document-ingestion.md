# Chapter 6 — Document Ingestion (PDF/DOCX) (Day 6)

> **Deliverables today:** real, working parsers for PDF and DOCX files (`src/pipelines/documents/pdf_parser.py`, `docx_parser.py`); the real fixed-size chunker that ADR-006 specified but never implemented (`chunker.py`); a shared text-cleanup module (`src/core/text_normalize.py`); an orchestrator that ties them together into real `Chunk` objects (`ingest.py`); a small synthetic starter corpus (`scripts/generate_sample_corpus.py` + three real files in `data/documents/`); a new test file that runs the real pipeline against those real files; and ADR-008, the one genuinely new design decision this chapter forces.
>
> **Prerequisites:** [Chapter 5](ch05-environment-setup-and-offline-llm.md) (the frozen `Chunk` schema and `Settings` config this chapter builds on top of, unchanged) and [Chapter 4](ch04-timeline-and-team-split.md) §4.2–§4.4 (the requirements and fixtures this chapter finally makes real).
>
> **Related ADRs:** [ADR-006](../decisions/adr-006-fixed-size-chunking.md) (chunk size and overlap — decided Day 4, implemented today), [ADR-008](../decisions/adr-008-docx-pagination-via-explicit-breaks.md) (DOCX pagination — a decision this chapter's own work forced).
>
> **The framing for today.** Chapter 5 froze an interface and proved it with fixtures nobody had actually produced from a real file. Today that changes: this is Track A's first pipeline, and every chunk it produces from here on is checked against the exact contract Chapter 5 built, not a simplified stand-in for it. As with Chapter 5, every code block, number, and terminal output below was actually run against the real files in this repository while this chapter was written — including a genuine design dead-end (§2.4's investigation of `w:lastRenderedPageBreak`, which looked like a fix and turned out not to be) worked through in full rather than glossed over.

---

## How to read this chapter

| Part | What it does | Time |
|---|---|---|
| **Part 1 — LEARN: How PDFs Actually Store Text** | What a PDF page "is" internally; PyMuPDF's extraction modes; reading-order heuristics and their limits; why a page can legitimately have no text at all. | ~40 min |
| **Part 2 — LEARN: How DOCX Actually Stores (or Doesn't Store) Pages** | The XML signals that exist, the one that looks like a solution but isn't, and why. | ~40 min |
| **Part 3 — LEARN: Chunking in Practice** | Turning ADR-006's numbers into real index arithmetic; a tail-merge problem discovered by actually implementing the formula; why a chunk must never cross a page. | ~40 min |
| **Part 4 — DECIDE** | Module layout, where shared code lives and why, the error-handling policy, ADR-008 in summary. | ~20 min |
| **Part 5 — BUILD** | Writing each file in order, generating the corpus, running the tests, inspecting a real chunk. | ~2 hours |
| **Part 6 — CHECK** | Rubric, question bank, troubleshooting, completion checklist. | ~30 min |

**Learning outcomes.** You will be able to: explain what PyMuPDF's `get_text()` actually reconstructs and why it can get multi-column layouts wrong; explain why a `.docx` file has no stored concept of a printed page, and what the two things it *does* store instead are; explain why `w:lastRenderedPageBreak` looks like a fix for that and isn't; hand-derive how many chunks a page of a given word count produces under this project's chunking rule, including the tail-merge case; explain why chunking must never cross a page boundary; read and extend `ingest_document()`; and explain, with a real example, why this chapter's tests run against generated files instead of hand-written fixtures.

---

# Part 1 — LEARN: How PDFs Actually Store Text

## 1.1 What a PDF page "is" internally

A PDF page is not a grid of characters — it is a **content stream**: a sequence of low-level drawing instructions (`Tj` to show a string of text at the current position, `Tm` to set a text matrix, and so on), each instruction placing glyphs at explicit `(x, y)` coordinates on the page. There is no structural "this is paragraph two" or even "this is a word" — a PDF renderer (or a text extractor like PyMuPDF) reconstructs words, lines, and reading order from the *geometry* of where glyphs land, not from any stored logical structure.

This single fact explains almost everything interesting — and every limitation — in this section. Extracting "the text of a PDF" is not reading a stored value; it is **inferring** one from a drawing program's output, and inference can be wrong when the layout is unusual enough.

## 1.2 PyMuPDF's `get_text()` modes

`page.get_text()` (used in `pdf_parser.py`) takes an optional mode argument controlling what it returns:

| Mode | Returns |
|---|---|
| `"text"` (default) | Plain string, lines joined by `\n`, reconstructed reading order |
| `"blocks"` | A list of `(x0, y0, x1, y1, text, block_no, block_type)` tuples — one per detected layout block, with position |
| `"words"` | A list of individual words, each with its own bounding box |
| `"dict"` | The full structured breakdown: blocks → lines → spans, each span carrying font, size, and color |

This project uses plain `"text"` mode — the simplest option, and the right default for a single-column corpus. The other modes exist for exactly the problem in §1.3 below, and are worth knowing about even though this chapter doesn't need them yet.

## 1.3 Reading order heuristics, and the multi-column gotcha

In `"text"` mode, PyMuPDF sorts the blocks it detects primarily top-to-bottom, then left-to-right, to approximate natural reading order. For a normal single-column document (a notice, a report, most of what this project's own corpus contains), this is exactly right. **For a genuinely multi-column layout** — two side-by-side columns of text, common in academic papers and newsletters — naive top-to-bottom sorting can interleave the columns: a line from the top of column 2 can sort *before* a line from the bottom of column 1, because it's physically higher on the page, even though a human reader would finish column 1 first.

This project's corpus does not currently contain multi-column PDFs, so this is a **documented, deliberately deferred** limitation rather than a built feature. If it becomes necessary later, PyMuPDF supports two named mitigations without changing libraries: `get_text("text", sort=True)` (a stricter sort), or bucketing `get_text("blocks")` by x-coordinate to detect and separate columns before reading them in order. Neither is implemented here — noted so a future contributor doesn't have to rediscover that the option exists.

## 1.4 The zero-extractable-text page

A page can legitimately produce `""` from `get_text()` — most commonly, a **scanned page**: an image of a document, with no text content stream at all, only a picture of text that happens to be human-readable. PyMuPDF has genuinely nothing to extract there; this is not a bug or a missing feature, it's an accurate report that the page contains no machine-readable text.

**Decision: `ingest_document()` warns to `stderr` and skips that page, and continues with the rest of the file.** Three reasons, all stated plainly rather than assumed:

1. **One bad page shouldn't cost the other nineteen.** A 20-page PDF with one scanned title page should still index its other 19 pages.
2. **There is currently no recovery path.** Chapter 8's Tesseract OCR is wired to the *image modality* (a standalone image file), not to a scanned page embedded inside a PDF — building that connection is real, deferrable future work, not something to fake here.
3. **It matches how this codebase already handles the "found a problem, but not a fatal one" case.** `validate_chunk()` (Chapter 5) reports every problem it finds rather than crashing on the first; `verify_setup.py` prints a clear failure and keeps checking the rest. A visible warning that doesn't abort the whole file fits that same house style.

A **corrupt or unreadable** file is different and is *not* caught — `fitz.open()`'s own exception is allowed to propagate unchanged. There is no sensible degraded behaviour for a file that cannot be opened at all, so failing loudly is the honest choice.

---

# Part 2 — LEARN: How DOCX Actually Stores (or Doesn't Store) Pages

## 2.1 DOCX has no stored page concept for reflowed text

A `.docx` file is a zip archive of XML files (`document.xml` holds the body text). Unlike a PDF, where each page is a distinct object in the file, a Word document's XML describes a **continuous flow** of paragraphs and runs — where one page ends and the next begins is computed by Word's layout engine **at render or print time**, from the active font, margins, page size, and even printer driver. None of that is stored in the file itself. Two documents with byte-for-byte identical text content can paginate differently on two different computers, depending on which fonts are installed.

This is a real, load-bearing fact for this project: the frozen `Chunk` schema (Chapter 5) requires an integer `page` for every document chunk. For PDF, PyMuPDF hands this to us for free. For DOCX, **there is nothing to hand over** — whatever "page" ends up meaning here has to be defined, not read off the file.

## 2.2 The two signals that actually exist

Although DOCX has no *rendered* page concept, its XML does store two things a human author can explicitly insert, both of which python-docx's object model can see:

1. **A manual page break** — what you get when a person presses Ctrl+Enter in Word, or when code calls `document.add_page_break()`. Structurally, this inserts a paragraph containing a run with `<w:br w:type="page"/>` — an explicit "start a new page here" instruction baked into the XML.
2. **"Page break before" on a paragraph** — a formatting property (`<w:pageBreakBefore/>`), commonly turned on for Heading styles, meaning "this paragraph always starts a fresh page, however the rest of the layout flows."

Both are genuinely stored, author-controlled facts, not computed ones — which is exactly why this chapter uses them and nothing else.

## 2.3 Dropping to lxml for the run-level break

python-docx's high-level API has no `run.has_page_break` property — a real gap this project has to work around, not oversight. Every python-docx object wraps an underlying XML element accessible via a private-looking but stable, documented pattern: `run._element`. `docx_parser.py`'s `_run_has_manual_page_break()` uses exactly this to search a run's own XML children for `<w:br w:type="page"/>`:

```python
from docx.oxml.ns import qn

def _run_has_manual_page_break(run) -> bool:
    return any(
        br.get(qn("w:type")) == "page"
        for br in run._element.findall(qn("w:br"))
    )
```

`qn()` ("qualified name") converts a short tag like `"w:br"` into the fully-qualified XML namespace name the underlying `lxml` element tree actually uses internally — a standard python-docx idiom for exactly this kind of low-level lookup. This is the one place this project depends on structure python-docx's own public API doesn't formally promise — which is precisely why `requirements.txt` pins `python-docx==1.1.2` exactly: an upgrade that changes this internal structure would silently break page detection, and the pin means that upgrade is a deliberate, tested decision, not something that happens accidentally under `pip install --upgrade`.

## 2.4 `w:lastRenderedPageBreak` — investigated, and rejected

Searching for "detect page breaks python-docx" quickly surfaces a third XML element: `<w:lastRenderedPageBreak/>`, which Word itself writes into a document at the exact position where the page broke **the last time the document was opened and rendered in Word**. This looks, at first glance, like precisely the fix for §2.1's problem — a real, stored rendered-page position.

**It was investigated for this chapter, and rejected, for two independent reasons — both worth understanding, not just the conclusion:**

1. **It would not even help our own corpus.** This marker is written only by Word's actual layout engine, during an actual render. Every file this chapter's `scripts/generate_sample_corpus.py` produces is built entirely with python-docx's own writer API — it never passes through Word at all, so `w:lastRenderedPageBreak` would simply never appear in it. A detection strategy that can't see its own project's generated files is not a strategy worth having.
2. **Even in a real Word-authored file, it isn't a stable property of the document — it's a cache of one specific save.** It reflects whatever fonts, margins, and printer driver were active on whichever machine last saved the file through Word. Re-open it on a different machine, or with a different default printer, and Word would compute different break positions on next save. Trusting it would make a citation's page number **not reproducible** — a document re-saved by a different team member could silently shift where every downstream page number points. That is a direct violation of this project's own reproducibility standard (Chapter 3 §3.8, restated in `requirements.txt`'s pinning rationale) — a standard this project has already chosen to take seriously enough to pin every dependency for.

Both of these reasons — not used, and why — are recorded permanently in [ADR-008](../decisions/adr-008-docx-pagination-via-explicit-breaks.md), specifically so a future contributor who has the same "wait, doesn't this field solve it?" idea (a very natural one to have) doesn't have to re-derive the answer from scratch.

## 2.5 Walking the algorithm through the real `it_onboarding.docx`

`extract_docx_pages()` walks every top-level paragraph once, tracking a running page counter:

```python
def extract_docx_pages(path):
    document = Document(Path(path))
    pages = [[]]
    page_num = 1
    for paragraph in document.paragraphs:
        if paragraph.paragraph_format.page_break_before:
            page_num += 1; pages.append([])
        if paragraph.text.strip():
            pages[page_num - 1].append(paragraph.text)
        if any(_run_has_manual_page_break(r) for r in paragraph.runs):
            page_num += 1; pages.append([])
    return [(i + 1, "\n".join(p)) for i, p in enumerate(pages)]
```

`it_onboarding.docx` (§5.4 builds this file for real) contains exactly one `document.add_page_break()` call between its two paragraph groups. Walking the loop by hand: every paragraph in the "email/Wi-Fi/VPN" group is appended while `page_num == 1`. The manual break lives in its **own, essentially textless paragraph** (this is how `add_page_break()` and a human's Ctrl+Enter both construct the underlying XML) — so the check for it happens *after* that (empty) paragraph contributes nothing, then increments `page_num` to 2 and opens a new page bucket. Every subsequent paragraph — the acceptable-use-policy group — lands in page 2. Running the real function against the real file confirms exactly this split (§5.7 shows the captured output).

## 2.6 Disclosed limitation

**Automatic reflow — Word wrapping a paragraph onto a new page purely because the previous one ran out of room, with no explicit break anywhere — is completely invisible to this approach.** A long, unbroken real-world document with no manual structure will report as far fewer pages than it actually prints as. This is not a bug to be quietly patched later; it's the direct, accepted cost of ADR-008's decision, and it must be stated plainly wherever DOCX citations are shown to a user (flagged for Chapter 11's UI). Also out of scope, and equally worth stating rather than silently omitting: `document.paragraphs` walks only top-level body paragraphs — text inside tables, headers, and footers is not extracted by this chapter's code at all.

> **Misconception check:** "So DOCX page numbers from this pipeline are just wrong?" No — they're **narrower than a PDF's**, not wrong: every page number this pipeline reports for a DOCX file corresponds to a real, author-inserted structural break. What's missing is coverage of the *other* way a page can end (automatic reflow), not correctness of what it does report.

---

# Part 3 — LEARN: Chunking in Practice — From Formula to Code

## 3.1 From ADR-006's numbers to real index arithmetic

ADR-006 (Day 4) decided *what*: fixed-size chunks, ~300 words, 50-word overlap, as tunable parameters rather than hardcoded literature values. It did not decide the exact index arithmetic — that's today's work, in `chunker.py`'s `chunk_page_text(text, size_words, overlap_words)`.

The core loop advances a window of `size_words` words at a time, but steps forward by only `size_words - overlap_words` words each iteration — the **step**, `250` at this project's default settings — which is what creates the overlap: each new window starts 250 words after the previous one started, but is still 300 words wide, so its first 50 words repeat the previous window's last 50.

## 3.2 Worked example — the real 380-word page

`notice.pdf`'s page 2 (generated in §5.4) is **exactly 380 words**, chosen deliberately, not by accident, to land past the tail-merge boundary derived below. Tracing `chunk_page_text(text, size_words=300, overlap_words=50)` by hand:

```
words = 380 total, step = 300 - 50 = 250

Iteration 1: start=0,   end=min(0+300, 380)=300   → first window, no previous chunk to compare
             ranges = [[0, 300]]
             end (300) != n (380), so continue: start += 250 → start=250

Iteration 2: start=250, end=min(250+300, 380)=380
             new words beyond the previous chunk's end: 380 - 300 = 80
             80 is NOT < overlap_words (50) → do not merge, append a new range
             ranges = [[0, 300], [250, 380]]
             end (380) == n (380) → stop

Result: 2 chunks, lengths 300 and 130
```

Running the real function against the real file confirms this exactly (verified first-hand while writing this chapter):

```
>>> from src.pipelines.documents.ingest import ingest_document
>>> chunks = [c for c in ingest_document("data/documents/notice.pdf") if c.page == 2]
>>> [len(c.text.split()) for c in chunks]
[300, 130]
```

## 3.3 The tail-chunk problem — discovered by implementing the formula, not assumed in advance

Implementing §3.1's formula literally, with no special case, on a **305-word** page produces something worth noticing: chunk one is `[0, 300]`; the next window would be `[250, 305]` — just **5 new words** sitting on top of **50 words already covered** by chunk one. That second "chunk" is almost pure redundancy: 91% of it duplicates content already indexed.

**Decision: if a window's new (non-overlapping) content would be smaller than `overlap_words`, fold it into the previous chunk instead of emitting it separately.** Traced against the real code:

```
n = 305: chunk one = [0, 300]. Next window: end = min(250+300, 305) = 305.
         new words = 305 - 300 = 5.  Is 5 < overlap_words (50)?  Yes → merge.
         ranges[-1][1] = 305  →  ranges = [[0, 305]]
Result: exactly 1 chunk, 305 words long — not 2.
```
Verified directly against the real function:
```
>>> from src.pipelines.documents.chunker import chunk_page_text
>>> text = " ".join(f"w{i}" for i in range(305))
>>> [len(c.split()) for c in chunk_page_text(text, 300, 50)]
[305]
```

This has a clean, exact boundary, also verified directly rather than assumed:

| Page words | Merge? | Result |
|---|---|---|
| 300 | (only one window ever forms) | 1 chunk, 300 words |
| 301 | new=1 word `< 50` → merge | 1 chunk, 301 words |
| 349 | new=49 words `< 50` → merge | 1 chunk, 349 words |
| **350** | new=50 words, **not** `< 50` → no merge | 2 chunks: 300, 100 |
| 351 | new=51 words → no merge | 2 chunks: 300, 101 |

**350 is the exact tipping point** — worth internalizing as "roughly `size_words + overlap_words`" (300 + 50), not as a magic number to memorize, since it falls directly out of the merge condition (`new_words < overlap_words`, where `new_words = n - size_words` for the second window) rather than being independently chosen.

A page **shorter** than `size_words` needs no special case at all: the very first iteration already has `end == n`, so the loop emits exactly one chunk and stops — there is no "page too short" branch anywhere in the code, because the general loop already degrades correctly.

## 3.4 Why chunking must never cross a page boundary

This is the reason `chunk_page_text()` is called **once per page**, never once across a whole multi-page document's concatenated text. `Chunk.page` (Chapter 5) is not decoration — Chapter 4 §4.2's requirements table ties it directly to a citation promise: "view page N." If chunking ran across the whole document as one continuous stream and a chunk's text happened to start on page 2 and end on page 3, no single, honest value of `page` could describe it — whichever page got picked, part of the citation would point somewhere the cited text doesn't actually appear. Extracting text per-page first, then chunking independently *within* each page, is what keeps that promise exactly true for every chunk this pipeline produces — verified concretely by `test_chunk_never_spans_a_page_boundary` in §5.7.

## 3.5 `chunk_id` assembly

Convention, from Chapter 4 §4.3: `"<file>__p<page>__c<seq>"`, e.g. `notice_pdf__p2__c003`. Two details, each backed by a reason rather than a stylistic preference:

- **`path.name.replace(".", "_")`, not `path.stem`.** `Path("report.pdf").stem` is `"report"` — dropping the extension entirely means `report.pdf` and `report.docx` would collide on the identical id prefix `report`. `.replace(".", "_")` keeps the extension as part of the id (`report_pdf` vs. `report_docx`), preserving it as a disambiguator.
- **Sequence numbers reset to `c001` at the start of every page.** The id already encodes the page (`p2`), so "third chunk of page 2" reading as `c003` is self-explanatory without cross-referencing how many chunks page 1 had. It also means page 2's ids are **stable** if page 1's text is edited later and its own chunk count changes — a continuous, whole-file counter would couple two pages that have nothing to do with each other.

---

# Part 4 — DECIDE

## 4.1 Module layout

```
src/
├── core/
│   ├── schemas.py          (unchanged — Chapter 5)
│   ├── config.py           (unchanged — Chapter 5)
│   └── text_normalize.py   ← NEW today: shared, not track-A-private
└── pipelines/
    └── documents/
        ├── pdf_parser.py    ← extract_pdf_pages()
        ├── docx_parser.py   ← extract_docx_pages()
        ├── chunker.py       ← chunk_page_text() — pure, no Chunk/settings import
        └── ingest.py        ← ingest_document() — the orchestrator
```

Organized by **modality** (`documents/`, and eventually `images/`, `audio/`), not by track label — matching the same Coupling/Cohesion argument Chapter 4 §1.2 used to justify splitting the whole project this way: a third document type later means adding one file here, not editing the two that already exist.

## 4.2 Where text normalization lives, and why

`normalize_text()` (whitespace collapse, control-character removal — the exact spec from `reports/methodology-draft.md` §3.1) lives in `src/core/`, not `src/pipelines/documents/`, even though this chapter is its first caller. Chapter 4 §1.3's own rule for what belongs in `core/`: shared, joint-owned code that more than one track's output shape depends on. Chapter 8's OCR text and Chapter 9's Whisper transcripts will both need the identical cleanup before they're chunked — putting it here once means three tracks call one tested function, instead of three tracks eventually writing three slightly different regexes that quietly disagree with each other.

## 4.3 The tail-merge threshold is a code constant, not a new `.env` setting

The `< overlap_words` merge condition (§3.3) is derived directly from `CHUNK_OVERLAP_WORDS` — it isn't an independent number that needs its own tuning knob. Adding a separate `.env` setting for it would let the two drift out of sync for no benefit; keeping the relationship as code (not configuration) is the simpler choice, and simpler is correct here since there's no scenario yet where a team member would legitimately want to change the merge rule without also changing the overlap it's derived from.

## 4.4 Error-handling policy

| Situation | Behaviour | Why |
|---|---|---|
| Unsupported file extension | `ValueError`, checked before touching the filesystem | Cheap, and a clearer message than whatever the parser library would raise on a file type it wasn't built for |
| File doesn't exist | `FileNotFoundError`, with the path included | Standard, unambiguous |
| Corrupt / unreadable file | The parser library's own exception, unchanged | No sensible degraded behaviour exists for a file that can't be opened |
| PDF page with zero extractable text | Warn to `stderr`, skip that page, continue | One bad page shouldn't cost the rest of the document (§1.4) |
| DOCX with zero explicit page breaks | Entire file reported as page 1 | Honestly incomplete, per ADR-008, rather than confidently wrong |

## 4.5 ADR-008, in summary

DOCX pages are tracked only from explicit, author-inserted signals (§2.2) — never from `w:lastRenderedPageBreak` (§2.4's two independent reasons), never estimated from a word-count heuristic, and never faked as "always page 1." Full reasoning, alternatives, and the "revisit if" condition: [ADR-008](../decisions/adr-008-docx-pagination-via-explicit-breaks.md).

---

# Part 5 — BUILD: the actual Day 6

> **A note on how today's outputs below were captured.** Chapter 5 was written before this machine had a working Python-3.11 venv with the project's exact pinned dependencies — its captured output honestly showed Ollama not yet running, rather than a faked clean pass. The same is true today: the outputs below come from actually running this chapter's real code (the same files now committed to this repository) against real generated files, using currently-available PyMuPDF/python-docx/pytest builds rather than the exact pins in `requirements.txt` (that pinned Python 3.11 venv still doesn't exist on this machine as of Chapter 6 — completing Chapter 5's §5.1–§5.4 on your own machine is still open). The logic, the numbers, and the pass/fail results are real and were not hand-typed to look right; re-run every command below yourself, inside your own pinned venv, and confirm you see the same shape of result.

## 5.1 Write `src/core/text_normalize.py`

Collapses whitespace to single spaces first, **then** strips remaining non-whitespace control characters — that order matters, because collapsing first turns a newline between two paragraphs into a space (so two paragraphs don't glue into one word), while a later, separate step removes genuine junk bytes (a stray NUL from a malformed extraction) without disturbing real word boundaries. See the file's own docstring for the full reasoning; the two-line contract:

```python
>>> normalize_text("Hello\n\n\tworld  again")
'Hello world again'
>>> normalize_text("Hello \x00world \x1fagain\x7f")
'Hello world again'
```

## 5.2 Write `src/pipelines/documents/pdf_parser.py`

`extract_pdf_pages()` — see Part 1. One line worth flagging before you type it: **`import fitz`**, not `import pymupdf` — the pip package name and the import name genuinely differ (§6.3 has this in the troubleshooting table too, because it catches people every time).

## 5.3 Write `src/pipelines/documents/docx_parser.py`

`extract_docx_pages()` and `_run_has_manual_page_break()` — see Part 2. Needs `from docx.oxml.ns import qn` for the low-level break lookup.

## 5.4 Write `src/pipelines/documents/chunker.py`

`chunk_page_text()` — see Part 3. Deliberately imports nothing from `src.core` — it's a pure function of `(text, size_words, overlap_words)`, independently testable and reusable.

## 5.5 Write `src/pipelines/documents/ingest.py`

`ingest_document()` — the orchestrator. Dispatches on file extension, calls the right parser, normalizes each page's text, chunks it, and assembles real `Chunk` objects with `embedding_model` set from `settings.TEXT_EMBEDDING_MODEL` (recording *intent* — Chapter 7 hasn't computed an actual vector yet, but the field is required and non-empty, so it's set now to the model that will eventually do that embedding).

## 5.6 Generate the sample corpus

```bash
python scripts/generate_sample_corpus.py
```

**Real captured output:**
```
wrote notice.pdf (2 page(s))
wrote library_hours.pdf (1 page(s))
wrote it_onboarding.docx (2 page(s), 1 explicit page break(s))

Done. Next: pytest tests/test_document_ingestion.py -v
```

The generator asserts non-negative spare space after laying out each PDF page (`page.insert_textbox()` returns negative spare space if text overflowed and got silently truncated) — this is a real, runnable self-check, not a decorative comment. Confirmed directly while writing this chapter, not just claimed: at 11pt on an A4 page with 1-inch margins, the real 380-word page 2 leaves `spare=135.5` points of untouched space — comfortably positive, so nothing was silently dropped — and the same check was re-run at 10.5pt and 10pt (`spare=189.9` and `214.1`) to confirm the assertion actually tracks shrinking headroom correctly, not just returning a constant. If you lengthen any page's text later, this is the check that will tell you honestly whether it still fits, rather than silently mailing you a corpus file quietly missing its last paragraph.

`data/documents/` now has three real files:

| File | Pages | Notes |
|---|---|---|
| `notice.pdf` | 2 | Page 2 is exactly 380 words on purpose — see §3.2 |
| `library_hours.pdf` | 1 | Single-chunk path — 304 words, comfortably under the 350-word merge boundary from §3.3 |
| `it_onboarding.docx` | 2 | One explicit `add_page_break()` — exercises ADR-008's detection directly |

## 5.7 Run `tests/test_document_ingestion.py`

```bash
pytest tests/test_document_ingestion.py -v
```

**Real captured output**, run against the actual files now in this repository:

```
============================= test session starts =============================
collecting ... collected 25 items

tests/test_document_ingestion.py::test_normalize_text_collapses_whitespace PASSED [  4%]
tests/test_document_ingestion.py::test_normalize_text_strips_control_characters PASSED [  8%]
tests/test_document_ingestion.py::test_normalize_text_handles_empty_and_whitespace_only_input PASSED [ 12%]
tests/test_document_ingestion.py::test_chunker_short_page_is_one_chunk PASSED [ 16%]
tests/test_document_ingestion.py::test_chunker_produces_overlapping_windows_for_a_long_page PASSED [ 20%]
tests/test_document_ingestion.py::test_chunker_merges_short_tail_into_previous_chunk PASSED [ 24%]
tests/test_document_ingestion.py::test_chunker_rejects_overlap_not_smaller_than_size PASSED [ 28%]
tests/test_document_ingestion.py::test_chunker_empty_text_produces_no_chunks PASSED [ 32%]
tests/test_document_ingestion.py::test_docx_parser_detects_run_level_page_break PASSED [ 36%]
tests/test_document_ingestion.py::test_docx_parser_detects_page_break_before_property PASSED [ 40%]
tests/test_document_ingestion.py::test_docx_parser_reports_single_page_when_no_breaks_exist PASSED [ 44%]
tests/test_document_ingestion.py::test_every_real_chunk_satisfies_the_contract PASSED [ 48%]
tests/test_document_ingestion.py::test_chunk_ids_are_unique_per_file PASSED [ 52%]
tests/test_document_ingestion.py::test_chunk_id_format_matches_convention PASSED [ 56%]
tests/test_document_ingestion.py::test_chunk_never_spans_a_page_boundary PASSED [ 60%]
tests/test_document_ingestion.py::test_notice_page_two_produces_two_overlapping_chunks PASSED [ 64%]
tests/test_document_ingestion.py::test_notice_pdf_contains_the_day5_fixture_sentence_verbatim PASSED [ 68%]
tests/test_document_ingestion.py::test_library_hours_pdf_produces_exactly_one_chunk PASSED [ 72%]
tests/test_document_ingestion.py::test_docx_page_break_is_detected_end_to_end PASSED [ 76%]
tests/test_document_ingestion.py::test_embedding_model_field_matches_settings PASSED [ 80%]
tests/test_document_ingestion.py::test_source_field_uses_forward_slashes_and_matches_convention PASSED [ 84%]
tests/test_document_ingestion.py::test_modality_field_matches_file_extension PASSED [ 88%]
tests/test_document_ingestion.py::test_ingest_document_rejects_unsupported_extension PASSED [ 92%]
tests/test_document_ingestion.py::test_ingest_document_missing_file_raises_file_not_found PASSED [ 96%]
tests/test_document_ingestion.py::test_real_chunks_round_trip_through_chromadb SKIPPED [100%]

======================== 24 passed, 1 skipped in 0.26s ========================
```

The one skip is `test_real_chunks_round_trip_through_chromadb` — the same `pytest.importorskip("chromadb")` pattern Chapter 5 used, skipping cleanly when `chromadb` isn't installed in whichever environment runs the check, rather than failing. Then confirm nothing in Chapter 5's frozen contract broke:

```bash
pytest tests/ -v
```
```
======================== 33 passed, 2 skipped in 0.26s ========================
```

24 new + 9 from Chapter 5 = 33; 1 new skip + 1 from Chapter 5 = 2 — the whole suite, old and new, in one honest number.

## 5.8 Inspect a real, non-hand-written chunk

```bash
python -m src.pipelines.documents.ingest data/documents/notice.pdf
```
```
notice_pdf__p1__c001  (page 1, 233 words)
notice_pdf__p2__c001  (page 2, 300 words)
notice_pdf__p2__c002  (page 2, 130 words)
```

**This is the moment this whole chapter has been building toward**: `notice_pdf__p2__c003` was a string Chapter 5's hand-written `text_fixture` invented, with an invented sentence, before this file existed. Today, `notice.pdf` is a real file, parsed by real code, and its real page 2 genuinely contains the sentence that fixture predicted — check it yourself:

```python
>>> from src.pipelines.documents.ingest import ingest_document
>>> chunks = ingest_document("data/documents/notice.pdf")
>>> any("21st August" in c.text for c in chunks)
True
```

## 5.9 Fill in `data/README.md`

Add the three generated files to the file-inventory table (with a clear "starter corpus, not the target" note above it — the team's real 10–15 PDF / 5–8 DOCX target from Day 1 is still fully open), and fill gold-set rows T1–T3 with real paraphrase questions against this real content, so Chapter 7's first Recall@5 measurement has something genuine, if small, to measure against.

## 5.10 Git hygiene for today

- [ ] `src/core/text_normalize.py` committed
- [ ] `src/pipelines/__init__.py`, `src/pipelines/documents/*.py` committed
- [ ] `scripts/generate_sample_corpus.py` committed
- [ ] `data/documents/notice.pdf`, `library_hours.pdf`, `it_onboarding.docx` committed — these are real binary files, not code; confirm `git status` actually shows them staged, not silently ignored by a stray `.gitignore` pattern
- [ ] `tests/test_document_ingestion.py` committed; `tests/test_contract.py` **unchanged**
- [ ] `docs/decisions/adr-008-docx-pagination-via-explicit-breaks.md` committed
- [ ] `docs/decisions/README.md`, `docs/GLOSSARY.md`, `docs/ROADMAP.md`, `data/README.md` diffs committed
- [ ] Every team member has run §5.6–§5.7 on their **own** machine and seen the same pass/fail shape — the practiced version of Chapter 4 §4.4's fixture requirement, now against a real pipeline instead of a hand-written stand-in for one

---

# Part 6 — CHECK

## 6.1 Rubric

| # | Criterion | Score |
|---|---|---|
| 1 | `python scripts/generate_sample_corpus.py` runs with no assertion failure, produces 3 files | /3 |
| 2 | `pytest tests/test_document_ingestion.py -v` passes (24 passed, 1 skip acceptable without chromadb) | /3 |
| 3 | `pytest tests/test_contract.py` still fully passes — Chapter 6 didn't disturb Chapter 5's contract | /3 |
| 4 | Team can explain why `notice.pdf` page 2 produces exactly 2 chunks, with the real numbers | /3 |
| 5 | Team can explain the tail-merge rule and derive the 350-word tipping point themselves | /3 |
| 6 | Team can explain why a chunk must never cross a page boundary, in terms of the citation promise | /3 |
| 7 | Team can explain what `w:lastRenderedPageBreak` is and both reasons it isn't used | /3 |
| 8 | Team can explain why `text_normalize.py` lives in `src/core/` and not `src/pipelines/documents/` | /3 |
| 9 | Team can explain the difference between "PDF page 3" and "DOCX page 3" in this project's own pipeline | /3 |
| 10 | `data/README.md`'s inventory and T1–T3 are filled in with real, checkable content | /3 |
| | **Total** | **/30** |

## 6.2 Question bank

1. What does a PDF's content stream actually store, and why does that make text extraction an *inference* rather than a read? → §1.1.
2. Which `get_text()` mode does this project use, and name one other mode and what it returns. → §1.2.
3. Why can multi-column PDFs confuse naive text extraction, and what two mitigations exist without changing libraries? → §1.3.
4. Why does a zero-extractable-text PDF page get skipped with a warning instead of raising an error? → §1.4; three reasons, none of them "we didn't think about it."
5. What does a `.docx` file store instead of a rendered page number? → §2.1; nothing — pagination is computed by Word at render time from data not in the file.
6. Name the two signals this project's DOCX parser actually detects. → §2.2.
7. What is `w:lastRenderedPageBreak`, and why was it rejected even though it looks like a fix? → §2.4; two independent reasons — absent from our own generated files, and non-reproducible even in real ones.
8. Why does `chunk_id` use `path.name.replace(".", "_")` instead of `Path.stem`? → §3.5; `.stem` drops the extension, causing `report.pdf`/`report.docx` to collide.
9. A page has exactly 349 words. How many chunks, at size=300/overlap=50? → §3.3's table: 1 chunk, 349 words (new words = 49 < 50, merges).
10. A page has exactly 640 words. Work out the chunk ranges and lengths by hand, then check your answer. → §3.1's method: ranges `[0,300]`, `[250,550]`, `[500,640]` → lengths 300, 300, 140.
11. Why must `chunk_page_text()` be called once per page, never once across a whole document? → §3.4; the citation promise "page N" would become false for any chunk spanning two pages.
12. Why does `normalize_text()` collapse whitespace *before* stripping control characters, not after? → §5.1; collapsing first turns a paragraph-separating newline into a space instead of deleting it and gluing two paragraphs together.
13. Why does `Chunk.embedding_model` get set during ingestion, before Chapter 7 has computed any actual vector? → Chapter 5 §3.2 plus this chapter's `ingest.py`; the field is required and records *intent* — which model *will* embed this chunk — not a value that depends on the embedding already existing.
14. What's the difference between an unsupported file extension and a missing file, in terms of what `ingest_document()` raises and when it checks? → §4.4's table; `ValueError` is checked first, before any filesystem access; `FileNotFoundError` only after confirming the extension is supported.

## 6.3 Troubleshooting — extends Chapter 5 §6.3

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'fitz'` | Installed `PyMuPDF` correctly, but the **import name** differs from the **pip package name** | `pip install PyMuPDF`, then `import fitz` — this mismatch is real and common, not a sign anything is broken |
| `pip install docx` "succeeds" but `from docx import Document` fails, or behaves strangely | A real PyPI footgun: the package literally named `docx` on PyPI is a **different, largely abandoned** library, not python-docx | Always `pip install python-docx` (already correctly pinned in `requirements.txt`) — the import name `docx` is shared by both packages, which is exactly how this mistake happens |
| Every DOCX chunk reports `page=1`, even for a long real document | Not a bug — this is ADR-008's disclosed limitation: the source document has no *explicit* page breaks, only automatic reflow, which this pipeline cannot see | Confirmed expected behaviour (§2.6); if this matters for a real report, ask the author to insert manual breaks, or accept the limitation and say so |
| Off-by-one or unexpected chunk counts on a real file | Usually a page-boundary miscount, not a chunker bug — check `extract_pdf_pages`/`extract_docx_pages`'s raw per-page output first | Print `[len(t.split()) for _, t in extract_pdf_pages(path)]` before blaming `chunk_page_text()` — isolate which stage produced the surprise |
| `AssertionError: ... text overflowed the page` from `generate_sample_corpus.py` | A page's drafted text is too long for an A4 page at the chosen font size — the generator's own overflow check working correctly | Shorten the text, reduce font size, or accept fewer words on that page — do **not** remove the assertion; it exists to catch exactly this |
| `tests/test_document_ingestion.py`'s Part 4 tests fail with `FileNotFoundError` | The sample corpus hasn't been generated yet on this machine | Run `python scripts/generate_sample_corpus.py` first (§5.6) |
| A chunk's `text` looks like it's missing a space between two sentences | Possible PDF extraction quirk (rare, layout-dependent) rather than a normalization bug | Check the *raw* `extract_pdf_pages()` output before `normalize_text()` runs — normalization cannot re-insert a space extraction never produced |

## 6.4 Day 6 completion checklist

- [ ] `src/core/text_normalize.py` written and its two-line contract (§5.1) understood
- [ ] All four `src/pipelines/documents/*.py` files written
- [ ] `scripts/generate_sample_corpus.py` run successfully; three real files present in `data/documents/`
- [ ] `pytest tests/test_document_ingestion.py -v` passes on every team member's machine
- [ ] `pytest tests/test_contract.py -v` still fully passes — no regression to Chapter 5's frozen contract
- [ ] Team can trace the 380-word page-2 example by hand, matching §3.2 exactly
- [ ] Team can state both reasons `w:lastRenderedPageBreak` was rejected, without notes
- [ ] `data/README.md` updated: inventory rows + T1–T3 filled with real content
- [ ] ADR-008 read by the whole team, not just whoever wrote the parser
- [ ] Rubric §6.1 scored ≥ 24/30

---

**Next:** Chapter 7 — Embeddings & the Vector Database (Day 7), where these real chunks finally get real vectors — via `sentence-transformers`, into ChromaDB's `text_index` — and this project runs its first genuine semantic search, measured against the gold-set rows this chapter just wrote.
