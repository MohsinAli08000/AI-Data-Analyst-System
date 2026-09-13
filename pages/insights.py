"""
pages/insights.py — AI Insights Page
Sends dataset summary to OpenAI GPT and returns detailed analysis
"""

import streamlit as st
import pandas as pd
from utils.ai_engine import generate_insights
from utils.data_processor import get_data_summary
uploaded_file = st.file_uploader("Upload your dataset", type=["csv"])


def render():
    st.title("🧠 AI-Powered Data Insights")
    st.caption("GPT analyzes your dataset and generates a comprehensive professional report.")
    uploaded_file = st.file_uploader(
    "Upload your dataset (CSV or Excel)",
    type=["csv", "xlsx"]
)

    if st.session_state.df is None:
        st.warning("⚠️ No dataset loaded. Please go to **Home & Upload** first.")
        return

    df = st.session_state.df
    summary = get_data_summary(df)

    # ── Dataset Summary Card ──────────────────────────────────────────────────
    with st.expander("📋 Dataset Summary (sent to AI)", expanded=False):
        st.json(summary)

    # ── Generate Insights ─────────────────────────────────────────────────────
    api_key = st.session_state.get("openai_key", "")

    if not api_key:
        st.info("🔑 Enter your OpenAI API key in the field below to enable AI insights.")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Your key is used only in this session and never stored.",
        )
        if api_key:
            st.session_state["openai_key"] = api_key

    if api_key:
        if st.button("🚀 Generate AI Insights", use_container_width=True, type="primary"):
            with st.spinner("🤖 AI is analyzing your dataset…"):
                result = generate_insights(df, api_key)

            if result.get("error"):
                st.error(f"❌ {result['error']}")
            else:
                st.session_state.ai_insights = result["insights"]
                st.session_state.report_generated = False
                st.success("✅ Insights generated successfully!")

    # ── Display Insights ──────────────────────────────────────────────────────
    if st.session_state.ai_insights:
        st.divider()
        st.subheader("📝 AI Analysis Report")

        insights_text = st.session_state.ai_insights

        # Split by section headers for nicer display
        sections = insights_text.split("\n\n")
        for section in sections:
            if section.strip():
                if section.strip().startswith("#"):
                    st.markdown(section)
                else:
                    st.markdown(section)

        st.divider()

        # Download insights as text
        st.download_button(
            "⬇️ Download Insights (TXT)",
            data=insights_text,
            file_name="ai_insights.txt",
            mime="text/plain",
            use_container_width=True,
        )

        st.info("💡 Go to **PDF Report** to bundle all insights into a downloadable PDF.")

    # ── Navigation ────────────────────────────────────────────────────────────
    st.divider()
    if st.button("➡️ Next: AI Chatbot", use_container_width=True):
        st.session_state.page_nav = "💬 AI Chatbot"
        st.experimental_rerun()
