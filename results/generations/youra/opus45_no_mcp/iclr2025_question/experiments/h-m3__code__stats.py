"""Statistical analysis for H-M3 fusion evaluation."""
import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score

from fusion import LinearFusionScorer


def compute_correlation(consistencies: list, correctness: list) -> dict:
    """T-test, AUROC, Cohen's d for consistency vs correctness."""
    consistencies = np.array(consistencies)
    correctness = np.array(correctness, dtype=bool)

    correct_vals = consistencies[correctness]
    incorrect_vals = consistencies[~correctness]

    if len(correct_vals) < 2 or len(incorrect_vals) < 2:
        return {"error": "insufficient samples"}

    t_stat, p_value = stats.ttest_ind(correct_vals, incorrect_vals)

    try:
        auroc = roc_auc_score(correctness, consistencies)
    except ValueError:
        auroc = 0.5

    pooled_std = np.sqrt(
        ((len(correct_vals) - 1) * np.var(correct_vals, ddof=1) +
         (len(incorrect_vals) - 1) * np.var(incorrect_vals, ddof=1)) /
        (len(correct_vals) + len(incorrect_vals) - 2)
    )
    cohens_d = (np.mean(correct_vals) - np.mean(incorrect_vals)) / pooled_std if pooled_std > 0 else 0

    return {
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "auroc": float(auroc),
        "cohens_d": float(cohens_d),
        "mean_correct": float(np.mean(correct_vals)),
        "mean_incorrect": float(np.mean(incorrect_vals)),
    }


def pearson_entropy_consistency(entropies: list, consistencies: list) -> float:
    """Pearson correlation between entropy and consistency."""
    r, _ = stats.pearsonr(entropies, consistencies)
    return float(r)


def evaluate_variants(
    entropy: np.ndarray,
    consistency: np.ndarray,
    labels: np.ndarray,
    alpha_beta_pairs: dict,
) -> dict:
    """Compute AUROC per named (alpha,beta) variant."""
    results = {}
    for name, (alpha, beta) in alpha_beta_pairs.items():
        scorer = LinearFusionScorer(alpha, beta)
        scores = scorer.compute_scores(entropy, consistency)
        try:
            auroc = roc_auc_score(labels, scores)
        except ValueError:
            auroc = 0.5
        results[name] = {"auroc": float(auroc), "scores": scores}
    return results


def bootstrap_ci_improvement(
    labels: np.ndarray,
    scores_a: np.ndarray,
    scores_b: np.ndarray,
    n_boot: int = 1000,
    seed: int = 42,
) -> dict:
    """Bootstrap CI for AUROC(scores_a) - AUROC(scores_b)."""
    rng = np.random.RandomState(seed)
    n = len(labels)
    diffs = []

    for _ in range(n_boot):
        idx = rng.randint(0, n, n)
        boot_labels = labels[idx]
        if len(np.unique(boot_labels)) < 2:
            continue  # skip degenerate resamples
        try:
            auroc_a = roc_auc_score(boot_labels, scores_a[idx])
            auroc_b = roc_auc_score(boot_labels, scores_b[idx])
            diffs.append(auroc_a - auroc_b)
        except ValueError:
            continue

    if len(diffs) == 0:
        return {"improvement": 0.0, "ci_low": 0.0, "ci_high": 0.0}

    diffs = np.array(diffs)
    return {
        "improvement": float(np.mean(diffs)),
        "ci_low": float(np.percentile(diffs, 2.5)),
        "ci_high": float(np.percentile(diffs, 97.5)),
    }
