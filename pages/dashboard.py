"""
pages/dashboard.py — Interactive Dashboard & Auto Graph Suggestions
AI decides the best chart types based on column data types
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.chart_engine import (
    suggest_charts,
    render_chart,
    get_filter_columns,
)


def render():
    st.title("📊 Interactive Dashboard")
    st.caption("AI-powered auto graph selection — upload a dataset on the Home page first.")

    if st.session_state.df is None:
        st.warning("⚠️ No dataset loaded. Please go to **Home & Upload** first.")
        return

    df = st.session_state.df.copy()
    all_columns = df.columns.tolist()

    # Initialize or reset preferences for the current dataset
    selected_columns = st.session_state.get("selected_columns", all_columns)
    analysis_goals = st.session_state.get("analysis_goals", [])
    column_selection_mode = st.session_state.get("column_selection_mode", "All Columns")

    if column_selection_mode == "Select Specific Columns":
        if not selected_columns or any(col not in all_columns for col in selected_columns):
            selected_columns = all_columns
            column_selection_mode = "All Columns"
            st.session_state.selected_columns = selected_columns
            st.session_state.column_selection_mode = column_selection_mode

    with st.expander("🎯 Tell us what you want from this data", expanded=True):
        st.markdown("Choose your goals and the columns to focus on. This helps the dashboard show the most useful charts and insights.")
        with st.form("analysis_preferences", clear_on_submit=False):
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
                default=analysis_goals,
                help="Select all that apply. This helps the dashboard focus on what matters most to you."
            )

            col_selection = st.radio(
                "Column Selection",
                ["All Columns", "Select Specific Columns"],
                index=0 if column_selection_mode == "All Columns" else 1,
                help="Choose 'All Columns' to analyze everything, or select specific columns for a focused view."
            )

            selected_columns_input = all_columns
            if col_selection == "Select Specific Columns":
                selected_columns_input = st.multiselect(
                    "Choose columns to focus on:",
                    all_columns,
                    default=selected_columns,
                    help="Select the columns most relevant to your current analysis goals."
                )
                if not selected_columns_input:
                    st.warning("⚠️ Please select at least one column.")
                    selected_columns_input = all_columns

            submit_preferences = st.form_submit_button("Save analysis preferences")
            if submit_preferences:
                st.session_state.analysis_goals = analysis_help
                st.session_state.selected_columns = selected_columns_input
                st.session_state.column_selection_mode = col_selection
                selected_columns = selected_columns_input
                analysis_goals = analysis_help
                column_selection_mode = col_selection
                st.success("✅ Analysis preferences updated.")

        st.markdown("**Current selections:**")
        st.write(f"• Goals: {', '.join(analysis_goals) if analysis_goals else 'General data exploration'}")
        st.write(f"• Column selection mode: {column_selection_mode}")
        if column_selection_mode == "Select Specific Columns":
            st.write(f"• Selected columns: {', '.join(selected_columns)}")

    # Filter dataframe to selected columns if specific columns chosen
    if column_selection_mode == "Select Specific Columns" and selected_columns:
        df = df[selected_columns]
        st.info(f"📋 **Focused Analysis**: Working with {len(selected_columns)} selected columns based on your preferences.")
    else:
        st.info("📋 **Comprehensive Analysis**: Analyzing all available columns.")

    # Show analysis goals if specified
    if analysis_goals:
        with st.expander("🎯 Your Analysis Goals", expanded=False):
            st.markdown("Based on your selections, the dashboard will focus on:")
            for goal in analysis_goals:
                st.write(f"• {goal}")

    # ── Dashboard Selector ────────────────────────────────────────────────────
    dashboard_options = [
        "Overview Dashboard",
        "Detailed Analysis Dashboard",
        "Custom Chart Builder",
        "AI-Suggested Charts"
    ]
    selected_dashboard = st.selectbox(
        "Choose Your Dashboard View",
        dashboard_options,
        help="Select the type of dashboard you want to explore. Each view is optimized for different analysis needs."
    )

    # ── Cleaning Summary ──────────────────────────────────────────────────────
    if st.session_state.get("cleaning_log"):
        with st.expander("🧹 Auto-Cleaning Summary", expanded=False):
            for item in st.session_state.cleaning_log:
                st.write(f"• {item}")
        st.divider()

    # ── Sidebar Filters ───────────────────────────────────────────────────────
    st.sidebar.subheader("🔧 Dashboard Filters")
    filter_cols = get_filter_columns(df)

    for col in filter_cols[:3]:           # max 3 quick-filters to keep UI clean
        unique_vals = df[col].dropna().unique().tolist()
        if len(unique_vals) <= 20:
            selected = st.sidebar.multiselect(f"Filter: {col}", unique_vals, default=unique_vals)
            df = df[df[col].isin(selected)]

    st.sidebar.caption(f"Showing {len(df):,} rows after filters")

    if selected_dashboard == "Overview Dashboard":
        render_overview_dashboard(df)
    elif selected_dashboard == "Detailed Analysis Dashboard":
        render_detailed_dashboard(df, selected_columns, column_selection_mode)
    elif selected_dashboard == "Custom Chart Builder":
        render_custom_builder(df)
    elif selected_dashboard == "AI-Suggested Charts":
        render_ai_suggested(df, selected_columns, column_selection_mode)

    st.divider()

    # ── Navigation ────────────────────────────────────────────────────────────
    if st.button("➡️ Next: AI Insights", use_container_width=True):
        st.session_state.page_nav = "🧠 AI Insights"
        st.experimental_rerun()


def render_overview_dashboard(df):
    st.subheader("📈 Overview Dashboard")
    st.markdown("This dashboard provides a quick summary of your data with key visualizations. It's perfect for getting a high-level understanding of your dataset at a glance.")

    num_cols = df.select_dtypes("number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if num_cols:
        # Summary stats
        st.markdown("### Key Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            st.metric("Numeric Columns", len(num_cols))
        with col3:
            st.metric("Categorical Columns", len(cat_cols))

        # Simple bar chart if categorical data
        if cat_cols:
            cat = cat_cols[0]
            if df[cat].nunique() <= 10:
                fig = px.bar(df[cat].value_counts().reset_index(), x=cat, y='count',
                           title=f"Distribution of {cat}",
                           template="plotly_white")
                fig.update_layout(margin=dict(t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f"**Understanding this chart:** This bar chart shows how many records belong to each category in '{cat}'. It helps you see which categories are most common in your data, which can be useful for identifying patterns or focusing on important groups.")

        # Histogram for first numeric
        fig = px.histogram(df, x=num_cols[0], nbins=20,
                         title=f"Distribution of {num_cols[0]}",
                         template="plotly_white")
        fig.update_layout(margin=dict(t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"**Understanding this chart:** This histogram shows the spread of values for '{num_cols[0]}'. The height of each bar tells you how many records fall into that value range. This helps you understand the typical values and whether the data is evenly distributed or concentrated in certain areas.")


def render_detailed_dashboard(df, selected_columns, column_selection_mode):
    st.subheader("🔍 Detailed Analysis Dashboard")
    st.markdown("This dashboard offers in-depth analysis with multiple chart types to explore relationships and trends in your data. Ideal for thorough data investigation.")

    suggestions = suggest_charts(df, selected_columns if column_selection_mode == "Select Specific Columns" else None)
    if suggestions:
        st.markdown("### Comprehensive Data Analysis")
        for spec in suggestions:
            with st.container(border=True):
                st.markdown(f"**{spec['title']}**")
                fig = render_chart(df, spec)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                # Enhanced explanations
                explanation = get_detailed_explanation(spec, df)
                st.markdown(explanation)


def render_custom_builder(df):
    # ── Manual Chart Builder ──────────────────────────────────────────────────
    st.subheader("🛠️ Custom Chart Builder")
    st.markdown("Build your own charts by selecting data columns and chart types. This gives you full control over your visualizations.")

    all_cols = df.columns.tolist()
    num_cols = df.select_dtypes("number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    chart_type = st.selectbox(
        "Chart Type",
        ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart",
         "Histogram", "Box Plot", "Heatmap (Correlation)", "Area Chart"],
    )

    c1, c2, c3 = st.columns(3)
    x_col = c1.selectbox("X Axis", all_cols, key="cx")
    y_col = c2.selectbox("Y Axis", num_cols if num_cols else all_cols, key="cy")
    color_col = c3.selectbox("Color By", ["None"] + cat_cols, key="cc")
    color_col = None if color_col == "None" else color_col

    if st.button("🎨 Generate Chart", use_container_width=True):
        try:
            if chart_type == "Bar Chart":
                fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} by {x_col}")
            elif chart_type == "Line Chart":
                fig = px.line(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} over {x_col}")
            elif chart_type == "Scatter Plot":
                fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} vs {x_col}")
            elif chart_type == "Pie Chart":
                fig = px.pie(df, names=x_col, values=y_col, title=f"{y_col} distribution")
            elif chart_type == "Histogram":
                fig = px.histogram(df, x=x_col, color=color_col, title=f"Distribution of {x_col}")
            elif chart_type == "Box Plot":
                fig = px.box(df, x=color_col, y=y_col, title=f"{y_col} box plot")
            elif chart_type == "Heatmap (Correlation)":
                corr = df[num_cols].corr().round(2)
                fig = px.imshow(corr, text_auto=True, title="Correlation Heatmap", color_continuous_scale="RdBu_r")
            elif chart_type == "Area Chart":
                fig = px.area(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} area over {x_col}")
            else:
                fig = None

            if fig:
                fig.update_layout(template="plotly_white", margin=dict(t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
                # Add explanation for custom chart
                st.markdown(get_custom_chart_explanation(chart_type, x_col, y_col, color_col))
        except Exception as e:
            st.error(f"Could not generate chart: {e}")


def render_ai_suggested(df, selected_columns, column_selection_mode):
    # ── Auto Chart Suggestions ────────────────────────────────────────────────
    suggestions = suggest_charts(df, selected_columns if column_selection_mode == "Select Specific Columns" else None)

    if not suggestions:
        st.info("Not enough varied columns to auto-suggest charts. Try a richer dataset.")
        return

    num_num = len(df.select_dtypes("number").columns)
    num_cat = len(df.select_dtypes(include=["object", "category"]).columns)
    num_date = len(df.select_dtypes(include=["datetime"]).columns)

    st.subheader("📝 Suggested Chart Summary")
    st.markdown(
        f"Your uploaded dataset has **{num_num} numeric**, **{num_cat} categorical" \
        f"{' and **' + str(num_date) + ' date**' if num_date else ''} columns."
    )
    st.markdown("The charts below were selected using dataset characteristics and best visualization practices.")

    for spec in suggestions:
        description = get_enhanced_description(spec)
        st.markdown(f"- **{spec['title']}**: {description}")

    st.divider()

    st.subheader("🔥 AI-Suggested Charts")
    st.caption("The system automatically selects the best chart types for your data.")

    # Render top suggestions in a 2-col grid
    n = len(suggestions)
    for i in range(0, n, 2):
        cols = st.columns(2)
        for j, col_ui in enumerate(cols):
            idx = i + j
            if idx >= n:
                break
            chart_spec = suggestions[idx]
            with col_ui:
                with st.container(border=True):
                    st.markdown(f"**{chart_spec['title']}**")
                    st.caption(f"📌 Reason: {chart_spec['reason']}")
                    fig = render_chart(df, chart_spec)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    # Add detailed explanation
                    explanation = get_detailed_explanation(chart_spec, df)
                    st.markdown(explanation)


def get_enhanced_description(spec):
    if spec["type"] == "heatmap":
        return (
            f"This heatmap shows how strongly different numeric variables in your data are related to each other. "
            "Blue colors indicate positive relationships (when one goes up, the other tends to go up too), while red colors show negative relationships. "
            "This helps you understand which factors influence each other, which is useful for identifying key drivers in your data and making better decisions."
        )
    elif spec["type"] == "histogram":
        return (
            f"This histogram shows the distribution of values for **{spec['x']}**. "
            "It displays how often different value ranges appear in your data. "
            "Understanding this helps you see the typical values, identify unusual patterns, and spot potential data quality issues."
        )
    elif spec["type"] == "bar":
        return (
            f"This bar chart compares **{spec['y']}** across different categories in **{spec['x']}**. "
            "The height of each bar shows the average value for that category. "
            "This visualization makes it easy to see which categories perform best or have the highest/lowest values, helping you prioritize your focus areas."
        )
    elif spec["type"] == "pie":
        if spec.get("values"):
            return (
                f"This pie chart shows how **{spec['values']}** is distributed across categories in **{spec['names']}**. "
                "Each slice represents the proportion of the total that belongs to that category. "
                "It's useful for understanding the relative importance of different groups and seeing how much each contributes to the whole."
            )
        else:
            return (
                f"This pie chart shows the frequency of each category in **{spec['names']}**. "
                "The size of each slice indicates how common that category is in your data. "
                "This helps you understand the composition of your dataset and identify dominant categories."
            )
    elif spec["type"] == "line":
        return (
            f"This line chart shows how **{spec['y']}** changes over time using **{spec['x']}**. "
            "The line connects data points chronologically, making it easy to spot trends, patterns, and changes. "
            "This is particularly useful for tracking performance over time and identifying when things improved or declined."
        )
    elif spec["type"] == "scatter":
        color_part = f", with points colored by **{spec['color']}**" if spec.get("color") else ""
        return (
            f"This scatter plot shows the relationship between **{spec['y']}** and **{spec['x']}**{color_part}. "
            "Each point represents one record from your data. "
            "If points form a pattern (like a line), it indicates a relationship between the variables. "
            "This helps you discover correlations, groups, and outliers that might not be obvious otherwise."
        )
    elif spec["type"] == "box":
        return (
            f"This box plot shows the distribution of **{spec['y']}** for different groups in **{spec['x']}**. "
            "The box shows the middle 50% of values, the line in the box is the median, and whiskers show the range. "
            "Dots outside are outliers. This helps compare how values vary across groups and identify unusual data points."
        )
    else:
        return spec["reason"]


def get_detailed_explanation(spec, df):
    base = get_enhanced_description(spec)
    # Add benefits
    if spec["type"] == "heatmap":
        benefit = " **Benefits:** Helps in feature selection for modeling, understanding multicollinearity, and identifying key relationships for business decisions."
    elif spec["type"] == "histogram":
        benefit = " **Benefits:** Reveals data distribution patterns, helps detect skewness or normality, and identifies potential data cleaning needs."
    elif spec["type"] == "bar":
        benefit = " **Benefits:** Enables quick comparison across categories, highlights top/bottom performers, and supports resource allocation decisions."
    elif spec["type"] == "pie":
        benefit = " **Benefits:** Shows proportional contributions, helps understand market share or composition, and communicates relative importance clearly."
    elif spec["type"] == "line":
        benefit = " **Benefits:** Tracks changes over time, identifies trends and seasonality, and helps forecast future values based on historical patterns."
    elif spec["type"] == "scatter":
        benefit = " **Benefits:** Uncovers hidden relationships, detects clusters or segments, and helps validate assumptions about variable interactions."
    elif spec["type"] == "box":
        benefit = " **Benefits:** Compares distributions across groups, identifies outliers and variability, and supports statistical analysis and quality control."
    else:
        benefit = ""
    
    return base + benefit


def get_custom_chart_explanation(chart_type, x_col, y_col, color_col):
    if chart_type == "Bar Chart":
        return f"**Understanding this chart:** This bar chart shows '{y_col}' for each category in '{x_col}'. The height of each bar represents the value. {'Bars are colored by ' + color_col + ' to show additional grouping.' if color_col else ''} This helps compare values across different groups easily."
    elif chart_type == "Line Chart":
        return f"**Understanding this chart:** This line chart tracks '{y_col}' as '{x_col}' changes. The line shows the trend or progression. {'Different colors represent ' + color_col + ' groups.' if color_col else ''} It's great for seeing how values change over time or sequence."
    elif chart_type == "Scatter Plot":
        return f"**Understanding this chart:** Each point represents a data record, plotting '{y_col}' against '{x_col}'. {'Points are colored by ' + color_col + ' to distinguish groups.' if color_col else ''} Look for patterns like clusters or lines to understand relationships between these variables."
    elif chart_type == "Pie Chart":
        return f"**Understanding this chart:** This pie chart shows how '{y_col}' is distributed across categories in '{x_col}'. Each slice represents a portion of the total. It's useful for seeing what percentage each category contributes."
    elif chart_type == "Histogram":
        return f"**Understanding this chart:** This histogram shows the frequency of values in '{x_col}' across different ranges. {'Grouped by ' + color_col + '.' if color_col else ''} It helps you see the most common values and the overall spread of your data."
    elif chart_type == "Box Plot":
        return f"**Understanding this chart:** This box plot summarizes '{y_col}' distribution. The box shows middle values, whiskers show range, and dots are outliers. {'Grouped by ' + color_col + '.' if color_col else ''} It helps compare variability across groups."
    elif chart_type == "Heatmap (Correlation)":
        return "**Understanding this chart:** This heatmap shows correlations between numeric columns. Values close to 1 or -1 indicate strong relationships. Blue means positive correlation, red means negative. It helps identify which variables move together."
    elif chart_type == "Area Chart":
        return f"**Understanding this chart:** This area chart shows '{y_col}' over '{x_col}' with the area filled. {'Colored by ' + color_col + '.' if color_col else ''} It's similar to a line chart but emphasizes magnitude changes."
    else:
        return "This chart visualizes your selected data to help uncover patterns and insights."
