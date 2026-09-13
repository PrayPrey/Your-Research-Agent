#!/usr/bin/env python3
"""
Main entrypoint: Structured vs Raw error format comparison experiment.
Runs models x benchmarks x {structured, raw} and generates results + figures.
"""
import os
import sys
import json
import random
import torch
import numpy as np

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG
from evaluate import run_benchmark
from visualize import (
    plot_gate_comparison,
    plot_repair_success,
    plot_repair_iterations,
    plot_error_type_heatmap,
    plot_benchmark_comparison
)

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def main():
    set_seed(CONFIG["seed"])
    os.makedirs(CONFIG["figures_dir"], exist_ok=True)

    all_results = {}
    models = CONFIG["models"]
    benchmarks = CONFIG["benchmarks"]
    formats = [(True, "structured"), (False, "raw")]

    print("=" * 60)
    print("STRUCTURED vs RAW ERROR FORMAT COMPARISON")
    print("=" * 60)

    for model_name in models:
        for benchmark in benchmarks:
            for use_structured, fmt_name in formats:
                key = f"{model_name}|{benchmark}|{fmt_name}"
                print(f"\nRunning: {key}")

                try:
                    result = run_benchmark(model_name, benchmark, use_structured)
                    all_results[key] = result
                    print(f"  Pass@1: {result['pass_at_1']:.4f}")
                    print(f"  Repair Success: {result['repair_success_rate']:.4f}")
                except Exception as e:
                    print(f"  ERROR: {e}")
                    all_results[key] = {"error": str(e), "pass_at_1": 0}

    results_path = CONFIG["results_path"]
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    print("\nGenerating figures...")
    plot_gate_comparison(all_results)
    plot_repair_success(all_results)
    plot_repair_iterations(all_results)
    plot_error_type_heatmap(all_results)
    plot_benchmark_comparison(all_results)

    print("\n" + "=" * 60)
    print("POC GATE CHECK")
    print("=" * 60)

    structured_wins = 0
    total_combos = 0
    for model in models:
        for benchmark in benchmarks:
            s_key = f"{model}|{benchmark}|structured"
            r_key = f"{model}|{benchmark}|raw"
            s_pass = all_results.get(s_key, {}).get("pass_at_1", 0)
            r_pass = all_results.get(r_key, {}).get("pass_at_1", 0)
            if s_pass > r_pass:
                structured_wins += 1
            total_combos += 1
            print(f"  {model.split('/')[-1]}|{benchmark}: structured={s_pass:.4f} vs raw={r_pass:.4f} {'WIN' if s_pass > r_pass else ''}")

    print(f"\nStructured wins: {structured_wins}/{total_combos}")
    gate_pass = structured_wins >= 4
    print(f"PoC Gate: {'PASS' if gate_pass else 'FAIL'} (need >= 4/6 wins)")

    with open(CONFIG["results_path"].replace(".json", "_summary.txt"), "w") as f:
        f.write(f"Structured wins: {structured_wins}/{total_combos}\n")
        f.write(f"Gate: {'PASS' if gate_pass else 'FAIL'}\n")

    return gate_pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
