"""Visualization module for H-E1 experiment."""
import matplotlib.pyplot as plt
import numpy as np
import os
import config

def plot_gate_bar_chart(correlation: float, threshold: float, out_path: str):
    """Bar chart of abs(correlation) vs threshold."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(['Correlation'], [abs(correlation)], color='steelblue', label=f'|r| = {abs(correlation):.3f}')
    ax.axhline(y=threshold, color='red', linestyle='--', label=f'Threshold = {threshold}')
    ax.set_ylabel('Absolute Correlation')
    ax.set_title('Gate Check: Orthogonality Test')
    ax.legend()
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_score_histogram(chosen: list, rejected: list, out_path: str):
    """Overlapping histograms of chosen vs rejected scores."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(chosen, bins=30, alpha=0.6, label='Chosen', color='green')
    ax.hist(rejected, bins=30, alpha=0.6, label='Rejected', color='red')
    ax.set_xlabel('Collaboration Score')
    ax.set_ylabel('Frequency')
    ax.set_title('Score Distribution: Chosen vs Rejected')
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_scatter_regression(scores: list, labels: list, out_path: str):
    """Scatter plot with regression line."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    jitter = np.random.normal(0, 0.03, len(labels))
    ax.scatter(np.array(labels) + jitter, scores, alpha=0.3, s=10)
    z = np.polyfit(labels, scores, 1)
    p = np.poly1d(z)
    ax.plot([0, 1], [p(0), p(1)], 'r--', linewidth=2, label=f'y = {z[0]:.3f}x + {z[1]:.3f}')
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Rejected', 'Chosen'])
    ax.set_xlabel('Preference Label')
    ax.set_ylabel('Collaboration Score')
    ax.set_title('Score vs Preference Label')
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_boxplot(chosen: list, rejected: list, out_path: str):
    """Side-by-side boxplot."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.boxplot([rejected, chosen], labels=['Rejected', 'Chosen'])
    ax.set_ylabel('Collaboration Score')
    ax.set_title('Score Distribution Comparison')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
