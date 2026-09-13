"""Visualization module for H-M2."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict


def plot_distance_distribution_panel(
    ax: plt.Axes,
    distances: np.ndarray,
    mean_dist: float,
    p_value: float,
    condition: str
) -> None:
    """Plot histogram of pairwise distance distribution."""
    ax.hist(distances, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
    ax.axvline(mean_dist, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_dist:.2f}')
    ax.set_xlabel('Pairwise Distance')
    ax.set_ylabel('Frequency')
    ax.set_title(f'{condition}\np-value: {p_value:.2e}')
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_loss_trajectory_fan(
    ax: plt.Axes,
    loss_trajectories: np.ndarray,
    cv_final: float,
    condition: str
) -> None:
    """Plot all loss trajectories with semi-transparent lines."""
    n_seeds, n_epochs = loss_trajectories.shape
    epochs = np.arange(n_epochs)

    # Plot all trajectories
    for seed in range(n_seeds):
        ax.plot(epochs, loss_trajectories[seed], alpha=0.5, linewidth=1, color='steelblue')

    # Highlight mean trajectory
    mean_trajectory = np.mean(loss_trajectories, axis=0)
    ax.plot(epochs, mean_trajectory, color='red', linewidth=2, label='Mean')

    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.set_title(f'{condition}\nFinal CV: {cv_final:.2f}%')
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_gate_metrics_comparison(
    all_results: Dict[str, Dict],
    save_path: Path
) -> None:
    """
    Generate 2×4 grid figure.
    Top row: Final weight distance distributions
    Bottom row: Loss trajectory fans
    """
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    conditions = list(all_results.keys())  # Use actual condition names from results

    for i, condition in enumerate(conditions):
        result = all_results[condition]

        # Top row: Distance histograms
        plot_distance_distribution_panel(
            axes[0, i],
            result['distances'],
            result['mean_final_distance'],
            result['final_distance_p_value'],
            condition
        )

        # Bottom row: Trajectory fans
        plot_loss_trajectory_fan(
            axes[1, i],
            result['loss_trajectories'],
            result['cv_final_loss_percent'],
            condition
        )

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Figure saved: {save_path}")
