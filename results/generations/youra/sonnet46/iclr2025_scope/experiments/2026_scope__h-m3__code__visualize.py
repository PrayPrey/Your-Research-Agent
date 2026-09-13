"""Visualization module: 6 required figures for H-M3."""
import os
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict


def plot_gate_metrics_comparison(
    pearson_r: Dict[str, float],
    kendall_tau: Dict[str, float],
    unique_var: float,
    thresholds: Dict,
    output_dir: str,
) -> None:
    """Bar chart: gate metrics vs. thresholds for SST-2 and MNLI."""
    os.makedirs(output_dir, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    # Pearson r
    tasks = ["SST-2", "MNLI"]
    vals_pearson = [pearson_r.get("sst2", float("nan")), pearson_r.get("mnli", float("nan"))]
    colors_p = ["green" if v <= thresholds.get("pearson_r_threshold", -0.4) else "red" for v in vals_pearson]
    axes[0].bar(tasks, vals_pearson, color=colors_p, alpha=0.8)
    axes[0].axhline(thresholds.get("pearson_r_threshold", -0.4), color="black", linestyle="--", label="threshold")
    axes[0].set_title("Pearson r (sparsity vs sensitivity)")
    axes[0].set_ylabel("Pearson r")
    axes[0].legend()

    # Kendall tau
    vals_tau = [kendall_tau.get("sst2", float("nan")), kendall_tau.get("mnli", float("nan"))]
    colors_tau = ["green" if v >= thresholds.get("kendall_tau_threshold", 0.4) else "red" for v in vals_tau]
    axes[1].bar(tasks, vals_tau, color=colors_tau, alpha=0.8)
    axes[1].axhline(thresholds.get("kendall_tau_threshold", 0.4), color="black", linestyle="--", label="threshold")
    axes[1].set_title("Kendall tau (sparsity vs AdaLoRA)")
    axes[1].set_ylabel("Kendall tau")
    axes[1].legend()

    # Unique variance
    uv_color = "green" if unique_var >= thresholds.get("unique_var_threshold", 0.2) else "red"
    axes[2].bar(["Unique Var"], [unique_var], color=uv_color, alpha=0.8)
    axes[2].axhline(thresholds.get("unique_var_threshold", 0.2), color="black", linestyle="--", label="threshold")
    axes[2].set_title("Semipartial r² (sparsity → spectral)")
    axes[2].set_ylabel("Unique variance")
    axes[2].legend()

    plt.suptitle("H-M3 Gate Metrics vs Thresholds", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "gate_metrics_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()


def plot_sparsity_vs_sensitivity(
    sparsity: np.ndarray,
    accuracy_drops: Dict[str, np.ndarray],
    sensitive_masks: Dict[str, np.ndarray],
    pearson_results: Dict,
    output_dir: str,
) -> None:
    """Scatter: per-layer sparsity vs. sensitivity."""
    os.makedirs(output_dir, exist_ok=True)
    tasks = list(accuracy_drops.keys())
    fig, axes = plt.subplots(1, len(tasks), figsize=(7 * len(tasks), 5))
    if len(tasks) == 1:
        axes = [axes]

    for ax, task in zip(axes, tasks):
        drops = accuracy_drops[task]
        mask = sensitive_masks.get(task, np.zeros(len(drops), dtype=bool))
        colors = ["red" if m else "blue" for m in mask]
        ax.scatter(sparsity, drops, c=colors, alpha=0.7, s=60)
        r = pearson_results.get(task, {}).get("r", float("nan"))
        ax.set_xlabel("Layer Sparsity (ε=0.01)")
        ax.set_ylabel("Accuracy Drop")
        ax.set_title(f"{task.upper()} — Pearson r={r:.3f}")
        ax.legend(handles=[
            plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="red", label="Sensitive"),
            plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="blue", label="Non-sensitive"),
        ])

    plt.suptitle("Sparsity vs Sensitivity per Layer", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "sparsity_vs_sensitivity.png"), dpi=150, bbox_inches="tight")
    plt.close()


