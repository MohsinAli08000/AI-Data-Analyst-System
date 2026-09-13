"""
pages/report.py — PDF Report Generator
Bundles dataset summary, charts, and AI insights into a downloadable PDF
"""

import streamlit as st
import pandas as pd
import io
import base64
from utils.data_processor import get_data_summary
from utils.pdf_generator import generate_pdf_report
from utils.chart_engine import suggest_charts, render_chart_as_image


def render():
    st.title("📄 PDF Report Generator")
    st.caption("Generate a complete professional PDF report — dataset summary, charts, and AI insights.")

    if st.session_state.df is None:
        st.warning("⚠️ No dataset loaded. Please go to **Home & Upload** first.")
        return

    df = st.session_state.df
    filename = st.session_state.filename or "dataset"

    # ── Report Options ────────────────────────────────────────────────────────
    st.subheader("⚙️ Report Settings")
    c1, c2 = st.columns(2)
    include_stats   = c1.checkbox("Include Descriptive Statistics", value=True)
    include_charts  = c1.checkbox("Include Auto-Generated Charts",  value=True)
    include_ai      = c2.checkbox("Include AI Insights",            value=True)
    include_missing = c2.checkbox("Include Missing Values Analysis", value=True)

    report_title = st.text_input(
        "Report Title",
        value=f"Data Analysis Report — {filename}",
    )
    author_name = st.text_input("Author / Student Name", value="Mohsin Ali & Sammar Abbas")
    university   = st.text_input("University", value="University of Sindh, Jamshoro")

    st.divider()

    # ── AI Insights status ────────────────────────────────────────────────────
    if include_ai and not st.session_state.ai_insights:
        st.info(
            "💡 AI Insights are not generated yet. "
            "Go to **🧠 AI Insights** page and click **Generate AI Insights** to include them in the report."
        )

    # ── Generate Button ───────────────────────────────────────────────────────
    if st.button("🚀 Generate PDF Report", use_container_width=True, type="primary"):
        with st.spinner("📄 Building report…"):
            try:
                pdf_bytes = generate_pdf_report(
                    df=df,
                    title=report_title,
                    author=author_name,
                    university=university,
                    filename=filename,
                    include_stats=include_stats,
                    include_charts=include_charts,
                    include_missing=include_missing,
                    ai_insights=st.session_state.ai_insights if include_ai else None,
                )
                st.session_state["pdf_bytes"] = pdf_bytes
                st.session_state.report_generated = True
                st.success("✅ PDF report generated successfully!")
            except Exception as e:
                st.error(f"❌ Error generating report: {e}")

    # ── Download PDF ──────────────────────────────────────────────────────────
    if st.session_state.get("pdf_bytes"):
        st.download_button(
            label="⬇️ Download PDF Report",
            data=st.session_state["pdf_bytes"],
            file_name=f"AI_Data_Report_{filename.replace('.', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )

        # Preview notice
        st.info("📌 Click the button above to download your full PDF report.")
