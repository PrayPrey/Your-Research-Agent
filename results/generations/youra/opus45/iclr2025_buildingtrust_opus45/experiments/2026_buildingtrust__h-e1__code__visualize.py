"""
Visualization module for H-E1 AUROC experiment.

Publication-quality figures for AUROC comparison, margin distributions, and forest plots.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("colorblind")

FONT_SIZE = 12
TITLE_SIZE = 14
FIGSIZE_SINGLE = (8, 6)
FIGSIZE_WIDE = (12, 5)


def plot_auroc_comparison(results: dict, save_path: str) -> None:
    """
    Create grouped bar chart comparing base vs instruct AUROC.

    Args:
        results: Dict with per-family AUROC metrics
        save_path: Path to save figure
    """
    families = ["qwen", "llama", "mistral"]
    x = np.arange(len(families))
    width = 0.35

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

    base_aurocs = []
    inst_aurocs = []
    base_errs = []
    inst_errs = []

    for family in families:
        if family in results:
            base = results[family]["base"]
            inst = results[family]["instruct"]
            base_aurocs.append(base["auroc"])
            inst_aurocs.append(inst["auroc"])
            base_errs.append([base["auroc"] - base["ci_lower"], base["ci_upper"] - base["auroc"]])
            inst_errs.append([inst["auroc"] - inst["ci_lower"], inst["ci_upper"] - inst["auroc"]])
        else:
            base_aurocs.append(0)
            inst_aurocs.append(0)
            base_errs.append([0, 0])
            inst_errs.append([0, 0])

    base_errs = np.array(base_errs).T
    inst_errs = np.array(inst_errs).T

    bars1 = ax.bar(x - width/2, base_aurocs, width, label='Base', color='#2ecc71',
                   yerr=base_errs, capsize=5)
    bars2 = ax.bar(x + width/2, inst_aurocs, width, label='Instruct', color='#e74c3c',
                   yerr=inst_errs, capsize=5)

    ax.set_ylabel('AUROC', fontsize=FONT_SIZE)
    ax.set_xlabel('Model Family', fontsize=FONT_SIZE)
    ax.set_title('AUROC: Margin → Correctness Prediction', fontsize=TITLE_SIZE)
    ax.set_xticks(x)
    ax.set_xticklabels([f.capitalize() for f in families])
    ax.legend(fontsize=FONT_SIZE - 2)
    ax.set_ylim(0.4, 1.0)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.3f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_margin_distributions(
    margins_by_model: dict[str, np.ndarray],
    correctness_by_model: dict[str, np.ndarray],
    save_path: str,
) -> None:
    """
    Create KDE plots showing margin distributions for correct vs incorrect.

    Args:
        margins_by_model: Dict mapping model_id to margin arrays
        correctness_by_model: Dict mapping model_id to correctness arrays
        save_path: Path to save figure
    """
    n_models = len(margins_by_model)
    fig, axes = plt.subplots(1, n_models, figsize=(4 * n_models, 5))

    if n_models == 1:
        axes = [axes]

    for idx, (model_id, margins) in enumerate(margins_by_model.items()):
        ax = axes[idx]
        correctness = correctness_by_model[model_id]

        correct_margins = margins[correctness == 1]
        incorrect_margins = margins[correctness == 0]

        # KDE plots
        if len(correct_margins) > 1:
            sns.kdeplot(correct_margins, ax=ax, label='Correct', color='#2ecc71', fill=True, alpha=0.3)
        if len(incorrect_margins) > 1:
            sns.kdeplot(incorrect_margins, ax=ax, label='Incorrect', color='#e74c3c', fill=True, alpha=0.3)

        ax.set_xlabel('Margin (top1 - top2 logit)', fontsize=FONT_SIZE)
        ax.set_ylabel('Density', fontsize=FONT_SIZE)
        ax.set_title(model_id.split('/')[-1], fontsize=TITLE_SIZE - 2)
        ax.legend(fontsize=FONT_SIZE - 2)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_forest(results: dict, save_path: str) -> None:
    """
    Create forest plot showing AUROC delta per family.

    Args:
        results: Dict with per-family results
        save_path: Path to save figure
    """
    families = ["qwen", "llama", "mistral"]
    deltas = []
    ci_lowers = []
    ci_uppers = []
    labels = []

    for family in families:
        if family not in results:
            continue

        base = results[family]["base"]
        inst = results[family]["instruct"]

        delta = base["auroc"] - inst["auroc"]

        # Compute delta CI
        base_se = (base["ci_upper"] - base["ci_lower"]) / 3.92
        inst_se = (inst["ci_upper"] - inst["ci_lower"]) / 3.92
        delta_se = np.sqrt(base_se**2 + inst_se**2)

        deltas.append(delta)
        ci_lowers.append(delta - 1.96 * delta_se)
        ci_uppers.append(delta + 1.96 * delta_se)
        labels.append(family.capitalize())

    # Add pooled estimate
    if len(deltas) > 0:
        pooled_delta = np.mean(deltas)
        pooled_se = np.std(deltas) / np.sqrt(len(deltas))
        deltas.append(pooled_delta)
        ci_lowers.append(pooled_delta - 1.96 * pooled_se)
        ci_uppers.append(pooled_delta + 1.96 * pooled_se)
        labels.append("Pooled")

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

    y_pos = np.arange(len(labels))
    errors = [[d - l for d, l in zip(deltas, ci_lowers)],
              [u - d for d, u in zip(deltas, ci_uppers)]]

    colors = ['#3498db'] * (len(labels) - 1) + ['#e74c3c']  # Pooled in red

    ax.barh(y_pos, deltas, xerr=errors, height=0.5, color=colors, capsize=5, alpha=0.7)
    ax.axvline(x=0, color='black', linestyle='--', linewidth=1)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel('AUROC Difference (Base - Instruct)', fontsize=FONT_SIZE)
    ax.set_title('Forest Plot: AUROC Degradation by Model Family', fontsize=TITLE_SIZE)

    # Add value labels
    for i, (d, l, u) in enumerate(zip(deltas, ci_lowers, ci_uppers)):
        ax.annotate(f'{d:.3f} [{l:.3f}, {u:.3f}]',
                   xy=(max(u, 0) + 0.01, i),
                   va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def save_all_figures(
    results: dict,
    margins_by_model: dict,
    correctness_by_model: dict,
    figures_dir: str,
) -> None:
    """
    Generate and save all figures.

    Args:
        results: Dict with per-family AUROC results
        margins_by_model: Dict mapping model_id to margin arrays
        correctness_by_model: Dict mapping model_id to correctness arrays
        figures_dir: Directory to save figures
    """
    figures_path = Path(figures_dir)
    figures_path.mkdir(parents=True, exist_ok=True)

    # AUROC comparison bar chart
    plot_auroc_comparison(results, str(figures_path / "auroc_comparison.png"))

    # Margin distributions (only if we have margin data)
    if margins_by_model and correctness_by_model:
        plot_margin_distributions(
            margins_by_model,
            correctness_by_model,
            str(figures_path / "margin_distributions.png")
        )

    # Forest plot
    plot_forest(results, str(figures_path / "forest_plot.png"))

    print(f"All figures saved to: {figures_dir}")
