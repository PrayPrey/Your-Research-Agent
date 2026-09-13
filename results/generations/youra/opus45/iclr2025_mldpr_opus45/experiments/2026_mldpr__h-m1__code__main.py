"""Main experiment runner for h-m1 PELT changepoint detection experiment."""

import sys
import os

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from typing import Dict
from datetime import datetime

from config import ExperimentConfig
from data import load_series, preprocess_for_pelt, validate_series
from model import BaselineDetector, PELTDetector
from evaluate import compute_gate_metrics, generate_figures, write_validation_report


def run_experiment(config: ExperimentConfig) -> Dict:
    """
    Run the full h-m1 PELT changepoint detection experiment.

    Returns:
        Dictionary with all results and gate pass/fail status
    """
    print("=" * 60)
    print("H-M1: PELT Changepoint Detection Experiment")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    # Step 1: Data Loading
    print("[Step 1/6] Loading time series data...")
    datasets = load_series(config)
    print(f"  Loaded {len(datasets)} time series")

    # Validate data quality
    quality_passed, quality_report = validate_series(datasets, config)
    print(f"  Valid series: {quality_report['n_valid']}/{quality_report['n_total']}")
    print(f"  Data quality check: {'PASS' if quality_passed else 'WARN'}")

    # Step 2: Preprocessing
    print("\n[Step 2/6] Preprocessing for PELT...")
    raw_series = [d["series"] for d in datasets]
    preprocessed = preprocess_for_pelt(raw_series)
    print(f"  Preprocessed {len(preprocessed)} series")
    print(f"  Series lengths: min={min(len(s) for s in preprocessed)}, "
          f"max={max(len(s) for s in preprocessed)}, "
          f"mean={np.mean([len(s) for s in preprocessed]):.1f}")

    # Step 3: Baseline Models
    print("\n[Step 3/6] Running baseline detectors...")
    baseline = BaselineDetector(config)

    baseline_random = baseline.compute_detection_rate(preprocessed, "random")
    baseline_fixed = baseline.compute_detection_rate(preprocessed, "fixed_interval")
    baseline_none = baseline.compute_detection_rate(preprocessed, "none")

    print(f"  Random baseline: {baseline_random:.2%}")
    print(f"  Fixed-interval baseline: {baseline_fixed:.2%}")
    print(f"  No-changepoint baseline: {baseline_none:.2%}")

    baseline_rates = {
        "random": baseline_random,
        "fixed_interval": baseline_fixed,
        "none": baseline_none,
    }

    # Step 4: PELT Detector
    print("\n[Step 4/6] Running PELT changepoint detection...")
    pelt = PELTDetector(config)
    all_changepoints, pelt_rate = pelt.detect_all(preprocessed)

    print(f"  PELT detection rate: {pelt_rate:.2%}")
    print(f"  (Threshold: > {config.detection_rate_threshold:.0%})")

    # Step 5: Compute Gate Metrics
    print("\n[Step 5/6] Computing gate metrics...")
    metrics = compute_gate_metrics(all_changepoints, config)

    print(f"  Detection rate: {metrics['detection_rate']:.4f}")
    print(f"  Mean changepoints: {metrics['mean_cps']:.2f}")
    print(f"  Gate check: {'PASS' if metrics['gate_pass'] else 'FAIL'}")

    # Step 6: Generate Figures and Report
    print("\n[Step 6/6] Generating figures and validation report...")

    figure_paths = generate_figures(
        preprocessed,
        all_changepoints,
        baseline_rates,
        pelt_rate,
        config,
    )
    print(f"  Generated {len(figure_paths)} figures")

    # Compile results
    results = {
        'detection_rate': metrics['detection_rate'],
        'mean_cps': metrics['mean_cps'],
        'n_total': metrics['n_total'],
        'n_with_changepoint': metrics['n_with_changepoint'],
        'cp_distribution': metrics['cp_distribution'],
        'gate_pass': metrics['gate_pass'],
        'threshold': metrics['threshold'],
        'baseline_random': baseline_random,
        'baseline_fixed': baseline_fixed,
        'baseline_none': baseline_none,
        'figure_paths': figure_paths,
    }

    # Write validation report
    gate_result = write_validation_report(results, config)
    results['gate_result'] = gate_result

    # Summary
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print(f"Detection Rate: {metrics['detection_rate']:.4f} ({metrics['detection_rate']*100:.1f}%)")
    print(f"Threshold: > {config.detection_rate_threshold} ({config.detection_rate_threshold*100:.0f}%)")
    print(f"Mean Changepoints: {metrics['mean_cps']:.2f}")
    print(f"\nGATE RESULT: {gate_result}")
    print(f"End time: {datetime.now().isoformat()}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)

    # Get base path
    base = os.path.dirname(os.path.abspath(__file__))
    research_folder = os.path.abspath(os.path.join(base, "..", ".."))

    # Create config with absolute paths
    config = ExperimentConfig(
        figures_dir=os.path.join(research_folder, "h-m1", "figures"),
        output_path=os.path.join(research_folder, "h-m1", "04_validation.md"),
        cache_path="hf_dataset_cache.json",  # Local to code folder
    )

    results = run_experiment(config)

    # Exit with appropriate code
    sys.exit(0 if results['gate_pass'] else 1)
