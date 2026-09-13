"""
Analysis module for H-M2 Percentile-Normalized Monotonicity Attenuation.
Implements zscore normalization, logistic regression for β_percentile, and bootstrap CI/difference tests.
"""

import numpy as np
from scipy.stats import zscore as scipy_zscore
from sklearn.linear_model import LogisticRegression
from sklearn.utils import resample

from config import SEED, BOOTSTRAP_N, LR_C, LR_MAX_ITER, P_VALUE_THRESHOLD


def zscore_normalize(margins: np.ndarray) -> np.ndarray:
    """
    Z-score normalize margins within model.

    Uses scipy.stats.zscore. Returns zeros if std=0 (constant margins edge case).

    Args:
        margins: (N,) float array of raw margin values

    Returns:
        (N,) float array of z-score normalized margins
    """
    std = np.std(margins)
    if std == 0:
        # Edge case: constant margins - return zeros
        return np.zeros_like(margins)
    return scipy_zscore(margins)


def compute_beta_percentile(
    margins: np.ndarray,
    correctness: np.ndarray,
) -> float:
    """
    Compute β coefficient from logistic regression on z-score normalized margins.

    Fits: Pr(correct) = σ(α + β·z(margin))
    where z() is z-score normalization.

    Args:
        margins: (N,) raw logit margin values
        correctness: (N,) binary correctness labels {0, 1}

    Returns:
        β coefficient (coef_[0][0] from LogisticRegression)
    """
    # Step 1: Z-score normalize margins
    margins_normalized = zscore_normalize(margins)

    # Step 2: Fit logistic regression
    lr = LogisticRegression(
        solver='lbfgs',
        C=LR_C,           # Very weak regularization (near unregularized)
        max_iter=LR_MAX_ITER,
        random_state=SEED,
    )
    lr.fit(margins_normalized.reshape(-1, 1), correctness.astype(int))

    # Step 3: Extract β coefficient
    beta_percentile = float(lr.coef_[0][0])
    return beta_percentile


def bootstrap_beta(
    margins: np.ndarray,
    correctness: np.ndarray,
    n_iterations: int = BOOTSTRAP_N,
    seed: int = SEED,
) -> np.ndarray:
    """
    Bootstrap resampling to estimate distribution of β_percentile.

    Args:
        margins: (N,) raw margin values
        correctness: (N,) binary correctness labels
        n_iterations: Number of bootstrap iterations
        seed: Random seed for reproducibility

    Returns:
        (n_iterations,) array of β values from each bootstrap sample
    """
    rng = np.random.RandomState(seed)
    n = len(margins)
    betas = []

    for _ in range(n_iterations):
        idx = resample(np.arange(n), replace=True, random_state=rng)
        beta = compute_beta_percentile(margins[idx], correctness[idx])
        betas.append(beta)

    return np.array(betas)


