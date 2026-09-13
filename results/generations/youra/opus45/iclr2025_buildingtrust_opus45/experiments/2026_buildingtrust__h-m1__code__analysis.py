"""
Analysis module for H-M1 Conditional Margin Inflation Analysis.
Implements statistical tests for comparing E[margin|incorrect] between base and instruct models.
"""

import numpy as np
from scipy import stats

from config import SEED, PERMUTATION_N, BOOTSTRAP_N, N_KL_BINS, P_VALUE_THRESHOLD


def compute_conditional_stats(
    margins: np.ndarray,
    correctness: np.ndarray,
) -> dict[str, float]:
    """
    Compute conditional margin statistics partitioned by correctness.

    Args:
        margins: (N,) float array of margin values
        correctness: (N,) int array of correctness labels {0, 1}

    Returns:
        Dictionary with:
        - mean_correct: Mean margin for correct predictions
        - mean_incorrect: Mean margin for incorrect predictions
        - se_correct: Standard error for correct predictions
        - se_incorrect: Standard error for incorrect predictions
        - n_correct: Count of correct predictions
        - n_incorrect: Count of incorrect predictions
    """
    correct_mask = correctness == 1
    incorrect_mask = correctness == 0

    margins_correct = margins[correct_mask]
    margins_incorrect = margins[incorrect_mask]

    n_correct = len(margins_correct)
    n_incorrect = len(margins_incorrect)

    # Compute means
    mean_correct = float(np.mean(margins_correct)) if n_correct > 0 else 0.0
    mean_incorrect = float(np.mean(margins_incorrect)) if n_incorrect > 0 else 0.0

    # Compute standard errors
    se_correct = float(np.std(margins_correct, ddof=1) / np.sqrt(n_correct)) if n_correct > 1 else 0.0
    se_incorrect = float(np.std(margins_incorrect, ddof=1) / np.sqrt(n_incorrect)) if n_incorrect > 1 else 0.0

    return {
        "mean_correct": mean_correct,
        "mean_incorrect": mean_incorrect,
        "se_correct": se_correct,
        "se_incorrect": se_incorrect,
        "n_correct": n_correct,
        "n_incorrect": n_incorrect,
    }


def run_permutation_test(
    base_margins: np.ndarray,
    base_correctness: np.ndarray,
    inst_margins: np.ndarray,
    inst_correctness: np.ndarray,
    n_resamples: int = PERMUTATION_N,
    seed: int = SEED,
) -> dict[str, float]:
    """
    Run one-tailed permutation test comparing E[margin|incorrect] between base and instruct.

    Tests hypothesis: E[margin|incorrect]_instruct > E[margin|incorrect]_base

    Args:
        base_margins: (N_base,) margins from base model
        base_correctness: (N_base,) correctness labels for base
        inst_margins: (N_inst,) margins from instruct model
        inst_correctness: (N_inst,) correctness labels for instruct
        n_resamples: Number of permutation resamples
        seed: Random seed for reproducibility

    Returns:
        Dictionary with:
        - p_value: One-tailed p-value
        - statistic: Test statistic (mean_inst_incorrect - mean_base_incorrect)
    """
    # Extract incorrect predictions only
    base_incorrect_mask = base_correctness == 0
    inst_incorrect_mask = inst_correctness == 0

    base_inc = base_margins[base_incorrect_mask]
    inst_inc = inst_margins[inst_incorrect_mask]

    # Define test statistic: mean difference (inst - base)
    def statistic_fn(x, y, axis):
        return np.mean(x, axis=axis) - np.mean(y, axis=axis)

    # Run permutation test
    result = stats.permutation_test(
        (inst_inc, base_inc),
        statistic=statistic_fn,
        permutation_type="independent",
        alternative="greater",
        n_resamples=n_resamples,
        random_state=seed,
    )

    return {
        "p_value": float(result.pvalue),
        "statistic": float(result.statistic),
    }


def compute_effect_size(
    base_margins_incorrect: np.ndarray,
    inst_margins_incorrect: np.ndarray,
) -> dict[str, float]:
    """
    Compute effect size metrics for margin inflation.

    Args:
        base_margins_incorrect: (M_base,) margins for incorrect base predictions
        inst_margins_incorrect: (M_inst,) margins for incorrect instruct predictions

    Returns:
        Dictionary with:
        - raw_diff: Raw difference in means (inst - base)
        - inflation_ratio: Ratio of means (inst / base)
        - cohens_d: Cohen's d effect size
    """
    mean_base = np.mean(base_margins_incorrect)
    mean_inst = np.mean(inst_margins_incorrect)

    raw_diff = float(mean_inst - mean_base)

    # Inflation ratio (handle edge case of zero/negative base)
    if mean_base > 0:
        inflation_ratio = float(mean_inst / mean_base)
    else:
        inflation_ratio = float("inf") if mean_inst > 0 else 0.0

    # Cohen's d: (M1 - M2) / pooled_std
    var_base = np.var(base_margins_incorrect, ddof=1)
    var_inst = np.var(inst_margins_incorrect, ddof=1)
    n_base = len(base_margins_incorrect)
    n_inst = len(inst_margins_incorrect)

    # Pooled standard deviation
    pooled_var = ((n_base - 1) * var_base + (n_inst - 1) * var_inst) / (n_base + n_inst - 2)
    pooled_std = np.sqrt(pooled_var)

    if pooled_std > 0:
        cohens_d = float(raw_diff / pooled_std)
    else:
        cohens_d = 0.0

    return {
        "raw_diff": raw_diff,
        "inflation_ratio": inflation_ratio,
        "cohens_d": cohens_d,
    }


