#!/usr/bin/env python3
"""Main experiment pipeline."""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_loader import load_pwc_benchmark, preprocess_leaderboard
from detector import VelocityDecayDetector
from baseline import manual_inspection_baseline
from visualizer import (
    plot_score_timeline,
    plot_velocity_timeline,
    plot_pvalue_distribution,
    plot_metrics_comparison
)


def run_experiment(benchmark_id: str, output_dir: Path):
    """
    Run full pipeline.
    Returns: {'detection_success': bool, 'first_decay_date': Optional[pd.Timestamp], 'stability_cv': float}
    """
    print(f"\n{'='*60}")
    print(f"Running experiment: {benchmark_id}")
    print(f"{'='*60}\n")

    # 1. Load data
    print("Loading data...")
    df = load_pwc_benchmark(benchmark_id)
    print(f"  Loaded {len(df)} submissions")

    # 2. Preprocess
    print("Preprocessing...")
    df = preprocess_leaderboard(df)
    print(f"  {len(df)} submissions after preprocessing")

    # 3. Run detector
    print("Running velocity decay detector...")
    detector = VelocityDecayDetector(window_days=180, threshold=0.1)
    first_decay, velocities = detector.detect(df)

    print(f"  First decay: {first_decay.date() if first_decay else 'None detected'}")
    print(f"  Total velocity measurements: {len(velocities)}")

    # 4. Run baseline
    print("Running baseline...")
    baseline_date = manual_inspection_baseline(df)
    print(f"  Baseline decay: {baseline_date.date() if baseline_date else 'None detected'}")

    # 5. Compute metrics
    print("Computing metrics...")
    detection_success = first_decay is not None

    if velocities:
        velocity_vals = [v[1] for v in velocities]
        stability_cv = np.std(velocity_vals) / abs(np.mean(velocity_vals))
        p_vals = [v[2] for v in velocities]
        significance_ratio = sum(1 for p in p_vals if p < 0.05) / len(p_vals)
    else:
        stability_cv = float('inf')
        significance_ratio = 0.0

    print(f"  Detection success: {detection_success}")
    print(f"  Measurement stability (CV): {stability_cv:.3f}")
    print(f"  Statistical significance: {significance_ratio:.3f}")

    # 6. Generate figures
    print("Generating figures...")
    figures_dir = output_dir / 'figures'
    figures_dir.mkdir(exist_ok=True)

    plot_score_timeline(df, first_decay, figures_dir / f'{benchmark_id}_score_timeline.png')
    plot_velocity_timeline(velocities, 0.1, figures_dir / f'{benchmark_id}_velocity_timeline.png')
    plot_pvalue_distribution(velocities, figures_dir / f'{benchmark_id}_pvalue_dist.png')
    plot_metrics_comparison(detection_success, stability_cv, significance_ratio, figures_dir / 'gate_metrics_comparison.png')

    print(f"  Saved figures to {figures_dir}")

    # 7. Save results
    results = {
        'benchmark_id': benchmark_id,
        'detection_success': detection_success,
        'first_decay_date': first_decay.isoformat() if first_decay else None,
        'baseline_date': baseline_date.isoformat() if baseline_date else None,
        'stability_cv': stability_cv if not np.isinf(stability_cv) else None,
        'significance_ratio': significance_ratio,
        'total_submissions': len(df),
        'velocity_measurements': len(velocities)
    }

    return results


def main():
    """CLI entry point."""
    benchmarks = ['imagenet', 'glue', 'squad']
    output_dir = Path(__file__).parent / 'outputs'
    output_dir.mkdir(exist_ok=True)

    all_results = {}

    for benchmark_id in benchmarks:
        try:
            results = run_experiment(benchmark_id, Path(__file__).parent)
            all_results[benchmark_id] = results
        except Exception as e:
            print(f"ERROR: {benchmark_id} failed: {e}")
            all_results[benchmark_id] = {'error': str(e)}

    # Save aggregated results
    results_file = output_dir / 'experiment_results.json'
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Experiment complete!")
    print(f"Results saved to: {results_file}")
    print(f"{'='*60}\n")

    # Print summary
    successful = sum(1 for r in all_results.values() if r.get('detection_success', False))
    print(f"Summary: {successful}/{len(benchmarks)} benchmarks detected decay")


if __name__ == '__main__':
    main()
