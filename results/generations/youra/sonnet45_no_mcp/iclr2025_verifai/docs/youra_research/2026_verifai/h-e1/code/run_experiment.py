"""
Main Experiment Script for h-e1
Orchestrates full pipeline: sampling → execution → analysis → visualization → gate evaluation
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, Any

from config import EXPERIMENT_CONFIG
from data.loader import TheoremSampler
from experiment.runner import ExtendedTimeoutRunner
from analysis.analyzer import CorrelationAnalyzer
from visualization.visualizer import ExperimentVisualizer


class ExperimentOrchestrator:
    """Orchestrate full experiment pipeline."""

    def __init__(self, config: dict):
        """
        Initialize orchestrator with experiment configuration.

        Args:
            config: ExperimentConfig dict with all parameters
        """
        self.config = config
        self.sampler = None
        self.runner = None
        self.analyzer = None
        self.visualizer = None

    def run_full_experiment(self) -> Dict[str, Any]:
        """
        Execute full experiment pipeline.

        Returns:
            summary: {
                'correlation_pearson': {'r': float, 'p_value': float},
                'correlation_spearman': {'rho': float, 'p_value': float},
                'auc': float,
                'gate_result': str ('PASS' or 'FAIL'),
                'sample_size': int,
                'timeout_budget_seconds': int
            }
        """
        print("\n" + "="*80)
        print("H-E1 EXPERIMENT: Confidence-Timeout Correlation")
        print("="*80 + "\n")

        # Stage 1: Sample theorems
        print("STAGE 1: Sampling theorems from LeanDojo Benchmark")
        print("-" * 80)
        self.sampler = TheoremSampler(
            repo_url=self.config["repo_url"],
            commit_hash=self.config["commit_hash"],
            sample_size=self.config["sample_size"],
            seed=self.config["random_seed"]
        )
        benchmark = self.sampler.load_benchmark()
        theorems = self.sampler.sample_theorems(benchmark)
        print(f"✓ Sampled {len(theorems)} theorems\n")

        # Stage 2: Run experiments with confidence extraction
        print("STAGE 2: Running extended-timeout experiments")
        print("-" * 80)
        print(f"Timeout: {self.config['timeout_seconds']}s per theorem")
        print(f"Confidence window: {self.config['confidence_window']} steps")
        print(f"Estimated total time: ~{(self.config['timeout_seconds'] * len(theorems)) / 3600:.1f} hours\n")

        self.runner = ExtendedTimeoutRunner(
            timeout_seconds=self.config["timeout_seconds"],
            confidence_window=self.config["confidence_window"]
        )
        results = self.runner.run_batch(theorems)
        print(f"\n✓ Completed {len(results)} experiments\n")

        # Stage 3: Extract data for analysis
        print("STAGE 3: Extracting data for analysis")
        print("-" * 80)

        # Filter out errors
        valid_results = [r for r in results if r['confidence_derivative'] is not None]
        print(f"Valid results: {len(valid_results)}/{len(results)}")

        if len(valid_results) == 0:
            print("ERROR: No valid results. Cannot proceed with analysis.")
            return {
                'error': 'No valid results',
                'gate_result': 'FAIL'
            }

        confidence_derivatives = np.array([r['confidence_derivative'] for r in valid_results])
        outcomes = np.array([r['outcome'] for r in valid_results])

        print(f"Confidence derivatives range: [{confidence_derivatives.min():.4f}, {confidence_derivatives.max():.4f}]")
        print(f"Outcomes: {np.sum(outcomes == 0)} successes, {np.sum(outcomes == 1)} timeouts\n")

        # Stage 4: Compute correlations
        print("STAGE 4: Computing correlations")
        print("-" * 80)
        self.analyzer = CorrelationAnalyzer()

        r, p_r = self.analyzer.compute_pearson(confidence_derivatives, outcomes)
        rho, p_rho = self.analyzer.compute_spearman(confidence_derivatives, outcomes)
        auc_score = self.analyzer.compute_auc(confidence_derivatives, outcomes)
        gate_result = self.analyzer.evaluate_gate(r, rho, threshold=self.config["target_correlation"])

        print(f"Pearson r = {r:.4f} (p = {p_r:.6f})")
        print(f"Spearman ρ = {rho:.4f} (p = {p_rho:.6f})")
        print(f"AUC = {auc_score:.4f}")
        print(f"Gate threshold: {self.config['target_correlation']}")
        print(f"Gate result: {'PASS' if gate_result else 'FAIL'}\n")

        # Summary statistics
        summary_stats = self.analyzer.compute_summary_statistics(confidence_derivatives, outcomes)
        print("Summary Statistics:")
        print(f"  Success group: mean={summary_stats['success']['mean']:.4f}, std={summary_stats['success']['std']:.4f}, n={summary_stats['success']['count']}")
        print(f"  Timeout group: mean={summary_stats['timeout']['mean']:.4f}, std={summary_stats['timeout']['std']:.4f}, n={summary_stats['timeout']['count']}\n")

        # Stage 5: Generate visualizations
        print("STAGE 5: Generating visualizations")
        print("-" * 80)
        self.visualizer = ExperimentVisualizer(output_dir=self.config["figures_dir"])

        self.visualizer.plot_gate_metrics(r, rho, p_r, p_rho)
        self.visualizer.plot_scatter(confidence_derivatives, outcomes)
        self.visualizer.plot_distributions(confidence_derivatives, outcomes)
        self.visualizer.plot_trajectory_examples(
            [r['entropies'] for r in valid_results],
            outcomes.tolist()
        )
        self.visualizer.plot_roc_curve(confidence_derivatives, outcomes)
        print("✓ All figures saved\n")

        # Stage 6: Save results
        print("STAGE 6: Saving results")
        print("-" * 80)
        metrics = {
            'correlation_pearson': {'r': r, 'p_value': p_r},
            'correlation_spearman': {'rho': rho, 'p_value': p_rho},
            'auc': auc_score,
            'gate_result': 'PASS' if gate_result else 'FAIL',
            'sample_size': len(valid_results),
            'timeout_budget_seconds': self.config['timeout_seconds'],
            'confidence_window': self.config['confidence_window'],
            'summary_statistics': summary_stats
        }
        self.save_results(valid_results, metrics)
        print("✓ Results saved\n")

        # Stage 7: Gate evaluation
        print("STAGE 7: Gate Evaluation")
        print("=" * 80)
        print(f"\nGATE CONDITION: r > {self.config['target_correlation']} OR ρ > {self.config['target_correlation']}")
        print(f"RESULT: {metrics['gate_result']}")

        if not gate_result:
            print("\n⚠ WARNING: Gate condition FAILED")
            print(f"  Pearson r = {r:.4f} ≤ {self.config['target_correlation']}")
            print(f"  Spearman ρ = {rho:.4f} ≤ {self.config['target_correlation']}")
            print("\n  Hypothesis h-e1 REJECTED")
            print("  Recommendation: Reassess entire hypothesis chain\n")
        else:
            print("\n✓ Gate condition PASSED")
            print(f"  {'Pearson r' if r > self.config['target_correlation'] else 'Spearman ρ'} exceeds threshold")
            print("\n  Hypothesis h-e1 VALIDATED")
            print("  Recommendation: Proceed to h-m1 (mechanism hypothesis)\n")

        print("=" * 80)

        return metrics

    def save_results(self, results: list, metrics: Dict[str, Any]) -> None:
        """
        Save experiment results to files.

        Args:
            results: List of per-theorem results
            metrics: Correlation metrics and gate evaluation
        """
        # Create output directories
        os.makedirs(self.config["results_dir"], exist_ok=True)

        # Save raw results to CSV
        results_df = pd.DataFrame([
            {
                'theorem_id': r['theorem_id'],
                'confidence_derivative': r['confidence_derivative'],
                'outcome': r['outcome'],
                'execution_time': r['execution_time'],
                'status': r['status'],
                'entropy_trajectory_length': len(r['entropies'])
            }
            for r in results
        ])
        csv_path = os.path.join(self.config["results_dir"], "results_raw.csv")
        results_df.to_csv(csv_path, index=False)
        print(f"  Saved: {csv_path}")

        # Save metrics summary
        metrics_path = os.path.join(self.config["results_dir"], "metrics_summary.json")
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"  Saved: {metrics_path}")

        # Save experiment metadata
        metadata = {
            'experiment_id': 'h-e1',
            'hypothesis_type': 'EXISTENCE',
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'config': self.config,
            'total_theorems': len(results),
            'valid_theorems': sum(1 for r in results if r['confidence_derivative'] is not None),
            'failed_theorems': sum(1 for r in results if r['status'] == 'error')
        }
        metadata_path = os.path.join(self.config["results_dir"], "experiment_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"  Saved: {metadata_path}")


def main():
    """Main entry point for experiment execution."""

    # Load configuration
    cfg = EXPERIMENT_CONFIG

    # Set random seed for reproducibility
    np.random.seed(cfg["random_seed"])

    # Check GPU availability
    print("\nChecking GPU availability...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ GPU available: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA_VISIBLE_DEVICES: {os.environ.get('CUDA_VISIBLE_DEVICES', 'not set')}")
        else:
            print("⚠ No GPU detected - proceeding with CPU (may be slow)")
    except ImportError:
        print("⚠ PyTorch not installed - cannot check GPU")

    # Create output directories
    os.makedirs(cfg["results_dir"], exist_ok=True)
    os.makedirs(cfg["figures_dir"], exist_ok=True)

    # Run experiment
    orchestrator = ExperimentOrchestrator(cfg)

    try:
        summary = orchestrator.run_full_experiment()

        # Print final summary
        print("\n" + "="*80)
        print("EXPERIMENT COMPLETE")
        print("="*80)
        print(f"\nFinal Results:")
        print(f"  Gate Result: {summary.get('gate_result', 'UNKNOWN')}")
        if 'correlation_pearson' in summary:
            print(f"  Pearson r: {summary['correlation_pearson']['r']:.4f}")
            print(f"  Spearman ρ: {summary['correlation_spearman']['rho']:.4f}")
            print(f"  AUC: {summary['auc']:.4f}")
        print(f"\nResults saved to: {cfg['results_dir']}")
        print(f"Figures saved to: {cfg['figures_dir']}")
        print("\n" + "="*80 + "\n")

        return 0 if summary.get('gate_result') == 'PASS' else 1

    except Exception as e:
        print(f"\n{'='*80}")
        print("EXPERIMENT FAILED")
        print("="*80)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*80 + "\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
