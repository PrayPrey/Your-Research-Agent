"""data_loader.py — load and align h-m3/h-m2/h-e1 results for h-m4 analysis."""
from __future__ import annotations

import json
import os
import warnings
from typing import Any

import numpy as np
import pandas as pd

from .config import (
    CONFIDENCE_SCORES_FILENAME,
    HARD_THRESHOLD,
    EASY_THRESHOLD,
    MIN_TIER_SIZE,
    TIER_ASSIGNMENTS_FILENAME,
)


_CHECKPOINT_MODEL_MAP = {
    "llama3_8b": "llama3_8b",
    "codellama_7b": "codellama_7b",
    "deepseek_6.7b": "deepseek_6.7b",
}


def load_confidence_scores(hm3_results_dir: str) -> dict[str, dict[str, float]]:
    """Load per-task confidence scores from h-m3 checkpoint files.

    Loads ptrue_checkpoint_{model}.json files which have format:
    {task_id: {confidence_scores: [c1,...,c5], correctness_labels: [0/1,...], tier: str, pass_at_1: float}}
    Returns: {model_short: {task_id: mean_c}}
    """
    result: dict[str, dict[str, float]] = {}

    for model_short in _CHECKPOINT_MODEL_MAP:
        fname = f"ptrue_checkpoint_{model_short}.json"
        path = os.path.join(hm3_results_dir, fname)
        if not os.path.exists(path):
            raise FileNotFoundError(f"h-m3 checkpoint file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        result[model_short] = {}
        for task_id, task_data in raw.items():
            c_values = task_data.get("confidence_scores", [])
            if len(c_values) == 0:
                warnings.warn(f"Empty confidence list for {model_short}/{task_id}, skipping.")
                continue
            result[model_short][task_id] = float(np.mean(c_values))

    return result


def load_tier_assignments(hm2_results_dir: str) -> pd.DataFrame:
    """Load tier_assignments.csv from h-m2 results.

    Returns DataFrame with columns: [task_id, llama3_tier, codellama_tier, deepseek_tier]
    """
    path = os.path.join(hm2_results_dir, TIER_ASSIGNMENTS_FILENAME)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Tier assignments file not found: {path}")

    df = pd.read_csv(path)

    required_cols = {"task_id", "llama3_tier", "codellama_tier", "deepseek_tier"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"tier_assignments.csv missing columns: {missing}")

    return df[["task_id", "llama3_tier", "codellama_tier", "deepseek_tier"]].copy()


def load_correctness(he1_results_dir: str, model_short: str) -> dict[str, int]:
    """Load correctness_{model_short}.json from h-e1 results.

    Raw format: {task_id: [binary_per_solution]}
    Returns: {task_id: int(mean > 0)}
    """
    filename = f"correctness_{model_short}.json"
    path = os.path.join(he1_results_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Correctness file not found: {path}")

    with open(path, "r") as f:
        raw: dict[str, list[int]] = json.load(f)

    result: dict[str, int] = {}
    for task_id, binary_list in raw.items():
        if len(binary_list) == 0:
            warnings.warn(f"Empty correctness list for {model_short}/{task_id}, labeling as 0.")
            result[task_id] = 0
        else:
            result[task_id] = int(np.mean(binary_list) > 0)

    return result


def align_model_data(
    confidence: dict[str, float],
    tier_df: pd.DataFrame,
    correctness: dict[str, int],
    model_short: str,
) -> dict[str, Any]:
    """Align confidence scores, tier assignments, and correctness labels for a model.

    Parameters
    ----------
    confidence : {task_id: mean_c} for this model
    tier_df : DataFrame with task_id + tier columns
    correctness : {task_id: binary_label} for this model
    model_short : short name of model

    Returns
    -------
    dict with keys: c_hard, y_hard, c_easy, y_easy, n_hard, n_easy
    """
    tier_col_map = {
        "llama3_8b": "llama3_tier",
        "codellama_7b": "codellama_tier",
        "deepseek_6.7b": "deepseek_tier",
    }

    if model_short not in tier_col_map:
        raise ValueError(f"Unknown model_short: {model_short}. Expected one of {list(tier_col_map)}")

    tier_col = tier_col_map[model_short]

    # Extract hard and easy task ids from tier DataFrame (tier is a string: 'hard', 'easy', 'medium')
    hard_mask = tier_df[tier_col] == "hard"
    easy_mask = tier_df[tier_col] == "easy"

    hard_ids = set(tier_df.loc[hard_mask, "task_id"].tolist())
    easy_ids = set(tier_df.loc[easy_mask, "task_id"].tolist())

    # Filter to tasks that have both confidence and correctness
    available = set(confidence.keys()) & set(correctness.keys())

    hard_ids = hard_ids & available
    easy_ids = easy_ids & available

    # CodeLlama special case: if n_easy < MIN_TIER_SIZE, try MBPP-only easy tasks
    if model_short == "codellama_7b" and len(easy_ids) < MIN_TIER_SIZE:
        mbpp_easy = {t for t in easy_ids if "Mbpp" in t or "mbpp" in t or "MBPP" in t}
        if len(mbpp_easy) >= MIN_TIER_SIZE:
            warnings.warn(
                f"CodeLlama: n_easy_total={len(easy_ids)} < {MIN_TIER_SIZE}, "
                f"using MBPP-only easy ({len(mbpp_easy)} tasks)"
            )
            easy_ids = mbpp_easy
        else:
            warnings.warn(
                f"CodeLlama: n_easy={len(easy_ids)} < {MIN_TIER_SIZE} even after MBPP filter; "
                f"using all easy tasks available"
            )

    n_hard = len(hard_ids)
    n_easy = len(easy_ids)

    if n_hard < MIN_TIER_SIZE:
        raise ValueError(
            f"Not enough hard samples for {model_short}: got {n_hard}, need {MIN_TIER_SIZE}"
        )
    if n_easy < MIN_TIER_SIZE:
        raise ValueError(
            f"Not enough easy samples for {model_short}: got {n_easy}, need {MIN_TIER_SIZE}"
        )

    hard_ids_sorted = sorted(hard_ids)
    easy_ids_sorted = sorted(easy_ids)

    c_hard = np.array([confidence[t] for t in hard_ids_sorted], dtype=float)
    y_hard = np.array([correctness[t] for t in hard_ids_sorted], dtype=float)
    c_easy = np.array([confidence[t] for t in easy_ids_sorted], dtype=float)
    y_easy = np.array([correctness[t] for t in easy_ids_sorted], dtype=float)

    return {
        "c_hard": c_hard,
        "y_hard": y_hard,
        "c_easy": c_easy,
        "y_easy": y_easy,
        "n_hard": n_hard,
        "n_easy": n_easy,
    }


def make_holdout_split(
    c_hard: np.ndarray,
    y_hard: np.ndarray,
    c_easy: np.ndarray,
    y_easy: np.ndarray,
    holdout_frac: float = 0.2,
    seed: int = 42,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Split data into eval (80%) and holdout (20%) sets per tier independently.

    Parameters
    ----------
    c_hard, y_hard : confidence and labels for hard tier
    c_easy, y_easy : confidence and labels for easy tier
    holdout_frac : fraction to hold out (default 0.2)
    seed : random seed

    Returns
    -------
    (eval_data, holdout_data) each with keys: c_hard, y_hard, c_easy, y_easy
    """
    rng = np.random.default_rng(seed)

    # Hard tier split
    n_hard = len(c_hard)
    n_hard_holdout = max(1, int(round(n_hard * holdout_frac)))
    perm_hard = rng.permutation(n_hard)
    holdout_hard_idx = perm_hard[:n_hard_holdout]
    eval_hard_idx = perm_hard[n_hard_holdout:]

    # Easy tier split
    n_easy = len(c_easy)
    n_easy_holdout = max(1, int(round(n_easy * holdout_frac)))
    perm_easy = rng.permutation(n_easy)
    holdout_easy_idx = perm_easy[:n_easy_holdout]
    eval_easy_idx = perm_easy[n_easy_holdout:]

    eval_data = {
        "c_hard": c_hard[eval_hard_idx],
        "y_hard": y_hard[eval_hard_idx],
        "c_easy": c_easy[eval_easy_idx],
        "y_easy": y_easy[eval_easy_idx],
    }

    holdout_data = {
        "c_hard": c_hard[holdout_hard_idx],
        "y_hard": y_hard[holdout_hard_idx],
        "c_easy": c_easy[holdout_easy_idx],
        "y_easy": y_easy[holdout_easy_idx],
    }

    return eval_data, holdout_data
