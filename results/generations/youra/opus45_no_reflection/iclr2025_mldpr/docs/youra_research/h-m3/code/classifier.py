"""Benchmark classifier for H-M3: Map benchmark names to categories."""

from typing import Literal
import pandas as pd

from config import EMERGENT_BENCHMARKS, TRADITIONAL_BENCHMARKS


def classify_benchmark(name: str) -> Literal["emergent", "traditional", "unknown"]:
    """Map benchmark name to emergent/traditional/unknown."""
    name_lower = name.lower()

    for b in EMERGENT_BENCHMARKS:
        if b.lower() in name_lower or name_lower in b.lower():
            return "emergent"

    for b in TRADITIONAL_BENCHMARKS:
        if b.lower() in name_lower or name_lower in b.lower():
            return "traditional"

    return "unknown"


def label_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Add 'category' column to DataFrame based on benchmark name."""
    df = df.copy()
    df["category"] = df["benchmark"].apply(classify_benchmark)
    return df
