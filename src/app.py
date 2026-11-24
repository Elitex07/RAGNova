"""
RAGNova — Professional Multimodal AI Assistant UI

A unified multimodal Streamlit interface for the offline multimodal RAG system.
Features:
  - Text, voice (faster-whisper), and image (CLIP + OCR) query processing
  - Live token streaming via stream_answer() and st.write_stream()
  - Expandable, rich citations adhering to ADR-003, ADR-007, and ADR-008
  - Human feedback collection loop logging to feedback.jsonl
  - Live knowledge base upload and indexing for PDF, DOCX, Images, and Audio
  - Canned demo answers: opt-in only, always labelled, logged as "scaffold-mock"
  - System status and corpus overview in the sidebar

If the live system cannot answer (Ollama down, the model will not start, the
index is unreadable) the chat says so and shows the real error. It never swaps
in a canned answer: a tester would rate it as if the system had written it.

Run with:  streamlit run src/app.py
from the project root, so that .streamlit/config.toml applies (localhost only,
no usage telemetry).
"""

from __future__ import annotations

import html
import sys
from datetime import datetime
from pathlib import Path

# Add project root to sys.path so src imports resolve cleanly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import ollama
from PIL import Image

from src.core.config import settings
from src.pipelines.rag.answer import check_citations, extract_citation_numbers, is_refusal, search_question, stream_answer
from src.pipelines.rag.attachments import image_attachment
from src.ui.backend import (
    AUDIO_EXTS,
    DOCUMENT_EXTS,
    IMAGE_EXTS,
    add_to_corpus,
    attachment_note,
    check_model_generates,
    index_counts,
    kind_of,
    list_sources,
    ocr_available,
    ocr_image,
    ollama_status,
    transcribe_audio_bytes,
)
from src.ui.citations import CitationView, cited_views, citation_views
from src.ui.feedback import FeedbackEntry, model_label, record_feedback

ENGINE_LIVE = "Live Multimodal RAG"
ENGINE_CANNED = "Canned demo answers (not the real system)"
CANNED_BANNER = (
    "⚠️ Canned demo answer: hand-written text in src/app.py, not retrieved from "
    "the index and not written by the model. Do not rate it as a RAGNova answer."
)
SOURCE_ICONS = {"document": "📄", "image": "🖼️", "audio": "🎙️"}
GREETING = (
    "Hello! I am **RAGNova**, your private offline multimodal intelligence assistant. "
    "I can analyze and answer questions grounded strictly in your indexed documents, images, "
    "and audio recordings with zero cloud exposure. "
    "To ask about your own files, add them in the sidebar: the page "
    "then answers from that file alone, and **Answer from** switches back to everything."
)

