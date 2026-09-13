"""
Visualization module for H-M2 Percentile-Normalized Monotonicity Attenuation.
Publication-quality figures for β_percentile comparison, bootstrap distributions, and forest plots.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional

from config import FIGURES_DIR

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid')

FONT_SIZE = 12
TITLE_SIZE = 14
DPI = 300
FIGSIZE_SINGLE = (8, 6)
FIGSIZE_WIDE = (12, 5)


def plot_gate_metrics(
    family_results: dict[str, dict],
    figures_dir: Optional[Path] = None,
) -> str:
    """
    Bar chart: β_percentile base vs instruct per family with 95% CI error bars (REQUIRED figure).

    Args:
        family_results: Dict mapping family name to analyze_family() results
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

    # Extract values
    base_means = [family_results[f]["base_ci"][0] for f in families]  # mean from CI tuple
    inst_means = [family_results[f]["inst_ci"][0] for f in families]
    base_errs_low = [family_results[f]["base_ci"][0] - family_results[f]["base_ci"][1] for f in families]
    base_errs_high = [family_results[f]["base_ci"][2] - family_results[f]["base_ci"][0] for f in families]
    inst_errs_low = [family_results[f]["inst_ci"][0] - family_results[f]["inst_ci"][1] for f in families]
    inst_errs_high = [family_results[f]["inst_ci"][2] - family_results[f]["inst_ci"][0] for f in families]

    # Plot bars
    bars1 = ax.bar(x - width/2, base_means, width, label='Base',
                   yerr=[base_errs_low, base_errs_high], capsize=5, color='steelblue')
    bars2 = ax.bar(x + width/2, inst_means, width, label='Instruct',
                   yerr=[inst_errs_low, inst_errs_high], capsize=5, color='coral')

    # Formatting
    ax.set_xlabel('Model Family', fontsize=FONT_SIZE)
    ax.set_ylabel('β_percentile (Monotonicity Slope)', fontsize=FONT_SIZE)
    ax.set_title('H-M2: Percentile-Normalized Monotonicity Attenuation\n'
                 '(Higher β = stronger confidence-correctness relationship)',
                 fontsize=TITLE_SIZE)
    ax.set_xticks(x)
    ax.set_xticklabels([f.capitalize() for f in families], fontsize=FONT_SIZE)
    ax.legend(fontsize=FONT_SIZE)
    ax.tick_params(axis='both', labelsize=FONT_SIZE)

    # Add significance markers
    for i, family in enumerate(families):
        if family_results[family]["gate_pass"]:
            y_max = max(base_means[i], inst_means[i]) + 0.3
            ax.annotate('*', xy=(i, y_max), ha='center', fontsize=16, fontweight='bold')

    plt.tight_layout()
    output_path = figures_dir / "gate_metrics_beta_percentile.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()

    return str(output_path)


def plot_bootstrap_distributions(
    family_results: dict[str, dict],
    figures_dir: Optional[Path] = None,
) -> str:
    """
    Overlaid histograms of bootstrap β distributions (base vs instruct) per family.

    Args:
        family_results: Dict mapping family name to analyze_family() results
        figures_dir: Output directory

    Returns:
        Path to saved figure
    """
    if figures_dir is None:
        figures_dir = FIGURES_DIR

    families = list(family_results.keys())
    n_families = len(families)

    fig, axes = plt.subplots(1, n_families, figsize=(6*n_families, 5))
    if n_families == 1:
        axes = [axes]

    for ax, family in zip(axes, families):
        result = family_results[family]
        base_betas = result["base_betas"]
        inst_betas = result["inst_betas"]

        ax.hist(base_betas, bins=50, alpha=0.6, label='Base', color='steelblue', density=True)
        ax.hist(inst_betas, bins=50, alpha=0.6, label='Instruct', color='coral', density=True)

        # Add vertical lines for means
        ax.axvline(np.mean(base_betas), color='steelblue', linestyle='--', linewidth=2, label=f'Base mean: {np.mean(base_betas):.3f}')
        ax.axvline(np.mean(inst_betas), color='coral', linestyle='--', linewidth=2, label=f'Inst mean: {np.mean(inst_betas):.3f}')

        ax.set_xlabel('β_percentile', fontsize=FONT_SIZE)
        ax.set_ylabel('Density', fontsize=FONT_SIZE)
        ax.set_title(f'{family.capitalize()}: Bootstrap β Distributions', fontsize=TITLE_SIZE)
        ax.legend(fontsize=10)
        ax.tick_params(axis='both', labelsize=FONT_SIZE)

    plt.tight_layout()
    output_path = figures_dir / "bootstrap_distributions.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()

    return str(output_path)


