"""Statistical evaluation for H-M1 gate check."""

import numpy as np
from scipy.stats import mannwhitneyu
from sklearn.metrics import roc_auc_score
from config import P_VALUE_THRESHOLD, COHENS_D_THRESHOLD


def cohens_d(correct: np.ndarray, incorrect: np.ndarray) -> float:
    """Pooled-std Cohen's d effect size."""
    n1, n2 = len(correct), len(incorrect)
    if n1 < 2 or n2 < 2:
        return 0.0

    var1 = np.var(correct, ddof=1)
    var2 = np.var(incorrect, ddof=1)

    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    if pooled_std == 0:
        return 0.0

    d = (np.mean(incorrect) - np.mean(correct)) / pooled_std
    return float(d)


def mann_whitney_test(correct: np.ndarray, incorrect: np.ndarray) -> tuple:
    """One-sided Mann-Whitney U test (incorrect > correct).

    Returns: (statistic, p_value)
    """
    if len(correct) < 2 or len(incorrect) < 2:
        return 0.0, 1.0

    statistic, p_value = mannwhitneyu(incorrect, correct, alternative='greater')
    return float(statistic), float(p_value)


def compute_auroc(entropies: np.ndarray, labels: np.ndarray) -> float:
    """AUROC for entropy as incorrectness predictor.

    labels: 1=incorrect (higher entropy expected), 0=correct
    """
    if len(np.unique(labels)) < 2:
        return 0.5

    return float(roc_auc_score(labels, entropies))


def evaluate_gate(entropy_correct: np.ndarray, entropy_incorrect: np.ndarray) -> dict:
    """Full gate evaluation for H-M1.

    Returns dict with all metrics and gate_passed boolean.
    """
    statistic, p_value = mann_whitney_test(entropy_correct, entropy_incorrect)
    d = cohens_d(entropy_correct, entropy_incorrect)

    # Combine for AUROC
    all_entropies = np.concatenate([entropy_correct, entropy_incorrect])
    labels = np.concatenate([np.zeros(len(entropy_correct)), np.ones(len(entropy_incorrect))])
    auroc = compute_auroc(all_entropies, labels)

    # Gate check: p < 0.05 AND d > 0.3
    gate_passed = (p_value < P_VALUE_THRESHOLD) and (d > COHENS_D_THRESHOLD)

    return {
        "statistic": statistic,
        "p_value": p_value,
        "cohens_d": d,
        "auroc": auroc,
        "mean_entropy_correct": float(np.mean(entropy_correct)),
        "mean_entropy_incorrect": float(np.mean(entropy_incorrect)),
        "std_entropy_correct": float(np.std(entropy_correct)),
        "std_entropy_incorrect": float(np.std(entropy_incorrect)),
        "n_correct": len(entropy_correct),
        "n_incorrect": len(entropy_incorrect),
        "gate_passed": gate_passed,
        "gate_type": "MUST_WORK",
        "gate_criteria": f"p < {P_VALUE_THRESHOLD} AND d > {COHENS_D_THRESHOLD}"
    }
