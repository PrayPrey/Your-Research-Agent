"""Cross-cluster transfer runner for H-M4."""

import os
import numpy as np
import importlib.util
from typing import List, Tuple
from sklearn.metrics import roc_curve, roc_auc_score

# Import H-M4 config using importlib
H_M4_PATH = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("m4_config", os.path.join(H_M4_PATH, "config.py"))
m4_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m4_config)

CROSS_CLUSTER_PAIRS = m4_config.CROSS_CLUSTER_PAIRS
TARGET_FPR = m4_config.TARGET_FPR


def calibrate_threshold(entropies: np.ndarray, labels: np.ndarray, target_fpr: float = TARGET_FPR) -> float:
    """Find threshold at target FPR (inlined from H-M3)."""
    y_true = ~labels.astype(bool)
    fpr, tpr, thresholds = roc_curve(y_true, entropies)
    idx = np.argmin(np.abs(fpr - target_fpr))
    return float(thresholds[idx])


def evaluate_transfer(source_threshold: float, target_entropies: np.ndarray, target_labels: np.ndarray) -> dict:
    """Evaluate AUROC using source-calibrated threshold on target data (inlined from H-M3)."""
    y_true = ~target_labels.astype(bool)
    auroc = roc_auc_score(y_true, target_entropies)
    return {"auroc": float(auroc), "threshold_used": source_threshold}


def compute_auroc_degradation(source_auroc: float, target_auroc: float) -> float:
    """Positive = performance dropped (inlined from H-M3)."""
    return source_auroc - target_auroc


def run_pair_transfer(source: str, target: str, entropy_cache: dict) -> dict:
    """Run transfer from source to target benchmark."""
    src_calib_e, src_calib_l, src_eval_e, src_eval_l = entropy_cache[source]
    _, _, tgt_eval_e, tgt_eval_l = entropy_cache[target]

    threshold = calibrate_threshold(src_calib_e, src_calib_l)
    source_result = evaluate_transfer(threshold, src_eval_e, src_eval_l)
    target_result = evaluate_transfer(threshold, tgt_eval_e, tgt_eval_l)
    degradation = compute_auroc_degradation(source_result["auroc"], target_result["auroc"])

    return {
        "source": source,
        "target": target,
        "source_auroc": source_result["auroc"],
        "target_auroc": target_result["auroc"],
        "degradation": degradation,
        "source_threshold": threshold
    }


def run_cross_cluster_transfers(pairs: List[Tuple[str, str]], entropy_cache: dict) -> List[dict]:
    """Run directional cross-cluster transfers (source->target only, not bidirectional)."""
    results = []
    for source, target in pairs:
        result = run_pair_transfer(source, target, entropy_cache)
        results.append(result)
    return results
