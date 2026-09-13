"""Main orchestrator for H-M3 Bootstrap CI Stability Analysis.

Task: T-EPIC-07 (A-7: Results Output)
Task: T-EPIC-08 (A-8: Orchestration)
"""

import json
import sys
import time
from pathlib import Path

from config import BootstrapConfig
from data_loader import load_h_e1_test_accuracies
from bootstrap_analysis import analyze_all_conditions
from gate_validator import check_ci_width_threshold, generate_gate_report, save_gate_result
from visualize import generate_all_figures


def save_bootstrap_results(bootstrap_results: dict, save_path: str) -> None:
    """Save bootstrap_results.json.

    Args:
        bootstrap_results: Dictionary of bootstrap analysis results
        save_path: Path to save JSON file
    """
    with open(save_path, 'w') as f:
        json.dump(bootstrap_results, f, indent=2)

    print(f"✓ Bootstrap results saved to {save_path}")


def main() -> str:
    """Run full bootstrap analysis pipeline.

    Returns:
        Gate result: 'PASS' or 'FAIL'
    """
    start_time = time.time()

    print("\n" + "=" * 70)
    print("H-M3 BOOTSTRAP CI STABILITY ANALYSIS")
    print("=" * 70)
    print("Hypothesis: Bootstrap CI width ≤ 50% for variance estimates from N=30 samples")
    print("Gate: SHOULD_WORK")
    print("=" * 70)

    try:
        # Step 1: Load configuration
        print("\n[1/6] Loading configuration...")
        config = BootstrapConfig()
        print(f"  ✓ Bootstrap resamples: {config.n_resamples}")
        print(f"  ✓ Confidence level: {config.confidence_level * 100}%")
        print(f"  ✓ CI width threshold: {config.ci_width_threshold_pct}%")
        print(f"  ✓ Random seed: {config.random_seed}")

        # Step 2: Load h-e1 test accuracy data
        print("\n[2/6] Loading h-e1 test accuracy data...")
        conditions_data = load_h_e1_test_accuracies(config.h_e1_results_path)

        # Step 3: Run bootstrap analysis
        print("\n[3/6] Running bootstrap analysis...")
        bootstrap_results = analyze_all_conditions(
            conditions_data,
            config.n_resamples,
            config.confidence_level,
            config.random_seed
        )

        # Step 4: Validate gate condition
        print("\n[4/6] Validating gate condition...")
        gate_result = check_ci_width_threshold(bootstrap_results, config.ci_width_threshold_pct)

        # Generate and print gate report
        report = generate_gate_report(bootstrap_results, gate_result)
        print(report)

        # Step 5: Save results
        print("\n[5/6] Saving results...")
        bootstrap_results_path = f"{config.results_dir}/bootstrap_results.json"
        gate_result_path = f"{config.results_dir}/gate_result.json"

        save_bootstrap_results(bootstrap_results, bootstrap_results_path)
        save_gate_result(gate_result, gate_result_path)

        # Step 6: Generate visualizations
        print("\n[6/6] Generating visualizations...")
        generate_all_figures(conditions_data, bootstrap_results, config)

        # Final summary
        elapsed_time = time.time() - start_time

        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        print(f"Gate Result: {gate_result['gate_result']}")
        print(f"Runtime: {elapsed_time:.2f} seconds")
        print(f"Results: {config.results_dir}/")
        print(f"Figures: {config.figures_dir}/")
        print("=" * 70)

        return gate_result['gate_result']

    except Exception as e:
        print(f"\n✗ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result == "PASS" else 1)
