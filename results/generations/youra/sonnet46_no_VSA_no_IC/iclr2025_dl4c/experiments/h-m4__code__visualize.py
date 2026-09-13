import json
from pathlib import Path
from typing import List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_improvement_bar(results: dict, cfg) -> str:
    conditions = cfg.conditions
    labels = ["Variance-50", "Random-50", "Full-374"]
    colors = ["#2196F3", "#FF9800", "#4CAF50"]

    improvements_pp = [
        (results["improvement"].get(c, {}).get("step_50") or 0.0) * 100
        for c in conditions
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, improvements_pp, color=colors, alpha=0.85, edgecolor="black")

    ax.axhline(cfg.p1_improvement_pp * 100, color="red", linestyle="--",
               linewidth=1.5, label=f"P1 threshold: {cfg.p1_improvement_pp*100:.0f}pp")
    ax.axhline(cfg.p1_gap_pp * 100, color="orange", linestyle=":",
               linewidth=1.5, label=f"Gap threshold: {cfg.p1_gap_pp*100:.0f}pp")
    ax.axhline(0, color="black", linewidth=0.8)

    for bar, val in zip(bars, improvements_pp):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                f"{val:.2f}pp", ha="center", va="bottom", fontsize=10)

    ax.set_ylabel("pass@1 Improvement (pp) at Step 50")
    ax.set_title("H-M4: HumanEval+ pass@1 Improvement Over Frozen Baseline")
    ax.legend(loc="upper right")
    all_vals = improvements_pp + [0.0]
    ax.set_ylim(bottom=min(all_vals) - 1)

    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    out = f"{cfg.figures_dir}/fig1_improvement_bar.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_learning_curves(results: dict, cfg) -> str:
    step_labels = [10, 20, 50]
    step_keys = ["step_10", "step_20", "step_50"]
    colors = {"variance50": "#2196F3", "random50": "#FF9800", "full374": "#4CAF50"}
    labels = {"variance50": "Variance-50", "random50": "Random-50", "full374": "Full-374"}

    fig, ax = plt.subplots(figsize=(8, 5))
    for cond in cfg.conditions:
        vals = [(results["improvement"].get(cond, {}).get(s) or 0.0) * 100 for s in step_keys]
        ax.plot(step_labels, vals, marker="o", color=colors[cond], label=labels[cond])

    ax.axhline(cfg.p1_improvement_pp * 100, color="red", linestyle="--",
               linewidth=1.2, label="P1 threshold (2pp)")
    ax.set_xlabel("Training Step")
    ax.set_ylabel("pass@1 Improvement (pp)")
    ax.set_title("H-M4: Learning Curve — pass@1 Improvement Trajectory")
    ax.legend()

    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    out = f"{cfg.figures_dir}/fig2_learning_curves.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_pass_at_1_heatmap(results: dict, cfg) -> str:
    step_keys = ["step_0", "step_10", "step_20", "step_50"]
    step_labels = ["Step 0\n(baseline)", "Step 10", "Step 20", "Step 50"]
    cond_labels = ["Variance-50", "Random-50", "Full-374"]

    data = np.array([
        [(results["pass_at_1"].get(c, {}).get(s) or 0.0) * 100 for s in step_keys]
        for c in cfg.conditions
    ])

    fig, ax = plt.subplots(figsize=(8, 4))
    im = ax.imshow(data, cmap="YlGn", aspect="auto", vmin=0, vmax=100)

    ax.set_xticks(range(len(step_labels)))
    ax.set_xticklabels(step_labels)
    ax.set_yticks(range(len(cond_labels)))
    ax.set_yticklabels(cond_labels)

    for i in range(len(cond_labels)):
        for j in range(len(step_labels)):
            ax.text(j, i, f"{data[i, j]:.1f}%", ha="center", va="center", fontsize=9)

    plt.colorbar(im, ax=ax, label="pass@1 (%)")
    ax.set_title("H-M4: HumanEval+ pass@1 by Condition and Training Step")

    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    out = f"{cfg.figures_dir}/fig3_heatmap.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_mechanistic_scatter(results: dict, cfg) -> str:
    import json

    h_m2_gate = f"{cfg.h_m2_results_dir}/gate_results.json"
    try:
        with open(h_m2_gate) as f:
            h_m2_data = json.load(f)
        frac_zero_std = h_m2_data.get("mean_frac_zero_std", {})
    except FileNotFoundError:
        print("[H-M4] H-M2 gate_results.json not found; skipping Fig 4.")
        return ""

    colors = {"variance50": "#2196F3", "random50": "#FF9800", "full374": "#4CAF50"}
    labels = {"variance50": "Variance-50", "random50": "Random-50", "full374": "Full-374"}

    fig, ax = plt.subplots(figsize=(6, 5))
    plotted = False
    for cond in ["variance50", "random50"]:
        x = frac_zero_std.get(cond, {}).get("at_50") if isinstance(frac_zero_std.get(cond), dict) else frac_zero_std.get(cond)
        y_raw = results["improvement"].get(cond, {}).get("step_50")
        if x is not None and y_raw is not None:
            y = y_raw * 100
            ax.scatter([x], [y], color=colors[cond], s=120, label=labels[cond], zorder=5)
            ax.annotate(labels[cond], (x, y), textcoords="offset points", xytext=(5, 5), fontsize=9)
            plotted = True

    if not plotted:
        plt.close(fig)
        return ""

    ax.set_xlabel("Mean frac_reward_zero_std at Step 50 (H-M2)")
    ax.set_ylabel("pass@1 Improvement at Step 50 (pp)")
    ax.set_title("H-M4: Gradient Concentration vs Capability Transfer")
    ax.legend()

    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    out = f"{cfg.figures_dir}/fig4_scatter.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def generate_all_figures(results: dict, cfg) -> List[str]:
    paths = []
    paths.append(plot_improvement_bar(results, cfg))
    paths.append(plot_learning_curves(results, cfg))
    paths.append(plot_pass_at_1_heatmap(results, cfg))
    scatter_path = plot_mechanistic_scatter(results, cfg)
    if scatter_path:
        paths.append(scatter_path)
    return paths
