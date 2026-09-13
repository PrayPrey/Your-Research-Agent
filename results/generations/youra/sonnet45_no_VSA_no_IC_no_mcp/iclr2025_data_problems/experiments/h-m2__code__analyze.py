"""Compute transfer deltas and perform statistical analysis."""

import pandas as pd
import numpy as np
import yaml
from scipy.stats import ttest_ind

def compute_transfer_delta(acc_transferred, acc_tuned):
    """Delta = |transferred - tuned| / tuned * 100%"""
    return abs(acc_transferred - acc_tuned) / acc_tuned * 100.0

def bootstrap_ci(deltas, n_resamples=10000, confidence=0.95):
    """Bootstrap confidence interval."""
    bootstrapped = np.random.choice(deltas, size=(n_resamples, len(deltas)), replace=True)
    means = bootstrapped.mean(axis=1)
    alpha = 1 - confidence
    lower = np.percentile(means, alpha/2 * 100)
    upper = np.percentile(means, (1 - alpha/2) * 100)
    return lower, upper

def cohens_d(group1, group2):
    """Effect size."""
    mean_diff = abs(group1.mean() - group2.mean())
    pooled_std = np.sqrt((group1.var() + group2.var()) / 2)
    return mean_diff / pooled_std if pooled_std > 0 else 0.0

def main():
    # Load scores
    df = pd.read_csv("results/benchmark_scores.csv")

    # Extract scores
    scores = {}
    for _, row in df.iterrows():
        scores[row["condition"]] = {
            "mmlu": row["mmlu"],
            "hellaswag": row["hellaswag"]
        }

    # Compute deltas
    tasks = ["mmlu", "hellaswag"]

    # Independent deltas
    indep_deltas = [
        compute_transfer_delta(
            scores["transferred_indep"][task],
            scores["tuned_indep"][task]
        )
        for task in tasks
    ]

    # Dependent deltas
    dep_deltas = [
        compute_transfer_delta(
            scores["transferred_dep"][task],
            scores["tuned_dep"][task]
        )
        for task in tasks
    ]

    print("\nTransfer Deltas:")
    print(f"  Independent: {indep_deltas} (avg: {np.mean(indep_deltas):.2f}%)")
    print(f"  Dependent: {dep_deltas} (avg: {np.mean(dep_deltas):.2f}%)")

    # Bootstrap CIs
    np.random.seed(42)
    indep_ci = bootstrap_ci(np.array(indep_deltas))
    dep_ci = bootstrap_ci(np.array(dep_deltas))

    print(f"\n95% Confidence Intervals:")
    print(f"  Independent: [{indep_ci[0]:.2f}%, {indep_ci[1]:.2f}%]")
    print(f"  Dependent: [{dep_ci[0]:.2f}%, {dep_ci[1]:.2f}%]")

    # Statistical tests
    t_stat, p_value = ttest_ind(indep_deltas, dep_deltas, equal_var=False)
    effect_size = cohens_d(np.array(indep_deltas), np.array(dep_deltas))

    print(f"\nStatistical Tests:")
    print(f"  Welch's t-test: t={t_stat:.3f}, p={p_value:.4f}")
    print(f"  Cohen's d: {effect_size:.3f}")

    # Save results
    results = {
        "transfer_deltas": {
            "independent": {
                "mmlu": float(indep_deltas[0]),
                "hellaswag": float(indep_deltas[1]),
                "average": float(np.mean(indep_deltas))
            },
            "dependent": {
                "mmlu": float(dep_deltas[0]),
                "hellaswag": float(dep_deltas[1]),
                "average": float(np.mean(dep_deltas))
            }
        },
        "confidence_intervals": {
            "independent": {"lower": float(indep_ci[0]), "upper": float(indep_ci[1])},
            "dependent": {"lower": float(dep_ci[0]), "upper": float(dep_ci[1])}
        },
        "statistical_tests": {
            "welch_t_test": {"statistic": float(t_stat), "p_value": float(p_value)},
            "cohens_d": float(effect_size)
        }
    }

    with open("results/statistical_analysis.yaml", "w") as f:
        yaml.dump(results, f, default_flow_style=False)

    print("\nSaved statistical_analysis.yaml")

if __name__ == "__main__":
    main()
