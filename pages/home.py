"""
pages/home.py — Home & Multi-File Upload Page
Handles CSV / Excel uploads, data preview, cleaning summary
"""

import streamlit as st
import pandas as pd
import io
from utils.data_processor import (
    load_dataframe,
    clean_dataframe,
    get_data_summary,
    analyze_dataframe_issues,
    get_unnamed_column_suggestions,
)


def render():
    # ── Header ────────────────────────────────────────────────────────────────
    st.title("🤖 AI Powered Automated Data Analyst System")
    st.markdown(
        "> **Upload your dataset → AI analyzes, cleans, visualizes, and explains everything automatically.**"
    )
    st.divider()

    col_upload, col_info = st.columns([2, 1])

    # ── Upload Section ────────────────────────────────────────────────────────
    with col_upload:
        st.subheader("📁 Upload Dataset(s)")
        uploaded_files = st.file_uploader(
            "Upload one or more CSV / Excel files",
            type=["csv", "xlsx", "xls"],
            accept_multiple_files=True,
            help="Supports .csv, .xlsx, .xls — multiple files allowed",
        )

        if uploaded_files:
            # File selector when multiple uploaded
            if len(uploaded_files) > 1:
                names = [f.name for f in uploaded_files]
                chosen_name = st.selectbox("Select active dataset:", names)
                chosen_file = next(f for f in uploaded_files if f.name == chosen_name)
            else:
                chosen_file = uploaded_files[0]

            raw_df = None
            try:
                raw_df = load_dataframe(chosen_file)
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")
                return

            if (
                st.session_state.get("last_uploaded_filename") != chosen_file.name
                or "cleaning_log" not in st.session_state
            ):
                for key in [
                    "remove_duplicates_choice",
                    "numeric_imputation_choice",
                    "categorical_imputation_choice",
                    "continue_dashboard",
                    "cleaning_log",
                ]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.last_uploaded_filename = chosen_file.name

            st.session_state.cleaning_log = []
            unnamed_suggestions = get_unnamed_column_suggestions(raw_df)
            issues = analyze_dataframe_issues(raw_df)
            duplicate_count = issues["duplicate_count"]
            missing_total = issues["missing_total"]

            if unnamed_suggestions:
                with st.expander("⚠️ Unnamed columns detected", expanded=True):
                    st.write(
                        "This dataset contains unnamed columns. You can remove them if they are not useful, "
                        "or keep them and let the system assign a smart name."
                    )
                    for col, suggestion in unnamed_suggestions.items():
                        sample_values = raw_df[col].dropna().astype(str).head(5).tolist()
                        st.write(f"- **{col}** → suggested name: `{suggestion}`")
                        if sample_values:
                            st.caption(f"Sample values: {sample_values}")
                        else:
                            st.caption("Sample values: all missing / blank")

                    remove_unnamed = st.checkbox(
                        "Remove unnamed columns if they are not useful",
                        value=False,
                        key="remove_unnamed_choice",
                    )
            else:
                remove_unnamed = False

            with st.spinner("🔄 Preparing data-cleaning options…"):
                st.subheader("🧹 Review cleaning options before applying them")
                st.markdown(
                    f"- Duplicate rows detected: **{duplicate_count}**\n"
                    f"- Total missing values: **{missing_total}**"
                )

                remove_duplicates = False
                if duplicate_count > 0:
                    remove_duplicates = st.radio(
                        "Remove duplicate rows before cleaning?",
                        ["No, keep duplicates", "Yes, remove duplicates"],
                        index=0,
                        key="remove_duplicates_choice",
                    ) == "Yes, remove duplicates"
                else:
                    st.success("No duplicate rows detected.")

                if missing_total > 0:
                    st.markdown("**Missing value handling**")
                    numeric_imputation = st.selectbox(
                        "Numeric missing-value strategy",
                        ["Auto", "Mean", "Median", "Mode", "None"],
                        index=0,
                        key="numeric_imputation_choice",
                    )
                    categorical_imputation = st.selectbox(
                        "Categorical missing-value strategy",
                        ["Mode", "Unknown", "None"],
                        index=0,
                        key="categorical_imputation_choice",
                    )
                    st.caption("Choose 'None' if you do not want missing values filled automatically.")
                else:
                    numeric_imputation = "Auto"
                    categorical_imputation = "Mode"
                    st.success("No missing values detected.")

                if st.button("🧹 Apply cleaning options", use_container_width=True):
                    try:
                        cleaned_df, cleaning_log = clean_dataframe(
                            raw_df.copy(),
                            remove_duplicates=remove_duplicates,
                            numeric_imputation=numeric_imputation.lower(),
                            categorical_imputation=categorical_imputation.lower(),
                            remove_unnamed_columns=remove_unnamed,
                        )
                        st.session_state.df = cleaned_df
                        st.session_state.filename = chosen_file.name
                        st.session_state.ai_insights = None
                        st.session_state.report_generated = False
                        st.session_state.cleaning_log = cleaning_log

                        st.success(f"✅ **{chosen_file.name}** loaded and cleaned successfully!")

                        if st.session_state.get("cleaning_log"):
                            with st.expander("🧹 Auto-Cleaning Summary", expanded=True):
                                for item in st.session_state.cleaning_log:
                                    st.write(f"• {item}")

                        # ── User Analysis Goals ──────────────────────────────────────────────
                        st.divider()
                        st.subheader("🎯 Tell Us About Your Analysis Goals")
                        st.markdown("Help us provide better insights by sharing what you want to achieve with this data.")

                        # Analysis objectives
                        analysis_help = st.multiselect(
                            "What kind of help do you need from this data?",
                            [
                                "📊 Data Visualization & Charts",
                                "🔍 Find Patterns & Trends",
                                "📈 Performance Analysis",
                                "🎯 Identify Key Insights",
                                "⚖️ Compare Categories/Groups",
                                "📉 Detect Anomalies/Outliers",
                                "🔗 Understand Relationships",
                                "📋 Generate Reports",
                                "🤖 AI-Powered Recommendations",
                                "❓ Answer Specific Questions",
                                "🔮 Predictive Analysis",
                                "📊 Custom Analysis"
                            ],
                            help="Select all that apply. This helps the AI focus on what matters most to you."
                        )

                        # Column selection
                        st.markdown("**Which columns interest you most?**")
                        all_columns = list(cleaned_df.columns)
                        
                        col_selection = st.radio(
                            "Column Selection",
                            ["All Columns", "Select Specific Columns"],
                            index=0,
                            help="Choose 'All Columns' to analyze everything, or select specific columns for focused analysis."
                        )
                        
                        selected_columns = all_columns
                        if col_selection == "Select Specific Columns":
                            selected_columns = st.multiselect(
                                "Choose columns to focus on:",
                                all_columns,
                                default=all_columns[:min(5, len(all_columns))],  # Default to first 5 or all if less
                                help="Select the columns most relevant to your analysis goals."
                            )
                            
                            if not selected_columns:
                                st.warning("⚠️ Please select at least one column.")
                                selected_columns = all_columns

                        # Store user preferences
                        st.session_state.analysis_goals = analysis_help
                        st.session_state.selected_columns = selected_columns
                        st.session_state.column_selection_mode = col_selection

                        # Show summary of selections
                        with st.expander("📋 Your Analysis Preferences", expanded=True):
                            st.markdown("**Analysis Goals:**")
                            if analysis_help:
                                for goal in analysis_help:
                                    st.write(f"• {goal}")
                            else:
                                st.write("• General data exploration")
                            
                            st.markdown(f"**Column Focus:** {col_selection}")
                            if col_selection == "Select Specific Columns":
                                st.write(f"Selected {len(selected_columns)} columns: {', '.join(selected_columns)}")
                            else:
                                st.write(f"All {len(all_columns)} columns will be analyzed")

                        if st.button(
                            "➡️ Continue to Dashboard",
                            use_container_width=True,
                            key="continue_dashboard",
                        ):
                            st.session_state.page_nav = "📊 Dashboard & Charts"
                            st.experimental_rerun()

                    except Exception as e:
                        st.error(f"❌ Error cleaning data: {e}")
                        return

    # ── Info Box ──────────────────────────────────────────────────────────────
    with col_info:
        st.subheader("ℹ️ How It Works")
        st.markdown(
            """
**Step 1 — Upload**  
Upload any CSV or Excel file.

**Step 2 — Auto-Processing**  
AI cleans, detects types, handles missing values.

**Step 3 — Explore**  
Go to Dashboard → view smart charts.

**Step 4 — Ask AI**  
Use the Chatbot to ask questions.

**Step 5 — Download**  
Generate a full PDF report.
"""
        )

    # ── Dataset Preview ───────────────────────────────────────────────────────
    if st.session_state.df is not None:
        df = st.session_state.df
        st.divider()
        st.subheader("🔍 Dataset Preview")

        summary = get_data_summary(df)

        # KPI Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rows", f"{summary['rows']:,}")
        m2.metric("Columns", summary['columns'])
        m3.metric("Numeric Cols", summary['numeric_cols'])
        m4.metric("Missing Values", summary['missing_total'])

        # Preview table
        rows_to_show = st.slider("Rows to preview", 5, min(100, len(df)), 10)
        st.dataframe(df.head(rows_to_show), use_container_width=True)

        # Column types breakdown
        with st.expander("📋 Column Details"):
            col_info_df = pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes.astype(str).values,
                "Non-Null": df.notnull().sum().values,
                "Null": df.isnull().sum().values,
                "Unique": df.nunique().values,
            })
            st.dataframe(col_info_df, use_container_width=True)

        # Descriptive stats
        with st.expander("📈 Descriptive Statistics"):
            st.dataframe(df.describe(include="all").T, use_container_width=True)

        st.divider()
        st.info("👈 Use the sidebar to navigate to **Dashboard**, **AI Insights**, **Chatbot**, or **PDF Report**.")

    else:
        st.divider()
        # Feature cards
        st.subheader("✨ Features")
        c1, c2, c3, c4 = st.columns(4)
        c1.info("📤 **Multi-File Upload**\nCSV & Excel support")
        c2.info("📊 **Smart Charts**\nAI picks the best graphs")
        c3.info("🧠 **AI Insights**\nOpenAI-powered analysis")
        c4.info("📄 **PDF Report**\nOne-click professional report")
