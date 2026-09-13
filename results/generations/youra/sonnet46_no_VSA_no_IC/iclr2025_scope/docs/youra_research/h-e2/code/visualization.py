"""Visualization for h-e2 experiment results."""
from __future__ import annotations

import os
from typing import List, Optional


def plot_ppl_comparison(
    ppl_baseline: float,
    ppl_swa_k4: float,
    delta_threshold: float = 2.0,
    save_path: str = "figures/ppl_comparison.png",
) -> None:
    """Bar chart comparing ppl_baseline vs ppl_swa_k4 with Δ=2.0 threshold line."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ["Baseline\n(full attention)", f"SWA k=4\n(w=512)"]
    values = [ppl_baseline, ppl_swa_k4]
    colors = ["steelblue", "darkorange" if ppl_swa_k4 - ppl_baseline <= delta_threshold else "crimson"]

    bars = ax.bar(labels, values, color=colors, width=0.4, zorder=2)
    ax.set_ylim(0, max(values) * 1.25)
    ax.set_ylabel("Perplexity (WikiText-103 test)")
    ax.set_title("h-e2: Entropy-Guided k=4 SWA vs Baseline\nLlama-2-7B (zero-shot)")

    # Threshold line at baseline + 2.0
    threshold_val = ppl_baseline + delta_threshold
    ax.axhline(threshold_val, color="red", linestyle="--", linewidth=1.5,
               label=f"PASS threshold (baseline + {delta_threshold:.1f})")

    # Annotate bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.05,
                f"{val:.3f}", ha="center", va="bottom", fontsize=11, fontweight="bold")

    delta = ppl_swa_k4 - ppl_baseline
    status = "PASS" if delta <= delta_threshold else "FAIL"
    ax.text(0.98, 0.97, f"Δ = {delta:+.3f}  [{status}]",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=11, color="green" if status == "PASS" else "red",
            fontweight="bold")

    ax.legend(loc="upper left")
    ax.grid(axis="y", alpha=0.3, zorder=1)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {save_path}")


def plot_entropy_scatter(
    entropy_scores: List[float],
    target_layers: List[int],
    save_path: str = "figures/entropy_scatter.png",
) -> None:
    """x=layer index, y=entropy, top-4 highlighted."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    n_layers = len(entropy_scores)
    xs = list(range(n_layers))
    colors = ["darkorange" if i in target_layers else "steelblue" for i in xs]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.scatter(xs, entropy_scores, c=colors, s=60, zorder=2)
    ax.set_xlabel("Layer index")
    ax.set_ylabel("Mean attention entropy")
    ax.set_title(f"h-e2: Per-layer entropy (Llama-2-7B, n=100 calibration sequences)\n"
                 f"Orange = SWA-converted layers {target_layers}")
    ax.grid(alpha=0.3, zorder=1)
    ax.set_xticks(range(0, n_layers, 4))

    # Label target layers
    for idx in target_layers:
        ax.annotate(f"L{idx}", (idx, entropy_scores[idx]),
                    textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8)

    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {save_path}")
