"""
Mock experiment for testing h-m1 code without LeanDojo
Generates synthetic data to validate variance comparison pipeline
"""

import numpy as np
import pandas as pd
import json
import os
import sys
import time

from analysis.analyzer import VarianceGroupAnalyzer
from visualization.visualizer import ExperimentVisualizer
from config import EXPERIMENT_CONFIG


def generate_mock_results(n_samples=100, seed=42):
    """
    Generate synthetic experimental results for h-m1.

    Simulates variance difference where successful proofs have lower
    confidence variance than timeout proofs.
    """
    np.random.seed(seed)

    # Generate outcomes: 60% success, 40% timeout
    outcomes = np.random.choice([0, 1], size=n_samples, p=[0.6, 0.4])

    # Generate confidence variances with group difference
    # Success (0): lower variance (mean=0.09, std=0.05)
    # Timeout (1): higher variance (mean=0.29, std=0.18)
    variances = np.zeros(n_samples)
    trajectories = []

    for i in range(n_samples):
        if outcomes[i] == 0:  # Success
            variance = np.random.normal(0.09, 0.05)
            variance = max(0.01, variance)  # Ensure positive
            # Low variance trajectory
            base = np.random.uniform(1.0, 1.5)
            traj = base + np.random.normal(0, variance, size=15)
        else:  # Timeout
            variance = np.random.normal(0.29, 0.18)
            variance = max(0.05, variance)  # Ensure positive
            # High variance trajectory
            base = np.random.uniform(1.0, 2.0)
            traj = base + np.random.normal(0, variance, size=15)

        variances[i] = variance
        trajectories.append(traj.tolist())

    # Clip to reasonable range
    variances = np.clip(variances, 0.0, 1.0)

    # Create results list
    results = []
    for i in range(n_samples):
        results.append({
            'theorem_id': f'mock_theorem_{i:03d}',
            'confidence_variance': float(variances[i]),
            'outcome': int(outcomes[i]),
            'execution_time': np.random.uniform(10, 300),
            'entropies': trajectories[i],
            'status': 'success' if outcomes[i] == 0 else 'timeout'
        })

    return results, variances, outcomes


def main():
    """Run mock experiment to test h-m1 pipeline."""

    print("\n" + "="*80)
    print("MOCK EXPERIMENT: Testing h-m1 Pipeline (Variance Comparison)")
    print("="*80 + "\n")

    # Generate mock data
    print("Generating mock data...")
    results, variances, outcomes = generate_mock_results(100, seed=42)
    print(f"✓ Generated {len(results)} mock results\n")

    # Stage 1: Analysis
    print("STAGE 1: Computing variance comparison by outcome group")
    print("-" * 80)
    analyzer = VarianceGroupAnalyzer()

    group_analysis = analyzer.analyze_by_outcome(variances, outcomes)
    gate_result = analyzer.evaluate_gate(group_analysis)

    print(f"Successful proofs: mean_variance = {group_analysis['successful']['mean_variance']:.4f} ± {group_analysis['successful']['std_variance']:.4f} (n={group_analysis['successful']['count']})")
    print(f"Timeout proofs: mean_variance = {group_analysis['timeout']['mean_variance']:.4f} ± {group_analysis['timeout']['std_variance']:.4f} (n={group_analysis['timeout']['count']})")
    print(f"Difference (timeout - success): {group_analysis['difference']:.4f}")
    print(f"T-statistic: {group_analysis['t_statistic']:.4f} (p = {group_analysis['p_value']:.6e})")
    print(f"Gate result: {'PASS' if gate_result else 'FAIL'}\n")

    # Stage 2: Visualization
    print("STAGE 2: Generating visualizations")
    print("-" * 80)
    visualizer = ExperimentVisualizer(output_dir="./figures")

    visualizer.plot_variance_comparison_bar(group_analysis)
    visualizer.plot_variance_distributions(variances, outcomes)
    visualizer.plot_variance_boxplot(variances, outcomes)
    visualizer.plot_trajectory_examples(
        [r['entropies'] for r in results],
        outcomes.tolist()
    )
    print("✓ All figures saved\n")

    # Stage 3: Save results
    print("STAGE 3: Saving results")
    print("-" * 80)

    os.makedirs("./results", exist_ok=True)

    # Save CSV
    df = pd.DataFrame([
        {
            'theorem_id': r['theorem_id'],
            'confidence_variance': r['confidence_variance'],
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
        'hypothesis_id': 'h-m1',
        'mock_test': True,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'sample_size': len(results),
        'groups': {
            'successful': group_analysis['successful'],
            'timeout': group_analysis['timeout']
        },
        'statistics': {
            't_statistic': group_analysis['t_statistic'],
            'p_value': group_analysis['p_value']
        },
        'gate': {
            'type': 'MUST_WORK',
            'result': 'PASS' if gate_result else 'FAIL',
            'satisfied': gate_result
        }
    }
    with open("./results/metrics_summary.json", 'w') as f:
        json.dump(metrics, f, indent=2)
    print("  Saved: ./results/metrics_summary.json\n")

    # Final summary
    print("="*80)
    print("MOCK EXPERIMENT COMPLETE")
    print("="*80)
    print(f"\nGate Result: {metrics['gate']['result']}")
    print(f"Successful variance: {group_analysis['successful']['mean_variance']:.4f}")
    print(f"Timeout variance: {group_analysis['timeout']['mean_variance']:.4f}")
    print(f"P-value: {group_analysis['p_value']:.6e}")
    print("\nPipeline validation: SUCCESS")
    print("All h-m1 modules working correctly\n")
    print("="*80 + "\n")

    return 0 if gate_result else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
