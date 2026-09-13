"""Figure generation for H-M1 convergence analysis."""

import os
import json
import matplotlib.pyplot as plt
import numpy as np


def plot_loss_curves(all_results: dict, save_path: str):
    """Overlay of loss curves for all configs."""
    plt.figure(figsize=(10, 6))

    for config_id in sorted(all_results.keys()):
        lh = all_results[config_id].get("loss_history", [])
        if not lh:
            continue
        tokens = [d["tokens_seen"] / 1e9 for d in lh]
        losses = [d["loss"] for d in lh]
        plt.plot(tokens, losses, label=config_id, linewidth=1.5)

    plt.xlabel("Tokens (B)")
    plt.ylabel("Loss")
    plt.title("Training Loss Curves")
    plt.legend()
    plt.grid(True, alpha=0.3)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_steps_to_threshold(convergence_metrics: dict, save_path: str):
    """Bar chart of steps to threshold per config."""
    configs = [k for k in sorted(convergence_metrics.keys()) if k.startswith("M1-")]
    steps = [convergence_metrics[c]["steps_to_threshold"] for c in configs]
    steps = [s if s != float("inf") else 0 for s in steps]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(configs, steps, color="steelblue")

    for bar, s in zip(bars, steps):
        if s > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f"{int(s)}", ha="center", va="bottom", fontsize=9)

    plt.xlabel("Configuration")
    plt.ylabel("Steps to Loss < 3.5")
    plt.title("Convergence Speed: Steps to Threshold")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_quality_diversity_scatter(convergence_metrics: dict, ensemble_scores: dict, save_path: str):
    """Scatter: convergence AUC vs ensemble score."""
    configs = [k for k in sorted(convergence_metrics.keys()) if k.startswith("M1-")]
    aucs = [convergence_metrics[c]["convergence_auc"] for c in configs]
    scores = [ensemble_scores.get(c, 0.5) for c in configs]

    plt.figure(figsize=(8, 6))
    plt.scatter(aucs, scores, s=100, c="steelblue", alpha=0.7)

    for i, cfg in enumerate(configs):
        plt.annotate(cfg, (aucs[i], scores[i]), textcoords="offset points",
                    xytext=(5, 5), fontsize=9)

    plt.xlabel("Convergence AUC (lower = faster)")
    plt.ylabel("Ensemble Score")
    plt.title("Quality-Diversity Tradeoff")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_loss_at_checkpoints(convergence_metrics: dict, save_path: str):
    """Bar chart of loss at 1B/5B/10B token checkpoints."""
    configs = [k for k in sorted(convergence_metrics.keys()) if k.startswith("M1-")]
    checkpoints = [1_000_000_000, 5_000_000_000, 10_000_000_000]

    x = np.arange(len(configs))
    width = 0.25

    plt.figure(figsize=(12, 6))
    for i, ckpt in enumerate(checkpoints):
        losses = [convergence_metrics[c]["loss_at_checkpoints"].get(ckpt, 0) for c in configs]
        plt.bar(x + i*width, losses, width, label=f"{ckpt//1e9:.0f}B tokens")

    plt.xlabel("Configuration")
    plt.ylabel("Loss")
    plt.title("Loss at Token Checkpoints")
    plt.xticks(x + width, configs)
    plt.legend()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def generate_all_figures(results_dir: str, figures_dir: str):
    """Generate all required figures from results."""
    all_results_path = os.path.join(results_dir, "all_configs.json")
    convergence_path = os.path.join(results_dir, "convergence_metrics.json")

    with open(all_results_path) as f:
        all_results = json.load(f)
    with open(convergence_path) as f:
        convergence_metrics = json.load(f)

    ensemble_scores = {
        cfg: r.get("ensemble_score", 0.5)
        for cfg, r in all_results.items()
    }

    plot_loss_curves(all_results, os.path.join(figures_dir, "loss_curves_overlay.png"))
    plot_steps_to_threshold(convergence_metrics, os.path.join(figures_dir, "steps_to_threshold_bar.png"))
    plot_quality_diversity_scatter(convergence_metrics, ensemble_scores,
                                   os.path.join(figures_dir, "quality_diversity_scatter.png"))
    plot_loss_at_checkpoints(convergence_metrics, os.path.join(figures_dir, "loss_at_checkpoints.png"))

    print(f"Figures saved to {figures_dir}")
