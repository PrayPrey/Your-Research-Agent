# baselines.py - Load h-e1 baseline scores
import json
import os
import pandas as pd
from config import BASELINE_SCORES_CSV, BASELINE_METRICS_JSON


def load_h_e1_scores(scores_csv_path: str = BASELINE_SCORES_CSV) -> dict[str, list[float]]:
    """Read h-e1 scores.csv. Returns {method: [...]} for UQ columns found."""
    if not os.path.exists(scores_csv_path):
        print(f"Warning: {scores_csv_path} not found")
        return {}
    df = pd.read_csv(scores_csv_path)
    known_methods = ["choice_entropy", "max_prob", "token_entropy", "p_true", "semantic_entropy"]
    result = {}
    for col in known_methods:
        if col in df.columns:
            result[col] = df[col].tolist()
    return result


def load_h_e1_metrics(metrics_json_path: str = BASELINE_METRICS_JSON) -> dict:
    """Load h-e1 metrics.json with authoritative AUROC values."""
    if not os.path.exists(metrics_json_path):
        print(f"Warning: {metrics_json_path} not found")
        return {}
    with open(metrics_json_path) as f:
        return json.load(f)
