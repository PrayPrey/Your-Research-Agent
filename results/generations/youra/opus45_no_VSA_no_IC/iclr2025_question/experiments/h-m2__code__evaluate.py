"""Transfer matrix evaluation and gap statistics for h-m2."""

import numpy as np
from sklearn.metrics import roc_auc_score

from transfer import AffineAligner, TransferEvaluator
from config import GAP_ALIGNMENT_TRIGGER


def build_transfer_matrix(
    probes: dict,
    hidden_val: dict[str, np.ndarray],
    labels_val: np.ndarray,
    aligners: dict[tuple[str, str], AffineAligner],
) -> tuple[np.ndarray, dict]:
    """
    Build 3x3 AUROC matrix.
    matrix[i][j] = probe trained on model i, evaluated on model j's hidden states.
    Returns (matrix, method_used) where method_used tracks direct vs aligned.
    """
    keys = list(probes.keys())
    n = len(keys)
    matrix = np.zeros((n, n))
    method_used = {}

    for i, src in enumerate(keys):
        evaluator = TransferEvaluator(probes[src])
        baseline = None

        for j, tgt in enumerate(keys):
            target_hidden = hidden_val[tgt].astype(np.float32)

            if src == tgt:
                proba = probes[src].predict_proba(target_hidden)[:, 1]
                auroc = roc_auc_score(labels_val, proba)
                baseline = auroc
                method_used[(src, tgt)] = "baseline"
            else:
                auroc_direct = evaluator.evaluate_direct(target_hidden, labels_val)

                if auroc_direct is not None and baseline is not None:
                    gap_direct = abs(auroc_direct - baseline)
                    if gap_direct <= GAP_ALIGNMENT_TRIGGER:
                        auroc = auroc_direct
                        method_used[(src, tgt)] = "direct"
                    else:
                        auroc = evaluator.evaluate_aligned(
                            target_hidden, labels_val, aligners[(src, tgt)]
                        )
                        method_used[(src, tgt)] = "aligned"
                else:
                    auroc = evaluator.evaluate_aligned(
                        target_hidden, labels_val, aligners[(src, tgt)]
                    )
                    method_used[(src, tgt)] = "aligned"

            matrix[i][j] = auroc

    return matrix, method_used


def compute_gap_stats(matrix: np.ndarray, model_keys: list[str]) -> dict:
    """Compute transfer gap statistics from AUROC matrix."""
    diag = np.diag(matrix)
    pair_gaps = {}

    for i, src in enumerate(model_keys):
        for j, tgt in enumerate(model_keys):
            if i != j:
                pair_gaps[f"{src}->{tgt}"] = abs(matrix[i][j] - diag[i])

    gaps = list(pair_gaps.values())
    return {
        "mean_gap": float(np.mean(gaps)),
        "max_gap": float(np.max(gaps)),
        "per_pair_gaps": pair_gaps,
    }


def check_transfer_success(gap_stats: dict, mean_threshold: float = 0.10, max_threshold: float = 0.15) -> dict:
    """Check if h-m2 hypothesis criteria met."""
    mean_ok = gap_stats["mean_gap"] <= mean_threshold
    max_ok = gap_stats["max_gap"] <= max_threshold

    return {
        "passed": mean_ok and max_ok,
        "mean_gap": gap_stats["mean_gap"],
        "max_gap": gap_stats["max_gap"],
        "mean_threshold": mean_threshold,
        "max_threshold": max_threshold,
        "mean_ok": mean_ok,
        "max_ok": max_ok,
        "per_pair_gaps": gap_stats["per_pair_gaps"],
    }
