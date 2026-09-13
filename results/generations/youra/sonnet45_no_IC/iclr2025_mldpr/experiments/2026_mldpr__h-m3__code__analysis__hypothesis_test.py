"""
Statistical Hypothesis Testing Module (M3-6, M3-7, M3-8)
Mann-Whitney U Test, Cohen's d Effect Size, Spearman Correlation.
"""

import numpy as np
from scipy.stats import mannwhitneyu, spearmanr
from typing import Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def mann_whitney_test(high_cv: np.ndarray, low_cv: np.ndarray,
                     alternative: str = "less") -> Dict:
    """
    Mann-Whitney U test comparing CV distributions.

    H0: No difference in CV between groups
    H1: CV_high < CV_low (one-tailed test)

    Args:
        high_cv: CV values for high-artifact benchmarks
        low_cv: CV values for low-artifact benchmarks
        alternative: 'less' (CV_high < CV_low), 'two-sided', 'greater'

    Returns:
        Dict with statistic, p_value, significant
    """
    statistic, p_value = mannwhitneyu(high_cv, low_cv, alternative=alternative)

    logger.info(f"\nMann-Whitney U Test (alternative={alternative}):")
    logger.info(f"  U-statistic: {statistic:.2f}")
    logger.info(f"  p-value: {p_value:.4f}")
    logger.info(f"  Significant (α=0.05): {p_value < 0.05}")

    return {
        "test": "Mann-Whitney U",
        "statistic": float(statistic),
        "p_value": float(p_value),
        "significant": p_value < 0.05,
        "alpha": 0.05
    }


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> Tuple[float, str]:
    """
    Calculate Cohen's d effect size.

    Formula: d = (μ1 - μ2) / σ_pooled
    Pooled SD: sqrt((σ1² + σ2²) / 2)

    Args:
        group1: First group values
        group2: Second group values

    Returns:
        Tuple of (effect_size, interpretation)
    """
    mean1 = np.mean(group1)
    mean2 = np.mean(group2)
    std1 = np.std(group1, ddof=1)
    std2 = np.std(group2, ddof=1)

    # Pooled standard deviation
    pooled_std = np.sqrt((std1**2 + std2**2) / 2)

    # Cohen's d
    d = (mean1 - mean2) / pooled_std

    # Interpretation
    if abs(d) < 0.2:
        interpretation = "negligible"
    elif abs(d) < 0.5:
        interpretation = "small"
    elif abs(d) < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"

    logger.info(f"\nCohen's d Effect Size:")
    logger.info(f"  d = {d:.3f} ({interpretation})")
    logger.info(f"  Mean group1: {mean1:.4f}")
    logger.info(f"  Mean group2: {mean2:.4f}")
    logger.info(f"  Pooled SD: {pooled_std:.4f}")

    return float(d), interpretation


def spearman_correlation(artifact_count: np.ndarray, cv: np.ndarray) -> Dict:
    """
    Spearman correlation for dose-response analysis.

    Tests relationship between artifact count (0-3) and CV.
    Expected: Negative correlation (more artifacts → lower CV).

    Args:
        artifact_count: Artifact count (0-3) per benchmark
        cv: CV values per benchmark

    Returns:
        Dict with rho, p_value, significant
    """
    rho, p_value = spearmanr(artifact_count, cv)

    logger.info(f"\nSpearman Correlation (Dose-Response):")
    logger.info(f"  ρ (rho): {rho:.3f}")
    logger.info(f"  p-value: {p_value:.4f}")
    logger.info(f"  Significant (α=0.05): {p_value < 0.05}")
    logger.info(f"  Direction: {'Negative (expected)' if rho < 0 else 'Positive (unexpected)'}")

    return {
        "test": "Spearman Correlation",
        "rho": float(rho),
        "p_value": float(p_value),
        "significant": p_value < 0.05,
        "direction": "negative" if rho < 0 else "positive",
        "alpha": 0.05
    }


