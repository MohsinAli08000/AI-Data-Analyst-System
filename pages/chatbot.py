"""
pages/chatbot.py — Advanced AI Chatbot with OpenAI GPT Integration
Users ask questions about their data in natural language
"""

import os

import streamlit as st
import pandas as pd
from utils.ai_engine import chat_with_data
from utils.data_processor import get_data_summary


STARTER_QUESTIONS = [
    "What are the main trends in this dataset?",
    "Which column has the most missing values?",
    "What is the average of all numeric columns?",
    "Are there any outliers I should be aware of?",
    "Summarize this dataset in simple words.",
    "Which category appears most frequently?",
]


def render():
    st.title("💬 AI Data Chatbot")
    st.caption("Ask any question about your dataset — powered by OpenAI GPT.")

    if st.session_state.df is None:
        st.warning("⚠️ No dataset loaded. Please go to **Home & Upload** first.")
        return

    df = st.session_state.df

    # ── API Key ───────────────────────────────────────────────────────────────
    api_key = _get_api_key()
    if not api_key:
        api_key = st.text_input(
            "🔑 OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Used only in this session, never stored.",
        )
        if api_key:
            st.session_state["openai_key"] = api_key
        else:
            st.info("Enter your OpenAI API key above to start chatting.")
            return

    # ── Chat History Display ──────────────────────────────────────────────────
    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # ── Starter Question Chips ────────────────────────────────────────────────
    if not st.session_state.chat_history:
        st.subheader("💡 Quick Questions")
        cols = st.columns(3)
        for i, q in enumerate(STARTER_QUESTIONS):
            with cols[i % 3]:
                if st.button(q, key=f"sq_{i}", use_container_width=True):
                    _send_message(q, df, api_key)
                    st.rerun()

    # ── User Input ────────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask a question about your data…")
    if user_input:
        _send_message(user_input, df, api_key)
        st.rerun()

    # ── Controls ──────────────────────────────────────────────────────────────
    if st.session_state.chat_history:
        col_l, col_r = st.columns([3, 1])
        with col_r:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

    # ── Navigation ────────────────────────────────────────────────────────────
    st.divider()
    if st.button("➡️ Next: PDF Report", use_container_width=True):
        st.session_state.page_nav = "📄 PDF Report"
        st.experimental_rerun()


def _get_api_key() -> str:
    """Load the API key from session state, Streamlit secrets, or the environment."""
    api_key = st.session_state.get("openai_key", "")
    if api_key:
        return api_key

    try:
        api_key = st.secrets.get("OPENAI_API_KEY", "")
    except FileNotFoundError:
        api_key = ""

    return api_key or os.getenv("OPENAI_API_KEY", "")


def _send_message(user_msg: str, df: pd.DataFrame, api_key: str):
    """Append user message, call AI, append assistant reply."""
    st.session_state.chat_history.append({"role": "user", "content": user_msg})

    with st.spinner("🤔 Thinking…"):
        response = chat_with_data(
            question=user_msg,
            df=df,
            history=st.session_state.chat_history[:-1],   # exclude current msg
            api_key=api_key,
        )

    if response.get("error"):
        reply = f"❌ Error: {response['error']}"
    else:
        reply = response["answer"]

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
