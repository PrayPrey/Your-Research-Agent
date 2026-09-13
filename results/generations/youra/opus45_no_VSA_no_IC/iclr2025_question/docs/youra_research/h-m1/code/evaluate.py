"""Evaluation and gate checking for h-m1."""

import json
import numpy as np
from sklearn.metrics import roc_auc_score

from config import AUROC_PASS_THRESHOLD, AUROC_FAIL_THRESHOLD, RESULTS_DIR


def compute_auroc(y_true: list, y_pred_proba: np.ndarray) -> float:
    """Compute AUROC score."""
    return roc_auc_score(y_true, y_pred_proba)


def check_gate(auroc: float) -> dict:
    """Check gate: pass if >0.70, fail if <0.60, else inconclusive."""
    if auroc >= AUROC_PASS_THRESHOLD:
        status = "pass"
    elif auroc < AUROC_FAIL_THRESHOLD:
        status = "fail"
    else:
        status = "inconclusive"
    return {"status": status, "auroc": auroc, "threshold": AUROC_PASS_THRESHOLD}


def save_results(results: dict, filename: str = "results.json"):
    """Save results to JSON."""
    import os
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, "w") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"Results saved to {path}")
