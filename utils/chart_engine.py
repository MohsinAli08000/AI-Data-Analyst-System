"""
utils/chart_engine.py — Smart Auto Chart Selection Engine
AI logic decides the best chart types based on column data types and cardinality
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from typing import List, Dict, Any, Optional
import io


# ── Chart Suggestion Logic ────────────────────────────────────────────────────

def suggest_charts(df: pd.DataFrame, selected_columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Analyze DataFrame columns and suggest the best chart types automatically.
    If selected_columns is provided, only use those columns for suggestions.
    Returns a list of chart specification dicts.
    """
    if selected_columns:
        df = df[selected_columns]
    
    suggestions = []
    num_cols  = df.select_dtypes("number").columns.tolist()
    cat_cols  = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime"]).columns.tolist()

    # 1. Correlation Heatmap — if 3+ numeric columns
    if len(num_cols) >= 3:
        suggestions.append({
            "type":   "heatmap",
            "title":  "Correlation Heatmap",
            "reason": "Shows relationships between all numeric columns",
            "cols":   num_cols,
        })

    # 2. Histogram — first numeric column (distribution)
    if num_cols:
        suggestions.append({
            "type":   "histogram",
            "title":  f"Distribution of {num_cols[0]}",
            "reason": f"Reveals the spread and shape of {num_cols[0]}",
            "x":      num_cols[0],
        })

    # 3. Bar Chart — categorical column with manageable cardinality vs numeric
    for cat in cat_cols:
        card = df[cat].nunique()
        if 2 <= card <= 20 and num_cols:
            suggestions.append({
                "type":   "bar",
                "title":  f"{num_cols[0]} by {cat}",
                "reason": f"Compares {num_cols[0]} across {card} {cat} categories",
                "x":      cat,
                "y":      num_cols[0],
            })
            break

    # 4. Pie Chart — low-cardinality categorical column
    for cat in cat_cols:
        if 2 <= df[cat].nunique() <= 8:
            suggestions.append({
                "type":   "pie",
                "title":  f"Share of {cat}",
                "reason": f"Shows proportional breakdown of {cat}",
                "names":  cat,
                "values": num_cols[0] if num_cols else None,
            })
            break

    # 5. Line Chart — time series if date column present
    if date_cols and num_cols:
        suggestions.append({
            "type":   "line",
            "title":  f"{num_cols[0]} over {date_cols[0]}",
            "reason": "Tracks numeric trend over time",
            "x":      date_cols[0],
            "y":      num_cols[0],
        })

    # 6. Scatter Plot — two numeric columns
    if len(num_cols) >= 2:
        color = cat_cols[0] if cat_cols else None
        suggestions.append({
            "type":   "scatter",
            "title":  f"{num_cols[0]} vs {num_cols[1]}",
            "reason": "Identifies correlation or clusters between two numeric variables",
            "x":      num_cols[0],
            "y":      num_cols[1],
            "color":  color,
        })

    # 7. Box Plot — numeric column grouped by category
    if num_cols and cat_cols:
        cat = cat_cols[0]
        if df[cat].nunique() <= 15:
            suggestions.append({
                "type":   "box",
                "title":  f"{num_cols[0]} distribution by {cat}",
                "reason": "Shows median, spread, and outliers per group",
                "x":      cat,
                "y":      num_cols[0],
            })

    return suggestions[:8]   # cap at 8 suggestions


# ── Render Chart (returns Plotly figure) ──────────────────────────────────────

def render_chart(df: pd.DataFrame, spec: Dict[str, Any]) -> Optional[go.Figure]:
    """
    Render a Plotly figure from a chart spec dict.
    Returns None on failure.
    """
    try:
        t = spec["type"]
        template = "plotly_white"

        if t == "heatmap":
            corr = df[spec["cols"]].corr().round(2)
            fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                            title=spec["title"], template=template)

        elif t == "histogram":
            fig = px.histogram(df, x=spec["x"], nbins=30,
                               title=spec["title"], template=template)

        elif t == "bar":
            agg = df.groupby(spec["x"])[spec["y"]].mean().reset_index().sort_values(spec["y"], ascending=False)
            fig = px.bar(agg, x=spec["x"], y=spec["y"],
                         title=spec["title"], template=template)

        elif t == "pie":
            if spec.get("values"):
                agg = df.groupby(spec["names"])[spec["values"]].sum().reset_index()
                fig = px.pie(agg, names=spec["names"], values=spec["values"],
                             title=spec["title"])
            else:
                counts = df[spec["names"]].value_counts().reset_index()
                counts.columns = [spec["names"], "count"]
                fig = px.pie(counts, names=spec["names"], values="count",
                             title=spec["title"])

        elif t == "line":
            df_sorted = df.sort_values(spec["x"])
            fig = px.line(df_sorted, x=spec["x"], y=spec["y"],
                          title=spec["title"], template=template)

        elif t == "scatter":
            fig = px.scatter(df, x=spec["x"], y=spec["y"],
                             color=spec.get("color"),
                             title=spec["title"], template=template,
                             opacity=0.7)

        elif t == "box":
            fig = px.box(df, x=spec["x"], y=spec["y"],
                         title=spec["title"], template=template)

        else:
            return None

        fig.update_layout(margin=dict(t=40, b=20, l=10, r=10), height=380)
        return fig

    except Exception:
        return None


# ── Render Chart as PNG bytes (for PDF embedding) ─────────────────────────────

def render_chart_as_image(df: pd.DataFrame, spec: Dict[str, Any]) -> Optional[bytes]:
    """
    Return chart as PNG bytes for PDF embedding.
    Requires kaleido: pip install kaleido
    """
    fig = render_chart(df, spec)
    if fig is None:
        return None
    try:
        return fig.to_image(format="png", width=700, height=380, scale=1.5)
    except Exception:
        return None


# ── Filter Columns Helper ─────────────────────────────────────────────────────

def get_filter_columns(df: pd.DataFrame) -> List[str]:
    """Return categorical columns suitable for sidebar filters."""
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    return [c for c in cat_cols if 2 <= df[c].nunique() <= 20]
