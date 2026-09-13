#!/usr/bin/env python3
"""H-C1 Experiment: Execution Feedback vs AI-Critic, Complexity Effect.

Tests whether execution feedback advantage is larger on complex tasks (MBPP)
compared to simple tasks (HumanEval).
"""
import json
import os
import random
import sys
import time
from datetime import datetime

import torch

from config import CFG
from base.data_loader import load_humaneval, load_mbpp
from base.sandbox_executor import SandboxExecutor
from model_client import ModelClient
from evaluator import compare_feedback_mechanisms
from metrics import compute_complexity_effect
from visualize import (
    plot_exec_advantage_bar,
    plot_pass_at_1_grouped,
    plot_error_type_breakdown,
    plot_complexity_scatter,
)


def generate_initial_code(client: ModelClient, problem: dict) -> str:
    """Generate initial code solution for a problem."""
    prompt = f"""Write a Python function to solve the following problem.
Only provide the code, no explanation.

{problem['prompt']}
"""
    return client.generate(prompt)


def run_experiment():
    """Run full H-C1 experiment."""
    print("=" * 60)
    print("H-C1 EXPERIMENT: Execution Feedback vs AI-Critic")
    print("=" * 60)
    start_time = time.time()

    random.seed(CFG.seed)
    torch.manual_seed(CFG.seed)

    os.makedirs(CFG.results_dir, exist_ok=True)
    os.makedirs(CFG.figures_dir, exist_ok=True)

    print("\n[1/5] Loading datasets...")
    humaneval = load_humaneval()
    mbpp = load_mbpp()
    print(f"  HumanEval: {len(humaneval)} problems")
    print(f"  MBPP: {len(mbpp)} problems")

    print("\n[2/5] Loading model...")
    client = ModelClient()
    executor = SandboxExecutor(timeout_s=CFG.timeout_s, memory_mb=CFG.memory_mb)

    print("\n[3/5] Evaluating HumanEval problems...")
    humaneval_results = []
    for i, problem in enumerate(humaneval):
        if i % 20 == 0:
            print(f"  Progress: {i}/{len(humaneval)}")
        initial_code = generate_initial_code(client, problem)
        result = compare_feedback_mechanisms(client, executor, problem, initial_code)
        humaneval_results.append(result)
    print(f"  Completed: {len(humaneval_results)} HumanEval problems")

    print("\n[4/5] Evaluating MBPP problems...")
    mbpp_results = []
    for i, problem in enumerate(mbpp):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(mbpp)}")
        initial_code = generate_initial_code(client, problem)
        result = compare_feedback_mechanisms(client, executor, problem, initial_code)
        mbpp_results.append(result)
    print(f"  Completed: {len(mbpp_results)} MBPP problems")

    print("\n[5/5] Computing metrics and generating figures...")
    complexity_effect = compute_complexity_effect(humaneval_results, mbpp_results)

    all_results = humaneval_results + mbpp_results
    experiment_output = {
        "hypothesis_id": "h-c1",
        "hypothesis_type": "CONDITION",
        "statement": "The execution feedback advantage over AI-critic is larger on complex tasks (MBPP) compared to simple tasks (HumanEval).",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "seed": CFG.seed,
            "model_id": CFG.model_id,
            "temperature": CFG.temperature,
            "timeout_s": CFG.timeout_s,
        },
        "metrics": complexity_effect,
        "humaneval_results": humaneval_results,
        "mbpp_results": mbpp_results,
        "gate_result": "PASS" if complexity_effect["hypothesis_supported"] else "FAIL",
    }

    results_path = os.path.join(CFG.results_dir, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(experiment_output, f, indent=2)
    print(f"  Results saved: {results_path}")

    figures_base = CFG.figures_dir
    plot_exec_advantage_bar(complexity_effect, os.path.join(figures_base, "exec_advantage_bar.png"))
    plot_pass_at_1_grouped(humaneval_results, mbpp_results, os.path.join(figures_base, "pass_at_1_grouped.png"))
    plot_error_type_breakdown(all_results, os.path.join(figures_base, "error_type_breakdown.png"))
    plot_complexity_scatter(all_results, os.path.join(figures_base, "complexity_scatter.png"))

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"  Runtime: {elapsed/60:.1f} minutes")
    print(f"  HumanEval exec advantage: {complexity_effect['humaneval_exec_advantage']:.4f}")
    print(f"  MBPP exec advantage: {complexity_effect['mbpp_exec_advantage']:.4f}")
    print(f"  Complexity effect: {complexity_effect['complexity_effect']:.4f}")
    print(f"  Hypothesis supported: {complexity_effect['hypothesis_supported']}")
    print(f"  Gate result: {experiment_output['gate_result']}")

    return experiment_output


if __name__ == "__main__":
    results = run_experiment()
    sys.exit(0 if results["gate_result"] == "PASS" else 1)
