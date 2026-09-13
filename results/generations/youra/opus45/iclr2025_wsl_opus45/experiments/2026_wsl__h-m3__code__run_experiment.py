"""RunExperiment: Orchestration entry point for H-M3 correlation analysis."""

import argparse
import json
import os
import sys
from datetime import datetime

import config
from grassmann_loader import load_or_compute_distances, validate_distance_matrix
from taxonomy import (
    build_taxonomy_distance_matrix,
    extract_task_labels_from_meta,
    save_taxonomy_matrix,
    validate_taxonomy_matrix,
)
from correlation import (
    CorrelationResult,
    P3ControlResult,
    compute_spearman_correlation,
    compute_p3_control,
    save_correlation_results,
)
from visualize import generate_all_figures


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="H-M3: FLAN Taxonomy Correlation with Grassmann Distances"
    )
    parser.add_argument(
        "--force-recompute",
        action="store_true",
        help="Force recomputation of Grassmann distances from adapters",
    )
    parser.add_argument(
        "--skip-figures",
        action="store_true",
        help="Skip figure generation",
    )
    return parser.parse_args()


def print_gate_summary(corr: CorrelationResult, p3: P3ControlResult) -> None:
    """Print structured pass/fail summary to stdout."""
    print("\n" + "=" * 60)
    print("H-M3 GATE EVALUATION SUMMARY")
    print("=" * 60)

    # Spearman correlation gate
    rho_threshold = config.ANALYSIS_CONFIG["spearman_rho_threshold"]
    p_threshold = config.ANALYSIS_CONFIG["p_threshold"]
    rho_status = "PASS" if corr.spearman_rho > rho_threshold else "FAIL"
    p_status = "PASS" if corr.p_value < p_threshold else "FAIL"

    print("\n[Spearman Correlation]")
    print(f"  Spearman ρ: {corr.spearman_rho:.4f} (threshold: >{rho_threshold}) [{rho_status}]")
    print(f"  P-value:    {corr.p_value:.2e} (threshold: <{p_threshold}) [{p_status}]")
    print(f"  95% CI:     [{corr.ci_low:.4f}, {corr.ci_high:.4f}]")
    print(f"  N pairs:    {corr.n_pairs}")
    print(f"  Gate:       {'PASS' if corr.gate_passed else 'FAIL'}")

    # P3 control gate
    ratio_threshold = config.ANALYSIS_CONFIG["p3_ratio_threshold"]
    ratio_status = "PASS" if p3.control_passed else "FAIL"

    print("\n[P3 Control Analysis]")
    print(f"  Within-task mean:    {p3.within_task_mean:.4f}")
    print(f"  Within-cluster mean: {p3.within_cluster_mean:.4f}")
    print(f"  Ratio:               {p3.ratio:.4f} (threshold: <{ratio_threshold}) [{ratio_status}]")
    print(f"  Control:             {'PASS' if p3.control_passed else 'FAIL'}")

    # Overall gate
    overall = corr.gate_passed and p3.control_passed
    print("\n" + "-" * 60)
    print(f"OVERALL GATE: {'PASS' if overall else 'FAIL'}")
    print("=" * 60 + "\n")


def run(force_recompute: bool = False, skip_figures: bool = False) -> dict:
    """
    Orchestration: Run the full H-M3 analysis pipeline.

    Steps:
    1. Load/compute Grassmann distance matrix (GrassmannLoader)
    2. Build FLAN taxonomy distance matrix (TaxonomyMatrix)
    3. Compute Spearman correlation + P3 control (CorrelationAnalyzer)
    4. Save results JSON
    5. Generate figures (Visualizer)
    6. Print gate pass/fail summary

    Args:
        force_recompute: Force recomputation of Grassmann distances
        skip_figures: Skip figure generation

    Returns:
        Combined results dict for downstream consumption
    """
    print("=" * 60)
    print("H-M3: FLAN Taxonomy Correlation with Grassmann Distances")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    # 1. Load Grassmann distances from H-E1
    print("\n[Step 1] Loading Grassmann distance matrix from H-E1...")
    dist_matrix, adapter_meta = load_or_compute_distances(
        config.H_E1_HYPOTHESIS_DIR,
        force_recompute=force_recompute,
    )
    validate_distance_matrix(dist_matrix)
    print(f"  Loaded: {dist_matrix.shape[0]} adapters")
    print(f"  Tasks: {len(set(m['task'] for m in adapter_meta))}")

    # 2. Build taxonomy matrix
    print("\n[Step 2] Building FLAN taxonomy distance matrix...")
    task_labels = extract_task_labels_from_meta(adapter_meta)
    taxonomy_matrix = build_taxonomy_distance_matrix(
        task_labels,
        config.FLAN_CATEGORIES,
        mode="binary",
    )
    validate_taxonomy_matrix(taxonomy_matrix)
    save_taxonomy_matrix(taxonomy_matrix, config.RESULTS_DIR)
    print(f"  Built: {taxonomy_matrix.shape} binary matrix")
    same_cat = (taxonomy_matrix == 0).sum() - taxonomy_matrix.shape[0]  # exclude diagonal
    diff_cat = (taxonomy_matrix == 1).sum()
    print(f"  Same category pairs: {same_cat // 2}")
    print(f"  Different category pairs: {diff_cat // 2}")

    # 3. Compute Spearman correlation + P3 control
    print("\n[Step 3] Computing Spearman correlation...")
    corr = compute_spearman_correlation(
        dist_matrix,
        taxonomy_matrix,
        n_bootstrap=config.ANALYSIS_CONFIG["n_bootstrap"],
        random_seed=config.ANALYSIS_CONFIG["random_seed"],
    )
    print(f"  Spearman ρ: {corr.spearman_rho:.4f}")
    print(f"  P-value: {corr.p_value:.2e}")

    print("\n[Step 4] Computing P3 control analysis...")
    p3 = compute_p3_control(
        dist_matrix,
        adapter_meta,
        ratio_threshold=config.ANALYSIS_CONFIG["p3_ratio_threshold"],
    )
    print(f"  Within-task mean: {p3.within_task_mean:.4f}")
    print(f"  Within-cluster mean: {p3.within_cluster_mean:.4f}")
    print(f"  Ratio: {p3.ratio:.4f}")

    # 4. Save results
    print("\n[Step 5] Saving results...")
    save_correlation_results(corr, p3, config.RESULTS_DIR)
    print(f"  Saved to: {config.RESULTS_DIR}/correlation_results.json")

    # 5. Generate figures
    if not skip_figures:
        print("\n[Step 6] Generating figures...")
        generate_all_figures(
            config.HYPOTHESIS_FOLDER,
            dist_matrix,
            taxonomy_matrix,
            adapter_meta,
            corr,
            p3,
        )
    else:
        print("\n[Step 6] Skipping figure generation (--skip-figures)")

    # 6. Print summary
    print_gate_summary(corr, p3)

    # Build return dict
    results = {
        **corr._asdict(),
        **p3._asdict(),
        "overall_gate_passed": corr.gate_passed and p3.control_passed,
        "timestamp": datetime.now().isoformat(),
    }

    return results


if __name__ == "__main__":
    args = parse_args()
    results = run(
        force_recompute=args.force_recompute,
        skip_figures=args.skip_figures,
    )

    # Exit with appropriate code
    sys.exit(0 if results["overall_gate_passed"] else 1)