def compute_bootstrap_ci(
    betas: np.ndarray,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """
    Compute bootstrap confidence interval using percentile method.

    Args:
        betas: (n_iterations,) array of bootstrap β values
        alpha: Significance level (default: 0.05 for 95% CI)

    Returns:
        (beta_mean, ci_lower, ci_upper) tuple
        ci_lower: 2.5th percentile
        ci_upper: 97.5th percentile
    """
    beta_mean = float(np.mean(betas))
    ci_lower = float(np.percentile(betas, 100 * alpha / 2))
    ci_upper = float(np.percentile(betas, 100 * (1 - alpha / 2)))
    return (beta_mean, ci_lower, ci_upper)


def bootstrap_difference_test(
    base_margins: np.ndarray,
    base_correctness: np.ndarray,
    inst_margins: np.ndarray,
    inst_correctness: np.ndarray,
    n_iterations: int = BOOTSTRAP_N,
    seed: int = SEED,
) -> dict[str, float]:
    """
    Paired bootstrap test for β_base - β_instruct difference.

    Uses SAME indices for base and instruct per iteration to preserve pairing.
    This is critical for controlled comparison on the same samples.

    Args:
        base_margins: (N,) base model margins
        base_correctness: (N,) base model correctness
        inst_margins: (N,) instruct model margins
        inst_correctness: (N,) instruct model correctness
        n_iterations: Bootstrap iterations
        seed: Random seed

    Returns:
        Dictionary with:
        - delta_beta_mean: Mean of (β_base - β_instruct)
        - delta_ci_lower: 2.5th percentile of delta
        - delta_ci_upper: 97.5th percentile of delta
        - p_value: Proportion of iterations where Δβ <= 0
        - effect_size: Δβ_mean / std(Δβ) (standardized effect)
    """
    rng = np.random.RandomState(seed)
    n = len(base_margins)
    delta_betas = []

    for _ in range(n_iterations):
        # PAIRED resampling: same indices for base and instruct
        idx = resample(np.arange(n), replace=True, random_state=rng)

        beta_base = compute_beta_percentile(base_margins[idx], base_correctness[idx])
        beta_inst = compute_beta_percentile(inst_margins[idx], inst_correctness[idx])

        delta_betas.append(beta_base - beta_inst)

    delta_betas = np.array(delta_betas)

    delta_mean = float(np.mean(delta_betas))
    delta_ci_lower = float(np.percentile(delta_betas, 2.5))
    delta_ci_upper = float(np.percentile(delta_betas, 97.5))

    # p-value: proportion where delta <= 0 (testing H1: delta > 0, i.e., β_base > β_inst)
    p_value = float(np.mean(delta_betas <= 0))

    # Effect size: standardized by pooled std
    pooled_std = float(np.std(delta_betas))
    if pooled_std > 0:
        effect_size = delta_mean / pooled_std
    else:
        effect_size = 0.0

    return {
        "delta_beta_mean": delta_mean,
        "delta_ci_lower": delta_ci_lower,
        "delta_ci_upper": delta_ci_upper,
        "p_value": p_value,
        "effect_size": effect_size,
    }


def run_2x2_analysis(
    arrays_by_family: dict[str, dict[str, np.ndarray]],
) -> dict[str, dict[str, float]]:
    """
    Compute β_percentile per (family × model_type) cell.

    For 2×2 design: family (qwen/mistral) × model_type (base/instruct)
    Note: Prompt format not available in H-E1 cache, so this is effectively 1×2.

    Args:
        arrays_by_family: {family: {base_margins, base_correctness, ...}}

    Returns:
        {family: {base: β_base, instruct: β_instruct}}
    """
    results = {}

    for family, arrays in arrays_by_family.items():
        beta_base = compute_beta_percentile(
            arrays["base_margins"],
            arrays["base_correctness"]
        )
        beta_inst = compute_beta_percentile(
            arrays["inst_margins"],
            arrays["inst_correctness"]
        )

        results[family] = {
            "base": beta_base,
            "instruct": beta_inst,
        }

    return results


def analyze_family(
    family: str,
    arrays: dict[str, np.ndarray],
) -> dict:
    """
    Full per-family analysis pipeline.

    Steps:
    1. Compute β_percentile for base and instruct
    2. Bootstrap β for confidence intervals
    3. Run paired bootstrap difference test
    4. Determine gate pass/fail

    Args:
        family: Model family name
        arrays: {base_margins, base_correctness, inst_margins, inst_correctness}

    Returns:
        Structured results dict:
        - family: str
        - base_beta: float
        - base_ci: (mean, lower, upper)
        - inst_beta: float
        - inst_ci: (mean, lower, upper)
        - delta_beta: float
        - p_value: float
        - effect_size: float
        - gate_pass: bool (β_inst < β_base AND p < threshold)
        - base_betas: (N,) bootstrap samples (for visualization)
        - inst_betas: (N,) bootstrap samples (for visualization)
    """
    # 1. Compute point estimates
    base_beta = compute_beta_percentile(
        arrays["base_margins"],
        arrays["base_correctness"]
    )
    inst_beta = compute_beta_percentile(
        arrays["inst_margins"],
        arrays["inst_correctness"]
    )

    # 2. Bootstrap for CIs
    base_betas = bootstrap_beta(
        arrays["base_margins"],
        arrays["base_correctness"]
    )
    inst_betas = bootstrap_beta(
        arrays["inst_margins"],
        arrays["inst_correctness"]
    )

    base_ci = compute_bootstrap_ci(base_betas)
    inst_ci = compute_bootstrap_ci(inst_betas)

    # 3. Paired difference test
    diff_result = bootstrap_difference_test(
        arrays["base_margins"],
        arrays["base_correctness"],
        arrays["inst_margins"],
        arrays["inst_correctness"],
    )

    # 4. Gate logic: β_instruct < β_base AND p < threshold
    direction_correct = inst_beta < base_beta
    statistically_significant = diff_result["p_value"] < P_VALUE_THRESHOLD
    gate_pass = direction_correct and statistically_significant

    return {
        "family": family,
        "base_beta": base_beta,
        "base_ci": base_ci,
        "inst_beta": inst_beta,
        "inst_ci": inst_ci,
        "delta_beta": diff_result["delta_beta_mean"],
        "delta_ci_lower": diff_result["delta_ci_lower"],
        "delta_ci_upper": diff_result["delta_ci_upper"],
        "p_value": diff_result["p_value"],
        "effect_size": diff_result["effect_size"],
        "direction_correct": direction_correct,
        "statistically_significant": statistically_significant,
        "gate_pass": gate_pass,
        "base_betas": base_betas,  # For visualization
        "inst_betas": inst_betas,  # For visualization
        "n_samples": len(arrays["base_margins"]),
    }
