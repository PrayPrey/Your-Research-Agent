"""Evaluation metrics: AUROC, AUPRC, ECE, bootstrap CI, gate check."""
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.calibration import calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from scipy.stats import bootstrap as scipy_bootstrap

from aggregation import aggregate


def compute_auroc(labels: np.ndarray, scores: np.ndarray) -> float:
    """Compute AUROC. Returns 0.5 if only one class present."""
    if len(np.unique(labels)) < 2:
        return 0.5
    return float(roc_auc_score(labels, scores))


def compute_auprc(labels: np.ndarray, scores: np.ndarray) -> float:
    """Compute AUPRC (average precision)."""
    if len(np.unique(labels)) < 2:
        return float(np.mean(labels))
    return float(average_precision_score(labels, scores))


def compute_ece(labels: np.ndarray, scores: np.ndarray, n_bins: int = 15) -> float:
    """
    Compute ECE after Platt scaling (logistic regression calibration).
    Returns ECE in [0, 1].
    """
    if len(np.unique(labels)) < 2:
        return float("nan")
    try:
        scaler = StandardScaler()
        X = scaler.fit_transform(scores.reshape(-1, 1))
        clf = LogisticRegression()
        clf.fit(X, labels)
        probs = clf.predict_proba(X)[:, 1]
        fraction_of_positives, mean_predicted_value = calibration_curve(
            labels, probs, n_bins=n_bins, strategy="uniform"
        )
        ece = float(np.mean(np.abs(fraction_of_positives - mean_predicted_value)))
    except Exception:
        ece = float("nan")
    return ece


def bootstrap_auroc_diff(
    scores_a: np.ndarray,
    scores_b: np.ndarray,
    labels: np.ndarray,
    n_resamples: int = 1000,
) -> Tuple[float, float]:
    """
    Bootstrap 95% CI for AUROC(scores_a) - AUROC(scores_b).
    Returns (ci_lower, ci_upper).
    """
    idx = np.arange(len(labels))

    def stat(idx_sample):
        idx_sample = idx_sample.astype(int)
        lab = labels[idx_sample]
        if len(np.unique(lab)) < 2:
            return 0.0
        return (roc_auc_score(lab, scores_a[idx_sample])
                - roc_auc_score(lab, scores_b[idx_sample]))

    result = scipy_bootstrap(
        (idx,), stat,
        n_resamples=n_resamples,
        confidence_level=0.95,
        method="percentile",
        random_state=42,
    )
    return float(result.confidence_interval.low), float(result.confidence_interval.high)


def evaluate_cell(labels: np.ndarray, scores: np.ndarray) -> Dict:
    """Returns {auroc, auprc, ece} for one (model x dataset x aggregation) cell."""
    return {
        "auroc": compute_auroc(labels, scores),
        "auprc": compute_auprc(labels, scores),
        "ece": compute_ece(labels, scores),
    }


def compute_all_pairwise_ci(
    method_scores: Dict[str, np.ndarray],
    labels: np.ndarray,
    n_resamples: int = 1000,
) -> Dict[str, Tuple[float, float]]:
    """Compute bootstrap CI for all 3 pairwise AUROC differences."""
    pairs = [("min", "mean"), ("min", "sum"), ("mean", "sum")]
    out = {}
    for a, b in pairs:
        key = f"{a}_vs_{b}"
        ci = bootstrap_auroc_diff(method_scores[a], method_scores[b], labels, n_resamples)
        out[key] = ci
    return out


def length_stratified_auroc(
    records: List[Dict],
    method: str,
    threshold: int = 5,
) -> Dict:
    """
    Compute AUROC for short (T <= threshold) and long (T > threshold) answers.
    Returns {"short": auroc, "long": auroc, "n_short": int, "n_long": int}
    """
    short = [(r, aggregate(r["logprobs"], method)) for r in records if len(r["logprobs"]) <= threshold]
    long_ = [(r, aggregate(r["logprobs"], method)) for r in records if len(r["logprobs"]) > threshold]

    def safe_auroc(subset):
        if len(subset) < 10:
            return None
        labels = np.array([r["label"] for r, _ in subset])
        scores = -np.array([s for _, s in subset])
        if len(np.unique(labels)) < 2:
            return None
        return float(roc_auc_score(labels, scores))

    return {
        "short": safe_auroc(short),
        "long": safe_auroc(long_),
        "n_short": len(short),
        "n_long": len(long_),
    }


def check_gate(
    ci_table: Dict,
    auroc_table: Dict,
    diff_threshold: float = 0.02,
) -> Tuple[bool, str]:
    """
    H-E1 gate: pass if any pairwise diff >= threshold AND ci_lower > 0.

    Args:
        ci_table: {model: {dataset: {pair_key: (ci_lower, ci_upper)}}}
        auroc_table: {model: {dataset: {method: auroc_value}}}

    Returns:
        (passed: bool, justification: str)
    """
    pairs = [("min", "mean"), ("min", "sum"), ("mean", "sum")]
    for model in auroc_table:
        for dataset in auroc_table[model]:
            aurocs = auroc_table[model][dataset]
            cis = ci_table.get(model, {}).get(dataset, {})
            for a, b in pairs:
                diff = aurocs[a] - aurocs[b]
                pair_key = f"{a}_vs_{b}"
                if pair_key in cis:
                    ci_lower, _ = cis[pair_key]
                    if abs(diff) >= diff_threshold and ci_lower > 0:
                        return True, (
                            f"PASS: {model}/{dataset} {a} vs {b}: "
                            f"diff={diff:.4f}, CI_lower={ci_lower:.4f}"
                        )
    return False, "FAIL: No pairwise diff >= 0.02 with CI_lower > 0 found"
