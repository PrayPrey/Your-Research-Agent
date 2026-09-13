#!/usr/bin/env python3
"""
H-M3: Stratified Correlation Comparison (Fisher z-Test)
Main experiment execution script
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import CachedResultsLoader
from fisher_z_test import FisherZTest
from gate_validator import MechanismGateValidator
from visualizer import ComparisonVisualizer
from report_generator import ValidationReportGenerator
from config import load_config


def main():
    """Main experiment execution for h-m3."""
    print("="*80)
    print("H-M3: Stratified Correlation Comparison (Fisher z-Test)")
    print("="*80)
    print()

    # Load configuration
    config = load_config()
    print("✓ Configuration loaded")

    # Load cached correlation results from H-M1
    print("\n" + "="*80)
    print("LOADING CACHED RESULTS FROM H-M1")
    print("="*80)
    loader = CachedResultsLoader(config.h_m1_output_path)
    results_df = loader.load_correlation_results()
    print(f"✓ Loaded results from {config.h_m1_output_path}")

    # Verify data format
    if not loader.validate_cached_data(results_df):
        raise ValueError("Invalid H-M1 cached data format")
    print("✓ Data validation passed")

    # Extract per-stratum correlations
    factual_corr = loader.get_factual_correlation(results_df)
    misinfo_corr = loader.get_misinfo_correlation(results_df)

    print(f"\nFactual stratum:")
    print(f"  r = {factual_corr['r']:.4f}, p = {factual_corr['p_value']:.6f}, n = {factual_corr['n']}")
    print(f"  95% CI: [{factual_corr['ci_lower']:.4f}, {factual_corr['ci_upper']:.4f}]")

    print(f"\nMisinformation stratum:")
    print(f"  r = {misinfo_corr['r']:.4f}, p = {misinfo_corr['p_value']:.6f}, n = {misinfo_corr['n']}")
    print(f"  95% CI: [{misinfo_corr['ci_lower']:.4f}, {misinfo_corr['ci_upper']:.4f}]")

    # Fisher z-test comparison
    print("\n" + "="*80)
    print("FISHER Z-TEST COMPARISON")
    print("="*80)
    fisher_test = FisherZTest(alpha=config.fisher_test.alpha)
    fisher_result = fisher_test.compare_correlations(
        r1=factual_corr["r"],
        n1=factual_corr["n"],
        r2=misinfo_corr["r"],
        n2=misinfo_corr["n"]
    )

    print(f"z-statistic: {fisher_result['z_stat']:.4f}")
    print(f"p-value: {fisher_result['p_value']:.6f}")
    print(f"Significant: {fisher_result['significant']}")
    print(f"Correlation difference: Δr = {fisher_result['delta_r']:.4f}")

    # Compute confidence intervals
    ci_factual = fisher_test.compute_confidence_intervals(factual_corr["r"], factual_corr["n"])
    ci_misinfo = fisher_test.compute_confidence_intervals(misinfo_corr["r"], misinfo_corr["n"])

    print(f"\n95% Confidence Intervals:")
    print(f"  Factual: [{ci_factual[0]:.4f}, {ci_factual[1]:.4f}]")
    print(f"  Misinfo: [{ci_misinfo[0]:.4f}, {ci_misinfo[1]:.4f}]")

    # Compute effect size
    effect_size = fisher_test.compute_effect_size(factual_corr["r"], misinfo_corr["r"])
    print(f"\nEffect size:")
    print(f"  Cohen's q = {effect_size['cohens_q']:.4f} ({effect_size['magnitude']})")

    # Gate validation
    print("\n" + "="*80)
    print("SHOULD_WORK GATE EVALUATION")
    print("="*80)
    validator = MechanismGateValidator(
        p_threshold=config.gate.p_threshold,
        delta_r_threshold=config.gate.delta_r_threshold
    )
    gate_result = validator.evaluate_gate(
        fisher_result,
        factual_corr["r"],
        misinfo_corr["r"]
    )

    print(f"Primary (p < 0.05): {'✓ PASS' if gate_result['primary'] else '✗ FAIL'}")
    print(f"Secondary (|Δr| >= 0.1): {'✓ PASS' if gate_result['secondary'] else '✗ FAIL'}")
    print(f"Tertiary (directional): {'✓ PASS' if gate_result['tertiary'] else '✗ FAIL'}")
    print()
    print(f"Gate result: {gate_result['result']}")
    print("="*80)

    # Visualization
    visualizer = ComparisonVisualizer(config.figures_dir)
    visualizer.generate_all_figures({
        "fisher": fisher_result,
        "factual": {**factual_corr, "ci": ci_factual},
        "misinfo": {**misinfo_corr, "ci": ci_misinfo},
        "effect_size": effect_size,
        "gate": gate_result
    })

    # Generate validation report
    print("\n" + "="*80)
    print("GENERATING VALIDATION REPORT")
    print("="*80)
    report_gen = ValidationReportGenerator(
        os.path.join("..", "04_validation.md")
    )
    report_gen.generate_report(fisher_result, gate_result, {
        "factual": factual_corr,
        "misinfo": misinfo_corr
    }, effect_size)

    # Save results
    report_gen.save_results_json({
        "fisher_test": fisher_result,
        "correlations": {"factual": factual_corr, "misinfo": misinfo_corr},
        "effect_size": effect_size,
        "gate": gate_result
    }, os.path.join(config.output_dir, "fisher_test_results.json"))

    print("\n" + "="*80)
    print("EXPERIMENT COMPLETE")
    print("="*80)
    print(f"Gate result: {gate_result['result']}")
    print("="*80)

    return 0 if gate_result['passed'] else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
