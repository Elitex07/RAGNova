"""
Generate the multimodal corpus for RAGNova:
  - data/images/: 12 images (screenshots, notice posters, diagrams, ID card)
  - data/audio/: 4 spoken audio clips (.wav) matching the campus corpus topics

Run with:  python scripts/generate_multimodal_corpus.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
import wave
import math
import struct

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
AUDIO_DIR = DATA_DIR / "audio"


def _get_font(size: int = 16, bold: bool = False):
    font_names = ["arial.ttf", "segoeui.ttf", "DejaVuSans.ttf", "calibri.ttf"]
    if bold:
        font_names = ["arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf", "calibrib.ttf"] + font_names
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def create_image(
    filename: str,
    width: int,
    height: int,
    bg_color: tuple[int, int, int],
    title: str,
    sections: list[tuple[str, str | list[str]]],
    border_color: tuple[int, int, int] | None = None,
    badge: str | None = None,
):
    """Render a clean, high-contrast image containing visible text suitable for OCR and CLIP."""
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    header_font = _get_font(16, bold=True)
    body_font = _get_font(14, bold=False)
    small_font = _get_font(12, bold=False)

    # Optional border
    if border_color:
        draw.rectangle([(0, 0), (width - 1, height - 1)], outline=border_color, width=2)

    # Header bar
    header_bg = (30, 41, 59) if bg_color != (30, 41, 59) else (15, 23, 42)
    draw.rectangle([(0, 0), (width, 42)], fill=header_bg)

    # Window control dots
    draw.ellipse([(12, 16), (22, 26)], fill=(239, 68, 68))
    draw.ellipse([(28, 16), (38, 26)], fill=(245, 158, 11))
    draw.ellipse([(44, 16), (54, 26)], fill=(16, 185, 129))

    # Header title text
    draw.text((68, 12), title, font=header_font, fill=(255, 255, 255))

    if badge:
        b_w = len(badge) * 8 + 16
        draw.rectangle([(width - b_w - 15, 10), (width - 15, 32)], fill=(59, 130, 246))
        draw.text((width - b_w - 7, 13), badge, font=small_font, fill=(255, 255, 255))

    y = 60
    margin_x = 30

    for sec_title, sec_content in sections:
        if sec_title:
            draw.text((margin_x, y), sec_title, font=header_font, fill=(30, 58, 138) if bg_color[0] > 200 else (147, 197, 253))
            y += 26

        if isinstance(sec_content, str):
            lines = sec_content.split("\n")
        else:
            lines = sec_content

        for line in lines:
            if y > height - 30:
                break
            text_color = (15, 23, 42) if bg_color[0] > 200 else (226, 232, 240)
            draw.text((margin_x + 10, y), line, font=body_font, fill=text_color)
            y += 22
        y += 12

    out_path = IMAGES_DIR / filename
    img.save(out_path, format="PNG")
    print(f"wrote image: {out_path.name} ({width}x{height})")


def generate_all_images():
    """Generates 12 deliberate images covering screenshots, posters, and diagrams."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Portal Login Screenshot
    create_image(
        "screenshot_portal_login.png",
        700, 480, (248, 250, 252),
        "RAGNova Student Portal — Single Sign-On",
        [
            ("Student & Faculty Authentication", [
                "Service: Campus Central Single Sign-On (SSO)",
                "Notice: Activate your account before first use.",
                "",
                "[ Username / Institute Email ]",
                "  student.id@ragnova.edu",
                "",
                "[ Password ]",
                "  ••••••••••••••••",
                "",
                "Notice: Use the temporary password from your admission letter.",
                "Sharing credentials with another person violates institute policy.",
                "Support: Contact Information Technology help desk (9am - 5pm).",
            ])
        ],
        border_color=(203, 213, 225),
        badge="STUDENT PORTAL"
    )

    # 2. Wi-Fi Setup Screenshot
    create_image(
        "screenshot_wifi_setup.png",
        650, 450, (241, 245, 249),
        "Network Settings — Wireless Connection",
        [
            ("Wireless Network: RAGNOVA-STUDENT", [
                "Status: Available across Hostel, Library, and Academic Blocks",
                "Security Protocol: WPA2-Enterprise (802.1X PEAP)",
                "",
                "Identity (Email): username@ragnova.edu",
                "Password: Same password as campus email activation",
                "CA Certificate: Do not validate (or Use System Certs)",
                "",
                "Troubleshooting:",
                "If connection fails repeatedly, restart the wireless adapter.",
                "Visit the IT help desk if persistent authentication errors occur."
            ])
        ],
        border_color=(148, 163, 184),
        badge="WIFI SETTINGS"
    )

    # 3. 403 Forbidden Access Error Screenshot
    create_image(
        "screenshot_error_403.png",
        650, 400, (254, 242, 242),
        "Access Denied — 403 Forbidden",
        [
            ("Institute Network Security Gateway", [
                "Your request to download academic content was blocked.",
                "Reason: Mass scraping or downloading copyrighted media is restricted.",
                "Policy Reference: Acceptable Use Policy §3.2 (Copyrighted Material)",
                "",
                "Notice of Penalties:",
                "First violation: Network access suspended for two weeks.",
                "Mandatory requirement: Complete IT awareness session before access restored.",
                "Second violation: Long-term suspension via Disciplinary Committee."
            ])
        ],
        border_color=(239, 68, 68),
        badge="SECURITY ALERT"
    )

    # 4. Synopsis Submission Portal Screenshot
    create_image(
        "screenshot_synopsis_portal.png",
        700, 500, (248, 250, 252),
        "CSE-AIML Final Year Project Submission Portal",
        [
            ("B.Tech Final Year Project — Synopsis Submission", [
                "Submission Deadline: 21st August (Strict deadline)",
                "Document format: Single PDF file (Max 3 pages excluding references)",
                "Team composition: 2 or 3 students per project team",
                "",
                "Evaluation Components:",
                "  - Working Prototype Demonstration: 40% weighting",
                "  - Written Project Report: 35% weighting",
                "  - Individual Viva Voce: 25% weighting",
                "",
                "File Selected: final_synopsis_team12.pdf (1.8 MB)",
                "[ SUBMIT SYNOPSIS FOR FACULTY GUIDE REVIEW ]"
            ])
        ],
        border_color=(59, 130, 246),
        badge="DEADLINE: 21 AUG"
    )

    # 5. VPN Client Screenshot
    create_image(
        "screenshot_vpn_client.png",
        640, 420, (243, 244, 246),
        "RAGNova SecureConnect VPN Client v2.4",
        [
            ("Remote Access to Campus Digital Library", [
                "Gateway: vpn.ragnova.edu:443",
                "Tunnel Status: Connected (AES-256 Encryption)",
                "Assigned IP: 10.120.44.18",
                "",
                "Accessible Services:",
                "  - Subscribed IEEE, ACM, and Springer Academic Journals",
                "  - Digital Resource Centre 2nd floor library catalog",
                "  - Department compute cluster SSH gateway",
                "",
                "Download client installer from the IT self-service portal."
            ])
        ],
        border_color=(107, 114, 128),
        badge="VPN CONNECTED"
    )

    # 6. Seminar Poster Notice
    create_image(
        "notice_seminar_poster.png",
        600, 520, (238, 242, 255),
        "Department of Computer Science & Engineering",
        [
            ("Guest Seminar: Multimodal Retrieval Augmented Generation", [
                "Date: September 28, 2026 | Time: 2:00 PM - 4:30 PM",
                "Venue: Main Auditorium Hall B, AIML Academic Block",
                "",
                "Key Topics Covered:",
                "  - Offline vector databases: ChromaDB and HNSW indexing",
                "  - Cross-modal retrieval using OpenCLIP embeddings",
                "  - Local LLM inference with Ollama and Llama 3.2 3B",
                "  - Verifiable citations from PDF, audio, and image sources",
                "",
                "Open to all B.Tech and M.Tech CSE-AIML students.",
                "Registration: Scan QR at Department Office or sign up on portal."
            ])
        ],
        border_color=(99, 102, 241),
        badge="SEMINAR NOTICE"
    )

    # 7. Library Fines Notice
    create_image(
        "notice_library_fines.png",
        620, 460, (255, 251, 235),
        "Central Library — Borrowing Policy and Overdue Fines",
        [
            ("Circulation Desk Policy Summary", [
                "Undergraduate borrowing quota: 4 books for 14 days",
                "Postgraduate and faculty quota: 8 books for 30 days",
                "One renewal permitted if no reservation is pending.",
                "",
                "Late Return Fine Schedule:",
                "  - Fine rate: 2 rupees per day per overdue book",
                "  - Maximum fine cap: 200 rupees per single title",
                "  - Borrowing privileges suspended when unpaid fines exceed cap.",
                "",
                "Working Hours: 8:00 AM to 10:00 PM on all working days.",
                "Help Desk: library@ragnova.edu | Ground Floor Counter"
            ])
        ],
        border_color=(245, 158, 11),
        badge="LIBRARY NOTICE"
    )

    # 8. Lab Rules Notice
    create_image(
        "notice_lab_rules.png",
        620, 440, (240, 253, 244),
        "AIML Computing Laboratory — Acceptable Use Rules",
        [
            ("Laboratory Guidelines & Account Security", [
                "1. Each account is strictly for individual student use.",
                "2. Credential sharing with any peer or friend is forbidden.",
                "3. No unlicensed media, game, or commercial downloading.",
                "",
                "Disciplinary Process:",
                "  - First violation: 2-week campus network suspension.",
                "  - Second violation: Referral to institute disciplinary committee.",
                "",
                "Laboratory Operating Hours: Monday to Friday 9:00 AM - 5:00 PM",
                "Report infractions to IT Help Desk, Ground Floor Academic Block."
            ])
        ],
        border_color=(34, 197, 94),
        badge="LAB SAFETY"
    )

    # 9. Midterm Schedule Notice
    create_image(
        "notice_midterm_schedule.png",
        650, 460, (245, 243, 255),
        "Final Year Project — Mid-Term Evaluation Timetable",
        [
            ("B.Tech Evaluation Weighting Scheme", [
                "Evaluation Panel Schedule:",
                "  - Team demonstrations: October 14th - 16th, 2026",
                "  - Venue: Conference Room 3, Department of CSE-AIML",
                "",
                "Marking Distribution:",
                "  - Working Prototype Demo: 40% (must run completely offline)",
                "  - Written Project Report: 35% (standard institute template)",
                "  - Individual Viva Voce: 25% (all team members must attend)",
                "",
                "Note: Absent members without prior dean approval receive zero for viva."
            ])
        ],
        border_color=(168, 85, 247),
        badge="EVALUATION DATES"
    )

    # 10. RAGNova Architecture Diagram
    create_image(
        "diagram_rag_architecture.png",
        720, 520, (15, 23, 42),
        "RAGNova Offline Multimodal Architecture Diagram",
        [
            ("SYSTEM PIPELINE FLOW", [
                "1. Input Modalities:",
                "   [ Documents: PDF/DOCX ]  [ Images: PNG/JPG ]  [ Audio: WAV/MP3 ]",
                "",
                "2. Ingestion & Embedding Layers:",
                "   - Text Pipeline: PyMuPDF / python-docx -> all-MiniLM-L6-v2 (384-dim)",
                "   - Vision Pipeline: Tesseract OCR + OpenCLIP ViT-B-32 (512-dim)",
                "   - Audio Pipeline: faster-whisper -> Text Chunks with timestamps",
                "",
                "3. Dual Vector Stores (ChromaDB):",
                "   [ text_index collection ]       [ image_index collection ]",
                "",
                "4. Retrieval & Local Generation:",
                "   - Cosine top-K retrieval -> Prompt with provenance chunks",
                "   - Ollama (Llama 3.2 3B) -> Grounded answer with numbered citations"
            ])
        ],
        border_color=(56, 189, 248),
        badge="ARCHITECTURE"
    )

    # 11. Campus Map Diagram
    create_image(
        "diagram_campus_map.png",
        680, 480, (248, 250, 252),
        "Campus Facility Blueprint & Directory",
        [
            ("Key Infrastructure Locations", [
                "[ Building 1 ] Administrative Block & Admission Registry",
                "[ Building 2 ] Department of CSE & AIML Labs (Auditorium Hall B)",
                "[ Building 3 ] Central Library & Digital Resource Centre (2nd Fl)",
                "[ Building 4 ] Information Technology Help Desk & Data Centre",
                "[ Building 5 ] Student Hostels & Residential Common Halls",
                "",
                "Wireless Coverage: RAGNOVA-STUDENT available in Buildings 1 through 5.",
                "Opening Hours:",
                "  - Central Library: 8:00 AM - 10:00 PM (24h during exams)",
                "  - IT Help Desk: 9:00 AM - 5:00 PM (Monday - Friday)"
            ])
        ],
        border_color=(100, 116, 139),
        badge="CAMPUS MAP"
    )

    # 12. Student ID Card Mockup
    create_image(
        "photo_id_card_sample.png",
        580, 360, (241, 245, 249),
        "RAGNova Institute of Technology — Student ID",
        [
            ("INSTITUTE IDENTITY CARD", [
                "Student Name: Alex Morgan",
                "Roll Number: 23AIML042",
                "Program: B.Tech Computer Science (AIML)",
                "Library Barcode: *LIB-884920*",
                "Valid Through: June 2027",
                "",
                "Borrowing Privilege: 4 books / 14 days renewal",
                "Night Reading Room Access: Valid during examination fortnight."
            ])
        ],
        border_color=(79, 70, 229),
        badge="STUDENT ID"
    )


