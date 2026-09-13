"""
utils/ai_engine.py — OpenAI GPT Integration
Handles AI Insights generation and Chatbot Q&A about the dataset
"""

import json
import re
from typing import Dict, Any, List
import pandas as pd
from utils.data_processor import get_data_summary

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ── System Prompt Template ────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert Data Analyst AI assistant.
You have been given a summary of a dataset. Your job is to analyze it and produce clear,
professional, and actionable insights suitable for a university project report.
Always be concise, structured, and use Markdown headings and bullet points.
Do NOT make up data — only use what is provided to you."""

CHATBOT_SYSTEM = """You are a helpful Data Analyst AI chatbot.
You have been given a summary of a dataset the user uploaded.
Answer the user's questions clearly and helpfully based ONLY on the provided dataset summary.
If you cannot answer from the data provided, say so honestly.
Keep answers concise and professional."""


# ── Insights ──────────────────────────────────────────────────────────────────

def generate_insights(df: pd.DataFrame, api_key: str) -> Dict[str, Any]:
    """
    Send dataset summary to OpenAI GPT and return detailed analysis.
    Returns {"insights": str} or {"error": str}
    """
    if not OPENAI_AVAILABLE:
        return {"error": "openai package is not installed. Run: pip install openai"}

    summary = get_data_summary(df)
    prompt = _build_insights_prompt(summary)

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.4,
        )
        insights = response.choices[0].message.content
        return {"insights": insights}

    except Exception as e:
        return {"error": str(e)}


def _build_insights_prompt(summary: dict) -> str:
    summary_json = json.dumps(summary, indent=2, default=str)
    return f"""Analyze the following dataset summary and provide a comprehensive data analysis report.

## Dataset Summary:
{summary_json}

## Please provide:
1. **Executive Summary** — 2-3 sentence overview
2. **Key Statistics** — notable numeric findings
3. **Data Quality Assessment** — missing values, outliers, anomalies
4. **Top Patterns & Trends** — what stands out
5. **Category Distribution** — insights on categorical columns
6. **Recommendations** — actionable next steps for analysis
7. **Conclusion** — brief closing statement

Use proper Markdown formatting with headers and bullet points.
"""


# ── Chatbot ───────────────────────────────────────────────────────────────────

def chat_with_data(
    question: str,
    df: pd.DataFrame,
    history: List[Dict[str, str]],
    api_key: str,
) -> Dict[str, Any]:
    """
    Answer a natural language question about the dataset using GPT.
    Returns {"answer": str} or {"error": str}
    """
    if not OPENAI_AVAILABLE:
        return {"error": "openai package is not installed. Run: pip install openai"}

    summary = get_data_summary(df)
    summary_str = json.dumps(summary, indent=2, default=str)

    # Build message history (keep last 6 turns to save tokens)
    messages = [{"role": "system", "content": CHATBOT_SYSTEM + f"\n\nDataset Summary:\n{summary_str}"}]
    for turn in history[-6:]:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": question})

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=600,
            temperature=0.5,
        )
        answer = response.choices[0].message.content
        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}
