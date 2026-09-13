"""Visualization suite for H-M1 lagged correlation analysis."""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple

from config import FIGURES_DIR

FIGURE_DPI = 150


def plot_lag_profile(multilag_results: Dict[int, List[float]], save_path: str = None) -> None:
    """Plot mean correlation vs lag."""
    if save_path is None:
        save_path = os.path.join(FIGURES_DIR, "lag_profile.png")

    lags = sorted(multilag_results.keys())
    means = [np.mean(multilag_results[lag]) for lag in lags]
    stds = [np.std(multilag_results[lag]) / np.sqrt(len(multilag_results[lag])) for lag in lags]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(lags, means, yerr=stds, marker='o', capsize=5, linewidth=2)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=1, color='red', linestyle='--', alpha=0.5, label='Primary lag (1)')
    ax.set_xlabel('Lag (AI leads User when positive)')
    ax.set_ylabel('Mean Correlation')
    ax.set_title('Lagged Correlation Profile: AI → User Adaptation')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=FIGURE_DPI)
    plt.close()
    print(f"Saved: {save_path}")


def plot_gate_pvalue(p_value: float, target: float = 0.05, save_path: str = None) -> None:
    """Visualize p-value vs gate threshold."""
    if save_path is None:
        save_path = os.path.join(FIGURES_DIR, "gate_pvalue.png")

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = ['green' if p_value < target else 'red']
    ax.bar(['Lag-1 p-value'], [p_value], color=colors, alpha=0.7, edgecolor='black')
    ax.axhline(y=target, color='red', linestyle='--', linewidth=2, label=f'Gate threshold ({target})')
    ax.set_ylabel('p-value')
    ax.set_title(f'Gate Criterion: p < {target}\n({"PASS" if p_value < target else "FAIL"})')
    ax.legend()
    ax.set_ylim(0, max(0.2, p_value * 1.2))
    plt.tight_layout()
    plt.savefig(save_path, dpi=FIGURE_DPI)
    plt.close()
    print(f"Saved: {save_path}")


def plot_lag1_histogram(lag1_rs: List[float], save_path: str = None) -> None:
    """Histogram of lag-1 correlations."""
    if save_path is None:
        save_path = os.path.join(FIGURES_DIR, "lag1_histogram.png")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(lag1_rs, bins=50, edgecolor='black', alpha=0.7)
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero')
    ax.axvline(x=np.mean(lag1_rs), color='green', linestyle='-', linewidth=2,
               label=f'Mean: {np.mean(lag1_rs):.3f}')
    ax.set_xlabel('Lag-1 Correlation')
    ax.set_ylabel('Count')
    ax.set_title('Distribution of Per-Conversation Lag-1 Correlations')
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=FIGURE_DPI)
    plt.close()
    print(f"Saved: {save_path}")


def plot_length_scatter(
    trajectories: List[Tuple[List[float], List[float]]],
    lag1_rs: List[float],
    save_path: str = None
) -> None:
    """Scatter plot of correlation vs conversation length."""
    if save_path is None:
        save_path = os.path.join(FIGURES_DIR, "length_scatter.png")

    lengths = [len(user) for user, _ in trajectories]
    valid_mask = ~np.isnan(lag1_rs)
    lengths_valid = np.array(lengths)[valid_mask]
    rs_valid = np.array(lag1_rs)[valid_mask]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(lengths_valid, rs_valid, alpha=0.1, s=10)
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)

    from scipy import stats
    slope, intercept, r, p, _ = stats.linregress(lengths_valid, rs_valid)
    x_fit = np.linspace(lengths_valid.min(), lengths_valid.max(), 100)
    ax.plot(x_fit, slope * x_fit + intercept, color='green', linewidth=2,
            label=f'Trend: r={r:.3f}, p={p:.4f}')

    ax.set_xlabel('Conversation Length (turns)')
    ax.set_ylabel('Lag-1 Correlation')
    ax.set_title('Adaptation Strength vs Conversation Length')
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=FIGURE_DPI)
    plt.close()
    print(f"Saved: {save_path}")


def plot_shuffled_vs_real(
    real_rs: List[float],
    shuffled_rs: List[float],
    save_path: str = None
) -> None:
    """Box plot comparing real vs shuffled lag-1 correlations."""
    if save_path is None:
        save_path = os.path.join(FIGURES_DIR, "shuffled_vs_real.png")

    fig, ax = plt.subplots(figsize=(8, 6))
    data = [real_rs, shuffled_rs]
    bp = ax.boxplot(data, labels=['Real', 'Shuffled'], patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightgray')
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    ax.set_ylabel('Lag-1 Correlation')
    ax.set_title('Real vs Shuffled Baseline')
    plt.tight_layout()
    plt.savefig(save_path, dpi=FIGURE_DPI)
    plt.close()
    print(f"Saved: {save_path}")


def generate_all_figures(results: Dict) -> None:
    """Generate all figures from experiment results."""
    if 'multilag_results' in results:
        plot_lag_profile(results['multilag_results'])

    if 'real_stats' in results:
        plot_gate_pvalue(results['real_stats']['p_value'])

    if 'lag1_rs' in results:
        plot_lag1_histogram(results['lag1_rs'])

    if 'trajectories' in results and 'lag1_rs' in results:
        lag1_full = []
        from lagcorr import compute_lagged_correlation
        for user, ai in results['trajectories']:
            r, _ = compute_lagged_correlation(user, ai, lag=1)
            lag1_full.append(r)
        plot_length_scatter(results['trajectories'], lag1_full)

    if 'lag1_rs' in results and 'baseline_stats' in results:
        plot_shuffled_vs_real(
            results['lag1_rs'],
            results['baseline_stats'].get('shuffled_lag1_rs', [])
        )

    print(f"All figures saved to {FIGURES_DIR}")
