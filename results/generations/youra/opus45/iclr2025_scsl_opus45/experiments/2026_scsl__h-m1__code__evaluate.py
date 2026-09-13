"""Evaluation and visualization module for H-M1 experiment.

Implements gate evaluation logic and visualization functions for
curvature timing analysis results.
"""

import json
import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import yaml

from config import Config


def evaluate_timing_gap(results_per_seed: List[Dict[str, Any]], config: Config) -> Dict[str, Any]:
    """Compute aggregate gate metrics from per-seed results.

    Args:
        results_per_seed: List of result dicts from CurvatureTimingAnalyzer
        config: Experiment configuration

    Returns:
        Dictionary with:
            gaps: List[float] - per-seed timing gaps
            passes: List[bool] - per-seed gap >= threshold
            pass_rate: float - fraction passing
            mean_gap: float
            std_gap: float
            gate_passed: bool - pass_rate >= 0.70
    """
    gaps = [r['timing_gap'] for r in results_per_seed]
    passes = [g >= config.timing_gap_threshold for g in gaps]
    pass_rate = float(np.mean(passes))

    return {
        'gaps': gaps,
        'passes': passes,
        'pass_rate': pass_rate,
        'mean_gap': float(np.mean(gaps)),
        'std_gap': float(np.std(gaps)),
        'gate_passed': pass_rate >= config.pass_rate_threshold,
        'num_seeds': len(gaps),
        'num_passed': sum(passes),
    }


def evaluate_gate(pass_rate: float, threshold: float = 0.70) -> bool:
    """Return True if pass_rate >= threshold.

    Args:
        pass_rate: Fraction of seeds meeting timing gap criterion
        threshold: Required pass rate (default: 0.70)

    Returns:
        Boolean gate result
    """
    return pass_rate >= threshold


