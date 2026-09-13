"""H-E1 Visualization Module: Generate required figures."""
import os
import logging
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from config import PATHS
from evaluate import CheckpointResult

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def plot_gate_scatter(
    contamination: np.ndarray,
    residuals: np.ndarray,
    r: float,
    p: float,
    out_path: str,
) -> None:
    """Scatter plot: contamination vs inflation residual (Gate Figure)."""
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(contamination, residuals, alpha=0.6, s=50)

    if len(contamination) > 1:
        z = np.polyfit(contamination, residuals, 1)
        poly = np.poly1d(z)
        x_line = np.linspace(contamination.min(), contamination.max(), 100)
        ax.plot(x_line, poly(x_line), 'r--', linewidth=2, label=f'r={r:.3f}, p={p:.4f}')

    ax.set_xlabel('Contamination (%)', fontsize=12)
    ax.set_ylabel('Inflation Residual', fontsize=12)
    ax.set_title('Contamination vs Score Inflation', fontsize=14)
    ax.legend(loc='best')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    log.info(f"Saved: {out_path}")

def plot_contamination_by_benchmark(
    contamination_by_task: dict[str, float],
    out_path: str,
) -> None:
    """Bar chart: contamination by benchmark."""
    fig, ax = plt.subplots(figsize=(8, 5))

    tasks = list(contamination_by_task.keys())
    values = [contamination_by_task[t] for t in tasks]

    bars = ax.bar(tasks, values, color=sns.color_palette("husl", len(tasks)))

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=10)

    ax.set_xlabel('Benchmark', fontsize=12)
    ax.set_ylabel('13-gram Overlap (%)', fontsize=12)
    ax.set_title('Contamination by Benchmark', fontsize=14)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    log.info(f"Saved: {out_path}")

def plot_checkpoint_trajectory(
    checkpoints_data: list[CheckpointResult],
    out_path: str,
) -> None:
    """Line plot: benchmark scores across training steps by model size."""
    fig, ax = plt.subplots(figsize=(10, 6))

    sizes = sorted(set(c.size for c in checkpoints_data),
                   key=lambda s: float(s.replace('b', '').replace('m', 'e-3')))
    colors = sns.color_palette("viridis", len(sizes))

    for size, color in zip(sizes, colors):
        size_data = [c for c in checkpoints_data if c.size == size]
        steps = sorted(set(c.step for c in size_data))

        avg_scores = []
        for step in steps:
            step_scores = [c.score for c in size_data if c.step == step]
            avg_scores.append(np.mean(step_scores) if step_scores else 0)

        ax.plot(steps, avg_scores, marker='o', label=size, color=color, linewidth=2, markersize=4)

    ax.set_xlabel('Training Step', fontsize=12)
    ax.set_ylabel('Average Benchmark Score', fontsize=12)
    ax.set_title('Checkpoint Trajectory by Model Size', fontsize=14)
    ax.legend(title='Model Size', bbox_to_anchor=(1.02, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    log.info(f"Saved: {out_path}")

def plot_capability_detrending(
    wikitext_ppl: np.ndarray,
    scores: np.ndarray,
    out_path: str,
) -> None:
    """Scatter: WikiText perplexity vs benchmark score with regression."""
    fig, ax = plt.subplots(figsize=(8, 6))

    valid = (wikitext_ppl > 0) & np.isfinite(wikitext_ppl) & np.isfinite(scores)
    x = np.log(1.0 / wikitext_ppl[valid])
    y = scores[valid]

    ax.scatter(x, y, alpha=0.5, s=30)

    if len(x) > 1:
        coeffs = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_line, np.polyval(coeffs, x_line), 'r-', linewidth=2, label='Regression')

    ax.set_xlabel('log(1/Perplexity)', fontsize=12)
    ax.set_ylabel('Benchmark Score', fontsize=12)
    ax.set_title('Capability Detrending', fontsize=14)
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    log.info(f"Saved: {out_path}")

def plot_residual_distribution(
    residuals: np.ndarray,
    out_path: str,
) -> None:
    """Histogram: inflation residuals distribution."""
    fig, ax = plt.subplots(figsize=(8, 5))

    valid = np.isfinite(residuals)
    ax.hist(residuals[valid], bins=30, edgecolor='black', alpha=0.7)

    mean_val = np.mean(residuals[valid])
    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.4f}')

    ax.set_xlabel('Inflation Residual', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Distribution of Inflation Residuals', fontsize=14)
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    log.info(f"Saved: {out_path}")

def generate_all_figures(
    checkpoints_data: list[CheckpointResult],
    contamination_by_task: dict[str, float],
    analysis_result,
    figures_dir: Optional[str] = None,
) -> list[str]:
    """Generate all required figures."""
    figures_dir = figures_dir or PATHS.figures_dir
    os.makedirs(figures_dir, exist_ok=True)

    generated = []

    all_contam = []
    all_residuals = []
    all_ppl = []
    all_scores = []

    from analysis import fit_capability_regression, compute_inflation_residuals

    tasks = list(set(c.task for c in checkpoints_data))
    for task in tasks:
        rows = [c for c in checkpoints_data if c.task == task]
        ppl = np.array([r.wikitext_ppl for r in rows])
        scores = np.array([r.score for r in rows])

        _, expected = fit_capability_regression(ppl, scores)
        residuals = compute_inflation_residuals(scores, expected)

        contam_val = contamination_by_task.get(task, 0.0)

        all_contam.extend([contam_val] * len(rows))
        all_residuals.extend(residuals.tolist())
        all_ppl.extend(ppl.tolist())
        all_scores.extend(scores.tolist())

    all_contam = np.array(all_contam)
    all_residuals = np.array(all_residuals)
    all_ppl = np.array(all_ppl)
    all_scores = np.array(all_scores)

    path = os.path.join(figures_dir, "gate_scatter.png")
    plot_gate_scatter(all_contam, all_residuals, analysis_result.r, analysis_result.p_value, path)
    generated.append(path)

    path = os.path.join(figures_dir, "contamination_by_benchmark.png")
    plot_contamination_by_benchmark(contamination_by_task, path)
    generated.append(path)

    path = os.path.join(figures_dir, "checkpoint_trajectory.png")
    plot_checkpoint_trajectory(checkpoints_data, path)
    generated.append(path)

    path = os.path.join(figures_dir, "capability_detrending.png")
    plot_capability_detrending(all_ppl, all_scores, path)
    generated.append(path)

    path = os.path.join(figures_dir, "residual_distribution.png")
    plot_residual_distribution(all_residuals, path)
    generated.append(path)

    return generated

if __name__ == "__main__":
    print("Run via run.py for full figure generation")
