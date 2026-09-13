"""
PoC validation and visualization for h-e3.
"""

import matplotlib
matplotlib.use('Agg')  # Headless backend
import matplotlib.pyplot as plt
import numpy as np
import csv
import os


def check_poc_pass(results: dict) -> bool:
    """
    Validate PoC success criteria.

    Pass conditions:
    1. R_temporal(5) > R_temporal(50) (direction check)
    2. delta >= 0.1 (effect size)
    3. worst_group_acc >= 0.7 (sanity check)

    Returns:
        True if all conditions met
    """
    delta = results.get('delta')
    if delta is None or delta < 0.1:
        return False

    worst_acc = results.get('worst_group_acc', 0.0)
    if worst_acc < 0.7:
        return False

    return True


def compute_delta(R_history: dict) -> float | None:
    """Compute R_temporal(5) - R_temporal(50). Returns: delta or None if missing."""
    if 5 not in R_history or 50 not in R_history:
        return None
    return R_history[5] - R_history[50]


def plot_temporal_ratio(R_history: dict, output_path: str):
    """
    Plot R_temporal vs epoch (line chart).
    Saves to output_path as PNG.
    """
    epochs = sorted(R_history.keys())
    ratios = [R_history[e] for e in epochs]

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, ratios, marker='o', color='#3498DB', linewidth=2)
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('R_temporal', fontsize=12)
    plt.title('Temporal Ratio Evolution', fontsize=14)
    plt.grid(True, alpha=0.3)

    # Annotate start/end values
    plt.annotate(f'{ratios[0]:.3f}', xy=(epochs[0], ratios[0]), xytext=(5, 5),
                 textcoords='offset points', fontsize=10)
    plt.annotate(f'{ratios[-1]:.3f}', xy=(epochs[-1], ratios[-1]), xytext=(5, 5),
                 textcoords='offset points', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved R_temporal plot to {output_path}")


def save_results(results: dict, output_dir: str):
    """Export R_temporal history as CSV."""
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, 'temporal_ratios.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['epoch', 'R_temporal'])
        for epoch, R in sorted(results['R_temporal_history'].items()):
            writer.writerow([epoch, R])

    print(f"Saved temporal ratios to {csv_path}")
