"""Mode classification based on human entropy and RM variance."""

import numpy as np
import pandas as pd


def compute_pair_entropy(df: pd.DataFrame) -> pd.DataFrame:
    """Compute human entropy at model-pair level and broadcast to all rows."""
    df = df.copy()

    if "model_a" not in df.columns or "model_b" not in df.columns:
        df["human_entropy"] = 1.0
        return df

    pair_entropy = {}

    for (ma, mb), grp in df.groupby(["model_a", "model_b"]):
        counts = grp["winner"].value_counts(normalize=True)
        p_a = counts.get("model_a", 0.0)
        p_b = counts.get("model_b", 0.0)
        p_tie = counts.get("tie", 0.0) + counts.get("tie (bothbad)", 0.0)

        probs = [p for p in [p_a, p_b, p_tie] if p > 0]
        if probs:
            H = -sum(p * np.log2(p) for p in probs)
        else:
            H = 0.0

        pair_entropy[(ma, mb)] = H

    df["human_entropy"] = df.apply(
        lambda r: pair_entropy.get((r["model_a"], r["model_b"]), 1.0), axis=1
    )

    return df


def compute_cluster_entropy_fallback(df: pd.DataFrame) -> pd.DataFrame:
    """Fallback: cluster similar prompts and compute entropy within clusters."""
    df = df.copy()
    df["human_entropy"] = 1.0
    return df


def assign_modes(df: pd.DataFrame) -> pd.DataFrame:
    """Median split on human_entropy and rm_variance -> 4 modes."""
    df = df.copy()

    h_med = df["human_entropy"].median()
    v_med = df["rm_variance"].median()

    high_h = df["human_entropy"] > h_med
    low_v = df["rm_variance"] <= v_med

    df["mode"] = 1
    df.loc[~high_h & ~low_v, "mode"] = 2
    df.loc[high_h & low_v, "mode"] = 3
    df.loc[high_h & ~low_v, "mode"] = 4

    return df


def mode_distribution(df: pd.DataFrame) -> dict:
    """Return counts and proportions for all 4 modes."""
    counts = df["mode"].value_counts().to_dict()
    total = len(df)

    result = {}
    for mode in [1, 2, 3, 4]:
        count = counts.get(mode, 0)
        result[mode] = {
            "count": count,
            "proportion": count / total if total > 0 else 0.0,
        }

    return result
