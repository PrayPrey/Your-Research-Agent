"""H-M1 Visualization: Generate required figures for validation report."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

FIGURE_CONFIG = {
    "dpi": 150,
    "format": "png",
    "figsize": (8, 6),
}


def plot_group_comparison_bar(results: dict, out_path: str) -> None:
    """Bar chart: high-HHI vs low-HHI mean top-5 share with error bars."""
    fig, ax = plt.subplots(figsize=FIGURE_CONFIG["figsize"])

    groups = ['High HHI', 'Low HHI']
    means = [results['high_mean'], results['low_mean']]
    colors = ['#e74c3c', '#3498db']

    bars = ax.bar(groups, means, color=colors, edgecolor='black', linewidth=1.2)

    ax.set_ylabel('Mean Top-5 Share', fontsize=12)
    ax.set_title(f"High vs Low HHI Group Comparison\n(Mann-Whitney p={results['mann_whitney_p']:.4f})", fontsize=14)
    ax.set_ylim(0, max(means) * 1.2)

    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{mean:.3f}', ha='center', va='bottom', fontsize=11)

    plt.tight_layout()
    plt.savefig(out_path, dpi=FIGURE_CONFIG["dpi"], format=FIGURE_CONFIG["format"])
    plt.close()
    print(f"  Saved: {out_path}")


def plot_hhi_vs_top5_scatter(venue_year_df: pd.DataFrame, out_path: str) -> None:
    """Scatter plot: HHI vs top-5 share, color by venue."""
    fig, ax = plt.subplots(figsize=FIGURE_CONFIG["figsize"])

    venues = venue_year_df['venue'].unique()
    colors = {'NeurIPS': '#e74c3c', 'ICML': '#3498db', 'ICLR': '#2ecc71'}

    for venue in venues:
        subset = venue_year_df[venue_year_df['venue'] == venue]
        ax.scatter(subset['hhi'], subset['top5_share'],
                   c=colors.get(venue, 'gray'), label=venue, s=80, alpha=0.7)

    # Add trend line
    z = np.polyfit(venue_year_df['hhi'], venue_year_df['top5_share'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(venue_year_df['hhi'].min(), venue_year_df['hhi'].max(), 100)
    ax.plot(x_line, p(x_line), '--', color='gray', alpha=0.8, label='Trend')

    ax.set_xlabel('HHI', fontsize=12)
    ax.set_ylabel('Top-5 Share', fontsize=12)
    ax.set_title('HHI vs Top-5 Share by Venue', fontsize=14)
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=FIGURE_CONFIG["dpi"], format=FIGURE_CONFIG["format"])
    plt.close()
    print(f"  Saved: {out_path}")


def plot_distribution_histograms(venue_year_df: pd.DataFrame, median_hhi: float, out_path: str) -> None:
    """Side-by-side histograms of top-5 share for high/low HHI groups."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    high = venue_year_df[venue_year_df['hhi'] > median_hhi]['top5_share']
    low = venue_year_df[venue_year_df['hhi'] <= median_hhi]['top5_share']

    axes[0].hist(low, bins=8, color='#3498db', edgecolor='black', alpha=0.7)
    axes[0].axvline(low.mean(), color='red', linestyle='--', label=f'Mean: {low.mean():.3f}')
    axes[0].set_xlabel('Top-5 Share', fontsize=11)
    axes[0].set_ylabel('Count', fontsize=11)
    axes[0].set_title(f'Low HHI Group (n={len(low)})', fontsize=12)
    axes[0].legend()

    axes[1].hist(high, bins=8, color='#e74c3c', edgecolor='black', alpha=0.7)
    axes[1].axvline(high.mean(), color='blue', linestyle='--', label=f'Mean: {high.mean():.3f}')
    axes[1].set_xlabel('Top-5 Share', fontsize=11)
    axes[1].set_ylabel('Count', fontsize=11)
    axes[1].set_title(f'High HHI Group (n={len(high)})', fontsize=12)
    axes[1].legend()

    plt.suptitle('Distribution of Top-5 Share by HHI Group', fontsize=14)
    plt.tight_layout()
    plt.savefig(out_path, dpi=FIGURE_CONFIG["dpi"], format=FIGURE_CONFIG["format"])
    plt.close()
    print(f"  Saved: {out_path}")


def plot_venue_year_heatmap(venue_year_df: pd.DataFrame, out_path: str) -> None:
    """Heatmap showing top-5 share by venue and year."""
    pivot = venue_year_df.pivot_table(index='venue', columns='year', values='top5_share')

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(pivot, annot=True, fmt='.3f', cmap='RdYlBu_r', ax=ax,
                cbar_kws={'label': 'Top-5 Share'})

    ax.set_title('Top-5 Share by Venue and Year', fontsize=14)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Venue', fontsize=12)

    plt.tight_layout()
    plt.savefig(out_path, dpi=FIGURE_CONFIG["dpi"], format=FIGURE_CONFIG["format"])
    plt.close()
    print(f"  Saved: {out_path}")


def generate_all(results: dict, venue_year_df: pd.DataFrame, out_dir: str = "figures/") -> None:
    """Generate all 4 required figures."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    plot_group_comparison_bar(results, str(out_path / "group_comparison_bar.png"))
    plot_hhi_vs_top5_scatter(venue_year_df, str(out_path / "hhi_vs_top5_scatter.png"))
    plot_distribution_histograms(venue_year_df, results['median_hhi'], str(out_path / "distribution_histograms.png"))
    plot_venue_year_heatmap(venue_year_df, str(out_path / "venue_year_heatmap.png"))
