"""Visualization suite for H-M2."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from analysis import get_component_means
import config as cfg


def plot_score_comparison_bar(stats: dict, out_path: str) -> None:
    """Bar chart, BiDPO vs DPO mean +/- std error bars. Required figure."""
    fig, ax = plt.subplots(figsize=(8, 6))

    means = [stats["dpo_mean"], stats["bidpo_mean"]]
    stds = [stats["dpo_std"], stats["bidpo_std"]]
    labels = ["DPO Baseline", "BiDPO"]
    colors = ["#2196F3", "#4CAF50"]

    x = np.arange(len(labels))
    bars = ax.bar(x, means, yerr=stds, capsize=5, color=colors, alpha=0.8)

    ax.set_ylabel("Collaboration Score", fontsize=12)
    ax.set_title(f"BiDPO vs DPO Collaboration Scores\n(p={stats['p_value_onesided']:.4f}, d={stats['effect_size_cohens_d']:.3f})", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)

    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{mean:.3f}", ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_score_distributions(bidpo_scores: list, dpo_scores: list, out_path: str) -> None:
    """Overlapping histograms of BiDPO vs DPO scores."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(dpo_scores, bins=30, alpha=0.6, label="DPO Baseline", color="#2196F3")
    ax.hist(bidpo_scores, bins=30, alpha=0.6, label="BiDPO", color="#4CAF50")

    ax.axvline(np.mean(dpo_scores), color="#1565C0", linestyle="--", label=f"DPO mean: {np.mean(dpo_scores):.3f}")
    ax.axvline(np.mean(bidpo_scores), color="#2E7D32", linestyle="--", label=f"BiDPO mean: {np.mean(bidpo_scores):.3f}")

    ax.set_xlabel("Collaboration Score", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title("Collaboration Score Distributions", fontsize=14)
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_per_prompt_scatter(dpo_scores: list, bidpo_scores: list, out_path: str) -> None:
    """X=DPO, Y=BiDPO, diagonal reference line."""
    fig, ax = plt.subplots(figsize=(8, 8))

    ax.scatter(dpo_scores, bidpo_scores, alpha=0.5, s=20, c="#673AB7")

    min_val = min(min(dpo_scores), min(bidpo_scores))
    max_val = max(max(dpo_scores), max(bidpo_scores))
    ax.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label="y=x")

    ax.set_xlabel("DPO Score", fontsize=12)
    ax.set_ylabel("BiDPO Score", fontsize=12)
    ax.set_title("Per-Prompt Score Comparison", fontsize=14)
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_score_component_breakdown(bidpo_responses: list, dpo_responses: list, out_path: str) -> None:
    """Stacked bar: mean reasoning/uncertainty/engagement/depth counts."""
    fig, ax = plt.subplots(figsize=(10, 6))

    dpo_comp = get_component_means(dpo_responses)
    bidpo_comp = get_component_means(bidpo_responses)

    labels = ["DPO Baseline", "BiDPO"]
    components = ["reasoning", "uncertainty", "engagement", "depth"]
    colors = ["#E91E63", "#FF9800", "#03A9F4", "#8BC34A"]

    x = np.arange(len(labels))
    width = 0.5

    bottom_dpo = 0
    bottom_bidpo = 0

    for comp, color in zip(components, colors):
        vals = [dpo_comp[comp], bidpo_comp[comp]]
        ax.bar(x, vals, width, bottom=[bottom_dpo, bottom_bidpo], label=comp.capitalize(), color=color)
        bottom_dpo += dpo_comp[comp]
        bottom_bidpo += bidpo_comp[comp]

    ax.set_ylabel("Mean Raw Score Count", fontsize=12)
    ax.set_title("Score Component Breakdown", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_length_vs_score(responses: list, scores: list, out_path: str) -> None:
    """Scatter: word_count vs score, verbosity confound check."""
    fig, ax = plt.subplots(figsize=(10, 6))

    lengths = [len(r.split()) for r in responses]

    ax.scatter(lengths, scores, alpha=0.4, s=15, c="#009688")

    z = np.polyfit(lengths, scores, 1)
    p = np.poly1d(z)
    x_line = np.linspace(min(lengths), max(lengths), 100)
    ax.plot(x_line, p(x_line), 'r--', alpha=0.7, label=f"Trend: y={z[0]:.4f}x + {z[1]:.3f}")

    ax.set_xlabel("Response Length (words)", fontsize=12)
    ax.set_ylabel("Collaboration Score", fontsize=12)
    ax.set_title("Response Length vs Collaboration Score", fontsize=14)
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
