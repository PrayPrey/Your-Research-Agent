#!/usr/bin/env python
"""Main experiment runner for H-E1: Training×Refinement Interaction."""
import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from data import load_humaneval_plus, get_training_data
from model import load_base_model, wrap_lora
from train import run_all_conditions
from evaluate import run_2x2_eval, interaction_effect, save_results
from visualize import generate_all_figures


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def main():
    parser = argparse.ArgumentParser(description="H-E1: Training×Refinement Interaction")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ce-epochs", type=int, default=10)
    parser.add_argument("--rl-epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--smoke-test", action="store_true", help="Quick smoke test (1 epoch, subset)")
    args = parser.parse_args()

    print("="*60)
    print("H-E1: Training×Refinement Interaction Experiment")
    print("="*60)
    print(f"Start time: {datetime.now().isoformat()}")

    cfg = Config(
        seed=args.seed,
        ce_epochs=1 if args.smoke_test else args.ce_epochs,
        rl_epochs=1 if args.smoke_test else args.rl_epochs,
        batch_size=args.batch_size,
    )

    set_seed(cfg.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # Load data
    print("\n[1/4] Loading HumanEval+ dataset...")
    problems = load_humaneval_plus(cfg)
    train_data = get_training_data(problems)
    print(f"Loaded {len(train_data)} problems")

    if args.smoke_test:
        train_data = train_data[:10]
        problems = {k: v for i, (k, v) in enumerate(problems.items()) if i < 10}
        print(f"[SMOKE TEST] Using subset: {len(train_data)} problems")

    # Train all conditions
    print("\n[2/4] Training models...")
    models = run_all_conditions(train_data, cfg)

    # Evaluate 2x2
    print("\n[3/4] Running 2x2 evaluation...")
    results = run_2x2_eval(models, problems, cfg)

    # Compute interaction
    interaction = interaction_effect(results)
    print(f"\nInteraction effect: {interaction:+.4f}")
    print(f"Gate PASS: {interaction > 0}")

    # Save results
    print("\n[4/4] Saving results and figures...")
    save_results(results, interaction, cfg)
    figures = generate_all_figures(results, cfg)
    print(f"Figures saved: {[str(f) for f in figures]}")

    # Summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    for cond, val in results.items():
        print(f"  {cond}: {val:.4f}")
    print(f"\n  Interaction: {interaction:+.4f}")
    print(f"  Gate: {'PASS' if interaction > 0 else 'FAIL'}")
    print(f"\nEnd time: {datetime.now().isoformat()}")
    print("="*60)

    return interaction > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
