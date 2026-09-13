"""Main experiment runner for H-M1."""
import os
import sys
import json
import torch

from config import HM1Config, set_seed
from train import run_training
from evaluate import run_evaluation


def main():
    cfg = HM1Config()
    set_seed(cfg.seed)

    os.makedirs(cfg.output_dir, exist_ok=True)

    print("=" * 60)
    print("H-M1: RLHF Reward Model Smoothing Experiment")
    print("=" * 60)
    print(f"Base model: {cfg.base_model}")
    print(f"Output dir: {cfg.output_dir}")
    print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    print()

    # Phase 1: Training
    print("Phase 1: Training reward model...")
    checkpoint_path = run_training(cfg)

    # Phase 2: Evaluation
    print("\nPhase 2: Running smoothness evaluation...")
    results = run_evaluation(cfg, checkpoint_path)

    # Summary
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print(f"Gradient smoothness: {'PASS' if results['pass']['gradient'] else 'FAIL'}")
    print(f"  Mean gradient norm: {results['gradient']['mean_gradient_norm']:.4f} < {cfg.threshold_gradient_norm}")
    print(f"Distribution continuity: {'PASS' if results['pass']['distribution'] else 'FAIL'}")
    print(f"  Bimodality coefficient: {results['distribution']['bimodality_coefficient']:.4f} < {cfg.threshold_bimodality}")
    print(f"Interpolation smoothness: {'PASS' if results['pass']['interpolation'] else 'FAIL'}")
    print(f"  Mean interpolation error: {results['interpolation']['mean_interpolation_error']:.4f} < {cfg.threshold_interp_error}")
    print()
    print(f"OVERALL: {'PASS' if results['overall_pass'] else 'FAIL'}")
    print("=" * 60)

    return 0 if results["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
