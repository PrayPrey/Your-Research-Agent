"""Main orchestrator for h-c1 experiment."""

import random
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from baselines.iterative_feedback import IterativeFeedbackBaseline
from baselines.self_consistency import SelfConsistencyBaseline
from baselines.hybrid import HybridBaseline
from core.experiment_runner import ExperimentRunner
from analysis.statistical_tests import StatisticalAnalyzer
from analysis.visualizer import ComputeMatchedVisualizer
from analysis.report_generator import ReportGenerator


class MainOrchestrator:
    """Main orchestrator for h-c1 compute-matched control experiment."""

    def __init__(self):
        # Set random seeds for reproducibility
        random.seed(42)
        np.random.seed(42)

        # Hypothesis folder
        self.hypothesis_folder = Path(__file__).parent.parent.parent

        # Initialize baselines
        self.baselines = {
            'iterative_feedback': IterativeFeedbackBaseline(max_iterations=10, temperature=0.2),
            'self_consistency': SelfConsistencyBaseline(temperature=0.7),
            'hybrid': HybridBaseline(initial_samples=3)
        }

        # Initialize components
        self.experiment_runner = ExperimentRunner(self.baselines)
        self.statistical_analyzer = StatisticalAnalyzer(significance_level=0.05)
        self.visualizer = ComputeMatchedVisualizer(
            output_dir=str(self.hypothesis_folder / "figures")
        )
        self.report_generator = ReportGenerator(
            hypothesis_folder=str(self.hypothesis_folder)
        )

    def run(self):
        """Execute full experiment pipeline."""
        print("=" * 80)
        print("H-C1 Compute-Matched Control Experiment")
        print("=" * 80)

        # Stage 1: Calibration
        avg_budget, N = self.experiment_runner.calibrate_budgets(
            num_validation_programs=15
        )

        # Stage 2: Test set evaluation
        experiment_results = self.experiment_runner.run_test_set_evaluation(
            avg_budget=avg_budget,
            N=N,
            num_test_programs=50,
            checkpoint_freq=10
        )

        # Stage 3: Statistical analysis
        print("\nStage 3: Statistical analysis...")
        stats_results = self._perform_statistical_analysis(experiment_results)

        # Stage 4: Visualization
        print("\nStage 4: Generating visualizations...")
        self.visualizer.generate_all_figures(
            results=stats_results,
            program_results=experiment_results['program_results']
        )

        # Stage 5: Report generation
        print("\nStage 5: Generating validation report...")
        report_content = self.report_generator.generate_validation_report(
            results=stats_results,
            gate_decision=stats_results['gate_decision']
        )

        report_path = self.report_generator.save_validation_report(report_content)
        print(f"\nValidation report saved to: {report_path}")

        # Export results JSON
        results_path = self.report_generator.export_results_json(stats_results)
        print(f"Results JSON saved to: {results_path}")

        # Final gate decision
        print("\n" + "=" * 80)
        print(f"GATE DECISION: {stats_results['gate_decision']['status']}")
        print("=" * 80)

        if stats_results['gate_decision']['status'] == 'SATISFIED':
            print("✓ All criteria satisfied")
            print(f"  - Mean difference: {stats_results['mean_difference']:.2f}pp ≥ 10pp")
            print(f"  - Statistical significance: p = {stats_results['p_value']:.4f} < 0.05")
            print(f"  - Effect size: d = {stats_results['cohens_d']:.2f} ≥ 0.5")
            print(f"  - Compute budget fair: {stats_results['compute_fair']}")
        else:
            print("✗ Gate failed")
            print(f"Failure reasons: {stats_results['gate_decision']['failure_reasons']}")

        return stats_results

    def _perform_statistical_analysis(self, experiment_results: dict) -> dict:
        """Perform statistical analysis on experiment results."""
        program_results = experiment_results['program_results']

        # Extract discharge rates
        baseline1_rates = [r['baseline1']['discharge_rate'] for r in program_results]
        baseline2_rates = [r['baseline2']['discharge_rate'] for r in program_results]
        baseline3_rates = [r['baseline3']['discharge_rate'] for r in program_results]

        # Extract budgets
        baseline1_budgets = [r['baseline1']['compute_budget'] for r in program_results]
        baseline2_budgets = [r['baseline2']['compute_budget'] for r in program_results]

        # Primary hypothesis test
        hypothesis_test = self.statistical_analyzer.primary_hypothesis_test(
            baseline1_rates, baseline2_rates
        )

        # Compute fairness validation
        fairness = self.statistical_analyzer.validate_compute_fairness(
            baseline1_budgets, baseline2_budgets, tolerance=0.10
        )

        # Gate decision
        gate_decision = self.statistical_analyzer.make_gate_decision(
            hypothesis_test, fairness
        )

        # Per-program stats
        b1_wins = sum(1 for r in program_results
                      if r['baseline1']['discharge_rate'] > r['baseline2']['discharge_rate'])
        b2_wins = len(program_results) - b1_wins

        return {
            'mean_baseline1': hypothesis_test.mean_baseline1,
            'mean_baseline2': hypothesis_test.mean_baseline2,
            'mean_baseline3': np.mean(baseline3_rates),
            'std_baseline1': np.std(baseline1_rates),
            'std_baseline2': np.std(baseline2_rates),
            'std_baseline3': np.std(baseline3_rates),
            'mean_difference': hypothesis_test.mean_difference,
            't_statistic': hypothesis_test.t_statistic,
            'p_value': hypothesis_test.p_value,
            'cohens_d': hypothesis_test.cohens_d,
            'token_ratio': fairness.token_ratio,
            'time_ratio': fairness.time_ratio,
            'compute_fair': fairness.overall_fair,
            'b1_wins': b1_wins,
            'b2_wins': b2_wins,
            'gate_decision': {
                'status': gate_decision.status,
                'criteria': gate_decision.criteria,
                'failure_reasons': gate_decision.failure_reasons
            },
            'avg_tokens': experiment_results['calibration_budget']['total_tokens'],
            'avg_verifier_time': experiment_results['calibration_budget']['verifier_time_seconds'],
            'avg_iterations': experiment_results['calibration_budget']['iterations'],
            'N_samples': experiment_results['N_samples']
        }


if __name__ == '__main__':
    orchestrator = MainOrchestrator()
    results = orchestrator.run()
