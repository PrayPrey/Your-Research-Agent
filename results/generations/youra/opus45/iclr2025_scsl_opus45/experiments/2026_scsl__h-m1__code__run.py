#!/usr/bin/env python3
"""Main experiment runner for H-M1: Curvature Timing Analysis.

Orchestrates multi-seed training, curvature computation, and gate evaluation.

Hypothesis: Minority samples show delayed curvature stabilization
(sign-flip epoch >= 3 epochs later than majority in >= 70% of seeds).

Gate: SHOULD_WORK
"""

import os
import random
import sys
from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import torch

from config import Config, get_config
from data import get_dataloaders, get_eval_dataloader, get_group_labels
from model import build_model
from train import train
from curvature import CurvatureTimingAnalyzer, verify_curvature_mechanism
from evaluate import (
    evaluate_timing_gap,
    plot_gate_metrics,
    plot_per_seed_timing_gap,
    plot_curvature_trajectories,
    plot_sign_flip_distribution,
    save_results,
    update_verification_state,
)


def set_seed(seed: int) -> None:
    """Set random seeds for reproducibility.

    Args:
        seed: Random seed value
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # For deterministic behavior (may impact performance)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def run_single_seed(
    config: Config,
    seed: int,
    device: torch.device,
) -> Dict[str, Any]:
    """Run full pipeline for one seed.

    Steps:
    1. Set seed for reproducibility
    2. Build model
    3. Get dataloaders
    4. Train with loss trajectory logging
    5. Compute curvature and timing gap

    Args:
        config: Experiment configuration
        seed: Random seed
        device: Compute device

    Returns:
        Dictionary with per-seed results
    """
    print(f"\n{'='*60}")
    print(f"Running seed {seed}")
    print(f"{'='*60}")

    # Set seed
    set_seed(seed)

    # Build model
    print("Building model...")
    model = build_model(config)

    # Get dataloaders
    print("Loading data...")
    train_loader, _, _ = get_dataloaders(config)
    eval_loader = get_eval_dataloader(config)
    group_labels = get_group_labels(config)

    print(f"  Training samples: {len(train_loader.dataset)}")
    print(f"  Group distribution: {np.bincount(group_labels)}")

    # Train with loss trajectory logging
    print("Training...")
    model, tracker = train(config, model, train_loader, eval_loader, device)

    # Get loss matrix
    loss_matrix = tracker.get_loss_matrix()
    print(f"  Loss matrix shape: {loss_matrix.shape}")

    # Verify curvature mechanism
    print("Verifying curvature mechanism...")
    verify_curvature_mechanism(loss_matrix, group_labels, sigma=config.smoothing_sigma)

    # Compute timing gap
    print("Computing curvature timing gap...")
    analyzer = CurvatureTimingAnalyzer(
        loss_matrix,
        kappa_threshold=config.curvature_threshold,
        consecutive_epochs=config.consecutive_epochs,
    )
    timing_results = analyzer.compute_timing_gap(group_labels, sigma=config.smoothing_sigma)

    # Compile results
    result = {
        'seed': seed,
        'loss_matrix': loss_matrix,
        'group_labels': group_labels,
        'timing_gap': timing_results['timing_gap'],
        'minority_median_epoch': timing_results['minority_median_epoch'],
        'majority_median_epoch': timing_results['majority_median_epoch'],
        'minority_count': timing_results['minority_count'],
        'majority_count': timing_results['majority_count'],
        'sign_flip_epochs': timing_results['sign_flip_epochs'],
        'curvature': timing_results['curvature'],
    }

    print(f"\n  Seed {seed} Results:")
    print(f"    Timing gap: {result['timing_gap']:.2f} epochs")
    print(f"    Minority median: {result['minority_median_epoch']:.2f}")
    print(f"    Majority median: {result['majority_median_epoch']:.2f}")
    print(f"    Gap passes threshold: {result['timing_gap'] >= config.timing_gap_threshold}")

    return result


def main() -> Dict[str, Any]:
    """Main experiment orchestration.

    Runs multi-seed training, evaluates gate, generates visualizations,
    and updates verification state.

    Returns:
        Gate evaluation results
    """
    print("="*70)
    print("H-M1: Curvature Timing Analysis Experiment")
    print("="*70)
    print(f"Start time: {datetime.now().isoformat()}")

    # Load configuration
    config = get_config()
    print(f"\nConfiguration:")
    print(f"  Seeds: {config.seeds}")
    print(f"  Epochs: {config.epochs}")
    print(f"  Trajectory epochs: {config.trajectory_epochs}")
    print(f"  Smoothing sigma: {config.smoothing_sigma}")
    print(f"  Curvature threshold: {config.curvature_threshold}")
    print(f"  Consecutive epochs: {config.consecutive_epochs}")
    print(f"  Timing gap threshold: {config.timing_gap_threshold}")
    print(f"  Pass rate threshold: {config.pass_rate_threshold}")

    # Select device
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"\nUsing GPU: {torch.cuda.get_device_name()}")
    else:
        device = torch.device("cpu")
        print("\nUsing CPU (no GPU available)")

    # Run multi-seed experiments
    results_per_seed: List[Dict[str, Any]] = []

    for seed in config.seeds:
        result = run_single_seed(config, seed, device)
        results_per_seed.append(result)

    # Evaluate gate
    print("\n" + "="*70)
    print("Gate Evaluation")
    print("="*70)

    gate_results = evaluate_timing_gap(results_per_seed, config)

    print(f"\n  Results Summary:")
    print(f"    Mean timing gap: {gate_results['mean_gap']:.2f} +/- {gate_results['std_gap']:.2f} epochs")
    print(f"    Pass rate: {gate_results['pass_rate'] * 100:.1f}% ({gate_results['num_passed']}/{gate_results['num_seeds']} seeds)")
    print(f"    Gate threshold: {config.pass_rate_threshold * 100:.0f}%")
    print(f"\n  Per-seed gaps: {[f'{g:.2f}' for g in gate_results['gaps']]}")
    print(f"  Per-seed passes: {gate_results['passes']}")

    gate_status = "PASS" if gate_results['gate_passed'] else "FAIL"
    print(f"\n  >>> Gate SHOULD_WORK: {gate_status} <<<")

    # Create output directories
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    # Generate visualizations
    print("\nGenerating visualizations...")

    plot_gate_metrics(
        gate_results,
        os.path.join(config.figures_dir, "gate_metrics.png"),
        config,
    )

    plot_per_seed_timing_gap(
        gate_results['gaps'],
        os.path.join(config.figures_dir, "per_seed_timing_gap.png"),
        config,
    )

    # Use group labels from first seed for visualization
    group_labels = results_per_seed[0]['group_labels']

    plot_curvature_trajectories(
        [r['curvature'] for r in results_per_seed],
        group_labels,
        os.path.join(config.figures_dir, "curvature_trajectories.png"),
        config,
    )

    plot_sign_flip_distribution(
        [r['sign_flip_epochs'] for r in results_per_seed],
        group_labels,
        os.path.join(config.figures_dir, "sign_flip_distribution.png"),
        config,
    )

    # Save results
    print("\nSaving results...")
    save_results(gate_results, results_per_seed, config)

    # Update verification state
    print("\nUpdating verification state...")
    verification_state_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "..",
        "verification_state.yaml"
    )
    # Normalize path
    verification_state_path = os.path.normpath(verification_state_path)
    print(f"  Verification state path: {verification_state_path}")

    update_verification_state(
        gate_results['gate_passed'],
        gate_results['pass_rate'],
        gate_results['mean_gap'],
        gate_results['std_gap'],
        verification_state_path,
    )

    # Final summary
    print("\n" + "="*70)
    print("Experiment Complete")
    print("="*70)
    print(f"End time: {datetime.now().isoformat()}")
    print(f"\nFinal Results:")
    print(f"  Hypothesis: H-M1 (Curvature Timing Analysis)")
    print(f"  Gate: SHOULD_WORK")
    print(f"  Result: {gate_status}")
    print(f"  Mean timing gap: {gate_results['mean_gap']:.2f} +/- {gate_results['std_gap']:.2f} epochs")
    print(f"  Pass rate: {gate_results['pass_rate'] * 100:.1f}%")
    print(f"\nOutput files:")
    print(f"  - {config.output_dir}/results.json")
    print(f"  - {config.figures_dir}/gate_metrics.png")
    print(f"  - {config.figures_dir}/per_seed_timing_gap.png")
    print(f"  - {config.figures_dir}/curvature_trajectories.png")
    print(f"  - {config.figures_dir}/sign_flip_distribution.png")

    return gate_results


if __name__ == "__main__":
    main()