def _generate_synthetic_speech_wav(filepath: Path, text: str):
    """Attempt Windows PowerShell TTS for natural speech; fallback to synthetic acoustic waveform."""
    escaped_text = text.replace("'", "''")
    ps_cmd = (
        f"Add-Type -AssemblyName System.Speech; "
        f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$synth.SetOutputToWaveFile('{filepath.as_posix()}'); "
        f"$synth.Speak('{escaped_text}'); "
        f"$synth.Dispose()"
    )
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=30)
        if res.returncode == 0 and filepath.exists() and filepath.stat().st_size > 1000:
            print(f"wrote audio via Windows TTS: {filepath.name} ({filepath.stat().st_size} bytes)")
            return
    except Exception as e:
        print(f"Windows TTS exception: {e}")

    # Fallback: Generate a clean multi-tone synthetic acoustic wav file
    sample_rate = 16000
    duration_s = max(10.0, len(text.split()) * 0.4)
    total_frames = int(sample_rate * duration_s)

    with wave.open(str(filepath), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)

        frames = bytearray()
        for i in range(total_frames):
            t = float(i) / sample_rate
            val = 0.3 * math.sin(2.0 * math.pi * 220.0 * t) + \
                  0.2 * math.sin(2.0 * math.pi * 440.0 * t + math.sin(2 * math.pi * 2.5 * t)) + \
                  0.1 * math.sin(2.0 * math.pi * 880.0 * t)
            envelope = 0.5 * (1.0 + math.sin(2.0 * math.pi * 3.5 * t))
            val *= envelope
            sample = int(max(-32767, min(32767, val * 32767)))
            frames.extend(struct.pack("<h", sample))

        w.writeframes(frames)
    print(f"wrote synthetic audio: {filepath.name} ({duration_s:.1f}s, {filepath.stat().st_size} bytes)")


