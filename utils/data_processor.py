"""
utils/data_processor.py — Data Loading, Cleaning, and Summarization
Handles CSV and Excel files; auto-detects types; cleans missing values
"""

import re
import pandas as pd
import numpy as np
import io
from typing import Tuple, List, Dict, Any


# ── Load ──────────────────────────────────────────────────────────────────────

def load_dataframe(uploaded_file) -> pd.DataFrame:
    """
    Load a CSV or Excel uploaded file into a DataFrame.
    Raises ValueError on unsupported format.
    """
    name = uploaded_file.name.lower()
    content = uploaded_file.read()
    buf = io.BytesIO(content)

    if name.endswith(".csv"):
        # Try common encodings
        for enc in ("utf-8", "latin-1", "cp1252"):
            try:
                buf.seek(0)
                return pd.read_csv(buf, encoding=enc)
            except UnicodeDecodeError:
                continue
        raise ValueError("Could not decode CSV file — try saving it as UTF-8.")

    elif name.endswith((".xlsx", ".xls")):
        engine = "openpyxl" if name.endswith(".xlsx") else "xlrd"
        buf.seek(0)
        return pd.read_excel(buf, engine=engine)

    else:
        raise ValueError(f"Unsupported file type: {name}")


# ── Clean ─────────────────────────────────────────────────────────────────────

