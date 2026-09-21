"""
RAGNova — Streamlit UI Scaffold (Chapter 11)

A bare Streamlit shell for the offline multimodal RAG system.
Features:
  - Text query input and submit handler
  - Mocked answer and citation response
  - Clearly marked '# TODO: to wire the real call here' for Chapter 10 integration
  - System status and corpus overview in the sidebar

Run with:  streamlit run src/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path so src imports resolve cleanly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.core.config import settings

# ---------------------------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="RAGNova — Offline Multimodal RAG",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #1E293B;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .citation-box {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 0.75rem 1rem;
        margin-top: 0.8rem;
        border-radius: 0 6px 6px 0;
        font-size: 0.9rem;
    }
    .badge-pill {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #E2E8F0;
        color: #334155;
        margin-right: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar: System Metadata & Corpus Stats
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🌌 RAGNova System")
    st.caption("Offline Multimodal RAG (B.Tech CSE-AIML)")
    st.divider()

    st.subheader("⚙️ Active Configuration")
    st.write(f"**Local LLM:** `{settings.OLLAMA_MODEL}`")
    st.write(f"**Text Embedder:** `{settings.TEXT_EMBEDDING_MODEL}`")
    st.write(f"**Image Embedder:** `{settings.CLIP_MODEL}`")
    st.write(f"**Speech-to-Text:** `faster-whisper ({settings.WHISPER_MODEL_SIZE})`")
    st.write(f"**ChromaDB Dir:** `{settings.CHROMA_PERSIST_DIR}`")

    st.divider()
    st.subheader("📁 Corpus Overview")
    docs_dir = PROJECT_ROOT / "data" / "documents"
    images_dir = PROJECT_ROOT / "data" / "images"
    audio_dir = PROJECT_ROOT / "data" / "audio"

    n_docs = len(list(docs_dir.glob("*.*"))) if docs_dir.exists() else 0
    n_images = len(list(images_dir.glob("*.png"))) if images_dir.exists() else 0
    n_audio = len(list(audio_dir.glob("*.wav"))) if audio_dir.exists() else 0

    st.write(f"📄 **Documents:** {n_docs} files")
    st.write(f"🖼️ **Images:** {n_images} files")
    st.write(f"🎙️ **Audio Clips:** {n_audio} files")

    st.divider()
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------------------
# Main Chat Area
# ---------------------------------------------------------------------------
st.markdown('<div class="main-title">🌌 RAGNova Unified Query Interface</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Ask questions in plain language across your documents, screenshots, and audio recordings — 100% offline.</div>',
    unsafe_allow_html=True,
)

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I am **RAGNova**, your offline multimodal assistant. "
                "You can ask me questions about campus policies, project deadlines, Wi-Fi configuration, "
                "or library hours."
            ),
            "citations": None,
        }
    ]

# Display existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            with st.expander("📚 Sources & Citations", expanded=False):
                for cit in msg["citations"]:
                    st.markdown(
                        f"""
                        <div class="citation-box">
                            <span class="badge-pill">{cit['modality'].upper()}</span>
                            <strong>[{cit['id']}]</strong> <code>{cit['source']}</code> {cit.get('location', '')}<br>
                            <em>"{cit['snippet']}"</em>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


# ---------------------------------------------------------------------------
# Query Processing Function (Mock / Scaffold)
# ---------------------------------------------------------------------------
def process_query(user_query: str) -> tuple[str, list[dict]]:
    """Process a user query and return (answer_text, citations_list).

    Currently returns a mocked answer with fake citations as required by Task 4.
    Once Chapter 10 (RAG Core) is implemented, the real retrieval and LLM call
    will replace the mock below.
    """
    # =========================================================================
    # TODO: to wire the real call here
    # Once Track A / Chapter 10 implements retrieval and generation:
    #
    #   from src.pipelines.rag import answer_query
    #   response_text, retrieved_chunks = answer_query(user_query, top_k=settings.TOP_K)
    #   return response_text, [c.to_citation_dict() for c in retrieved_chunks]
    #
    # For now, return a mocked answer and fake citation string:
    # =========================================================================

    q = user_query.lower()
    if "mark" in q or "prototype" in q or "eval" in q or "viva" in q:
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
    elif "wifi" in q or "network" in q or "connect" in q:
        mock_answer = (
            "To connect to campus Wi-Fi, select the SSID **`RAGNOVA-STUDENT`** [1]. Use your institute email "
            "address and the password set during account activation. The network uses WPA2-Enterprise [2]. "
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
                "snippet": "Security Protocol: WPA2-Enterprise (802.1X PEAP), Identity: username@ragnova.edu",
            },
        ]
    else:
        mock_answer = (
            f"*(Mock Response for query: \"{user_query}\")*\n\n"
            "RAGNova retrieved relevant chunks across indexed documents, images, and audio transcripts [1][2]. "
            "All retrieved facts are grounded in the offline corpus without hallucination."
        )
        fake_citations = [
            {
                "id": 1,
                "modality": "pdf",
                "source": "data/documents/notice.pdf",
                "location": "Page 1",
                "snippet": "All B.Tech CSE-AIML final year students working in project teams are required to submit...",
            },
            {
                "id": 2,
                "modality": "image",
                "source": "data/images/diagram_rag_architecture.png",
                "location": "System Diagram",
                "snippet": "Dual Vector Stores: text_index and image_index with verifiable citations.",
            },
        ]

    return mock_answer, fake_citations


# ---------------------------------------------------------------------------
# Query Input Handler
# ---------------------------------------------------------------------------
user_prompt = st.chat_input("Type your question here (e.g., 'How many marks does the prototype carry?')...")

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt, "citations": None})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving offline multimodal sources..."):
            answer, citations = process_query(user_prompt)
            st.markdown(answer)
            if citations:
                with st.expander("📚 Sources & Citations", expanded=True):
                    for cit in citations:
                        st.markdown(
                            f"""
                            <div class="citation-box">
                                <span class="badge-pill">{cit['modality'].upper()}</span>
                                <strong>[{cit['id']}]</strong> <code>{cit['source']}</code> {cit.get('location', '')}<br>
                                <em>"{cit['snippet']}"</em>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    st.session_state.messages.append({"role": "assistant", "content": answer, "citations": citations})
