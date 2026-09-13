"""
Data loader for H-E1: TrustLLM published score tables.
Loads per-model per-dimension scores from TrustLLM/results/*.json
(Sun et al., ICML 2024, Table 1).
"""

import glob
import json
import os

import numpy as np
import pandas as pd

DIMENSIONS = [
    "truthfulness",
    "safety",
    "fairness",
    "robustness",
    "privacy",
    "machine_ethics",
]

MODEL_ANNOTATIONS = {
    "LLaMA-2-7b-base":   {"log10_params": 9.845,  "is_RLHF": 0},
    "LLaMA-2-7b-chat":   {"log10_params": 9.845,  "is_RLHF": 1},
    "LLaMA-2-13b-base":  {"log10_params": 10.114, "is_RLHF": 0},
    "LLaMA-2-13b-chat":  {"log10_params": 10.114, "is_RLHF": 1},
    "LLaMA-2-70b-base":  {"log10_params": 10.845, "is_RLHF": 0},
    "LLaMA-2-70b-chat":  {"log10_params": 10.845, "is_RLHF": 1},
    "Mistral-7b":        {"log10_params": 9.845,  "is_RLHF": 0},
    "Falcon-7b":         {"log10_params": 9.845,  "is_RLHF": 0},
    "Vicuna-7b":         {"log10_params": 9.845,  "is_RLHF": 1},
    "Vicuna-13b":        {"log10_params": 10.114, "is_RLHF": 1},
    "Vicuna-33b":        {"log10_params": 10.519, "is_RLHF": 1},
    "GPT-3.5-turbo":     {"log10_params": 11.176, "is_RLHF": 1},
    "GPT-4":             {"log10_params": 11.903, "is_RLHF": 1},
    "Claude-2":          {"log10_params": 11.699, "is_RLHF": 1},
    "ChatGLM2":          {"log10_params": 9.845,  "is_RLHF": 1},
    "Koala-13b":         {"log10_params": 10.114, "is_RLHF": 1},
}

# Canonical model order (matches TrustLLM paper Table 1)
MODEL_ORDER = list(MODEL_ANNOTATIONS.keys())


def load_trustllm_scores(results_dir: str = "TrustLLM/results") -> pd.DataFrame:
    """Load TrustLLM 16x6 score matrix from results/*.json files.

    Each JSON file is named <model>.json and contains a dict mapping
    dimension name to aggregate score (float in [0, 1]).
    """
    if not os.path.isdir(results_dir):
        raise FileNotFoundError(
            f"TrustLLM results directory not found: {results_dir}\n"
            f"Clone HowieHwong/TrustLLM and ensure results/ folder exists."
        )

    json_files = glob.glob(os.path.join(results_dir, "*.json"))
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {results_dir}")

    # Build model_name -> scores dict from JSON files
    raw = {}
    for path in json_files:
        model_name = os.path.splitext(os.path.basename(path))[0]
        # Reverse filename sanitization: underscores in model names kept as-is
        with open(path) as f:
            data = json.load(f)
        raw[model_name] = data

    # Build DataFrame in canonical model order
    records = []
    for model in MODEL_ORDER:
        if model not in raw:
            raise ValueError(
                f"Model '{model}' missing from {results_dir}. "
                f"Found: {sorted(raw.keys())}"
            )
        row = raw[model]
        scores = [row[dim] for dim in DIMENSIONS]
        records.append(scores)

    df = pd.DataFrame(records, index=MODEL_ORDER, columns=DIMENSIONS)
    return df


def add_annotations(scores_df: pd.DataFrame) -> pd.DataFrame:
    """Add log10_params and is_RLHF columns from MODEL_ANNOTATIONS."""
    log10_params = []
    is_rlhf = []
    for model in scores_df.index:
        if model not in MODEL_ANNOTATIONS:
            raise ValueError(f"Model '{model}' not in MODEL_ANNOTATIONS")
        ann = MODEL_ANNOTATIONS[model]
        log10_params.append(ann["log10_params"])
        is_rlhf.append(ann["is_RLHF"])

    df = scores_df.copy()
    df["log10_params"] = log10_params
    df["is_RLHF"] = is_rlhf
    return df


def validate(df: pd.DataFrame) -> dict:
    """Validate data quality. Returns report dict."""
    score_cols = DIMENSIONS
    scores = df[score_cols]

    missing_count = scores.isnull().sum().sum()
    if missing_count >= 3:
        raise ValueError(f"{missing_count} missing values — too many")

    # Floor/ceiling: >20% of models at 0 or 1
    floor_ceiling_flags = {}
    for col in score_cols:
        pct_extreme = ((scores[col] == 0) | (scores[col] == 1)).mean()
        if pct_extreme > 0.20:
            floor_ceiling_flags[col] = pct_extreme

    # VIF for covariates (log10_params, is_RLHF)
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    X = df[["log10_params", "is_RLHF"]].values
    vif_log10 = variance_inflation_factor(X, 0)
    vif_rlhf = variance_inflation_factor(X, 1)

    if vif_log10 > 5 or vif_rlhf > 5:
        print(f"WARNING: High VIF detected (log10={vif_log10:.2f}, RLHF={vif_rlhf:.2f})")

    return {
        "missing_count": int(missing_count),
        "floor_ceiling_flags": floor_ceiling_flags,
        "vif_log10": float(vif_log10),
        "vif_rlhf": float(vif_rlhf),
    }