def plot_sensitivity_heatmap(
    accuracy_drops: Dict[str, np.ndarray],
    sparsity: np.ndarray,
    output_dir: str,
) -> None:
    """32 × 2 heatmap (layers × tasks) with sparsity overlay."""
    os.makedirs(output_dir, exist_ok=True)
    tasks = list(accuracy_drops.keys())
    matrix = np.column_stack([accuracy_drops[t] for t in tasks])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 10), gridspec_kw={"width_ratios": [4, 1]})
    sns.heatmap(matrix, ax=ax1, cmap="Reds", xticklabels=[t.upper() for t in tasks],
                yticklabels=[str(i) for i in range(len(sparsity))], cbar_kws={"label": "Accuracy Drop"})
    ax1.set_xlabel("Task")
    ax1.set_ylabel("Layer Index")
    ax1.set_title("Layer Sensitivity Heatmap")

    ax2.barh(range(len(sparsity)), sparsity, color="steelblue", alpha=0.8)
    ax2.set_yticks(range(len(sparsity)))
    ax2.set_yticklabels([str(i) for i in range(len(sparsity))], fontsize=7)
    ax2.set_xlabel("Sparsity")
    ax2.set_title("Sparsity")
    ax2.invert_yaxis()

    plt.suptitle("Sensitivity Heatmap + Sparsity", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "sensitivity_heatmap.png"), dpi=150, bbox_inches="tight")
    plt.close()


def plot_adalora_allocation(
    adalora_ranks: Dict[str, np.ndarray],
    sparsity: np.ndarray,
    kendall_tau: Dict[str, float],
    output_dir: str,
) -> None:
    """Bar chart: AdaLoRA allocation vs. sparsity-predicted allocation."""
    os.makedirs(output_dir, exist_ok=True)
    tasks = list(adalora_ranks.keys())
    n = len(sparsity)
    x = np.arange(n)
    width = 0.35

    fig, axes = plt.subplots(1, len(tasks), figsize=(14, 5))
    if len(tasks) == 1:
        axes = [axes]

    for ax, task in zip(axes, tasks):
        ranks = adalora_ranks[task]
        # Sparsity-predicted: higher sparsity → lower rank (inverse)
        inverted = 1.0 / (sparsity + 1e-6)
        inverted_norm = inverted / inverted.sum() * ranks.sum()

        ax.bar(x - width / 2, ranks, width, label="AdaLoRA", alpha=0.8, color="steelblue")
        ax.bar(x + width / 2, inverted_norm, width, label="Sparsity-pred", alpha=0.8, color="orange")
        tau = kendall_tau.get(task, float("nan"))
        ax.set_title(f"{task.upper()} — Kendall tau={tau:.3f}")
        ax.set_xlabel("Layer Index")
        ax.set_ylabel("Effective Rank")
        ax.legend()

    plt.suptitle("AdaLoRA Allocation vs Sparsity-Predicted", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "adalora_allocation.png"), dpi=150, bbox_inches="tight")
    plt.close()


def plot_spectral_vs_sparsity(
    spectral_decay: np.ndarray,
    sparsity: np.ndarray,
    grad_norms: np.ndarray,
    regression_results: Dict,
    output_dir: str,
) -> None:
    """Scatter: ΔW spectral decay vs. sparsity; regression line + 95% CI."""
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(sparsity, spectral_decay, alpha=0.7, s=60, color="steelblue", label="Layers")

    # Regression line
    x_sorted = np.sort(sparsity)
    try:
        coef = regression_results.get("coef_sparsity", 0.0)
        intercept_approx = np.mean(spectral_decay) - coef * np.mean(sparsity)
        y_fit = coef * x_sorted + intercept_approx
        ax.plot(x_sorted, y_fit, "r-", label="Regression line")
    except Exception:
        pass

    uv = regression_results.get("unique_var_sparsity", float("nan"))
    p = regression_results.get("p_value_sparsity_beta", float("nan"))
    ax.set_xlabel("Layer Sparsity (ε=0.01)")
    ax.set_ylabel("ΔW Spectral Decay Ratio")
    ax.set_title(f"Spectral Decay vs Sparsity\nSemipartial r²={uv:.3f}, p={p:.4f}")
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "spectral_vs_sparsity.png"), dpi=150, bbox_inches="tight")
    plt.close()


