from __future__ import annotations
import pandas as pd
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def load_score_matrix(path: str) -> pd.DataFrame:
    """Load and validate score matrix CSV. Raises FileNotFoundError/ValueError."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Score matrix not found: {path}")
    df = pd.read_csv(p)
    if len(df) < config.MIN_MODELS:
        raise ValueError(
            f"Score matrix has {len(df)} rows; expected >= {config.MIN_MODELS}"
        )
    return df


def validate_schema(
    df: pd.DataFrame,
    required_cols: list[str],
    gate_cols: list[str],
) -> bool:
    """Check all required_cols present and no NaN in gate_cols. Returns True if valid."""
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    nan_cols = [c for c in gate_cols if df[c].isna().any()]
    if nan_cols:
        raise ValueError(f"NaN values in gate columns: {nan_cols}")
    return True


def add_top_quartile_label(
    df: pd.DataFrame,
    col: str,
    quantile: float,
) -> pd.DataFrame:
    """Add binary top_quartile column: 1 if col >= quantile threshold."""
    threshold = df[col].quantile(quantile)
    df = df.copy()
    df[config.TARGET_COL] = (df[col] >= threshold).astype(int)
    return df
