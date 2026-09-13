"""Main experiment orchestration."""
import os
import json
import random
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, Any

from config import TRAINING_CONFIG, OUTPUT_CONFIG
from data import get_dataloaders
from model import StandardCNN
from train import train_model
from evaluate import evaluate_all_metrics
from visualize import plot_gate_metrics, plot_per_class_accuracy, plot_training_curves


def setup_environment(seed: int = 42) -> torch.device:
    """Set random seeds and determine device.

    Args:
        seed: Random seed for reproducibility

    Returns:
        torch.device ('cuda' or 'cpu')
    """
    # Set seeds
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        device = torch.device('cuda')
        print(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device('cpu')
        print("CUDA not available, using CPU (training will be slower)")

    return device


def save_checkpoint(model: nn.Module, save_path: str) -> None:
    """Save model checkpoint."""
    torch.save(model.state_dict(), save_path)
    print(f"Checkpoint saved to {save_path}")


def save_metrics(metrics: Dict[str, Any], save_path: str) -> None:
    """Save evaluation metrics to JSON."""
    with open(save_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {save_path}")


def run_experiment(augmentation_type: str, device: torch.device, save_dir: str):
    """Run full experiment for one condition.

    Args:
        augmentation_type: "baseline" or "rotation"
        device: cuda or cpu
        save_dir: Directory to save checkpoints and logs

    Returns:
        (trained_model, training_history, per_class_accuracy)
    """
    print(f"\n{'='*60}")
    print(f"Running {augmentation_type.upper()} experiment")
    print(f"{'='*60}\n")

    # Get dataloaders
    train_loader, test_loader = get_dataloaders(
        augmentation_type=augmentation_type,
        batch_size=TRAINING_CONFIG["batch_size"],
        num_workers=TRAINING_CONFIG["num_workers"],
        seed=TRAINING_CONFIG["seed"]
    )

    # Initialize model
    model = StandardCNN().to(device)

    # Train model
    history = train_model(
        model=model,
        train_loader=train_loader,
        test_loader=test_loader,
        device=device,
        max_epochs=TRAINING_CONFIG["epochs"],
        lr=TRAINING_CONFIG["lr"],
        patience=TRAINING_CONFIG["early_stopping_patience"]
    )

    # Save checkpoint
    checkpoint_path = os.path.join(OUTPUT_CONFIG["checkpoints_dir"], f"{augmentation_type}_model.pt")
    save_checkpoint(model, checkpoint_path)

    # Save training history
    log_path = os.path.join(OUTPUT_CONFIG["logs_dir"], f"{augmentation_type}_training.json")
    with open(log_path, 'w') as f:
        json.dump(history, f, indent=2)

    return model, history, test_loader


def main():
    """Main orchestration function."""
    # Setup
    device = setup_environment(seed=TRAINING_CONFIG["seed"])

    # Create directories
    os.makedirs(OUTPUT_CONFIG["checkpoints_dir"], exist_ok=True)
    os.makedirs(OUTPUT_CONFIG["logs_dir"], exist_ok=True)
    os.makedirs(OUTPUT_CONFIG["figures_dir"], exist_ok=True)
    os.makedirs(OUTPUT_CONFIG["output_dir"] + "/results", exist_ok=True)

    # Baseline experiment
    baseline_model, baseline_history, test_loader = run_experiment('baseline', device, OUTPUT_CONFIG["output_dir"])

    # Rotation experiment
    rotation_model, rotation_history, _ = run_experiment('rotation', device, OUTPUT_CONFIG["output_dir"])

    # Evaluate all metrics
    print(f"\n{'='*60}")
    print("EVALUATING METRICS")
    print(f"{'='*60}\n")

    metrics = evaluate_all_metrics(baseline_model, rotation_model, test_loader, device)

    # Print summary
    print(f"\nRESULTS SUMMARY:")
    print(f"  Baseline differential: {metrics['baseline_diff']:.4f}")
    print(f"  Rotation differential: {metrics['rotation_diff']:.4f}")
    print(f"  Success check: {metrics['success_check']}")

    # Generate visualizations
    print(f"\n{'='*60}")
    print("GENERATING VISUALIZATIONS")
    print(f"{'='*60}\n")

    plot_gate_metrics(
        metrics['baseline_diff'],
        metrics['rotation_diff'],
        os.path.join(OUTPUT_CONFIG["figures_dir"], "gate_metrics_comparison.png")
    )

    plot_per_class_accuracy(
        metrics['baseline_per_class'],
        metrics['rotation_per_class'],
        os.path.join(OUTPUT_CONFIG["figures_dir"], "per_class_accuracy.png")
    )

    plot_training_curves(
        baseline_history,
        rotation_history,
        os.path.join(OUTPUT_CONFIG["figures_dir"], "training_curves.png")
    )

    # Save final metrics
    results_path = os.path.join(OUTPUT_CONFIG["output_dir"], "results", OUTPUT_CONFIG["results_file"])
    save_metrics(metrics, results_path)

    # Save gate decision
    gate_decision = {
        "gate_type": "MUST_WORK",
        "status": metrics['success_check'],
        "baseline_differential": metrics['baseline_diff'],
        "rotation_differential": metrics['rotation_diff'],
        "threshold": 0.02
    }
    gate_path = os.path.join(OUTPUT_CONFIG["output_dir"], "results", OUTPUT_CONFIG["gate_file"])
    save_metrics(gate_decision, gate_path)

    print(f"\n{'='*60}")
    print("EXPERIMENT COMPLETE")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
