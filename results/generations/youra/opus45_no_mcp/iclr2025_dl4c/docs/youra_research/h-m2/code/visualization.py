"""Visualization for H-M2 results."""
import os
from typing import Dict, List
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot_accuracy_bar(category_accuracy: Dict, path: str) -> None:
    """Bar chart of U_line vs U_ignore accuracy with CI error bars."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)

    categories = ['U_line', 'U_ignore']
    accuracies = [category_accuracy[c]['accuracy'] * 100 for c in categories]
    ci_lows = [category_accuracy[c]['ci_low'] * 100 for c in categories]
    ci_highs = [category_accuracy[c]['ci_high'] * 100 for c in categories]

    yerr_low = [max(0, acc - ci) for acc, ci in zip(accuracies, ci_lows)]
    yerr_high = [max(0, ci - acc) for acc, ci in zip(accuracies, ci_highs)]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(categories, accuracies, color=['#2ecc71', '#e74c3c'],
                  yerr=[yerr_low, yerr_high], capsize=10)

    ax.set_ylabel('Localization Accuracy (%)')
    ax.set_title('H-M2: U_line vs U_ignore Localization Accuracy')
    ax.set_ylim(0, 100)

    for bar, acc, n in zip(bars, accuracies, [category_accuracy[c]['n'] for c in categories]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                f'{acc:.1f}%\n(n={n})', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_distance_distribution(distance_dist: Dict, path: str) -> None:
    """Histogram of traceback-to-actual distances per category."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    max_dist = max(
        max(distance_dist['U_line']) if distance_dist['U_line'] else 0,
        max(distance_dist['U_ignore']) if distance_dist['U_ignore'] else 0
    )
    bins = np.arange(0, min(max_dist + 2, 20), 1)

    if distance_dist['U_line']:
        ax.hist(distance_dist['U_line'], bins=bins, alpha=0.7,
                label=f"U_line (n={len(distance_dist['U_line'])})", color='#2ecc71')
    if distance_dist['U_ignore']:
        ax.hist(distance_dist['U_ignore'], bins=bins, alpha=0.7,
                label=f"U_ignore (n={len(distance_dist['U_ignore'])})", color='#e74c3c')

    ax.set_xlabel('Distance (|traceback_line - actual_line|)')
    ax.set_ylabel('Count')
    ax.set_title('H-M2: Traceback-to-Actual Line Distance Distribution')
    ax.legend()
    ax.axvline(x=2, color='black', linestyle='--', label='±2 tolerance')

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_exception_breakdown(breakdown: Dict, path: str) -> None:
    """Horizontal bar chart of accuracy per exception type."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)

    exc_types = list(breakdown.keys())[:10]
    accuracies = [breakdown[e]['accuracy'] * 100 for e in exc_types]
    counts = [breakdown[e]['n'] for e in exc_types]

    fig, ax = plt.subplots(figsize=(10, 6))

    from config import U_LINE_ERRORS
    colors = ['#2ecc71' if e in U_LINE_ERRORS else '#e74c3c' for e in exc_types]

    bars = ax.barh(exc_types, accuracies, color=colors)
    ax.set_xlabel('Localization Accuracy (%)')
    ax.set_title('H-M2: Accuracy by Exception Type')
    ax.set_xlim(0, 100)

    for bar, acc, n in zip(bars, accuracies, counts):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{acc:.0f}% (n={n})', va='center')

    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
