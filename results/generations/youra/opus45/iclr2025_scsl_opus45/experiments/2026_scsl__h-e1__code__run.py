"""Main experiment runner for H-E1 hypothesis validation.

Orchestrates: setup → data → train → evaluate → visualize → gate check

Usage:
    python run.py
"""

import json
import os
import random
import sys
from datetime import datetime
from typing import Dict

import numpy as np
import torch

from config import Config, get_config
from data import get_dataloaders, get_eval_dataloader, get_minority_labels, WaterbirdsDataset
from model import build_model
from train import train
from evaluate import (
    extract_trajectory_features,
    compute_auroc_cv,
    compute_per_feature_auroc,
    evaluate_gate,
    plot_gate_metrics,
    plot_loss_trajectories,
    plot_roc_curve,
    plot_feature_distributions,
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


def main(config: Config) -> Dict[str, float]:
    """Run complete H-E1 experiment.

    Args:
        config: Experiment configuration

    Returns:
        Dict with experiment results
    """
    print("=" * 60)
    print("H-E1 Experiment: Loss Trajectory Features for Minority Detection")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    # 1. Setup
    print("[1/6] Setting up experiment...")
    set_seed(config.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  Device: {device}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")

    # Create output directories
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)
    print(f"  Output dir: {config.output_dir}")
    print(f"  Figures dir: {config.figures_dir}")
    print()

    # 2. Load data
    print("[2/6] Loading Waterbirds dataset...")
    train_loader, val_loader, test_loader = get_dataloaders(config)
    eval_loader = get_eval_dataloader(config)

    train_dataset = train_loader.dataset
    num_train = len(train_dataset)
    print(f"  Training samples: {num_train}")
    print(f"  Validation samples: {len(val_loader.dataset)}")
    print(f"  Test samples: {len(test_loader.dataset)}")

    # Get minority labels for evaluation
    minority_labels = get_minority_labels(train_dataset)
    num_minority = minority_labels.sum()
    num_majority = len(minority_labels) - num_minority
    print(f"  Minority samples: {num_minority} ({100*num_minority/len(minority_labels):.1f}%)")
    print(f"  Majority samples: {num_majority} ({100*num_majority/len(minority_labels):.1f}%)")
    print()

    # 3. Build model
    print("[3/6] Building ResNet-50 model...")
    model = build_model(config)
    num_params = sum(p.numel() for p in model.parameters())
    print(f"  Parameters: {num_params / 1e6:.1f}M")
    print()

    # 4. Train with trajectory tracking
    print("[4/6] Training with loss trajectory tracking...")
    print(f"  Epochs: {config.epochs}")
    print(f"  Trajectory epochs: {config.trajectory_epochs}")
    print(f"  Batch size: {config.batch_size}")
    print(f"  Learning rate: {config.lr}")
    print()

    model, tracker = train(config, model, train_loader, eval_loader, device)
    loss_matrix = tracker.get_loss_matrix()
    print()
    print(f"  Loss matrix shape: {loss_matrix.shape}")
    print()

    # 5. Extract features and evaluate
    print("[5/6] Extracting trajectory features and evaluating...")
    features = extract_trajectory_features(loss_matrix)
    print(f"  Features shape: {features.shape}")

    # Compute AUROC with cross-validation
    auroc_mean, auroc_std = compute_auroc_cv(
        features, minority_labels, n_splits=config.n_folds, seed=config.seed
    )
    print(f"  AUROC (5-fold CV): {auroc_mean:.4f} ± {auroc_std:.4f}")

    # Compute per-feature AUROC
    per_feature_auroc = compute_per_feature_auroc(features, minority_labels)
    print("  Per-feature AUROC:")
    for name, score in per_feature_auroc.items():
        print(f"    {name}: {score:.4f}")

    # Gate evaluation
    gate_passed = evaluate_gate(auroc_mean, config.auroc_threshold)
    gate_result = "PASS" if gate_passed else "FAIL"
    print()
    print(f"  Gate threshold: {config.auroc_threshold}")
    print(f"  Gate result: {gate_result}")
    print()

    # 6. Generate visualizations
    print("[6/6] Generating visualizations...")
    plot_gate_metrics(
        auroc_mean,
        config.auroc_threshold,
        os.path.join(config.figures_dir, config.fig_gate_filename),
        config,
    )
    plot_loss_trajectories(
        loss_matrix,
        minority_labels,
        os.path.join(config.figures_dir, config.fig_trajectory_filename),
        config,
    )
    plot_roc_curve(
        features,
        minority_labels,
        os.path.join(config.figures_dir, config.fig_roc_filename),
        config,
    )
    plot_feature_distributions(
        features,
        minority_labels,
        os.path.join(config.figures_dir, config.fig_features_filename),
        config,
    )
    print()

    # Compile results
    results = {
        "hypothesis_id": "H-E1",
        "hypothesis_type": "EXISTENCE",
        "gate_type": "MUST_WORK",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "seed": config.seed,
            "epochs": config.epochs,
            "trajectory_epochs": config.trajectory_epochs,
            "batch_size": config.batch_size,
            "lr": config.lr,
            "n_folds": config.n_folds,
        },
        "dataset": {
            "name": "Waterbirds",
            "train_samples": num_train,
            "minority_samples": int(num_minority),
            "majority_samples": int(num_majority),
            "minority_ratio": float(num_minority / num_train),
        },
        "metrics": {
            "auroc_mean": float(auroc_mean),
            "auroc_std": float(auroc_std),
            "per_feature_auroc": {k: float(v) for k, v in per_feature_auroc.items()},
        },
        "gate": {
            "threshold": config.auroc_threshold,
            "achieved": float(auroc_mean),
            "passed": bool(gate_passed),
            "result": gate_result,
        },
    }

    # Save results
    results_path = os.path.join(config.output_dir, "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {results_path}")

    # Save loss matrix and features for analysis
    np.save(os.path.join(config.output_dir, "loss_matrix.npy"), loss_matrix)
    np.save(os.path.join(config.output_dir, "features.npy"), features)
    np.save(os.path.join(config.output_dir, "minority_labels.npy"), minority_labels)
    print(f"Arrays saved to: {config.output_dir}")

    # Final summary
    print()
    print("=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"AUROC: {auroc_mean:.4f} ± {auroc_std:.4f}")
    print(f"Threshold: {config.auroc_threshold}")
    print(f"Gate Result: {gate_result}")
    print("=" * 60)
    print(f"End time: {datetime.now().isoformat()}")

    return results


if __name__ == "__main__":
    config = get_config()
    results = main(config)

    # Exit with appropriate code
    if results["gate"]["passed"]:
        sys.exit(0)
    else:
        sys.exit(1)
