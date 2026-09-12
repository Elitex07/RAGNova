"""
Generate the Chapter 6 starter corpus: three small, synthetic documents
under data/documents/, used to develop and test the ingestion pipeline
before the team supplies the project's real corpus (data/README.md's
10-15 PDF / 5-8 DOCX target).

Run with:  python scripts/generate_sample_corpus.py

Uses only PyMuPDF's and python-docx's own WRITE APIs — no new dependency
beyond what requirements.txt already pins for Chapter 6's PDF/DOCX parsing.

Why generate instead of finding real files: Chapter 6 needs something to
run the pipeline against today, and hand-picked real documents would still
need their exact word counts controlled to exercise both the single-chunk
and multi-chunk/overlap/tail-merge code paths on purpose (Chapter 6 §3).
Writing the corpus is also how `notice.pdf` — the file
tests/test_contract.py's Day-5 fixture already invented a chunk_id and a
sentence for — becomes a real file for the first time.

This is a STARTER corpus for pipeline development, not a substitute for
the team's full target corpus. See data/README.md's inventory table and
the "starter corpus only" note above it.
"""

from __future__ import annotations

from pathlib import Path

import fitz
from docx import Document

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "documents"
PAGE_W, PAGE_H = fitz.paper_size("a4")
MARGIN = 72  # 1 inch, in points

# ---------------------------------------------------------------------------
# Page text. Word counts here are not incidental:
#   - NOTICE_P2 is exactly 380 words on purpose (Chapter 6 §3.2's worked
#     example) — with CHUNK_SIZE_WORDS=300/CHUNK_OVERLAP_WORDS=50, that
#     produces exactly two chunks of 300 and 130 words. Changing this
#     text's length changes which branch of the chunker's tail-merge rule
#     fires — see tests/test_document_ingestion.py before editing it.
#   - Every other page is comfortably under 350 words, landing in the
#     "single chunk after tail-merge" zone, on purpose, to exercise that
#     path too.
#   - NOTICE_P2 deliberately contains the exact sentence
#     tests/test_contract.py's Day-5 fixture invented
#     ("The submission deadline for the project synopsis is 21st August.")
#     — the fixture predicted this file; today it becomes real.
# ---------------------------------------------------------------------------

NOTICE_P1 = """
Department of Computer Science and Engineering (Artificial Intelligence and Machine Learning)

Notice: Final Year B.Tech Project — Synopsis Submission Guidelines

All B.Tech CSE-AIML final year students working in project teams of two or three members are required to submit a project synopsis before the announced deadline. The synopsis must clearly state the problem being addressed, the proposed methodology, the technology stack, and the expected outcomes of the project. Teams should also include a short literature review summarising at least five related systems or research papers, along with a brief explanation of how the proposed project differs from or improves upon existing work.

The synopsis document should not exceed three pages, excluding the cover page and references. It must be submitted as a single PDF file through the department portal, with the team number and all member names clearly printed on the cover page. Only one submission per team is required; submitting multiple copies or asking a teammate to submit separately will cause confusion during evaluation and should be avoided.

Every team will be allotted a faculty guide who will review the synopsis and provide feedback before the presentation date. Teams are encouraged to meet their allotted guide at least once before submission to confirm that the scope of the project is realistic for the available timeline. Guide allocation will be published on the department noticeboard and the student portal separately from this notice.
""".strip()

NOTICE_P2 = """
Key Dates and Evaluation Structure

The submission deadline for the project synopsis is 21st August. Synopses received after this date will only be accepted with a written extension request approved by the head of department, and late submissions may be penalised at the evaluator's discretion. Teams are strongly advised not to wait until the final day, since the portal has historically experienced heavy load in the last few hours before a deadline.

The mid-term evaluation will weight three components: the working prototype demonstrated on the day of evaluation will carry forty percent of the total marks, the written project report will carry thirty-five percent, and the individual viva voce conducted with each team member will carry the remaining twenty-five percent. Every team member must be present for the viva; a member who is absent without prior approval from the department will receive a zero for that component regardless of the team's overall performance.

Formatting requirements for the written report follow the standard institute template, which is available for download from the student portal under the final year project section. Reports that do not follow the prescribed template, including font size, margins, and heading styles, will be returned for correction before evaluation, which may affect the submission timeline for that team.

All submitted work must be original. Any section of the report or presentation found to be copied from another team, a previous year's submission, or an online source without proper citation will be treated as a case of academic dishonesty and referred to the disciplinary committee, independent of how small the copied portion is. Teams are encouraged to run their own plagiarism check before submission using the tool recommended by the department.

Students with questions about any part of this notice should first consult their allotted faculty guide. If the guide is unavailable or the question concerns scheduling rather than technical content, students may contact the final year project coordinator through the department office during working hours, Monday through Friday.

Teams that need to modify their submitted synopsis after the deadline because of a genuine change in project scope must first inform their allotted faculty guide in writing, explaining the reason for the change, before requesting permission from the project coordinator to upload one revised document through the same portal.
""".strip()

