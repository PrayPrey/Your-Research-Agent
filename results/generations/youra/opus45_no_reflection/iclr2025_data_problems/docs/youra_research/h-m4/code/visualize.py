"""H-M4 Visualization: Pareto curves and comparison plots."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from typing import Dict

COLORS = {"bert": "#1f77b4", "gpt2": "#ff7f0e"}
MARKERS = {"ekfac": "o", "tracin": "s", "trak": "^"}

def plot_pareto_frontier_grid(results: Dict, out_path: str) -> None:
    """Required: 2x3 grid showing Pareto curves. Row=arch, Col=method."""
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    methods = ["ekfac", "tracin", "trak"]
    archs = ["bert", "gpt2"]

    for row, arch in enumerate(archs):
        for col, method in enumerate(methods):
            ax = axes[row, col]
            if method in results and arch in results[method]:
                points = []
                for budget, data in results[method][arch].items():
                    points.append((data["time_mean"], data["auc_mean"], budget))
                points.sort(key=lambda x: x[0])

                times = [p[0] for p in points]
                aucs = [p[1] for p in points]
                budgets = [p[2] for p in points]

                ax.plot(times, aucs, marker=MARKERS[method], color=COLORS[arch],
                        linewidth=2, markersize=8, label=f"{arch.upper()}")
                for t, a, b in zip(times, aucs, budgets):
                    ax.annotate(str(b), (t, a), textcoords="offset points",
                                xytext=(5, 5), fontsize=7)

            ax.set_xscale("log")
            ax.set_xlabel("Compute Time (s)")
            ax.set_ylabel("Mislabeled AUC")
            ax.set_title(f"{method.upper()} - {arch.upper()}")
            ax.grid(True, alpha=0.3)
            ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_arch_comparison_per_method(results: Dict, method: str, out_path: str) -> None:
    """Overlay BERT vs GPT-2 Pareto curves for one method."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for arch in ["bert", "gpt2"]:
        if method in results and arch in results[method]:
            points = []
            for budget, data in results[method][arch].items():
                points.append((data["time_mean"], data["auc_mean"], budget))
            points.sort(key=lambda x: x[0])

            times = [p[0] for p in points]
            aucs = [p[1] for p in points]

            ax.plot(times, aucs, marker=MARKERS[method], color=COLORS[arch],
                    linewidth=2, markersize=8, label=arch.upper())

    ax.set_xscale("log")
    ax.set_xlabel("Compute Time (s)")
    ax.set_ylabel("Mislabeled Detection AUC")
    ax.set_title(f"{method.upper()}: BERT vs GPT-2 Pareto Comparison")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_auc_vs_projdim(results: Dict, out_path: str) -> None:
    """Line plot: AUC vs projection dimension for each (method, arch)."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    methods = ["ekfac", "tracin", "trak"]

    for idx, method in enumerate(methods):
        ax = axes[idx]
        for arch in ["bert", "gpt2"]:
            if method in results and arch in results[method]:
                budgets = sorted(results[method][arch].keys())
                aucs = [results[method][arch][b]["auc_mean"] for b in budgets]
                ax.plot(budgets, aucs, marker=MARKERS[method], color=COLORS[arch],
                        linewidth=2, markersize=8, label=arch.upper())

        ax.set_xlabel("Compute Budget (proj_dim / ckpt count)")
        ax.set_ylabel("AUC")
        ax.set_title(f"{method.upper()}")
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_auc_bar_fixed_budget(results: Dict, budget: int, out_path: str) -> None:
    """Bar chart comparing methods at fixed budget."""
    methods = ["ekfac", "tracin", "trak"]
    archs = ["bert", "gpt2"]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(methods))
    width = 0.35

    for i, arch in enumerate(archs):
        aucs = []
        errs = []
        for method in methods:
            if method in results and arch in results[method] and budget in results[method][arch]:
                aucs.append(results[method][arch][budget]["auc_mean"])
                errs.append(results[method][arch][budget].get("auc_std", 0))
            else:
                aucs.append(0)
                errs.append(0)
        ax.bar(x + i * width, aucs, width, yerr=errs, label=arch.upper(),
               color=COLORS[arch], alpha=0.8)

    ax.set_xlabel("Method")
    ax.set_ylabel("Mislabeled Detection AUC")
    ax.set_title(f"AUC Comparison at Budget={budget}")
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels([m.upper() for m in methods])
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_dominance_heatmap(dominance: Dict, out_path: str) -> None:
    """Heatmap showing method-arch dominance relationships."""
    keys = list(dominance.keys())
    n = len(keys)
    matrix = np.zeros((n, n))

    for i, k1 in enumerate(keys):
        for j, k2 in enumerate(keys):
            if k2 in dominance[k1].get("dominates", []):
                matrix[i, j] = 1

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matrix, cmap="Blues", aspect="auto")

    labels = [f"{k[0]}-{k[1]}" for k in keys]
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)
    ax.set_xlabel("Dominated")
    ax.set_ylabel("Dominates")
    ax.set_title("Pareto Dominance Matrix")
    plt.colorbar(im)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_gate_comparison(results: dict, out_path: str) -> None:
    """6-bar chart for backward compat."""
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
    ax.set_title('H-M4: Attribution Method Comparison Across Architectures')
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
