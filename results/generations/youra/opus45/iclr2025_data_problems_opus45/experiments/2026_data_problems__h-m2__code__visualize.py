"""
Visualization for H-M2: R^2 comparison and metric decoupling figures.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any

from config import HM2Config


def plot_gate_r2_comparison(
    r2_convex: Dict[str, float],
    r2_deep: Dict[str, float],
    cfg: HM2Config,
) -> None:
    """
    Bar chart: R^2 convex (H-M1) vs R^2 deep (H-M2) for rho_r and rho_m.
    Horizontal line at 0.80 threshold. Saves: figures/gate_r2_comparison.png
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    metrics = ['rho_r', 'rho_m']
    x = np.arange(len(metrics))
    width = 0.35

    convex_vals = [r2_convex.get('r2_rho_r', 0), r2_convex.get('r2_rho_m', 0)]
    deep_vals = [r2_deep.get('r2_rho_r', 0), r2_deep.get('r2_rho_m', 0)]

    bars1 = ax.bar(x - width/2, convex_vals, width, label='Convex (H-M1)', color='steelblue', alpha=0.8)
    bars2 = ax.bar(x + width/2, deep_vals, width, label='Deep (H-M2)', color='coral', alpha=0.8)

    # Threshold line
    ax.axhline(y=cfg.r2_threshold, color='red', linestyle='--', linewidth=2, label=f'Gate threshold ({cfg.r2_threshold})')

    ax.set_ylabel('R^2 (Single-Error-Axis)')
    ax.set_xlabel('Metric')
    ax.set_title('H-M2 Gate: R^2 Drop from Convex to Deep Network')
    ax.set_xticks(x)
    ax.set_xticklabels([r'$\rho_r$ (rank)', r'$\rho_m$ (magnitude)'])
    ax.legend()
    ax.set_ylim(0, 1.1)

    # Add value labels on bars
    for bar, val in zip(bars1, convex_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2f}', ha='center', va='bottom', fontsize=10)
    for bar, val in zip(bars2, deep_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    save_path = os.path.join(cfg.figures_dir, 'gate_r2_comparison.png')
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_scatter_metrics_vs_error(metrics_df: pd.DataFrame, cfg: HM2Config) -> None:
    """
    2-subplot scatter: rho_r vs error_norm and rho_m vs error_norm.
    Color by method, regression line overlaid.
    Saves: figures/scatter_metrics_vs_error.png
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    methods = metrics_df['method'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(methods)))
    color_map = dict(zip(methods, colors))

    for ax, metric in zip(axes, ['rho_r', 'rho_m']):
        for method in methods:
            df_method = metrics_df[metrics_df['method'] == method]
            ax.scatter(df_method['error_norm'], df_method[metric],
                      c=[color_map[method]], label=method, alpha=0.7, s=50)

        # Overall regression line
        x = metrics_df['error_norm'].values
        y = metrics_df[metric].values
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_line, p(x_line), 'k--', alpha=0.5, linewidth=2, label='Regression')

        ax.set_xlabel('Error Norm ||phi_hat - phi||')
        ax.set_ylabel(f'{metric} ({"Rank Preservation" if metric == "rho_r" else "Magnitude Fidelity"})')
        ax.set_title(f'{metric} vs Approximation Error (Deep Network)')
        ax.legend()

    plt.tight_layout()
    save_path = os.path.join(cfg.figures_dir, 'scatter_metrics_vs_error.png')
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_correlation_heatmap(
    partial_corr_convex: Dict[int, float],
    partial_corr_deep: Dict[int, float],
    cfg: HM2Config,
) -> None:
    """
    Side-by-side heatmap corr(rho_r, rho_m) by budget: convex vs deep.
    Saves: figures/correlation_heatmap.png
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    budgets = sorted(cfg.compute_budgets)

    for ax, (title, corr_dict) in zip(axes, [('Convex (H-M1)', partial_corr_convex),
                                              ('Deep (H-M2)', partial_corr_deep)]):
        corr_values = [corr_dict.get(b, 0) for b in budgets]
        data = np.array(corr_values).reshape(1, -1)

        sns.heatmap(data, ax=ax, annot=True, fmt='.3f', cmap='RdYlGn',
                   xticklabels=budgets, yticklabels=['corr(rho_r, rho_m)'],
                   vmin=0, vmax=1, cbar_kws={'label': 'Correlation'})
        ax.set_xlabel('Compute Budget')
        ax.set_title(title)

    plt.tight_layout()
    save_path = os.path.join(cfg.figures_dir, 'correlation_heatmap.png')
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_r2_by_method(
    metrics_df: pd.DataFrame,
    r2_by_method: Dict[str, Dict[str, float]],
    cfg: HM2Config,
) -> None:
    """
    Bar chart of R^2 per method. Saves: figures/r2_by_method.png
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    methods = list(r2_by_method.keys())
    x = np.arange(len(methods))
    width = 0.35

    r2_rho_r = [r2_by_method[m]['r2_rho_r'] for m in methods]
    r2_rho_m = [r2_by_method[m]['r2_rho_m'] for m in methods]

    bars1 = ax.bar(x - width/2, r2_rho_r, width, label=r'$R^2$ ($\rho_r$)', color='steelblue', alpha=0.8)
    bars2 = ax.bar(x + width/2, r2_rho_m, width, label=r'$R^2$ ($\rho_m$)', color='coral', alpha=0.8)

    ax.axhline(y=cfg.r2_threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({cfg.r2_threshold})')

    ax.set_ylabel('R^2')
    ax.set_xlabel('Attribution Method')
    ax.set_title('R^2 by Method (Deep Network)')
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.legend()
    ax.set_ylim(0, 1.1)

    plt.tight_layout()
    save_path = os.path.join(cfg.figures_dir, 'r2_by_method.png')
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_r2_vs_budget(
    r2_convex_by_budget: Dict[int, Dict[str, float]],
    r2_deep_by_budget: Dict[int, Dict[str, float]],
    cfg: HM2Config,
) -> None:
    """
    Line plot of R^2 across budget levels, convex vs deep.
    Saves: figures/r2_vs_budget.png
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    budgets = sorted(cfg.compute_budgets)

    for ax, metric in zip(axes, ['r2_rho_r', 'r2_rho_m']):
        convex_vals = [r2_convex_by_budget.get(b, {}).get(metric, np.nan) for b in budgets]
        deep_vals = [r2_deep_by_budget.get(b, {}).get(metric, np.nan) for b in budgets]

        ax.plot(budgets, convex_vals, 'o-', label='Convex (H-M1)', color='steelblue', linewidth=2, markersize=8)
        ax.plot(budgets, deep_vals, 's-', label='Deep (H-M2)', color='coral', linewidth=2, markersize=8)
        ax.axhline(y=cfg.r2_threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({cfg.r2_threshold})')

        metric_name = 'Rank Preservation' if metric == 'r2_rho_r' else 'Magnitude Fidelity'
        ax.set_xlabel('Compute Budget')
        ax.set_ylabel(f'R^2 ({metric_name})')
        ax.set_title(f'R^2 vs Budget: {metric_name}')
        ax.legend()
        ax.set_ylim(0, 1.1)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    save_path = os.path.join(cfg.figures_dir, 'r2_vs_budget.png')
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_delta_r2(
    gate_results: Dict[str, Any],
    cfg: HM2Config,
) -> None:
    """
    Bar chart showing delta R^2 (convex - deep).
    Saves: figures/delta_r2.png
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    metrics = ['rho_r', 'rho_m']
    deltas = [gate_results['delta_r2_rho_r'], gate_results['delta_r2_rho_m']]

    colors = ['green' if d > cfg.delta_r2_threshold else 'red' for d in deltas]
    bars = ax.bar(metrics, deltas, color=colors, alpha=0.8)

    ax.axhline(y=cfg.delta_r2_threshold, color='orange', linestyle='--', linewidth=2,
               label=f'Threshold ({cfg.delta_r2_threshold})')

    ax.set_ylabel(r'$\Delta R^2$ (Convex - Deep)')
    ax.set_xlabel('Metric')
    ax.set_title('Metric Decoupling: R^2 Drop from Convex to Deep')
    ax.set_xticklabels([r'$\rho_r$', r'$\rho_m$'])
    ax.legend()

    # Add value labels
    for bar, val in zip(bars, deltas):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{val:.3f}', ha='center', va='bottom', fontsize=12)

    plt.tight_layout()
    save_path = os.path.join(cfg.figures_dir, 'delta_r2.png')
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def generate_all_figures(
    metrics_df: pd.DataFrame,
    r2_deep: Dict[str, float],
    partial_corr_deep: Dict[int, float],
    hm1_baseline: Dict[str, Any],
    gate_results: Dict[str, Any],
    r2_by_method: Dict[str, Dict[str, float]],
    r2_deep_by_budget: Dict[int, Dict[str, float]],
    cfg: HM2Config,
) -> None:
    """Generate all figures. Convenience entry point from run_experiment."""
    os.makedirs(cfg.figures_dir, exist_ok=True)

    print("\nGenerating figures...")

    # Mandatory gate figure
    plot_gate_r2_comparison(
        r2_convex={'r2_rho_r': hm1_baseline['r2_rho_r'], 'r2_rho_m': hm1_baseline['r2_rho_m']},
        r2_deep=r2_deep,
        cfg=cfg,
    )

    # Supplementary figures
    plot_scatter_metrics_vs_error(metrics_df, cfg)

    plot_correlation_heatmap(
        partial_corr_convex=hm1_baseline['partial_corr_by_budget'],
        partial_corr_deep=partial_corr_deep,
        cfg=cfg,
    )

    plot_r2_by_method(metrics_df, r2_by_method, cfg)

    # R^2 by budget (use convex baseline values per budget)
    r2_convex_by_budget = {
        b: {'r2_rho_r': hm1_baseline['r2_rho_r'], 'r2_rho_m': hm1_baseline['r2_rho_m']}
        for b in cfg.compute_budgets
    }
    plot_r2_vs_budget(r2_convex_by_budget, r2_deep_by_budget, cfg)

    plot_delta_r2(gate_results, cfg)

    print(f"All figures saved to {cfg.figures_dir}")
