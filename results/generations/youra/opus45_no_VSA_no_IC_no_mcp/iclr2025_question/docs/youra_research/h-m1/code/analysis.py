# H-M1 Statistical analysis
import numpy as np
from scipy import stats

def cohens_d(a: list[float], b: list[float]) -> float:
    """Calculate Cohen's d effect size."""
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return 0.0
    pooled_std = np.sqrt(((na-1)*np.std(a, ddof=1)**2 + (nb-1)*np.std(b, ddof=1)**2) / (na+nb-2))
    return (np.mean(b) - np.mean(a)) / pooled_std if pooled_std > 0 else 0.0

def compare_groups(correct_entropy: list[float], incorrect_entropy: list[float]) -> dict:
    """Compare entropy distributions, return stats dict."""
    mean_correct = np.mean(correct_entropy) if correct_entropy else 0.0
    mean_incorrect = np.mean(incorrect_entropy) if incorrect_entropy else 0.0

    d = cohens_d(correct_entropy, incorrect_entropy)

    # Mann-Whitney U (one-sided: incorrect > correct)
    if len(correct_entropy) >= 2 and len(incorrect_entropy) >= 2:
        stat, pvalue = stats.mannwhitneyu(incorrect_entropy, correct_entropy, alternative='greater')
    else:
        stat, pvalue = 0.0, 1.0

    direction_pass = mean_incorrect > mean_correct
    effect_pass = d > 0.2

    return {
        "mean_correct": float(mean_correct),
        "mean_incorrect": float(mean_incorrect),
        "effect_size_d": float(d),
        "pvalue": float(pvalue),
        "direction_pass": direction_pass,
        "effect_pass": effect_pass,
        "gate_pass": direction_pass and effect_pass
    }
