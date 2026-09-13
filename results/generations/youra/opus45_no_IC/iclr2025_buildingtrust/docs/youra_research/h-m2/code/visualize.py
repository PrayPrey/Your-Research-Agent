"""Visualization suite for H-M2 temperature scaling results."""

import numpy as np
import matplotlib.pyplot as plt
from config import CLUSTER_NAMES, FIGURES_DIR
import os


def plot_temperature_bar(optimal_temps, fold_temps, path=None):
    """Bar chart: mean T per cluster with std error bars (mandatory gate figure)."""
    if path is None:
        path = os.path.join(FIGURES_DIR, "temperature_bar.png")

    os.makedirs(os.path.dirname(path), exist_ok=True)

    clusters = sorted(optimal_temps.keys())
    means = [optimal_temps[c] for c in clusters]
    stds = [np.std(fold_temps.get(c, [optimal_temps[c]])) for c in clusters]
    labels = [CLUSTER_NAMES.get(c, f"Cluster {c}").split("/")[0] for c in clusters]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(range(len(clusters)), means, yerr=stds, capsize=5, alpha=0.8)
    ax.set_xticks(range(len(clusters)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Optimal Temperature")
    ax.set_title("Optimal Temperature per Cluster (with CV fold std)")
    ax.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='T=1.0 (baseline)')
    ax.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_temperature_boxplot(fold_temps, path=None):
    """Box plot: T distribution per cluster across 5 folds."""
    if path is None:
        path = os.path.join(FIGURES_DIR, "temperature_boxplot.png")

    os.makedirs(os.path.dirname(path), exist_ok=True)

    clusters = sorted(fold_temps.keys())
    data = [fold_temps[c] for c in clusters]
    labels = [CLUSTER_NAMES.get(c, f"Cluster {c}").split("/")[0] for c in clusters]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.boxplot(data, tick_labels=labels)
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Temperature")
    ax.set_title("Temperature Distribution Across CV Folds")
    plt.xticks(rotation=45, ha="right")
    ax.axhline(y=1.0, color='r', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_t_vs_cluster_line(optimal_temps, path=None):
    """Line plot: T across ordered clusters."""
    if path is None:
        path = os.path.join(FIGURES_DIR, "temperature_line.png")

    os.makedirs(os.path.dirname(path), exist_ok=True)

    clusters = sorted(optimal_temps.keys())
    temps = [optimal_temps[c] for c in clusters]
    labels = [CLUSTER_NAMES.get(c, f"C{c}").split("/")[0][:10] for c in clusters]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(len(clusters)), temps, marker='o', linewidth=2, markersize=8)
    ax.set_xticks(range(len(clusters)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Optimal Temperature")
    ax.set_title("Optimal Temperature Across Clusters")
    ax.axhline(y=1.0, color='r', linestyle='--', alpha=0.5)
    ax.axhline(y=np.mean(temps), color='g', linestyle=':', alpha=0.7, label=f'Mean T={np.mean(temps):.3f}')
    ax.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_cv_bootstrap_hist(bootstrap_cvs, path=None):
    """Histogram of CV across bootstrap resamples."""
    if path is None:
        path = os.path.join(FIGURES_DIR, "cv_bootstrap_hist.png")

    os.makedirs(os.path.dirname(path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(bootstrap_cvs, bins=50, alpha=0.7, edgecolor='black')
    ax.axvline(x=0.1, color='r', linestyle='--', label='Gate threshold (CV=0.1)')
    ax.axvline(x=np.mean(bootstrap_cvs), color='g', linestyle='-', label=f'Mean={np.mean(bootstrap_cvs):.3f}')
    ax.set_xlabel("Coefficient of Variation")
    ax.set_ylabel("Frequency")
    ax.set_title("Bootstrap Distribution of CV(T)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path
