"""EVAF Pipeline orchestration for H-E1."""

import os
import sys
import json
import time
from datetime import datetime
from tqdm import tqdm

from config import CONFIG
from data import get_all_problems
from model import BaselineModel, FeedbackModel
from gating import run_unit_tests, evaf_gate
from metrics import compute_metrics
from visualize import plot_gate_metrics, plot_accept_distribution, plot_rejection_breakdown


def filter_failing(problems: list[dict], baseline: BaselineModel) -> list[dict]:
    """Generate baseline solutions and filter to failing problems."""
    failing = []
    print(f"Generating baseline solutions for {len(problems)} problems...")

    for p in tqdm(problems, desc="Baseline generation"):
        generated = baseline.generate(p["prompt"])
        p["generated_code"] = generated

        result = run_unit_tests(generated, p["test"], p["entry_point"])
        if not result["all_passed"]:
            failing.append(p)

    print(f"Found {len(failing)}/{len(problems)} failing problems")
    return failing


def run_pipeline(problems: list[dict], baseline: BaselineModel, feedback: FeedbackModel) -> list[dict]:
    """Full EVAF pipeline."""
    failing = filter_failing(problems, baseline)

    if not failing:
        print("No failing problems found - baseline solved all!")
        return []

    results = []
    print(f"\nRunning EVAF gating on {len(failing)} failing problems...")

    for p in tqdm(failing, desc="EVAF gating"):
        r = evaf_gate(p, p["generated_code"], feedback)
        r["task_id"] = p["task_id"]
        results.append(r)

    return results


def save_results(results: list[dict], metrics: dict, out_dir: str) -> None:
    """Save results and metrics to JSON files."""
    os.makedirs(out_dir, exist_ok=True)

    results_path = os.path.join(out_dir, "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved results to {results_path}")

    metrics_path = os.path.join(out_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {metrics_path}")


def main():
    """Main entry point for EVAF H-E1 experiment."""
    start_time = time.time()
    timestamp = datetime.now().isoformat()
    print(f"EVAF H-E1 Experiment Started: {timestamp}")
    print("=" * 60)

    os.makedirs(CONFIG["results_dir"], exist_ok=True)
    os.makedirs(CONFIG["figures_dir"], exist_ok=True)

    print("\n[1/5] Loading HumanEval dataset...")
    problems = get_all_problems()
    print(f"Loaded {len(problems)} problems")

    print("\n[2/5] Loading baseline model (CodeT5-770M)...")
    baseline = BaselineModel()

    print("\n[3/5] Loading feedback model (CodeLlama-7b-Instruct)...")
    feedback = FeedbackModel()

    print("\n[4/5] Running EVAF pipeline...")
    results = run_pipeline(problems, baseline, feedback)

    print("\n[5/5] Computing metrics and generating figures...")
    metrics = compute_metrics(results)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total failing problems: {metrics['total_problems']}")
    print(f"Accepted suggestions:   {metrics['accepted_count']}")
    print(f"Accept rate:            {metrics['accept_rate']*100:.1f}%")
    print(f"Coverage:               {metrics['coverage']*100:.1f}%")
    print(f"Rejection breakdown:    {metrics['rejection_breakdown']}")

    accept_rate = metrics["accept_rate"] * 100
    if 20 <= accept_rate <= 60:
        gate_result = "PASS"
        print(f"\n✓ GATE: PASS (accept rate {accept_rate:.1f}% is within 20-60% target)")
    elif accept_rate < 10:
        gate_result = "FAIL"
        print(f"\n✗ GATE: FAIL (accept rate {accept_rate:.1f}% < 10% - EVAF not viable)")
    elif accept_rate > 90:
        gate_result = "FAIL"
        print(f"\n✗ GATE: FAIL (accept rate {accept_rate:.1f}% > 90% - gating unnecessary)")
    else:
        gate_result = "MARGINAL"
        print(f"\n~ GATE: MARGINAL (accept rate {accept_rate:.1f}% outside 20-60% target)")

    metrics["gate_result"] = gate_result
    metrics["timestamp"] = timestamp

    save_results(results, metrics, CONFIG["results_dir"])

    print("\nGenerating figures...")
    plot_gate_metrics(metrics, os.path.join(CONFIG["figures_dir"], "gate_metrics.png"))
    plot_accept_distribution(results, os.path.join(CONFIG["figures_dir"], "accept_distribution.png"))
    plot_rejection_breakdown(metrics, os.path.join(CONFIG["figures_dir"], "rejection_breakdown.png"))
    print(f"Figures saved to {CONFIG['figures_dir']}")

    elapsed = time.time() - start_time
    print(f"\nExperiment completed in {elapsed/60:.1f} minutes")
    print("=" * 60)

    return metrics


if __name__ == "__main__":
    main()
