"""H-M1 Findable sub-score extraction from H-E1 proxy scores."""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def compute_f1_pid(cohort: pd.DataFrame) -> pd.Series:
    """Proxy: 1.0 if dataset has fair_F > 0 (persistent ID indicator); else 0.0."""
    if "fair_F" in cohort.columns:
        return (cohort["fair_F"] > 0).astype(float)
    return pd.Series(0.0, index=cohort.index)


def compute_f2_metadata(cohort: pd.DataFrame) -> pd.Series:
    """Proxy: use fair_F score directly as metadata richness proxy (0-1 range)."""
    if "fair_F" in cohort.columns:
        vals = cohort["fair_F"].clip(0.0, 1.0)
        return vals.fillna(0.0)
    return pd.Series(0.0, index=cohort.index)


def compute_f3_search_indexed(cohort: pd.DataFrame) -> pd.Series:
    """Proxy: 1.0 if fair_F >= 0.5 (search-indexed indicator); else 0.0."""
    if "fair_F" in cohort.columns:
        return (cohort["fair_F"] >= 0.5).astype(float)
    return pd.Series(0.0, index=cohort.index)


def compute_findable_score(
    cohort: pd.DataFrame,
    f1_weight: float,
    f2_weight: float,
    f3_weight: float,
) -> pd.DataFrame:
    """Compute findable_score composite and binary high_findable treatment.
    Returns: cohort + columns [F1_PID, F2_metadata, F3_search_indexed, findable_score, high_findable]
    """
    df = cohort.copy()
    df["F1_PID"] = compute_f1_pid(df)
    df["F2_metadata"] = compute_f2_metadata(df)
    df["F3_search_indexed"] = compute_f3_search_indexed(df)
    df["findable_score"] = (
        f1_weight * df["F1_PID"] +
        f2_weight * df["F2_metadata"] +
        f3_weight * df["F3_search_indexed"]
    )
    median_score = df["findable_score"].median()
    df["high_findable"] = (df["findable_score"] > median_score).astype(int)
    logger.info(f"Findable score: median={median_score:.3f}, "
                f"high={df['high_findable'].sum()}, low={(df['high_findable']==0).sum()}")
    return df


def compute_accessible_score(cohort: pd.DataFrame) -> pd.Series:
    """Proxy: accessible_score = 0.5*A1_open_license + 0.5*A2_standard_format.
    Uses fair_A column as proxy for accessible sub-criteria.
    """
    if "fair_A" in cohort.columns:
        return cohort["fair_A"].clip(0.0, 1.0).fillna(0.0)
    return pd.Series(0.0, index=cohort.index)
