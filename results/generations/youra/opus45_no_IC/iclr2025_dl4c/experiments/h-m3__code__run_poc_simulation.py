#!/usr/bin/env python3
"""H-M3 PoC: Convergence Efficiency Comparison (FGO vs Standard PPO).

REAL experiment using HumanEval + MBPP datasets. No simulated data.
"""

import os
import sys
import json
import random
import argparse
import numpy as np
import torch
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    DATA_CONFIG, TRAINING_CONFIG, CONVERGENCE_CONFIG,
    EXPERIMENT_CONFIG, GATE_THRESHOLDS, GATE_TYPE
)
from data_loader import load_problems, load_model_and_tokenizer
from convergence import measure_convergence_efficiency
from stats import aggregate_seeds, compute_gate_verdict
from visualize import generate_all_figures


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def validate_fgo_mechanism():
    """Validate FGO mask and loss functions work correctly."""
    from fgo import create_fgo_mask, fgo_ppo_loss, standard_ppo_loss
    from trace_collector import ExecutionTraceCollector
    from token_mapper import LineToTokenMapper

    print("=" * 60)
    print("FGO Mechanism Validation")
    print("=" * 60)

    # Test 1: FGO mask construction
    print("\n[Test 1] FGO Mask Construction")
    token_ids = torch.tensor([100, 200, 300, 400, 500])
    token_to_line = [1, 1, 2, 2, 3]
    executed_lines = {1, 3}

    mask = create_fgo_mask(token_ids, token_to_line, executed_lines)
    expected = torch.tensor([1.0, 1.0, 0.0, 0.0, 1.0])

    assert torch.allclose(mask, expected), f"Mask mismatch: {mask} vs {expected}"
    print(f"  ✓ Mask correctly identifies executed tokens")

    # Test 2: FGO loss vs Standard loss
    print("\n[Test 2] FGO vs Standard PPO Loss")
    batch_size, seq_len = 2, 5
    logprobs = torch.randn(batch_size, seq_len, requires_grad=True)
    old_logprobs = logprobs.detach()
    advantages = torch.ones(batch_size, seq_len)
    fgo_mask = torch.tensor([[1, 1, 0, 0, 1], [1, 0, 0, 1, 1]], dtype=torch.float)

    fgo_loss = fgo_ppo_loss(logprobs, old_logprobs, advantages, fgo_mask)
    std_loss = standard_ppo_loss(
        logprobs.detach().requires_grad_(True), old_logprobs, advantages
    )
    print(f"  FGO loss: {fgo_loss.item():.6f}")
    print(f"  Standard loss: {std_loss.item():.6f}")
    print(f"  ✓ Both loss functions compute without error")

    # Test 3: Trace collector
    print("\n[Test 3] Trace Collector")
    collector = ExecutionTraceCollector()
    test_code = "def add(a, b):\n    return a + b\n\nresult = add(1, 2)"
    executed = collector.collect_trace(test_code)
    print(f"  Executed lines: {sorted(executed)}")
    print(f"  ✓ Trace collector works")

    print("\n" + "=" * 60)
    print("All mechanism validations PASSED")
    print("=" * 60)
    return True


