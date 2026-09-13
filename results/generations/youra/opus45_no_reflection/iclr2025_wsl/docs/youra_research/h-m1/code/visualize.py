import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
from config import FIGURES_DIR


def plot_gate_metric(baseline_r2: float, proposed_r2: float, out_path: str = None) -> str:
    """Bar chart comparing proposed vs baseline mean R²."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "gate_comparison.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    x = [0, 1]
    heights = [baseline_r2, proposed_r2]
    colors = ['#1f77b4', '#2ca02c' if proposed_r2 > baseline_r2 else '#d62728']
    bars = ax.bar(x, heights, color=colors, width=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(['Baseline\n(Stratified)', 'Proposed\n(Weight Features)'])
    ax.set_ylabel('Mean R²')
    ax.set_title('H-M1 Gate: Weight Features vs Stratified Baseline')
    ax.set_ylim(0, 1)

    for bar, h in zip(bars, heights):
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.02, f'{h:.4f}', ha='center', va='bottom')

    gate_result = "PASS" if proposed_r2 > baseline_r2 else "FAIL"
    ax.text(0.5, 0.95, f'Gate: {gate_result}', transform=ax.transAxes, ha='center',
            fontsize=12, fontweight='bold',
            color='green' if gate_result == "PASS" else 'red')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def plot_per_class_r2_comparison(baseline_per_class: list, proposed_per_class: list, out_path: str = None) -> str:
    """Bar chart comparing per-class R² for baseline vs proposed."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "per_class_r2.png")

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(10)
    width = 0.35

    ax.bar(x - width/2, baseline_per_class, width, label='Baseline', color='#1f77b4')
    ax.bar(x + width/2, proposed_per_class, width, label='Proposed', color='#2ca02c')

    ax.set_xlabel('Class')
    ax.set_ylabel('R²')
    ax.set_title('Per-Class R² Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels([f'Class {i}' for i in range(10)], rotation=45, ha='right')
    ax.legend()
    ax.set_ylim(min(0, min(min(baseline_per_class), min(proposed_per_class)) - 0.1), 1)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def plot_predicted_vs_actual(y_true: np.ndarray, y_pred: np.ndarray, class_idx: int = 0, out_path: str = None) -> str:
    """Scatter plot of predicted vs actual for a specific class."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, f"pred_vs_actual_class{class_idx}.png")

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_true[:, class_idx], y_pred[:, class_idx], alpha=0.5, s=10)

    lims = [min(y_true[:, class_idx].min(), y_pred[:, class_idx].min()),
            max(y_true[:, class_idx].max(), y_pred[:, class_idx].max())]
    ax.plot(lims, lims, 'r--', alpha=0.75, label='Perfect prediction')

    ax.set_xlabel('Actual Accuracy')
    ax.set_ylabel('Predicted Accuracy')
    ax.set_title(f'Class {class_idx}: Predicted vs Actual')
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path
