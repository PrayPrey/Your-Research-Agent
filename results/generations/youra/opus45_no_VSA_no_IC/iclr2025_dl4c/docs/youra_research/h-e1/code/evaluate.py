"""Visualization and evaluation metrics."""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from config import P_VALUE_THRESHOLD, OUTPUT_DIR


def ensure_output_dir():
    """Create output directory if needed."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/figures", exist_ok=True)


def plot_error_distribution(results: pd.DataFrame, path: str = None):
    """Stacked bar chart of error types per scale."""
    ensure_output_dir()
    path = path or f"{OUTPUT_DIR}/figures/error_distribution.png"

    pivot = pd.crosstab(results['scale'], results['error_type'], normalize='index')
    colors = {'TP': '#2ecc71', 'TN': '#3498db', 'FP': '#e74c3c', 'FN': '#f39c12'}

    fig, ax = plt.subplots(figsize=(10, 6))
    pivot.plot(kind='bar', stacked=True, ax=ax, color=[colors.get(c, '#95a5a6') for c in pivot.columns])
    ax.set_xlabel('Model Scale')
    ax.set_ylabel('Proportion')
    ax.set_title('Error Distribution by Model Scale')
    ax.legend(title='Error Type', bbox_to_anchor=(1.02, 1))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_gate_metric(p_value: float, path: str = None):
    """Visualize p-value vs threshold."""
    ensure_output_dir()
    path = path or f"{OUTPUT_DIR}/figures/gate_metric.png"

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ['#2ecc71' if p_value < P_VALUE_THRESHOLD else '#e74c3c']
    ax.bar(['Chi-square p-value'], [p_value], color=colors)
    ax.axhline(y=P_VALUE_THRESHOLD, color='red', linestyle='--', label=f'Threshold ({P_VALUE_THRESHOLD})')
    ax.set_ylabel('p-value')
    ax.set_title(f'Gate Metric: {"PASS" if p_value < P_VALUE_THRESHOLD else "FAIL"}')
    ax.legend()
    ax.set_ylim(0, max(p_value * 1.5, P_VALUE_THRESHOLD * 2))
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_contingency_heatmap(contingency: pd.DataFrame, path: str = None):
    """Heatmap of contingency table."""
    ensure_output_dir()
    path = path or f"{OUTPUT_DIR}/figures/contingency_heatmap.png"

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(contingency, annot=True, fmt='d', cmap='YlOrRd', ax=ax)
    ax.set_title('Contingency Table: Scale × Error Type')
    ax.set_xlabel('Error Type')
    ax.set_ylabel('Scale')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_fp_fn_comparison(metrics: pd.DataFrame, path: str = None):
    """Compare FPR and FNR across scales."""
    ensure_output_dir()
    path = path or f"{OUTPUT_DIR}/figures/fp_fn_comparison.png"

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(metrics))
    width = 0.35
    ax.bar([i - width/2 for i in x], metrics['FPR'], width, label='FPR', color='#e74c3c')
    ax.bar([i + width/2 for i in x], metrics['FNR'], width, label='FNR', color='#f39c12')
    ax.set_xlabel('Model Scale')
    ax.set_ylabel('Rate')
    ax.set_title('False Positive and False Negative Rates by Scale')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics['scale'])
    ax.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def generate_all_figures(results: pd.DataFrame, contingency: pd.DataFrame,
                         metrics: pd.DataFrame, p_value: float) -> dict:
    """Generate all visualization figures."""
    return {
        "error_distribution": plot_error_distribution(results),
        "gate_metric": plot_gate_metric(p_value),
        "contingency_heatmap": plot_contingency_heatmap(contingency),
        "fp_fn_comparison": plot_fp_fn_comparison(metrics),
    }
