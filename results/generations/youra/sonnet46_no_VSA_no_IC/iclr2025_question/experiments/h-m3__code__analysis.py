"""Statistical analysis for H-M2: Spearman ρ, bootstrap CI, AUROC, gate check."""
import numpy as np
from scipy.stats import spearmanr, bootstrap
from sklearn.metrics import roc_auc_score
from typing import Dict, Tuple


def compute_spearman_with_ci(
    scores: np.ndarray, labels: np.ndarray,
    n_resamples: int = 1000, ci: float = 0.95
) -> Tuple[float, float, object]:
    """Returns (rho, p_value, bootstrap_ci)."""
    rho, pval = spearmanr(scores, labels)

    def stat(s, l):
        return spearmanr(s, l).statistic

    res = bootstrap(
        (scores, labels), stat,
        n_resamples=n_resamples,
        confidence_level=ci,
        paired=True,
        method="percentile",
    )
    return float(rho), float(pval), res.confidence_interval


def compute_auroc(scores: np.ndarray, labels: np.ndarray) -> float:
    """AUROC; negated scores since lower score = more uncertain = hallucinated."""
    return float(roc_auc_score(labels, -scores))


def compute_rho_differential(
    scores_min: np.ndarray, scores_mean: np.ndarray, labels: np.ndarray,
    n_resamples: int = 1000
) -> Dict:
    """Returns {diff, ci_low, ci_high} for rho(min) - rho(mean)."""
    rho_min,  _, _ = compute_spearman_with_ci(scores_min,  labels, n_resamples=n_resamples)
    rho_mean, _, _ = compute_spearman_with_ci(scores_mean, labels, n_resamples=n_resamples)
    diff = rho_min - rho_mean

    def stat_diff(s_min, s_mean, l):
        rm = spearmanr(s_min,  l).statistic
        rn = spearmanr(s_mean, l).statistic
        return rm - rn

    res = bootstrap(
        (scores_min, scores_mean, labels), stat_diff,
        n_resamples=n_resamples,
        confidence_level=0.95,
        paired=True,
        method="percentile",
    )
    return {
        "diff":   float(diff),
        "ci_low":  float(res.confidence_interval.low),
        "ci_high": float(res.confidence_interval.high),
        "rho_min":  float(rho_min),
        "rho_mean": float(rho_mean),
    }


def gate_check(results: Dict) -> Dict:
    """
    P1: rho(min) > rho(mean) on TriviaQA or NQ for >=1 model
    P2: rho(mean) > rho(min) on TruthfulQA for >=1 model
    Gate: PASS if both, PARTIAL_PASS if one, FAIL if neither.
    """
    p1_met = any(
        results[m].get("trivia_qa", {}).get("rho_min", -99) >
        results[m].get("trivia_qa", {}).get("rho_mean", 99)
        for m in results
    ) or any(
        results[m].get("nq", {}).get("rho_min", -99) >
        results[m].get("nq", {}).get("rho_mean", 99)
        for m in results
    )
    p2_met = any(
        results[m].get("truthful_qa", {}).get("rho_mean", -99) >
        results[m].get("truthful_qa", {}).get("rho_min", 99)
        for m in results
    )

    if p1_met and p2_met:
        gate = "PASS"
    elif p1_met or p2_met:
        gate = "PARTIAL_PASS"
    else:
        gate = "FAIL"

    return {"gate": gate, "p1_met": p1_met, "p2_met": p2_met}
