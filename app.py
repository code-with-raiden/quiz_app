import hashlib
import json
import random
import uuid
from math import comb
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Configuration & Setup
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
QUESTIONS_FILE = BASE_DIR / "questions.json"
QR_DIR = BASE_DIR / "qr_codes"
QUESTIONS_PER_STUDENT = 10

st.set_page_config(
    page_title="Python Assessment Portal",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom responsive CSS
st.markdown(
    """
    <style>
      /* Main container aesthetics */
      .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 720px;
      }
      .q-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 18px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.05);
      }
      .q-badge {
        display: inline-block;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 10px;
      }
      .scenario-box {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 12px;
        font-size: 0.95rem;
        color: #334155;
        line-height: 1.5;
      }
      .question-box {
        font-size: 1.05rem;
        font-weight: 600;
        color: #0f172a;
        line-height: 1.45;
      }
      .meta-info {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 4px;
      }
      .header-card {
        padding: 20px;
        border-radius: 14px;
        color: white;
        text-align: center;
        margin-bottom: 24px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_all_levels():
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        return json.load(f)["levels"]


def build_pool(data, level):
    """
    Hierarchical question pooling:
    - Basic        : Basic pool only (150 questions)
    - Intermediate : Basic + Intermediate (206 questions)
    - Advanced     : Basic + Intermediate + Advanced (286 questions)
    """
    pool = []
    if level == "basic":
        pool = list(data["basic"]["questions"])
    elif level == "intermediate":
        pool = list(data["basic"]["questions"]) + list(data["intermediate"]["questions"])
    elif level == "advanced":
        pool = (
            list(data["basic"]["questions"])
            + list(data["intermediate"]["questions"])
            + list(data["advanced"]["questions"])
        )
    return pool


def pick_questions(pool, seed_value, n=QUESTIONS_PER_STUDENT):
    """Deterministically sample n questions given a numeric seed."""
    rng = random.Random(seed_value)
    return rng.sample(pool, min(n, len(pool)))


# ---------------------------------------------------------------------------
# View: Student Question Paper (Triggered via QR code scan)
# ---------------------------------------------------------------------------
LEVEL_METADATA = {
    "basic": {
        "title": "Basic Level Assessment",
        "sub": "Conditional Statements (if, if-else, elif, nested if)",
        "color": "#10b981",  # Emerald green
        "prefix": "BAS",
    },
    "intermediate": {
        "title": "Intermediate Level Assessment",
        "sub": "Functions, Decorators, Generators (+ Conditionals)",
        "color": "#f59e0b",  # Amber
        "prefix": "INT",
    },
    "advanced": {
        "title": "Advanced Level Assessment",
        "sub": "OOP, Exceptions, Comprehensions, Lambda, Map, Files (+ All)",
        "color": "#ef4444",  # Red
        "prefix": "ADV",
    },
}


def render_student_paper(level_key):
    meta = LEVEL_METADATA[level_key]
    data = load_all_levels()
    pool = build_pool(data, level_key)

    # Manage Paper ID / Seed:
    # If the student scanned the clean QR code (e.g. ?level=basic),
    # we automatically mint a unique paper_id in query params so:
    # 1. Next student scanning the same QR code gets a different paper.
    # 2. This student refreshing their browser keeps the same paper!
    current_paper_id = st.query_params.get("paper_id", None)

    if not current_paper_id:
        current_paper_id = uuid.uuid4().hex[:8].upper()
        st.query_params["paper_id"] = current_paper_id

    # Compute a deterministic integer seed from the unique paper_id
    seed_val = int(hashlib.sha256(current_paper_id.encode("utf-8")).hexdigest(), 16) % (2**32)
    selected_questions = pick_questions(pool, seed_val, QUESTIONS_PER_STUDENT)

    # Header Card
    st.markdown(
        f"""
        <div class="header-card" style="background: {meta['color']};">
            <h2 style="margin: 0; color: #ffffff; font-size: 1.6rem;">{meta['title']}</h2>
            <p style="margin: 6px 0 12px; font-size: 0.95rem; opacity: 0.95;">{meta['sub']}</p>
            <div style="display: inline-block; background: rgba(0,0,0,0.2); padding: 4px 14px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; letter-spacing: 0.5px;">
                PAPER CODE: #{meta['prefix']}-{current_paper_id} &nbsp;|&nbsp; 10 QUESTIONS
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info("📌 **Instructions:** Read both the **Scenario** and **Question** carefully. Write your solutions on your laptop.")

    # Render each question
    for idx, q in enumerate(selected_questions, 1):
        st.markdown(
            f"""
            <div class="q-card">
                <span class="q-badge" style="background: {meta['color']}18; color: {meta['color']}; border: 1px solid {meta['color']}40;">
                    Question {idx} of {QUESTIONS_PER_STUDENT}
                </span>
                <div class="scenario-box" style="border-left-color: {meta['color']};">
                    <strong>📖 Scenario:</strong><br>{q['scenario']}
                </div>
                <div class="question-box">
                    <strong>❓ Task:</strong> {q['question']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # st.markdown("---")
    # col1, col2 = st.columns([2, 1])
    # with col1:
    #     st.caption(f"Paper ID: `{meta['prefix']}-{current_paper_id}` • Seed: `{seed_val}`")
    # with col2:
    #     if st.button("🔄 Generate New Set", use_container_width=True):
    #         st.query_params["paper_id"] = uuid.uuid4().hex[:8].upper()
    #         st.rerun()


# ---------------------------------------------------------------------------
# View: Instructor / Home Page (Shows QR codes & Live Monitoring)
# ---------------------------------------------------------------------------
def render_instructor_home():
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="margin: 0; font-size: 2.1rem; color: #1e293b;">🎓 Python Mock Assessment</h1>
            <p style="color: #64748b; font-size: 1.05rem; margin-top: 6px;">
                Scan a QR code below to receive an instant, anti-cheating 10-question assessment
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    data = load_all_levels()

    basic_pool = build_pool(data, "basic")
    inter_pool = build_pool(data, "intermediate")
    adv_pool = build_pool(data, "advanced")

    st.markdown("### 📱 Scan QR Code to Start")

    col1, col2, col3 = st.columns(3)

    cards = [
        ("basic", col1, basic_pool, LEVEL_METADATA["basic"]),
        ("intermediate", col2, inter_pool, LEVEL_METADATA["intermediate"]),
        ("advanced", col3, adv_pool, LEVEL_METADATA["advanced"]),
    ]

    for key, col, pool, meta in cards:
        with col:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 10px; border-radius: 12px; border: 2px solid {meta['color']}; background: #ffffff;">
                    <strong style="color: {meta['color']}; font-size: 1.05rem;">{meta['title'].split()[0]}</strong>
                    <div style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">{len(pool)} Question Pool</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            qr_file = QR_DIR / f"qr_{key}.png"
            if qr_file.exists():
                st.image(str(qr_file), use_container_width=True)
            else:
                st.warning("QR not generated yet. Run `python make_qr.py`")

            # Direct link button for browser test
            if st.button(f"Open {meta['title'].split()[0]} Test", key=f"btn_{key}", use_container_width=True):
                st.query_params["level"] = key
                st.query_params["paper_id"] = uuid.uuid4().hex[:8].upper()
                st.rerun()

    st.markdown("---")
    st.markdown("### 🛡️ Anti-Cheating & Randomization Architecture")

    st.markdown(
        f"""
        - **No duplicate papers for adjacent students**:
          - **🟢 Basic Level**: Pool of **{len(basic_pool)} questions** $\\rightarrow$ **{comb(len(basic_pool), 10):,}** possible combinations.
          - **🟡 Intermediate Level**: Pool of **{len(inter_pool)} questions** (Basic + Functions + Decorators + Generators) $\\rightarrow$ **{comb(len(inter_pool), 10):,}** combinations.
          - **🔴 Advanced Level**: Pool of **{len(adv_pool)} questions** (All categories) $\\rightarrow$ **{comb(len(adv_pool), 10):,}** combinations.
        - **No Database Storage**: Everything is calculated dynamically on-the-fly when the QR code is scanned.
        - **Accidental Refresh Safe**: Once a student scans the QR, a unique `paper_id` is tied to their test session so they won't lose their paper if their phone screen sleeps or reloads.
        """
    )


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
current_level = st.query_params.get("level", None)

if current_level in LEVEL_METADATA:
    render_student_paper(current_level)
else:
    render_instructor_home()
