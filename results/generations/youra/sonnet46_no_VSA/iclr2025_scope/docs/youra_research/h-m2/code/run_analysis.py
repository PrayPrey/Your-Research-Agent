"""
H-M2 Main Analysis Pipeline: Depth-Slope Differential Analysis.

Pipeline:
  1. Load H-E1 per-example results (MOHAWK-SSM + LAWCAT)
  2. Load LongBench v2 context, merge by positional alignment
  3. Filter to retrieval-heavy subset
  4. Compute depth_percentile per example
  5. Fit mixed-effects logistic regression per model
  6. Evaluate gate: |β_SSM| / |β_LAWCAT| >= 2.0 AND CI non-overlap
  7. Generate 4 figures
  8. Save results JSON + Markdown summary
"""
import sys
import json
import os
from pathlib import Path

# Add code dir to path for sibling imports
CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

from config import MOHAWK_RESULTS_JSON, LAWCAT_RESULTS_JSON, RESULTS_JSON, FIGURES_DIR
from data_loader import load_and_prepare
from depth_computer import add_depth_percentiles, depth_stats
from regression import run_regression
from gate_evaluator import evaluate_gate
from visualizer import generate_all_figures
from reporter import save_results_json, save_summary_md


def main():
    print("=" * 60)
    print("H-M2: Depth-Slope Differential Analysis")
    print("MOHAWK-SSM vs LAWCAT on LongBench v2 Retrieval Tasks")
    print("=" * 60)

    # Step 1 + 2 + 3: Load, merge, filter
    print("\n[Step 1-3] Loading data and filtering retrieval subset...")
    mohawk_records, lawcat_records = load_and_prepare(MOHAWK_RESULTS_JSON, LAWCAT_RESULTS_JSON)

    sample_sizes = {
        "mohawk_ssm": len(mohawk_records),
        "lawcat": len(lawcat_records),
    }
    print(f"Sample sizes: MOHAWK={sample_sizes['mohawk_ssm']}, LAWCAT={sample_sizes['lawcat']}")

    # Step 4: Compute depth percentiles
    print("\n[Step 4] Computing depth percentiles...")
    add_depth_percentiles(mohawk_records)
    add_depth_percentiles(lawcat_records)

    ds_mohawk = depth_stats(mohawk_records)
    ds_lawcat = depth_stats(lawcat_records)
    print(f"Depth stats MOHAWK: mean={ds_mohawk['mean']:.3f}, std={ds_mohawk['std']:.3f}, "
          f"fallback={ds_mohawk['fallback_fraction']:.1%}")
    print(f"Depth stats LAWCAT: mean={ds_lawcat['mean']:.3f}, std={ds_lawcat['std']:.3f}, "
          f"fallback={ds_lawcat['fallback_fraction']:.1%}")

    # Step 5: Fit regression
    print("\n[Step 5] Fitting mixed-effects logistic regression...")
    reg_results = run_regression(mohawk_records, lawcat_records)

    # Step 6: Evaluate gate
    print("\n[Step 6] Evaluating gate criterion...")
    gate_result = evaluate_gate(reg_results)

    # Step 7: Generate figures
    print("\n[Step 7] Generating figures...")
    os.makedirs(FIGURES_DIR, exist_ok=True)
    figure_paths = generate_all_figures(mohawk_records, lawcat_records, reg_results, gate_result)

    # Step 8: Save results
    print("\n[Step 8] Saving results...")
    save_results_json(gate_result, reg_results, sample_sizes, ds_mohawk, ds_lawcat)
    save_summary_md(gate_result, reg_results, sample_sizes, ds_mohawk, figure_paths)

    print("\n" + "=" * 60)
    print(f"ANALYSIS COMPLETE")
    print(f"Gate verdict: {gate_result['verdict']}")
    print(f"Ratio: {gate_result['ratio']:.4f} (threshold: 2.0)")
    print(f"β_SSM: {gate_result['beta_ssm']:.4f}")
    print(f"β_LAWCAT: {gate_result['beta_lawcat']:.4f}")
    print(f"CI overlap: {gate_result['ci_overlap']}")
    print("=" * 60)

    return gate_result


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["gate_pass"] else 2)


# Self-check
if __name__ == "__main____test__":
    from gate_evaluator import evaluate_gate
    mock_reg = {
        "mohawk_ssm": {"beta": -0.8, "ci_low": -1.2, "ci_high": -0.4, "p_value": 0.001, "method": "test"},
        "lawcat": {"beta": -0.3, "ci_low": -0.5, "ci_high": -0.1, "p_value": 0.05, "method": "test"},
        "holm_corrected_p_values": {"mohawk_ssm": 0.002, "lawcat": 0.05},
    }
    g = evaluate_gate(mock_reg)
    assert g["ratio"] == round(0.8 / 0.3, 4), f"Expected {round(0.8/0.3,4)}, got {g['ratio']}"
    assert not g["ci_overlap"], "CIs should not overlap"
    assert g["gate_pass"], "Should PASS"
    print("Self-check passed.")