def compute_bootstrap_ci(
    base_margins_incorrect: np.ndarray,
    inst_margins_incorrect: np.ndarray,
    n_bootstrap: int = BOOTSTRAP_N,
    seed: int = SEED,
) -> dict[str, float]:
    """
    Compute 95% bootstrap confidence interval on mean difference.

    Args:
        base_margins_incorrect: (M_base,) margins for incorrect base predictions
        inst_margins_incorrect: (M_inst,) margins for incorrect instruct predictions
        n_bootstrap: Number of bootstrap samples
        seed: Random seed for reproducibility

    Returns:
        Dictionary with:
        - ci_lower: Lower bound of 95% CI
        - ci_upper: Upper bound of 95% CI
    """
    rng = np.random.default_rng(seed)

    n_base = len(base_margins_incorrect)
    n_inst = len(inst_margins_incorrect)

    diffs = []
    for _ in range(n_bootstrap):
        # Bootstrap resample with replacement
        base_sample = rng.choice(base_margins_incorrect, size=n_base, replace=True)
        inst_sample = rng.choice(inst_margins_incorrect, size=n_inst, replace=True)
        diff = np.mean(inst_sample) - np.mean(base_sample)
        diffs.append(diff)

    diffs = np.array(diffs)
    ci_lower = float(np.percentile(diffs, 2.5))
    ci_upper = float(np.percentile(diffs, 97.5))

    return {
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
    }


def compute_kl_divergence(
    base_margins: np.ndarray,
    inst_margins: np.ndarray,
    n_bins: int = N_KL_BINS,
) -> float:
    """
    Compute KL divergence between base and instruct margin distributions.

    Uses histogram-based approximation.

    Args:
        base_margins: (N_base,) margins from base model
        inst_margins: (N_inst,) margins from instruct model
        n_bins: Number of histogram bins

    Returns:
        KL divergence D_KL(inst || base)
    """
    # Find common bin edges
    all_margins = np.concatenate([base_margins, inst_margins])
    bin_edges = np.linspace(all_margins.min(), all_margins.max(), n_bins + 1)

    # Compute histograms (density)
    base_hist, _ = np.histogram(base_margins, bins=bin_edges, density=True)
    inst_hist, _ = np.histogram(inst_margins, bins=bin_edges, density=True)

    # Add small epsilon to avoid log(0)
    eps = 1e-10
    base_hist = base_hist + eps
    inst_hist = inst_hist + eps

    # Normalize to sum to 1 (after epsilon)
    base_hist = base_hist / base_hist.sum()
    inst_hist = inst_hist / inst_hist.sum()

    # KL divergence: sum(P * log(P / Q))
    kl = float(np.sum(inst_hist * np.log(inst_hist / base_hist)))

    return kl


def analyze_family(
    family: str,
    arrays: dict[str, np.ndarray],
) -> dict:
    """
    Run full per-family analysis pipeline.

    Args:
        family: Model family name
        arrays: Dictionary with base/inst margins and correctness arrays

    Returns:
        Structured results dictionary matching experiment_results.yaml schema
    """
    # 1. Compute conditional stats for both models
    base_stats = compute_conditional_stats(
        arrays["base_margins"],
        arrays["base_correctness"],
    )
    inst_stats = compute_conditional_stats(
        arrays["inst_margins"],
        arrays["inst_correctness"],
    )

    # 2. Run permutation test
    perm_result = run_permutation_test(
        arrays["base_margins"],
        arrays["base_correctness"],
        arrays["inst_margins"],
        arrays["inst_correctness"],
    )

    # 3. Extract incorrect predictions for effect size
    base_inc = arrays["base_margins"][arrays["base_correctness"] == 0]
    inst_inc = arrays["inst_margins"][arrays["inst_correctness"] == 0]

    # 4. Compute effect size
    effect = compute_effect_size(base_inc, inst_inc)

    # 5. Compute bootstrap CI
    ci = compute_bootstrap_ci(base_inc, inst_inc)

    # 6. Compute KL divergence (on full distributions)
    kl = compute_kl_divergence(arrays["base_margins"], arrays["inst_margins"])

    # 7. Also compute KL on incorrect subsets
    kl_incorrect = compute_kl_divergence(base_inc, inst_inc) if len(base_inc) > 0 and len(inst_inc) > 0 else 0.0

    # 8. Determine gate pass
    direction_correct = inst_stats["mean_incorrect"] > base_stats["mean_incorrect"]
    statistically_significant = perm_result["p_value"] < P_VALUE_THRESHOLD
    gate_pass = direction_correct and statistically_significant

    # Build result structure
    result = {
        "family": family,
        "base_stats": base_stats,
        "inst_stats": inst_stats,
        "permutation_test": perm_result,
        "effect_size": effect,
        "bootstrap_ci": ci,
        "kl_divergence": kl,
        "kl_divergence_incorrect": kl_incorrect,
        "direction_correct": direction_correct,
        "statistically_significant": statistically_significant,
        "gate_pass": gate_pass,
        "n_samples": len(arrays["base_margins"]),
    }

    return result
