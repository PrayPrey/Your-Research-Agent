"""H-M3 Analysis Orchestration: Non-Monotonicity Confirmation (G3 >= G4).

Entry point for running the full analysis pipeline.
"""
import sys
from pathlib import Path
from datetime import datetime

from config import AnalysisConfig
from data_loader import load_h_m1_results, extract_paired_outcomes, validate_data_integrity
from stat_tests import (
    build_contingency_table,
    run_mcnemar_test,
    run_tost_equivalence,
    compute_confidence_interval
)
from evaluate import evaluate_gate_condition, save_results
from visualize import generate_all_figures


def run_analysis(cfg: AnalysisConfig) -> dict:
    """Run full H-M3 analysis pipeline.

    Pipeline: load -> extract -> validate -> stats -> gate -> save -> visualize

    Args:
        cfg: Analysis configuration

    Returns:
        Gate result dict with gate_passed, reason, g3_rate, g4_rate
    """
    print("=" * 60)
    print("H-M3: Non-Monotonicity Confirmation (G3 >= G4)")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")
    print(f"Data source: {cfg.h_m1_results_path}")
    print()

    # Step 1: Load H-M1 results
    print("[Step 1/7] Loading H-M1 results...")
    results = load_h_m1_results(cfg.h_m1_results_path)

    # Step 2: Extract paired G3/G4 outcomes
    print("\n[Step 2/7] Extracting paired outcomes...")
    g3_outcomes, g4_outcomes, problem_ids = extract_paired_outcomes(results)

    # Step 3: Validate data integrity
    print("\n[Step 3/7] Validating data integrity...")
    validation = validate_data_integrity(g3_outcomes, g4_outcomes, problem_ids)
    if not validation['valid']:
        raise ValueError(f"Data validation failed: {validation['issues']}")

    n_pairs = validation['n_pairs']
    g3_successes = validation['g3_count']
    g4_successes = validation['g4_count']
    g3_rate = validation['g3_rate']
    g4_rate = validation['g4_rate']

    # Step 4: Build contingency table and run McNemar's test
    print("\n[Step 4/7] Running statistical tests...")
    table = build_contingency_table(g3_outcomes, g4_outcomes)
    mcnemar_result = run_mcnemar_test(table)
    print(f"McNemar's test: p={mcnemar_result['pvalue']:.4f}, "
          f"significant={mcnemar_result['significant']}")

    # Step 5: Run TOST equivalence and compute CI
    print("\n[Step 5/7] Running equivalence tests...")
    tost_result = run_tost_equivalence(
        g3_successes, n_pairs,
        g4_successes, n_pairs,
        margin=cfg.equivalence_margin,
        alpha=cfg.alpha
    )
    print(f"TOST: equivalent={tost_result['equivalent']}, "
          f"diff={tost_result['difference']*100:.2f}%")

    ci_result = compute_confidence_interval(
        g3_successes, n_pairs,
        g4_successes, n_pairs,
        confidence=cfg.confidence
    )
    print(f"95% CI: [{ci_result['ci_lower']*100:.2f}%, {ci_result['ci_upper']*100:.2f}%]")

    # Step 6: Evaluate gate condition
    print("\n[Step 6/7] Evaluating gate condition...")
    gate_result = evaluate_gate_condition(
        g3_rate, g4_rate,
        mcnemar_result['pvalue'],
        margin=cfg.equivalence_margin
    )

    # Step 7: Save results and generate figures
    print("\n[Step 7/7] Saving results and generating figures...")
    save_results(table, mcnemar_result, tost_result, ci_result, gate_result, cfg)
    generate_all_figures(g3_rate, g4_rate, table, ci_result, results, cfg)

    # Summary
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"G3 success rate: {g3_rate*100:.2f}% ({g3_successes}/{n_pairs})")
    print(f"G4 success rate: {g4_rate*100:.2f}% ({g4_successes}/{n_pairs})")
    print(f"Difference (G4-G3): {(g4_rate-g3_rate)*100:.2f}%")
    print(f"McNemar p-value: {mcnemar_result['pvalue']:.4f}")
    print(f"TOST equivalent: {tost_result['equivalent']}")
    print(f"Gate: {'PASS' if gate_result['gate_passed'] else 'FAIL'}")
    print(f"Reason: {gate_result['reason']}")
    print("=" * 60)

    return gate_result


if __name__ == "__main__":
    cfg = AnalysisConfig()

    # Ensure output directories exist
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)

    try:
        result = run_analysis(cfg)
        status = "PASS" if result['gate_passed'] else "FAIL"
        print(f"\nFinal Gate Result: {status}")
        sys.exit(0 if result['gate_passed'] else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
