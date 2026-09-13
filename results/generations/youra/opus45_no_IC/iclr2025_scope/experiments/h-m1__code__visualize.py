"""H-M1: Visualization - Gate chart, heatmap, boxplot for LongBench-v2 domains."""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from config import DOMAINS, DOMAIN_CATEGORIES, ExperimentConfig


def plot_gate_metrics(
    f_stat: float,
    p_value: float,
    threshold: float = 0.05,
    output_dir: str = "figures"
) -> str:
    """Mandatory gate chart with p=0.05 threshold."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # F-statistic bar
    ax1 = axes[0]
    ax1.bar(["F-statistic"], [f_stat], color="steelblue")
    ax1.set_ylabel("F-statistic")
    ax1.set_title("ANOVA F-statistic")
    ax1.text(0, f_stat * 1.05 + 0.1, f"{f_stat:.2f}", ha="center", fontsize=12)

    # P-value with threshold line
    ax2 = axes[1]
    color = "green" if p_value < threshold else "red"
    ax2.bar(["p-value"], [min(p_value, 0.2)], color=color)  # Cap for visibility
    ax2.axhline(y=threshold, color="black", linestyle="--", label=f"threshold={threshold}")
    ax2.set_ylabel("p-value")
    ax2.set_title("Gate Evaluation")
    ax2.legend()
    ax2.text(0, min(p_value, 0.2) + 0.005, f"{p_value:.2e}", ha="center", fontsize=10)

    result = "PASS" if p_value < threshold else "FAIL"
    fig.suptitle(f"H-M1 Gate Result: {result}", fontsize=14, fontweight="bold")

    plt.tight_layout()
    path = os.path.join(output_dir, "gate_metrics.png")
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(path, dpi=150)
    plt.close()

    return path


def plot_entropy_heatmap(
    entropy_matrix: np.ndarray,
    domains: list[str],
    samples_per_domain: int,
    output_dir: str = "figures"
) -> str:
    """Heatmap: 6 domains x 32 layers showing mean entropy."""
    n_domains = len(domains)

    # Compute mean entropy per domain per layer (average over samples and heads)
    domain_layer_entropy = np.zeros((n_domains, 32))
    for i, domain in enumerate(domains):
        start_idx = i * samples_per_domain
        end_idx = start_idx + samples_per_domain
        if end_idx > entropy_matrix.shape[0]:
            end_idx = entropy_matrix.shape[0]
        domain_entropy = entropy_matrix[start_idx:end_idx]  # [samples, 32, 32]
        if domain_entropy.shape[0] > 0:
            domain_layer_entropy[i] = domain_entropy.mean(axis=(0, 2))  # mean over samples and heads

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(
        domain_layer_entropy,
        xticklabels=[f"L{i}" for i in range(32)],
        yticklabels=[d[:20] for d in domains],  # Truncate long names
        cmap="viridis",
        ax=ax
    )
    ax.set_xlabel("Layer")
    ax.set_ylabel("Domain")
    ax.set_title("Attention Entropy: Domains x Layers")

    plt.tight_layout()
    path = os.path.join(output_dir, "entropy_heatmap.png")
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(path, dpi=150)
    plt.close()

    return path


def plot_domain_boxplot(
    entropy_by_domain: dict,
    output_dir: str = "figures"
) -> str:
    """Boxplot of sample entropy distribution by domain."""
    fig, ax = plt.subplots(figsize=(12, 6))

    domain_names = list(entropy_by_domain.keys())
    domain_data = []
    for domain in domain_names:
        tensor = entropy_by_domain[domain]
        sample_means = tensor.mean(dim=(1, 2)).numpy()
        domain_data.append(sample_means)

    bp = ax.boxplot(domain_data, labels=[d[:15] for d in domain_names], patch_artist=True)

    colors = plt.cm.Set2(np.linspace(0, 1, len(domain_names)))
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)

    ax.set_xlabel("Domain")
    ax.set_ylabel("Mean Entropy (per sample)")
    ax.set_title("Entropy Distribution by Domain")
    plt.xticks(rotation=30, ha="right")

    plt.tight_layout()
    path = os.path.join(output_dir, "domain_boxplot.png")
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(path, dpi=150)
    plt.close()

    return path


def plot_layer_discrimination(
    entropy_by_domain: dict,
    output_dir: str = "figures"
) -> str:
    """Per-layer F-stat across domains."""
    from scipy import stats

    layer_f_stats = []

    for layer_idx in range(32):
        groups = []
        for domain, tensor in entropy_by_domain.items():
            # [n_samples, 32, 32] -> layer [n_samples, 32 heads] -> mean -> [n_samples]
            layer_data = tensor[:, layer_idx, :].mean(dim=1).numpy()
            groups.append(layer_data)

        try:
            f_stat, _ = stats.f_oneway(*groups)
            layer_f_stats.append(f_stat)
        except:
            layer_f_stats.append(0)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(range(32), layer_f_stats, marker="o", linewidth=2)
    ax.set_xlabel("Layer")
    ax.set_ylabel("F-statistic")
    ax.set_title("Per-Layer Domain Discrimination (ANOVA F-stat)")
    ax.set_xticks(range(32))
    ax.grid(True, alpha=0.3)

    max_layer = np.argmax(layer_f_stats)
    ax.axvline(x=max_layer, color="red", linestyle="--", alpha=0.5,
               label=f"Max F at layer {max_layer}")
    ax.legend()

    plt.tight_layout()
    path = os.path.join(output_dir, "layer_discrimination.png")
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(path, dpi=150)
    plt.close()

    return path


def main(
    entropy_matrix_path: str = "entropy_matrix.npy",
    domain_means_path: str = "domain_means.json",
    stats_results_path: str = "stats_results.json",
    output_dir: str = "figures"
):
    """Generate all visualizations."""
    os.makedirs(output_dir, exist_ok=True)

    # Load data
    entropy_matrix = np.load(entropy_matrix_path)
    with open(domain_means_path, "r") as f:
        domain_means = json.load(f)
    with open(stats_results_path, "r") as f:
        stats_results = json.load(f)

    print("Generating visualizations...")

    # Mandatory: Gate metrics
    plot_gate_metrics(
        stats_results["f_stat"],
        stats_results["p_value"],
        output_dir=output_dir
    )
    print("  Gate metrics saved")

    print("All visualizations generated.")


if __name__ == "__main__":
    main()
