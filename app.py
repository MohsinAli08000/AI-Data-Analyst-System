"""
AI Powered Automated Data Analyst System
=========================================
University of Sindh, Jamshoro — Final Year Project 2026
Department of Software Engineering
Students: Mohsin Ali (2K23/SWEE/36) | Sammar Abbas (2K23/SWEE/69)
Supervisor: Engr. Noorulain | Co-Supervisor: Sir Amir Mal
"""

import streamlit as st

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Data Analyst System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State Initialization ──────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "filename" not in st.session_state:
    st.session_state.filename = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ai_insights" not in st.session_state:
    st.session_state.ai_insights = None
if "report_generated" not in st.session_state:
    st.session_state.report_generated = False

# ── Sidebar Navigation ────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
st.sidebar.title("🤖 AI Data Analyst")
st.sidebar.caption("University of Sindh — FYP 2026")
st.sidebar.divider()

pages = {
    "🏠 Home & Upload":      "home",
    "📊 Dashboard & Charts":  "dashboard",
    "🧠 AI Insights":         "insights",
    "💬 AI Chatbot":          "chatbot",
    "📄 PDF Report":          "report",
}

nav_labels = list(pages.keys())
selected = st.sidebar.radio(
    "Navigation",
    nav_labels,
    label_visibility="collapsed",
    key="page_nav",
)
page_key = pages[selected]

# Dataset status badge in sidebar
st.sidebar.divider()
if st.session_state.df is not None:
    st.sidebar.success(f"✅ Dataset: **{st.session_state.filename}**")
    rows, cols = st.session_state.df.shape
    st.sidebar.info(f"📐 {rows:,} rows × {cols} columns")
else:
    st.sidebar.warning("⚠️ No dataset loaded yet")

st.sidebar.divider()
st.sidebar.caption("© 2026 Mohsin Ali & Sammar Abbas\nDept. of Software Engineering, USINDH")

# ── Page Router ───────────────────────────────────────────────────────────────
if page_key == "home":
    from pages.home import render
    render()
elif page_key == "dashboard":
    from pages.dashboard import render
    render()
elif page_key == "insights":
    from pages.insights import render
    render()
elif page_key == "chatbot":
    from pages.chatbot import render
    render()
elif page_key == "report":
    from pages.report import render
    render()
