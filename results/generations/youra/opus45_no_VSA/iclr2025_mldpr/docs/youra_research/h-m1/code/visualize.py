# Visualization module for h-m1
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from config import PATHS


def plot_mediation_path(result: dict, out_path: str) -> None:
    """Draw mediation path diagram with coefficients."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.text(1, 3, "Metadata\nCompleteness\n(X)", ha="center", va="center",
            bbox=dict(boxstyle="round", facecolor="lightblue"), fontsize=12)
    ax.text(5, 5, "Preprocessing\nEntropy\n(M)", ha="center", va="center",
            bbox=dict(boxstyle="round", facecolor="lightyellow"), fontsize=12)
    ax.text(9, 3, "Reproducibility\nVariance\n(Y)", ha="center", va="center",
            bbox=dict(boxstyle="round", facecolor="lightgreen"), fontsize=12)

    ax.annotate("", xy=(4, 4.5), xytext=(2, 3.5),
                arrowprops=dict(arrowstyle="->", lw=2, color="blue"))
    ax.text(2.5, 4.3, f"a = {result['path_a']:.4f}", fontsize=10, color="blue")

    ax.annotate("", xy=(8, 3.5), xytext=(6, 4.5),
                arrowprops=dict(arrowstyle="->", lw=2, color="green"))
    ax.text(7, 4.3, f"b = {result['path_b']:.4f}", fontsize=10, color="green")

    ax.annotate("", xy=(8, 3), xytext=(2, 3),
                arrowprops=dict(arrowstyle="->", lw=2, color="gray", linestyle="--"))
    ax.text(5, 2.5, f"c' = {result['direct_effect']:.4f}", fontsize=10, color="gray")

    ax.text(5, 1, f"Indirect (a×b) = {result['indirect_effect']:.4f}\n"
                  f"Proportion Mediated = {result['proportion_mediated']:.1%}\n"
                  f"Sobel Z = {result['sobel_z']:.2f}, p = {result['sobel_p']:.4f}",
            ha="center", fontsize=11, bbox=dict(facecolor="white", edgecolor="black"))

    plt.title("Mediation Path Diagram: Metadata → Preprocessing Entropy → Variance")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved mediation path diagram to {out_path}")


def plot_entropy_boxplot(df: pd.DataFrame, col: str, out_path: str) -> None:
    """Box plot of entropy column by metadata quartile."""
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=df, x="metadata_quartile", y=col, ax=ax)
    ax.set_xlabel("Metadata Score Quartile")
    ylabel = "Preprocessing Entropy" if "prep" in col else "Hyperparameter Entropy"
    ax.set_ylabel(ylabel)
    ax.set_title(f"{ylabel} by Metadata Quartile")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved entropy boxplot to {out_path}")


def plot_bootstrap_distribution(boot_estimates: list, out_path: str) -> None:
    """Histogram of bootstrap indirect effect estimates."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(boot_estimates, bins=50, edgecolor="black", alpha=0.7)
    ax.axvline(0, color="red", linestyle="--", label="Zero")
    ax.set_xlabel("Indirect Effect (bootstrap)")
    ax.set_ylabel("Frequency")
    ax.set_title("Bootstrap Distribution of Indirect Effect")
    ax.legend()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved bootstrap distribution to {out_path}")


def plot_mediation_proportion(result: dict, out_path: str) -> None:
    """Bar chart: direct vs indirect effect."""
    fig, ax = plt.subplots(figsize=(8, 6))
    effects = ["Direct Effect", "Indirect Effect"]
    values = [abs(result["direct_effect"]), abs(result["indirect_effect"])]
    colors = ["gray", "blue"]
    ax.bar(effects, values, color=colors)
    ax.set_ylabel("|Effect Size|")
    ax.set_title(f"Direct vs Indirect Effect\n(Proportion Mediated: {result['proportion_mediated']:.1%})")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved mediation proportion bar to {out_path}")