def plot_logistic_curves(
    family_results: dict[str, dict],
    arrays_by_family: dict[str, dict],
    figures_dir: Optional[Path] = None,
) -> str:
    """
    Pr(correct) vs z-score(margin) sigmoid curves for each condition.

    Args:
        family_results: Dict mapping family name to analyze_family() results
        arrays_by_family: Raw arrays for computing z-scores
        figures_dir: Output directory

    Returns:
        Path to saved figure
    """
    if figures_dir is None:
        figures_dir = FIGURES_DIR

    from analysis import zscore_normalize

    families = list(family_results.keys())
    n_families = len(families)

    fig, axes = plt.subplots(1, n_families, figsize=(6*n_families, 5))
    if n_families == 1:
        axes = [axes]

    for ax, family in zip(axes, families):
        result = family_results[family]
        arrays = arrays_by_family[family]

        # Z-score normalize margins
        base_z = zscore_normalize(arrays["base_margins"])
        inst_z = zscore_normalize(arrays["inst_margins"])

        # Create smooth x-range for curves
        x_range = np.linspace(-4, 4, 200)

        # Sigmoid: σ(α + β*x) - assuming α≈0 for normalized data
        def sigmoid(x, beta, alpha=0):
            return 1 / (1 + np.exp(-(alpha + beta * x)))

        base_curve = sigmoid(x_range, result["base_beta"])
        inst_curve = sigmoid(x_range, result["inst_beta"])

        # Plot curves
        ax.plot(x_range, base_curve, 'b-', linewidth=2, label=f'Base (β={result["base_beta"]:.3f})')
        ax.plot(x_range, inst_curve, 'r-', linewidth=2, label=f'Instruct (β={result["inst_beta"]:.3f})')

        # Scatter actual data (subsample for clarity)
        n_plot = 1000
        idx = np.random.choice(len(base_z), min(n_plot, len(base_z)), replace=False)
        ax.scatter(base_z[idx], arrays["base_correctness"][idx], alpha=0.1, s=10, c='steelblue')
        ax.scatter(inst_z[idx], arrays["inst_correctness"][idx], alpha=0.1, s=10, c='coral')

        ax.set_xlabel('z-score(margin)', fontsize=FONT_SIZE)
        ax.set_ylabel('Pr(correct)', fontsize=FONT_SIZE)
        ax.set_title(f'{family.capitalize()}: Logistic Regression Curves', fontsize=TITLE_SIZE)
        ax.legend(fontsize=10)
        ax.set_xlim(-4, 4)
        ax.set_ylim(-0.05, 1.05)
        ax.tick_params(axis='both', labelsize=FONT_SIZE)

    plt.tight_layout()
    output_path = figures_dir / "logistic_curves.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()

    return str(output_path)


def plot_forest(
    family_results: dict[str, dict],
    figures_dir: Optional[Path] = None,
) -> str:
    """
    Forest plot: delta_beta effect sizes with 95% CIs per family.

    Args:
        family_results: Dict mapping family name to analyze_family() results
        figures_dir: Output directory

    Returns:
        Path to saved figure
    """
    if figures_dir is None:
        figures_dir = FIGURES_DIR

    families = list(family_results.keys())
    n_families = len(families)

    fig, ax = plt.subplots(figsize=(8, 4 + n_families))

    y_positions = np.arange(n_families)

    for i, family in enumerate(families):
        result = family_results[family]
        delta = result["delta_beta"]
        ci_low = result["delta_ci_lower"]
        ci_high = result["delta_ci_upper"]

        # Plot point and error bar
        color = 'green' if result["gate_pass"] else 'red'
        ax.errorbar(delta, i, xerr=[[delta - ci_low], [ci_high - delta]],
                   fmt='o', markersize=10, color=color, capsize=5, capthick=2)

        # Add text annotation
        ax.annotate(f'Δβ={delta:.3f} (p={result["p_value"]:.3f})',
                   xy=(delta, i), xytext=(10, 0),
                   textcoords='offset points', fontsize=10, va='center')

    # Reference line at 0
    ax.axvline(0, color='gray', linestyle='--', linewidth=1)

    ax.set_yticks(y_positions)
    ax.set_yticklabels([f.capitalize() for f in families], fontsize=FONT_SIZE)
    ax.set_xlabel('Δβ = β_base - β_instruct\n(Positive = monotonicity attenuation)', fontsize=FONT_SIZE)
    ax.set_title('H-M2: Forest Plot of Effect Sizes', fontsize=TITLE_SIZE)
    ax.tick_params(axis='both', labelsize=FONT_SIZE)

    # Legend for colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', label='Gate PASS'),
        Patch(facecolor='red', label='Gate FAIL'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    plt.tight_layout()
    output_path = figures_dir / "forest_plot.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()

    return str(output_path)


def save_all_figures(
    family_results: dict[str, dict],
    arrays_by_family: dict[str, dict],
    figures_dir: Optional[Path] = None,
) -> list[str]:
    """
    Generate all figures for H-M2 validation report.

    Args:
        family_results: Dict mapping family name to analyze_family() results
        arrays_by_family: Raw arrays for z-score computation
        figures_dir: Output directory

    Returns:
        List of saved figure paths
    """
    if figures_dir is None:
        figures_dir = FIGURES_DIR

    figures_dir.mkdir(parents=True, exist_ok=True)

    paths = []
    paths.append(plot_gate_metrics(family_results, figures_dir))
    paths.append(plot_bootstrap_distributions(family_results, figures_dir))
    paths.append(plot_logistic_curves(family_results, arrays_by_family, figures_dir))
    paths.append(plot_forest(family_results, figures_dir))

    return paths
