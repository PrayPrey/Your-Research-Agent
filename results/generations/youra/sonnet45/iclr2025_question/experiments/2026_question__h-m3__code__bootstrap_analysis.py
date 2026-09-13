"""Bootstrap variance CI estimation module for H-M3.

Task: T-EPIC-03 (A-3: Bootstrap Core Algorithm)
Task: T-EPIC-04 (A-4: Multi-Condition Analysis)
"""

import numpy as np
from typing import Tuple, Dict


def bootstrap_variance_ci(
    data: np.ndarray,
    n_resamples: int,
    confidence_level: float,
    random_seed: int
) -> Tuple[float, float, float, float]:
    """Bootstrap variance estimation with percentile CI.

    Args:
        data: Test accuracy samples (shape: (30,))
        n_resamples: Number of bootstrap iterations (default: 1000)
        confidence_level: CI level (default: 0.95 for 95% CI)
        random_seed: Random seed for reproducibility

    Returns:
        Tuple of (variance_point, ci_lower, ci_upper, ci_width_pct)
    """
    # Set random seed for reproducibility
    np.random.seed(random_seed)

    n = len(data)
    variance_estimates = []

    # Bootstrap resampling
    for _ in range(n_resamples):
        # Resample with replacement
        bootstrap_sample = np.random.choice(data, size=n, replace=True)

        # Compute variance on bootstrap sample (with Bessel's correction)
        variance_estimates.append(np.var(bootstrap_sample, ddof=1))

    variance_estimates = np.array(variance_estimates)

    # Point estimate: mean of bootstrap distribution
    variance_point = compute_variance_point_estimate(variance_estimates)

    # Percentile CI
    ci_lower, ci_upper = compute_percentile_ci(variance_estimates, confidence_level)

    # CI width as percentage of point estimate
    ci_width_pct = ((ci_upper - ci_lower) / variance_point) * 100

    return variance_point, ci_lower, ci_upper, ci_width_pct


def compute_variance_point_estimate(bootstrap_samples: np.ndarray) -> float:
    """Mean of bootstrap variance distribution.

    Args:
        bootstrap_samples: Array of bootstrap variance estimates (shape: (B,))

    Returns:
        Point estimate (mean of bootstrap distribution)
    """
    return np.mean(bootstrap_samples)


def compute_percentile_ci(
    bootstrap_samples: np.ndarray,
    confidence_level: float
) -> Tuple[float, float]:
    """95% CI using [2.5, 97.5] percentiles.

    Args:
        bootstrap_samples: Array of bootstrap variance estimates (shape: (B,))
        confidence_level: CI level (e.g., 0.95)

    Returns:
        Tuple of (ci_lower, ci_upper)
    """
    alpha = 1 - confidence_level
    ci_lower = np.percentile(bootstrap_samples, (alpha / 2) * 100)
    ci_upper = np.percentile(bootstrap_samples, (confidence_level + alpha / 2) * 100)

    return ci_lower, ci_upper


def analyze_all_conditions(
    conditions_data: Dict[str, np.ndarray],
    n_resamples: int,
    confidence_level: float,
    random_seed: int
) -> Dict[str, Dict[str, float]]:
    """Run bootstrap analysis for all 4 conditions.

    Args:
        conditions_data: Dictionary mapping condition names to test accuracy arrays
        n_resamples: Number of bootstrap iterations
        confidence_level: CI level
        random_seed: Random seed for reproducibility

    Returns:
        Dictionary mapping condition names to bootstrap results
    """
    results = {}

    print("\n" + "=" * 60)
    print("BOOTSTRAP ANALYSIS - MULTI-CONDITION PROCESSING")
    print("=" * 60)

    for i, (condition_name, data) in enumerate(conditions_data.items(), 1):
        print(f"\n[{i}/{len(conditions_data)}] Processing: {condition_name}")
        print(f"  - Samples: {len(data)}")
        print(f"  - Mean accuracy: {np.mean(data):.4f}%")
        print(f"  - Running {n_resamples} bootstrap resamples...")

        try:
            variance_point, ci_lower, ci_upper, ci_width_pct = bootstrap_variance_ci(
                data,
                n_resamples,
                confidence_level,
                random_seed
            )

            results[condition_name] = {
                "variance_point": float(variance_point),
                "ci_lower": float(ci_lower),
                "ci_upper": float(ci_upper),
                "ci_width_pct": float(ci_width_pct),
                "n_samples": int(len(data)),
                "n_resamples": int(n_resamples)
            }

            print(f"  ✓ Variance: {variance_point:.6f}")
            print(f"  ✓ CI: [{ci_lower:.6f}, {ci_upper:.6f}]")
            print(f"  ✓ CI Width: {ci_width_pct:.2f}%")

        except Exception as e:
            print(f"  ✗ Error processing {condition_name}: {e}")
            # Continue with other conditions
            continue

    print("\n" + "=" * 60)
    print(f"✓ Bootstrap analysis completed for {len(results)}/{len(conditions_data)} conditions")
    print("=" * 60)

    return results
