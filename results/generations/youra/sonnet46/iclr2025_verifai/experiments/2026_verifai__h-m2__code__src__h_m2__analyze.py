"""H-M2: Analysis module — histograms, distribution stats, tier assignments."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from h_m2.stratify import (
    HARD_THRESHOLD,
    EASY_THRESHOLD,
    HE_PREFIX,
    MODEL_IDS,
    MODEL_SHORT_NAMES,
    split_by_benchmark,
)

logger = logging.getLogger(__name__)

HIST_BINS: list[float] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]


# ─── Histograms ───────────────────────────────────────────────────────────────

def compute_histograms(
    pass_at_1_data: dict[str, dict[str, float]],
    per_benchmark: bool = True,
) -> dict[str, dict[str, dict[str, int]]]:
    """Compute 6-point discrete pass@1 histogram per model (and optionally per benchmark).

    Uses np.isclose for exact float matching (mirrors h-m1 approach).

    Returns:
        {model_id: {
            "combined": {bin_str: count},
            "humaneval": {bin_str: count},  # if per_benchmark=True
            "mbpp":      {bin_str: count},  # if per_benchmark=True
        }}
    """
    result: dict[str, dict[str, dict[str, int]]] = {}

    for model_id, task_scores in pass_at_1_data.items():
        model_result: dict[str, dict[str, int]] = {}

        # Combined histogram
        arr = np.array(list(task_scores.values()), dtype=float)
        model_result["combined"] = _histogram_6pt(arr)

        if per_benchmark:
            he_scores, mbpp_scores = split_by_benchmark(task_scores)
            he_arr = np.array(list(he_scores.values()), dtype=float)
            mbpp_arr = np.array(list(mbpp_scores.values()), dtype=float)
            model_result["humaneval"] = _histogram_6pt(he_arr)
            model_result["mbpp"] = _histogram_6pt(mbpp_arr)

        result[model_id] = model_result

    return result


def _histogram_6pt(arr: np.ndarray) -> dict[str, int]:
    """Compute 6-point discrete histogram using np.isclose."""
    histogram: dict[str, int] = {}
    for b in HIST_BINS:
        histogram[str(b)] = int(np.sum(np.isclose(arr, b)))
    return histogram


# ─── Distribution Stats ───────────────────────────────────────────────────────

def compute_distribution_stats(
    pass_at_1: dict[str, float],
) -> dict[str, float]:
    """Compute mean, std, min, max and tier percentage breakdown.

    Returns:
        {"mean": float, "std": float, "min": float, "max": float,
         "pct_hard": float, "pct_easy": float, "pct_medium": float}
    """
    arr = np.array(list(pass_at_1.values()), dtype=float)
    total = len(arr)
    if total == 0:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0,
                "pct_hard": 0.0, "pct_easy": 0.0, "pct_medium": 0.0}

    pct_hard = float(np.sum(arr == HARD_THRESHOLD)) / total
    pct_easy = float(np.sum(arr >= EASY_THRESHOLD)) / total
    pct_medium = 1.0 - pct_hard - pct_easy

    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "pct_hard": pct_hard,
        "pct_easy": pct_easy,
        "pct_medium": max(0.0, pct_medium),
    }


# ─── Distribution Shape ───────────────────────────────────────────────────────

def classify_distribution_shape(
    histogram: dict[str, int],
) -> str:
    """Classify distribution shape from 6-point histogram.

    Returns:
        "bimodal" | "skewed_hard" | "skewed_easy" | "uniform" | "other"
    """
    counts = [histogram.get(str(b), 0) for b in HIST_BINS]
    total = sum(counts)
    if total == 0:
        return "other"

    hard_count = counts[0]        # bin 0.0
    easy_counts = counts[3:]      # bins 0.6, 0.8, 1.0
    mid_counts = counts[1:3]      # bins 0.2, 0.4

    hard_pct = hard_count / total
    easy_pct = sum(easy_counts) / total
    mid_pct = sum(mid_counts) / total

    if hard_pct > 0.2 and easy_pct > 0.2 and mid_pct < 0.3:
        return "bimodal"
    if hard_pct > 0.5:
        return "skewed_hard"
    if easy_pct > 0.5:
        return "skewed_easy"
    if max(counts) / total < 0.3:
        return "uniform"
    return "other"


# ─── Tier Assignments DataFrame ───────────────────────────────────────────────

def build_tier_assignments_df(
    pass_at_1_data: dict[str, dict[str, float]],
    tiers: dict[str, dict[str, set]],
) -> pd.DataFrame:
    """Build tier_assignments.csv dataframe.

    Columns:
        task_id, benchmark,
        llama3_tier, codellama_tier, deepseek_tier,
        n_models_hard, n_models_easy
    """
    all_task_ids: set[str] = set()
    for task_scores in pass_at_1_data.values():
        all_task_ids |= set(task_scores.keys())

    col_map = {
        "NousResearch/Meta-Llama-3-8B": "llama3_tier",
        "codellama/CodeLlama-7b-hf": "codellama_tier",
        "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_tier",
    }

    rows = []
    for task_id in sorted(all_task_ids):
        benchmark = "humaneval" if task_id.startswith(HE_PREFIX) else "mbpp"
        row: dict = {"task_id": task_id, "benchmark": benchmark}
        n_hard = 0
        n_easy = 0
        for model_id in MODEL_IDS:
            col_name = col_map[model_id]
            model_tiers = tiers.get(model_id, {})
            if task_id in model_tiers.get("hard", set()):
                row[col_name] = "hard"
                n_hard += 1
            elif task_id in model_tiers.get("easy", set()):
                row[col_name] = "easy"
                n_easy += 1
            else:
                row[col_name] = "medium"
        row["n_models_hard"] = n_hard
        row["n_models_easy"] = n_easy
        rows.append(row)

    return pd.DataFrame(rows, columns=[
        "task_id", "benchmark",
        "llama3_tier", "codellama_tier", "deepseek_tier",
        "n_models_hard", "n_models_easy",
    ])
