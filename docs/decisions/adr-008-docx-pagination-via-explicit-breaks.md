# ADR-008: Track DOCX pages from explicit break markers only, not Word's rendered layout

## Status
Accepted — Day 6

## Context

The frozen `Chunk` schema (Chapter 5) requires an integer `page` for every document chunk, and Chapter 6 §3.4 fixes that a chunk must never span a page boundary — a citation that says "page N" is a promise, and the promise breaks the moment a chunk's text starts on one page and ends on another. PyMuPDF gives PDF page numbers natively, because a PDF stores each page as a discrete object. A `.docx` file stores no equivalent: Word computes where a page ends at render time, from fonts, margins, and the active printer driver, none of which live in the file. Track A needs a `page` number for every DOCX chunk regardless.

## Decision

Track only two explicit, author-inserted signals that genuinely are stored in a `.docx` file's XML: a manual page break (`<w:br w:type="page"/>`, inserted by Ctrl+Enter in Word or `document.add_page_break()` in python-docx) and a paragraph's "page break before" property (`<w:pageBreakBefore/>`, common on Heading styles). Text before the first detected break is page 1; a document with no breaks at all is entirely page 1. Automatic reflow — Word wrapping a long paragraph onto a new page purely because the previous one ran out of room — is not tracked and is not detectable by this approach.

## Alternatives considered

1. **`w:lastRenderedPageBreak`** — a marker Word itself writes into the XML at the position where the document last broke pages when it was rendered and saved. This looks, at first glance, like exactly what's needed. Rejected for two independent reasons: first, it is written only by Word's own layout engine — any `.docx` this project *generates* (scripts/generate_sample_corpus.py) never passes through that engine, so this marker would be entirely absent from our own starter corpus and would not even help the file we control most. Second, even in a real Word-authored file, it is a stale snapshot of one save's fonts, margins, and print settings — not a stable property of the document — so trusting it would make citation page numbers non-reproducible across machines or across a re-save, directly against this project's own reproducibility standard (Chapter 3 §3.8, restated in `requirements.txt`'s pinning rationale).
2. **Reimplement Word's layout/reflow engine** to compute true rendered page breaks from font metrics and margins. Rejected outright: disproportionate effort for page-number accuracy alone, far outside what a 9-day sprint with a beginner team can absorb, and duplicates work a $149 piece of software (Microsoft Word) already does.
3. **Treat every DOCX as a single page.** Rejected: `validate_chunk()` requires `page >= 1` for every document chunk, so this technically satisfies the contract, but it is confidently wrong for any real multi-page document — every citation for a DOCX source would claim "page 1," which is worse than admitting the limitation.
4. **Estimate a page number from a fixed words-per-page constant** (e.g., "every 400 words is a new page"). Rejected: this produces a page number that looks exactly as trustworthy as a real one while being no more accurate than alternative 3 — a citation should either be right or visibly limited, not confidently wrong.

## Consequences

**Positive**
+ Correct for any DOCX that uses explicit structure — which includes every file in this project's own starter corpus (`it_onboarding.docx` uses one manual break on purpose, to exercise exactly this code path).
+ Zero new dependencies: both signals come from python-docx's own object model or one documented drop to its underlying XML.
+ Fails visibly rather than silently: a document that relies entirely on automatic reflow reports as one page, which is an obviously-incomplete answer a reader will question, not a wrong answer stated with false confidence.

**Negative**
− Undercounts any document that relies on Word's automatic reflow instead of explicit breaks — a real report with no manual page breaks will report as fewer pages than it actually prints as.
− Two visually-identical printed documents can report different page numbers here, depending only on whether their author happened to insert manual breaks — an inconsistency a PDF citation never has.

**Implications for other components**
- Track C's citation display (Chapter 11) should not present a DOCX page number with the same visual confidence as a PDF page number — flag this distinction when building that UI.
- Chapter 6's teaching doc must state this limitation plainly rather than let a team member discover it by noticing DOCX citations look "off."

## Revisit if

The team's real corpus (once populated per `data/README.md`'s target) turns out to contain DOCX files that rely heavily on automatic reflow rather than explicit structure — at that point, converting DOCX to PDF first (e.g. via a headless LibreOffice call) before parsing would give true rendered page numbers, at the cost of a new, heavier dependency this project has avoided so far.

---

*This ADR's investigation of `w:lastRenderedPageBreak` is deliberately recorded even though it was rejected — see Chapter 6 §2.4 for the worked-through reasoning, so a future contributor who has the same "wait, doesn't this field solve it?" idea doesn't have to re-derive why it doesn't.*
