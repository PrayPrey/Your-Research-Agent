import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_permutation_histogram(result: dict, out_path: str) -> None:
    """Histogram of perm_coefs, vline at true_coef, annotate percentile."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(result["perm_coefs"], bins=40, alpha=0.7, edgecolor="black", label="Permuted coefficients")
    ax.axvline(result["true_coef"], color="red", linewidth=2, label=f"True coef = {result['true_coef']:.4f}")
    ax.set_xlabel("metadata_score coefficient")
    ax.set_ylabel("Frequency")
    ax.set_title(f"Permutation Test (n=1000)\nPercentile Rank: {result['percentile_rank']:.1f}%")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_effect_comparison(result: dict, out_path: str) -> None:
    """Bar chart: true |coef| vs 95th percentile |perm_coefs|."""
    true_abs = abs(result["true_coef"])
    perm_95 = np.percentile(np.abs(result["perm_coefs"]), 95)

    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(["True |β|", "95th pctl |permuted|"], [true_abs, perm_95], color=["#2E7D32", "#C62828"])
    ax.set_ylabel("Absolute coefficient magnitude")
    ax.set_title(f"Effect Comparison\nRatio: {result['effect_ratio']:.3f} (< 0.05 = pass)")
    for bar, val in zip(bars, [true_abs, perm_95]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001, f"{val:.4f}", ha="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
