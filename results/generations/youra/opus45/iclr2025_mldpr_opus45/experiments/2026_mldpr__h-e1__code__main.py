"""Main experiment runner for h-e1 DTW clustering experiment."""

import sys
import os

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from typing import Dict
from datetime import datetime

from config import ExperimentConfig
from data import collect_datasets, preprocess, extract_features, validate_data_quality
from model import BaselineModel, DTWModel
from evaluate import (
    compute_jaccard_stability,
    verify_mechanism,
    generate_figures,
    write_validation_report,
)


def run_experiment(config: ExperimentConfig) -> Dict:
    """
    Run the full h-e1 experiment pipeline.

    Returns:
        Dictionary with all results and gate pass/fail status
    """
    print("=" * 60)
    print("H-E1: DTW Time Series Clustering Experiment")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    # Step 1: Data Collection
    print("[Step 1/7] Collecting time series from HuggingFace Hub...")
    datasets = collect_datasets(config)

    # Validate data quality
    quality_passed, quality_report = validate_data_quality(datasets)
    print(f"  Datasets collected: {quality_report['n_datasets']}")
    print(f"  Data quality check: {'PASS' if quality_passed else 'FAIL'}")

    if not quality_passed:
        print("  WARNING: Data quality below threshold, proceeding anyway")

    # Step 2: Preprocessing
    print("\n[Step 2/7] Preprocessing time series...")
    raw_series = [d["series"] for d in datasets]
    X = preprocess(raw_series)
    features = extract_features(raw_series)
    print(f"  X shape (tslearn format): {X.shape}")
    print(f"  Features shape: {features.shape}")

    # Step 3: Baseline Model
    print("\n[Step 3/7] Running baseline model (KMeans on features)...")
    baseline_model = BaselineModel(config)
    baseline_k, baseline_silhouette, baseline_labels, baseline_scores = baseline_model.best_k_silhouette(features)
    print(f"  Best baseline k: {baseline_k}")
    print(f"  Best baseline silhouette: {baseline_silhouette:.4f}")

    # Step 4: DTW Model
    print("\n[Step 4/7] Running DTW TimeSeriesKMeans...")
    dtw_model = DTWModel(config)
    best_k, best_silhouette, best_model, dtw_scores = dtw_model.best_k_silhouette(X)
    print(f"  Best DTW k: {best_k}")
    print(f"  Best DTW silhouette: {best_silhouette:.4f}")

    # Step 5: Bootstrap Jaccard Stability
    print("\n[Step 5/7] Computing bootstrap Jaccard stability...")
    jaccard_stability = compute_jaccard_stability(X, best_model, config)

    # Step 6: Mechanism Verification
    print("\n[Step 6/7] Verifying mechanism activation...")
    mechanism_passed, mechanism_indicators = verify_mechanism(
        best_model, best_silhouette, baseline_silhouette
    )
    print(f"  Mechanism verification: {'PASS' if mechanism_passed else 'FAIL'}")
    for indicator, status in mechanism_indicators.items():
        print(f"    - {indicator}: {'PASS' if status else 'FAIL'}")

    # Prepare gate metrics
    gate_metrics = {
        'silhouette': best_silhouette,
        'jaccard_stability': jaccard_stability,
        'optimal_k': best_k,
    }

    # Step 7: Generate figures and report
    print("\n[Step 7/7] Generating figures and validation report...")
    figure_paths = generate_figures(
        X, best_model.labels_, dtw_scores, best_model, config, gate_metrics
    )
    print(f"  Generated {len(figure_paths)} figures")

    # Compile results
    results = {
        'silhouette': best_silhouette,
        'optimal_k': best_k,
        'jaccard_stability': jaccard_stability,
        'baseline_silhouette': baseline_silhouette,
        'baseline_k': baseline_k,
        'n_datasets': len(datasets),
        'dtw_silhouette_scores': dtw_scores,
        'baseline_silhouette_scores': baseline_scores,
        'mechanism_indicators': mechanism_indicators,
        'figure_paths': figure_paths,
    }

    # Write validation report
    gate_result = write_validation_report(results, config)
    results['gate_pass'] = gate_result == 'PASS'
    results['gate_result'] = gate_result

    # Summary
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print(f"DTW Silhouette Score: {best_silhouette:.4f} (threshold: > {config.silhouette_threshold})")
    print(f"Optimal k: {best_k} (expected: in [{config.k_range[0]}, {config.k_range[1]}])")
    print(f"Jaccard Stability: {jaccard_stability:.4f} (threshold: > {config.jaccard_threshold})")
    print(f"\nGATE RESULT: {gate_result}")
    print(f"End time: {datetime.now().isoformat()}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)

    # Create config with output paths relative to research folder
    config = ExperimentConfig(
        figures_dir="/home/anonymous/YouRA_results_new_4_sonnet45/TEST_mldpr_opus45/docs/youra_research/20260325_mldpr/h-e1/figures",
        output_path="/home/anonymous/YouRA_results_new_4_sonnet45/TEST_mldpr_opus45/docs/youra_research/20260325_mldpr/h-e1/04_validation.md",
    )

    results = run_experiment(config)

    # Exit with appropriate code
    sys.exit(0 if results['gate_pass'] else 1)
