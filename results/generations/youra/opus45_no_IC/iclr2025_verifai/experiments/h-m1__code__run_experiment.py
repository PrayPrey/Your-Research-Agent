#!/usr/bin/env python
import json
import os
import sys
from datetime import datetime

from config import ExperimentConfig, setup_experiment
from data_loader import load_humaneval_problems
from generators import BaselineGenerator, ConstrainedGenerator
from evaluate import evaluate_condition
from visualize import plot_error_rate_comparison, save_summary_table

def main():
    config = ExperimentConfig()
    setup_experiment(config)

    print(f"[{datetime.now()}] Loading HumanEval dataset...")
    problems = load_humaneval_problems(config.dataset_id)
    print(f"Loaded {len(problems)} problems")

    baseline_results = {}
    constrained_results = {}

    baseline_path = os.path.join(config.output_dir, "baseline_samples.json")
    constrained_path = os.path.join(config.output_dir, "constrained_samples.json")

    if os.path.exists(baseline_path):
        print(f"Loading cached baseline results from {baseline_path}")
        with open(baseline_path) as f:
            baseline_results = json.load(f)
    else:
        print(f"[{datetime.now()}] Initializing Baseline Generator...")
        baseline_gen = BaselineGenerator(config.model_id, config.device, config.seed)

        print(f"[{datetime.now()}] Running baseline generation ({len(problems)} problems x {config.num_samples} samples)...")
        for i, prob in enumerate(problems):
            baseline_results[prob["task_id"]] = baseline_gen.generate(
                prob["prompt"], config.num_samples, config.temperature, config.max_new_tokens
            )
            if (i + 1) % 20 == 0:
                print(f"  Baseline progress: {i+1}/{len(problems)}")
                with open(baseline_path, "w") as f:
                    json.dump(baseline_results, f)

        with open(baseline_path, "w") as f:
            json.dump(baseline_results, f)
        print(f"Saved baseline results to {baseline_path}")

        del baseline_gen
        import torch
        torch.cuda.empty_cache()

    if os.path.exists(constrained_path):
        print(f"Loading cached constrained results from {constrained_path}")
        with open(constrained_path) as f:
            constrained_results = json.load(f)
    else:
        print(f"[{datetime.now()}] Initializing Constrained Generator (SynCode)...")
        constrained_gen = ConstrainedGenerator(
            config.model_id, config.grammar, config.device, config.seed,
            config.temperature, config.max_new_tokens
        )

        print(f"[{datetime.now()}] Running constrained generation ({len(problems)} problems x {config.num_samples} samples)...")
        for i, prob in enumerate(problems):
            constrained_results[prob["task_id"]] = constrained_gen.generate(
                prob["prompt"], config.num_samples, config.temperature, config.max_new_tokens
            )
            if (i + 1) % 20 == 0:
                print(f"  Constrained progress: {i+1}/{len(problems)}")
                with open(constrained_path, "w") as f:
                    json.dump(constrained_results, f)

        with open(constrained_path, "w") as f:
            json.dump(constrained_results, f)
        print(f"Saved constrained results to {constrained_path}")

    print(f"\n[{datetime.now()}] Evaluating results...")
    baseline_stats = evaluate_condition(baseline_results)
    constrained_stats = evaluate_condition(constrained_results)

    print(f"\n=== RESULTS ===")
    print(f"Baseline error rate:     {baseline_stats['error_rate']*100:.2f}% ({baseline_stats['n_errors']}/{baseline_stats['n_total']})")
    print(f"Constrained error rate:  {constrained_stats['error_rate']*100:.2f}% ({constrained_stats['n_errors']}/{constrained_stats['n_total']})")

    gate_pass = constrained_stats["error_rate"] < baseline_stats["error_rate"]
    print(f"\n=== GATE CHECK (MUST_WORK) ===")
    print(f"Condition: constrained_error_rate < baseline_error_rate")
    print(f"Result: {'PASS' if gate_pass else 'FAIL'}")

    print(f"\n[{datetime.now()}] Generating visualizations...")
    plot_error_rate_comparison(
        baseline_stats["error_rate"],
        constrained_stats["error_rate"],
        os.path.join(config.figures_dir, "error_rate_comparison.png")
    )
    save_summary_table(
        baseline_stats,
        constrained_stats,
        os.path.join(config.figures_dir, "summary.md")
    )

    results = {
        "hypothesis_id": "h-m1",
        "timestamp": datetime.now().isoformat(),
        "baseline": baseline_stats,
        "constrained": constrained_stats,
        "gate": {
            "type": "MUST_WORK",
            "condition": "constrained_error_rate < baseline_error_rate",
            "satisfied": gate_pass,
            "verdict": "PASS" if gate_pass else "FAIL"
        },
        "config": {
            "model_id": config.model_id,
            "num_samples": config.num_samples,
            "temperature": config.temperature,
            "seed": config.seed
        }
    }

    results_path = os.path.join(config.output_dir, "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved results to {results_path}")

    return 0 if gate_pass else 1

if __name__ == "__main__":
    sys.exit(main())
