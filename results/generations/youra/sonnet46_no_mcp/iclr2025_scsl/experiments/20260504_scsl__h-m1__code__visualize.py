import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Dict, Any, List


def plot_mean_early_gdr_bar(
    analysis: Dict[str, Any],
    figures_dir: str,
) -> str:
    os.makedirs(figures_dir, exist_ok=True)
    seeds = sorted(analysis["mean_early_gdr_per_seed"].keys())
    values = [analysis["mean_early_gdr_per_seed"][s] for s in seeds]
    std = analysis.get("std_early_gdr", 0.0)

    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(len(seeds))
    ax.bar(x, values, yerr=std, capsize=5, color="steelblue", alpha=0.8)
    ax.axhline(y=1.0, color="red", linestyle="--", linewidth=1.5, label="Threshold (1.0)")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Seed {s}" for s in seeds])
    ax.set_xlabel("Seed")
    ax.set_ylabel("Mean Early GDR")
    ax.set_title("H-M1: Mean Early GDR per Seed")
    ax.legend()
    plt.tight_layout()

    out_path = os.path.abspath(os.path.join(figures_dir, "mean_early_gdr_bar.png"))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_gdr_timeline(
    seed_results: Dict[int, Dict[str, Any]],
    delta_series: np.ndarray,
    figures_dir: str,
) -> str:
    os.makedirs(figures_dir, exist_ok=True)
    checkpoint_epochs = [2 * i for i in range(1, 16)]  # [2,4,...,30]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    all_gdrs = []
    for seed, res in seed_results.items():
        gdr = res["gdr_series"]
        n = min(len(gdr), len(checkpoint_epochs))
        ax1.plot(checkpoint_epochs[:n], gdr[:n], alpha=0.4, linewidth=1, label=f"Seed {seed}")
        all_gdrs.append(gdr[:n])

    mean_gdr = np.mean(all_gdrs, axis=0)
    ax1.plot(checkpoint_epochs[:len(mean_gdr)], mean_gdr, color="blue", linewidth=2.5, label="Mean GDR")
    ax1.axhline(y=1.0, color="gray", linestyle=":", linewidth=1)
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("GDR(t)")

    if delta_series is not None and len(delta_series) > 0:
        ax2 = ax1.twinx()
        n = min(len(delta_series), len(checkpoint_epochs))
        ax2.plot(checkpoint_epochs[:n], delta_series[:n], color="orange", linestyle="--",
                 linewidth=1.5, label="H-E1 delta(t)")
        ax2.set_ylabel("H-E1 delta(t)", color="orange")
        ax2.tick_params(axis="y", labelcolor="orange")

    ax1.set_title("H-M1: GDR Timeline vs H-E1 delta(t)")
    ax1.legend(loc="upper right")
    plt.tight_layout()

    out_path = os.path.abspath(os.path.join(figures_dir, "gdr_timeline.png"))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_grad_norm_dual_axis(
    seed_results: Dict[int, Dict[str, Any]],
    figures_dir: str,
) -> str:
    os.makedirs(figures_dir, exist_ok=True)
    checkpoint_epochs = [2 * i for i in range(1, 16)]

    all_spurious, all_core = [], []
    for res in seed_results.values():
        all_spurious.append(res["spurious_grad_norms"])
        all_core.append(res["core_grad_norms"])

    n = min(len(all_spurious[0]), len(checkpoint_epochs))
    mean_sp = np.mean(all_spurious, axis=0)[:n]
    std_sp = np.std(all_spurious, axis=0)[:n]
    mean_co = np.mean(all_core, axis=0)[:n]
    std_co = np.std(all_core, axis=0)[:n]
    epochs = checkpoint_epochs[:n]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(epochs, mean_sp, color="red", linewidth=2, label="Spurious grad norm")
    ax1.fill_between(epochs, mean_sp - std_sp, mean_sp + std_sp, alpha=0.2, color="red")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Spurious Grad Norm", color="red")
    ax1.tick_params(axis="y", labelcolor="red")

    ax2 = ax1.twinx()
    ax2.plot(epochs, mean_co, color="blue", linewidth=2, label="Core grad norm")
    ax2.fill_between(epochs, mean_co - std_co, mean_co + std_co, alpha=0.2, color="blue")
    ax2.set_ylabel("Core Grad Norm", color="blue")
    ax2.tick_params(axis="y", labelcolor="blue")

    ax1.set_title("H-M1: Gradient Norms — Spurious vs Core")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
    plt.tight_layout()

    out_path = os.path.abspath(os.path.join(figures_dir, "grad_norm_dual_axis.png"))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_early_late_violin(
    seed_results: Dict[int, Dict[str, Any]],
    early_epochs: list,
    figures_dir: str,
) -> str:
    os.makedirs(figures_dir, exist_ok=True)
    checkpoint_interval = 2
    early_indices = [(e // checkpoint_interval) - 1 for e in early_epochs]
    late_indices = [12, 13, 14]  # epochs 26, 28, 30

    early_vals, late_vals = [], []
    for res in seed_results.values():
        gdr = res["gdr_series"]
        early_vals.extend([gdr[i] for i in early_indices if i < len(gdr)])
        late_vals.extend([gdr[i] for i in late_indices if i < len(gdr)])

    fig, ax = plt.subplots(figsize=(6, 5))
    data = [early_vals, late_vals]
    parts = ax.violinplot(data, positions=[1, 2], showmeans=True)
    for pc in parts["bodies"]:
        pc.set_alpha(0.7)
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["Early (epochs 2-6)", "Late (epochs 26-30)"])
    ax.set_ylabel("GDR")
    ax.set_title("H-M1: GDR Distribution — Early vs Late Training")
    plt.tight_layout()

    out_path = os.path.abspath(os.path.join(figures_dir, "early_late_violin.png"))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def generate_all_figures(
    seed_results: Dict[int, Dict[str, Any]],
    analysis: Dict[str, Any],
    delta_series: np.ndarray,
    figures_dir: str,
) -> None:
    plot_mean_early_gdr_bar(analysis, figures_dir)
    plot_gdr_timeline(seed_results, delta_series, figures_dir)
    plot_grad_norm_dual_axis(seed_results, figures_dir)
    from config import GDRConfig
    early_epochs = [2, 4, 6]
    plot_early_late_violin(seed_results, early_epochs, figures_dir)