def generate_all_audio():
    """Generates 4 campus audio clips (.wav) corresponding to the academic topics."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    audio_clips = [
        (
            "hod_project_announcement.wav",
            "Good morning final year students. This is an important announcement regarding your B.Tech CSE-AIML "
            "project evaluation. Please remember that the working prototype demonstrated on evaluation day carries "
            "forty percent of your total marks. The written project report carries thirty-five percent, and the "
            "individual viva voce with each team member carries the remaining twenty-five percent. Every member must "
            "attend the viva in person. Do not miss the synopsis submission deadline on August twenty-first."
        ),
        (
            "library_orientation_excerpt.wav",
            "Welcome to the Central Library orientation. Effective this semester, our working hours are eight in the "
            "morning until ten at night on working days, and nine in the morning until six in the evening on weekends. "
            "Undergraduate students may check out up to four books at a time for fourteen days. Overdue fines are two "
            "rupees per day, capped at two hundred rupees per title. The digital resource centre is located on the "
            "second floor."
        ),
        (
            "it_helpdesk_wifi_instructions.wav",
            "Hello students. If you are experiencing difficulty connecting to the campus wireless network named "
            "RAGNOVA-STUDENT, please follow these steps. Enter your full institute email address and the password set "
            "during account activation. If the connection fails, restart your wireless adapter before visiting the help "
            "desk. Remember that sharing your credentials with any other student is strictly prohibited and results in a "
            "two-week network suspension."
        ),
        (
            "lab_assistant_briefing.wav",
            "Attention students in the AI and Machine Learning laboratory. If you need remote access to academic journal "
            "databases while working from home, please install the institute VPN client available on the self-service "
            "portal. Downloading copyrighted movies or commercial software over the campus network is strictly barred. "
            "The IT help desk is open Monday to Friday from nine in the morning until five in the evening."
        ),
    ]

    for filename, text in audio_clips:
        filepath = AUDIO_DIR / filename
        _generate_synthetic_speech_wav(filepath, text)


def main():
    print(f"Generating multimodal corpus under {DATA_DIR}...")
    generate_all_images()
    generate_all_audio()
    print("\nMultimodal corpus generation complete.")


if __name__ == "__main__":
    main()
