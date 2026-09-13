"""Visualization for correlation results."""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, Tuple

def plot_correlation_matrix(
    correlations: Dict[str, Tuple[float, float]],
    dataset_name: str,
    output_dir: Path
):
    """Plot 3x3 correlation heatmap."""
    labels = ["Execution", "AI", "Human"]
    matrix = np.zeros((3, 3))

    # Extract correlations
    exec_human_r, _ = correlations["exec_human"]
    ai_human_r, _ = correlations["ai_human"]
    exec_ai_r, _ = correlations["exec_ai"]

    # Fill matrix (symmetric)
    matrix[0, 2] = matrix[2, 0] = exec_human_r
    matrix[1, 2] = matrix[2, 1] = ai_human_r
    matrix[0, 1] = matrix[1, 0] = exec_ai_r
    matrix[0, 0] = matrix[1, 1] = matrix[2, 2] = 1.0

    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, fmt=".3f", cmap="coolwarm",
                xticklabels=labels, yticklabels=labels, vmin=-1, vmax=1)
    plt.title(f"Correlation Matrix: {dataset_name}")
    plt.tight_layout()
    plt.savefig(output_dir / f"correlation_matrix_{dataset_name}.png", dpi=150)
    plt.close()

def plot_scatter(
    x: np.ndarray,
    y: np.ndarray,
    labels: Tuple[str, str],
    output_path: Path
):
    """Scatter plot with regression line."""
    plt.figure(figsize=(6, 5))
    plt.scatter(x, y, alpha=0.5)

    # Add regression line
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    plt.plot(x, p(x), "r--", alpha=0.8)

    plt.xlabel(labels[0])
    plt.ylabel(labels[1])
    plt.title(f"{labels[0]} vs {labels[1]}")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def plot_distributions(
    exec: np.ndarray,
    ai: np.ndarray,
    human: np.ndarray,
    output_dir: Path,
    dataset_name: str
):
    """Plot distributions of feedback values."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    axes[0].hist(exec, bins=2, alpha=0.7, edgecolor='black')
    axes[0].set_title("Execution Feedback")
    axes[0].set_xlabel("Result (0=fail, 1=pass)")

    axes[1].hist(ai, bins=20, alpha=0.7, edgecolor='black')
    axes[1].set_title("AI Feedback")
    axes[1].set_xlabel("Score")

    axes[2].hist(human, bins=20, alpha=0.7, edgecolor='black')
    axes[2].set_title("Human Feedback")
    axes[2].set_xlabel("Rating")

    plt.tight_layout()
    plt.savefig(output_dir / f"distributions_{dataset_name}.png", dpi=150)
    plt.close()
