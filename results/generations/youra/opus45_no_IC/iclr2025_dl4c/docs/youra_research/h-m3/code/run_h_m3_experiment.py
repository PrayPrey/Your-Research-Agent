#!/usr/bin/env python3
"""H-M3 Experiment: Convergence Efficiency Comparison (FGO vs Standard PPO)."""

import os
import sys
import json
import random
import argparse
import numpy as np
import torch
from datetime import datetime

from config import (
    DATA_CONFIG, TRAINING_CONFIG, CONVERGENCE_CONFIG,
    EXPERIMENT_CONFIG, GATE_THRESHOLDS, GATE_TYPE
)
from data_loader import load_problems, load_model_and_tokenizer
from convergence import measure_convergence_efficiency
from stats import aggregate_seeds, compute_gate_verdict, learning_curve_slope, sample_efficiency
from visualize import generate_all_figures, plot_learning_curve_comparison


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def run_experiment(args):
    """Run H-M3 convergence comparison experiment."""
    print("=" * 60)
    print("H-M3 Experiment: Dense Credit Assignment Convergence")
    print("=" * 60)

    output_dir = args.output_dir or EXPERIMENT_CONFIG["output_dir"]
    os.makedirs(output_dir, exist_ok=True)
    figures_dir = os.path.join(output_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)

    print(f"\n[1/5] Loading problems...")
    all_problems = load_problems(include_humaneval=True, include_mbpp=True)
    print(f"Loaded {len(all_problems)} problems")

    random.shuffle(all_problems)
    train_size = int(len(all_problems) * 0.7)
    train_problems = all_problems[:train_size]
    eval_problems = all_problems[train_size:]
    print(f"Train: {len(train_problems)}, Eval: {len(eval_problems)}")

    conditions = args.conditions or EXPERIMENT_CONFIG["conditions"]
    seeds = args.seeds or EXPERIMENT_CONFIG["seeds"]
    max_steps = args.max_steps or CONVERGENCE_CONFIG["max_steps"]
    eval_interval = args.eval_interval or CONVERGENCE_CONFIG["eval_interval"]
    target_pass1 = CONVERGENCE_CONFIG["target_pass1"]

    print(f"\n[2/5] Configuration:")
    print(f"  Conditions: {conditions}")
    print(f"  Seeds: {seeds}")
    print(f"  Max steps: {max_steps}")
    print(f"  Eval interval: {eval_interval}")
    print(f"  Target pass@1: {target_pass1}")

    results = {"standard": [], "fgo": []}

    print(f"\n[3/5] Running experiments...")
    for condition in conditions:
        for seed in seeds:
            print(f"\n{'='*40}")
            print(f"Condition: {condition.upper()}, Seed: {seed}")
            print(f"{'='*40}")

            set_seed(seed)

            print("Loading model...")
            model, tokenizer = load_model_and_tokenizer(
                model_name=DATA_CONFIG["model_name"],
                device=DATA_CONFIG["device"],
                dtype=DATA_CONFIG["dtype"]
            )

            fgo_enabled = (condition == "fgo")

            result = measure_convergence_efficiency(
                model=model,
                tokenizer=tokenizer,
                train_problems=train_problems,
                eval_problems=eval_problems,
                fgo_enabled=fgo_enabled,
                max_steps=max_steps,
                eval_interval=eval_interval,
                target_pass1=target_pass1,
                seed=seed,
                device=DATA_CONFIG["device"]
            )

            results[condition].append(result)

            print(f"\nResult: steps_to_target={result['steps_to_target']}, "
                  f"final_pass1={result['final_pass1']:.3f}")

            del model
            torch.cuda.empty_cache()

    print(f"\n[4/5] Computing statistics...")
    fgo_agg = aggregate_seeds(results["fgo"]) if results["fgo"] else {}
    std_agg = aggregate_seeds(results["standard"]) if results["standard"] else {}

    print(f"\nFGO: steps={fgo_agg.get('steps_to_target_mean', 'N/A'):.0f} ± "
          f"{fgo_agg.get('steps_to_target_std', 0):.0f}, "
          f"pass@1={fgo_agg.get('final_pass1_mean', 0):.3f} ± "
          f"{fgo_agg.get('final_pass1_std', 0):.3f}")
    print(f"Standard: steps={std_agg.get('steps_to_target_mean', 'N/A'):.0f} ± "
          f"{std_agg.get('steps_to_target_std', 0):.0f}, "
          f"pass@1={std_agg.get('final_pass1_mean', 0):.3f} ± "
          f"{std_agg.get('final_pass1_std', 0):.3f}")

    gate_verdict = {}
    if fgo_agg and std_agg:
        gate_verdict = compute_gate_verdict(fgo_agg, std_agg, GATE_THRESHOLDS["steps_to_target_ratio_max"])
        print(f"\n[GATE] {GATE_TYPE}: {'PASS' if gate_verdict['passed'] else 'FAIL'}")
        print(f"  Steps ratio: {gate_verdict['steps_ratio']:.2f} (threshold: <{GATE_THRESHOLDS['steps_to_target_ratio_max']})")
        print(f"  Faster convergence: {gate_verdict['criteria']['faster_convergence']}")
        print(f"  Higher final pass@1: {gate_verdict['criteria']['higher_final_pass1']}")

    print(f"\n[5/5] Generating figures...")
    try:
        generate_all_figures(results, figures_dir)
    except Exception as e:
        print(f"Warning: Figure generation failed: {e}")

    experiment_results = {
        "hypothesis": "H-M3",
        "statement": "Dense credit assignment enables faster and more precise policy learning",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "max_steps": max_steps,
            "eval_interval": eval_interval,
            "target_pass1": target_pass1,
            "conditions": conditions,
            "seeds": seeds,
        },
        "results": {
            "fgo": results["fgo"],
            "standard": results["standard"],
        },
        "aggregated": {
            "fgo": fgo_agg,
            "standard": std_agg,
        },
        "gate": gate_verdict,
        "figures": [
            "figures/learning_curve_comparison.png",
            "figures/steps_to_target.png",
        ]
    }

    results_path = os.path.join(output_dir, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(experiment_results, f, indent=2, default=str)
    print(f"\nResults saved: {results_path}")

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)

    return experiment_results


def main():
    parser = argparse.ArgumentParser(description="H-M3 Convergence Experiment")
    parser.add_argument("--output-dir", type=str, default=None)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--eval-interval", type=int, default=None)
    parser.add_argument("--conditions", nargs="+", default=None)
    parser.add_argument("--seeds", nargs="+", type=int, default=None)
    parser.add_argument("--quick", action="store_true", help="Quick PoC run")

    args = parser.parse_args()

    if args.quick:
        args.max_steps = args.max_steps or 100
        args.eval_interval = args.eval_interval or 25
        args.seeds = args.seeds or [42]

    run_experiment(args)


if __name__ == "__main__":
    main()
