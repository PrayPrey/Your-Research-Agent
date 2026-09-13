"""Statistical analysis: t-test, AUROC, Cohen's d, Pearson r"""
import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score


def compute_correlation(entropies: list[float], correctness: list[bool]) -> dict:
    """Compute entropy-correctness correlation statistics."""
    entropies = np.array(entropies)
    correctness = np.array(correctness, dtype=bool)

    correct_e = entropies[correctness]
    incorrect_e = entropies[~correctness]

    if len(correct_e) == 0 or len(incorrect_e) == 0:
        return {"error": "Need both correct and incorrect samples"}

    # t-test: incorrect should have higher entropy
    t_stat, p_value = stats.ttest_ind(incorrect_e, correct_e)

    # AUROC: low entropy = correct, so use negative entropy as score
    y_true = correctness.astype(int)
    y_scores = -entropies  # invert: low entropy = high confidence = correct
    auroc = roc_auc_score(y_true, y_scores)

    # Cohen's d
    n1, n2 = len(incorrect_e), len(correct_e)
    pooled_std = np.sqrt(((n1 - 1) * np.var(incorrect_e, ddof=1) +
                          (n2 - 1) * np.var(correct_e, ddof=1)) / (n1 + n2 - 2))
    cohens_d = (np.mean(incorrect_e) - np.mean(correct_e)) / pooled_std if pooled_std > 0 else 0

    # Pearson r
    pearson_r, _ = stats.pearsonr(entropies, correctness.astype(float))

    return {
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "auroc": float(auroc),
        "cohens_d": float(cohens_d),
        "pearson_r": float(pearson_r),
        "mean_correct": float(np.mean(correct_e)),
        "mean_incorrect": float(np.mean(incorrect_e)),
        "n_correct": int(len(correct_e)),
        "n_incorrect": int(len(incorrect_e))
    }