def plot_gate_metrics(
    results: Dict[str, Any],
    save_path: str,
    config: Config,
) -> None:
    """Generate gate metrics visualization.

    Creates a two-panel figure:
    - Left: Per-seed timing gap vs 3-epoch threshold
    - Right: Pass rate vs 70% threshold

    Args:
        results: Gate evaluation results from evaluate_timing_gap
        save_path: Path to save figure
        config: Experiment configuration
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left panel: Per-seed timing gaps
    ax1 = axes[0]
    seeds = list(range(1, len(results['gaps']) + 1))
    colors = ['green' if p else 'red' for p in results['passes']]
    bars = ax1.bar(seeds, results['gaps'], color=colors, alpha=0.7, edgecolor='black')
    ax1.axhline(y=config.timing_gap_threshold, color='blue', linestyle='--', linewidth=2,
                label=f'Threshold ({config.timing_gap_threshold} epochs)')
    ax1.set_xlabel('Seed', fontsize=12)
    ax1.set_ylabel('Timing Gap (epochs)', fontsize=12)
    ax1.set_title('Per-Seed Timing Gap', fontsize=14)
    ax1.legend(loc='upper right')
    ax1.set_xticks(seeds)

    # Add value labels on bars
    for bar, gap in zip(bars, results['gaps']):
        height = bar.get_height()
        ax1.annotate(f'{gap:.1f}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=10)

    # Right panel: Pass rate
    ax2 = axes[1]
    bar_color = 'green' if results['gate_passed'] else 'red'
    ax2.bar(['Pass Rate'], [results['pass_rate'] * 100], color=bar_color, alpha=0.7,
            edgecolor='black', width=0.5)
    ax2.axhline(y=config.pass_rate_threshold * 100, color='blue', linestyle='--',
                linewidth=2, label=f'Threshold ({config.pass_rate_threshold * 100:.0f}%)')
    ax2.set_ylabel('Percentage (%)', fontsize=12)
    ax2.set_title('Gate Pass Rate', fontsize=14)
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper right')

    # Add value label
    ax2.annotate(f'{results["pass_rate"] * 100:.1f}%',
                 xy=(0, results['pass_rate'] * 100),
                 xytext=(0, 3), textcoords="offset points",
                 ha='center', va='bottom', fontsize=14, fontweight='bold')

    # Gate result annotation
    gate_result = "PASS" if results['gate_passed'] else "FAIL"
    gate_color = 'green' if results['gate_passed'] else 'red'
    fig.suptitle(f"H-M1 Gate Evaluation: {gate_result}", fontsize=16, fontweight='bold',
                 color=gate_color)

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.fig_dpi, bbox_inches='tight')
    plt.close()
    print(f"  Saved gate metrics figure: {save_path}")


def plot_per_seed_timing_gap(
    gaps: List[float],
    save_path: str,
    config: Config,
) -> None:
    """Generate per-seed timing gap bar chart.

    Args:
        gaps: List of timing gaps per seed
        save_path: Path to save figure
        config: Experiment configuration
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    seeds = list(range(1, len(gaps) + 1))
    colors = ['green' if g >= config.timing_gap_threshold else 'red' for g in gaps]
    bars = ax.bar(seeds, gaps, color=colors, alpha=0.7, edgecolor='black')

    ax.axhline(y=config.timing_gap_threshold, color='blue', linestyle='--', linewidth=2,
               label=f'Threshold ({config.timing_gap_threshold} epochs)')
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=1)

    ax.set_xlabel('Seed Index', fontsize=12)
    ax.set_ylabel('Timing Gap (epochs)', fontsize=12)
    ax.set_title('Curvature Timing Gap: Minority - Majority Median Sign-Flip Epoch', fontsize=14)
    ax.legend(loc='upper right')
    ax.set_xticks(seeds)

    # Add value labels
    for bar, gap in zip(bars, gaps):
        height = bar.get_height()
        ax.annotate(f'{gap:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

    # Summary statistics
    mean_gap = np.mean(gaps)
    std_gap = np.std(gaps)
    ax.text(0.02, 0.98, f'Mean: {mean_gap:.2f} | Std: {std_gap:.2f}',
            transform=ax.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.fig_dpi, bbox_inches='tight')
    plt.close()
    print(f"  Saved per-seed timing gap figure: {save_path}")


def plot_curvature_trajectories(
    curvature_per_seed: List[np.ndarray],
    group_labels: np.ndarray,
    save_path: str,
    config: Config,
) -> None:
    """Generate curvature trajectory comparison figure.

    Shows mean +/- std curvature over epochs for minority vs majority groups.

    Args:
        curvature_per_seed: List of curvature matrices (N, E-2) per seed
        group_labels: Group labels array, shape (N,)
        save_path: Path to save figure
        config: Experiment configuration
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Minority mask
    minority_mask = (group_labels == 1) | (group_labels == 2)
    majority_mask = ~minority_mask

    # Average across seeds
    curvature_stack = np.stack(curvature_per_seed, axis=0)  # (num_seeds, N, E-2)
    curvature_mean = np.mean(curvature_stack, axis=0)  # (N, E-2)

    epochs = np.arange(2, curvature_mean.shape[1] + 2)  # Offset for central diff

    # Minority statistics
    minority_curvature = curvature_mean[minority_mask]
    minority_mean = np.mean(minority_curvature, axis=0)
    minority_std = np.std(minority_curvature, axis=0)

    # Majority statistics
    majority_curvature = curvature_mean[majority_mask]
    majority_mean = np.mean(majority_curvature, axis=0)
    majority_std = np.std(majority_curvature, axis=0)

    # Plot
    ax.plot(epochs, minority_mean, 'r-', linewidth=2, label='Minority (mean)')
    ax.fill_between(epochs, minority_mean - minority_std, minority_mean + minority_std,
                    color='red', alpha=0.2, label='Minority (std)')

    ax.plot(epochs, majority_mean, 'b-', linewidth=2, label='Majority (mean)')
    ax.fill_between(epochs, majority_mean - majority_std, majority_mean + majority_std,
                    color='blue', alpha=0.2, label='Majority (std)')

    ax.axhline(y=config.curvature_threshold, color='green', linestyle='--', linewidth=1.5,
               label=f'Threshold ({config.curvature_threshold})')
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=1)

    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Curvature (d²L/dt²)', fontsize=12)
    ax.set_title('Curvature Trajectories: Minority vs Majority Groups', fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.fig_dpi, bbox_inches='tight')
    plt.close()
    print(f"  Saved curvature trajectories figure: {save_path}")


def plot_sign_flip_distribution(
    sign_flip_epochs_per_seed: List[np.ndarray],
    group_labels: np.ndarray,
    save_path: str,
    config: Config,
) -> None:
    """Generate sign-flip epoch distribution figure.

    Shows histogram/violin of sign-flip epochs for minority vs majority groups.

    Args:
        sign_flip_epochs_per_seed: List of sign-flip epoch arrays (N,) per seed
        group_labels: Group labels array, shape (N,)
        save_path: Path to save figure
        config: Experiment configuration
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Minority mask
    minority_mask = (group_labels == 1) | (group_labels == 2)
    majority_mask = ~minority_mask

    # Aggregate across seeds (use first seed for visualization)
    sign_flip_epochs = sign_flip_epochs_per_seed[0]

    minority_epochs = sign_flip_epochs[minority_mask]
    majority_epochs = sign_flip_epochs[majority_mask]

    # Left: Histogram
    ax1 = axes[0]
    bins = np.arange(1, 24)  # Up to 22 (never stabilized default)
    ax1.hist(majority_epochs, bins=bins, alpha=0.6, label='Majority', color='blue', edgecolor='black')
    ax1.hist(minority_epochs, bins=bins, alpha=0.6, label='Minority', color='red', edgecolor='black')
    ax1.axvline(x=np.median(majority_epochs), color='blue', linestyle='--', linewidth=2,
                label=f'Majority median ({np.median(majority_epochs):.1f})')
    ax1.axvline(x=np.median(minority_epochs), color='red', linestyle='--', linewidth=2,
                label=f'Minority median ({np.median(minority_epochs):.1f})')
    ax1.set_xlabel('Sign-Flip Epoch', fontsize=12)
    ax1.set_ylabel('Count', fontsize=12)
    ax1.set_title('Sign-Flip Epoch Distribution', fontsize=14)
    ax1.legend(loc='upper right')

    # Right: Box plot
    ax2 = axes[1]
    bp = ax2.boxplot([majority_epochs, minority_epochs], labels=['Majority', 'Minority'],
                     patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightcoral')
    ax2.set_ylabel('Sign-Flip Epoch', fontsize=12)
    ax2.set_title('Sign-Flip Epoch Comparison', fontsize=14)

    # Add median annotations
    for i, (data, label) in enumerate(zip([majority_epochs, minority_epochs], ['Majority', 'Minority'])):
        median = np.median(data)
        ax2.annotate(f'Median: {median:.1f}',
                     xy=(i + 1, median),
                     xytext=(10, 0), textcoords="offset points",
                     ha='left', va='center', fontsize=10,
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.fig_dpi, bbox_inches='tight')
    plt.close()
    print(f"  Saved sign-flip distribution figure: {save_path}")


def save_results(
    gate_results: Dict[str, Any],
    results_per_seed: List[Dict[str, Any]],
    config: Config,
) -> str:
    """Save results to JSON file.

    Args:
        gate_results: Gate evaluation results
        results_per_seed: Per-seed analysis results
        config: Experiment configuration

    Returns:
        Path to saved results file
    """
    os.makedirs(config.output_dir, exist_ok=True)
    results_path = os.path.join(config.output_dir, "results.json")

    # Prepare serializable results
    output = {
        'hypothesis_id': 'h-m1',
        'gate_type': 'SHOULD_WORK',
        'gate_result': 'PASS' if gate_results['gate_passed'] else 'FAIL',
        'pass_rate': gate_results['pass_rate'],
        'pass_rate_threshold': config.pass_rate_threshold,
        'timing_gap_threshold': config.timing_gap_threshold,
        'mean_gap': gate_results['mean_gap'],
        'std_gap': gate_results['std_gap'],
        'num_seeds': gate_results['num_seeds'],
        'num_passed': gate_results['num_passed'],
        'per_seed_results': [],
    }

    for i, r in enumerate(results_per_seed):
        seed_result = {
            'seed': r['seed'],
            'timing_gap': r['timing_gap'],
            'minority_median_epoch': r['minority_median_epoch'],
            'majority_median_epoch': r['majority_median_epoch'],
            'minority_count': r['minority_count'],
            'majority_count': r['majority_count'],
            'gap_passes': r['timing_gap'] >= config.timing_gap_threshold,
        }
        output['per_seed_results'].append(seed_result)

    with open(results_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"  Saved results to: {results_path}")
    return results_path


def update_verification_state(
    gate_passed: bool,
    pass_rate: float,
    mean_gap: float,
    std_gap: float,
    yaml_path: str,
) -> None:
    """Update verification_state.yaml with H-M1 results.

    Args:
        gate_passed: Boolean gate result
        pass_rate: Fraction of seeds passing
        mean_gap: Mean timing gap across seeds
        std_gap: Standard deviation of timing gap
        yaml_path: Path to verification_state.yaml
    """
    with open(yaml_path, 'r') as f:
        state = yaml.safe_load(f)

    # Update h-m1 section
    state['sub_hypotheses']['h-m1']['status'] = 'COMPLETED'
    state['sub_hypotheses']['h-m1']['completed'] = True
    state['sub_hypotheses']['h-m1']['completed_at'] = None  # Will be set by pipeline
    state['sub_hypotheses']['h-m1']['gate']['satisfied'] = gate_passed
    state['sub_hypotheses']['h-m1']['gate']['result'] = 'PASS' if gate_passed else 'FAIL'
    state['sub_hypotheses']['h-m1']['validation']['status'] = 'COMPLETED'
    state['sub_hypotheses']['h-m1']['validation']['result'] = 'PASS' if gate_passed else 'FAIL'
    state['sub_hypotheses']['h-m1']['validation']['key_findings'] = [
        f"Timing gap = {mean_gap:.2f} +/- {std_gap:.2f} epochs",
        f"Pass rate = {pass_rate * 100:.1f}% (threshold: 70%)",
        f"Gate SHOULD_WORK: {'PASSED' if gate_passed else 'FAILED'}",
    ]

    # Update statistics
    if gate_passed:
        state['statistics']['validated_sub_hypotheses'] += 1
        state['statistics']['gates_passed'] += 1
    else:
        state['statistics']['failed_sub_hypotheses'] += 1
        state['statistics']['gates_failed'] += 1

    with open(yaml_path, 'w') as f:
        yaml.dump(state, f, default_flow_style=False, sort_keys=False)

    print(f"  Updated verification state: {yaml_path}")
