"""Prompt categorization: objective vs subjective."""

import pandas as pd
from config import (
    OBJECTIVE_KEYWORDS, SUBJECTIVE_KEYWORDS,
    OBJECTIVE_CATEGORIES, SUBJECTIVE_CATEGORIES
)


def classify_prompt(prompt: str) -> str:
    """Keyword-based classifier. Returns 'objective' | 'subjective' | 'ambiguous'."""
    if not isinstance(prompt, str):
        return "ambiguous"
    prompt_lower = prompt.lower()
    has_obj = any(kw.lower() in prompt_lower for kw in OBJECTIVE_KEYWORDS)
    has_subj = any(kw.lower() in prompt_lower for kw in SUBJECTIVE_KEYWORDS)
    if has_obj and not has_subj:
        return "objective"
    if has_subj and not has_obj:
        return "subjective"
    return "ambiguous"


def categorize_battles(df: pd.DataFrame) -> pd.DataFrame:
    """Add 'category' column. Uses Arena tag if present, else keyword fallback."""
    df = df.copy()
    if "category" in df.columns:
        def map_tag(tag):
            if pd.isna(tag):
                return "ambiguous"
            tag_lower = str(tag).lower().strip()
            if tag_lower in {c.lower() for c in SUBJECTIVE_CATEGORIES}:
                return "subjective"
            if tag_lower in {c.lower() for c in OBJECTIVE_CATEGORIES}:
                return "objective"
            return "ambiguous"
        df["category"] = df["category"].apply(map_tag)
    else:
        df["category"] = df["prompt"].apply(classify_prompt)
    return df


def exclude_ambiguous(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows where category == 'ambiguous'."""
    return df[df["category"] != "ambiguous"].copy()


def filter_min_count(df: pd.DataFrame, min_n: int = 500) -> pd.DataFrame:
    """Raise ValueError if either category has fewer than min_n samples."""
    counts = df["category"].value_counts()
    for cat in ["subjective", "objective"]:
        n = counts.get(cat, 0)
        if n < min_n:
            raise ValueError(f"Category '{cat}' has {n} samples, need >= {min_n}")
    return df
