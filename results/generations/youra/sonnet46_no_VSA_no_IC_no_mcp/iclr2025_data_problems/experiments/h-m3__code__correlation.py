"""correlation.py — A-2: Pearson/Spearman correlation analysis with bootstrap CI."""
from dataclasses import dataclass
from typing import Optional
import numpy as np
from scipy import stats


BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
MODEL_SIZES = ["160m", "410m", "1b", "6.9b"]


@dataclass
class CorrelationResult:
    pearson_r: float
    pearson_p: float
    spearman_rho: float
    spearman_p: float
    n_observations: int
    bootstrap_ci_95: Optional[tuple[float, float]] = None

    def to_dict(self) -> dict:
        return {
            "pearson_r": self.pearson_r,
            "pearson_p": self.pearson_p,
            "spearman_rho": self.spearman_rho,
            "spearman_p": self.spearman_p,
            "n_observations": self.n_observations,
            "bootstrap_ci_95": list(self.bootstrap_ci_95) if self.bootstrap_ci_95 else None,
        }


def pearson_spearman(
    cont_vec: np.ndarray,
    diff_vec: np.ndarray,
) -> CorrelationResult:
    """Compute Pearson and Spearman correlations on paired vectors."""
    if len(cont_vec) != len(diff_vec):
        raise ValueError(f"Vector length mismatch: {len(cont_vec)} vs {len(diff_vec)}")
    if np.any(np.isnan(cont_vec) | np.isnan(diff_vec)):
        raise ValueError("NaN values in input vectors")

    pearson_r, pearson_p = stats.pearsonr(cont_vec, diff_vec)
    spearman_rho, spearman_p = stats.spearmanr(cont_vec, diff_vec)

    return CorrelationResult(
        pearson_r=float(pearson_r),
        pearson_p=float(pearson_p),
        spearman_rho=float(spearman_rho),
        spearman_p=float(spearman_p),
        n_observations=len(cont_vec),
    )


def bootstrap_ci(
    cont_vec: np.ndarray,
    diff_vec: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 42,
) -> tuple[tuple[float, float], np.ndarray]:
    """Bootstrap 95% CI on Pearson r via resampling with replacement.
    Returns: ((ci_lower, ci_upper), boot_r_distribution)
    """
    if len(cont_vec) != len(diff_vec):
        raise ValueError("Vector length mismatch")
    if np.any(np.isnan(cont_vec) | np.isnan(diff_vec)):
        raise ValueError("NaN values in input vectors")

    rng = np.random.default_rng(seed)
    n = len(cont_vec)
    boot_r = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        r, _ = stats.pearsonr(cont_vec[idx], diff_vec[idx])
        boot_r.append(r)

    boot_r_arr = np.array(boot_r)
    ci_lower = float(np.percentile(boot_r_arr, 2.5))
    ci_upper = float(np.percentile(boot_r_arr, 97.5))
    return (ci_lower, ci_upper), boot_r_arr


def directional_check(
    cont_vec: np.ndarray,
    diff_matrix: np.ndarray,
) -> dict:
    """Check whether high-contamination benchmarks show negative accuracy differential.
    cont_vec: (4,), diff_matrix: (4 model_sizes, 4 benchmarks)
    """
    mean_diff_per_benchmark = diff_matrix.mean(axis=0)  # (4,)
    cont_ranks = stats.rankdata(cont_vec)
    diff_ranks = stats.rankdata(mean_diff_per_benchmark)

    # Count concordant pairs: high contamination predicts negative (lower) differential
    n_pairs = 0
    n_correct = 0
    for i in range(4):
        for j in range(i + 1, 4):
            n_pairs += 1
            if (cont_vec[i] > cont_vec[j]) == (mean_diff_per_benchmark[i] < mean_diff_per_benchmark[j]):
                n_correct += 1

    fraction_correct = n_correct / n_pairs if n_pairs > 0 else 0.0
    benchmark_signs = {b: float(mean_diff_per_benchmark[i]) for i, b in enumerate(BENCHMARKS)}

    return {
        "n_correct_direction": fraction_correct,
        "n_concordant_pairs": n_correct,
        "n_total_pairs": n_pairs,
        "benchmark_signs": benchmark_signs,
        "contamination_rank": cont_ranks.tolist(),
        "differential_mean_rank": diff_ranks.tolist(),
    }


if __name__ == "__main__":
    import numpy as np
    # Self-check: perfectly anti-correlated vectors should give r=-1
    x = np.array([1.0, 2.0, 3.0, 4.0] * 4)
    y = -x + np.random.default_rng(0).normal(0, 0.01, 16)
    res = pearson_spearman(x, y)
    assert res.pearson_r < -0.99, f"Expected r≈-1, got {res.pearson_r}"
    ci, dist = bootstrap_ci(x, y)
    assert ci[0] < res.pearson_r < ci[1] or (ci[0] < -0.99), "CI check"
    print(f"correlation.py self-check OK: r={res.pearson_r:.4f}, CI=[{ci[0]:.4f},{ci[1]:.4f}]")
