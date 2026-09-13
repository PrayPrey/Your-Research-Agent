"""Statistical analysis: Welch's t-test, Cohen's d, bootstrap CI."""

import numpy as np
from scipy import stats
from config import CONFIG


def cohen_d(x: np.ndarray, y: np.ndarray) -> float:
    """Pooled-SD Cohen's d for independent samples."""
    nx, ny = len(x), len(y)
    dof = nx + ny - 2
    pooled_std = np.sqrt(
        ((nx - 1) * np.std(x, ddof=1) ** 2 + (ny - 1) * np.std(y, ddof=1) ** 2) / dof
    )
    return (np.mean(x) - np.mean(y)) / pooled_std


def bootstrap_ci_d(
    x: np.ndarray, y: np.ndarray, n_boot: int = None, seed: int = None
) -> tuple[float, float]:
    """95% CI for Cohen's d via percentile bootstrap."""
    if n_boot is None:
        n_boot = CONFIG["bootstrap_samples"]
    if seed is None:
        seed = CONFIG["seed"]

    rng = np.random.default_rng(seed)
    d_values = []

    for _ in range(n_boot):
        x_boot = rng.choice(x, size=len(x), replace=True)
        y_boot = rng.choice(y, size=len(y), replace=True)
        d_values.append(cohen_d(x_boot, y_boot))

    return float(np.percentile(d_values, 2.5)), float(np.percentile(d_values, 97.5))


def run_statistical_analysis(sim_mode1: np.ndarray, sim_mode3: np.ndarray) -> dict:
    """Full statistical analysis: Welch's t-test + Cohen's d + bootstrap CI."""
    t_stat, p_value = stats.ttest_ind(sim_mode1, sim_mode3, equal_var=False)

    d = cohen_d(sim_mode1, sim_mode3)
    ci_lo, ci_hi = bootstrap_ci_d(sim_mode1, sim_mode3)

    if d > 0.3 and p_value < 0.05:
        result = "CONFIRMED"
    elif d < 0.1 or d < 0:
        result = "FALSIFIED"
    else:
        result = "INCONCLUSIVE"

    if abs(d) > 0.8:
        effect = "large"
    elif abs(d) > 0.5:
        effect = "medium"
    elif abs(d) > 0.2:
        effect = "small"
    else:
        effect = "negligible"

    return {
        "hypothesis_id": "h-m1",
        "mode_1_n": len(sim_mode1),
        "mode_3_n": len(sim_mode3),
        "mode_1_mean_similarity": float(np.mean(sim_mode1)),
        "mode_3_mean_similarity": float(np.mean(sim_mode3)),
        "mode_1_std": float(np.std(sim_mode1, ddof=1)),
        "mode_3_std": float(np.std(sim_mode3, ddof=1)),
        "cohens_d": float(d),
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "ci_95_d": [ci_lo, ci_hi],
        "result": result,
        "effect_interpretation": effect,
    }
