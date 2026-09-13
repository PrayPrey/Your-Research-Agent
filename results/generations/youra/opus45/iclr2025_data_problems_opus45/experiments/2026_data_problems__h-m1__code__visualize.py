"""
Visualization for H-M1 convex experiment.
Generates gate figures and supplementary plots.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict

from config import HM1Config


def plot_gate_metric(
    partial_corrs: Dict[int, float],
    cfg: HM1Config,
) -> None:
    """
    Bar chart: partial corr per budget. Horizontal line at 0.95 threshold.
    Saves: cfg.figures_dir/gate_partial_correlation.png
    """
    budgets = sorted(partial_corrs.keys())
    correlations = [partial_corrs[b] for b in budgets]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(range(len(budgets)), correlations, color='steelblue', alpha=0.8)

    # Color bars based on threshold
    for i, (b, c) in enumerate(zip(budgets, correlations)):
        if c >= cfg.partial_corr_threshold:
            bars[i].set_color('green')
        else:
            bars[i].set_color('red')

    ax.axhline(y=cfg.partial_corr_threshold, color='red', linestyle='--',
               linewidth=2, label=f'Threshold ({cfg.partial_corr_threshold})')

    ax.set_xticks(range(len(budgets)))
    ax.set_xticklabels([str(b) for b in budgets])
    ax.set_xlabel('Compute Budget', fontsize=12)
    ax.set_ylabel('corr(rho_r, rho_m)', fontsize=12)
    ax.set_title('H-M1 Gate Metric: Cross-Metric Correlation by Budget\n(Convex Logistic Regression)', fontsize=14)
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    # Add value labels
    for i, c in enumerate(correlations):
        ax.text(i, c + 0.02, f'{c:.3f}', ha='center', fontsize=10)

    plt.tight_layout()
    path = os.path.join(cfg.figures_dir, 'gate_partial_correlation.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_scatter_rho_r_rho_m(
    metrics_df: pd.DataFrame,
    cfg: HM1Config,
) -> None:
    """
    rho_r vs rho_m scatter, colored by method, faceted by budget.
    Saves: cfg.figures_dir/scatter_metrics.png
    """
    budgets = sorted(metrics_df['budget'].unique())
    methods = metrics_df['method'].unique()
    colors = {'TRAK': 'blue', 'TracIn': 'orange', 'IF': 'green', 'FastIF': 'red'}

    fig, axes = plt.subplots(1, len(budgets), figsize=(4*len(budgets), 4))
    if len(budgets) == 1:
        axes = [axes]

    for ax, budget in zip(axes, budgets):
        df_budget = metrics_df[metrics_df['budget'] == budget]

        for method in methods:
            df_method = df_budget[df_budget['method'] == method]
            ax.scatter(df_method['rho_r'], df_method['rho_m'],
                      c=colors.get(method, 'gray'), label=method, alpha=0.7, s=50)

        ax.set_xlabel('rho_r (rank)', fontsize=10)
        ax.set_ylabel('rho_m (magnitude)', fontsize=10)
        ax.set_title(f'Budget {budget}', fontsize=11)
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.1)
        ax.plot([0, 1], [0, 1], 'k--', alpha=0.3)
        ax.grid(alpha=0.3)

    axes[0].legend(loc='lower right', fontsize=8)

    plt.suptitle('H-M1: rho_r vs rho_m by Method and Budget', fontsize=14, y=1.02)
    plt.tight_layout()
    path = os.path.join(cfg.figures_dir, 'scatter_metrics.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_error_axis_regression(
    metrics_df: pd.DataFrame,
    cfg: HM1Config,
) -> None:
    """
    Metrics vs approximation error norm with regression line and R^2 annotation.
    Saves: cfg.figures_dir/error_axis_regression.png
    """
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    X = metrics_df['error_norm'].values.reshape(-1, 1)

    for ax, (metric_name, color) in zip(axes, [('rho_r', 'blue'), ('rho_m', 'green')]):
        y = metrics_df[metric_name].values

        ax.scatter(X, y, c=color, alpha=0.6, label='Data points')

        # Fit regression
        reg = LinearRegression()
        reg.fit(X, y)
        X_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
        y_pred = reg.predict(X_line)

        r2 = r2_score(y, reg.predict(X))

        ax.plot(X_line, y_pred, 'r--', linewidth=2, label=f'R^2 = {r2:.4f}')
        ax.set_xlabel('Approximation Error ||scores - LOO||', fontsize=11)
        ax.set_ylabel(metric_name, fontsize=11)
        ax.set_title(f'{metric_name} vs Error Norm', fontsize=12)
        ax.legend()
        ax.grid(alpha=0.3)

    plt.suptitle('H-M1: Single-Error-Axis Regression', fontsize=14)
    plt.tight_layout()
    path = os.path.join(cfg.figures_dir, 'error_axis_regression.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_method_comparison(
    metrics_df: pd.DataFrame,
    cfg: HM1Config,
) -> None:
    """
    Bar chart: rho_r and rho_m per method at each budget.
    Saves: cfg.figures_dir/method_comparison.png
    """
    methods = cfg.methods
    budgets = cfg.compute_budgets

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    for ax, metric in zip(axes, ['rho_r', 'rho_m']):
        x = np.arange(len(budgets))
        width = 0.2
        colors = ['blue', 'orange', 'green', 'red']

        for i, method in enumerate(methods):
            means = []
            stds = []
            for budget in budgets:
                df_sub = metrics_df[(metrics_df['method'] == method) &
                                    (metrics_df['budget'] == budget)]
                means.append(df_sub[metric].mean())
                stds.append(df_sub[metric].std())

            ax.bar(x + i*width, means, width, label=method, color=colors[i], alpha=0.8)
            ax.errorbar(x + i*width, means, yerr=stds, fmt='none', color='black', capsize=3)

        ax.set_xlabel('Compute Budget', fontsize=11)
        ax.set_ylabel(metric, fontsize=11)
        ax.set_title(f'{metric} by Method and Budget', fontsize=12)
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels([str(b) for b in budgets])
        ax.legend(loc='lower right')
        ax.grid(axis='y', alpha=0.3)

    plt.suptitle('H-M1: Method Comparison (Convex Setting)', fontsize=14)
    plt.tight_layout()
    path = os.path.join(cfg.figures_dir, 'method_comparison.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_hessian_eigenspectrum(
    eigenvalues: np.ndarray,
    cfg: HM1Config,
) -> None:
    """
    Log-scale histogram of Hessian eigenvalues.
    Saves: cfg.figures_dir/hessian_eigenspectrum.png
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Log-scale eigenvalues
    log_eigs = np.log10(eigenvalues[eigenvalues > 0])

    ax.hist(log_eigs, bins=50, color='steelblue', alpha=0.8, edgecolor='black')
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='1.0 (log10=0)')

    ax.set_xlabel('log10(eigenvalue)', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title(f'H-M1: Hessian Eigenspectrum\nMin={eigenvalues.min():.2e}, Max={eigenvalues.max():.2e}', fontsize=12)
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    path = os.path.join(cfg.figures_dir, 'hessian_eigenspectrum.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_all(
    partial_corrs: Dict[int, float],
    metrics_df: pd.DataFrame,
    eigenvalues: np.ndarray,
    cfg: HM1Config,
) -> None:
    """Generate all figures."""
    print("\nGenerating figures...")
    plot_gate_metric(partial_corrs, cfg)
    plot_scatter_rho_r_rho_m(metrics_df, cfg)
    plot_error_axis_regression(metrics_df, cfg)
    plot_method_comparison(metrics_df, cfg)
    plot_hessian_eigenspectrum(eigenvalues, cfg)
    print("All figures generated.")