# ---------------------------------------------------------------------------
# Page Configuration & Advanced Executive Styling
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="RAGNova — Offline Multimodal Intelligence Studio",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1E293B;
    }

    /* Overall page container */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3rem !important;
        max-width: 1100px !important;
    }

    /* Executive Top Bar (Clean Light Theme) */
    .top-header-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 1px solid #DBEAFE;
        border-radius: 16px;
        padding: 1.6rem 2rem;
        margin-bottom: 1.6rem;
        color: #0F172A;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.05);
        position: relative;
        overflow: hidden;
    }
    .top-header-card::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.12) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #0F172A 0%, #2563EB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.35rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .sub-title {
        font-size: 0.98rem;
        color: #64748B;
        font-weight: 400;
        line-height: 1.5;
        max-width: 780px;
        margin-bottom: 1rem;
    }

    .header-pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
    }
    .header-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        color: #334155;
        padding: 0.25rem 0.7rem;
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }

    /* Hero Discovery Canvas for fresh chats */
    .hero-canvas {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.04);
    }
    .hero-canvas-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.3rem;
    }
    .hero-canvas-subtitle {
        font-size: 0.9rem;
        color: #64748B;
        margin-bottom: 1.2rem;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 1.4rem;
    }
    @media (max-width: 768px) {
        .feature-grid { grid-template-columns: 1fr; }
    }
    .feature-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.2s ease;
    }
    .feature-card:hover {
        border-color: #93C5FD;
        background: #F0F7FF;
        transform: translateY(-2px);
    }
    .feature-icon {
        font-size: 1.4rem;
        margin-bottom: 0.4rem;
    }
    .feature-heading {
        font-size: 0.88rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.25rem;
    }
    .feature-desc {
        font-size: 0.78rem;
        color: #64748B;
        line-height: 1.45;
    }

    /* Section Label */
    .showcase-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.6rem;
    }

    /* Sidebar metric cards */
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.65rem 0.5rem;
        text-align: center;
        transition: transform 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-1px);
        border-color: #CBD5E1;
    }
    .metric-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-label {
        font-size: 0.7rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-top: 0.15rem;
    }

    /* Live Status Badge */
    .status-badge-live {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        color: #065F46;
        padding: 0.3rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    .status-dot-live {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.25);
    }

    /* Streamlit Chat Messages Overhaul */
    [data-testid="stChatMessage"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        padding: 1.1rem 1.35rem !important;
        margin-bottom: 1.1rem !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03) !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background-color: #F8FAFC !important;
        border-color: #CBD5E1 !important;
    }

    /* Chat Input Styling */
    [data-testid="stChatInput"] {
        border-radius: 24px !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06) !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #2563EB !important;
        box-shadow: 0 4px 18px rgba(37, 99, 235, 0.18) !important;
    }

    /* Multimodal Dock Styling */
    .multimodal-dock-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.88rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 0.4rem;
    }

    /* Enhanced Citation container */
    .citation-box {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 0.95rem 1.2rem;
        margin-top: 0.75rem;
        border-radius: 0 10px 10px 0;
        font-size: 0.92rem;
        line-height: 1.55;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    .citation-box.docx-border {
        border-left-color: #2563EB;
    }
    .citation-box.audio-border {
        border-left-color: #10B981;
    }
    .citation-box.image-border {
        border-left-color: #F59E0B;
    }

    .badge-pill {
        display: inline-block;
        padding: 0.22rem 0.58rem;
        font-size: 0.72rem;
        font-weight: 700;
        border-radius: 9999px;
        background-color: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #DBEAFE;
        margin-right: 0.45rem;
        letter-spacing: 0.03em;
    }
    .badge-pill.badge-audio {
        background-color: #ECFDF5;
        color: #047857;
        border-color: #A7F3D0;
    }
    .badge-pill.badge-image {
        background-color: #FFFBEB;
        color: #B45309;
        border-color: #FDE68A;
    }

    /* Styled Expander Header */
    .streamlit-expanderHeader {
        background-color: #F8FAFC !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        color: #1E293B !important;
    }

    /* Dynamic Model Selector Dropdown */
    div[data-testid="stSelectbox"] > label {
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        color: #475569 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin-bottom: 0.35rem !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover {
        border-color: #3B82F6 !important;
    }

    /* Pulsing Cyan Status Indicator (Light Theme) */
    .status-panel {
        background-color: #ECFEFF; /* Soft fresh light cyan */
        border: 1px solid #A5F3FC; /* Light cyan border */
        border-radius: 8px;
        padding: 10px 14px;
        display: flex;
        align-items: center;
        gap: 10px;
        color: #0E7490; /* Crisp deep cyan text */
        font-family: sans-serif;
        font-size: 0.88rem;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    .pulsing-dot {
        width: 10px;
        height: 10px;
        background-color: #06B6D4; /* Vibrant Cyan */
        border-radius: 50%;
        box-shadow: 0 0 6px rgba(6, 182, 212, 0.45);
        animation: pulse-animation 1.5s infinite alternate;
    }
    @keyframes pulse-animation {
        0% { box-shadow: 0 0 3px rgba(6, 182, 212, 0.3); opacity: 0.6; }
        100% { box-shadow: 0 0 10px rgba(6, 182, 212, 0.9); opacity: 1; }
    }

    /* Telemetry st.metric Cards (Clean Light Theme) */
    [data-testid="stMetric"] {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 0.6rem 0.75rem !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
    }
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }
    [data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def new_message(role: str, **fields) -> dict:
    """One chat-history entry. `engine` is "live" for the real pipeline and
    "scaffold" for canned demo text; `error` is a failure the user must see,
    and is the reason an answer is not offered for rating."""
    return {
        "role": role,
        "content": "",
        "citations": None,
        "views": None,
        "warning": None,
        "error": None,
        "engine": None,
        "image_note": None,
        **fields,
    }


def render_views(views: list[CitationView], expanded: bool = False) -> None:
    """The citation list for a real answer (one CitationView per chunk)."""
    with st.expander(f"📚 Sources & Citations ({len(views)})", expanded=expanded):
        for view in views:
            modality_lower = view.modality_label.lower()
            border_cls = f"{modality_lower}-border"
            badge_mod = f"badge-{modality_lower}" if modality_lower in ["audio", "image"] else ""
            st.markdown(
                f"""
                <div class="citation-box {border_cls}">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.35rem;">
                        <span>
                            <span class="badge-pill {badge_mod}">{html.escape(view.modality_label.upper())}</span>
                            <strong style="color: #0F172A; font-size: 0.95rem;">{html.escape(view.title)}</strong>
                        </span>
                    </div>
                    <div style="margin-top: 0.4rem; color: #334155; font-style: italic;">"{html.escape(view.excerpt)}"</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if view.note:
                st.caption(f"ℹ️ {view.note}")
            if view.modality_label == "Audio" and view.audio_start_s is not None and view.file_exists:
                st.audio(view.file_path, start_time=int(view.audio_start_s))
            elif view.modality_label == "Image" and view.file_exists:
                try:
                    st.image(view.file_path, width=320, caption=view.title)
                except Exception:
                    pass


def render_canned_citations(citations: list[dict], expanded: bool = False) -> None:
    """The hand-written citations that go with a canned demo answer."""
    with st.expander(f"📚 Sources & Citations ({len(citations)})", expanded=expanded):
        for cit in citations:
            st.markdown(
                f"""
                <div class="citation-box">
                    <span class="badge-pill">{html.escape(cit['modality'].upper())}</span>
                    <strong>[{cit['id']}]</strong> <code>{html.escape(cit['source'])}</code> {html.escape(cit.get('location', ''))}<br>
                    <div style="margin-top: 0.35rem; font-style: italic;">"{html.escape(cit['snippet'])}"</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Sidebar: System Metadata, Ingestion & Corpus Stats
# ---------------------------------------------------------------------------
st.session_state.setdefault("kb_nonce", 0)            # changing an uploader's key empties it
st.session_state.setdefault("query_img_nonce", 0)

with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.2rem;">
            <span style="font-size: 1.85rem;">🌌</span>
            <div>
                <div style="font-size: 1.35rem; font-weight: 800; color: #0F172A; line-height: 1.2;">RAGNova</div>
                <div style="font-size: 0.78rem; font-weight: 500; color: #64748B;">Offline Multimodal Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("### ⚙️ System Status")

    # Fetch available models directly from local Ollama instance
    try:
        response = ollama.list()
        raw_models = response.get("models", []) if isinstance(response, dict) else getattr(response, "models", [])
        local_models = []
        for m in raw_models:
            name = m.get("model") or m.get("name") if isinstance(m, dict) else (getattr(m, "model", None) or getattr(m, "name", None))
            if name:
                local_models.append(str(name))
        if not local_models:
            local_models = [settings.OLLAMA_MODEL]
    except Exception:
        local_models = ["llama3.2:3b (Offline)"]

    if settings.OLLAMA_MODEL not in local_models and f"{settings.OLLAMA_MODEL} (Offline)" not in local_models:
        local_models.insert(0, settings.OLLAMA_MODEL)

    # Dynamic dropdown styled for a dark UI
    selected_idx = 0
    for idx, opt in enumerate(local_models):
        if settings.OLLAMA_MODEL in opt:
            selected_idx = idx
            break

    selected_engine = st.selectbox(
        "Active Engine",
        options=local_models,
        index=selected_idx,
        help="Select the active local LLM model served by Ollama on the fly."
    )
    if selected_engine:
        clean_model_name = selected_engine.split(" ")[0]
        if clean_model_name != settings.OLLAMA_MODEL:
            settings.OLLAMA_MODEL = clean_model_name
            st.session_state["selected_engine"] = clean_model_name

    # Render the dynamic HTML component
    st.markdown(f"""
        <div class="status-panel">
            <div class="pulsing-dot"></div>
            <span><strong>Live:</strong> {html.escape(selected_engine)}</span>
        </div>
    """, unsafe_allow_html=True)

    ollama_state, ollama_detail = ollama_status()
    if ollama_state == "missing_model":
        st.warning(f"⚠️ Ollama is running but `{settings.OLLAMA_MODEL}` is not pulled")
        st.caption(f"Run `ollama pull {settings.OLLAMA_MODEL}`.")
    elif ollama_state != "ready":
        st.warning("⚠️ Ollama is not reachable")
        st.caption("Run `ollama serve`. Answers require the local LLM daemon.")

    with st.expander("🧩 Model Specs & Diagnostics", expanded=False):
        st.markdown(
            f"""
            <div style="font-size: 0.82rem; line-height: 1.75; color: #334155; margin-bottom: 0.8rem;">
                <div><strong>LLM Model:</strong> <code>{html.escape(settings.OLLAMA_MODEL)}</code></div>
                <div><strong>Text Embedder:</strong> <code>{html.escape(settings.TEXT_EMBEDDING_MODEL)}</code></div>
                <div><strong>Vision Embedder:</strong> <code>{html.escape(settings.CLIP_MODEL)}</code></div>
                <div><strong>Speech Engine:</strong> <code>faster-whisper ({html.escape(settings.WHISPER_MODEL_SIZE)})</code></div>
                <div><strong>Vector DB:</strong> <code>ChromaDB (HNSW Cosine)</code></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🔬 Test the model", key="btn_model_check", use_container_width=True):
            with st.spinner(f"Verifying {settings.OLLAMA_MODEL} generation..."):
                worked, detail = check_model_generates()
            st.session_state.model_check = (worked, detail, datetime.now().strftime("%H:%M:%S"))
        model_check = st.session_state.get("model_check")
        if model_check:
            worked, detail, when = model_check
            (st.success if worked else st.error)(f"{when}: {detail}")

    st.divider()
    st.subheader("📁 Knowledge Base")
    docs_dir = PROJECT_ROOT / "data" / "documents"
    images_dir = PROJECT_ROOT / "data" / "images"
    audio_dir = PROJECT_ROOT / "data" / "audio"

    n_docs = len([p for p in docs_dir.iterdir() if p.is_file() and p.suffix.lower() in DOCUMENT_EXTS]) if docs_dir.exists() else 0
    n_images = len([p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS]) if images_dir.exists() else 0
    n_audio = len([p for p in audio_dir.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_EXTS]) if audio_dir.exists() else 0

    st.markdown("#### 🗄️ RAG Index Status")

    # Fetch actual ChromaDB collection counts and connectivity
    try:
        counts = index_counts()
        doc_chunks = counts.get('text', 0) + counts.get('image', 0)
        db_status = "Connected"
    except Exception:
        doc_chunks = 0
        db_status = "Offline"

    if "initial_chunks" not in st.session_state:
        st.session_state["initial_chunks"] = doc_chunks

    delta_count = doc_chunks - st.session_state.get("initial_chunks", doc_chunks)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="ChromaDB Vector Space", 
            value=db_status, 
            delta="Local Storage", 
            delta_color="normal"
        )
    with col2:
        st.metric(
            label="Indexed Chunks", 
            value=f"{doc_chunks:,}", 
            delta=f"+{delta_count} this session" if delta_count > 0 else "Synced"
        )

    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.4rem; margin-top: 0.6rem; margin-bottom: 0.6rem;">
            <div class="metric-card">
                <div class="metric-value">📄 {n_docs}</div>
                <div class="metric-label">Docs</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">🖼️ {n_images}</div>
                <div class="metric-label">Images</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">🎙️ {n_audio}</div>
                <div class="metric-label">Audio</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.subheader("📥 Add Knowledge")
    kb_flash = st.session_state.pop("kb_flash", None)
    if kb_flash:
        (st.success if kb_flash[0] else st.error)(kb_flash[1])
    all_allowed = sorted([ext.lstrip(".") for ext in (DOCUMENT_EXTS | IMAGE_EXTS | AUDIO_EXTS)])
    uploaded_kb_file = st.file_uploader(
        "Upload document, image or audio",
        type=all_allowed,
        key=f"kb_uploader_{st.session_state.kb_nonce}",
    )
    if uploaded_kb_file is not None and st.button("Save & Index File", key="btn_index_upload", use_container_width=True):
        with st.spinner(f"Indexing {uploaded_kb_file.name}..."):
            try:
                result = add_to_corpus(
                    uploaded_kb_file.name,
                    uploaded_kb_file.getvalue(),
                    data_root=PROJECT_ROOT / "data",
                )
                if result.focus:
                    st.session_state.focus_sources = result.focus
                st.session_state.kb_flash = (result.ok, result.message)
                st.session_state.kb_nonce += 1       # empty the uploader so it cannot be indexed twice by accident
            except Exception as err:
                st.session_state.kb_flash = (False, f"Failed to index file: {err}")
        st.rerun()

    st.divider()
    st.subheader("🎯 Search Scope")
    try:
        listed_sources = list_sources()
    except Exception as err:
        listed_sources = []
        st.warning(f"⚠️ Could not list the indexed files: {err}")
    # A stored pick that is no longer in the index (a file removed, an index rebuilt) would crash the widget.
    st.session_state["focus_sources"] = [s for s in st.session_state.get("focus_sources", []) if s in listed_sources]
    picked_sources = st.multiselect(
        "Files to answer from",
        options=listed_sources,
        default=st.session_state["focus_sources"],
        format_func=lambda path: f"{SOURCE_ICONS.get(kind_of(path), '📄')} {Path(path).name}",
        placeholder="Search all indexed files",
        label_visibility="collapsed",
    )
    st.session_state["focus_sources"] = picked_sources
    if picked_sources:
        st.caption(f"🎯 Focused on **{len(picked_sources)}** selected file(s).")
    else:
        st.caption("🌐 Global Scope: Searching all indexed documents, images, and audio.")

    st.divider()
    with st.expander("⚙️ Advanced Settings", expanded=False):
        st.markdown("<div style='font-size: 0.82rem; font-weight: 600; margin-bottom: 0.35rem; color: #475569;'>Response Engine</div>", unsafe_allow_html=True)
        engine_mode = st.radio(
            "Response Engine",
            options=[ENGINE_LIVE, ENGINE_CANNED],
            index=0,
            label_visibility="collapsed",
            help="Live RAG queries ChromaDB and streams Ollama. Canned demo answers are hand-written text for demos with no model; every one is labelled.",
        )
        if engine_mode == ENGINE_CANNED:
            st.warning("Canned mode: responses are pre-defined benchmarks. Visual queries disabled.")

    st.divider()
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = [new_message("assistant", content=GREETING)]
        st.session_state.feedback_submitted = set()
        st.rerun()

# ---------------------------------------------------------------------------
# Right-Side Main Output Window: Header & Overview
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="top-header-card">
        <div class="main-title">🌌 RAGNova Assistant</div>
        <div class="sub-title">Private offline multimodal intelligence across documents, visual images, and audio recordings — 100% local.</div>
        <div class="header-pill-row">
            <span class="header-pill">🔒 100% Air-Gapped Local</span>
            <span class="header-pill">🧠 Llama 3.2 3B Engine</span>
            <span class="header-pill">📑 PDF & DOCX Parser</span>
            <span class="header-pill">👁️ OpenCLIP Vision</span>
            <span class="header-pill">🎙️ Whisper Speech</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

def clear_focus() -> None:
    # A callback, not code after the button: Streamlit forbids changing a widget's value
    # once it has been drawn in this run, and the picker in the sidebar is drawn first.
    st.session_state["focus_sources"] = []


focus = list(st.session_state.get("focus_sources", []))
if focus:
    banner, clear = st.columns([5, 1])
    banner.info("📌 Answering from **" + ", ".join(Path(s).name for s in focus) + "** only.")
    clear.button("Use everything", key="btn_clear_focus", on_click=clear_focus)

# Initialize conversation history and state
if "messages" not in st.session_state:
    st.session_state.messages = [new_message("assistant", content=GREETING)]

if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = set()

if "tester_name" not in st.session_state:
    st.session_state.tester_name = ""


# Hero Discovery Canvas (Presented on clean conversation state)
if len(st.session_state.messages) <= 1 and not focus:
    st.markdown(
        """
        <div class="hero-canvas">
            <div class="hero-canvas-title">What would you like to explore?</div>
            <div class="hero-canvas-subtitle">Query your offline knowledge base using text, speech audio, or image screenshots with full citation transparency.</div>
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">📄</div>
                    <div class="feature-heading">Document Semantics</div>
                    <div class="feature-desc">Deep vector & lexical retrieval across PDFs, reports, and Word docs with exact page citations.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🖼️</div>
                    <div class="feature-heading">Cross-Modal Vision</div>
                    <div class="feature-desc">Attach visual plaques, screenshots, or diagrams. Searches via OpenCLIP and native OCR text.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🎙️</div>
                    <div class="feature-heading">Spoken Audio Insights</div>
                    <div class="feature-desc">Whisper speech-to-text integration with timestamped audio segments and inline playback.</div>
                </div>
            </div>
            <div class="showcase-label">💡 Recommended Inquiries (Click to run):</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    starters = [
        "How many marks does the prototype carry?",
        "How do I connect to campus Wi-Fi?",
        "What are the library borrowing limits and overdue fines?",
    ]
    for col, starter in zip(st.columns(len(starters)), starters):
        if col.button(starter, key=f"starter_{starter}", use_container_width=True):
            st.session_state["active_prompt_override"] = starter
            st.rerun()


# Display existing messages
for msg_idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg.get("image_note"):
            st.caption(msg["image_note"])
        if msg.get("engine") == "scaffold":
            st.warning(CANNED_BANNER)
        if msg.get("error"):
            st.error(msg["error"])
        if msg.get("warning"):
            st.warning(msg["warning"])

        if msg.get("views"):
            render_views(msg["views"])
        elif msg.get("citations"):
            render_canned_citations(msg["citations"])

        # Human Feedback Form. Not offered for a failure: there is no answer to rate.
        if msg["role"] == "assistant" and msg_idx > 0 and not msg.get("error"):
            fb_key = f"fb_{msg_idx}"
            if fb_key not in st.session_state.feedback_submitted:
                with st.expander("⭐ Rate this answer (Feedback Form)", expanded=False):
                    with st.form(key=f"form_{fb_key}"):
                        f_col1, f_col2 = st.columns([1, 2])
                        with f_col1:
                            rating = st.select_slider("Rating (1-5)", options=[1, 2, 3, 4, 5], value=5)
                            tester = st.text_input("Reviewer / Evaluator", value=st.session_state.tester_name)
                        with f_col2:
                            comment = st.text_input("Feedback notes (optional)", placeholder="How helpful and accurate was this answer?")
                        if st.form_submit_button("Submit Rating"):
                            sources = [v.title for v in msg.get("views", [])] if msg.get("views") else [c.get("source", "") for c in msg.get("citations") or []]
                            user_q = st.session_state.messages[msg_idx - 1]["content"] if msg_idx > 0 else "N/A"
                            entry = FeedbackEntry(
                                query=user_q,
                                answer=msg["content"],
                                rating=rating,
                                sources=sources,
                                comment=comment,
                                tester=tester,
                                model=model_label(msg.get("engine")),
                            )
                            record_feedback(entry)
                            st.session_state.feedback_submitted.add(fb_key)
                            st.session_state.tester_name = tester
                            st.rerun()
            else:
                st.caption("✅ Feedback submitted for this response.")


# ---------------------------------------------------------------------------
# Canned demo answers (opt-in only; retained for demos with no model and for benchmark comparison)
# ---------------------------------------------------------------------------
def process_query(user_query: str) -> tuple[str, list[dict]]:
    """Canned demo answer for `user_query`: (answer_text, citations_list).

    NOT the RAG system. Keyword-matched, hand-written text with hand-written
    citations, kept for demos with no model and as a benchmark comparison.
    The chat calls it only when the user explicitly picks the canned engine,
    and labels every answer produced this way.
    """
    q = user_query.lower()

    # Negative controls: explicitly refuse without hallucinating or claiming false grounding
    if any(k in q for k in ["mess", "lunch", "dinner", "meal", "menu", "refund", "tuition fee", "fee refund"]):
        mock_answer = (
            "I could not find information about that in the provided offline sources (documents, images, or audio recordings). "
            "The indexed knowledge base does not cover hostel mess menus or tuition fee refund procedures. "
            "The system strictly refuses to hallucinate facts absent from the corpus."
        )
        return mock_answer, []

    # 1. Project Evaluation Weighting & Prototype Marks (Gold-standard T1, A1)
    is_proto_marks = (
        ("prototype" in q and any(k in q for k in ["mark", "demo", "percent", "weight", "score", "carry", "viva"]))
        or ("viva" in q and any(k in q for k in ["voce", "mark", "percent", "weight", "person", "eval"]))
        or ("evaluation" in q and any(k in q for k in ["weight", "mark", "scheme", "prototype", "breakdown"]))
        or ("how many marks" in q)
    )
    if is_proto_marks:
        mock_answer = (
            "According to the department notice and presentation timetable, the **working prototype** "
            "demonstrated on evaluation day carries **40% of the total marks** [1]. The written project "
            "report carries **35%**, and the individual **viva voce** carries the remaining **25%** [1][2]. "
            "Every team member must be present in person for the viva."
        )
        fake_citations = [
            {
                "id": 1,
                "modality": "pdf",
                "source": "data/documents/notice.pdf",
                "location": "Page 2",
                "snippet": "The working prototype demonstrated on the day of evaluation will carry forty percent of the total marks...",
            },
            {
                "id": 2,
                "modality": "audio",
                "source": "data/audio/hod_project_announcement.wav",
                "location": "Timestamp 00:08 - 00:22",
                "snippet": "Please remember that the working prototype carries forty percent... viva voce carries twenty-five percent...",
            },
        ]
        return mock_answer, fake_citations

    # 2. Campus Wi-Fi Configuration (Gold-standard T3, I1, M2)
    is_wifi = (
        ("wifi" in q or "wi-fi" in q or "ssid" in q or "ragnova-student" in q)
        or ("wireless" in q and any(k in q for k in ["adapter", "network", "connect", "setup", "setting", "lan"]))
        or ("connect" in q and any(k in q for k in ["campus", "internet", "wireless", "wifi", "wi-fi"]))
    )
    if is_wifi:
        mock_answer = (
            "To connect to campus Wi-Fi, select the SSID **`RAGNOVA-STUDENT`** [1]. Use your institute email "
            "address and the password set during account activation. The network uses WPA2-Enterprise (802.1X PEAP) "
            "with mandatory CA certificate validation (`ragnova.edu`) [2]. "
            "Never select 'Do not validate' for certificates to avoid credential theft attacks. "
            "If your device fails to connect, restart your wireless adapter before visiting the IT help desk."
        )
        fake_citations = [
            {
                "id": 1,
                "modality": "docx",
                "source": "data/documents/it_onboarding.docx",
                "location": "Page 1",
                "snippet": "Wireless internet on campus is available through the network named RAGNOVA-STUDENT...",
            },
            {
                "id": 2,
                "modality": "image",
                "source": "data/images/screenshot_wifi_setup.png",
                "location": "Dialog Window",
                "snippet": "Security Protocol: WPA2-Enterprise (802.1X PEAP), CA Certificate: Use system certificates (Domain: ragnova.edu)",
            },
        ]
        return mock_answer, fake_citations

    # 3. Library Borrowing, Quotas & Overdue Fines (Gold-standard T2, A2)
    is_library = (
        ("library" in q)
        or ("borrow" in q)
        or ("overdue" in q)
        or ("fine" in q and any(k in q for k in ["overdue", "late", "rupee", "library", "return", "cap", "title"]))
        or ("book" in q and any(k in q for k in ["borrow", "return", "quota", "checkout", "overdue", "library", "title", "renew"]))
    )
    if is_library:
        mock_answer = (
            "Undergraduate students can borrow up to **4 books for 14 days** [1][2]. Overdue fines are **Rs 2 per day "
            "per title**, capped at a maximum of **Rs 200** [1][3]. The library is open from 8:00 AM to 10:00 PM on "
            "working days, with an after-hours return drop box beside the ground floor exit [2]."
        )
        fake_citations = [
            {
                "id": 1,
                "modality": "pdf",
                "source": "data/documents/library_hours.pdf",
                "location": "Page 1",
                "snippet": "Undergraduate students may borrow up to four books at a time for a period of fourteen days...",
            },
            {
                "id": 2,
                "modality": "image",
                "source": "data/images/photo_library_desk_sign.png",
                "location": "Desk Sign",
                "snippet": "Circulation Desk: Undergraduate Quota 4 books for 14 days, After-Hours Drop Box at Ground Floor Exit",
            },
            {
                "id": 3,
                "modality": "audio",
                "source": "data/audio/library_orientation_excerpt.wav",
                "location": "Timestamp 00:15 - 00:30",
                "snippet": "Overdue fines are two rupees per day, capped at two hundred rupees per title.",
            },
        ]
        return mock_answer, fake_citations

    # 4. Project Synopsis Submission (Gold-standard T5, M1)
    is_synopsis = (
        ("synopsis" in q)
        or ("submission deadline" in q and any(k in q for k in ["project", "august", "final year"]))
        or ("21st august" in q and "deadline" in q)
    )
    if is_synopsis:
        mock_answer = (
            "The submission deadline for the project synopsis is **21st August** [1]. The document should not exceed "
            "3 pages excluding the cover page and references, and must be submitted as a single PDF via the department "
            "portal [1][2]. Teams must comprise 2 or 3 members."
        )
        fake_citations = [
            {
                "id": 1,
                "modality": "pdf",
                "source": "data/documents/notice.pdf",
                "location": "Page 1",
                "snippet": "The submission deadline for the project synopsis is 21st August. The synopsis document should not exceed three pages...",
            },
            {
                "id": 2,
                "modality": "image",
                "source": "data/images/screenshot_synopsis_portal.png",
                "location": "Upload Portal",
                "snippet": "Submission Deadline: 21st August (Strict deadline), Document format: Single PDF file",
            },
        ]
        return mock_answer, fake_citations

    # 5. RAGNova Architecture & System Pipeline Overview
    is_architecture = (
        ("what is this project" in q)
        or ("what is ragnova" in q)
        or ("tell me about ragnova" in q)
        or ("rag architecture" in q)
        or ("ragnova architecture" in q)
        or ("pipeline architecture" in q)
        or ("vector stores" in q or "chromadb collections" in q)
    )
    if is_architecture:
        mock_answer = (
            "**RAGNova** is an offline multimodal Retrieval-Augmented Generation system designed for campus environments [1]. "
            "It indexes documents (PDF/DOCX), images (screenshots and physical photo plaques via OCR and OpenCLIP), "
            "and audio briefings (via faster-whisper speech transcription) into dual ChromaDB vector collections [1][2]."
        )
        fake_citations = [
            {
                "id": 1,
                "modality": "image",
                "source": "data/images/diagram_rag_architecture.png",
                "location": "System Diagram",
                "snippet": "RAGNova Offline Multimodal Architecture: Documents, Images, and Audio pipelines with dual ChromaDB stores.",
            },
            {
                "id": 2,
                "modality": "pdf",
                "source": "data/documents/notice.pdf",
                "location": "Page 1",
                "snippet": "Department of Computer Science and Engineering (Artificial Intelligence and Machine Learning)...",
            },
        ]
        return mock_answer, fake_citations

    # 6. AIML Research Lab Location Plaque (Gold-standard I4)
    is_lab_location = (
        ("room 302" in q)
        or (
            any(k in q for k in ["ai lab", "aiml lab", "research lab", "computing lab"])
            and any(k in q for k in ["where", "locate", "in-charge", "faculty", "door", "sign", "plaque", "hours", "superintendent", "who heads"])
        )
    )
    if is_lab_location:
        mock_answer = (
            "The AI & Machine Learning Research Laboratory is located in **Academic Block B, Room 302** [1]. "
            "The faculty in-charge is **Dr. S. Rao**. Operating hours are 9:00 AM to 5:00 PM, and a smart card ID badge "
            "is required for entry [1]."
        )
        fake_citations = [
            {
                "id": 1,
                "modality": "image",
                "source": "data/images/photo_lab_door_sign.png",
                "location": "Room 302 Door Plaque",
                "snippet": "AI & Machine Learning Research Laboratory, Location: Academic Block B — Room 302, Faculty In-Charge: Dr. S. Rao",
            },
        ]
        return mock_answer, fake_citations

    # Catch-all for unsupported queries
    mock_answer = (
        f"I could not find sufficient information in the indexed corpus to answer: \"{user_query}\".\n\n"
        "The offline knowledge base contains academic policies, library regulations, IT network setup, "
        "project evaluation guidelines, and campus facilities. Please query one of these indexed topics."
    )
    fake_citations = []
    return mock_answer, fake_citations


# ---------------------------------------------------------------------------
# Multimodal Query Controls (Integrated Dock)
# ---------------------------------------------------------------------------
st.markdown("<div class='multimodal-dock-header'>📎 Multimodal Input Channels (Optional Voice / Image Attachments)</div>", unsafe_allow_html=True)
col_voice, col_img = st.columns([1, 1])

with col_voice:
    with st.expander("🎙️ Spoken / Voice Query", expanded=False):
        st.caption("Record a voice clip to automatically transcribe and search with faster-whisper.")
        voice_clip = st.audio_input("Record question with microphone", key="mic_query_input")
        if voice_clip is not None:
            if st.button("Transcribe & Submit Audio", key="btn_transcribe_audio", use_container_width=True):
                with st.spinner("Transcribing speech with faster-whisper..."):
                    try:
                        transcribed_text = transcribe_audio_bytes(voice_clip.getvalue(), suffix=".wav")
                        if transcribed_text.strip():
                            st.session_state["active_prompt_override"] = transcribed_text.strip()
                            st.rerun()
                        else:
                            st.warning("No intelligible speech detected in audio clip.")
                    except Exception as err:
                        st.error(f"Speech transcription failed: {err}")

query_img_file = None
with col_img:
    with st.expander("🖼️ Visual / Query Image", expanded=False):
        st.caption("Attach an image to execute cross-modal search using OCR and OpenCLIP embeddings.")
        query_img_file = st.file_uploader(
            "Attach query image (searches via OCR + OpenCLIP)",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"query_img_uploader_{st.session_state.query_img_nonce}",
        )
    if query_img_file is not None:
        st.info("📎 Query image attached. It will be analyzed with your next question.")

# Context-specific suggestions when a file is picked
if focus:
    these = "this file" if len(focus) == 1 else "these files"
    suggestions = [
        f"Give me a short summary of {these}.",
        "What are the key points?",
        "List the names, dates and numbers it mentions." if len(focus) == 1
        else "List the names, dates and numbers they mention.",
    ]
    st.markdown("<div class='showcase-label' style='margin-top: 0.6rem;'>🎯 Suggested Scope Queries:</div>", unsafe_allow_html=True)
    for column, suggestion in zip(st.columns(len(suggestions)), suggestions):
        if column.button(suggestion, key=f"suggest_{suggestion}", use_container_width=True):
            st.session_state["active_prompt_override"] = suggestion

# Chat input
user_prompt = st.chat_input("Ask a question across your documents, images, and audio recordings...")

# Check if there is an audio or button override prompt
if st.session_state.get("active_prompt_override"):
    user_prompt = st.session_state.pop("active_prompt_override")


# ---------------------------------------------------------------------------
# Query Execution & Response Streaming
# ---------------------------------------------------------------------------
if user_prompt:
    query_pil = None
    attachments = []
    image_note = None
    if query_img_file is not None:
        if engine_mode == ENGINE_CANNED:
            image_note = "📎 Query image ignored: canned demo mode does not search."
        else:
            try:
                query_pil = Image.open(query_img_file)
                ocr_text = ocr_image(query_pil)
                attachments = [image_attachment(query_img_file.name, ocr_text)]
                image_note = attachment_note(query_img_file.name, ocr_text, ocr_available())
            except Exception as exc:
                query_pil = None
                attachments = []
                image_note = f"⚠️ Could not use the attached image ({exc}); the question was run without it."

    # The last answered exchange, for follow-ups ("tell me more"): (what that turn searched with, its answer).
    history = None
    earlier_attachments = None
    past = st.session_state.messages
    if len(past) >= 2 and past[-1]["role"] == "assistant" and past[-2]["role"] == "user":
        last_answer = past[-1]
        if last_answer.get("engine") == "live" and not last_answer.get("error") \
                and not is_refusal(last_answer["content"]):
            history = [(past[-2].get("search") or past[-2]["content"], last_answer["content"])]
            earlier_attachments = past[-2].get("attachments") or None

    search = search_question(user_prompt, history, attachments, focus or None)
    st.session_state.messages.append(new_message(
        "user", content=user_prompt, image_note=image_note, search=search,
        attachments=attachments or (earlier_attachments if search != user_prompt else None),
    ))
    with st.chat_message("user"):
        st.markdown(user_prompt)
        if image_note:
            st.caption(image_note)

    reply: dict = {}
    with st.chat_message("assistant"):
        if engine_mode == ENGINE_CANNED:
            answer_text, canned_citations = process_query(user_prompt)
            st.markdown(answer_text)
            reply = {"content": answer_text, "citations": canned_citations or None, "engine": "scaffold"}
        else:
            with st.spinner("Retrieving offline multimodal sources & streaming answer..."):
                try:
                    retrieved_chunks, token_stream = stream_answer(
                        user_prompt,
                        top_k=settings.TOP_K,
                        include_images=True,
                        query_image=query_pil,
                        sources=focus or None,
                        attachments=attachments,
                        history=history,
                        earlier_attachments=earlier_attachments,
                    )
                    answer_text = st.write_stream(token_stream)

                    # Check citations for hallucination
                    out_of_range = check_citations(answer_text, retrieved_chunks, user_prompt)
                    warning_msg = None
                    if out_of_range:
                        warning_msg = f"⚠️ Citation Alert: The model referenced source index {sorted(out_of_range)}, which was not in the retrieved context."
                    reply = {
                        "content": answer_text,
                        "views": None if is_refusal(answer_text) else cited_views(
                            citation_views(retrieved_chunks), extract_citation_numbers(answer_text)
                        ),
                        "warning": warning_msg,
                        "engine": "live",
                    }
                except Exception as exc:
                    reply = {
                        "content": "⚠️ The live system could not answer this question. No canned answer was substituted.",
                        "error": f"{type(exc).__name__}: {exc}",
                        "engine": "live",
                    }

    st.session_state.messages.append(new_message("assistant", **reply))
    if query_img_file is not None:
        st.session_state.query_img_nonce += 1
    st.rerun()
