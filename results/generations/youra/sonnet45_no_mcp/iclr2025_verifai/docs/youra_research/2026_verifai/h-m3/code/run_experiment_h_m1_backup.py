"""
Main Experiment Script for h-m1
Orchestrates full pipeline: sampling → execution → analysis → visualization → gate evaluation
Tests MECHANISM hypothesis: confidence variance differs between successful vs timeout proofs
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
from analysis.analyzer import VarianceGroupAnalyzer
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
        print("H-M1 EXPERIMENT: Confidence Variance by Outcome Group")
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
        valid_results = [r for r in results if r['confidence_variance'] is not None]
        print(f"Valid results: {len(valid_results)}/{len(results)}")

        if len(valid_results) == 0:
            print("ERROR: No valid results. Cannot proceed with analysis.")
            return {
                'error': 'No valid results',
                'gate_result': 'FAIL'
            }

        confidence_variances = np.array([r['confidence_variance'] for r in valid_results])
        outcomes = np.array([r['outcome'] for r in valid_results])

        print(f"Confidence variances range: [{confidence_variances.min():.4f}, {confidence_variances.max():.4f}]")
        print(f"Outcomes: {np.sum(outcomes == 0)} successes, {np.sum(outcomes == 1)} timeouts\n")

        # Stage 4: Compute group variance comparison
        print("STAGE 4: Computing variance comparison by outcome group")
        print("-" * 80)
        self.analyzer = VarianceGroupAnalyzer()

        group_analysis = self.analyzer.analyze_by_outcome(confidence_variances, outcomes)
        gate_result = self.analyzer.evaluate_gate(group_analysis)

        print(f"Successful proofs: mean_variance = {group_analysis['successful']['mean_variance']:.4f} ± {group_analysis['successful']['std_variance']:.4f} (n={group_analysis['successful']['count']})")
        print(f"Timeout proofs: mean_variance = {group_analysis['timeout']['mean_variance']:.4f} ± {group_analysis['timeout']['std_variance']:.4f} (n={group_analysis['timeout']['count']})")
        print(f"Difference (timeout - success): {group_analysis['difference']:.4f}")
        print(f"T-statistic: {group_analysis['t_statistic']:.4f} (p = {group_analysis['p_value']:.6e})")
        print(f"Gate result: {'PASS' if gate_result else 'FAIL'}\n")

        # Summary statistics
        summary_stats = group_analysis
        print("Summary Statistics:")
        print(f"  Success group: mean_variance={summary_stats['successful']['mean_variance']:.4f}, std_variance={summary_stats['successful']['std_variance']:.4f}, n={summary_stats['successful']['count']}")
        print(f"  Timeout group: mean_variance={summary_stats['timeout']['mean_variance']:.4f}, std_variance={summary_stats['timeout']['std_variance']:.4f}, n={summary_stats['timeout']['count']}\n")

        # Stage 5: Generate visualizations
        print("STAGE 5: Generating visualizations")
        print("-" * 80)
        self.visualizer = ExperimentVisualizer(output_dir=self.config["figures_dir"])

        self.visualizer.plot_variance_comparison_bar(group_analysis)
        self.visualizer.plot_variance_distributions(confidence_variances, outcomes)
        self.visualizer.plot_variance_boxplot(confidence_variances, outcomes)
        self.visualizer.plot_trajectory_examples(
            [r['entropies'] for r in valid_results],
            outcomes.tolist()
        )
        print("✓ All figures saved\n")

        # Stage 6: Save results
        print("STAGE 6: Saving results")
        print("-" * 80)
        metrics = {
            'groups': {
                'successful': group_analysis['successful'],
                'timeout': group_analysis['timeout']
            },
            'statistics': {
                't_statistic': group_analysis['t_statistic'],
                'p_value': group_analysis['p_value']
            },
            'gate_result': 'PASS' if gate_result else 'FAIL',
            'sample_size': len(valid_results),
            'timeout_budget_seconds': self.config['timeout_seconds'],
            'confidence_window': self.config['confidence_window']
        }
        self.save_results(valid_results, metrics)
        print("✓ Results saved\n")

        # Stage 7: Gate evaluation
        print("STAGE 7: Gate Evaluation")
        print("=" * 80)
        print(f"\nGATE CONDITION: mean_variance(successful) < mean_variance(timeout)")
        print(f"RESULT: {metrics['gate_result']}")

        if not gate_result:
            print("\n⚠ WARNING: Gate condition FAILED")
            print(f"  Successful variance: {group_analysis['successful']['mean_variance']:.4f}")
            print(f"  Timeout variance: {group_analysis['timeout']['mean_variance']:.4f}")
            print("\n  Hypothesis h-m1 REJECTED")
            print("  Recommendation: Confidence variance does not reflect familiarity\n")
        else:
            print("\n✓ Gate condition PASSED")
            print(f"  Successful variance ({group_analysis['successful']['mean_variance']:.4f}) < Timeout variance ({group_analysis['timeout']['mean_variance']:.4f})")
            print("\n  Hypothesis h-m1 VALIDATED")
            print("  Recommendation: Confidence reflects proof state familiarity\n")

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
                'confidence_variance': r['confidence_variance'],
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
            'experiment_id': 'h-m1',
            'hypothesis_type': 'MECHANISM',
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'config': self.config,
            'total_theorems': len(results),
            'valid_theorems': sum(1 for r in results if r['confidence_variance'] is not None),
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
        if 'groups' in summary:
            print(f"  Successful mean variance: {summary['groups']['successful']['mean_variance']:.4f}")
            print(f"  Timeout mean variance: {summary['groups']['timeout']['mean_variance']:.4f}")
            print(f"  P-value: {summary['statistics']['p_value']:.6e}")
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
