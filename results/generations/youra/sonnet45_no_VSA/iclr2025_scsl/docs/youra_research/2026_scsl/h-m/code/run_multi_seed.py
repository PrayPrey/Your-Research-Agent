"""Multi-seed orchestrator for dose-response validation."""
import pandas as pd
from pathlib import Path
from itertools import product
import json
from typing import Dict
import torch
import sys
sys.path.append('/workspace/TEST_scsl/docs/youra_research/h-m/code')
from train import train_condition_with_seed
from evaluate import compute_per_class_accuracy
from data import get_dataloaders
from statistics import compute_spearman_correlation, aggregate_seed_results, test_rotation_control
from visualize import plot_dose_response_curve, plot_seed_variability_boxplot, plot_scatter_with_regression
from config import TRAINING_CONFIG, OUTPUT_CONFIG, EXPERIMENT_CONFIG


def run_all_seeds_and_conditions() -> pd.DataFrame:
    """
    Execute 5 conditions × 5 seeds = 25 training runs.

    Returns:
        DataFrame with columns: [condition, seed, overall_acc, asymmetric_acc, symmetric_acc, class_0-9]
    """
    results = []
    device = torch.device(TRAINING_CONFIG["device"])
    conditions = EXPERIMENT_CONFIG["conditions"]
    seeds = TRAINING_CONFIG["seeds"]

    total_runs = len(conditions) * len(seeds)
    current_run = 0

    for condition, seed in product(conditions, seeds):
        current_run += 1
        print(f"\n{'='*60}")
        print(f"Run {current_run}/{total_runs}: {condition} | Seed: {seed}")
        print(f"{'='*60}")

        # Train
        train_result = train_condition_with_seed(
            condition,
            seed,
            epochs=TRAINING_CONFIG["epochs"]
        )

        # Evaluate
        _, test_loader = get_dataloaders(
            condition,
            TRAINING_CONFIG["batch_size"],
            seed
        )
        metrics = compute_per_class_accuracy(train_result['model'], test_loader, device)

        # Store result
        row = {
            'condition': condition,
            'seed': seed,
            'overall_acc': metrics['overall_acc'],
            'asymmetric_acc': metrics['asymmetric_mean'],
            'symmetric_acc': metrics['symmetric_mean']
        }
        # Add per-class accuracies
        for i, acc in enumerate(metrics['per_class']):
            row[f'class_{i}'] = acc

        results.append(row)
        print(f"Results: Overall={metrics['overall_acc']:.2f}%, "
              f"Asym={metrics['asymmetric_mean']:.2f}%, "
              f"Sym={metrics['symmetric_mean']:.2f}%")

    return pd.DataFrame(results)


def save_results_csv(results_df: pd.DataFrame, output_path: str):
    """Save results in CSV format."""
    results_df.to_csv(output_path, index=False)
    print(f"\nResults saved to: {output_path}")


def generate_statistical_report(results_df: pd.DataFrame) -> Dict:
    """
    Compute all statistical tests.

    Returns:
        {spearman_test, rotation_control, aggregated_stats}
    """
    # Compute tests
    spearman_test = compute_spearman_correlation(results_df)
    aggregated_stats = aggregate_seed_results(results_df)
    rotation_control = test_rotation_control(results_df)

    return {
        'spearman_test': spearman_test,
        'aggregated_stats': aggregated_stats.to_dict('records'),
        'rotation_control': rotation_control
    }


def validate_gate_criteria(stats: Dict) -> Dict:
    """
    Check SHOULD_WORK gate criteria.

    Returns:
        {passed, checks, action, details}
    """
    spearman = stats['spearman_test']
    rotation = stats['rotation_control']

    checks = {
        'spearman_negative': spearman['rho'] < 0,
        'spearman_significant': spearman['p_value'] < 0.05,
        'rotation_control_passed': rotation['within_threshold']
    }

    primary_passed = checks['spearman_negative'] and checks['spearman_significant']

    return {
        'passed': primary_passed,
        'checks': checks,
        'action': 'PROCEED' if primary_passed else 'DOCUMENT_LIMITATION',
        'gate_type': 'SHOULD_WORK',
        'details': {
            'rho': spearman['rho'],
            'p_value': spearman['p_value'],
            'interpretation': spearman['interpretation']
        }
    }


def main():
    """
    Main execution flow:
    1. Run 25 training runs
    2. Aggregate results
    3. Compute statistical tests
    4. Generate visualizations
    5. Save outputs
    6. Validate SHOULD_WORK gate
    """
    print("="*60)
    print("H-M Experiment: Dose-Response Validation")
    print("Total runs: 5 conditions × 5 seeds = 25 runs")
    print("="*60)

    # Step 1: Run all experiments
    results_df = run_all_seeds_and_conditions()

    # Step 2: Save CSV
    output_dir = Path(OUTPUT_CONFIG['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    save_results_csv(results_df, str(output_dir / OUTPUT_CONFIG['results_file']))

    # Step 3: Compute statistics
    print("\n" + "="*60)
    print("Computing statistical tests...")
    print("="*60)
    stats_report = generate_statistical_report(results_df)

    # Step 4: Save statistical report
    with open(output_dir / OUTPUT_CONFIG['stats_file'], 'w') as f:
        json.dump(stats_report, f, indent=2)
    print(f"Statistics saved to: {output_dir / OUTPUT_CONFIG['stats_file']}")

    # Step 5: Generate visualizations
    print("\n" + "="*60)
    print("Generating visualizations...")
    print("="*60)
    figures_dir = output_dir / OUTPUT_CONFIG['figures_dir']
    figures_dir.mkdir(parents=True, exist_ok=True)

    aggregated_df = aggregate_seed_results(results_df)

    plot_dose_response_curve(
        aggregated_df,
        stats_report['spearman_test'],
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
        stats_report['spearman_test'],
        str(figures_dir / 'scatter_regression.png')
    )
    print(f"Saved: {figures_dir / 'scatter_regression.png'}")

    # Step 6: Validate gate
    print("\n" + "="*60)
    print("Validating SHOULD_WORK gate...")
    print("="*60)
    gate_decision = validate_gate_criteria(stats_report)

    # Save gate decision
    with open(output_dir / OUTPUT_CONFIG['gate_file'], 'w') as f:
        json.dump({
            'hypothesis': 'h-m',
            'gate_type': 'SHOULD_WORK',
            'primary_passed': gate_decision['passed'],
            'action': gate_decision['action'],
            'checks': gate_decision['checks'],
            'spearman_test': stats_report['spearman_test'],
            'rotation_control': stats_report['rotation_control']
        }, f, indent=2)
    print(f"Gate decision saved to: {output_dir / OUTPUT_CONFIG['gate_file']}")

    # Print gate decision
    print("\n" + "="*60)
    print(f"GATE VALIDATION: {gate_decision['action']}")
    print("="*60)
    print(f"Spearman ρ: {gate_decision['details']['rho']:.3f}")
    print(f"p-value: {gate_decision['details']['p_value']:.4f}")
    print(f"Interpretation: {gate_decision['details']['interpretation']}")
    print(f"\nChecks:")
    for check, result in gate_decision['checks'].items():
        status = "✓" if result else "✗"
        print(f"  {status} {check}: {result}")

    return 0 if gate_decision['passed'] else 1


if __name__ == "__main__":
    sys.exit(main())
