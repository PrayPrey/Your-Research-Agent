"""
Visualization module for H-M1 Conditional Margin Inflation Analysis.
Publication-quality figures for margin comparison, distributions, and forest plots.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from config import FIGURES_DIR

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("colorblind")

FONT_SIZE = 12
TITLE_SIZE = 14
FIGSIZE_SINGLE = (8, 6)
FIGSIZE_WIDE = (12, 5)
FIGSIZE_QUAD = (12, 10)


def plot_gate_metrics(
    family_results: dict[str, dict],
    figures_dir: Path = None,
) -> str:
    """
    Bar chart: E[margin|incorrect] base vs instruct per family (REQUIRED figure).

    Args:
        family_results: Dict mapping family name to analysis results
        figures_dir: Output directory for figures

    Returns:
        Path to saved figure
    """
    if figures_dir is None:
        figures_dir = FIGURES_DIR

    families = list(family_results.keys())
    x = np.arange(len(families))
    width = 0.35

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

    base_means = []
    inst_means = []
    base_errs = []
    inst_errs = []

    for family in families:
        r = family_results[family]
        base_means.append(r["base_stats"]["mean_incorrect"])
        inst_means.append(r["inst_stats"]["mean_incorrect"])
        base_errs.append(r["base_stats"]["se_incorrect"] * 1.96)  # 95% CI
        inst_errs.append(r["inst_stats"]["se_incorrect"] * 1.96)

    bars1 = ax.bar(x - width/2, base_means, width, yerr=base_errs,
                   label='Base Model', color='steelblue', capsize=5)
    bars2 = ax.bar(x + width/2, inst_means, width, yerr=inst_errs,
                   label='Instruct Model', color='coral', capsize=5)

    ax.set_xlabel('Model Family', fontsize=FONT_SIZE)
    ax.set_ylabel('E[margin | incorrect]', fontsize=FONT_SIZE)
    ax.set_title('Conditional Margin Inflation for Incorrect Predictions\nH-M1: MUST_WORK Gate', fontsize=TITLE_SIZE)
    ax.set_xticks(x)
    ax.set_xticklabels([f.capitalize() for f in families])
    ax.legend()

    # Add significance markers
    for i, family in enumerate(families):
        r = family_results[family]
        if r["statistically_significant"]:
            y_max = max(inst_means[i] + inst_errs[i], base_means[i] + base_errs[i])
            ax.text(i, y_max + 0.05, f"p={r['permutation_test']['p_value']:.4f}*",
                    ha='center', fontsize=10)

    plt.tight_layout()
    save_path = figures_dir / "gate_metrics.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return str(save_path)


def plot_kde_distributions(
    family_results: dict[str, dict],
    arrays_by_family: dict[str, dict],
    figures_dir: Path = None,
) -> str:
    """
    4-panel KDE plot: base-correct, base-incorrect, inst-correct, inst-incorrect.

    Args:
        family_results: Dict mapping family name to analysis results
        arrays_by_family: Dict mapping family name to arrays dict
        figures_dir: Output directory for figures

    Returns:
        Path to saved figure
    """
    if figures_dir is None:
        figures_dir = FIGURES_DIR

    families = list(arrays_by_family.keys())
    n_families = len(families)

    fig, axes = plt.subplots(2, 2, figsize=FIGSIZE_QUAD)

    titles = [
        ('Base Model - Correct', 'base_margins', 'base_correctness', 1),
        ('Base Model - Incorrect', 'base_margins', 'base_correctness', 0),
        ('Instruct Model - Correct', 'inst_margins', 'inst_correctness', 1),
        ('Instruct Model - Incorrect', 'inst_margins', 'inst_correctness', 0),
    ]

    colors = plt.cm.Set2(np.linspace(0, 1, n_families))

    for ax, (title, margin_key, correct_key, correct_val) in zip(axes.flatten(), titles):
        for i, family in enumerate(families):
            arrays = arrays_by_family[family]
            mask = arrays[correct_key] == correct_val
            margins = arrays[margin_key][mask]

            if len(margins) > 0:
                sns.kdeplot(data=margins, ax=ax, label=family.capitalize(),
                            color=colors[i], fill=True, alpha=0.3)

        ax.set_xlabel('Margin', fontsize=FONT_SIZE)
        ax.set_ylabel('Density', fontsize=FONT_SIZE)
        ax.set_title(title, fontsize=TITLE_SIZE)
        ax.legend()

    plt.suptitle('Margin Distribution by Model Type and Correctness', fontsize=TITLE_SIZE + 2, y=1.02)
    plt.tight_layout()

    save_path = figures_dir / "kde_distributions.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return str(save_path)


def plot_box_plots(
    arrays_by_family: dict[str, dict],
    figures_dir: Path = None,
) -> str:
    """
    Box plots comparing margin distributions across conditions.

    Args:
        arrays_by_family: Dict mapping family name to arrays dict
        figures_dir: Output directory for figures

    Returns:
        Path to saved figure
    """
    if figures_dir is None:
        figures_dir = FIGURES_DIR

    fig, axes = plt.subplots(1, len(arrays_by_family), figsize=FIGSIZE_WIDE)
    if len(arrays_by_family) == 1:
        axes = [axes]

    for ax, (family, arrays) in zip(axes, arrays_by_family.items()):
        # Prepare data for boxplot
        data = []
        labels = []

        for model_type in ['base', 'inst']:
            for correct_type in ['correct', 'incorrect']:
                margin_key = f"{model_type}_margins"
                correct_key = f"{model_type}_correctness"
                correct_val = 1 if correct_type == 'correct' else 0

                mask = arrays[correct_key] == correct_val
                margins = arrays[margin_key][mask]
                data.append(margins)
                labels.append(f"{model_type.capitalize()}\n{correct_type.capitalize()}")

        bp = ax.boxplot(data, labels=labels, patch_artist=True)

        # Color the boxes
        colors = ['steelblue', 'lightsteelblue', 'coral', 'lightsalmon']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)

        ax.set_title(f'{family.capitalize()}', fontsize=TITLE_SIZE)
        ax.set_ylabel('Margin', fontsize=FONT_SIZE)

    plt.suptitle('Margin Distributions by Condition', fontsize=TITLE_SIZE + 2, y=1.02)
    plt.tight_layout()

    save_path = figures_dir / "box_plots.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return str(save_path)


def plot_inflation_ratios(
    family_results: dict[str, dict],
    figures_dir: Path = None,
) -> str:
    """
    Bar chart: correct_ratio vs incorrect_ratio per family.

    Args:
        family_results: Dict mapping family name to analysis results
        figures_dir: Output directory for figures

    Returns:
        Path to saved figure
    """
    if figures_dir is None:
        figures_dir = FIGURES_DIR

    families = list(family_results.keys())
    x = np.arange(len(families))
    width = 0.35

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

    correct_ratios = []
    incorrect_ratios = []

    for family in families:
        r = family_results[family]
        # Compute correct ratio: inst_mean_correct / base_mean_correct
        base_correct = r["base_stats"]["mean_correct"]
        inst_correct = r["inst_stats"]["mean_correct"]
        correct_ratio = inst_correct / base_correct if base_correct > 0 else 0

        # Incorrect ratio from effect size
        incorrect_ratio = r["effect_size"]["inflation_ratio"]

        correct_ratios.append(correct_ratio)
        incorrect_ratios.append(incorrect_ratio)

    bars1 = ax.bar(x - width/2, correct_ratios, width, label='Correct Predictions', color='steelblue')
    bars2 = ax.bar(x + width/2, incorrect_ratios, width, label='Incorrect Predictions', color='coral')

    ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=1, label='No Inflation (1.0)')

    ax.set_xlabel('Model Family', fontsize=FONT_SIZE)
    ax.set_ylabel('Inflation Ratio (Instruct / Base)', fontsize=FONT_SIZE)
    ax.set_title('Margin Inflation Ratios by Prediction Correctness', fontsize=TITLE_SIZE)
    ax.set_xticks(x)
    ax.set_xticklabels([f.capitalize() for f in families])
    ax.legend()

    plt.tight_layout()

    save_path = figures_dir / "inflation_ratios.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return str(save_path)


def plot_forest(
    family_results: dict[str, dict],
    figures_dir: Path = None,
) -> str:
    """
    Forest plot: Effect sizes with 95% CIs + pooled estimate.

    Args:
        family_results: Dict mapping family name to analysis results
        figures_dir: Output directory for figures

    Returns:
        Path to saved figure
    """
    if figures_dir is None:
        figures_dir = FIGURES_DIR

    families = list(family_results.keys())
    n = len(families)

    fig, ax = plt.subplots(figsize=(10, 4 + n * 0.5))

    y_pos = np.arange(n + 1)  # +1 for pooled estimate
    effects = []
    ci_lowers = []
    ci_uppers = []

    for family in families:
        r = family_results[family]
        effect = r["effect_size"]["raw_diff"]
        ci_lower = r["bootstrap_ci"]["ci_lower"]
        ci_upper = r["bootstrap_ci"]["ci_upper"]

        effects.append(effect)
        ci_lowers.append(ci_lower)
        ci_uppers.append(ci_upper)

    # Compute pooled estimate (simple mean)
    pooled_effect = np.mean(effects)
    pooled_ci_lower = np.mean(ci_lowers)
    pooled_ci_upper = np.mean(ci_uppers)

    all_effects = effects + [pooled_effect]
    all_ci_lowers = ci_lowers + [pooled_ci_lower]
    all_ci_uppers = ci_uppers + [pooled_ci_upper]
    all_labels = [f.capitalize() for f in families] + ['Pooled']

    # Plot
    colors = ['steelblue'] * n + ['darkred']
    markers = ['o'] * n + ['D']

    for i, (effect, ci_l, ci_u, label, color, marker) in enumerate(
        zip(all_effects, all_ci_lowers, all_ci_uppers, all_labels, colors, markers)
    ):
        ax.errorbar(effect, i, xerr=[[effect - ci_l], [ci_u - effect]],
                    fmt=marker, color=color, markersize=8, capsize=5, linewidth=2)

    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(all_labels)
    ax.set_xlabel('Effect Size (Mean Difference: Instruct - Base)', fontsize=FONT_SIZE)
    ax.set_title('Forest Plot: Conditional Margin Inflation Effect Sizes\n(95% Bootstrap CI)', fontsize=TITLE_SIZE)

    plt.tight_layout()

    save_path = figures_dir / "forest_plot.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return str(save_path)


def save_all_figures(
    family_results: dict[str, dict],
    arrays_by_family: dict[str, dict],
    figures_dir: Path = None,
) -> list[str]:
    """
    Generate and save all figures.

    Args:
        family_results: Dict mapping family name to analysis results
        arrays_by_family: Dict mapping family name to arrays dict
        figures_dir: Output directory for figures

    Returns:
        List of saved figure paths
    """
    if figures_dir is None:
        figures_dir = FIGURES_DIR

    figures_dir.mkdir(parents=True, exist_ok=True)

    paths = []

    # Required figure
    paths.append(plot_gate_metrics(family_results, figures_dir))

    # Additional figures
    paths.append(plot_kde_distributions(family_results, arrays_by_family, figures_dir))
    paths.append(plot_box_plots(arrays_by_family, figures_dir))
    paths.append(plot_inflation_ratios(family_results, figures_dir))
    paths.append(plot_forest(family_results, figures_dir))

    return paths
