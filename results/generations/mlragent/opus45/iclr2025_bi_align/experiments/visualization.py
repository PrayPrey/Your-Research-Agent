"""
Visualization utilities for the Mutual Calibration Framework experiments.
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import os


def set_style():
    """Set consistent plot style."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['legend.fontsize'] = 10


def plot_training_curves(
    histories: Dict[str, Dict],
    save_path: str,
    metric: str = "loss"
):
    """
    Plot training and validation curves for multiple models.

    Args:
        histories: Dict mapping model names to training history dicts
        save_path: Path to save the figure
        metric: Metric to plot ("loss" or "accuracy")
    """
    set_style()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    colors = plt.cm.tab10(np.linspace(0, 1, len(histories)))

    for idx, (model_name, history) in enumerate(histories.items()):
        color = colors[idx]

        # Training curve
        if f"train_{metric}" in history and len(history[f"train_{metric}"]) > 0:
            axes[0].plot(
                history[f"train_{metric}"],
                label=model_name,
                color=color,
                linewidth=2
            )

        # Validation curve
        if f"val_{metric}" in history and len(history[f"val_{metric}"]) > 0:
            axes[1].plot(
                history[f"val_{metric}"],
                label=model_name,
                color=color,
                linewidth=2
            )

    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel(f"Training {metric.capitalize()}")
    axes[0].set_title(f"Training {metric.capitalize()} Curves")
    axes[0].legend()

    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel(f"Validation {metric.capitalize()}")
    axes[1].set_title(f"Validation {metric.capitalize()} Curves")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_model_comparison(
    results: Dict,
    metrics: List[str],
    save_path: str,
    title: str = "Model Comparison"
):
    """
    Bar chart comparing models across multiple metrics.

    Args:
        results: Dict mapping model names to metric dicts
        metrics: List of metric names to compare
        save_path: Path to save figure
        title: Plot title
    """
    set_style()

    model_names = list(results.keys())
    n_models = len(model_names)
    n_metrics = len(metrics)

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(n_metrics)
    width = 0.8 / n_models
    colors = plt.cm.Set2(np.linspace(0, 1, n_models))

    for idx, model_name in enumerate(model_names):
        values = []
        errors = []
        for metric in metrics:
            if metric in results[model_name]:
                data = results[model_name][metric]
                if isinstance(data, dict):
                    values.append(data.get("mean", 0))
                    errors.append(data.get("std", 0))
                else:
                    values.append(data)
                    errors.append(0)
            else:
                values.append(0)
                errors.append(0)

        offset = (idx - n_models / 2 + 0.5) * width
        bars = ax.bar(
            x + offset, values, width,
            label=model_name, color=colors[idx],
            yerr=errors, capsize=3
        )

    ax.set_xlabel("Metrics")
    ax.set_ylabel("Value")
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace("_", " ").title() for m in metrics], rotation=45, ha='right')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 1.1)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_reliance_analysis(
    results: Dict,
    save_path: str
):
    """
    Plot reliance metrics (ARR, over-reliance, under-reliance) comparison.
    """
    set_style()

    model_names = list(results.keys())
    metrics = ["rel_appropriate_reliance_rate", "rel_over_reliance_rate", "rel_under_reliance_rate", "rel_correct_override_rate"]
    metric_labels = ["ARR", "Over-reliance", "Under-reliance", "Correct Override"]

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(metrics))
    width = 0.8 / len(model_names)
    colors = plt.cm.Set1(np.linspace(0, 1, len(model_names)))

    for idx, model_name in enumerate(model_names):
        values = []
        for metric in metrics:
            if metric in results[model_name]:
                data = results[model_name][metric]
                if isinstance(data, dict):
                    values.append(data.get("mean", 0))
                else:
                    values.append(data)
            else:
                values.append(0)

        offset = (idx - len(model_names) / 2 + 0.5) * width
        ax.bar(x + offset, values, width, label=model_name, color=colors[idx])

    ax.set_xlabel("Reliance Metrics")
    ax.set_ylabel("Rate")
    ax.set_title("Reliance Pattern Analysis Across Models")
    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels)
    ax.legend(loc='upper right')
    ax.set_ylim(0, 1.0)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_expertise_comparison(
    results: Dict,
    metric: str,
    save_path: str,
    title: str = None
):
    """
    Plot comparison across expertise levels for all models.

    Args:
        results: Nested dict {model_name_level: metrics} where keys are like "Baseline_novice"
        metric: Metric to plot
        save_path: Path to save figure
    """
    set_style()

    expertise_levels = ["novice", "intermediate", "expert"]

    # Extract unique model names from keys like "Baseline_novice"
    all_keys = list(results.keys())
    model_names = list(set("_".join(k.split("_")[:-1]) for k in all_keys))
    model_names.sort()  # Ensure consistent ordering

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(expertise_levels))
    width = 0.8 / len(model_names)
    colors = plt.cm.tab10(np.linspace(0, 1, len(model_names)))

    for idx, model_name in enumerate(model_names):
        values = []
        errors = []
        for level in expertise_levels:
            key = f"{model_name}_{level}"
            if key in results and metric in results[key]:
                data = results[key][metric]
                if isinstance(data, dict):
                    values.append(data.get("mean", 0))
                    errors.append(data.get("std", 0))
                else:
                    values.append(data)
                    errors.append(0)
            else:
                values.append(0)
                errors.append(0)

        offset = (idx - len(model_names) / 2 + 0.5) * width
        ax.bar(x + offset, values, width, label=model_name, color=colors[idx],
               yerr=errors, capsize=3)

    ax.set_xlabel("Expertise Level")
    ax.set_ylabel(metric.replace("_", " ").title())
    if title:
        ax.set_title(title)
    else:
        ax.set_title(f"{metric.replace('_', ' ').title()} by Expertise Level")
    ax.set_xticks(x)
    ax.set_xticklabels([l.capitalize() for l in expertise_levels])
    ax.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_calibration_curve(
    confidences: np.ndarray,
    accuracies: np.ndarray,
    model_name: str,
    save_path: str,
    n_bins: int = 10
):
    """
    Plot reliability diagram (calibration curve).
    """
    set_style()

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_accs = []
    bin_confs = []

    for i in range(n_bins):
        in_bin = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i + 1])
        if in_bin.sum() > 0:
            bin_accs.append(accuracies[in_bin].mean())
            bin_confs.append(confidences[in_bin].mean())

    fig, ax = plt.subplots(figsize=(8, 8))

    # Perfect calibration line
    ax.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration')

    # Actual calibration
    if bin_confs:
        ax.plot(bin_confs, bin_accs, 'o-', label=model_name, linewidth=2, markersize=8)

    ax.set_xlabel("Mean Predicted Confidence")
    ax.set_ylabel("Fraction of Positives")
    ax.set_title(f"Reliability Diagram - {model_name}")
    ax.legend()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_deference_distribution(
    deference_scores: np.ndarray,
    ai_correct: np.ndarray,
    model_name: str,
    save_path: str
):
    """
    Plot distribution of deference scores, split by AI correctness.
    """
    set_style()

    fig, ax = plt.subplots(figsize=(10, 6))

    # Deference when AI is correct
    ax.hist(
        deference_scores[ai_correct == 1],
        bins=20, alpha=0.6, label='AI Correct',
        color='green', density=True
    )

    # Deference when AI is wrong
    ax.hist(
        deference_scores[ai_correct == 0],
        bins=20, alpha=0.6, label='AI Wrong',
        color='red', density=True
    )

    ax.axvline(x=0.5, color='black', linestyle='--', label='Threshold')

    ax.set_xlabel("Deference Score")
    ax.set_ylabel("Density")
    ax.set_title(f"Deference Score Distribution - {model_name}")
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_radar_chart(
    results: Dict,
    metrics: List[str],
    save_path: str,
    title: str = "Model Performance Radar"
):
    """
    Radar chart comparing models across multiple metrics.
    """
    set_style()

    model_names = list(results.keys())
    n_metrics = len(metrics)

    angles = np.linspace(0, 2 * np.pi, n_metrics, endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    colors = plt.cm.Set1(np.linspace(0, 1, len(model_names)))

    for idx, model_name in enumerate(model_names):
        values = []
        for metric in metrics:
            if metric in results[model_name]:
                data = results[model_name][metric]
                if isinstance(data, dict):
                    values.append(data.get("mean", 0))
                else:
                    values.append(data)
            else:
                values.append(0)
        values += values[:1]  # Complete the circle

        ax.plot(angles, values, 'o-', linewidth=2, label=model_name, color=colors[idx])
        ax.fill(angles, values, alpha=0.25, color=colors[idx])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([m.replace("_", "\n").replace("rel ", "").title() for m in metrics])
    ax.set_title(title, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def create_summary_table(
    results: Dict,
    metrics: List[str],
    save_path: str
):
    """
    Create a summary table as a figure.
    """
    set_style()

    model_names = list(results.keys())

    # Prepare data
    data = []
    for model_name in model_names:
        row = [model_name]
        for metric in metrics:
            if metric in results[model_name]:
                val = results[model_name][metric]
                if isinstance(val, dict):
                    mean = val.get("mean", 0)
                    std = val.get("std", 0)
                    row.append(f"{mean:.3f}±{std:.3f}")
                else:
                    row.append(f"{val:.3f}")
            else:
                row.append("-")
        data.append(row)

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis('off')

    columns = ["Model"] + [m.replace("_", " ").title() for m in metrics]
    table = ax.table(
        cellText=data,
        colLabels=columns,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)

    # Style the header
    for i in range(len(columns)):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(color='white', weight='bold')

    plt.title("Summary of Results", fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def generate_all_figures(
    training_histories: Dict,
    evaluation_results: Dict,
    figures_dir: str
):
    """
    Generate all figures for the experiment.
    """
    os.makedirs(figures_dir, exist_ok=True)

    # 1. Training curves
    if training_histories:
        plot_training_curves(
            training_histories,
            os.path.join(figures_dir, "training_loss_curves.png"),
            metric="loss"
        )
        plot_training_curves(
            training_histories,
            os.path.join(figures_dir, "training_accuracy_curves.png"),
            metric="accuracy"
        )

    # 2. Model comparison
    if evaluation_results:
        key_metrics = ["perf_collaborative_accuracy", "rel_appropriate_reliance_rate",
                      "rel_over_reliance_rate", "agency_unique_contribution_rate"]
        available_metrics = [m for m in key_metrics if any(m in evaluation_results.get(model, {}) for model in evaluation_results)]

        if available_metrics:
            plot_model_comparison(
                evaluation_results,
                available_metrics,
                os.path.join(figures_dir, "model_comparison.png"),
                title="Model Performance Comparison"
            )

        # Reliance analysis
        plot_reliance_analysis(
            evaluation_results,
            os.path.join(figures_dir, "reliance_analysis.png")
        )

        # Radar chart
        radar_metrics = ["perf_collaborative_accuracy", "rel_appropriate_reliance_rate",
                        "agency_override_accuracy", "agency_unique_contribution_rate"]
        available_radar = [m for m in radar_metrics if any(m in evaluation_results.get(model, {}) for model in evaluation_results)]
        if available_radar:
            plot_radar_chart(
                evaluation_results,
                available_radar,
                os.path.join(figures_dir, "radar_comparison.png")
            )

        # Summary table
        summary_metrics = ["perf_ai_accuracy", "perf_collaborative_accuracy",
                         "rel_appropriate_reliance_rate", "rel_over_reliance_rate"]
        available_summary = [m for m in summary_metrics if any(m in evaluation_results.get(model, {}) for model in evaluation_results)]
        if available_summary:
            create_summary_table(
                evaluation_results,
                available_summary,
                os.path.join(figures_dir, "summary_table.png")
            )

    print(f"Figures saved to {figures_dir}")
