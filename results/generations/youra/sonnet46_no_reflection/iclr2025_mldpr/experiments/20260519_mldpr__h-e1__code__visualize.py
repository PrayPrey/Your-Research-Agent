"""visualize.py — 5 diagnostic figures for H-E1."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

DOMAIN_COLORS = {
    "cv": "#2196F3",
    "nlp": "#FF5722",
    "tabular": "#4CAF50",
}


def plot_gate_metrics(domain_results: dict, output_dir: str) -> None:
    """Bar chart: p-value, Cohen's d, AUC per domain with threshold lines."""
    os.makedirs(output_dir, exist_ok=True)
    domains = [d for d in domain_results if d != "summary"]
    metrics = ["p_value", "cohens_d", "auc"]
    titles = ["Mann-Whitney p-value", "Cohen's d", "AUC"]
    thresholds = [0.05, 0.5, 0.70]

    fig, axes = plt.subplots(1, 3, figsize=(12, 5), dpi=150)
    for ax, metric, title, threshold in zip(axes, metrics, titles, thresholds):
        values = []
        colors = []
        for d in domains:
            disc = domain_results[d].get("discriminability", {})
            val = disc.get(metric, 0.0)
            if metric == "cohens_d":
                val = abs(val)
            values.append(val)
            colors.append(DOMAIN_COLORS.get(d, "#888888"))
        bars = ax.bar(domains, values, color=colors, alpha=0.8, edgecolor="black")
        ax.axhline(threshold, color="#F44336", linestyle="--", linewidth=1.5,
                   label=f"threshold={threshold}")
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Domain")
        ax.set_ylabel(metric)
        ax.legend(fontsize=8)
        ax.set_ylim(bottom=0)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=8)

    plt.suptitle("H-E1 Gate Metrics by Domain", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "gate_metrics.png"), dpi=150, bbox_inches="tight")
    plt.close()


def plot_signal_boxplots(domain_signals: dict, output_dir: str) -> None:
    """Box plots: H_d signal distributions for saturated vs. healthy per domain."""
    os.makedirs(output_dir, exist_ok=True)
    domains = list(domain_signals.keys())
    n = len(domains)
    fig, axes = plt.subplots(1, max(n, 1), figsize=(10, 6), dpi=150)
    if n == 1:
        axes = [axes]

    for ax, domain in zip(axes, domains):
        df = domain_signals[domain]
        labeled = df[df["label"].isin(["saturated", "healthy"])]
        if len(labeled) == 0:
            ax.set_title(f"{domain} (no data)")
            continue
        color = DOMAIN_COLORS.get(domain, "#888888")
        groups = [
            labeled[labeled["label"] == "saturated"]["hd_signal"].values,
            labeled[labeled["label"] == "healthy"]["hd_signal"].values,
        ]
        bp = ax.boxplot(groups, labels=["Saturated", "Healthy"], patch_artist=True)
        bp["boxes"][0].set_facecolor(color)
        if len(bp["boxes"]) > 1:
            bp["boxes"][1].set_facecolor("#BBBBBB")
        ax.set_title(f"{domain.upper()} H_d Signals", fontsize=10)
        ax.set_ylabel("H_d Signal")

    plt.suptitle("H_d Signal Distributions: Saturated vs. Healthy", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "boxplots.png"), dpi=150, bbox_inches="tight")
    plt.close()


def plot_roc_curves(domain_results: dict, output_dir: str) -> None:
    """ROC curves for signal vs. baseline per domain."""
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random")

    for domain, res in domain_results.items():
        if domain == "summary":
            continue
        color = DOMAIN_COLORS.get(domain, "#888888")
        roc = res.get("roc_data", {})
        fpr = roc.get("fpr", [0, 1])
        tpr = roc.get("tpr", [0, 1])
        auc = res.get("signal_auc", 0.5)
        ax.plot(fpr, tpr, color=color, linewidth=2,
                label=f"{domain.upper()} H_d (AUC={auc:.3f})")

        b_roc = res.get("baseline_roc", {})
        b_fpr = b_roc.get("fpr", [0, 1])
        b_tpr = b_roc.get("tpr", [0, 1])
        b_auc = res.get("baseline_auc", 0.5)
        ax.plot(b_fpr, b_tpr, color=color, linewidth=1.5, linestyle=":",
                label=f"{domain.upper()} Baseline (AUC={b_auc:.3f})")

    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves: H_d Signal vs. Baseline", fontsize=12)
    ax.legend(fontsize=8, loc="lower right")
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "roc_curves.png"), dpi=150, bbox_inches="tight")
    plt.close()


def plot_temporal_separation(temporal_results: dict, output_dir: str) -> None:
    """Line plot: Cohen's d vs. lookback horizon per domain."""
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 5), dpi=150)

    for domain, lb_results in temporal_results.items():
        color = DOMAIN_COLORS.get(domain, "#888888")
        lookbacks = sorted(lb_results.keys())
        cohens_ds = [abs(lb_results[lb].get("cohens_d", 0.0)) for lb in lookbacks]
        ax.plot(lookbacks, cohens_ds, "o-", color=color, linewidth=2,
                markersize=6, label=f"{domain.upper()}")

    ax.axhline(0.5, color="#FF9800", linestyle="--", linewidth=1.5, label="d=0.5 threshold")
    ax.set_xlabel("Lookback (months before collapse)")
    ax.set_ylabel("|Cohen's d|")
    ax.set_title("Temporal Signal Separation: H_d Discriminability vs. Lookback Horizon", fontsize=11)
    ax.legend()
    ax.set_xlim([0, max(max(temporal_results[d].keys()) for d in temporal_results) + 2])
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "temporal_separation.png"), dpi=150, bbox_inches="tight")
    plt.close()


def plot_scatter_saturation(domain_signals: dict, output_dir: str) -> None:
    """Scatter: H_d signal colored by saturation label."""
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 7), dpi=150)

    for domain, df in domain_signals.items():
        labeled = df[df["label"].isin(["saturated", "healthy"])]
        if len(labeled) == 0:
            continue
        color = DOMAIN_COLORS.get(domain, "#888888")
        sat = labeled[labeled["label"] == "saturated"]
        healthy = labeled[labeled["label"] == "healthy"]
        ax.scatter(range(len(sat)), sat["hd_signal"].values,
                   c=color, marker="^", alpha=0.7, s=60,
                   label=f"{domain.upper()} Saturated")
        ax.scatter(range(len(healthy)), healthy["hd_signal"].values,
                   c=color, marker="o", alpha=0.4, s=40,
                   label=f"{domain.upper()} Healthy")

    ax.set_xlabel("Benchmark index")
    ax.set_ylabel("H_d Signal")
    ax.set_title("H_d Signal by Saturation Label", fontsize=12)
    ax.legend(fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "scatter.png"), dpi=150, bbox_inches="tight")
    plt.close()


def generate_all_figures(
    domain_results: dict,
    domain_signals: dict,
    temporal_results: dict,
    output_dir: str = "h-e1/figures/",
) -> None:
    """Call all plot_* functions. Save PNGs to output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"Generating figures to {output_dir}...")
    plot_gate_metrics(domain_results, output_dir)
    print("  ✓ gate_metrics.png")
    plot_signal_boxplots(domain_signals, output_dir)
    print("  ✓ boxplots.png")
    plot_roc_curves(domain_results, output_dir)
    print("  ✓ roc_curves.png")
    plot_temporal_separation(temporal_results, output_dir)
    print("  ✓ temporal_separation.png")
    plot_scatter_saturation(domain_signals, output_dir)
    print("  ✓ scatter.png")
    print("All figures generated.")
