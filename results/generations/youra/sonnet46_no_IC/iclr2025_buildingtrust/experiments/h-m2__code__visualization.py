"""Visualization for H-M2: 4 mandatory figures."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns

from config import DIMENSIONS, ETHICS_IDX, FIGURES_DIR, RHO_THRESHOLD, ROBUSTNESS_IDX, SAFETY_IDX


def plot_gate_metrics(rho_sr: float, delta_values: dict, figures_dir: str = FIGURES_DIR) -> str:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))

    color1 = "green" if rho_sr < RHO_THRESHOLD else "red"
    ax1.bar(["ρ_partial(safety,robustness)"], [rho_sr], color=color1, alpha=0.8)
    ax1.axhline(RHO_THRESHOLD, color="black", linestyle="--", label=f"threshold={RHO_THRESHOLD}")
    ax1.set_ylim(-1.0, 0.2)
    ax1.set_title("Primary Gate: ρ_partial(safety, robustness)")
    ax1.set_ylabel("Partial Spearman ρ")
    ax1.legend()

    scales = list(delta_values.keys())
    dvals = [delta_values[s] for s in scales]
    colors2 = ["green" if d <= 0 else "red" for d in dvals]
    ax2.bar(scales, dvals, color=colors2, alpha=0.8)
    ax2.axhline(0, color="black", linestyle="--", label="threshold=0")
    ax2.set_title("Secondary Gate: Δ_robustness (chat − base)")
    ax2.set_ylabel("Δ_robustness")
    ax2.legend()

    plt.tight_layout()
    path = os.path.join(figures_dir, "gate_metrics.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


def plot_within_family_deltas(deltas: list, figures_dir: str = FIGURES_DIR) -> str:
    scales = [d["scale"] for d in deltas]
    delta_safety = [d["delta_safety"] for d in deltas]
    delta_rob = [d["delta_robustness"] for d in deltas]

    x = np.arange(len(scales))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(x - width/2, delta_safety, width, label="Δ_safety", color="steelblue", alpha=0.8)
    ax.bar(x + width/2, delta_rob, width, label="Δ_robustness", color="coral", alpha=0.8)
    ax.axhline(0, color="black", linestyle="--", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"LLaMA-2-{s}" for s in scales])
    ax.set_title("Within-Family Δ: Safety vs Robustness (RLHF Chat − Base)")
    ax.set_ylabel("Score Delta")
    ax.legend()

    plt.tight_layout()
    path = os.path.join(figures_dir, "delta_robustness.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


def plot_rho_heatmap(rho_partial: np.ndarray, figures_dir: str = FIGURES_DIR) -> str:
    dim_labels = [d[:6] for d in DIMENSIONS]
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(rho_partial, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1,
                xticklabels=dim_labels, yticklabels=dim_labels, ax=ax)

    # Highlight safety-robustness cells (1,3),(3,1) and safety-ethics cells (1,5),(5,1)
    for (row, col) in [(SAFETY_IDX, ROBUSTNESS_IDX), (ROBUSTNESS_IDX, SAFETY_IDX),
                        (SAFETY_IDX, ETHICS_IDX), (ETHICS_IDX, SAFETY_IDX)]:
        ax.add_patch(mpatches.Rectangle((col, row), 1, 1, fill=False,
                                         edgecolor="orange", lw=2))

    ax.set_title("6×6 ρ_partial Heatmap (orange: safety-robustness & safety-ethics)")
    plt.tight_layout()
    path = os.path.join(figures_dir, "rho_heatmap.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


def plot_safety_robustness_scatter(annotated_df, figures_dir: str = FIGURES_DIR) -> str:
    fig, ax = plt.subplots(figsize=(7, 5))

    base_mask = annotated_df["is_RLHF"] == 0
    chat_mask = annotated_df["is_RLHF"] == 1

    ax.scatter(annotated_df.loc[base_mask, "safety"], annotated_df.loc[base_mask, "robustness"],
               color="steelblue", label="Base (RLHF=0)", alpha=0.8, zorder=5)
    ax.scatter(annotated_df.loc[chat_mask, "safety"], annotated_df.loc[chat_mask, "robustness"],
               color="red", label="Chat/Instruct (RLHF=1)", alpha=0.8, zorder=5)

    for mask, color in [(base_mask, "steelblue"), (chat_mask, "red")]:
        sub = annotated_df[mask]
        if len(sub) >= 2:
            x = sub["safety"].values
            y = sub["robustness"].values
            coef = np.polyfit(x, y, 1)
            x_line = np.linspace(x.min(), x.max(), 50)
            ax.plot(x_line, np.polyval(coef, x_line), color=color, linestyle="--", alpha=0.6)

    ax.set_xlabel("Safety Score")
    ax.set_ylabel("Robustness Score")
    ax.set_title("Safety vs Robustness (16 TrustLLM models)")
    ax.legend()

    plt.tight_layout()
    path = os.path.join(figures_dir, "safety_rob_scatter.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


def generate_all_figures(rho_sr: float, delta_values: dict, deltas: list,
                          rho_partial: np.ndarray, annotated_df,
                          figures_dir: str = FIGURES_DIR) -> list:
    os.makedirs(figures_dir, exist_ok=True)
    paths = []
    paths.append(plot_gate_metrics(rho_sr, delta_values, figures_dir))
    paths.append(plot_within_family_deltas(deltas, figures_dir))
    paths.append(plot_rho_heatmap(rho_partial, figures_dir))
    paths.append(plot_safety_robustness_scatter(annotated_df, figures_dir))
    return paths
