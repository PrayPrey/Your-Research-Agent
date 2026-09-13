#!/usr/bin/env python3
"""Main experiment runner for H-M1: Granularity Effect on Repair Success.

This script tests whether error feedback granularity (G0-G4) has a statistically
significant effect on LLM repair success rate using one-way ANOVA.

Gate condition: ANOVA p < 0.05 (significant effect of granularity)
"""

import argparse
import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime

# Add current directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import RepairConfig, repair_config_to_experiment_config, GRANULARITY_LEVELS
from data import load_runtime_error_cases, load_mbpp_index
from repair import run_repair_experiment
from analyze import aggregate_by_granularity, run_anova, run_posthoc
from evaluate import save_results, generate_all_figures
from model import CodeGenerator


# Exit codes
GATE_EXIT_PASS = 0
GATE_EXIT_FAIL = 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="H-M1: Granularity Effect on Repair Success Experiment"
    )
    parser.add_argument(
        "--gpu", type=int, default=0,
        help="GPU device ID (default: 0)"
    )
    parser.add_argument(
        "--results-dir", type=str, default="results",
        help="Directory for output files (default: results)"
    )
    parser.add_argument(
        "--h-e1-results", type=str, default="data/h_e1_results.json",
        help="Path to H-E1 execution_results.json (default: data/h_e1_results.json)"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume from checkpoint if available"
    )
    parser.add_argument(
        "--skip-repair", action="store_true",
        help="Skip repair experiment, use existing results for analysis"
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point for H-M1 experiment.

    Pipeline:
      1. Load H-E1 runtime error cases (304)
      2. Load MBPP index for task text + test_list
      3. Load CodeLlama-7B-Instruct (same as H-E1)
      4. Run 1,520 repair attempts (304 x 5 granularity levels)
      5. ANOVA analysis
      6. Post-hoc Tukey HSD (if significant)
      7. Save results + generate figures
      8. Report gate: ANOVA p < 0.05

    Returns:
        Exit code: 0 if gate passes, 1 if fails
    """
    args = parse_args()

    # Set GPU
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
    print(f"Using GPU: {args.gpu}")

    # Initialize config
    config = RepairConfig(
        h_e1_results_path=args.h_e1_results,
        results_dir=args.results_dir,
        figures_dir="figures",
        checkpoint_path=f"{args.results_dir}/checkpoint.json",
    )

    # Create output directories
    Path(config.results_dir).mkdir(parents=True, exist_ok=True)
    Path(config.figures_dir).mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("H-M1: Granularity Effect on Repair Success")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Granularity levels: {GRANULARITY_LEVELS}")
    print(f"H-E1 results: {config.h_e1_results_path}")
    print(f"Output directory: {config.results_dir}")
    print(f"Gate condition: ANOVA p < {config.anova_alpha}")
    print("=" * 60)

    # Step 1: Load H-E1 runtime error cases
    print("\n[Step 1/7] Loading H-E1 runtime error cases...")
    runtime_cases = load_runtime_error_cases(config)
    print(f"Loaded {len(runtime_cases)} runtime error cases")

    # Step 2: Load MBPP index
    print("\n[Step 2/7] Loading MBPP dataset index...")
    mbpp_index = load_mbpp_index(config)
    print(f"Loaded {len(mbpp_index)} MBPP tasks")

    # Check if we should skip repair and use existing results
    if args.skip_repair and os.path.exists(config.output_json):
        print("\n[Step 3/7] Skipping repair (--skip-repair), loading existing results...")
        with open(config.output_json, "r") as f:
            results = json.load(f)
        print(f"Loaded {len(results)} existing repair results")
    else:
        # Step 3: Load model
        print("\n[Step 3/7] Loading CodeLlama-7B-Instruct model...")
        exp_config = repair_config_to_experiment_config(config)
        generator = CodeGenerator(exp_config)
        generator.load()

        # Step 4: Run repair experiment
        print("\n[Step 4/7] Running repair experiment...")
        print(f"Total attempts: {len(runtime_cases)} cases x {len(GRANULARITY_LEVELS)} levels = {len(runtime_cases) * len(GRANULARITY_LEVELS)}")
        results = run_repair_experiment(runtime_cases, mbpp_index, generator, config)
        print(f"Completed {len(results)} repair attempts")

    # Step 5: Aggregate and analyze
    print("\n[Step 5/7] Running ANOVA analysis...")
    groups = aggregate_by_granularity(results)

    print("\nSuccess rates per granularity:")
    for g in GRANULARITY_LEVELS:
        rate = sum(groups[g]) / len(groups[g]) if groups[g] else 0
        print(f"  {g}: {sum(groups[g])}/{len(groups[g])} = {rate:.2%}")

    metrics = run_anova(groups, config)
    print(f"\nANOVA Results:")
    print(f"  F-statistic: {metrics['f_statistic']:.4f}")
    print(f"  p-value: {metrics['p_value']:.6f}")
    print(f"  eta-squared: {metrics['eta_squared']:.4f}")
    print(f"  Gate passed: {metrics['gate_passed']}")

    # Step 6: Post-hoc analysis (if significant)
    posthoc = None
    if metrics["gate_passed"]:
        print("\n[Step 6/7] Running Tukey HSD post-hoc analysis...")
        posthoc = run_posthoc(groups)
        print("Significant pairwise comparisons:")
        sig_count = 0
        for key, val in posthoc.items():
            if val["significant"]:
                print(f"  {key}: p = {val['p_value']:.4f}")
                sig_count += 1
        if sig_count == 0:
            print("  (no significant pairwise differences)")
    else:
        print("\n[Step 6/7] Skipping post-hoc (ANOVA not significant)")

    # Step 7: Save results and generate figures
    print("\n[Step 7/7] Saving results and generating figures...")
    save_results(results, metrics, posthoc, config)
    generate_all_figures(results, groups, metrics, posthoc, config)

    # Final gate verdict
    print("\n" + "=" * 60)
    if metrics["gate_passed"]:
        print("GATE RESULT: PASS")
        print(f"  ANOVA p = {metrics['p_value']:.6f} < {config.anova_alpha}")
        print(f"  Effect size (eta-squared) = {metrics['eta_squared']:.4f}")
        print("  Conclusion: Granularity has significant effect on repair success")
        exit_code = GATE_EXIT_PASS
    else:
        print("GATE RESULT: FAIL")
        print(f"  ANOVA p = {metrics['p_value']:.6f} >= {config.anova_alpha}")
        print("  Conclusion: No significant effect of granularity detected")
        exit_code = GATE_EXIT_FAIL

    print("=" * 60)
    print(f"End time: {datetime.now().isoformat()}")

    # Save experiment summary
    summary = {
        "hypothesis": "h-m1",
        "title": "Granularity Effect on Repair Success",
        "completed_at": datetime.now().isoformat(),
        "gate_type": "MUST_WORK",
        "gate_condition": f"ANOVA p < {config.anova_alpha}",
        "gate_passed": metrics["gate_passed"],
        "metrics": {
            "f_statistic": float(metrics["f_statistic"]),
            "p_value": float(metrics["p_value"]),
            "eta_squared": float(metrics["eta_squared"]),
            "success_rates": {k: float(v) for k, v in metrics["success_rates"].items()},
            "n_per_group": int(metrics["n_per_group"]),
        },
        "total_repair_attempts": len(results),
        "runtime_cases": len(runtime_cases),
    }

    with open(f"{config.results_dir}/experiment_summary.yaml", "w") as f:
        yaml.dump(summary, f, default_flow_style=False)
    print(f"Saved experiment summary to {config.results_dir}/experiment_summary.yaml")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