def run_primary_analysis(df):
    """
    Run primary statistical analysis (Mann-Whitney + Cohen's d).

    Args:
        df: DataFrame with 'cv' and 'artifact_group' columns

    Returns:
        Dict with test results
    """
    high_cv = df[df["artifact_group"] == "high"]["cv"].values
    low_cv = df[df["artifact_group"] == "low"]["cv"].values

    logger.info(f"\nPrimary Analysis Sample Sizes:")
    logger.info(f"  High artifact: n={len(high_cv)}")
    logger.info(f"  Low artifact: n={len(low_cv)}")

    # Mann-Whitney U Test
    mw_result = mann_whitney_test(high_cv, low_cv, alternative="less")

    # Cohen's d Effect Size (low - high, so positive d = low > high CV)
    d, interpretation = cohens_d(low_cv, high_cv)

    return {
        "mann_whitney": mw_result,
        "cohens_d": {
            "effect_size": d,
            "interpretation": interpretation,
            "threshold": 0.5,
            "passes_gate": abs(d) > 0.5
        }
    }


def run_secondary_analysis(df):
    """
    Run secondary analysis (Spearman dose-response).

    Args:
        df: DataFrame with 'artifact_count' and 'cv' columns

    Returns:
        Dict with correlation results
    """
    artifact_count = df["artifact_count"].values
    cv = df["cv"].values

    logger.info(f"\nSecondary Analysis (Dose-Response):")
    logger.info(f"  Sample size: n={len(df)}")

    # Spearman Correlation
    spearman_result = spearman_correlation(artifact_count, cv)

    return {
        "spearman": spearman_result
    }


def evaluate_gate_conditions(primary_results: Dict, gate_type: str = "SHOULD_WORK") -> Dict:
    """
    Evaluate gate conditions based on test results.

    Args:
        primary_results: Dict with Mann-Whitney and Cohen's d results
        gate_type: MUST_WORK or SHOULD_WORK

    Returns:
        Dict with gate verdict and rationale
    """
    mw = primary_results["mann_whitney"]
    cd = primary_results["cohens_d"]

    # Gate logic: (p < 0.05) AND (|d| > 0.5)
    passes_significance = mw["significant"]
    passes_effect_size = cd["passes_gate"]

    gate_satisfied = passes_significance and passes_effect_size

    logger.info(f"\n{'='*60}")
    logger.info(f"GATE EVALUATION ({gate_type})")
    logger.info(f"{'='*60}")
    logger.info(f"Criterion 1 (Significance): {'PASS' if passes_significance else 'FAIL'}")
    logger.info(f"  Mann-Whitney p={mw['p_value']:.4f} {'<' if passes_significance else '>='} 0.05")
    logger.info(f"Criterion 2 (Effect Size): {'PASS' if passes_effect_size else 'FAIL'}")
    logger.info(f"  Cohen's d={cd['effect_size']:.3f} {'>' if passes_effect_size else '<='} 0.5")
    logger.info(f"\nGate Result: {'PASS' if gate_satisfied else 'FAIL'}")
    logger.info(f"{'='*60}")

    return {
        "gate_type": gate_type,
        "gate_satisfied": gate_satisfied,
        "criteria": {
            "significance": passes_significance,
            "effect_size": passes_effect_size
        },
        "rationale": f"Mann-Whitney p={mw['p_value']:.4f}, Cohen's d={cd['effect_size']:.3f}"
    }


if __name__ == "__main__":
    import pandas as pd
    import os

    # Load variance results
    data_path = "../outputs/variance_results.csv"
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Variance results not found: {data_path}")

    df = pd.read_csv(data_path)

    # Run analyses
    primary_results = run_primary_analysis(df)
    secondary_results = run_secondary_analysis(df)

    # Evaluate gate
    gate_results = evaluate_gate_conditions(primary_results, gate_type="SHOULD_WORK")

    # Combine all results
    all_results = {
        "primary": primary_results,
        "secondary": secondary_results,
        "gate": gate_results
    }

    # Save results
    import json
    output_path = "../outputs/hypothesis_test_results.json"
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✓ Hypothesis test results saved to: {output_path}")
