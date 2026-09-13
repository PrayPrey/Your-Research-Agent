"""Run Experiment: Orchestrate H-M4 layer-wise Grassmann distance analysis."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

import config
from adapter_loader import load_adapter_metadata, validate_adapter_count
from layer_distances import (
    compute_all_layer_type_distances,
    save_layer_distances,
    load_layer_distances,
)
from stats_analysis import (
    analyze_all_layer_types,
    compute_group_statistics,
    evaluate_gate,
)
from visualize import generate_all_figures


def run(force_recompute: bool = False) -> dict:
    """
    Execute the full H-M4 analysis pipeline.

    Steps:
    1. Load adapter metadata from H-E1
    2. Compute layer-type distance matrices (or load from cache)
    3. Run statistical analysis (Cohen's d per layer type)
    4. Evaluate gate (at least one layer type with d > 0.8)
    5. Generate figures
    6. Save results

    Args:
        force_recompute: If True, recompute distances even if cached

    Returns:
        Analysis summary dict with results and gate evaluation
    """
    print("=" * 60)
    print("H-M4: Layer-wise Grassmann Distance Analysis")
    print("=" * 60)
    print()

    # Step 1: Load adapter metadata
    print("Step 1: Loading adapter metadata from H-E1...")
    records = load_adapter_metadata(config.H_E1_RESULTS_DIR)
    validate_adapter_count(records, expected=config.N_ADAPTERS)
    print(f"  Loaded {len(records)} adapter records")
    print(f"  Tasks: {sorted(set(r.task for r in records))}")
    print(f"  Categories: {sorted(set(r.category for r in records))}")
    print()

    # Step 2: Compute or load layer-type distance matrices
    distances_path = os.path.join(config.RESULTS_DIR, "layer_distances.npz")

    if not force_recompute and os.path.exists(distances_path):
        print("Step 2: Loading cached layer distances...")
        distances = load_layer_distances(distances_path)
        print(f"  Loaded {len(distances)} layer types from cache")
    else:
        print("Step 2: Computing layer-type distance matrices...")
        distances = compute_all_layer_type_distances(
            records=records,
            layer_types=config.ALL_LAYER_TYPES,
            verbose=True,
        )
        save_layer_distances(distances, distances_path)
    print()

    # Step 3: Statistical analysis
    print("Step 3: Running statistical analysis...")
    cohens_d_results = analyze_all_layer_types(
        distances=distances,
        records=records,
        n_bootstrap=config.ANALYSIS_CONFIG["n_bootstrap"],
        random_seed=config.ANALYSIS_CONFIG["random_seed"],
    )

    print("\n  Cohen's d by layer type (sorted):")
    for r in cohens_d_results:
        marker = "✓" if r["cohens_d"] > config.ANALYSIS_CONFIG["cohens_d_threshold"] else " "
        print(f"    {marker} {r['layer_type']:10s}: d={r['cohens_d']:.4f} "
              f"[{r['ci_low']:.4f}, {r['ci_high']:.4f}] p={r['p_value']:.2e}")
    print()

    # Step 4: Group statistics (attention vs MLP)
    print("Step 4: Computing group statistics...")
    group_stats = compute_group_statistics(
        results=cohens_d_results,
        attention_types=config.ATTENTION_LAYER_TYPES,
        mlp_types=config.MLP_LAYER_TYPES,
    )
    print(f"  Attention group mean: {group_stats['attention_mean']:.4f} ± {group_stats['attention_std']:.4f}")
    print(f"  MLP group mean: {group_stats['mlp_mean']:.4f} ± {group_stats['mlp_std']:.4f}")
    print(f"  Group difference: {group_stats['group_difference']:.4f}")
    if group_stats['p_value']:
        print(f"  Mann-Whitney p-value: {group_stats['p_value']:.4f}")
    print()

    # Step 5: Gate evaluation
    print("Step 5: Evaluating gate...")
    gate_result = evaluate_gate(
        results=cohens_d_results,
        threshold=config.ANALYSIS_CONFIG["cohens_d_threshold"],
    )
    print(f"  Gate PASSED: {gate_result['passed']}")
    print(f"  Best layer: {gate_result['best_layer']} (d={gate_result['max_d']:.4f})")
    print(f"  Layers above threshold: {gate_result['layers_above_threshold']}")
    print()

    # Step 6: Generate figures
    print("Step 6: Generating figures...")
    figure_paths = generate_all_figures(
        results=cohens_d_results,
        distances=distances,
        records=records,
        group_stats=group_stats,
        figures_dir=config.FIGURES_DIR,
    )
    print()

    # Step 7: Save results
    print("Step 7: Saving results...")
    save_results(
        cohens_d_results=cohens_d_results,
        group_stats=group_stats,
        gate_result=gate_result,
        output_dir=config.RESULTS_DIR,
    )

    # Create analysis summary
    analysis_summary = {
        "hypothesis_id": "h-m4",
        "timestamp": datetime.now().isoformat(),
        "n_adapters": len(records),
        "layer_types_analyzed": list(distances.keys()),
        "cohens_d_results": [dict(r) for r in cohens_d_results],
        "group_statistics": group_stats,
        "gate_evaluation": gate_result,
        "figures_generated": figure_paths,
    }

    # Save summary
    summary_path = os.path.join(config.RESULTS_DIR, "analysis_summary.json")
    with open(summary_path, 'w') as f:
        json.dump(analysis_summary, f, indent=2, default=str)
    print(f"  Saved analysis summary: {summary_path}")

    # Print final summary
    print()
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Gate Result: {'PASS' if gate_result['passed'] else 'FAIL'}")
    print(f"Best Layer Type: {gate_result['best_layer']} (Cohen's d = {gate_result['max_d']:.4f})")
    print(f"Layers Above Threshold (d > {config.ANALYSIS_CONFIG['cohens_d_threshold']}): "
          f"{len(gate_result['layers_above_threshold'])}/{len(config.ALL_LAYER_TYPES)}")
    print(f"Results saved to: {config.RESULTS_DIR}")
    print(f"Figures saved to: {config.FIGURES_DIR}")
    print("=" * 60)

    return analysis_summary


def save_results(
    cohens_d_results: list,
    group_stats: dict,
    gate_result: dict,
    output_dir: str,
) -> None:
    """
    Save analysis results to JSON files.

    Args:
        cohens_d_results: List of CohensDResult
        group_stats: Group statistics dict
        gate_result: Gate evaluation dict
        output_dir: Directory to save files
    """
    os.makedirs(output_dir, exist_ok=True)

    # Cohen's d results
    cohens_d_path = os.path.join(output_dir, "cohens_d_results.json")
    with open(cohens_d_path, 'w') as f:
        json.dump([dict(r) for r in cohens_d_results], f, indent=2)
    print(f"  Saved: {cohens_d_path}")

    # Group statistics
    group_stats_path = os.path.join(output_dir, "group_statistics.json")
    with open(group_stats_path, 'w') as f:
        json.dump(group_stats, f, indent=2)
    print(f"  Saved: {group_stats_path}")

    # Gate result
    gate_path = os.path.join(output_dir, "gate_result.json")
    with open(gate_path, 'w') as f:
        json.dump(gate_result, f, indent=2)
    print(f"  Saved: {gate_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run H-M4 layer-wise analysis")
    parser.add_argument(
        "--force-recompute",
        action="store_true",
        help="Recompute distances even if cached",
    )
    args = parser.parse_args()

    summary = run(force_recompute=args.force_recompute)

    # Exit with appropriate code based on gate result
    sys.exit(0 if summary["gate_evaluation"]["passed"] else 1)
