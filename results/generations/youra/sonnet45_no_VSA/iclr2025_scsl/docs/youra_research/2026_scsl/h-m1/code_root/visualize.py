"""Visualization functions for dose-response analysis"""
from pathlib import Path
from typing import Dict, List
import sys
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sys.path.insert(0, str(Path(__file__).parent))
from config import VisualizationConfig


def plot_dose_response_curve(
    results: Dict[float, List[float]],
    output_path: Path,
    config: VisualizationConfig
) -> None:
    """Plot dose-response curve with error bars.

    Args:
        results: {flip_prob: [acc_seed1, ...], ...}
        output_path: Output file path
        config: Visualization config
    """
    flip_probs = sorted(results.keys())
    mean_accs = [np.mean(results[p]) for p in flip_probs]
    std_accs = [np.std(results[p]) for p in flip_probs]

    plt.figure(figsize=config.figure_size_single)
    plt.errorbar(
        flip_probs, mean_accs, yerr=std_accs,
        marker=config.marker_style,
        markersize=config.marker_size,
        linewidth=config.line_width,
        capsize=config.error_capsize,
        color=config.line_color,
        ecolor=config.error_color
    )
    plt.xlabel("Flip Probability", fontsize=config.label_size)
    plt.ylabel("Asymmetric Digit Accuracy", fontsize=config.label_size)
    plt.title("Dose-Response Relationship", fontsize=config.title_size)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=config.figure_dpi, format=config.figure_format)
    plt.close()


def plot_per_digit_heatmap(
    per_digit_results: Dict[float, Dict[int, float]],
    output_path: Path,
    config: VisualizationConfig
) -> None:
    """Plot per-digit accuracy heatmap.

    Args:
        per_digit_results: {flip_prob: {digit: accuracy, ...}, ...}
        output_path: Output file path
        config: Visualization config
    """
    flip_probs = sorted(per_digit_results.keys())
    digits = list(range(10))

    # Build matrix [digits x flip_probs]
    matrix = np.zeros((len(digits), len(flip_probs)))
    for j, p in enumerate(flip_probs):
        for i, d in enumerate(digits):
            matrix[i, j] = per_digit_results[p][d]

    plt.figure(figsize=config.figure_size_single)
    sns.heatmap(
        matrix,
        annot=config.heatmap_annot,
        fmt=config.heatmap_fmt,
        cmap=config.heatmap_cmap,
        xticklabels=[f"p={p:.1f}" for p in flip_probs],
        yticklabels=digits,
        cbar_kws={"label": config.heatmap_cbar_label}
    )
    plt.xlabel("Flip Probability", fontsize=config.label_size)
    plt.ylabel("Digit", fontsize=config.label_size)
    plt.title("Per-Digit Accuracy Heatmap", fontsize=config.title_size)
    plt.tight_layout()
    plt.savefig(output_path, dpi=config.figure_dpi, format=config.figure_format)
    plt.close()


def plot_degradation_bars(
    results: Dict[float, List[float]],
    output_path: Path,
    config: VisualizationConfig
) -> None:
    """Plot degradation magnitude bar chart.

    Args:
        results: {flip_prob: [acc_seed1, ...], ...}
        output_path: Output file path
        config: Visualization config
    """
    baseline_acc = np.mean(results[0.0])
    flip_probs = sorted([p for p in results.keys() if p > 0])
    degradations = [baseline_acc - np.mean(results[p]) for p in flip_probs]
    std_errors = [np.std(results[p]) / np.sqrt(len(results[p])) for p in flip_probs]

    plt.figure(figsize=config.figure_size_single)
    bars = plt.bar(
        [f"p={p:.1f}" for p in flip_probs],
        degradations,
        yerr=std_errors,
        capsize=config.error_capsize,
        color=config.bar_colors[:len(flip_probs)]
    )
    plt.ylabel("Accuracy Degradation", fontsize=config.label_size)
    plt.xlabel("Flip Probability", fontsize=config.label_size)
    plt.title("Degradation vs Baseline", fontsize=config.title_size)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=config.figure_dpi, format=config.figure_format)
    plt.close()


def plot_gate_metrics(
    target_rho: float,
    target_p: float,
    actual_rho: float,
    actual_p: float,
    gate_status: str,
    output_path: Path,
    config: VisualizationConfig
) -> None:
    """Plot gate metrics comparison.

    Args:
        target_rho: Target Spearman rho (< 0)
        target_p: Target p-value (< 0.05)
        actual_rho: Actual Spearman rho
        actual_p: Actual p-value
        gate_status: "PASS" or "FAIL"
        output_path: Output file path
        config: Visualization config
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=config.figure_size_wide)

    # Rho comparison
    color_rho = config.gate_pass_color if actual_rho < 0 else config.gate_fail_color
    ax1.bar(["Target", "Actual"], [target_rho, actual_rho], color=[color_rho, color_rho])
    ax1.axhline(y=0, color='black', linestyle='--', linewidth=1)
    ax1.set_ylabel("Spearman ρ", fontsize=config.label_size)
    ax1.set_title("Correlation Test", fontsize=config.title_size)
    ax1.grid(True, alpha=0.3, axis='y')

    # P-value comparison
    color_p = config.gate_pass_color if actual_p < target_p else config.gate_fail_color
    ax2.bar(["Target", "Actual"], [target_p, actual_p], color=[color_p, color_p])
    ax2.axhline(y=0.05, color='red', linestyle='--', linewidth=1, label='α=0.05')
    ax2.set_ylabel("p-value", fontsize=config.label_size)
    ax2.set_title("Significance Test", fontsize=config.title_size)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    # Overall title
    status_color = config.gate_pass_color if gate_status == "PASS" else config.gate_fail_color
    fig.suptitle(f"Gate Status: {gate_status}", fontsize=config.title_size + 2,
                 color=status_color, weight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=config.figure_dpi, format=config.figure_format)
    plt.close()
