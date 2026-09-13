"""Visualization module for h-m3 experiment results"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict

def plot_correlation_comparison(
    metrics: Dict[str, float],
    baseline_corr: float,
    output_path: Path
):
    """
    Bar chart comparing baseline vs supervised correlations

    Args:
        metrics: Current experiment metrics
        baseline_corr: h-e1 baseline correlation
        output_path: Where to save figure
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    models = ['Baseline\n(h-e1)', 'Supervised\n(h-m3)']
    corrs = [baseline_corr, metrics['spearman_rho']]
    colors = ['#E57373', '#81C784']  # Red for baseline, green for supervised

    bars = ax.bar(models, corrs, color=colors, alpha=0.8, edgecolor='black')

    # Add threshold line
    ax.axhline(y=0.7, color='red', linestyle='--', linewidth=2, label='Gate threshold (0.7)')

    # Add value labels on bars
    for bar, corr in zip(bars, corrs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{corr:.3f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel('Spearman Correlation (ρ)', fontsize=12)
    ax.set_title('AI-Human Correlation: Baseline vs Supervised', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1.0)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def plot_scatter(
    human_scores: np.ndarray,
    ai_predictions: np.ndarray,
    metrics: Dict[str, float],
    output_path: Path
):
    """
    Scatter plot of human scores vs AI predictions

    Args:
        human_scores: Ground truth scores (0-10)
        ai_predictions: Model predictions (0-10)
        metrics: Correlation metrics
        output_path: Where to save figure
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    ax.scatter(human_scores, ai_predictions, alpha=0.5, s=30, edgecolor='black', linewidth=0.5)

    # Add diagonal reference line
    ax.plot([0, 10], [0, 10], 'r--', linewidth=2, label='Perfect agreement')

    # Add correlation text
    rho = metrics['spearman_rho']
    p = metrics['spearman_p']
    ax.text(0.05, 0.95, f"Spearman ρ = {rho:.3f}\np = {p:.4f}",
            transform=ax.transAxes, fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    ax.set_xlabel('Human Scores (Ground Truth)', fontsize=12)
    ax.set_ylabel('AI Predictions (Supervised Model)', fontsize=12)
    ax.set_title('Human vs AI Scatter Plot', fontsize=14, fontweight='bold')
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 10.5)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def plot_learning_curve(
    trainer_log_history,
    output_path: Path
):
    """
    Learning curve showing validation correlation vs epoch

    Args:
        trainer_log_history: HuggingFace Trainer log history
        output_path: Where to save figure
    """
    # Extract validation losses (proxy for correlation improvement)
    epochs = []
    val_losses = []

    for entry in trainer_log_history:
        if 'eval_loss' in entry:
            epochs.append(entry.get('epoch', len(epochs)))
            val_losses.append(entry['eval_loss'])

    if not epochs:
        print("  No validation data available for learning curve")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(epochs, val_losses, marker='o', linewidth=2, markersize=8, label='Validation Loss')

    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Validation Loss (MSE)', fontsize=12)
    ax.set_title('Training Progress: Validation Loss vs Epoch', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def plot_error_distribution(
    human_scores: np.ndarray,
    ai_predictions: np.ndarray,
    output_path: Path
):
    """
    Histogram of prediction errors (residuals)

    Args:
        human_scores: Ground truth scores
        ai_predictions: Model predictions
        output_path: Where to save figure
    """
    errors = np.abs(human_scores - ai_predictions)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(errors, bins=30, alpha=0.7, color='skyblue', edgecolor='black')

    # Add mean error line
    mean_error = np.mean(errors)
    ax.axvline(mean_error, color='red', linestyle='--', linewidth=2,
               label=f'Mean Error: {mean_error:.3f}')

    ax.set_xlabel('Absolute Error |Human - AI|', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Prediction Error Distribution', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def generate_all_figures(
    human_scores: np.ndarray,
    ai_predictions: np.ndarray,
    metrics: Dict[str, float],
    baseline_corr: float,
    trainer_log_history,
    figures_dir: Path
):
    """Generate all required figures for h-m3"""

    figures_dir.mkdir(exist_ok=True, parents=True)

    print("Generating figures...")

    # Figure 1: Correlation comparison bar chart
    plot_correlation_comparison(
        metrics, baseline_corr,
        figures_dir / "correlation_comparison.png"
    )

    # Figure 2: Scatter plot
    plot_scatter(
        human_scores, ai_predictions, metrics,
        figures_dir / "scatter_human_vs_ai.png"
    )

    # Figure 3: Learning curve
    plot_learning_curve(
        trainer_log_history,
        figures_dir / "learning_curve.png"
    )

    # Figure 4: Error distribution
    plot_error_distribution(
        human_scores, ai_predictions,
        figures_dir / "error_distribution.png"
    )

    print(f"✓ All figures saved to {figures_dir}")

if __name__ == "__main__":
    # Test with dummy data
    human = np.array([7.0, 5.0, 8.0, 6.0, 9.0] * 40)
    ai = human + np.random.normal(0, 0.5, len(human))

    from evaluation import calculate_correlations
    metrics = calculate_correlations(human, ai)

    test_dir = Path("./test_figures")
    generate_all_figures(human, ai, metrics, 0.485, [], test_dir)
    print("\n✓ Visualization module validated")
