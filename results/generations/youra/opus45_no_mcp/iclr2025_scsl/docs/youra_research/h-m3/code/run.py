#!/usr/bin/env python3
"""H-M3 Run: Second Derivative Crystallization Detection Pipeline"""
import json
import yaml
import numpy as np
from pathlib import Path
from datetime import datetime

from config import CONFIG
from data import load_all_curves
from analyzer import analyze_curve, aggregate_seed_results, compute_window_robustness, evaluate_gate
from visualize import (
    plot_gate_metrics, plot_wga_with_derivatives, plot_window_comparison,
    plot_detection_heatmap, plot_snr_distribution, plot_timing_variance
)


def main():
    print("=" * 60)
    print("H-M3: Second Derivative Crystallization Detection")
    print("=" * 60)

    Path(CONFIG.output_dir).mkdir(parents=True, exist_ok=True)
    Path(CONFIG.figures_dir).mkdir(parents=True, exist_ok=True)

    print("\n[1/5] Loading WGA curves...")
    all_curves = load_all_curves(CONFIG)
    total_curves = sum(len(seeds) for seeds in all_curves.values())
    print(f"  Loaded {total_curves} curves across {len(CONFIG.benchmarks)} benchmarks")
    for bm, seeds in all_curves.items():
        n_epochs = CONFIG.get_n_epochs(bm)
        print(f"    {bm}: {len(seeds)} seeds x {n_epochs} epochs")

    print("\n[2/5] Analyzing curves...")
    all_results = []
    for benchmark, seeds in all_curves.items():
        for seed, wga in seeds.items():
            result = analyze_curve(benchmark, seed, wga, CONFIG)
            robustness = compute_window_robustness(
                result['sensitivity'],
                result.get('epoch'),
                CONFIG.window_robustness_tolerance_epochs
            )
            result['window_robustness'] = robustness
            all_results.append(result)
            status = "DETECTED" if result['detected'] else "not detected"
            epoch_str = f"epoch {result['epoch']}" if result['epoch'] else "-"
            snr_str = f"SNR={result['snr']:.2f}" if result['snr'] else "-"
            print(f"    {benchmark}/seed{seed}: {status} @ {epoch_str} ({snr_str})")

    print("\n[3/5] Aggregating results...")
    aggregated = aggregate_seed_results(all_results)
    for bm, stats in aggregated.items():
        print(f"    {bm}: rate={stats['detection_rate']:.1%}, "
              f"var={stats['timing_variance_epochs']:.2f}, snr={stats['mean_snr']:.2f}")

    print("\n[4/5] Evaluating gate...")
    gate_result = evaluate_gate(aggregated, CONFIG)
    print(f"    Detection Rate: {gate_result['detection_rate']['value']:.1%} "
          f"(target: {gate_result['detection_rate']['target']:.0%})")
    print(f"    Timing Variance: {gate_result['timing_variance_epochs']['value']:.2f} epochs "
          f"(target: <{gate_result['timing_variance_epochs']['target']})")
    print(f"    Mean SNR: {gate_result['snr']['value']:.2f} "
          f"(target: >{gate_result['snr']['target']})")
    print(f"    Gate: {'PASS' if gate_result['passed'] else 'FAIL'}")

    print("\n[5/5] Generating outputs...")
    results_for_json = []
    for r in all_results:
        r_copy = {k: v for k, v in r.items() if k not in ['wga', 'smoothed', 'd2']}
        results_for_json.append(r_copy)
    results_path = Path(CONFIG.output_dir) / CONFIG.results_file
    with open(results_path, 'w') as f:
        json.dump(results_for_json, f, indent=2, default=str)
    print(f"    Saved: {results_path}")

    metrics_data = {
        'per_benchmark': aggregated,
        'gate': gate_result,
        'generated_at': datetime.now().isoformat()
    }
    metrics_path = Path(CONFIG.output_dir) / CONFIG.metrics_file
    with open(metrics_path, 'w') as f:
        yaml.dump(metrics_data, f, default_flow_style=False)
    print(f"    Saved: {metrics_path}")

    print("\n    Generating figures...")
    plot_gate_metrics(gate_result, str(Path(CONFIG.figures_dir) / 'gate_metrics.png'))
    print("      - gate_metrics.png")

    sample_result = all_results[0]
    plot_wga_with_derivatives(
        np.array(sample_result['wga']),
        np.array(sample_result['smoothed']),
        np.array(sample_result['d2']),
        sample_result.get('epoch'),
        str(Path(CONFIG.figures_dir) / 'wga_with_derivatives.png')
    )
    print("      - wga_with_derivatives.png")

    plot_window_comparison(
        np.array(sample_result['wga']),
        CONFIG.smoothing_windows,
        str(Path(CONFIG.figures_dir) / 'window_comparison.png')
    )
    print("      - window_comparison.png")

    plot_detection_heatmap(all_results, str(Path(CONFIG.figures_dir) / 'detection_heatmap.png'))
    print("      - detection_heatmap.png")

    plot_snr_distribution(all_results, str(Path(CONFIG.figures_dir) / 'snr_distribution.png'))
    print("      - snr_distribution.png")

    plot_timing_variance(aggregated, str(Path(CONFIG.figures_dir) / 'timing_variance.png'))
    print("      - timing_variance.png")

    print("\n" + "=" * 60)
    print(f"RESULT: Gate {'PASS' if gate_result['passed'] else 'FAIL'}")
    print("=" * 60)

    return gate_result


if __name__ == '__main__':
    result = main()
