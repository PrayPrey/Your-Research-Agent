"""Main orchestration for h-m3 Archetype Recovery experiment.

Runs the complete experiment pipeline:
1. Load cluster centroids from h-e1
2. Compute shape descriptors
3. Match clusters to archetypes
4. Evaluate gate metrics
5. Generate figures and validation report
"""

import sys
import os
import json
import numpy as np
from typing import Dict
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ExperimentConfig
from data import load_data, validate_cluster_profiles, load_cluster_centroids
from model import ArchetypeRecoveryMatcher, RandomBaselineMatcher
from evaluate import (
    compute_gate_metrics,
    verify_mechanism_activated,
    generate_figures,
    write_validation_report
)


def run_experiment(config: ExperimentConfig) -> Dict:
    """
    Run complete h-m3 archetype recovery experiment.

    Returns:
        Results dict with gate_pass, metrics, and paths
    """
    print("=" * 60)
    print("h-m3 Archetype Recovery Experiment")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    # 1. Load cluster profiles (shape descriptors)
    print("[1/7] Loading cluster profiles...")
    cluster_profiles = load_data(config)

    # Validate profiles
    valid, report = validate_cluster_profiles(cluster_profiles, config)
    if not valid:
        print(f"Validation failed: {report}")
        return {"gate_pass": False, "error": "Invalid cluster profiles"}

    print(f"  Clusters: {len(cluster_profiles)}")
    for cluster_id, profile in cluster_profiles.items():
        print(f"    Cluster {cluster_id}: {profile}")
    print()

    # 2. Create matcher
    print("[2/7] Initializing ArchetypeRecoveryMatcher...")
    matcher = ArchetypeRecoveryMatcher(config)
    print(f"  Alignment threshold: {config.alignment_threshold}")
    print(f"  Min archetypes required: {config.min_archetypes_recovered}")
    print()

    # 3. Build alignment matrix
    print("[3/7] Building alignment matrix...")
    alignment_matrix = matcher.build_alignment_matrix(cluster_profiles)
    print(f"  Shape: {alignment_matrix.shape}")
    print(f"  Max alignment: {alignment_matrix.max():.4f}")
    print(f"  Min alignment: {alignment_matrix.min():.4f}")
    print()

    # 4. Match clusters to archetypes
    print("[4/7] Matching clusters to archetypes...")
    assignments, n_recovered = matcher.match_clusters(cluster_profiles)
    print(f"  Recovered archetypes: {n_recovered}/{config.n_archetypes}")
    for cluster_id, (arch_name, score) in assignments.items():
        status = "✓" if score >= config.alignment_threshold else "✗"
        print(f"    Cluster {cluster_id} -> {arch_name}: {score:.4f} {status}")
    print()

    # 5. Run baseline for comparison
    print("[5/7] Running random baseline...")
    baseline = RandomBaselineMatcher(config)
    baseline_assignments, baseline_recovered = baseline.match_clusters(cluster_profiles)
    print(f"  Baseline recovered: {baseline_recovered}")
    print()

    # 6. Compute gate metrics
    print("[6/7] Computing gate metrics...")
    results = compute_gate_metrics(assignments, n_recovered, alignment_matrix, config)

    # Add mechanism verification
    activated, indicators = verify_mechanism_activated(results)
    results["mechanism_activated"] = activated
    results["mechanism_indicators"] = indicators

    print(f"  Gate pass: {results['gate_pass']}")
    print(f"  Recovery pass: {results['recovery_pass']} ({results['n_recovered']}>={results['min_required']})")
    print(f"  Alignment pass: {results['alignment_pass']} ({results['mean_alignment']:.4f}>={results['alignment_threshold']})")
    print(f"  Uniqueness pass: {results['uniqueness_pass']}")
    print()

    # 7. Generate figures
    print("[7/7] Generating figures...")
    figure_paths = generate_figures(
        alignment_matrix,
        assignments,
        cluster_profiles,
        baseline_assignments,
        n_recovered,
        config
    )
    results["figure_paths"] = figure_paths
    print()

    # 8. Write validation report
    print("Writing validation report...")
    gate_result = write_validation_report(results, config)
    print()

    # Summary
    print("=" * 60)
    print(f"EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Gate Type: SHOULD_WORK")
    print(f"Gate Result: {gate_result}")
    print(f"Archetypes Recovered: {n_recovered}/{config.min_archetypes_recovered} required")
    print(f"Mean Alignment: {results['mean_alignment']:.4f}")
    print(f"Figures: {len(figure_paths)} generated")
    print(f"Report: {config.output_path}")
    print(f"End time: {datetime.now().isoformat()}")
    print("=" * 60)

    # Save results to JSON
    results_path = os.path.join(os.path.dirname(config.output_path), "experiment_results.json")
    results_serializable = {
        "gate_pass": bool(results["gate_pass"]),
        "gate_type": "SHOULD_WORK",
        "n_recovered": int(results["n_recovered"]),
        "min_required": int(results["min_required"]),
        "mean_alignment": float(results["mean_alignment"]),
        "alignment_threshold": float(results["alignment_threshold"]),
        "recovery_pass": bool(results["recovery_pass"]),
        "alignment_pass": bool(results["alignment_pass"]),
        "uniqueness": bool(results["uniqueness"]),
        "recovered_archetypes": results["recovered_archetypes"],
        "assignments": {str(k): {"archetype": v[0], "score": float(v[1])} for k, v in assignments.items()},
        "alignment_matrix": alignment_matrix.tolist(),
        "figure_paths": figure_paths,
        "mechanism_activated": bool(results["mechanism_activated"]),
        "timestamp": datetime.now().isoformat(),
    }
    with open(results_path, 'w') as f:
        json.dump(results_serializable, f, indent=2)
    print(f"Results saved to: {results_path}")

    return results


if __name__ == "__main__":
    # Absolute paths for experiment execution
    base_dir = "/home/anonymous/YouRA_results_new_4_sonnet45/TEST_mldpr_opus45/docs/youra_research/20260325_mldpr"

    config = ExperimentConfig(
        h_e1_cache_path=os.path.join(base_dir, "h-e1/code/hf_dataset_cache.json"),
        figures_dir=os.path.join(base_dir, "h-m3/figures"),
        output_path=os.path.join(base_dir, "h-m3/04_validation.md"),
    )

    results = run_experiment(config)

    # Exit with appropriate code
    sys.exit(0 if results.get("gate_pass", False) else 1)
