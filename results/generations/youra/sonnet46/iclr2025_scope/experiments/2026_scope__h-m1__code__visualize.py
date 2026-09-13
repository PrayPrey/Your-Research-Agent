import os
from typing import Dict, Any, List
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


def plot_gate_metrics_bar(
    icc3k: float,
    tau_min: float,
    output_path: str,
) -> None:
    """Bar chart: ICC(3,k) and tau_min vs thresholds (0.75, 0.6 dashed lines)."""
    fig, ax = plt.subplots(figsize=(6, 5))
    labels = ["ICC(3,k)", "tau_min"]
    values = [icc3k, tau_min]
    thresholds = [0.75, 0.6]
    colors = ["green" if v >= t else "red" for v, t in zip(values, thresholds)]
    bars = ax.bar(labels, values, color=colors, alpha=0.8)
    ax.axhline(y=0.75, color="navy", linestyle="--", linewidth=1.5, label="ICC threshold (0.75)")
    ax.axhline(y=0.6, color="darkorange", linestyle="--", linewidth=1.5, label="tau threshold (0.60)")
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Value")
    ax.set_title("Gate Metrics vs Thresholds")
    ax.legend(fontsize=9)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_sparsity_heatmap(
    sparsity_profiles: Dict[str, np.ndarray],
    output_path: str,
) -> None:
    """32 layers x 4 distributions heatmap."""
    dist_names = list(sparsity_profiles.keys())
    matrix = np.array([sparsity_profiles[d] for d in dist_names])  # (4, 32)
    fig, ax = plt.subplots(figsize=(14, 4))
    sns.heatmap(matrix, ax=ax, cmap="viridis", annot=False,
                xticklabels=[str(i) for i in range(matrix.shape[1])],
                yticklabels=dist_names)
    ax.set_xlabel("Layer Index")
    ax.set_ylabel("Distribution")
    ax.set_title("Sparsity Profiles Heatmap (4 Distributions × 32 Layers)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_pairwise_tau_matrix(
    tau_results: Dict[str, Dict[str, float]],
    output_path: str,
) -> None:
    """4x4 symmetric heatmap of Kendall's tau values."""
    dist_set = set()
    for key in tau_results:
        d1, d2 = key.split("_vs_")
        dist_set.add(d1)
        dist_set.add(d2)
    dists = sorted(dist_set)
    n = len(dists)
    matrix = np.ones((n, n))
    for i, d1 in enumerate(dists):
        for j, d2 in enumerate(dists):
            if i == j:
                matrix[i, j] = 1.0
            else:
                key1 = f"{d1}_vs_{d2}"
                key2 = f"{d2}_vs_{d1}"
                if key1 in tau_results:
                    matrix[i, j] = tau_results[key1]["tau"]
                elif key2 in tau_results:
                    matrix[i, j] = tau_results[key2]["tau"]
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(matrix, ax=ax, annot=True, fmt=".2f", vmin=0, vmax=1,
                xticklabels=dists, yticklabels=dists, cmap="YlOrRd")
    ax.set_title("Pairwise Kendall's Tau Matrix")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_icc_confidence(
    icc3k: float,
    ci_lower: float,
    ci_upper: float,
    output_path: str,
) -> None:
    """Bar with 95% CI for ICC3k vs 0.75 threshold."""
    fig, ax = plt.subplots(figsize=(5, 5))
    color = "green" if icc3k > 0.75 else "red"
    ax.bar(["ICC(3,k)"], [icc3k], color=color, alpha=0.8,
           yerr=[[icc3k - ci_lower], [ci_upper - icc3k]],
           capsize=10, error_kw={"elinewidth": 2})
    ax.axhline(y=0.75, color="navy", linestyle="--", linewidth=1.5, label="Threshold (0.75)")
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("ICC(3,k)")
    ax.set_title(f"ICC(3,k) = {icc3k:.3f} [95% CI: {ci_lower:.3f}, {ci_upper:.3f}]")
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_sparsity_profiles_overlay(
    sparsity_profiles: Dict[str, np.ndarray],
    output_path: str,
) -> None:
    """4 overlaid lines: x=layer index, y=sparsity."""
    fig, ax = plt.subplots(figsize=(12, 5))
    colors = ["blue", "orange", "green", "red"]
    markers = ["o", "s", "^", "D"]
    for (dist_name, profile), color, marker in zip(sparsity_profiles.items(), colors, markers):
        x = list(range(len(profile)))
        ax.plot(x, profile, label=dist_name, color=color, marker=marker,
                markersize=4, linewidth=1.5, alpha=0.8)
    ax.set_xlabel("Layer Index")
    ax.set_ylabel("Sparsity")
    ax.set_title("Sparsity Profiles Across 4 Distributions")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_epsilon_sensitivity(
    icc_sensitivity: Dict[float, Dict[str, float]],
    tau_sensitivity: Dict[float, Dict[str, float]],
    output_path: str,
) -> None:
    """ICC(3,k) and tau_min vs 4 epsilon values (log-scale x-axis)."""
    epsilons = sorted(icc_sensitivity.keys())
    icc_vals = [icc_sensitivity[e]["icc3k"] for e in epsilons]
    tau_vals = [tau_sensitivity[e]["tau_min"] for e in epsilons]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(epsilons, icc_vals, "bo-", linewidth=2, markersize=8)
    ax1.axhline(y=0.75, color="navy", linestyle="--", linewidth=1.5, label="Threshold (0.75)")
    ax1.set_xscale("log")
    ax1.set_xlabel("Epsilon (log scale)")
    ax1.set_ylabel("ICC(3,k)")
    ax1.set_title("ICC(3,k) vs Epsilon")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(epsilons, tau_vals, "rs-", linewidth=2, markersize=8)
    ax2.axhline(y=0.6, color="darkorange", linestyle="--", linewidth=1.5, label="Threshold (0.60)")
    ax2.set_xscale("log")
    ax2.set_xlabel("Epsilon (log scale)")
    ax2.set_ylabel("tau_min")
    ax2.set_title("tau_min vs Epsilon")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def generate_all_figures(
    sparsity_profiles: Dict[str, np.ndarray],
    icc_result: Dict[str, float],
    tau_results: Dict[str, Dict[str, float]],
    gate_result: Dict[str, Any],
    icc_sensitivity: Dict[float, Dict[str, float]],
    tau_sensitivity: Dict[float, Dict[str, float]],
    figures_dir: str,
) -> List[str]:
    """Generate all 6 figures. Returns list of saved file paths."""
    os.makedirs(figures_dir, exist_ok=True)
    generated = []

    path1 = os.path.join(figures_dir, "gate_metrics.png")
    plot_gate_metrics_bar(gate_result["icc3k"], gate_result["tau_min"], path1)
    generated.append(path1)

    path2 = os.path.join(figures_dir, "sparsity_heatmap.png")
    plot_sparsity_heatmap(sparsity_profiles, path2)
    generated.append(path2)

    path3 = os.path.join(figures_dir, "pairwise_tau_matrix.png")
    plot_pairwise_tau_matrix(tau_results, path3)
    generated.append(path3)

    path4 = os.path.join(figures_dir, "icc_confidence.png")
    plot_icc_confidence(icc_result["icc3k"], icc_result["ci_lower"], icc_result["ci_upper"], path4)
    generated.append(path4)

    path5 = os.path.join(figures_dir, "sparsity_profiles_overlay.png")
    plot_sparsity_profiles_overlay(sparsity_profiles, path5)
    generated.append(path5)

    path6 = os.path.join(figures_dir, "epsilon_sensitivity.png")
    plot_epsilon_sensitivity(icc_sensitivity, tau_sensitivity, path6)
    generated.append(path6)

    return generated
