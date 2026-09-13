"""Visualization generators for gate metrics and autonomous figures."""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from typing import Dict, List


def plot_gate_metrics(r_squared: float, threshold: float, output_path: str):
    """Bar chart: actual vs target R². MANDATORY."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(['Target', 'Actual'], [threshold, r_squared], color=['gray', 'blue'])
    ax.axhline(y=threshold, color='red', linestyle='--', label='Gate Threshold')
    ax.set_ylabel('R²')
    ax.set_title('Gate Metrics: R² vs Target')
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_correlation_heatmap(corr_matrix: pd.DataFrame, output_path: str):
    """Heatmap: features × errors."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax)
    ax.set_title('Correlation Matrix: Features × Errors')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_feature_importance(importance: Dict[str, float], output_path: str):
    """Bar chart: ranked coefficients."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    sorted_feats = sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True)
    names, values = zip(*sorted_feats)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(names, values)
    ax.set_xlabel('Regression Coefficient')
    ax.set_title('Feature Importance (Ranked)')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_cv_results(cv_scores: List[float], output_path: str):
    """Box plot: R² distribution."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.boxplot(cv_scores, vert=True)
    ax.set_ylabel('R²')
    ax.set_title('Cross-Validation R² Distribution')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
