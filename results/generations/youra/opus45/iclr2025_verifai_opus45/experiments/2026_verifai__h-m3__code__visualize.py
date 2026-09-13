"""Visualization for H-M3 analysis."""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List

from config import AnalysisConfig


def plot_gate_comparison(
    g3_rate: float,
    g4_rate: float,
    margin: float,
    output_path: str,
    cfg: AnalysisConfig = None
) -> None:
    """Bar chart comparing G3 vs G4 with threshold line.

    MANDATORY figure for gate evaluation.

    Args:
        g3_rate: G3 success rate
        g4_rate: G4 success rate
        margin: Equivalence margin (0.02)
        output_path: Output file path
        cfg: Optional config for styling
    """
    if cfg is None:
        cfg = AnalysisConfig()

    fig, ax = plt.subplots(figsize=(cfg.fig_width, cfg.fig_height))

    # Bar positions
    x = [0, 1]
    heights = [g3_rate * 100, g4_rate * 100]
    colors = [cfg.color_g3, cfg.color_g4]
    labels = ['G3 (Error + Line)', 'G4 (Full Trace)']

    # Plot bars
    bars = ax.bar(x, heights, color=colors, width=0.6, edgecolor='black', linewidth=1.5)

    # Add threshold line (G3 + margin)
    threshold = (g3_rate + margin) * 100
    ax.axhline(y=threshold, color=cfg.color_threshold, linestyle='--', linewidth=2,
               label=f'G3 + {margin*100:.0f}% threshold ({threshold:.1f}%)')

    # Add value labels on bars
    for bar, height in zip(bars, heights):
        ax.text(bar.get_x() + bar.get_width()/2, height + 1,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Styling
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title('H-M3 Gate: G3 vs G4 Success Rate Comparison', fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(heights) + 10)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    # Gate result annotation
    diff = g4_rate - g3_rate
    within_margin = diff <= margin
    gate_text = "PASS" if within_margin else "FAIL"
    gate_color = "green" if within_margin else "red"
    ax.text(0.5, 0.95, f'Gate: {gate_text} (diff: {diff*100:.1f}%)',
            transform=ax.transAxes, fontsize=14, fontweight='bold',
            ha='center', va='top', color=gate_color,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=cfg.dpi, bbox_inches='tight')
    plt.close()
    print(f"Saved gate comparison figure to {output_path}")


def plot_contingency_heatmap(
    table: np.ndarray,
    output_path: str,
    cfg: AnalysisConfig = None
) -> None:
    """2x2 heatmap of paired outcomes.

    Args:
        table: 2x2 contingency table
        output_path: Output file path
        cfg: Optional config for styling
    """
    if cfg is None:
        cfg = AnalysisConfig()

    fig, ax = plt.subplots(figsize=(cfg.fig_width, cfg.fig_height))

    # Create heatmap with annotations
    sns.heatmap(table, annot=True, fmt='d', cmap='Blues',
                xticklabels=['G4 Success', 'G4 Fail'],
                yticklabels=['G3 Success', 'G3 Fail'],
                ax=ax, annot_kws={'size': 16, 'weight': 'bold'},
                cbar_kws={'label': 'Count'})

    ax.set_title('Contingency Table: Paired G3 vs G4 Outcomes', fontsize=14, fontweight='bold')
    ax.set_xlabel('G4 Outcome', fontsize=12)
    ax.set_ylabel('G3 Outcome', fontsize=12)

    # Add cell labels
    cell_labels = [
        ['Both Success', 'G3 Only'],
        ['G4 Only', 'Both Fail']
    ]
    for i in range(2):
        for j in range(2):
            ax.text(j + 0.5, i + 0.75, cell_labels[i][j],
                    ha='center', va='center', fontsize=9, color='gray')

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=cfg.dpi, bbox_inches='tight')
    plt.close()
    print(f"Saved contingency heatmap to {output_path}")


