"""Cross-method metrics for attribution evaluation"""
import numpy as np
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr
from typing import List

def compute_mislabeled_auc(influence_scores: np.ndarray, mislabeled_indices: List[int],
                           n_train: int) -> float:
    """Compute AUC for detecting mislabeled samples via influence scores.

    influence_scores: [n_query, n_train] or [n_train] aggregate
    Higher absolute influence -> more likely mislabeled
    """
    if influence_scores.ndim == 2:
        agg = np.mean(np.abs(influence_scores), axis=0)
    else:
        agg = np.abs(influence_scores)

    n_scores = len(agg)
    y_true = np.zeros(n_scores)

    valid_indices = [i for i in mislabeled_indices if i < n_scores]
    y_true[valid_indices] = 1

    if y_true.sum() == 0 or y_true.sum() == len(y_true):
        return 0.5

    return roc_auc_score(y_true, agg)

def compute_rank_correlation(score_list: List[np.ndarray]) -> float:
    """Compute average pairwise Spearman correlation across score matrices."""
    if len(score_list) < 2:
        return 1.0

    if score_list[0].ndim == 2:
        flat_scores = [np.mean(np.abs(s), axis=0) for s in score_list]
    else:
        flat_scores = [np.abs(s) for s in score_list]

    correlations = []
    for i in range(len(flat_scores)):
        for j in range(i+1, len(flat_scores)):
            if len(flat_scores[i]) == len(flat_scores[j]):
                rho, _ = spearmanr(flat_scores[i], flat_scores[j])
                if not np.isnan(rho):
                    correlations.append(rho)

    return np.mean(correlations) if correlations else 0.0

def compute_relative_arch_diff(bert_auc: float, gpt2_auc: float) -> float:
    """Compute relative difference: |bert - gpt2| / max(bert, gpt2)"""
    max_val = max(bert_auc, gpt2_auc)
    if max_val == 0:
        return 0.0
    return abs(bert_auc - gpt2_auc) / max_val

def build_results_dict(bert_results: dict, gpt2_results: dict, methods: List[str]) -> dict:
    """Build nested results dict: {method: {arch: auc}}"""
    results = {}
    for method in methods:
        results[method] = {
            "bert": bert_results.get(method, {}).get("auc", 0.5),
            "gpt2": gpt2_results.get(method, {}).get("auc", 0.5),
        }
    return results
