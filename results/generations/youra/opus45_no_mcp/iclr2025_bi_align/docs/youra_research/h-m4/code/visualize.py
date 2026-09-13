"""Visualization for H-M4."""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from config import H_M4_Config

cfg = H_M4_Config()


def plot_gate_metrics(metrics: dict, out_path: str) -> None:
    """Bar chart: metrics vs thresholds."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    labels = ['Point-Biserial r', "Cohen's d", 'Partial r']
    values = [
        abs(metrics["point_biserial_r"]),
        abs(metrics["cohens_d"]),
        abs(metrics["partial_r"])
    ]
    thresholds = [cfg.r_threshold, cfg.d_threshold, cfg.partial_r_threshold]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(x - width/2, values, width, label='Observed', color='steelblue')
    ax.bar(x + width/2, thresholds, width, label='Threshold', color='coral', alpha=0.7)

    ax.set_ylabel('Value')
    ax.set_title('H-M4 Gate Metrics: Bidirectional Features vs Calibration Clusters')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.set_ylim(0, max(max(values), max(thresholds)) * 1.2)

    for bar, val in zip(bars, values):
        ax.annotate(f'{val:.3f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_score_by_cluster(records: list, out_path: str) -> None:
    """Histogram of bidirectional score by cluster."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    scores_0 = [r["bidirectional_score"] for r in records if r["cluster_label"] == 0]
    scores_1 = [r["bidirectional_score"] for r in records if r["cluster_label"] == 1]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(scores_0, bins=4, alpha=0.6, label=f'Cluster 0 (n={len(scores_0)})', color='blue')
    ax.hist(scores_1, bins=4, alpha=0.6, label=f'Cluster 1 (n={len(scores_1)})', color='red')
    ax.set_xlabel('Bidirectional Score (0-3)')
    ax.set_ylabel('Count')
    ax.set_title('Bidirectional Score Distribution by Cluster')
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_feature_breakdown(records: list, out_path: str) -> None:
    """Stacked bar of feature prevalence by cluster."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    features = ["user_belief_reference", "context_dependent", "hedged_answer"]
    clusters = [0, 1]

    data = {c: {f: 0 for f in features} for c in clusters}
    counts = {c: 0 for c in clusters}

    for r in records:
        c = r["cluster_label"]
        counts[c] += 1
        for f in features:
            data[c][f] += r[f]

    # Normalize to prevalence
    for c in clusters:
        for f in features:
            data[c][f] = data[c][f] / counts[c] if counts[c] > 0 else 0

    x = np.arange(len(features))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, [data[0][f] for f in features], width, label='Cluster 0')
    ax.bar(x + width/2, [data[1][f] for f in features], width, label='Cluster 1 (Inverted)')
    ax.set_ylabel('Prevalence')
    ax.set_title('Feature Prevalence by Cluster')
    ax.set_xticks(x)
    ax.set_xticklabels(['User Belief', 'Context Dep.', 'Hedged'])
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