def plot_sensitivity_histogram(
    accuracy_drops: Dict[str, np.ndarray],
    threshold: float,
    output_dir: str,
) -> None:
    """Histogram of per-layer accuracy drops with threshold line."""
    os.makedirs(output_dir, exist_ok=True)
    tasks = list(accuracy_drops.keys())
    fig, axes = plt.subplots(1, len(tasks), figsize=(7 * len(tasks), 5))
    if len(tasks) == 1:
        axes = [axes]

    for ax, task in zip(axes, tasks):
        drops = accuracy_drops[task]
        ax.hist(drops, bins=20, color="steelblue", alpha=0.7, edgecolor="black")
        ax.axvline(threshold, color="red", linestyle="--", label=f"Threshold={threshold:.3f}")
        n_sensitive = (drops >= threshold).sum()
        ax.set_xlabel("Accuracy Drop")
        ax.set_ylabel("Count")
        ax.set_title(f"{task.upper()} — {n_sensitive} sensitive layers")
        ax.legend()

    plt.suptitle("Sensitivity Histogram per Task", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "sensitivity_histogram.png"), dpi=150, bbox_inches="tight")
    plt.close()


def generate_all_figures(results: Dict, cfg) -> None:
    """Call all 6 plot functions. Save to cfg.figures_dir."""
    os.makedirs(cfg.figures_dir, exist_ok=True)

    sparsity = results.get("sparsity", np.zeros(cfg.n_layers))
    accuracy_drops = results.get("accuracy_drops", {})
    sensitive_masks = results.get("sensitive_masks", {})
    adalora_ranks = results.get("adalora_ranks", {})
    spectral_decay = results.get("spectral_decay", np.zeros(cfg.n_layers))
    grad_norms = results.get("grad_norms_array", np.zeros(cfg.n_layers))
    regression_results = results.get("regression_results", {})
    gate_result = results.get("gate_result", {})

    all_metrics = gate_result.get("all_metrics", {})
    pearson_r = {
        "sst2": all_metrics.get("pearson_r_sst2", float("nan")),
        "mnli": all_metrics.get("pearson_r_mnli", float("nan")),
    }
    kendall_tau_dict = {
        "sst2": all_metrics.get("kendall_tau_sst2", float("nan")),
        "mnli": all_metrics.get("kendall_tau_mnli", float("nan")),
    }
    thresholds = {
        "pearson_r_threshold": cfg.pearson_r_threshold,
        "kendall_tau_threshold": cfg.kendall_tau_threshold,
        "unique_var_threshold": cfg.unique_var_threshold,
    }
    pearson_results = {
        task: {"r": all_metrics.get(f"pearson_r_{task}", float("nan"))}
        for task in accuracy_drops
    }

    plot_gate_metrics_comparison(
        pearson_r, kendall_tau_dict,
        regression_results.get("unique_var_sparsity", 0.0),
        thresholds, cfg.figures_dir
    )
    plot_sparsity_vs_sensitivity(sparsity, accuracy_drops, sensitive_masks, pearson_results, cfg.figures_dir)
    plot_sensitivity_heatmap(accuracy_drops, sparsity, cfg.figures_dir)
    plot_adalora_allocation(adalora_ranks, sparsity, kendall_tau_dict, cfg.figures_dir)
    plot_spectral_vs_sparsity(spectral_decay, sparsity, grad_norms, regression_results, cfg.figures_dir)
    plot_sensitivity_histogram(accuracy_drops, cfg.sensitive_drop_threshold, cfg.figures_dir)
    print(f"[FIGURES] All 6 figures saved to {cfg.figures_dir}")
