"""H-M2 Visualization: Gate metrics, scatter plots, and model comparison."""

from pathlib import Path
from typing import Dict, Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def plot_gate_metrics(metrics: Dict[str, Any], out_path: str) -> None:
    """Plot β coefficient with 95% CI and p-value annotation."""
    fig, ax = plt.subplots(figsize=(8, 6))

    beta = metrics['beta_hhi']
    ci_lower = metrics['ci_lower']
    ci_upper = metrics['ci_upper']
    p_value = metrics['p_value']

    # Convert to odds ratio scale for interpretation
    or_val = metrics['odds_ratio']
    or_ci_lower = ci_lower
    or_ci_upper = ci_upper

    # Plot coefficient (log-odds scale)
    ax.barh(['Prior HHI'], [beta], color='steelblue', alpha=0.7, height=0.5)
    ax.errorbar([beta], ['Prior HHI'],
                xerr=[[beta - np.log(or_ci_lower)], [np.log(or_ci_upper) - beta]],
                fmt='none', color='black', capsize=5, capthick=2)

    # Add vertical line at 0
    ax.axvline(x=0, color='red', linestyle='--', alpha=0.5, label='Null (β=0)')

    # Annotations
    sig_marker = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns'
    ax.text(beta, 0.3, f'β = {beta:.3f}\np = {p_value:.4f} {sig_marker}\nOR = {or_val:.2f}',
            ha='center', va='bottom', fontsize=10)

    ax.set_xlabel('Log-Odds Coefficient (β)', fontsize=12)
    ax.set_title('H-M2 Gate Metrics: Effect of Prior HHI on Standard Benchmark Adoption', fontsize=14)
    ax.set_xlim(min(-0.5, beta - 1), max(0.5, beta + 1))

    # Gate status annotation
    gate_status = "PASSED" if metrics['beta_hhi'] > 0 and p_value < 0.05 else "FAILED"
    gate_color = 'green' if gate_status == "PASSED" else 'red'
    ax.text(0.98, 0.98, f'GATE: {gate_status}', transform=ax.transAxes,
            ha='right', va='top', fontsize=14, fontweight='bold', color=gate_color,
            bbox=dict(boxstyle='round', facecolor='white', edgecolor=gate_color))

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_hhi_vs_adoption_scatter(labeled_df: pd.DataFrame, out_path: str) -> None:
    """Scatter plot of HHI vs adoption rate by venue."""
    # Aggregate by venue-year
    agg = labeled_df.groupby(['venue', 'year', 'prior_hhi']).agg(
        adoption_rate=('standard_benchmark', 'mean'),
        n_papers=('paper_id', 'count')
    ).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))

    venues = agg['venue'].unique()
    colors = {'NeurIPS': 'blue', 'ICML': 'green', 'ICLR': 'orange'}
    markers = {'NeurIPS': 'o', 'ICML': 's', 'ICLR': '^'}

    for venue in venues:
        venue_data = agg[agg['venue'] == venue]
        ax.scatter(venue_data['prior_hhi'], venue_data['adoption_rate'],
                   c=colors.get(venue, 'gray'), marker=markers.get(venue, 'o'),
                   s=venue_data['n_papers'] / 10, alpha=0.7, label=venue)

    # Add trend line
    z = np.polyfit(agg['prior_hhi'], agg['adoption_rate'], 1)
    p = np.poly1d(z)
    x_range = np.linspace(agg['prior_hhi'].min(), agg['prior_hhi'].max(), 100)
    ax.plot(x_range, p(x_range), 'r--', alpha=0.8, label=f'Trend (slope={z[0]:.2f})')

    ax.set_xlabel('Prior-Year HHI', fontsize=12)
    ax.set_ylabel('Standard Benchmark Adoption Rate', fontsize=12)
    ax.set_title('HHI vs Standard Benchmark Adoption by Venue-Year', fontsize=14)
    ax.legend(title='Venue', loc='lower right')
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_predicted_probability_curve(model_results, out_path: str) -> None:
    """Predicted probability curve across HHI range."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Generate HHI range
    hhi_range = np.linspace(0.1, 0.5, 100)

    # Get model coefficients
    intercept = model_results.params['Intercept']
    beta_hhi = model_results.params['prior_hhi']

    # Compute predicted probabilities
    log_odds = intercept + beta_hhi * hhi_range
    probs = 1 / (1 + np.exp(-log_odds))

    # Confidence intervals (approximate using standard errors)
    se_intercept = model_results.bse['Intercept']
    se_beta = model_results.bse['prior_hhi']

    # Upper and lower bounds (95% CI)
    log_odds_upper = (intercept + 1.96*se_intercept) + (beta_hhi + 1.96*se_beta) * hhi_range
    log_odds_lower = (intercept - 1.96*se_intercept) + (beta_hhi - 1.96*se_beta) * hhi_range
    probs_upper = 1 / (1 + np.exp(-log_odds_upper))
    probs_lower = 1 / (1 + np.exp(-log_odds_lower))

    ax.plot(hhi_range, probs, 'b-', linewidth=2, label='Predicted P(Standard)')
    ax.fill_between(hhi_range, probs_lower, probs_upper, alpha=0.2, color='blue', label='95% CI')

    ax.set_xlabel('Prior-Year HHI', fontsize=12)
    ax.set_ylabel('P(Standard Benchmark)', fontsize=12)
    ax.set_title('Predicted Probability of Standard Benchmark Adoption', fontsize=14)
    ax.set_xlim(0.1, 0.5)
    ax.set_ylim(0, 1)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_model_comparison_table(baseline_metrics: Dict[str, Any],
                                 proposed_metrics: Dict[str, Any],
                                 controlled_metrics: Dict[str, Any],
                                 out_path: str) -> None:
    """Model comparison table as figure."""
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('off')

    # Table data
    columns = ['Metric', 'Baseline', 'Proposed', 'Controlled']
    data = [
        ['N papers', f"{baseline_metrics['n_papers']:,}",
         f"{proposed_metrics['n_papers']:,}", f"{controlled_metrics['n_papers']:,}"],
        ['β(prior_HHI)', '-', f"{proposed_metrics['beta_hhi']:.4f}",
         f"{controlled_metrics['beta_hhi']:.4f}"],
        ['p-value', '-', f"{proposed_metrics['p_value']:.6f}",
         f"{controlled_metrics['p_value']:.6f}"],
        ['Odds Ratio', '-', f"{proposed_metrics['odds_ratio']:.3f}",
         f"{controlled_metrics['odds_ratio']:.3f}"],
        ['95% CI', '-',
         f"[{proposed_metrics['ci_lower']:.3f}, {proposed_metrics['ci_upper']:.3f}]",
         f"[{controlled_metrics['ci_lower']:.3f}, {controlled_metrics['ci_upper']:.3f}]"],
        ['Pseudo R²', '-', f"{proposed_metrics['pseudo_r2']:.4f}",
         f"{controlled_metrics['pseudo_r2']:.4f}"],
        ['AIC', f"{baseline_metrics['aic']:.1f}", f"{proposed_metrics['aic']:.1f}",
         f"{controlled_metrics['aic']:.1f}"],
    ]

    table = ax.table(cellText=data, colLabels=columns, loc='center',
                     cellLoc='center', colColours=['lightgray']*4)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)

    # Highlight significant results
    for i, row in enumerate(data):
        if 'p-value' in row[0]:
            for j in [2, 3]:
                if float(row[j]) < 0.05:
                    table[(i+1, j)].set_facecolor('lightgreen')

    ax.set_title('Model Comparison: Baseline vs Proposed vs Controlled',
                 fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def generate_all(proposed_metrics: Dict[str, Any],
                 controlled_metrics: Dict[str, Any],
                 baseline_metrics: Dict[str, Any],
                 labeled_df: pd.DataFrame,
                 model_results,
                 out_dir: str = "figures/") -> None:
    """Generate all visualizations."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    print("  Generating gate_metrics.png...")
    plot_gate_metrics(proposed_metrics, str(out_path / "gate_metrics.png"))

    print("  Generating hhi_vs_adoption_scatter.png...")
    plot_hhi_vs_adoption_scatter(labeled_df, str(out_path / "hhi_vs_adoption_scatter.png"))

    print("  Generating predicted_probability_curve.png...")
    plot_predicted_probability_curve(model_results, str(out_path / "predicted_probability_curve.png"))

    print("  Generating model_comparison_table.png...")
    plot_model_comparison_table(baseline_metrics, proposed_metrics, controlled_metrics,
                                str(out_path / "model_comparison_table.png"))

    print(f"  All figures saved to {out_dir}")


if __name__ == "__main__":
    # Test with dummy data
    print("Run analyze.py to generate actual figures")
