"""Visualization for H-M1 experiment."""
import matplotlib.pyplot as plt
import numpy as np


def plot_mi_comparison_bar(results: dict, out_path: str) -> None:
    """MI comparison bar chart (CE vs RL, raw and controlled)."""
    fig, ax = plt.subplots(figsize=(8, 5))

    labels = ["CE (raw)", "RL (raw)", "CE (controlled)", "RL (controlled)"]
    values = [
        results["mi_ce_raw"],
        results["mi_rl_raw"],
        results["mi_ce_controlled"],
        results["mi_rl_controlled"],
    ]
    colors = ["#1f77b4", "#ff7f0e", "#1f77b4", "#ff7f0e"]
    patterns = ["", "", "//", "//"]

    bars = ax.bar(labels, values, color=colors)
    for bar, pattern in zip(bars, patterns):
        bar.set_hatch(pattern)

    ax.set_ylabel("Mutual Information I(F;E)")
    ax.set_title(f"MI Comparison (p={results['p_value']:.4f})")
    ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_mi_vs_edit_length(
    mi_values: np.ndarray,
    edit_lengths: np.ndarray,
    condition_labels: np.ndarray,
    slope: float,
    intercept: float,
    out_path: str,
) -> None:
    """Scatter plot: MI vs edit length, colored by condition."""
    fig, ax = plt.subplots(figsize=(8, 5))

    rl_mask = condition_labels == "RL"
    ce_mask = condition_labels == "CE"

    ax.scatter(edit_lengths[ce_mask], mi_values[ce_mask], alpha=0.5, label="CE", c="#1f77b4", s=20)
    ax.scatter(edit_lengths[rl_mask], mi_values[rl_mask], alpha=0.5, label="RL", c="#ff7f0e", s=20)

    # Regression line
    x_line = np.linspace(edit_lengths.min(), edit_lengths.max(), 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, "k--", label=f"Regression (slope={slope:.4f})")

    ax.set_xlabel("Edit Length (chars)")
    ax.set_ylabel("MI Estimate")
    ax.set_title("MI vs Edit Length by Condition")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_permutation_distribution(
    perm_diffs: np.ndarray,
    observed_diff: float,
    p_value: float,
    out_path: str,
) -> None:
    """Histogram of null distribution with observed difference marked."""
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.hist(perm_diffs, bins=50, alpha=0.7, color="#1f77b4", edgecolor="black")
    ax.axvline(observed_diff, color="red", linestyle="--", linewidth=2, label=f"Observed: {observed_diff:.4f}")
    ax.axvline(-observed_diff, color="red", linestyle="--", linewidth=2, alpha=0.5)

    ax.set_xlabel("Permuted MI Difference (RL - CE)")
    ax.set_ylabel("Frequency")
    ax.set_title(f"Permutation Test (p={p_value:.4f})")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
