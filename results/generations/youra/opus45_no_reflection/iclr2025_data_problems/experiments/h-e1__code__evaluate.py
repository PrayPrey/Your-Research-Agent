"""Evaluation and statistical analysis for H-E1 experiment."""

from typing import Dict, List, Set, Tuple

import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score


def mislabeled_auc(scores: np.ndarray, mislabeled_indices: Set[int]) -> float:
    """Compute ROC-AUC for mislabeled detection.

    Higher self-influence scores should indicate mislabeled examples.
    """
    n_samples = len(scores)
    labels = np.array([1 if i in mislabeled_indices else 0 for i in range(n_samples)])

    if labels.sum() == 0 or labels.sum() == n_samples:
        return 0.5

    return roc_auc_score(labels, scores)


def paired_ttest(bert_aucs: List[float], gpt2_aucs: List[float]) -> Tuple[float, float]:
    """Perform paired t-test between BERT and GPT-2 AUC scores.

    Returns:
        (t_statistic, p_value)
    """
    if len(bert_aucs) != len(gpt2_aucs):
        raise ValueError("Lists must have same length")

    t_stat, p_value = stats.ttest_rel(bert_aucs, gpt2_aucs)
    return t_stat, p_value


def cohens_d(x: List[float], y: List[float]) -> float:
    """Compute Cohen's d effect size.

    Returns:
        Effect size (positive if x > y)
    """
    nx, ny = len(x), len(y)
    mean_diff = np.mean(x) - np.mean(y)

    var_x = np.var(x, ddof=1)
    var_y = np.var(y, ddof=1)

    pooled_std = np.sqrt(((nx - 1) * var_x + (ny - 1) * var_y) / (nx + ny - 2))

    if pooled_std == 0:
        return 0.0

    return mean_diff / pooled_std


def run_gate_check(results: Dict) -> Dict:
    """Check if PoC success criteria are met.

    Pass Criteria (MUST_WORK gate):
    1. At least one method shows >5% AUC difference (p < 0.05)
    2. Effect size Cohen's d > 0.3 for at least one method

    Args:
        results: Dict with structure {method: {arch: [aucs_per_seed]}}

    Returns:
        Dict with gate result and per-method statistics
    """
    gate_results = {
        "overall_pass": False,
        "methods": {},
        "best_method": None,
        "best_diff": 0.0,
    }

    for method in results:
        bert_aucs = results[method].get("bert", [])
        gpt2_aucs = results[method].get("gpt2", [])

        if len(bert_aucs) == 0 or len(gpt2_aucs) == 0:
            continue

        mean_bert = np.mean(bert_aucs)
        mean_gpt2 = np.mean(gpt2_aucs)
        auc_diff = mean_gpt2 - mean_bert

        t_stat, p_value = paired_ttest(bert_aucs, gpt2_aucs)
        d = cohens_d(gpt2_aucs, bert_aucs)

        method_pass = (
            abs(auc_diff) > 0.05 and
            p_value < 0.05 and
            abs(d) > 0.3
        )

        gate_results["methods"][method] = {
            "pass": method_pass,
            "auc_bert_mean": mean_bert,
            "auc_gpt2_mean": mean_gpt2,
            "auc_diff": auc_diff,
            "t_stat": t_stat,
            "p_value": p_value,
            "cohens_d": d,
        }

        if method_pass:
            gate_results["overall_pass"] = True

        if abs(auc_diff) > abs(gate_results["best_diff"]):
            gate_results["best_diff"] = auc_diff
            gate_results["best_method"] = method

    return gate_results
