"""Metrics computation for H-M1 scale ordering evaluation."""
from typing import Dict, List, TypedDict
import numpy as np
from scipy.stats import kruskal
from sklearn.metrics import cohen_kappa_score, accuracy_score, confusion_matrix


class ScaleEvalResult(TypedDict):
    accuracies: Dict[str, float]
    kappas: Dict[str, float]
    confusion_matrices: Dict[str, Dict[str, int]]
    ordering_satisfied: bool
    diminishing_returns: bool
    diff_7b_70b: float
    diff_70b_prop: float
    kruskal_h: float
    p_value: float


def compute_confusion_metrics(verdicts: Dict[str, int], ground_truth: Dict[str, int]) -> Dict[str, int]:
    """Compute TP, TN, FP, FN counts."""
    y_true = [ground_truth[tid] for tid in verdicts]
    y_pred = [verdicts[tid] for tid in verdicts]

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    return {
        "TP": int(tp),
        "TN": int(tn),
        "FP": int(fp),
        "FN": int(fn),
        "FPR": float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0,
        "FNR": float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0,
    }


def evaluate_scale_ordering(
    judge_verdicts: Dict[str, Dict[str, int]],
    ground_truth: Dict[str, int],
) -> ScaleEvalResult:
    """
    Evaluate judge-execution agreement across model scales.

    Args:
        judge_verdicts: {scale: {task_id: 0|1}}
        ground_truth: {task_id: 0|1}

    Returns:
        ScaleEvalResult with accuracies, ordering checks, Kruskal-Wallis test
    """
    scales = ["7B", "70B", "proprietary"]
    task_ids = list(ground_truth.keys())

    accuracies = {}
    kappas = {}
    confusion_matrices = {}

    for scale in scales:
        verdicts = judge_verdicts[scale]
        y_true = [ground_truth[tid] for tid in task_ids]
        y_pred = [verdicts[tid] for tid in task_ids]

        accuracies[scale] = accuracy_score(y_true, y_pred)
        kappas[scale] = cohen_kappa_score(y_true, y_pred)
        confusion_matrices[scale] = compute_confusion_metrics(verdicts, ground_truth)

    # Test ordering: 7B < 70B < proprietary
    ordering_satisfied = (
        accuracies["7B"] < accuracies["70B"] < accuracies["proprietary"]
    )

    # Test diminishing returns
    diff_7b_70b = accuracies["70B"] - accuracies["7B"]
    diff_70b_prop = accuracies["proprietary"] - accuracies["70B"]
    diminishing_returns = diff_7b_70b > diff_70b_prop

    # Kruskal-Wallis H-test for ordinal scale effect
    scale_groups = []
    for scale in scales:
        verdicts = judge_verdicts[scale]
        agreement = [1 if verdicts[tid] == ground_truth[tid] else 0 for tid in task_ids]
        scale_groups.append(agreement)

    h_stat, p_value = kruskal(*scale_groups)

    return ScaleEvalResult(
        accuracies=accuracies,
        kappas=kappas,
        confusion_matrices=confusion_matrices,
        ordering_satisfied=ordering_satisfied,
        diminishing_returns=diminishing_returns,
        diff_7b_70b=diff_7b_70b,
        diff_70b_prop=diff_70b_prop,
        kruskal_h=h_stat,
        p_value=p_value,
    )


def verify_mechanism(results: ScaleEvalResult) -> bool:
    """
    Verify scale ordering and diminishing returns.
    Returns True if all conditions satisfied, raises AssertionError otherwise.
    """
    acc = results["accuracies"]

    # Check 1: Ordering
    assert acc["7B"] < acc["70B"] < acc["proprietary"], (
        f"Ordering violated: {acc['7B']:.3f} < {acc['70B']:.3f} < {acc['proprietary']:.3f}"
    )

    # Check 2: Diminishing returns
    diff1 = results["diff_7b_70b"]
    diff2 = results["diff_70b_prop"]
    assert diff1 > diff2, f"No diminishing returns: {diff1:.3f} <= {diff2:.3f}"

    # Check 3: Statistical significance
    assert results["p_value"] < 0.05, f"Not significant: p={results['p_value']:.4f}"

    return True
