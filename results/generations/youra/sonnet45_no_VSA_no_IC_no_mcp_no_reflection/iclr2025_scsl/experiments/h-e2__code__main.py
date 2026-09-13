"""
Main experiment launcher for h-e2.
"""

import sys
import os
from train import run_single_experiment_with_tracking, TrainConfig
from evaluate import check_poc_pass, plot_gate_metrics, plot_rolling_variance, generate_validation_report
from config import EXTENDED_TRAIN_CONFIG, OUTPUT_CONFIG, PLOT_CONFIG

def main():
    # Create output directories
    os.makedirs(OUTPUT_CONFIG['results_dir'], exist_ok=True)
    os.makedirs(OUTPUT_CONFIG['figures_dir'], exist_ok=True)

    # Run experiment with tracking
    config = TrainConfig(
        dataset=EXTENDED_TRAIN_CONFIG['dataset'],
        lr=EXTENDED_TRAIN_CONFIG['lr'],
        max_epochs=EXTENDED_TRAIN_CONFIG['max_epochs'],
        weight_decay=EXTENDED_TRAIN_CONFIG['weight_decay'],
        batch_size=EXTENDED_TRAIN_CONFIG['batch_size'],
        seed=EXTENDED_TRAIN_CONFIG['seed']
    )

    print("Starting h-e2 experiment with gradient variance + forgetting tracking...")
    results = run_single_experiment_with_tracking(config)

    # Check gate
    print("\n" + "="*60)
    print("GATE EVALUATION")
    print("="*60)
    gate_passed = check_poc_pass(results)
    print(f"Variance ratio: {results['variance_ratio']:.4f} (threshold: 0.7)")
    print(f"Forgetting spurious: {results['forgetting_spurious']:.4f}")
    print(f"Forgetting core: {results['forgetting_core']:.4f}")
    print(f"\nGate result: {'PASS ✅' if gate_passed else 'FAIL ❌'}")

    # Generate visualizations
    print("\n" + "="*60)
    print("GENERATING VISUALIZATIONS")
    print("="*60)
    gate_metrics_path = os.path.join(OUTPUT_CONFIG['figures_dir'], OUTPUT_CONFIG['gate_plot'])
    variance_plot_path = os.path.join(OUTPUT_CONFIG['figures_dir'], OUTPUT_CONFIG['variance_plot'])

    plot_gate_metrics(results, gate_metrics_path)
    plot_rolling_variance(results, variance_plot_path)

    # Generate validation report
    print("\n" + "="*60)
    print("GENERATING VALIDATION REPORT")
    print("="*60)
    report_path = os.path.join(OUTPUT_CONFIG['results_dir'], '04_validation.md')
    generate_validation_report(results, gate_passed, report_path)

    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"Gate status: {'PASS' if gate_passed else 'FAIL'}")
    print(f"Results: {OUTPUT_CONFIG['results_dir']}/04_validation.md")
    print(f"Figures: {OUTPUT_CONFIG['figures_dir']}/")

    return 0 if gate_passed else 1


if __name__ == '__main__':
    sys.exit(main())
