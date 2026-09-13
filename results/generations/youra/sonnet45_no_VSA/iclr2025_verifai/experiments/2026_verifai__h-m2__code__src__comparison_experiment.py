"""Comparison experiment runner for Staged vs Complete strategies."""

import json
import random
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict

import staged_strategy
import complete_strategy

StagedRefinementStrategy = staged_strategy.StagedRefinementStrategy
StagedResult = staged_strategy.StagedResult
CompleteRefinementStrategy = complete_strategy.CompleteRefinementStrategy
CompleteResult = complete_strategy.CompleteResult


@dataclass
class ComparisonMetrics:
    """Comparison metrics between strategies."""
    staged_mean_discharge: float
    complete_mean_discharge: float
    staged_mean_iterations: float
    complete_mean_iterations: float
    iteration_reduction_ratio: float
    discharge_improvement_pp: float
    p_value: float
    effect_size: float


@dataclass
class ExperimentResults:
    """Complete experiment results."""
    staged_results: List[StagedResult]
    complete_results: List[CompleteResult]
    comparison_metrics: ComparisonMetrics
    programs_tested: int


class ComparisonExperiment:
    """Run comparison experiment between Staged and Complete strategies."""

    def __init__(
        self,
        staged_strategy: StagedRefinementStrategy,
        complete_strategy: CompleteRefinementStrategy,
        output_dir: str
    ):
        self.staged_strategy = staged_strategy
        self.complete_strategy = complete_strategy
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, programs: List[str]) -> ExperimentResults:
        """
        Run both strategies on same programs.

        Args:
            programs: List of C program code strings

        Returns:
            ExperimentResults with comparison metrics
        """
        print(f"Running comparison experiment on {len(programs)} programs...")

        # Run both strategies
        staged_results = self._run_staged(programs)
        complete_results = self._run_complete(programs)

        # Compute comparison metrics
        comparison_metrics = self._compute_comparison_metrics(staged_results, complete_results)

        # Save results
        results = ExperimentResults(
            staged_results=staged_results,
            complete_results=complete_results,
            comparison_metrics=comparison_metrics,
            programs_tested=len(programs)
        )

        self._save_results(results)

        return results

    def _run_staged(self, programs: List[str]) -> List[StagedResult]:
        """Run staged strategy on all programs."""
        results = []
        temp_dir = self.output_dir / "staged" / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        for i, program in enumerate(programs):
            print(f"  Staged strategy: Program {i+1}/{len(programs)}")
            result = self.staged_strategy.synthesize_specification(
                c_code=program,
                program_id=f"program_{i:03d}",
                temp_dir=temp_dir
            )
            results.append(result)

        return results

    def _run_complete(self, programs: List[str]) -> List[CompleteResult]:
        """Run complete strategy on all programs."""
        results = []
        temp_dir = self.output_dir / "complete" / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        for i, program in enumerate(programs):
            print(f"  Complete strategy: Program {i+1}/{len(programs)}")
            result = self.complete_strategy.synthesize_specification(
                c_code=program,
                program_id=f"program_{i:03d}",
                temp_dir=temp_dir
            )
            results.append(result)

        return results

    def _compute_comparison_metrics(
        self,
        staged_results: List[StagedResult],
        complete_results: List[CompleteResult]
    ) -> ComparisonMetrics:
        """Compute statistical comparison metrics."""
        from scipy import stats
        import numpy as np

        # Extract discharge rates
        staged_rates = [
            list(r.stage_history.values())[-1].discharge_rate
            for r in staged_results
        ]
        complete_rates = [
            r.discharge_history[-1] if r.discharge_history else 0.0
            for r in complete_results
        ]

        # Extract iterations
        staged_iters = [r.total_iterations for r in staged_results]
        complete_iters = [r.total_iterations for r in complete_results]

        # Compute means
        staged_mean_discharge = np.mean(staged_rates)
        complete_mean_discharge = np.mean(complete_rates)
        staged_mean_iterations = np.mean(staged_iters)
        complete_mean_iterations = np.mean(complete_iters)

        # Iteration reduction ratio
        iteration_reduction_ratio = staged_mean_iterations / complete_mean_iterations if complete_mean_iterations > 0 else 1.0

        # Discharge improvement
        discharge_improvement_pp = staged_mean_discharge - complete_mean_discharge

        # Paired t-test
        t_stat, p_value = stats.ttest_rel(staged_rates, complete_rates)

        # Effect size (Cohen's d)
        differences = np.array(staged_rates) - np.array(complete_rates)
        effect_size = np.mean(differences) / np.std(differences) if np.std(differences) > 0 else 0.0

        return ComparisonMetrics(
            staged_mean_discharge=staged_mean_discharge,
            complete_mean_discharge=complete_mean_discharge,
            staged_mean_iterations=staged_mean_iterations,
            complete_mean_iterations=complete_mean_iterations,
            iteration_reduction_ratio=iteration_reduction_ratio,
            discharge_improvement_pp=discharge_improvement_pp,
            p_value=p_value,
            effect_size=effect_size
        )

    def _save_results(self, results: ExperimentResults):
        """Save experiment results to JSON."""
        # Convert to dict for JSON serialization
        results_dict = {
            "programs_tested": results.programs_tested,
            "staged_mean_discharge": results.comparison_metrics.staged_mean_discharge,
            "complete_mean_discharge": results.comparison_metrics.complete_mean_discharge,
            "staged_mean_iterations": results.comparison_metrics.staged_mean_iterations,
            "complete_mean_iterations": results.comparison_metrics.complete_mean_iterations,
            "iteration_reduction_ratio": results.comparison_metrics.iteration_reduction_ratio,
            "discharge_improvement_pp": results.comparison_metrics.discharge_improvement_pp,
            "p_value": results.comparison_metrics.p_value,
            "effect_size": results.comparison_metrics.effect_size
        }

        output_file = self.output_dir / "comparison_metrics.json"
        with open(output_file, 'w') as f:
            json.dump(results_dict, f, indent=2)

        print(f"\nResults saved to {output_file}")
