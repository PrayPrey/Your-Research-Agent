from __future__ import annotations

import pandas as pd
from pathlib import Path

from config import REQUIRED_COLS, GATE_COLS, MIN_MODELS


def load_score_matrix(path: str) -> pd.DataFrame:
    """Load and validate greedy score matrix. Raises ValueError on schema/row issues."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Score matrix not found: {path}")
    df = pd.read_csv(p)
    validate_schema(df, REQUIRED_COLS, GATE_COLS)
    if len(df) < MIN_MODELS:
        raise ValueError(f"Insufficient rows: {len(df)} < {MIN_MODELS}")
    return df


def load_score_matrix_t07(path: str) -> pd.DataFrame:
    """Load T=0.7 score matrix. Returns empty DataFrame if file missing."""
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    try:
        validate_schema(df, REQUIRED_COLS, GATE_COLS)
    except ValueError:
        return pd.DataFrame()
    return df


def validate_schema(df: pd.DataFrame, required_cols: list[str], gate_cols: list[str]) -> bool:
    """Check all required_cols present and no NaN in gate_cols. Returns True if valid."""
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    for col in gate_cols:
        if col in df.columns and df[col].isna().any():
            raise ValueError(f"NaN values in gate column: {col}")
    return True
