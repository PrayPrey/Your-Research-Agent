"""H-C1 analysis: frozen PC1 projection and holdout loading computation."""
import numpy as np
from scipy.stats import pearsonr
from typing import Optional


LOADING_THRESHOLD = 0.3
MIN_SUCCESSFUL_BENCHMARKS = 2
N_BOOTSTRAP = 1000
RANDOM_SEED = 42


def compute_pc1_scores(residualized_matrix: np.ndarray, loadings: np.ndarray) -> np.ndarray:
    """
    Project residualized matrix onto frozen PC1.

    PC1 scores = residualized_matrix @ loadings (dot product)
    This is equivalent to PCA.transform() when loadings are the first component.
    """
    return residualized_matrix @ loadings


def compute_holdout_loading(pc1_scores: np.ndarray, benchmark_scores: np.ndarray) -> tuple[float, float]:
    """
    Compute Pearson correlation between PC1 scores and holdout benchmark.
    Returns (loading, p_value).
    """
    benchmark_std = (benchmark_scores - benchmark_scores.mean()) / benchmark_scores.std()
    r, p = pearsonr(pc1_scores, benchmark_std)
    return float(r), float(p)


def bootstrap_ci(
    pc1_scores: np.ndarray,
    benchmark_scores: np.ndarray,
    n_boot: int = N_BOOTSTRAP,
    seed: int = RANDOM_SEED,
    alpha: float = 0.05
) -> tuple[float, float]:
    """
    Bootstrap 95% CI for the loading (Pearson r).
    Returns (ci_lower, ci_upper).
    """
    rng = np.random.default_rng(seed)
    n = len(pc1_scores)
    benchmark_std = (benchmark_scores - benchmark_scores.mean()) / benchmark_scores.std()

    boot_r = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.choice(n, n, replace=True)
        boot_r[i], _ = pearsonr(pc1_scores[idx], benchmark_std[idx])

    ci_lower = float(np.percentile(boot_r, 100 * alpha / 2))
    ci_upper = float(np.percentile(boot_r, 100 * (1 - alpha / 2)))
    return ci_lower, ci_upper


def run_all_holdouts(
    pc1_scores: np.ndarray,
    holdout_df,
    holdout_cols: list[str]
) -> dict:
    """
    Compute loading, p-value, and CI for each holdout benchmark.
    Returns dict: {benchmark_name: {loading, p_value, ci_lower, ci_upper}}
    """
    results = {}
    for col in holdout_cols:
        scores = holdout_df[col].values
        loading, p_value = compute_holdout_loading(pc1_scores, scores)
        ci_lower, ci_upper = bootstrap_ci(pc1_scores, scores)
        results[col] = {
            "loading": loading,
            "p_value": p_value,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "passes_threshold": loading >= LOADING_THRESHOLD,
        }
    return results


def evaluate_gate(
    loadings: dict[str, dict],
    threshold: float = LOADING_THRESHOLD,
    min_pass: int = MIN_SUCCESSFUL_BENCHMARKS
) -> dict:
    """
    Evaluate SHOULD_WORK gate.
    Returns {verdict, n_passing, n_total, passing_benchmarks}.
    """
    passing = [name for name, data in loadings.items() if data["loading"] >= threshold]
    n_passing = len(passing)

    return {
        "verdict": "PASS" if n_passing >= min_pass else "FAIL",
        "n_passing": n_passing,
        "n_total": len(loadings),
        "threshold": threshold,
        "min_required": min_pass,
        "passing_benchmarks": passing,
    }
