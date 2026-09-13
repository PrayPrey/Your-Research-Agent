"""
Figure generation for H-E1 experiment results.
Generates 4 required figures for the validation report.
"""
import os
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


def plot_gate_metrics_comparison(
    mean_delta_cnn: float,
    mean_delta_transformer: float,
    threshold: float,
    save_path: str,
) -> None:
    """Bar chart comparing mean |Δacc| CNN vs Transformer with threshold line."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 5))
    x = [0, 1]
    vals = [mean_delta_cnn, mean_delta_transformer]
    colors = ["steelblue" if v < threshold else "tomato" for v in vals]
    bars = ax.bar(x, vals, color=colors, width=0.5, zorder=2)
    ax.axhline(threshold, color="red", linestyle="--", linewidth=1.5,
               label=f"Threshold ({threshold:.3f})")
    ax.set_xticks(x)
    ax.set_xticklabels(["CNN Zoo", "Transformer Zoo"], fontsize=12)
    ax.set_ylabel("Mean |Δ acc|", fontsize=12)
    ax.set_title("Gate Metrics: Mean |Δ acc| after Canonical Permutation", fontsize=13)
    ax.legend(fontsize=11)
    ax.set_ylim(0, max(max(vals) * 1.5, threshold * 3))

    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + threshold * 0.05,
                f"{v:.6f}", ha="center", va="bottom", fontsize=10)

    pass_label = "PASS" if max(vals) < threshold else "FAIL"
    ax.set_title(f"Gate Metrics: Mean |Δ acc| [{pass_label}]", fontsize=13)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved: {save_path}")


def plot_delta_acc_distribution(
    cnn_deltas: List[float],
    transformer_deltas: List[float],
    save_path: str,
) -> None:
    """Histogram of all |Δacc| values (log-scale x-axis)."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    eps = 1e-9
    cnn_arr = np.array(cnn_deltas) + eps
    tf_arr = np.array(transformer_deltas) + eps

    bins = np.logspace(np.log10(min(cnn_arr.min(), tf_arr.min())),
                       np.log10(max(cnn_arr.max(), tf_arr.max(), 0.01)), 30)

    ax.hist(cnn_arr, bins=bins, alpha=0.6, label="CNN Zoo", color="steelblue")
    ax.hist(tf_arr, bins=bins, alpha=0.6, label="Transformer Zoo", color="darkorange")
    ax.set_xscale("log")
    ax.set_xlabel("|Δ acc| (log scale)", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Distribution of |Δ acc| across all permutations", fontsize=13)
    ax.legend(fontsize=11)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved: {save_path}")


def plot_orbit_pe_success_table(
    success_flags: Dict[str, bool],
    save_path: str,
) -> None:
    """Table figure showing orbit-PE computability per layer type."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    from orbit_pe import SUPPORTED_LAYER_TYPES

    # Aggregate by layer type
    type_counts = {t: {"success": 0, "total": 0} for t in SUPPORTED_LAYER_TYPES}

    for param_name, success in success_flags.items():
        for t in SUPPORTED_LAYER_TYPES:
            if t.lower() in param_name.lower() or (
                t == "Linear" and "fc" in param_name.lower() and "conv" not in param_name.lower()
            ) or (t == "Conv2d" and "conv" in param_name.lower()):
                type_counts[t]["total"] += 1
                if success:
                    type_counts[t]["success"] += 1
                break
        else:
            # Default to Linear if not matched
            t = "Linear"
            type_counts[t]["total"] += 1
            if success:
                type_counts[t]["success"] += 1

    fig, ax = plt.subplots(figsize=(7, 3))
    ax.axis("off")

    rows = []
    for t in SUPPORTED_LAYER_TYPES:
        cnt = type_counts[t]
        status = "✓ PASS" if (cnt["total"] == 0 or cnt["success"] == cnt["total"]) else "✗ FAIL"
        rate = f"{cnt['success']}/{cnt['total']}" if cnt["total"] > 0 else "N/A"
        rows.append([t, rate, status])

    table = ax.table(
        cellText=rows,
        colLabels=["Layer Type", "Success/Total", "Status"],
        cellLoc="center",
        loc="center",
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)

    # Color header
    for j in range(3):
        table[0, j].set_facecolor("#4472C4")
        table[0, j].set_text_props(color="white", fontweight="bold")

    # Color status cells
    for i, row in enumerate(rows):
        color = "#C6EFCE" if "PASS" in row[2] else "#FFC7CE"
        table[i + 1, 2].set_facecolor(color)

    ax.set_title("Orbit-PE Computability by Layer Type", fontsize=13, pad=10)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved: {save_path}")


def plot_per_seed_stability(
    cnn_results: List[Dict],
    transformer_results: List[Dict],
    save_path: str,
) -> None:
    """Box plot of |Δacc| across 10 permutation seeds for CNN and Transformer."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Group by seed
    seeds = sorted(set(r["seed"] for r in cnn_results + transformer_results))

    cnn_by_seed = {s: [r["delta_acc"] for r in cnn_results if r["seed"] == s] for s in seeds}
    tf_by_seed = {s: [r["delta_acc"] for r in transformer_results if r["seed"] == s] for s in seeds}

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, by_seed, title in zip(axes, [cnn_by_seed, tf_by_seed], ["CNN Zoo", "Transformer Zoo"]):
        data = [by_seed.get(s, [0.0]) for s in seeds]
        ax.boxplot(data, labels=[str(s) for s in seeds])
        ax.set_xlabel("Permutation Seed", fontsize=11)
        ax.set_ylabel("|Δ acc|", fontsize=11)
        ax.set_title(f"{title}: |Δ acc| per Seed", fontsize=12)
        ax.set_ylim(bottom=0)

    plt.suptitle("Per-Seed Permutation Stability", fontsize=13)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved: {save_path}")
