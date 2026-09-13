#!/usr/bin/env python3
"""H-M2 Run Analysis: Orchestrator for conflation analysis."""
import sys
import json
from pathlib import Path
from datetime import datetime

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

from loader import load_results, load_full_results
from threshold_sweep import sweep_thresholds
from group_compare import compare_groups
from feature_breakdown import breakdown_by_feature
from model_consistency import per_model_rates, consistency_score
from plots import (
    plot_gate_metrics,
    plot_sensitivity_curve,
    plot_feature_heatmap,
    plot_cross_model_scatter,
)


def main(
    results_path: str = None,
    out_dir: str = None,
    figures_dir: str = None,
    threshold: float = 0.7,
):
    """Run full H-M2 analysis pipeline."""
    # Resolve paths
    base_dir = Path(__file__).parent.parent.parent
    if results_path is None:
        results_path = base_dir / "h-m1" / "code" / "outputs" / "results.json"
    if out_dir is None:
        out_dir = Path(__file__).parent / "outputs"
    if figures_dir is None:
        figures_dir = Path(__file__).parent.parent / "figures"

    out_dir = Path(out_dir)
    figures_dir = Path(figures_dir)
    out_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)

    print(f"H-M2 Conflation Analysis")
    print(f"=" * 50)
    print(f"Input: {results_path}")
    print(f"Output: {out_dir}")
    print(f"Figures: {figures_dir}")
    print()

    # Load data
    print("Loading H-M1 results...")
    records = load_results(str(results_path))
    full_data = load_full_results(str(results_path))
    print(f"  Loaded {len(records)} task records")
    print(f"  Type A: {full_data['aggregate']['n_type_a']}, Type B: {full_data['aggregate']['n_type_b']}")
    print()

    # Threshold sweep
    print("Running threshold sweep...")
    sweep = sweep_thresholds(records)
    for th, data in sorted(sweep.items()):
        print(f"  θ={th}: A={data['A']:.4f}, B={data['B']:.4f}, diff={data['diff']:.4f}")
    print()

    # Group comparison at primary threshold
    print(f"Group comparison (threshold={threshold})...")
    comparison = compare_groups(records, threshold=threshold)
    print(f"  Rate A: {comparison['rate_A']:.4f} ({comparison['n_high_A']}/{comparison['n_total_A']})")
    print(f"  Rate B: {comparison['rate_B']:.4f} ({comparison['n_high_B']}/{comparison['n_total_B']})")
    print(f"  Diff:   {comparison['rate_difference']:.4f}")
    print(f"  Conflation Score: {comparison['conflation_score']:.4f}")
    print(f"  Chi2 p-value: {comparison['chi2_p']:.4e}")
    print(f"  Gate PASS: {comparison['gate_pass']}")
    print()

    # Cross-model analysis
    print("Cross-model analysis...")
    per_model = per_model_rates(records, threshold=threshold)
    consistency = consistency_score(per_model)
    for model, data in per_model.items():
        short = model.replace("confidence_", "")
        print(f"  {short}: A={data['rate_A']:.4f}, B={data['rate_B']:.4f}, diff={data['diff']:.4f}")
    print(f"  Consistency: std={consistency['std_rate_difference']:.4f}, all_pass={consistency['same_gate_pass']}")
    print()

    # Feature breakdown (no task texts, so proxy analysis)
    print("Feature breakdown (proxy analysis)...")
    feature_breakdown = breakdown_by_feature(records, threshold=threshold, task_texts=None)
    print(f"  {feature_breakdown.get('note', 'N/A')}")
    print()

    # Generate figures
    print("Generating figures...")
    plot_gate_metrics(comparison, str(figures_dir / "gate_metrics.png"))
    print(f"  Saved: gate_metrics.png")

    plot_sensitivity_curve(sweep, str(figures_dir / "sensitivity_curve.png"))
    print(f"  Saved: sensitivity_curve.png")

    plot_feature_heatmap(feature_breakdown, str(figures_dir / "feature_heatmap.png"))
    print(f"  Saved: feature_heatmap.png")

    plot_cross_model_scatter(per_model, str(figures_dir / "cross_model_scatter.png"))
    print(f"  Saved: cross_model_scatter.png")
    print()

    # Compile metrics
    metrics = {
        "hypothesis": "H-M2",
        "title": "Annotator Approval Conflates Correctness with User-State Modeling",
        "timestamp": datetime.now().isoformat(),
        "input_file": str(results_path),
        "primary_threshold": threshold,
        "gate": {
            "type": "SHOULD_WORK",
            "pass": comparison["gate_pass"],
            "fail": comparison.get("gate_fail", False),
            "rate_difference": comparison["rate_difference"],
            "conflation_score": comparison["conflation_score"],
            "pass_condition": "rate_diff < 0.15 OR conflation_score > 0.85",
        },
        "primary_comparison": comparison,
        "threshold_sweep": sweep,
        "cross_model": {
            "per_model": per_model,
            "consistency": consistency,
        },
        "feature_breakdown": feature_breakdown,
        "sample_counts": {
            "total": len(records),
            "type_a": comparison["n_total_A"],
            "type_b": comparison["n_total_B"],
        },
    }

    # Save metrics
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"Saved: {metrics_path}")

    # Print gate result
    print()
    print("=" * 50)
    if comparison["gate_pass"]:
        print("GATE RESULT: PASS")
        print(f"  Rate difference ({comparison['rate_difference']:.4f}) < 0.15")
        print("  Evidence supports conflated reward signal hypothesis")
    else:
        print("GATE RESULT: FAIL")
        print(f"  Rate difference ({comparison['rate_difference']:.4f}) >= 0.15")
        print("  Explore alternative mechanisms")
    print("=" * 50)

    return metrics


if __name__ == "__main__":
    main()
