"""
Main experiment runner for h-e3.
Runs 50-epoch Waterbirds training with GradCAM temporal ratio tracking.
"""

import os
import sys
from train import TrainConfig, run_experiment
from validation import check_poc_pass, plot_temporal_ratio, save_results, compute_delta


def main():
    # Experiment config (PoC: single seed CMNIST, Waterbirds download failed)
    config = TrainConfig(
        dataset='CMNIST',
        lr=0.001,
        max_epochs=50,
        batch_size=128,
        seed=0,
        tracking_interval=5  # Track every 5 epochs
    )

    print("="*60)
    print("h-e3: GradCAM Temporal Ratio Tracking Experiment")
    print("="*60)

    # Run experiment
    results = run_experiment(config)

    # Compute delta explicitly
    if results['delta'] is None:
        results['delta'] = compute_delta(results['R_temporal_history'])

    # Save results
    output_dir = '../results'
    save_results(results, output_dir)

    # Generate visualizations
    figures_dir = '../figures'
    os.makedirs(figures_dir, exist_ok=True)
    plot_path = os.path.join(figures_dir, 'R_temporal_vs_epoch.png')
    plot_temporal_ratio(results['R_temporal_history'], plot_path)

    # PoC validation
    poc_pass = check_poc_pass(results)

    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"R_temporal history: {results['R_temporal_history']}")
    print(f"Delta (R(5) - R(50)): {results['delta']:.4f}")
    print(f"Worst-group accuracy: {results['worst_group_acc']:.4f}")
    print(f"PoC Pass: {poc_pass}")
    print("="*60)

    # Return results for validation report generation
    return results, poc_pass


if __name__ == '__main__':
    main()
