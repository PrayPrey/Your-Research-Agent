#!/usr/bin/env python3
"""Main experiment runner for H-M4: Task-Dependent Transformation Emergence"""

import os
import sys
import json
import torch
import argparse
from datetime import datetime

H_M4_CODE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H_M4_CODE)

from config import (
    BENCHMARKS, TRAIN_CONFIG, SHARPNESS_CONFIG, RANK_CONFIG, GATE_THRESHOLD,
    CHECKPOINTS_DIR, FIGURES_DIR, H_M4_DIR
)
from model import load_tokenizer
from data import load_benchmark_suite
from train import run_all_training
from evaluate import build_results_table
from correlate import analyze_correlation
from visualize import generate_all_figures


def main():
    parser = argparse.ArgumentParser(description="H-M4 Experiment: Task-Dependent Transformation Emergence")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--tasks", nargs="+", default=None, help="Tasks to run (default: all 4)")
    parser.add_argument("--skip-training", action="store_true", help="Skip training, load from checkpoints")
    args = parser.parse_args()

    torch.manual_seed(args.seed)

    os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"H-M4: Task-Dependent Transformation Emergence")
    print(f"{'='*60}")
    print(f"Seed: {args.seed}")
    print(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")

    tokenizer = load_tokenizer()
    print(f"Tokenizer loaded: {tokenizer.__class__.__name__}")

    print(f"\n{'='*40}")
    print("Loading benchmark suite...")
    print(f"{'='*40}")

    benchmark_suite = load_benchmark_suite(tokenizer, max_length=TRAIN_CONFIG["max_length"], batch_size=TRAIN_CONFIG["batch_size"])

    if args.tasks:
        benchmark_suite = {k: v for k, v in benchmark_suite.items() if k in args.tasks}

    if len(benchmark_suite) < 2:
        print("Error: Need at least 2 benchmarks for correlation analysis")
        sys.exit(1)

    print(f"\n{'='*40}")
    print("Training phase (8 runs: 2 arch x 4 tasks)")
    print(f"{'='*40}")

    train_config = TRAIN_CONFIG.copy()
    train_config["seed"] = args.seed

    training_results = run_all_training(tokenizer, benchmark_suite, train_config)

    successful_runs = sum(1 for v in training_results.values() if v is not None)
    print(f"\nSuccessful training runs: {successful_runs}/{len(training_results)}")

    print(f"\n{'='*40}")
    print("Evaluation phase")
    print(f"{'='*40}")

    results_table = build_results_table(training_results, benchmark_suite)

    if len(results_table) < 2:
        print("Error: Need at least 2 task results for correlation")
        sys.exit(1)

    print(f"\n{'='*40}")
    print("Correlation analysis")
    print(f"{'='*40}")

    correlation_result = analyze_correlation(results_table)

    primary = correlation_result["primary"]
    print(f"\nPrimary Gate (density vs accuracy_delta):")
    print(f"  Spearman rho: {primary['rho']:.4f}")
    print(f"  p-value: {primary['p_value']:.6f}")
    print(f"  Monotonic: {primary['is_monotonic']}")
    print(f"  Gate pass (|rho| > 0.7 and p < 0.01): {primary['gate_pass']}")

    print(f"\nAblation correlations:")
    for ablation_name, ablation_result in correlation_result["ablations"].items():
        print(f"  {ablation_name}: rho={ablation_result['rho']:.4f}, p={ablation_result['p_value']:.4f}")

    print(f"\n{'='*40}")
    print("Generating figures...")
    print(f"{'='*40}")

    figures = generate_all_figures(results_table, correlation_result)

    print(f"\n{'='*60}")
    print("EXPERIMENT RESULTS SUMMARY")
    print(f"{'='*60}")

    print(f"\nTask-Level Results (sorted by density):")
    sorted_tasks = sorted(results_table.keys(), key=lambda t: results_table[t]["density"])
    for task in sorted_tasks:
        r = results_table[task]
        print(f"\n  {task.upper()} (density={r['density']}):")
        print(f"    Transformer: acc={r['transformer']['accuracy']:.4f}, sharp={r['transformer']['sharpness']:.4f}, rank={r['transformer']['effective_rank']}")
        print(f"    Mamba:       acc={r['mamba']['accuracy']:.4f}, sharp={r['mamba']['sharpness']:.4f}, rank={r['mamba']['effective_rank']}")
        print(f"    Delta:       acc_Δ={r['delta']['accuracy_delta']:.4f}, sharp_Δ={r['delta']['sharpness_delta']:.4f}, rank_Δ={r['delta']['rank_delta']}")

    print(f"\n{'='*40}")
    print("GATE RESULT")
    print(f"{'='*40}")
    gate_result = "PASS" if primary["gate_pass"] else "FAIL"
    print(f"  MUST_WORK Gate: {gate_result}")
    print(f"  Spearman rho: {primary['rho']:.4f} (threshold: ±0.7)")
    print(f"  p-value: {primary['p_value']:.6f} (threshold: 0.01)")

    experiment_results = {
        "hypothesis_id": "h-m4",
        "hypothesis_type": "MECHANISM",
        "timestamp": datetime.now().isoformat(),
        "seed": args.seed,
        "gate": {
            "type": "MUST_WORK",
            "metric": "spearman_rho",
            "rho_threshold": GATE_THRESHOLD["min_spearman_rho"],
            "p_threshold": GATE_THRESHOLD["max_p_value"],
            "value": float(primary["rho"]),
            "p_value": float(primary["p_value"]),
            "is_monotonic": primary["is_monotonic"],
            "satisfied": bool(primary["gate_pass"]),
            "result": gate_result,
        },
        "primary_metrics": {
            "spearman_rho": float(primary["rho"]),
            "p_value": float(primary["p_value"]) if not (primary["p_value"] != primary["p_value"]) else None,
            "is_monotonic": primary["is_monotonic"],
        },
        "ablations": {
            name: {
                "rho": float(r["rho"]),
                "p_value": float(r["p_value"]) if not (r["p_value"] != r["p_value"]) else None,
            }
            for name, r in correlation_result["ablations"].items()
        },
        "task_results": {
            task: {
                "density": float(r["density"]),
                "transformer": {
                    "accuracy": float(r["transformer"]["accuracy"]),
                    "sharpness": float(r["transformer"]["sharpness"]),
                    "effective_rank": int(r["transformer"]["effective_rank"]),
                },
                "mamba": {
                    "accuracy": float(r["mamba"]["accuracy"]),
                    "sharpness": float(r["mamba"]["sharpness"]),
                    "effective_rank": int(r["mamba"]["effective_rank"]),
                },
                "delta": {
                    "accuracy_delta": float(r["delta"]["accuracy_delta"]),
                    "sharpness_delta": float(r["delta"]["sharpness_delta"]),
                    "rank_delta": int(r["delta"]["rank_delta"]),
                },
                "loss_curves": {
                    "transformer": [float(x) for x in r["loss_curves"]["transformer"]],
                    "mamba": [float(x) for x in r["loss_curves"]["mamba"]],
                },
            }
            for task, r in results_table.items()
        },
        "figures": figures,
        "config": {
            "train_config": TRAIN_CONFIG,
            "sharpness_config": SHARPNESS_CONFIG,
            "rank_config": RANK_CONFIG,
            "gate_threshold": GATE_THRESHOLD,
            "benchmarks": list(benchmark_suite.keys()),
        },
    }

    results_path = os.path.join(H_M4_DIR, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(experiment_results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    return experiment_results


if __name__ == "__main__":
    main()
