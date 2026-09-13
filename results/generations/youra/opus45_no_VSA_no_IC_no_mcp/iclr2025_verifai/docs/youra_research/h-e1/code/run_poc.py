#!/usr/bin/env python3
"""
PoC experiment: subset evaluation for Phase 4 validation.
Runs CodeLlama-7B only on first 100 HumanEval+ problems to validate mechanism.
"""
import os
import sys
import json
import random
import torch
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG
from datasets import load_dataset
from repair_loop import repair_problem
from models import load_hf_model
from visualize import plot_gate_comparison, ensure_figures_dir

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def run_subset_experiment(model_name: str, benchmark: str, n_problems: int = 100):
    dataset_name = CONFIG["benchmark_datasets"].get(benchmark)
    ds = load_dataset(dataset_name, split="test")
    problems = [dict(row) for row in ds][:n_problems]
    print(f"Loaded {len(problems)} problems from {benchmark}")

    model_ref, tokenizer = load_hf_model(model_name)

    results_structured = []
    results_raw = []

    print(f"\nRunning STRUCTURED format...")
    for i, problem in enumerate(problems):
        result = repair_problem(model_ref, tokenizer, problem, use_structured=True)
        results_structured.append(result)
        if (i + 1) % 20 == 0:
            print(f"  Structured: {i+1}/{len(problems)} - pass_rate={sum(r['passed'] for r in results_structured)/(i+1):.3f}")

    print(f"\nRunning RAW format...")
    for i, problem in enumerate(problems):
        result = repair_problem(model_ref, tokenizer, problem, use_structured=False)
        results_raw.append(result)
        if (i + 1) % 20 == 0:
            print(f"  Raw: {i+1}/{len(problems)} - pass_rate={sum(r['passed'] for r in results_raw)/(i+1):.3f}")

    s_pass = sum(r["passed"] for r in results_structured) / len(results_structured)
    r_pass = sum(r["passed"] for r in results_raw) / len(results_raw)

    return {
        "structured": {"pass_at_1": s_pass, "problems": len(problems)},
        "raw": {"pass_at_1": r_pass, "problems": len(problems)},
        "model": model_name,
        "benchmark": benchmark,
        "structured_wins": s_pass > r_pass
    }

def main():
    set_seed(42)
    ensure_figures_dir()

    model = "codellama/CodeLlama-7b-Instruct-hf"
    benchmark = "humaneval"
    n_problems = 100

    print("=" * 60)
    print("POC EXPERIMENT: Structured vs Raw Error Format")
    print(f"Model: {model}")
    print(f"Benchmark: {benchmark} (first {n_problems} problems)")
    print("=" * 60)

    result = run_subset_experiment(model, benchmark, n_problems)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Structured Pass@1: {result['structured']['pass_at_1']:.4f}")
    print(f"Raw Pass@1: {result['raw']['pass_at_1']:.4f}")
    print(f"Structured wins: {result['structured_wins']}")

    all_results = {
        f"{model}|{benchmark}|structured": result["structured"],
        f"{model}|{benchmark}|raw": result["raw"],
    }

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/poc_results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    gate_pass = result["structured_wins"]
    print(f"\nPoC Gate: {'PASS' if gate_pass else 'FAIL'}")

    with open("outputs/poc_summary.txt", "w") as f:
        f.write(f"Model: {model}\n")
        f.write(f"Benchmark: {benchmark}\n")
        f.write(f"Problems: {n_problems}\n")
        f.write(f"Structured Pass@1: {result['structured']['pass_at_1']:.4f}\n")
        f.write(f"Raw Pass@1: {result['raw']['pass_at_1']:.4f}\n")
        f.write(f"Gate: {'PASS' if gate_pass else 'FAIL'}\n")

    return gate_pass

if __name__ == "__main__":
    success = main()
    print("\nEXPERIMENT COMPLETE")
    sys.exit(0 if success else 1)
