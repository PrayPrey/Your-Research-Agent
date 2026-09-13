"""
Mock experiment for testing h-e1 code without LeanDojo
Generates synthetic data to validate pipeline
"""

import numpy as np
import pandas as pd
import json
import os
import sys

from analysis.analyzer import CorrelationAnalyzer
from visualization.visualizer import ExperimentVisualizer
from config import EXPERIMENT_CONFIG


def generate_mock_results(n_samples=100, seed=42):
    """
    Generate synthetic experimental results.

    Simulates correlation where higher confidence derivatives
    correlate with timeout outcomes.
    """
    np.random.seed(seed)

    # Generate outcomes: 60% success, 40% timeout
    outcomes = np.random.choice([0, 1], size=n_samples, p=[0.6, 0.4])

    # Generate confidence derivatives with correlation
    # Success (0): lower derivatives (mean=0.2, std=0.1)
    # Timeout (1): higher derivatives (mean=0.5, std=0.15)
    derivatives = np.zeros(n_samples)
    for i in range(n_samples):
        if outcomes[i] == 0:  # Success
            derivatives[i] = np.random.normal(0.2, 0.1)
        else:  # Timeout
            derivatives[i] = np.random.normal(0.5, 0.15)

    # Clip to reasonable range
    derivatives = np.clip(derivatives, 0.0, 1.5)

    # Generate mock entropy trajectories
    trajectories = []
    for i in range(n_samples):
        if outcomes[i] == 0:  # Success: low variance
            base = np.random.uniform(1.0, 1.5)
            traj = base + np.random.normal(0, 0.05, size=15)
        else:  # Timeout: high variance
            base = np.random.uniform(1.0, 2.0)
            traj = base + np.random.normal(0, 0.3, size=15)
        trajectories.append(traj.tolist())

    # Create results list
    results = []
    for i in range(n_samples):
        results.append({
            'theorem_id': f'mock_theorem_{i:03d}',
            'confidence_derivative': float(derivatives[i]),
            'outcome': int(outcomes[i]),
            'execution_time': np.random.uniform(10, 300),
            'entropies': trajectories[i],
            'status': 'success' if outcomes[i] == 0 else 'timeout'
        })

    return results, derivatives, outcomes


def main():
    """Run mock experiment to test pipeline."""

    print("\n" + "="*80)
    print("MOCK EXPERIMENT: Testing h-e1 Pipeline")
    print("="*80 + "\n")

    # Generate mock data
    print("Generating mock data...")
    results, derivatives, outcomes = generate_mock_results(100, seed=42)
    print(f"✓ Generated {len(results)} mock results\n")

    # Stage 1: Analysis
    print("STAGE 1: Computing correlations")
    print("-" * 80)
    analyzer = CorrelationAnalyzer()

    r, p_r = analyzer.compute_pearson(derivatives, outcomes)
    rho, p_rho = analyzer.compute_spearman(derivatives, outcomes)
    auc_score = analyzer.compute_auc(derivatives, outcomes)
    gate_result = analyzer.evaluate_gate(r, rho, threshold=0.3)

    print(f"Pearson r = {r:.4f} (p = {p_r:.6f})")
    print(f"Spearman ρ = {rho:.4f} (p = {p_rho:.6f})")
    print(f"AUC = {auc_score:.4f}")
    print(f"Gate result: {'PASS' if gate_result else 'FAIL'}\n")

    summary_stats = analyzer.compute_summary_statistics(derivatives, outcomes)
    print("Summary Statistics:")
    print(f"  Success: mean={summary_stats['success']['mean']:.4f}, std={summary_stats['success']['std']:.4f}")
    print(f"  Timeout: mean={summary_stats['timeout']['mean']:.4f}, std={summary_stats['timeout']['std']:.4f}\n")

    # Stage 2: Visualization
    print("STAGE 2: Generating visualizations")
    print("-" * 80)
    visualizer = ExperimentVisualizer(output_dir="./figures")

    visualizer.plot_gate_metrics(r, rho, p_r, p_rho)
    visualizer.plot_scatter(derivatives, outcomes)
    visualizer.plot_distributions(derivatives, outcomes)
    visualizer.plot_trajectory_examples(
        [r['entropies'] for r in results],
        outcomes.tolist()
    )
    visualizer.plot_roc_curve(derivatives, outcomes)
    print("✓ All figures saved\n")

    # Stage 3: Save results
    print("STAGE 3: Saving results")
    print("-" * 80)

    os.makedirs("./results", exist_ok=True)

    # Save CSV
    df = pd.DataFrame([
        {
            'theorem_id': r['theorem_id'],
            'confidence_derivative': r['confidence_derivative'],
            'outcome': r['outcome'],
            'execution_time': r['execution_time'],
            'status': r['status']
        }
        for r in results
    ])
    df.to_csv("./results/results_raw.csv", index=False)
    print("  Saved: ./results/results_raw.csv")

    # Save metrics
    metrics = {
        'correlation_pearson': {'r': r, 'p_value': p_r},
        'correlation_spearman': {'rho': rho, 'p_value': p_rho},
        'auc': auc_score,
        'gate_result': 'PASS' if gate_result else 'FAIL',
        'sample_size': len(results),
        'summary_statistics': summary_stats
    }
    with open("./results/metrics_summary.json", 'w') as f:
        json.dump(metrics, f, indent=2)
    print("  Saved: ./results/metrics_summary.json\n")

    # Final summary
    print("="*80)
    print("MOCK EXPERIMENT COMPLETE")
    print("="*80)
    print(f"\nGate Result: {metrics['gate_result']}")
    print(f"Pearson r: {r:.4f}")
    print(f"Spearman ρ: {rho:.4f}")
    print("\nPipeline validation: SUCCESS")
    print("All modules working correctly\n")
    print("="*80 + "\n")

    return 0 if gate_result else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