LIBRARY_P1 = """
Central Library Notice: Revised Working Hours and Borrowing Policy

Effective from the start of this semester, the central library will remain open from eight in the morning until ten at night on all working days, and from nine in the morning until six in the evening on weekends and public holidays. These revised hours apply to the main reading halls, the reference section, and the digital resource centre on the second floor.

Borrowing limits have also been revised this semester. Undergraduate students may now borrow up to four books at a time for a period of fourteen days, while postgraduate students and faculty members may borrow up to eight books for a period of thirty days. Renewal of an existing loan is permitted once, provided no other student has placed a reservation on the same title through the library portal.

A fine of two rupees per day will be charged for every book returned after its due date, with the total fine for any single book capped at two hundred rupees regardless of how long the delay continues. Students with unpaid fines exceeding this cap will have their borrowing privileges suspended until the outstanding amount is cleared at the circulation desk.

During the examination fortnight each semester, the main reading room will remain open twenty-four hours a day, including weekends, to support students preparing for their examinations. Students wishing to use the reading room after the normal closing hours during this period must carry their institute identity card, which will be checked at the entrance by the library security staff on duty.

For any queries regarding borrowing limits, fines, or access to the digital resource centre, students may contact the library help desk in person during working hours or send an email to the address listed on the library's page of the institute website.
""".strip()

IT_P1 = """
Information Technology Onboarding Guide for New Students

Welcome to the institute network. This short guide explains the steps every new student must complete before they can use the campus email, wireless internet, and remote library access services provided by the Information Technology department.

Your institute email account is created automatically once your admission is confirmed, but it must be activated manually before first use. To activate it, visit the self-service portal linked from the institute homepage and follow the account activation steps using the temporary password printed on your admission letter. You will be asked to set a new password immediately after activation; choose one that is not used for any other personal account.

Wireless internet on campus is available through the network named RAGNOVA-STUDENT, visible from any device in the hostel, library, and academic blocks. Connect using your institute email address and the same password you set during account activation. If a device fails to connect after several attempts, restarting the device's wireless adapter usually resolves the issue before it becomes necessary to visit the IT help desk in person.

Students who need to access subscribed academic journals from outside the campus network, for example from home during a vacation, must additionally install the institute's virtual private network client, referred to as the VPN, which is available for download from the same self-service portal used for email activation.
""".strip()

IT_P2 = """
Acceptable Use Policy

Every student granted access to the institute network is expected to follow the acceptable use policy summarised below. The full policy document is available on request from the Information Technology department and takes precedence over this summary in case of any disagreement between the two.

Sharing your institute email password or network login credentials with another person, including a friend, relative, or fellow student, is strictly prohibited under all circumstances, even for a short period of time. Each account exists to identify one individual, and shared credentials make it impossible to determine who actually performed a given action on the network.

Downloading copyrighted material, including films, television shows, and paid software, without a valid licence is not permitted on the institute network at any time. Students found doing so may have their network access suspended in addition to any other consequences under applicable law.

If a student's account is found to violate this policy for the first time, network access will be suspended for a period of two weeks, during which the student must complete a short awareness session conducted by the Information Technology department before access is restored. A second violation by the same student may result in a longer suspension decided by the department in consultation with the disciplinary committee.

For questions about this policy or to report a suspected violation, students should contact the Information Technology help desk, which operates on all working days between nine in the morning and five in the evening.
""".strip()


def _write_pdf(filename: str, pages_text: list[str]) -> None:
    doc = fitz.open()
    rect = fitz.Rect(MARGIN, MARGIN, PAGE_W - MARGIN, PAGE_H - MARGIN)
    for text in pages_text:
        page = doc.new_page(width=PAGE_W, height=PAGE_H)
        spare = page.insert_textbox(rect, text, fontsize=11, fontname="helv")
        # A real, runnable check, not a comment: insert_textbox() silently
        # drops whatever doesn't fit. spare < 0 means this page's text
        # would have been truncated — exactly the kind of silent data loss
        # this project's own philosophy (validate_chunk, verify_setup.py)
        # says should fail loudly instead.
        assert spare >= 0, f"{filename}: text overflowed the page (spare={spare:.1f})"
    doc.save(DOCS_DIR / filename)
    doc.close()
    print(f"wrote {filename} ({len(pages_text)} page(s))")


def _write_docx(filename: str, pages_text: list[str]) -> None:
    document = Document()
    for i, text in enumerate(pages_text):
        for para in text.split("\n\n"):
            document.add_paragraph(para)
        if i < len(pages_text) - 1:
            document.add_page_break()  # the exact <w:br w:type="page"/>
                                        # signal docx_parser.py detects
    document.save(DOCS_DIR / filename)
    print(f"wrote {filename} ({len(pages_text)} page(s), "
          f"{len(pages_text) - 1} explicit page break(s))")


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    _write_pdf("notice.pdf", [NOTICE_P1, NOTICE_P2])
    _write_pdf("library_hours.pdf", [LIBRARY_P1])
    _write_docx("it_onboarding.docx", [IT_P1, IT_P2])
    print("\nDone. Next: pytest tests/test_document_ingestion.py -v")


if __name__ == "__main__":
    main()
