"""Visualization functions for leaderboard analysis."""

from pathlib import Path
from typing import List, Tuple, Optional
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot_score_timeline(
    df: pd.DataFrame,
    first_decay_date: Optional[pd.Timestamp],
    output_path: Path
):
    """Score vs. Time Plot with detected decay point marked."""
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['score'], marker='o', markersize=3, alpha=0.7, label='Scores')

    if first_decay_date:
        plt.axvline(first_decay_date, color='r', linestyle='--', linewidth=2, label=f'Decay detected: {first_decay_date.date()}')

    plt.xlabel('Date')
    plt.ylabel('Score')
    plt.title('Leaderboard Score Timeline')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_velocity_timeline(
    velocities: List[Tuple[pd.Timestamp, float, float]],
    threshold: float,
    output_path: Path
):
    """Velocity Timeline with threshold line."""
    if not velocities:
        return

    dates, vels, pvals = zip(*velocities)

    plt.figure(figsize=(12, 6))
    plt.plot(dates, vels, marker='o', markersize=3, alpha=0.7, label='Monthly velocity')
    plt.axhline(threshold, color='r', linestyle='--', linewidth=2, label=f'Threshold: {threshold}/month')

    plt.xlabel('Date')
    plt.ylabel('Velocity (improvement/month)')
    plt.title('Improvement Velocity Timeline')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_pvalue_distribution(
    velocities: List[Tuple[pd.Timestamp, float, float]],
    output_path: Path
):
    """P-value distribution histogram."""
    if not velocities:
        return

    _, _, pvals = zip(*velocities)

    plt.figure(figsize=(10, 6))
    plt.hist(pvals, bins=20, alpha=0.7, edgecolor='black')
    plt.axvline(0.05, color='r', linestyle='--', linewidth=2, label='α = 0.05')
    plt.xlabel('P-value')
    plt.ylabel('Frequency')
    plt.title('P-value Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_metrics_comparison(
    detection_success: bool,
    stability_cv: float,
    significance_ratio: float,
    output_path: Path
):
    """Gate Metrics Comparison bar chart."""
    metrics = {
        'Detection Success': 1.0 if detection_success else 0.0,
        'Measurement Stability (1/CV)': 1.0 / stability_cv if stability_cv > 0 else 0.0,
        'Statistical Significance': significance_ratio
    }

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(metrics.keys(), metrics.values(), alpha=0.7, edgecolor='black')

    # Color code
    bars[0].set_color('green' if detection_success else 'red')
    bars[1].set_color('green' if stability_cv < 0.5 else 'orange')
    bars[2].set_color('green' if significance_ratio > 0.7 else 'orange')

    ax.set_ylabel('Score')
    ax.set_title('Gate Metrics Comparison')
    ax.set_ylim([0, 1.2])
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
