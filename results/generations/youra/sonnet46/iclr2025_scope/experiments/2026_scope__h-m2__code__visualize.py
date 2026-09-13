import os
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from compute_metrics import ADJACENT_PAIRS
from config import ExperimentConfig


def plot_gate_metrics(
    cv_per_epsilon: Dict[float, float],
    tau_matrix: Dict[str, Dict[str, float]],
    cfg: ExperimentConfig,
    save_path: str,
) -> None:
    """2-panel figure: CV bars + adjacent tau bars."""
    epsilons = cfg.epsilons
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: CV per epsilon
    cv_vals = [cv_per_epsilon[e] for e in epsilons]
    colors_cv = ["green" if v > cfg.cv_threshold else "red" for v in cv_vals]
    ax1.bar([str(e) for e in epsilons], cv_vals, color=colors_cv)
    ax1.axhline(cfg.cv_threshold, linestyle="--", color="black", label=f"threshold={cfg.cv_threshold}")
    ax1.set_title("CV per Epsilon")
    ax1.set_xlabel("Epsilon")
    ax1.set_ylabel("CV (std/mean)")
    ax1.legend()

    # Right: adjacent pair tau bars
    adj_keys = [f"{e1}_vs_{e2}" for e1, e2 in ADJACENT_PAIRS]
    adj_taus = [tau_matrix[k]["tau"] if k in tau_matrix else 0.0 for k in adj_keys]
    colors_tau = ["green" if t >= cfg.cross_epsilon_tau_threshold else "red" for t in adj_taus]
    ax2.bar(adj_keys, adj_taus, color=colors_tau)
    ax2.axhline(cfg.cross_epsilon_tau_threshold, linestyle="--", color="black",
                label=f"threshold={cfg.cross_epsilon_tau_threshold}")
    ax2.set_title("Adjacent Epsilon Pair Tau")
    ax2.set_xlabel("Epsilon Pair")
    ax2.set_ylabel("Kendall Tau")
    ax2.tick_params(axis="x", rotation=15)
    ax2.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_cross_epsilon_tau_heatmap(
    tau_matrix: Dict[str, Dict[str, float]],
    epsilons: List[float],
    save_path: str,
) -> None:
    """4x4 symmetric Kendall tau heatmap across epsilon pairs."""
    eps_list = list(epsilons)
    n = len(eps_list)
    mat = np.eye(n)

    for i, e1 in enumerate(eps_list):
        for j, e2 in enumerate(eps_list):
            if i < j:
                key = f"{e1}_vs_{e2}"
                val = tau_matrix[key]["tau"] if key in tau_matrix else 0.0
                mat[i, j] = mat[j, i] = val

    labels = [str(e) for e in eps_list]
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(mat, annot=True, xticklabels=labels, yticklabels=labels,
                vmin=0, vmax=1, fmt=".2f", cmap="YlOrRd", ax=ax)
    ax.set_title("Cross-Epsilon Kendall Tau Heatmap")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_sparsity_profiles_overlay(
    sparsity_dict: Dict[float, np.ndarray],
    epsilons: List[float],
    save_path: str,
) -> None:
    """Overlay sparsity profiles for all epsilon values."""
    colors = ["blue", "orange", "green", "red"]
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, eps in enumerate(epsilons):
        color = colors[i % len(colors)]
        ax.plot(range(32), sparsity_dict[eps], color=color, label=f"ε={eps}")
    ax.set_xlabel("Layer Index")
    ax.set_ylabel("Sparsity Fraction")
    ax.set_title("Sparsity Profiles Across Epsilon Values")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_cv_per_epsilon(
    cv_per_epsilon: Dict[float, float],
    cfg: ExperimentConfig,
    save_path: str,
) -> None:
    """Bar chart of CV values per epsilon with threshold line."""
    epsilons = list(cv_per_epsilon.keys())
    cv_vals = list(cv_per_epsilon.values())
    colors = ["green" if cv > cfg.cv_threshold else "red" for cv in cv_vals]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar([str(e) for e in epsilons], cv_vals, color=colors)
    ax.axhline(cfg.cv_threshold, linestyle="--", color="black",
               label=f"threshold={cfg.cv_threshold}")
    ax.set_title("CV per Epsilon")
    ax.set_xlabel("Epsilon")
    ax.set_ylabel("CV (std/mean)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def generate_all_figures(
    sparsity_dict: Dict[float, np.ndarray],
    cv_per_epsilon: Dict[float, float],
    tau_matrix: Dict[str, Dict[str, float]],
    cfg: ExperimentConfig,
) -> None:
    """Generate and save all 4 figures for H-M2."""
    os.makedirs(cfg.figures_dir, exist_ok=True)
    figs_dir = cfg.figures_dir
    epsilons = cfg.epsilons

    plot_gate_metrics(cv_per_epsilon, tau_matrix, cfg, f"{figs_dir}/gate_metrics.png")
    plot_cross_epsilon_tau_heatmap(tau_matrix, epsilons, f"{figs_dir}/cross_epsilon_tau_heatmap.png")
    plot_sparsity_profiles_overlay(sparsity_dict, epsilons, f"{figs_dir}/sparsity_profiles_overlay.png")
    plot_cv_per_epsilon(cv_per_epsilon, cfg, f"{figs_dir}/cv_per_epsilon.png")

    print(f"✓ All 4 figures saved to {figs_dir}/")
