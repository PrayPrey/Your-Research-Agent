#!/usr/bin/env python3
"""H-M2 Experiment: Emergent-Capability Benchmark Creation Analysis."""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_pwc_datasets
from analysis import build_benchmark_records, compute_post2020_ratio, compute_creation_rate_acceleration, evaluate_hypothesis
from date_extractor import resolve_missing_dates
from visualize import plot_gate_metrics, plot_creation_timeline, plot_cumulative_curve, plot_type_distribution_by_year
from config import RunConfig, MIN_EMERGENT_BENCHMARKS


def main():
    start_time = time.time()
    config = RunConfig()

    script_dir = Path(__file__).parent
    results_dir = script_dir / "outputs"
    figures_dir = script_dir.parent / "figures"
    results_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("H-M2: Emergent-Capability Benchmark Creation Analysis")
    print("=" * 60)

    print("\n[1/5] Loading PWC datasets...")
    raw_datasets = load_pwc_datasets()

    print("\n[2/5] Building benchmark records...")
    benchmarks = build_benchmark_records(raw_datasets)

    emergent_no_date = sum(1 for b in benchmarks if b["category"] == "emergent-capability" and b["year"] is None)
    print(f"Emergent benchmarks without dates: {emergent_no_date}")

    print("\n[3/5] Skipping Semantic Scholar lookups (using PWC introduced_date)...")

    print("\n[4/5] Computing metrics...")
    ratio_results = compute_post2020_ratio(benchmarks)
    accel_results = compute_creation_rate_acceleration(benchmarks)
    gate_eval = evaluate_hypothesis(ratio_results)

    print(f"\nTotal benchmarks: {len(benchmarks)}")
    print(f"Emergent-capability (with dates): {ratio_results['total_emergent']}")
    print(f"Post-2020 emergent: {ratio_results['post_2020_count']}")
    print(f"Pre-2020 emergent: {ratio_results['pre_2020_count']}")
    print(f"Post-2020 ratio: {ratio_results['post_2020_ratio']:.2%}")
    print(f"Threshold: 80%")
    print(f"Gate result: {gate_eval['result']}")

    print("\n[5/5] Generating figures...")
    plot_gate_metrics(gate_eval, str(figures_dir / "gate_metrics.png"))
    plot_creation_timeline(benchmarks, str(figures_dir / "creation_timeline.png"))
    plot_cumulative_curve(benchmarks, str(figures_dir / "cumulative_curve.png"))
    plot_type_distribution_by_year(benchmarks, str(figures_dir / "type_distribution.png"))

    elapsed = time.time() - start_time

    results = {
        "hypothesis_id": "H-M2",
        "hypothesis_statement": "Emergent-capability benchmarks created post-foundation-model emergence (>80% post-2020)",
        "gate_type": "SHOULD_WORK",
        "gate_result": gate_eval["result"],
        "metrics": {
            "total_benchmarks": len(benchmarks),
            "total_emergent": ratio_results["total_emergent"],
            "post_2020_count": ratio_results["post_2020_count"],
            "pre_2020_count": ratio_results["pre_2020_count"],
            "post_2020_ratio": ratio_results["post_2020_ratio"],
            "threshold": 0.80,
            "margin": gate_eval["margin"],
            "meets_minimum": ratio_results["total_emergent"] >= MIN_EMERGENT_BENCHMARKS,
        },
        "acceleration": accel_results,
        "runtime_seconds": elapsed,
        "figures_generated": [
            "gate_metrics.png",
            "creation_timeline.png",
            "cumulative_curve.png",
            "type_distribution.png",
        ],
    }

    results_path = results_dir / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    print("\n" + "=" * 60)
    print(f"H-M2 GATE: {gate_eval['result']} ({ratio_results['post_2020_ratio']:.1%} > 80%)")
    print(f"Runtime: {elapsed:.1f}s")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results["gate_result"] == "PASS" else 1)
