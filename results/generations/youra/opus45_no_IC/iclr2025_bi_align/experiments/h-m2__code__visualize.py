"""Visualization for H-M2 formality correlation experiment."""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from config import FIGURES_DIR, GATE_R_THRESHOLD


def plot_scatter_regression(human_scores: list, ai_scores: list, r: float, save_path: str = None) -> None:
    """Scatter plot with regression line."""
    if save_path is None:
        save_path = os.path.join(FIGURES_DIR, "scatter_regression.png")

    plt.figure(figsize=(10, 8))

    human_arr = np.array(human_scores)
    ai_arr = np.array(ai_scores)

    plt.scatter(human_arr, ai_arr, alpha=0.3, s=5, c='steelblue')

    slope, intercept, _, _, _ = stats.linregress(human_arr, ai_arr)
    x_line = np.array([human_arr.min(), human_arr.max()])
    y_line = slope * x_line + intercept
    plt.plot(x_line, y_line, 'r-', linewidth=2, label=f'r = {r:.4f}')

    plt.xlabel('Human Formality Score', fontsize=12)
    plt.ylabel('AI Formality Score', fontsize=12)
    plt.title('Human vs AI Formality (H-M2)', fontsize=14)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_correlation_bar(observed_r: float, threshold: float = GATE_R_THRESHOLD, save_path: str = None) -> None:
    """Bar chart comparing observed r to threshold."""
    if save_path is None:
        save_path = os.path.join(FIGURES_DIR, "correlation_bar.png")

    plt.figure(figsize=(8, 6))

    bars = plt.bar(['Observed |r|', 'Threshold'], [abs(observed_r), threshold],
                   color=['steelblue', 'coral'])

    for bar, val in zip(bars, [abs(observed_r), threshold]):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                 f'{val:.4f}', ha='center', fontsize=12)

    verdict = 'PASS' if abs(observed_r) > threshold else 'FAIL'
    plt.title(f'H-M2 Gate: {verdict}', fontsize=14)
    plt.ylabel('Correlation Coefficient', fontsize=12)
    plt.ylim(0, max(abs(observed_r), threshold) * 1.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_hexbin(human_scores: list, ai_scores: list, save_path: str = None) -> None:
    """Hexbin density plot for large n."""
    if save_path is None:
        save_path = os.path.join(FIGURES_DIR, "hexbin_density.png")

    plt.figure(figsize=(10, 8))
    plt.hexbin(human_scores, ai_scores, gridsize=50, cmap='Blues', mincnt=1)
    plt.colorbar(label='Count')
    plt.xlabel('Human Formality Score', fontsize=12)
    plt.ylabel('AI Formality Score', fontsize=12)
    plt.title('Human vs AI Formality Density', fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_qq(human_scores: list, ai_scores: list, save_path: str = None) -> None:
    """QQ plot for normality check of residuals."""
    if save_path is None:
        save_path = os.path.join(FIGURES_DIR, "qq_plot.png")

    human_arr = np.array(human_scores)
    ai_arr = np.array(ai_scores)

    slope, intercept, _, _, _ = stats.linregress(human_arr, ai_arr)
    residuals = ai_arr - (slope * human_arr + intercept)

    plt.figure(figsize=(8, 8))
    stats.probplot(residuals, dist="norm", plot=plt)
    plt.title('Q-Q Plot of Residuals', fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_residuals(human_scores: list, ai_scores: list, save_path: str = None) -> None:
    """Residual distribution plot."""
    if save_path is None:
        save_path = os.path.join(FIGURES_DIR, "residual_plot.png")

    human_arr = np.array(human_scores)
    ai_arr = np.array(ai_scores)

    slope, intercept, _, _, _ = stats.linregress(human_arr, ai_arr)
    residuals = ai_arr - (slope * human_arr + intercept)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].scatter(human_arr, residuals, alpha=0.3, s=5, c='steelblue')
    axes[0].axhline(y=0, color='r', linestyle='--')
    axes[0].set_xlabel('Human Formality Score')
    axes[0].set_ylabel('Residual')
    axes[0].set_title('Residuals vs Human Formality')

    axes[1].hist(residuals, bins=50, edgecolor='white', color='steelblue')
    axes[1].set_xlabel('Residual')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title('Residual Distribution')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def generate_all_figures(human_scores: list, ai_scores: list, r: float) -> None:
    """Generate all visualization figures."""
    plot_scatter_regression(human_scores, ai_scores, r)
    plot_correlation_bar(r)
    plot_hexbin(human_scores, ai_scores)
    plot_qq(human_scores, ai_scores)
    plot_residuals(human_scores, ai_scores)
