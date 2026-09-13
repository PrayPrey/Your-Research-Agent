#!/usr/bin/env python3
"""
H-E1 Main Experiment Runner
FGO vs Standard PPO 2x3 Factorial Experiment

Usage:
    python run_experiment.py                    # Full experiment
    python run_experiment.py --poc              # PoC mode (reduced scale)
    python run_experiment.py --eval-only        # Evaluation only
"""

import os
import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config, CONDITIONS
from train import run_factorial_experiment
from evaluate import evaluate_all_conditions
from visualize import generate_all_figures


def parse_args():
    parser = argparse.ArgumentParser(description="H-E1 FGO Experiment")
    parser.add_argument("--poc", action="store_true", help="PoC mode (reduced episodes)")
    parser.add_argument("--eval-only", action="store_true", help="Run evaluation only")
    parser.add_argument("--output-dir", default="outputs", help="Output directory")
    parser.add_argument("--episodes", type=int, default=None, help="Override episodes")
    parser.add_argument("--seed", type=int, default=1, help="Random seed")
    return parser.parse_args()


def main():
    args = parse_args()

    cfg = Config()
    cfg.seed = args.seed

    if args.poc:
        cfg.episodes = 100
        cfg.checkpoint_every = 50
        print("PoC MODE: Reduced to 100 episodes")

    if args.episodes:
        cfg.episodes = args.episodes

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    results_path = os.path.join(output_dir, "factorial_results.json")
    eval_path = os.path.join(output_dir, "evaluation_results.json")
    figures_dir = os.path.join(output_dir, "figures")

    if not args.eval_only:
        print("\n" + "=" * 70)
        print("H-E1: FGO vs Standard PPO - 2x3 Factorial Experiment")
        print("=" * 70)
        print(f"Episodes: {cfg.episodes}")
        print(f"Model: {cfg.model_id}")
        print(f"Seed: {cfg.seed}")
        print(f"Output: {output_dir}")
        print("=" * 70 + "\n")

        train_results = run_factorial_experiment(cfg, output_dir)
        print(f"\nTraining complete! Results: {results_path}")

    if os.path.exists(results_path) or args.eval_only:
        print("\n" + "=" * 70)
        print("EVALUATION")
        print("=" * 70 + "\n")

        eval_results = evaluate_all_conditions(output_dir, eval_path)
        print(f"\nEvaluation complete! Results: {eval_path}")

        print("\n" + "=" * 70)
        print("GENERATING FIGURES")
        print("=" * 70 + "\n")

        generate_all_figures(results_path if os.path.exists(results_path) else eval_path, figures_dir)

        print("\n" + "=" * 70)
        print("GATE CHECK: MUST_WORK")
        print("=" * 70)

        gate_passed = True
        for feedback_type in ["compile", "test", "combined"]:
            std_cond = f"standard_{feedback_type}"
            fgo_cond = f"fgo_{feedback_type}"

            if std_cond in eval_results and fgo_cond in eval_results:
                std_pass1 = eval_results[std_cond]["humaneval"]["pass@1"]
                fgo_pass1 = eval_results[fgo_cond]["humaneval"]["pass@1"]
                check = "PASS" if fgo_pass1 > std_pass1 else "FAIL"
                if fgo_pass1 <= std_pass1:
                    gate_passed = False
                print(f" {feedback_type.capitalize()}: FGO={fgo_pass1:.3f} vs Std={std_pass1:.3f} -> {check}")

        print("\n" + "=" * 70)
        print(f"GATE RESULT: {'PASS' if gate_passed else 'FAIL'}")
        print("=" * 70 + "\n")

        final_results = {
            "hypothesis_id": "h-e1",
            "gate_type": "MUST_WORK",
            "gate_passed": gate_passed,
            "timestamp": datetime.now().isoformat(),
            "evaluation_results": eval_results,
        }

        with open(os.path.join(output_dir, "experiment_results.json"), "w") as f:
            json.dump(final_results, f, indent=2)

        print("EXPERIMENT COMPLETE")

    return 0


if __name__ == "__main__":
    sys.exit(main())
