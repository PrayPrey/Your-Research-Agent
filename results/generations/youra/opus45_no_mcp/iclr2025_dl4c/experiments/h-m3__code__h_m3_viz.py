"""Visualization suite for H-M3 gradient noise analysis."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict


def plot_concentration_boxplot(
    u_line: List[float],
    u_ignore: List[float],
    path: str
) -> None:
    """Box plot comparing GT concentration between error types."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    data = pd.DataFrame({
        'Error Type': ['U_line'] * len(u_line) + ['U_ignore'] * len(u_ignore),
        'GT Concentration': u_line + u_ignore
    })

    plt.figure(figsize=(8, 6))
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
    except:
        pass

    ax = sns.boxplot(x='Error Type', y='GT Concentration', data=data, palette=['#4CAF50', '#F44336'])
    ax.set_ylabel('Ground Truth Concentration Ratio')
    ax.set_title('Gradient Concentration at Ground Truth Location')

    u_line_mean = np.mean(u_line)
    u_ignore_mean = np.mean(u_ignore)
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Baseline (1.0)')

    plt.annotate(f'mean={u_line_mean:.2f}', xy=(0, u_line_mean), xytext=(0.2, u_line_mean),
                 fontsize=9, color='#4CAF50')
    plt.annotate(f'mean={u_ignore_mean:.2f}', xy=(1, u_ignore_mean), xytext=(1.2, u_ignore_mean),
                 fontsize=9, color='#F44336')

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_noise_ratio_histogram(
    u_ignore_noise: List[float],
    path: str
) -> None:
    """Histogram of noise ratio for U_ignore samples."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    plt.figure(figsize=(8, 6))
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
    except:
        pass

    arr = np.array(u_ignore_noise)
    arr = np.clip(arr, 0, np.percentile(arr, 99))

    plt.hist(arr, bins=50, color='#F44336', alpha=0.7, edgecolor='black')
    plt.axvline(x=1.0, color='black', linestyle='--', linewidth=2, label='Noise=1.0 (boundary)')
    plt.axvline(x=np.mean(arr), color='blue', linestyle='-', linewidth=2, label=f'Mean={np.mean(arr):.2f}')

    plt.xlabel('Noise Ratio (TB grad / GT grad)')
    plt.ylabel('Count')
    plt.title('Noise Ratio Distribution for U_ignore Errors')
    plt.legend()

    pct_above = np.mean(np.array(u_ignore_noise) > 1.0) * 100
    plt.annotate(f'{pct_above:.1f}% > 1.0', xy=(0.95, 0.95), xycoords='axes fraction',
                 ha='right', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat'))

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_gradient_heatmap(
    sample_u_line: Dict,
    sample_u_ignore: Dict,
    path: str
) -> None:
    """Gradient heatmap for one U_line vs one U_ignore sample."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, sample, title, color in [
        (axes[0], sample_u_line, 'U_line Sample', '#4CAF50'),
        (axes[1], sample_u_ignore, 'U_ignore Sample', '#F44336')
    ]:
        gt_grad = sample.get('gt_grad', 0)
        tb_grad = sample.get('tb_grad', 0)
        other_grad = sample.get('other_grad', 0)

        bars = ax.bar(['Ground Truth', 'Traceback', 'Other'], [gt_grad, tb_grad, other_grad],
                      color=[color, '#FFC107', '#9E9E9E'])
        ax.set_ylabel('Gradient Magnitude')
        ax.set_title(title)

        for bar, val in zip(bars, [gt_grad, tb_grad, other_grad]):
            ax.annotate(f'{val:.3f}', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_concentration_vs_noise_scatter(
    results: Dict[str, List[Dict]],
    path: str
) -> None:
    """Scatter plot of GT concentration vs noise ratio by error type."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    plt.figure(figsize=(10, 8))
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
    except:
        pass

    for key, color, label in [('u_line', '#4CAF50', 'U_line'), ('u_ignore', '#F44336', 'U_ignore')]:
        if key not in results or not results[key]:
            continue
        x = [r['gt_concentration'] for r in results[key]]
        y = [r['noise_ratio'] for r in results[key]]

        x = np.clip(x, 0, np.percentile(x, 99))
        y = np.clip(y, 0, np.percentile(y, 99))

        plt.scatter(x, y, c=color, alpha=0.5, label=label, s=30)

    plt.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, label='Noise=1.0')
    plt.axvline(x=1.0, color='gray', linestyle=':', alpha=0.5)

    plt.xlabel('GT Concentration (gt_grad / other_grad)')
    plt.ylabel('Noise Ratio (tb_grad / gt_grad)')
    plt.title('Ground Truth Concentration vs Noise Ratio')
    plt.legend()

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
