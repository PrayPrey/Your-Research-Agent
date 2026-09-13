"""Orchestrator for H-M2 experiment.

Runs 3 training regimes (ERM, GroupDRO, Random Reweighting) across multiple seeds,
evaluates AUROC for each, computes gate condition, and saves results.

Gate: AUROC_ERM - AUROC_GroupDRO > 0.10 AND AUROC_ERM - AUROC_Random < 0.05
"""

import json
import os
import random
import sys
from datetime import datetime
from typing import Dict, Optional, Tuple

import numpy as np
import torch

from config import Config, get_config
from data import (
    WaterbirdsDataset,
    get_dataloaders,
    get_eval_dataloader,
    get_group_counts,
    get_minority_labels,
)
from model import build_model
from trainers import (
    train_erm,
    train_groupdro,
    train_random_reweight,
    compute_variance_matched_weights,
)
from evaluate import (
    extract_trajectory_features,
    evaluate_all_regimes,
    compute_delta_auroc,
    evaluate_gate,
    verify_mechanism_activation,
    compute_gradient_variance,
    plot_gate_metrics,
    plot_auroc_comparison,
    plot_group_weights_evolution,
    plot_gradient_variance_comparison,
    plot_loss_trajectory_panels,
)


def set_seed(seed: int) -> None:
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def run_regime(
    regime_name: str,
    config: Config,
    seed: int,
    device: torch.device,
    train_loader,
    eval_loader,
    group_counts: np.ndarray,
    group_ids: np.ndarray,
    random_weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Run one training regime.

    Args:
        regime_name: 'erm', 'groupdro', or 'random'
        config: Experiment configuration
        seed: Random seed
        device: Compute device
        train_loader: Training dataloader
        eval_loader: Evaluation dataloader
        group_counts: Per-group sample counts
        group_ids: Per-sample group IDs
        random_weights: Pre-computed random weights (for random regime)

    Returns:
        Tuple of (loss_matrix, group_weights_history or None)
    """
    set_seed(seed)
    model = build_model(config).to(device)

    print(f"\n{'='*60}")
    print(f"Running {regime_name.upper()} regime (seed={seed})")
    print(f"{'='*60}")

    if regime_name == "erm":
        model, tracker = train_erm(config, model, train_loader, eval_loader, device)
        return tracker.get_loss_matrix(), None

    elif regime_name == "groupdro":
        model, tracker, group_weights_history = train_groupdro(
            config, model, train_loader, eval_loader, device, group_counts
        )
        return tracker.get_loss_matrix(), group_weights_history

    elif regime_name == "random":
        model, tracker = train_random_reweight(
            config, model, train_loader, eval_loader, device, random_weights
        )
        return tracker.get_loss_matrix(), None

    else:
        raise ValueError(f"Unknown regime: {regime_name}")


def main(config: Config) -> Dict:
    """Main experiment orchestration.

    Args:
        config: Experiment configuration

    Returns:
        Results dictionary with AUROC, deltas, gate result, and mechanism info
    """
    print("=" * 70)
    print("H-M2: Spurious-Specificity Mechanism Test")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Config: epochs={config.epochs}, seeds={config.num_seeds}, batch_size={config.batch_size}")

    # Setup device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # Create output directories
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    # Load data once (shared across regimes)
    print("\nLoading data...")
    set_seed(config.base_seed)
    train_loader, val_loader, test_loader = get_dataloaders(config)
    eval_loader = get_eval_dataloader(config)

    # Get dataset info
    train_dataset = train_loader.dataset
    group_counts = get_group_counts(train_dataset)
    minority_labels = get_minority_labels(train_dataset)
    group_ids = train_dataset.group_ids
    num_samples = len(train_dataset)

    print(f"Training samples: {num_samples}")
    print(f"Group counts: {group_counts}")
    print(f"Minority samples: {minority_labels.sum()} ({100*minority_labels.mean():.1f}%)")

    # Pre-compute random weights (used by all seeds for consistency)
    random_weights = compute_variance_matched_weights(
        group_counts, num_samples, group_ids, config.groupdro_gamma, config.base_seed
    )
    random_grad_var = compute_gradient_variance(random_weights)
    print(f"Random weights variance: {random_grad_var:.6f}")

    # Collect results across seeds
    all_features = {"erm": [], "groupdro": [], "random": []}
    all_loss_matrices = {"erm": [], "groupdro": [], "random": []}
    all_group_weights_history = []

    seeds = [config.base_seed + i for i in range(config.num_seeds)]
    print(f"\nRunning {config.num_seeds} seeds: {seeds}")

    for seed_idx, seed in enumerate(seeds):
        print(f"\n{'#'*70}")
        print(f"# SEED {seed_idx + 1}/{config.num_seeds}: {seed}")
        print(f"{'#'*70}")

        # Run ERM
        loss_matrix_erm, _ = run_regime(
            "erm", config, seed, device, train_loader, eval_loader,
            group_counts, group_ids
        )
        features_erm = extract_trajectory_features(loss_matrix_erm)
        all_features["erm"].append(features_erm)
        all_loss_matrices["erm"].append(loss_matrix_erm)

        # Run GroupDRO
        loss_matrix_gdro, group_weights_history = run_regime(
            "groupdro", config, seed, device, train_loader, eval_loader,
            group_counts, group_ids
        )
        features_gdro = extract_trajectory_features(loss_matrix_gdro)
        all_features["groupdro"].append(features_gdro)
        all_loss_matrices["groupdro"].append(loss_matrix_gdro)
        all_group_weights_history.append(group_weights_history)

        # Run Random Reweighting
        loss_matrix_random, _ = run_regime(
            "random", config, seed, device, train_loader, eval_loader,
            group_counts, group_ids, random_weights
        )
        features_random = extract_trajectory_features(loss_matrix_random)
        all_features["random"].append(features_random)
        all_loss_matrices["random"].append(loss_matrix_random)

    # Average features across seeds
    print(f"\n{'='*70}")
    print("AGGREGATING RESULTS")
    print(f"{'='*70}")

    avg_features = {
        regime: np.mean(all_features[regime], axis=0)
        for regime in ["erm", "groupdro", "random"]
    }

    # Use first seed's loss matrices for visualization (representative)
    repr_loss_matrices = {
        regime: all_loss_matrices[regime][0]
        for regime in ["erm", "groupdro", "random"]
    }

    # Average group weights history
    avg_group_weights_history = np.mean(all_group_weights_history, axis=0)

    # Evaluate AUROC for each regime
    print("\nEvaluating AUROC...")
    auroc_results = evaluate_all_regimes(avg_features, minority_labels, config)

    # Compute deltas
    auroc_erm = auroc_results["erm"][0]
    auroc_gdro = auroc_results["groupdro"][0]
    auroc_random = auroc_results["random"][0]

    delta_gdro, delta_random = compute_delta_auroc(auroc_erm, auroc_gdro, auroc_random)
    print(f"\nΔAUROC (GroupDRO) = {auroc_erm:.4f} - {auroc_gdro:.4f} = {delta_gdro:.4f}")
    print(f"ΔAUROC (Random) = {auroc_erm:.4f} - {auroc_random:.4f} = {delta_random:.4f}")

    # Evaluate gate
    passed, result_str = evaluate_gate(delta_gdro, delta_random, config)

    # Compute GroupDRO gradient variance (use average final weights)
    final_gdro_weights = avg_group_weights_history[-1]
    # Approximate per-sample weight variance from group weights
    per_sample_gdro_weights = final_gdro_weights[group_ids]
    gdro_grad_var = compute_gradient_variance(per_sample_gdro_weights)

    # Verify mechanism activation
    mechanism = verify_mechanism_activation(
        avg_group_weights_history, gdro_grad_var, random_grad_var
    )

    # Generate figures
    print("\nGenerating figures...")
    plot_gate_metrics(
        delta_gdro, delta_random, config,
        os.path.join(config.figures_dir, config.fig_gate_filename)
    )
    plot_auroc_comparison(
        auroc_results, config,
        os.path.join(config.figures_dir, config.fig_auroc_comparison_filename)
    )
    plot_group_weights_evolution(
        avg_group_weights_history, config,
        os.path.join(config.figures_dir, config.fig_group_weights_filename)
    )
    plot_gradient_variance_comparison(
        gdro_grad_var, random_grad_var, config,
        os.path.join(config.figures_dir, config.fig_grad_variance_filename)
    )
    plot_loss_trajectory_panels(
        repr_loss_matrices, minority_labels, config,
        os.path.join(config.figures_dir, config.fig_trajectory_panels_filename)
    )

    # Compile results
    results = {
        "hypothesis_id": "h-m2",
        "gate_type": "SHOULD_WORK",
        "timestamp": datetime.now().isoformat(),
        "auroc": {
            "erm": {"mean": float(auroc_results["erm"][0]), "std": float(auroc_results["erm"][1])},
            "groupdro": {"mean": float(auroc_results["groupdro"][0]), "std": float(auroc_results["groupdro"][1])},
            "random": {"mean": float(auroc_results["random"][0]), "std": float(auroc_results["random"][1])},
        },
        "delta_auroc": {
            "delta_gdro": float(delta_gdro),
            "delta_random": float(delta_random),
        },
        "gate": {
            "passed": bool(passed),
            "delta_gdro_threshold": config.delta_gdro_threshold,
            "delta_random_threshold": config.delta_random_threshold,
            "result": result_str,
        },
        "mechanism": {
            "gdro_weights_diverged": bool(mechanism["weights_diverged"]),
            "variance_matched": bool(mechanism["variance_matched"]),
            "gdro_grad_var": float(gdro_grad_var),
            "random_grad_var": float(random_grad_var),
        },
        "config": {
            "epochs": config.epochs,
            "trajectory_epochs": config.trajectory_epochs,
            "batch_size": config.batch_size,
            "lr": config.lr,
            "weight_decay_erm": config.weight_decay_erm,
            "weight_decay_gdro": config.weight_decay_gdro,
            "groupdro_gamma": config.groupdro_gamma,
        },
        "seeds_used": seeds,
    }

    # Save results
    results_path = os.path.join(config.output_dir, config.results_filename)
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    # Print final summary
    print(f"\n{'='*70}")
    print("EXPERIMENT COMPLETE")
    print(f"{'='*70}")
    print(f"AUROC (ERM):      {auroc_erm:.4f} ± {auroc_results['erm'][1]:.4f}")
    print(f"AUROC (GroupDRO): {auroc_gdro:.4f} ± {auroc_results['groupdro'][1]:.4f}")
    print(f"AUROC (Random):   {auroc_random:.4f} ± {auroc_results['random'][1]:.4f}")
    print(f"\nΔAUROC (GroupDRO): {delta_gdro:.4f} (target: > {config.delta_gdro_threshold})")
    print(f"ΔAUROC (Random):   {delta_random:.4f} (target: < {config.delta_random_threshold})")
    print(f"\nGate Result: {result_str}")
    print(f"{'='*70}")

    return results


if __name__ == "__main__":
    config = get_config()
    results = main(config)
    sys.exit(0 if results["gate"]["passed"] else 1)
