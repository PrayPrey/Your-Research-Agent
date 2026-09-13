#!/usr/bin/env python3
"""Main experiment runner for H-E1: Runtime Error Prevalence.

This script measures the prevalence of runtime errors (with localizable stack traces)
in CodeLlama-7B-Instruct generated code on the MBPP benchmark.

Gate condition: runtime_error_prevalence CI lower bound >= 30%
"""

import argparse
import os
import sys
from datetime import datetime
from tqdm import tqdm

from config import ExperimentConfig
from data import load_mbpp_test
from model import CodeGenerator
from executor import execute_code, ErrorCategory
from evaluate import (
    calculate_prevalence,
    check_gate,
    save_results,
    generate_all_figures,
)


def run_experiment(config: ExperimentConfig) -> dict:
    """Run the full H-E1 experiment.

    Pipeline:
    1. Load MBPP test split (500 problems)
    2. Load CodeLlama-7B-Instruct model
    3. Generate code for all problems
    4. Execute generated code against tests
    5. Calculate prevalence with CI
    6. Save results and generate figures
    7. Check gate condition

    Args:
        config: Experiment configuration

    Returns:
        Metrics dict with prevalence and gate result
    """
    print("=" * 60)
    print("H-E1: Runtime Error Prevalence Experiment")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Model: {config.model_id}")
    print(f"Dataset: {config.dataset_name} (IDs {config.task_id_min}-{config.task_id_max})")
    print(f"Gate threshold: {config.gate_threshold * 100:.0f}%")
    print("=" * 60)

    # Step 1: Load dataset
    print("\n[1/6] Loading MBPP test set...")
    problems = load_mbpp_test(config)
    print(f"Loaded {len(problems)} problems")

    # Step 2: Load model
    print("\n[2/6] Loading model...")
    generator = CodeGenerator(config)
    generator.load()

    # Step 3: Generate code
    print("\n[3/6] Generating code for all problems...")
    generated_codes = generator.generate_batch(problems)

    # Step 4: Execute and categorize
    print("\n[4/6] Executing generated code...")
    results = []
    for i, (problem, code) in enumerate(tqdm(
        zip(problems, generated_codes),
        total=len(problems),
        desc="Executing"
    )):
        category, stderr = execute_code(
            code,
            problem["test_list"],
            timeout=config.execution_timeout
        )
        results.append({
            "task_id": problem["task_id"],
            "category": category.value,
            "stderr": stderr,
            "generated_code": code,
        })

    # Step 5: Calculate metrics
    print("\n[5/6] Calculating prevalence metrics...")
    metrics = calculate_prevalence(results, config)
    gate_passed = check_gate(metrics, config.gate_threshold)
    metrics["gate_passed"] = gate_passed
    metrics["gate_threshold"] = config.gate_threshold
    metrics["timestamp"] = datetime.now().isoformat()

    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total problems: {metrics['n_total']}")
    print(f"Pass rate: {metrics['pass_rate'] * 100:.1f}% ({metrics['n_pass']}/{metrics['n_total']})")
    print(f"Total failures: {metrics['n_failures']}")
    print(f"  - Runtime errors: {metrics['n_runtime']}")
    print(f"  - Wrong output: {metrics['n_wrong']}")
    print(f"  - Syntax errors: {metrics['n_syntax']}")
    print(f"  - Timeouts: {metrics['n_timeout']}")
    print("-" * 60)
    print(f"Runtime Error Prevalence: {metrics['prevalence'] * 100:.1f}%")
    print(f"95% Wilson CI: [{metrics['ci_lower'] * 100:.1f}%, {metrics['ci_upper'] * 100:.1f}%]")
    print("-" * 60)

    # Step 6: Save results and generate figures
    print("\n[6/6] Saving results and generating figures...")
    save_results(results, metrics, config)
    generate_all_figures(results, metrics, config)

    # Gate verdict
    print("\n" + "=" * 60)
    if gate_passed:
        print("GATE RESULT: PASS")
        print(f"CI lower bound ({metrics['ci_lower'] * 100:.1f}%) >= threshold ({config.gate_threshold * 100:.0f}%)")
    else:
        print("GATE RESULT: FAIL")
        print(f"CI lower bound ({metrics['ci_lower'] * 100:.1f}%) < threshold ({config.gate_threshold * 100:.0f}%)")
    print("=" * 60)
    print(f"End time: {datetime.now().isoformat()}")

    return metrics


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="H-E1: Measure runtime error prevalence in LLM-generated code"
    )
    parser.add_argument(
        "--gpu", type=int, default=None,
        help="GPU device ID to use (default: auto)"
    )
    parser.add_argument(
        "--results-dir", type=str, default="results",
        help="Directory to save results"
    )
    args = parser.parse_args()

    # Set GPU if specified
    if args.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
        print(f"Using GPU {args.gpu}")

    # Create config
    config = ExperimentConfig(
        results_dir=args.results_dir,
        figures_dir=f"{args.results_dir}/figures",
        output_json=f"{args.results_dir}/execution_results.json",
        output_metrics=f"{args.results_dir}/metrics.yaml",
    )

    # Run experiment
    metrics = run_experiment(config)

    # Exit code based on gate
    sys.exit(0 if metrics["gate_passed"] else 1)


if __name__ == "__main__":
    main()
