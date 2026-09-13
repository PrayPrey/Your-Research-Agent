#!/usr/bin/env python3
"""H-M4 Run: Benchmark-Relative Crystallization Timing Validation"""
import json
import yaml
import numpy as np
from pathlib import Path
from datetime import datetime
import torch

from config import CONFIG
from train import run_all_benchmarks
from analyzer import (
    analyze_all_runs, aggregate_per_benchmark, compute_cross_benchmark_variance,
    compute_range_compliance, detect_seed_outliers, evaluate_gate
)
from visualize import (
    plot_gate_metrics, plot_normalized_timing_bars, plot_wga_curves_overlay,
    plot_timing_distribution, plot_cross_benchmark_regression, plot_gate_dashboard
)


def main():
    print("=" * 60)
    print("H-M4: Benchmark-Relative Crystallization Timing Validation")
    print("=" * 60)

    Path(CONFIG.output_dir).mkdir(parents=True, exist_ok=True)
    Path(CONFIG.figures_dir).mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    print("\n[1/6] Training all benchmarks (or loading cached)...")
    wga_curves = run_all_benchmarks(CONFIG, device)
    total_runs = sum(len(seeds) for seeds in wga_curves.values())
    print(f"  {total_runs} total runs across {len(CONFIG.benchmarks)} benchmarks")

    print("\n[2/6] Analyzing timing for all runs...")
    results = analyze_all_runs(wga_curves, CONFIG)
    for bm, data in results.items():
        n_detected = sum(1 for r in data['runs'] if r['detected'])
        print(f"  {bm}: {n_detected}/{len(data['runs'])} detected")

    print("\n[3/6] Aggregating per-benchmark statistics...")
    aggregated = aggregate_per_benchmark(results, CONFIG)
    for bm, agg in aggregated.items():
        timing = agg['mean_normalized_timing']
        in_range = 'IN' if agg['in_expected_range'] else 'OUT'
        timing_str = f"{timing:.1f}%" if timing is not None else "N/A"
        print(f"  {bm}: {timing_str} ({in_range} range), rate={agg['detection_rate']:.0%}")

    print("\n[4/6] Computing cross-benchmark statistics...")
    cross_var = compute_cross_benchmark_variance(aggregated)
    compliance = compute_range_compliance(aggregated, CONFIG.expected_range)
    outliers = detect_seed_outliers(results, CONFIG)
    print(f"  Cross-benchmark variance: {cross_var['variance']:.2f}%")
    print(f"  Range compliance: {compliance:.0f}%")
    print(f"  Seed outliers: {outliers}")

    print("\n[5/6] Evaluating gate...")
    gate_result = evaluate_gate(aggregated, cross_var, compliance, CONFIG)
    print(f"  Status: {gate_result['status']}")
    print(f"  All in 20-40%: {gate_result['metrics']['all_in_range']}")
    print(f"  Variance: {cross_var['variance']:.2f}% (target: <{CONFIG.variance_target}%)")

    print("\n[6/6] Generating outputs...")

    results_for_json = {}
    for bm, data in results.items():
        results_for_json[bm] = {
            'runs': [{k: (v if not isinstance(v, np.ndarray) else v.tolist())
                      for k, v in r.items()} for r in data['runs']]
        }
    results_path = Path(CONFIG.output_dir) / 'timing_results.json'
    with open(results_path, 'w') as f:
        json.dump(results_for_json, f, indent=2, default=str)
    print(f"  Saved: {results_path}")

    metrics_data = {
        'per_benchmark': {bm: {k: (float(v) if isinstance(v, (np.floating, np.integer)) else v)
                               for k, v in agg.items()} for bm, agg in aggregated.items()},
        'cross_benchmark': cross_var,
        'range_compliance_percent': compliance,
        'outliers': outliers,
        'gate': gate_result,
        'generated_at': datetime.now().isoformat()
    }
    metrics_path = Path(CONFIG.output_dir) / 'aggregated_metrics.yaml'
    with open(metrics_path, 'w') as f:
        yaml.dump(metrics_data, f, default_flow_style=False)
    print(f"  Saved: {metrics_path}")

    print("\n  Generating figures...")
    figures_dir = Path(CONFIG.figures_dir)

    plot_gate_metrics(gate_result, str(figures_dir / 'gate_metrics.png'))
    print("    - gate_metrics.png")

    plot_normalized_timing_bars(aggregated, CONFIG.expected_range,
                                 str(figures_dir / 'normalized_timing_bars.png'))
    print("    - normalized_timing_bars.png")

    plot_wga_curves_overlay(wga_curves, CONFIG.benchmarks,
                             str(figures_dir / 'wga_curves_overlay.png'))
    print("    - wga_curves_overlay.png")

    plot_timing_distribution(results, str(figures_dir / 'timing_distribution.png'))
    print("    - timing_distribution.png")

    plot_cross_benchmark_regression(aggregated, CONFIG.benchmarks,
                                     str(figures_dir / 'cross_benchmark_regression.png'))
    print("    - cross_benchmark_regression.png")

    plot_gate_dashboard(gate_result, aggregated, str(figures_dir / 'gate_dashboard.png'))
    print("    - gate_dashboard.png")

    print("\n" + "=" * 60)
    print(f"RESULT: Gate {gate_result['status']}")
    print("=" * 60)

    return gate_result, aggregated, cross_var


if __name__ == '__main__':
    gate_result, aggregated, cross_var = main()
