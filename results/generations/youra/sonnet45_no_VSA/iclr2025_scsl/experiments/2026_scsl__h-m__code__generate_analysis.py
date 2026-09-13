"""Generate statistical analysis and visualizations from saved results."""
import pandas as pd
from pathlib import Path
import json
import sys
sys.path.append('/workspace/TEST_scsl/docs/youra_research/h-m/code')
from statistics import compute_spearman_correlation, aggregate_seed_results, test_rotation_control
from visualize import plot_dose_response_curve, plot_seed_variability_boxplot, plot_scatter_with_regression
from config import OUTPUT_CONFIG


def main():
    output_dir = Path(OUTPUT_CONFIG['output_dir'])

    # Load results
    print("Loading results from CSV...")
    results_df = pd.read_csv(output_dir / OUTPUT_CONFIG['results_file'])

    # Compute statistics
    print("Computing statistical tests...")
    spearman_test = compute_spearman_correlation(results_df)
    aggregated_stats = aggregate_seed_results(results_df)
    rotation_control = test_rotation_control(results_df)

    stats_report = {
        'spearman_test': spearman_test,
        'aggregated_stats': aggregated_stats.to_dict('records'),
        'rotation_control': rotation_control
    }

    # Save statistical report
    with open(output_dir / OUTPUT_CONFIG['stats_file'], 'w') as f:
        json.dump(stats_report, f, indent=2)
    print(f"Statistics saved to: {output_dir / OUTPUT_CONFIG['stats_file']}")

    # Generate visualizations
    print("Generating visualizations...")
    figures_dir = output_dir / OUTPUT_CONFIG['figures_dir']
    figures_dir.mkdir(parents=True, exist_ok=True)

    plot_dose_response_curve(
        aggregated_stats,
        spearman_test,
        str(figures_dir / 'dose_response_curve.png')
    )
    print(f"Saved: {figures_dir / 'dose_response_curve.png'}")

    plot_seed_variability_boxplot(
        results_df,
        str(figures_dir / 'seed_variability_boxplot.png')
    )
    print(f"Saved: {figures_dir / 'seed_variability_boxplot.png'}")

    plot_scatter_with_regression(
        results_df,
        spearman_test,
        str(figures_dir / 'scatter_regression.png')
    )
    print(f"Saved: {figures_dir / 'scatter_regression.png'}")

    # Validate gate
    print("\nValidating SHOULD_WORK gate...")
    checks = {
        'spearman_negative': spearman_test['rho'] < 0,
        'spearman_significant': spearman_test['p_value'] < 0.05,
        'rotation_control_passed': rotation_control['within_threshold']
    }

    primary_passed = checks['spearman_negative'] and checks['spearman_significant']

    gate_decision = {
        'hypothesis': 'h-m',
        'gate_type': 'SHOULD_WORK',
        'primary_passed': bool(primary_passed),
        'action': 'PROCEED' if primary_passed else 'DOCUMENT_LIMITATION',
        'checks': {k: bool(v) for k, v in checks.items()},
        'spearman_test': spearman_test,
        'rotation_control': rotation_control
    }

    # Save gate decision
    with open(output_dir / OUTPUT_CONFIG['gate_file'], 'w') as f:
        json.dump(gate_decision, f, indent=2)
    print(f"Gate decision saved to: {output_dir / OUTPUT_CONFIG['gate_file']}")

    # Print gate decision
    print("\n" + "="*60)
    print(f"GATE VALIDATION: {gate_decision['action']}")
    print("="*60)
    print(f"Spearman ρ: {spearman_test['rho']:.3f}")
    print(f"p-value: {spearman_test['p_value']:.4f}")
    print(f"Interpretation: {spearman_test['interpretation']}")
    print(f"\nChecks:")
    for check, result in checks.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check}: {result}")

    return 0 if primary_passed else 1


if __name__ == "__main__":
    sys.exit(main())
