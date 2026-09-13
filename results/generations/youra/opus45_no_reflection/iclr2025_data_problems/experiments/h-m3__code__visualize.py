"""Visualization for H-M3 attribution comparison"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import numpy as np
import os

def plot_gate_comparison(results: dict, out_path: str) -> None:
    """6-bar chart: 3 methods x 2 architectures, AUC on y-axis."""
    methods = list(results.keys())
    n_methods = len(methods)

    bert_aucs = [results[m]["bert"] for m in methods]
    gpt2_aucs = [results[m]["gpt2"] for m in methods]

    x = np.arange(n_methods)
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, bert_aucs, width, label='BERT', color='steelblue')
    bars2 = ax.bar(x + width/2, gpt2_aucs, width, label='GPT-2', color='coral')

    ax.set_xlabel('Attribution Method')
    ax.set_ylabel('Mislabeled Detection AUC')
    ax.set_title('H-M3: Attribution Method Comparison Across Architectures')
    ax.set_xticks(x)
    ax.set_xticklabels([m.upper() for m in methods])
    ax.legend()
    ax.set_ylim(0, 1)

    for bar in bars1 + bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}',
                   xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3), textcoords="offset points",
                   ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_quality_heatmap(results: dict, out_path: str) -> None:
    """Method x architecture heatmap of AUC."""
    methods = list(results.keys())
    architectures = ["bert", "gpt2"]

    data = np.array([[results[m][a] for a in architectures] for m in methods])

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(data, annot=True, fmt=".3f", cmap="YlGnBu",
                xticklabels=["BERT", "GPT-2"],
                yticklabels=[m.upper() for m in methods],
                ax=ax, vmin=0.4, vmax=1.0)
    ax.set_title("Attribution Quality (AUC)")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_score_distributions(score_dict: dict, out_path: str) -> None:
    """Violin plots of influence score distributions per method."""
    fig, axes = plt.subplots(1, len(score_dict), figsize=(4*len(score_dict), 5))
    if len(score_dict) == 1:
        axes = [axes]

    for ax, (name, scores) in zip(axes, score_dict.items()):
        if scores is not None and len(scores) > 0:
            flat = scores.flatten() if scores.ndim > 1 else scores
            flat = flat[~np.isnan(flat)]
            if len(flat) > 0:
                violin_data = flat[np.random.choice(len(flat), min(1000, len(flat)), replace=False)]
                ax.violinplot([violin_data], showmeans=True)
                ax.set_title(name.upper())
                ax.set_ylabel("Score")

    plt.suptitle("Attribution Score Distributions")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_rank_correlation_matrix(corr_matrix: np.ndarray, method_names: list, out_path: str) -> None:
    """Plot correlation matrix between method rankings."""
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm",
                xticklabels=method_names, yticklabels=method_names,
                ax=ax, vmin=-1, vmax=1, center=0)
    ax.set_title("Cross-Method Rank Correlation")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