def clean_dataframe(
    df: pd.DataFrame,
    remove_duplicates: bool = False,
    numeric_imputation: str = "auto",
    categorical_imputation: str = "mode",
    remove_unnamed_columns: bool = False,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Clean DataFrame based on user preferences.

    Args:
        df: input DataFrame.
        remove_duplicates: remove duplicate rows only if True.
        numeric_imputation: one of ['auto', 'mean', 'median', 'mode', 'none'].
        categorical_imputation: one of ['mode', 'unknown', 'none'].
        remove_unnamed_columns: drop unnamed columns if True; otherwise auto-rename them.
    Returns:
        cleaned DataFrame and a list of log messages.
    """
    log: List[str] = []
    df = df.copy()

    df.columns = [str(c).strip() for c in df.columns]

    if remove_unnamed_columns:
        unnamed_cols = [c for c in df.columns if _is_unnamed_column(c)]
        if unnamed_cols:
            df.drop(columns=unnamed_cols, inplace=True)
            log.append(
                f"Dropped unnamed columns: {', '.join(str(c) for c in unnamed_cols)}."
            )
    else:
        df = _rename_unnamed_columns(df, log)

    dups = int(df.duplicated().sum())
    if dups:
        if remove_duplicates:
            df.drop_duplicates(inplace=True)
            log.append(f"Removed {dups} duplicate rows.")
        else:
            log.append(f"Detected {dups} duplicate rows, left in place as requested.")

    for col in df.columns:
        if df[col].dtype == object:
            cleaned = df[col].astype(str).str.strip()
            cleaned = cleaned.replace({"nan": np.nan, "None": np.nan, "": np.nan})
            
            # Try numeric conversion more aggressively
            numeric = pd.to_numeric(cleaned, errors="coerce")
            non_null_count = cleaned.notna().sum()
            numeric_non_null = numeric.notna().sum()
            
            # If 80%+ of non-null values convert to numeric, convert the column
            if non_null_count > 0 and numeric_non_null / non_null_count >= 0.8:
                df[col] = numeric
                log.append(f"Column '{col}' inferred as numeric and converted automatically.")
            else:
                df[col] = cleaned
        
        # Try date conversion with stronger pattern detection
        if df[col].dtype == object:
            converted = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
            non_null_count = df[col].notna().sum()
            converted_non_null = converted.notna().sum()
            
            # If 50%+ of non-null values are valid dates, convert to datetime
            if non_null_count > 0 and converted_non_null / non_null_count >= 0.5:
                df[col] = converted
                log.append(f"Column '{col}' detected as datetime and converted.")

        if pd.api.types.is_numeric_dtype(df[col]):
            _impute_numeric_column(df, col, numeric_imputation, log)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            _impute_datetime_column(df, col, log)
        else:
            _impute_categorical_column(df, col, categorical_imputation, log)

    if not log:
        log.append("✅ No cleaning required — dataset is already clean.")

    return df, log


def analyze_dataframe_issues(df: pd.DataFrame) -> Dict[str, Any]:
    """Return duplicate and missing-value diagnostics for a raw DataFrame."""
    issues = {
        "duplicate_count": int(df.duplicated().sum()),
        "missing_total": int(df.isna().sum().sum()),
        "missing_by_column": df.isna().sum().to_dict(),
        "numeric_columns": df.select_dtypes("number").columns.tolist(),
        "categorical_columns": df.select_dtypes(include=["object", "category"]).columns.tolist(),
        "datetime_columns": df.select_dtypes(include=["datetime"]).columns.tolist(),
    }
    return issues


def _impute_numeric_column(
    df: pd.DataFrame,
    col: str,
    numeric_imputation: str,
    log: List[str],
) -> None:
    null_count = int(df[col].isna().sum())
    if not null_count:
        return

    non_null = df[col].dropna()
    if non_null.empty:
        log.append(f"Column '{col}' has only missing values; no numeric imputation applied.")
        return

    strategy = numeric_imputation.lower()
    fill_value = None
    method = strategy

    if strategy == "none":
        log.append(f"Column '{col}': {null_count} missing values left unchanged by user choice.")
        return
    elif strategy == "mean":
        fill_value = non_null.mean()
    elif strategy == "median":
        fill_value = non_null.median()
    elif strategy == "mode":
        fill_value = non_null.mode().iloc[0]
    else:
        unique_count = non_null.nunique()
        total_count = len(non_null)
        skewness = float(non_null.skew()) if total_count > 2 else 0.0
        if unique_count <= 5 and unique_count / total_count < 0.2:
            fill_value = non_null.mode().iloc[0]
            method = "mode"
        elif abs(skewness) > 0.7:
            fill_value = non_null.median()
            method = "median"
        else:
            fill_value = non_null.mean()
            method = "mean"

    df[col].fillna(fill_value, inplace=True)
    log.append(
        f"Column '{col}': filled {null_count} missing values with {method} ({fill_value})."
    )


def _impute_datetime_column(df: pd.DataFrame, col: str, log: List[str]) -> None:
    null_count = int(df[col].isna().sum())
    if not null_count:
        return

    non_null = df[col].dropna()
    if non_null.empty:
        log.append(f"Column '{col}' has only missing datetime values; no imputation applied.")
        return

    mode_values = non_null.mode()
    fill_value = mode_values.iloc[0] if len(mode_values) else non_null.median()
    df[col].fillna(fill_value, inplace=True)
    log.append(
        f"Column '{col}': filled {null_count} missing values with mode ({fill_value})."
    )


def _impute_categorical_column(
    df: pd.DataFrame,
    col: str,
    categorical_imputation: str,
    log: List[str],
) -> None:
    null_count = int(df[col].isna().sum())
    if not null_count:
        return

    non_null = df[col].dropna()
    if non_null.empty:
        fill_value = "Unknown" if categorical_imputation != "none" else np.nan
    elif categorical_imputation == "unknown":
        fill_value = "Unknown"
    elif categorical_imputation == "none":
        log.append(f"Column '{col}': {null_count} missing values left unchanged by user choice.")
        return
    else:
        mode_values = non_null.mode()
        fill_value = mode_values.iloc[0] if len(mode_values) else "Unknown"

    df[col].fillna(fill_value, inplace=True)
    log.append(
        f"Column '{col}': filled {null_count} missing values with {categorical_imputation} ('{fill_value}')."
    )


def _looks_like_date(col_name: str) -> bool:
    keywords = ["date", "time", "year", "month", "day", "created", "updated", "timestamp"]
    return any(k in col_name.lower() for k in keywords)


def _is_unnamed_column(col_name: Any) -> bool:
    value = str(col_name).strip()
    return value == "" or value.lower().startswith("unnamed")


def _make_unique_column_name(df: pd.DataFrame, name: str, index: int) -> str:
    candidate = name
    suffix = 1
    while candidate in df.columns:
        candidate = f"{name}_{suffix}"
        suffix += 1
    return candidate


def _infer_unnamed_column_name(series: pd.Series, index: int) -> str:
    non_null = series.dropna().astype(str).str.strip()
    if non_null.empty:
        return f"column_{index + 1}"

    sample = non_null.head(20).str.lower().tolist()
    if all(re.fullmatch(r"\d+(\.\d+)?", v) for v in sample):
        return f"numeric_{index + 1}"

    if all(re.fullmatch(r"\d{4}(-\d{2}){1,2}", v) or re.fullmatch(r"\d{2}/\d{2}/\d{4}", v) for v in sample):
        return f"date_{index + 1}"

    bool_values = {"yes", "no", "true", "false", "y", "n", "0", "1"}
    if all(v in bool_values for v in sample):
        return f"flag_{index + 1}"

    if len(set(sample)) <= 6 and len(sample) > 1:
        return f"category_{index + 1}"

    if any(k in " ".join(sample) for k in ["id", "code", "name", "type", "status", "amount", "price", "qty", "quantity"]):
        keyword = next(
            (k for k in ["id", "code", "name", "type", "status", "amount", "price", "qty", "quantity"] if any(k in v for v in sample)),
            None,
        )
        if keyword:
            return f"{keyword}_{index + 1}"

    return f"column_{index + 1}"


def _rename_unnamed_columns(df: pd.DataFrame, log: List[str]) -> pd.DataFrame:
    for idx, col in enumerate(list(df.columns)):
        if _is_unnamed_column(col):
            suggestion = _infer_unnamed_column_name(df[col], idx)
            new_name = _make_unique_column_name(df, suggestion, idx)
            df.rename(columns={col: new_name}, inplace=True)
            log.append(f"Unnamed column '{col}' renamed to '{new_name}'.")
    return df


def get_unnamed_column_suggestions(df: pd.DataFrame) -> Dict[str, str]:
    suggestions: Dict[str, str] = {}
    for idx, col in enumerate(df.columns):
        if _is_unnamed_column(col):
            suggestions[col] = _infer_unnamed_column_name(df[col], idx)
    return suggestions


# ── Summarize ─────────────────────────────────────────────────────────────────

def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Return a concise summary dict suitable for sending to AI.
    """
    num_cols   = df.select_dtypes("number").columns.tolist()
    cat_cols   = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols  = df.select_dtypes(include=["datetime"]).columns.tolist()

    summary: Dict[str, Any] = {
        "rows":          len(df),
        "columns":       len(df.columns),
        "numeric_cols":  len(num_cols),
        "categorical_cols": len(cat_cols),
        "date_cols":     len(date_cols),
        "missing_total": int(df.isnull().sum().sum()),
        "column_names":  df.columns.tolist(),
        "numeric_columns": num_cols,
        "categorical_columns": cat_cols,
        "date_columns":  date_cols,
        "sample_head":   df.head(3).to_dict(orient="records"),
    }

    # Per-column stats for numeric columns
    stats: Dict[str, Any] = {}
    for col in num_cols[:10]:    # limit to 10 to keep prompt size reasonable
        stats[col] = {
            "min":    round(float(df[col].min()), 4),
            "max":    round(float(df[col].max()), 4),
            "mean":   round(float(df[col].mean()), 4),
            "median": round(float(df[col].median()), 4),
            "std":    round(float(df[col].std()), 4),
        }
    summary["numeric_stats"] = stats

    # Top categories
    cat_freq: Dict[str, Any] = {}
    for col in cat_cols[:5]:
        top = df[col].value_counts().head(5).to_dict()
        cat_freq[col] = {str(k): int(v) for k, v in top.items()}
    summary["top_categories"] = cat_freq

    return summary
