"""Statistical analysis for H-M2: consistency-correctness correlation"""
import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score


def compute_correlation(consistencies: list[float], correctness: list[bool]) -> dict:
    """Compute t-test, AUROC, Cohen's d for consistency vs correctness.

    NOTE: Unlike H-M1 entropy (low entropy = correct), for consistency:
    HIGH consistency = correct (no score inversion needed).
    """
    consistencies = np.array(consistencies)
    correctness = np.array(correctness)

    correct_c = consistencies[correctness]
    incorrect_c = consistencies[~correctness]

    if len(correct_c) == 0 or len(incorrect_c) == 0:
        return {"error": "Need both correct and incorrect samples"}

    # t-test: alternative='greater' because correct > incorrect expected
    t_stat, p_value = stats.ttest_ind(correct_c, incorrect_c, alternative='greater')

    # AUROC: consistency score directly (no inversion)
    auroc = roc_auc_score(correctness.astype(int), consistencies)

    # Cohen's d
    pooled_std = np.sqrt(((len(correct_c) - 1) * np.var(correct_c, ddof=1) +
                          (len(incorrect_c) - 1) * np.var(incorrect_c, ddof=1)) /
                         (len(correct_c) + len(incorrect_c) - 2))
    cohens_d = (np.mean(correct_c) - np.mean(incorrect_c)) / pooled_std if pooled_std > 0 else 0.0

    return {
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "auroc": float(auroc),
        "cohens_d": float(cohens_d),
        "mean_correct": float(np.mean(correct_c)),
        "mean_incorrect": float(np.mean(incorrect_c)),
        "n_correct": int(len(correct_c)),
        "n_incorrect": int(len(incorrect_c))
    }


def pearson_entropy_consistency(entropies: list[float], consistencies: list[float]) -> float:
    """Compute Pearson correlation between entropy and consistency for H-M3 preview."""
    if len(entropies) < 2:
        return 0.0
    r, _ = stats.pearsonr(entropies, consistencies)
    return float(r)
