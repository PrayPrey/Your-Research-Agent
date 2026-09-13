"""
Main Experiment Runner for h-e1
Executes full experiment matrix: 4 conditions × 2 scales × 5 seeds
"""

import os
import sys
import argparse
import json
import torch
import numpy as np
from datetime import datetime
from pathlib import Path

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    MODEL_CONFIGS, TRAINING_CONFIG, DIVERSITY_SCORES,
    EXPERIMENT_MATRIX, CHECKPOINT_PERCENTAGES, SEEDS
)
from models.gpt2_model import create_model
from train import train_model
from evaluate import evaluate_model


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)


def run_single_experiment(condition: str, scale: str, seed: int, args):
    """
    Run single experiment with specified configuration.

    Args:
        condition: One of ["static", "diversity_ranked", "reversed", "shuffled"]
        scale: "1B" or "7B"
        seed: Random seed
        args: Command-line arguments
    """
    print("=" * 80)
    print(f"EXPERIMENT: {condition} | {scale} | seed={seed}")
    print("=" * 80)

    # Set seed
    set_seed(seed)

    # Create output directory
    exp_dir = Path(args.output_dir) / f"{condition}_{scale}_seed{seed}"
    exp_dir.mkdir(parents=True, exist_ok=True)

    # Save experiment config
    exp_config = {
        "condition": condition,
        "scale": scale,
        "seed": seed,
        "diversity_scores": DIVERSITY_SCORES,
        "model_config": MODEL_CONFIGS[scale],
        "training_config": TRAINING_CONFIG[scale],
        "started_at": datetime.now().isoformat()
    }

    with open(exp_dir / "config.json", "w") as f:
        json.dump(exp_config, f, indent=2)

    # Create model
    model = create_model(scale)

    # Move to GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    # Train model (simplified for PoC - uses smoke test mode)
    print(f"\nTraining {scale} model with {condition} curriculum...")
    train_results = train_model(
        model=model,
        condition=condition,
        scale=scale,
        seed=seed,
        output_dir=exp_dir,
        smoke_test=args.smoke_test
    )

    # Evaluate model
    print(f"\nEvaluating {scale} model...")
    eval_results = evaluate_model(
        model=model,
        output_dir=exp_dir,
        smoke_test=args.smoke_test
    )

    # Save results
    results = {
        "experiment_config": exp_config,
        "training_results": train_results,
        "evaluation_results": eval_results,
        "completed_at": datetime.now().isoformat()
    }

    with open(exp_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Experiment completed: {exp_dir}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Run h-e1 diversity curriculum experiments")
    parser.add_argument("--condition", type=str, default=None,
                       help="Specific condition to run (default: all)")
    parser.add_argument("--scale", type=str, default=None,
                       help="Specific scale to run: 1B or 7B (default: both)")
    parser.add_argument("--seed", type=int, default=None,
                       help="Specific seed to run (default: all 5 seeds)")
    parser.add_argument("--output_dir", type=str, default="./outputs",
                       help="Output directory for results")
    parser.add_argument("--smoke_test", action="store_true",
                       help="Run smoke test (1 epoch, small data) instead of full training")
    parser.add_argument("--gpu_id", type=int, default=0,
                       help="GPU device ID to use")

    args = parser.parse_args()

    # Set GPU
    if torch.cuda.is_available():
        torch.cuda.set_device(args.gpu_id)
        print(f"Using GPU {args.gpu_id}: {torch.cuda.get_device_name(args.gpu_id)}")
    else:
        print("WARNING: CUDA not available, using CPU (will be very slow)")

    # Filter experiment matrix based on arguments
    experiments_to_run = EXPERIMENT_MATRIX

    if args.condition:
        experiments_to_run = [e for e in experiments_to_run if e["condition"] == args.condition]

    if args.scale:
        experiments_to_run = [e for e in experiments_to_run if e["scale"] == args.scale]

    if args.seed is not None:
        experiments_to_run = [e for e in experiments_to_run if e["seed"] == args.seed]

    print(f"\n{'='*80}")
    print(f"EXPERIMENT MATRIX: {len(experiments_to_run)} experiments to run")
    print(f"{'='*80}\n")

    # Run experiments
    all_results = []
    for i, exp in enumerate(experiments_to_run, 1):
        print(f"\n[{i}/{len(experiments_to_run)}] Running experiment...")
        try:
            results = run_single_experiment(
                condition=exp["condition"],
                scale=exp["scale"],
                seed=exp["seed"],
                args=args
            )
            all_results.append(results)
        except Exception as e:
            print(f"❌ Experiment failed: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Aggregate results
    print(f"\n{'='*80}")
    print(f"ALL EXPERIMENTS COMPLETED")
    print(f"{'='*80}")
    print(f"Total experiments: {len(all_results)}/{len(experiments_to_run)}")

    # Save aggregate results
    aggregate_path = Path(args.output_dir) / "aggregate_results.json"
    with open(aggregate_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✅ Aggregate results saved: {aggregate_path}")


if __name__ == "__main__":
    main()