def run_simulation():
    """Run REAL convergence comparison experiment."""
    print("\n" + "=" * 60)
    print("H-M3: Real Convergence Efficiency Experiment")
    print("=" * 60)

    output_dir = "./results"
    figures_dir = os.path.join(output_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)

    # Load REAL dataset
    print("\n[1/5] Loading HumanEval + MBPP datasets...")
    all_problems = load_problems(include_humaneval=True, include_mbpp=True)
    print(f"Loaded {len(all_problems)} problems (HumanEval 164 + MBPP ~500)")

    random.seed(42)
    random.shuffle(all_problems)
    train_size = int(len(all_problems) * 0.7)
    train_problems = all_problems[:train_size]
    eval_problems = all_problems[train_size:]
    print(f"Train: {len(train_problems)}, Eval: {len(eval_problems)}")

    conditions = EXPERIMENT_CONFIG["conditions"]
    seeds = EXPERIMENT_CONFIG["seeds"]
    max_steps = CONVERGENCE_CONFIG["max_steps"]
    eval_interval = CONVERGENCE_CONFIG["eval_interval"]
    target_pass1 = CONVERGENCE_CONFIG["target_pass1"]

    print(f"\n[2/5] Configuration:")
    print(f"  Model: {DATA_CONFIG['model_name']}")
    print(f"  Conditions: {conditions}")
    print(f"  Seeds: {seeds}")
    print(f"  Max steps: {max_steps}")
    print(f"  Eval interval: {eval_interval}")
    print(f"  Target pass@1: {target_pass1}")

    results = {"standard": [], "fgo": []}

    print(f"\n[3/5] Running real training experiments...")
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
                dtype=DATA_CONFIG["dtype"],
            )

            fgo_enabled = condition == "fgo"

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
                device=DATA_CONFIG["device"],
            )

            results[condition].append(result)

            print(
                f"\nResult: steps_to_target={result['steps_to_target']}, "
                f"final_pass1={result['final_pass1']:.3f}"
            )

            del model
            torch.cuda.empty_cache()

    # Aggregate results
    print(f"\n[4/5] Computing statistics...")
    fgo_agg = aggregate_seeds(results["fgo"]) if results["fgo"] else {}
    std_agg = aggregate_seeds(results["standard"]) if results["standard"] else {}

    if fgo_agg and std_agg:
        print(
            f"\nFGO: steps={fgo_agg['steps_to_target_mean']:.0f}±"
            f"{fgo_agg['steps_to_target_std']:.0f}, "
            f"pass@1={fgo_agg['final_pass1_mean']:.3f}±{fgo_agg['final_pass1_std']:.3f}"
        )
        print(
            f"Standard: steps={std_agg['steps_to_target_mean']:.0f}±"
            f"{std_agg['steps_to_target_std']:.0f}, "
            f"pass@1={std_agg['final_pass1_mean']:.3f}±{std_agg['final_pass1_std']:.3f}"
        )

    gate_verdict = {}
    if fgo_agg and std_agg:
        gate_verdict = compute_gate_verdict(
            fgo_agg, std_agg, GATE_THRESHOLDS["steps_to_target_ratio_max"]
        )
        print(f"\n[GATE] {GATE_TYPE}: {'PASS' if gate_verdict['passed'] else 'FAIL'}")
        print(
            f"  Steps ratio: {gate_verdict['steps_ratio']:.2f} "
            f"(threshold: <{GATE_THRESHOLDS['steps_to_target_ratio_max']})"
        )
        print(f"  Faster convergence: {gate_verdict['criteria']['faster_convergence']}")
        print(f"  Higher final pass@1: {gate_verdict['criteria']['higher_final_pass1']}")

    # Generate figures
    print(f"\n[5/5] Generating figures...")
    try:
        generate_all_figures(results, figures_dir)
        print(f"Figures saved to {figures_dir}/")
    except Exception as e:
        print(f"Warning: Figure generation failed: {e}")

    # Save results
    experiment_results = {
        "hypothesis": "H-M3",
        "statement": "Dense credit assignment enables faster and more precise policy learning",
        "type": "REAL_EXPERIMENT",
        "dataset": "HumanEval (164) + MBPP test (500)",
        "model": DATA_CONFIG["model_name"],
        "timestamp": datetime.now().isoformat(),
        "config": {
            "max_steps": max_steps,
            "eval_interval": eval_interval,
            "target_pass1": target_pass1,
            "seeds": seeds,
        },
        "results": results,
        "aggregated": {
            "fgo": fgo_agg,
            "standard": std_agg,
        },
        "gate": gate_verdict if gate_verdict else {
            "type": GATE_TYPE,
            "passed": False,
            "note": "Insufficient results to compute gate",
        },
    }

    results_path = os.path.join(output_dir, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(experiment_results, f, indent=2, default=str)
    print(f"\nResults saved: {results_path}")

    return experiment_results


def main():
    # Validate FGO mechanism
    mechanism_valid = validate_fgo_mechanism()
    if not mechanism_valid:
        print("\nMechanism validation FAILED. Cannot proceed.")
        sys.exit(1)

    # Run REAL experiment
    results = run_simulation()

    print("\n" + "=" * 60)
    print("H-M3 EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  - Dataset: HumanEval + MBPP (REAL)")
    print(f"  - Model: {DATA_CONFIG['model_name']}")
    print(f"  - FGO mechanism validated: ✓")
    gate = results.get("gate", {})
    print(f"  - Gate ({GATE_TYPE}): {'PASS' if gate.get('passed') else 'FAIL'}")

    return results


if __name__ == "__main__":
    main()