def plot_confidence_interval(
    ci_result: Dict,
    output_path: str,
    margin: float = 0.02,
    cfg: AnalysisConfig = None
) -> None:
    """Point estimate with 95% CI for G4-G3 difference.

    Args:
        ci_result: Confidence interval results
        output_path: Output file path
        margin: Equivalence margin for reference lines
        cfg: Optional config for styling
    """
    if cfg is None:
        cfg = AnalysisConfig()

    fig, ax = plt.subplots(figsize=(cfg.fig_width, cfg.fig_height * 0.6))

    point = ci_result['point_estimate'] * 100
    ci_lower = ci_result['ci_lower'] * 100
    ci_upper = ci_result['ci_upper'] * 100

    # Plot point estimate and CI
    ax.errorbar(point, 0, xerr=[[point - ci_lower], [ci_upper - point]],
                fmt='o', markersize=12, color=cfg.color_g4, capsize=8,
                capthick=2, elinewidth=2, label=f'G4-G3 diff: {point:.2f}%')

    # Add margin reference lines
    ax.axvline(x=margin * 100, color=cfg.color_threshold, linestyle='--',
               linewidth=2, label=f'+{margin*100:.0f}% margin')
    ax.axvline(x=-margin * 100, color=cfg.color_threshold, linestyle='--',
               linewidth=2, label=f'-{margin*100:.0f}% margin')
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1, alpha=0.5)

    # Shading for equivalence region
    ax.axvspan(-margin * 100, margin * 100, alpha=0.2, color='green',
               label='Equivalence region')

    ax.set_xlim(-15, 15)
    ax.set_ylim(-0.5, 0.5)
    ax.set_yticks([])
    ax.set_xlabel('Difference in Success Rate (G4 - G3) [%]', fontsize=12)
    ax.set_title(f'95% Confidence Interval for G4-G3 Difference\n'
                 f'Point estimate: {point:.2f}% [{ci_lower:.2f}%, {ci_upper:.2f}%]',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=cfg.dpi, bbox_inches='tight')
    plt.close()
    print(f"Saved confidence interval plot to {output_path}")


def plot_granularity_curve(
    results: List[Dict],
    output_path: str,
    cfg: AnalysisConfig = None
) -> None:
    """G0-G4 success rates showing non-monotonic pattern.

    Args:
        results: Full H-M1 results list
        output_path: Output file path
        cfg: Optional config for styling
    """
    if cfg is None:
        cfg = AnalysisConfig()

    # Compute success rates per granularity
    granularities = ['G0', 'G1', 'G2', 'G3', 'G4']
    rates = []

    for g in granularities:
        g_results = [r for r in results if r['granularity'] == g]
        if g_results:
            successes = sum(1 for r in g_results if r['success'])
            rate = successes / len(g_results) * 100
        else:
            rate = 0
        rates.append(rate)

    fig, ax = plt.subplots(figsize=(cfg.fig_width, cfg.fig_height))

    # Plot line with markers
    x = range(len(granularities))
    ax.plot(x, rates, 'o-', markersize=10, linewidth=2, color=cfg.color_g4)

    # Highlight G3 and G4
    ax.scatter([3], [rates[3]], s=150, color=cfg.color_g3, zorder=5,
               label=f'G3: {rates[3]:.1f}%', edgecolors='black', linewidth=2)
    ax.scatter([4], [rates[4]], s=150, color=cfg.color_g4, zorder=5,
               label=f'G4: {rates[4]:.1f}%', edgecolors='black', linewidth=2)

    # Add value labels
    for i, (g, rate) in enumerate(zip(granularities, rates)):
        ax.annotate(f'{rate:.1f}%', (i, rate), textcoords="offset points",
                    xytext=(0, 10), ha='center', fontsize=10, fontweight='bold')

    # Labels for granularity levels
    granularity_labels = [
        'G0\n(Pass/Fail)',
        'G1\n(Error Type)',
        'G2\n(Error Msg)',
        'G3\n(Error+Line)',
        'G4\n(Full Trace)'
    ]

    ax.set_xticks(x)
    ax.set_xticklabels(granularity_labels, fontsize=10)
    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_xlabel('Error Feedback Granularity', fontsize=12)
    ax.set_title('Non-Monotonic Relationship: Success Rate vs Granularity\n'
                 '(From H-M1 Experiment)', fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(rates) + 15)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    # Add annotation about non-monotonicity
    ax.text(0.5, 0.02, 'Note: Higher granularity does not always improve success rate',
            transform=ax.transAxes, fontsize=10, ha='center', style='italic', alpha=0.7)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=cfg.dpi, bbox_inches='tight')
    plt.close()
    print(f"Saved granularity curve to {output_path}")


def generate_all_figures(
    g3_rate: float,
    g4_rate: float,
    table: np.ndarray,
    ci_result: Dict,
    results: List[Dict],
    cfg: AnalysisConfig
) -> None:
    """Generate all 4 required figures.

    Args:
        g3_rate: G3 success rate
        g4_rate: G4 success rate
        table: 2x2 contingency table
        ci_result: Confidence interval results
        results: Full H-M1 results list
        cfg: Analysis configuration
    """
    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)

    print("\nGenerating figures...")

    # 1. MANDATORY: Gate comparison bar chart
    plot_gate_comparison(g3_rate, g4_rate, cfg.equivalence_margin,
                         cfg.output_gate_comparison, cfg)

    # 2. Contingency table heatmap
    plot_contingency_heatmap(table, cfg.output_contingency_heatmap, cfg)

    # 3. Confidence interval plot
    plot_confidence_interval(ci_result, cfg.output_confidence_interval,
                             cfg.equivalence_margin, cfg)

    # 4. Granularity curve (non-monotonic pattern)
    plot_granularity_curve(results, cfg.output_granularity_curve, cfg)

    print(f"\nAll 4 figures saved to {cfg.figures_dir}/")
