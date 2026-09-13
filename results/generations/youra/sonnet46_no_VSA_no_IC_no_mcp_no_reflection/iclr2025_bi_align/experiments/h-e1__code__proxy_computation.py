"""Behavioral proxy computation: token counts, correction freq, Shannon entropy."""
import numpy as np
import pandas as pd
from scipy.stats import entropy as scipy_entropy
from typing import Literal


CORRECTION_MARKERS = [
    "actually",
    "that's wrong",
    "no, i meant",
    "please redo",
    "that is incorrect",
    "you're wrong",
]


def compute_prompt_token_count(
    prompt: str,
    method: Literal["approx", "tiktoken"] = "approx",
) -> float:
    if method == "approx":
        return len(prompt.split()) * 1.3
    elif method == "tiktoken":
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return float(len(enc.encode(prompt)))
    raise ValueError(f"Unknown method: {method}")


def compute_token_series(
    cohort_df: pd.DataFrame,
    method: str = "approx",
) -> dict[str, float]:
    """Monthly mean prompt token count."""
    df = cohort_df.copy()
    df["prompt_token_count"] = df["prompt"].apply(
        lambda p: compute_prompt_token_count(p, method=method)
    )
    monthly = df.groupby("monthly_bin")["prompt_token_count"].mean().sort_index()
    return monthly.to_dict()


def compute_correction_freq(session_turns: list[str]) -> float:
    if not session_turns:
        return 0.0
    n = len(session_turns)
    count = sum(
        1 for turn in session_turns
        if any(marker in turn.lower() for marker in CORRECTION_MARKERS)
    )
    return count / n


def compute_correction_series(cohort_df: pd.DataFrame) -> dict[str, float]:
    """Monthly mean correction frequency (single-turn approximation)."""
    df = cohort_df.copy()
    df["correction_freq"] = df["prompt"].apply(
        lambda p: compute_correction_freq([p])
    )
    monthly = df.groupby("monthly_bin")["correction_freq"].mean().sort_index()
    return monthly.to_dict()


def compute_entropy_series(
    lmsys_df: pd.DataFrame,
    entropy_base: int = 2,
    laplace_alpha: float = 1e-6,
) -> dict[str, float]:
    """Monthly mean Shannon entropy of win/loss/tie distribution."""
    results = {}
    for bin_id, group in lmsys_df.groupby("monthly_bin"):
        winner_counts = group["winner"].value_counts()
        categories = ["model_a", "model_b", "tie", "tie (bothbad)"]
        counts = np.array([
            winner_counts.get(cat, 0) + laplace_alpha for cat in categories
        ], dtype=float)
        probs = counts / counts.sum()
        h = scipy_entropy(probs, base=entropy_base)
        results[bin_id] = float(h)
    return dict(sorted(results.items()))
