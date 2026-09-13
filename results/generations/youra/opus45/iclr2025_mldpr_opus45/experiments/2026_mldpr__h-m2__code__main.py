"""Main experiment runner for h-m2 Shape Descriptor experiment."""

import sys
import os

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from typing import Dict
from datetime import datetime

from config import ExperimentConfig
from data import load_series_and_clusters, validate_centroids
from model import ShapeDescriptorAnalyzer, BaselineDescriptor
from evaluate import (
    compute_inter_cluster_variance,
    compute_intra_cluster_variance,
    compute_variance_ratios,
    compute_gate_metrics,
    generate_figures,
    write_validation_report,
)


def run_experiment(config: ExperimentConfig) -> Dict:
    """
    Run the full h-m2 experiment pipeline.

    Steps:
    1. Load series + cluster assignments + centroids from h-e1 data
    2. Validate centroid shape
    3. Compute shape descriptors for all centroids
    4. Compute baseline descriptors for all centroids
    5. Compute inter-cluster variance per descriptor
    6. Compute intra-cluster variance via bootstrap
    7. Compute variance ratios
    8. Evaluate gate: ratio > 2.0 on >= 2 descriptors
    9. Generate figures
    10. Write validation report

    Returns:
        Dict with all metrics and gate_pass boolean
    """
    print("=" * 60)
    print("H-M2: Shape Descriptor Differentiation Experiment")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    # Step 1: Load data and perform clustering
    print("[Step 1/10] Loading data and performing DTW clustering...")
    all_series, cluster_labels, centroids = load_series_and_clusters(config)
    print(f"  Series loaded: {len(all_series)}")
    print(f"  Centroids shape: {centroids.shape}")

    # Step 2: Validate centroids
    print("\n[Step 2/10] Validating centroids...")
    valid, validation_report = validate_centroids(centroids, config)
    print(f"  Validation: {'PASS' if valid else 'FAIL'}")
    if not valid:
        print(f"  Report: {validation_report}")

    # Step 3: Compute shape descriptors
    print("\n[Step 3/10] Computing shape descriptors for centroids...")
    shape_analyzer = ShapeDescriptorAnalyzer(config)
    descriptor_matrix, descriptor_names = shape_analyzer.compute_descriptor_matrix(centroids)
    print(f"  Descriptor matrix shape: {descriptor_matrix.shape}")
    print(f"  Descriptors: {descriptor_names}")

    # Print descriptor values per cluster
    for i in range(centroids.shape[0]):
        print(f"  Cluster {i}: {dict(zip(descriptor_names, descriptor_matrix[i]))}")

    # Step 4: Compute baseline descriptors
    print("\n[Step 4/10] Computing baseline descriptors (mean/std/trend)...")
    baseline = BaselineDescriptor(config)
    baseline_matrix, baseline_names = baseline.compute_descriptor_matrix(centroids)
    print(f"  Baseline matrix shape: {baseline_matrix.shape}")

    # Step 5: Compute inter-cluster variance
    print("\n[Step 5/10] Computing inter-cluster variance...")
    inter_variance = compute_inter_cluster_variance(descriptor_matrix, descriptor_names)
    for name, var in inter_variance.items():
        print(f"  {name}: {var:.6f}")

    # Step 6: Compute intra-cluster variance (bootstrap)
    print("\n[Step 6/10] Computing intra-cluster variance (bootstrap)...")
    print(f"  Bootstrap samples: {config.n_bootstrap}")
    intra_variance = compute_intra_cluster_variance(
        all_series, cluster_labels, shape_analyzer, descriptor_names, config
    )
    for name, var in intra_variance.items():
        print(f"  {name}: {var:.6f}")

    # Step 7: Compute variance ratios
    print("\n[Step 7/10] Computing variance ratios...")
    variance_ratios = compute_variance_ratios(inter_variance, intra_variance)
    for name, ratio in variance_ratios.items():
        status = "PASS" if ratio > config.variance_ratio_threshold else "FAIL"
        print(f"  {name}: {ratio:.4f} ({status})")

    # Step 8: Evaluate gate
    print("\n[Step 8/10] Evaluating gate metrics...")
    gate_metrics = compute_gate_metrics(variance_ratios, descriptor_matrix, config)
    print(f"  Passing descriptors: {gate_metrics['n_passing_descriptors']} / {len(descriptor_names)}")
    print(f"  Distinct profiles: {gate_metrics['distinct_profiles']}")
    print(f"  Gate pass: {gate_metrics['gate_pass']}")

    # Step 9: Generate figures
    print("\n[Step 9/10] Generating figures...")
    figure_paths = generate_figures(
        centroids, descriptor_matrix, descriptor_names,
        variance_ratios, baseline_matrix, baseline_names, config
    )

    # Compile results
    results = {
        'gate_pass': gate_metrics['gate_pass'],
        'n_passing_descriptors': gate_metrics['n_passing_descriptors'],
        'passing_descriptors': gate_metrics['passing_descriptors'],
        'ratio_gate_pass': gate_metrics['ratio_gate_pass'],
        'distinct_profiles': gate_metrics['distinct_profiles'],
        'min_pairwise_distance': gate_metrics['min_pairwise_distance'],
        'descriptor_names': descriptor_names,
        'descriptor_matrix': descriptor_matrix.tolist(),
        'inter_variance': inter_variance,
        'intra_variance': intra_variance,
        'variance_ratios': variance_ratios,
        'n_clusters': centroids.shape[0],
        'n_series': len(all_series),
        'centroids_shape': centroids.shape,
        'figure_paths': figure_paths,
    }

    # Step 10: Write validation report
    print("\n[Step 10/10] Writing validation report...")
    gate_result = write_validation_report(results, config)
    results['gate_result'] = gate_result

    # Summary
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print(f"Passing Descriptors: {gate_metrics['n_passing_descriptors']} / {len(descriptor_names)} (threshold: >= {config.min_descriptors_passing})")
    print(f"Passing: {gate_metrics['passing_descriptors']}")
    print(f"Distinct Profiles: {gate_metrics['distinct_profiles']}")
    print(f"\nGATE RESULT: {gate_result}")
    print(f"End time: {datetime.now().isoformat()}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)

    # Set CUDA device if available (not needed for this CPU-based experiment)
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "3")

    # Create config with absolute paths
    base_dir = "/home/anonymous/YouRA_results_new_4_sonnet45/TEST_mldpr_opus45/docs/youra_research/20260325_mldpr"
    config = ExperimentConfig(
        figures_dir=os.path.join(base_dir, "h-m2/figures"),
        output_path=os.path.join(base_dir, "h-m2/04_validation.md"),
        h_e1_cache_path=os.path.join(base_dir, "h-e1/code/hf_dataset_cache.json"),
    )

    results = run_experiment(config)

    # Exit with appropriate code
    sys.exit(0 if results['gate_pass'] else 1)
