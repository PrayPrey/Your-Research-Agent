"""Metrics tracking for experiments."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass

from .refinement_loop import RefinementHistory, ConvergenceReason


@dataclass
class ExperimentMetrics:
    """Per-program experiment results."""
    program_id: str
    initial_discharge_rate: float
    final_discharge_rate: float
    iterations_to_convergence: int
    convergence_reason: ConvergenceReason
    improvement_achieved: bool
    feedback_dimensions_used: Set[str]
    total_api_calls: int
    total_cost_usd: float
    runtime_seconds: float


class MetricsTracker:
    """Track experiment metrics across all programs."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.experiments: List[ExperimentMetrics] = []

    def record_experiment(
        self,
        program_id: str,
        history: RefinementHistory,
        api_calls: int,
        cost_usd: float,
        runtime: float
    ) -> ExperimentMetrics:
        """Record single program experiment."""

        # Extract feedback dimensions used
        dimensions_used = set()
        for iteration in history.iterations:
            if iteration.feedback:
                if iteration.feedback.witness.witness_values:
                    dimensions_used.add("witness")
                if iteration.feedback.structure.failed_obligations:
                    dimensions_used.add("structure")
                if iteration.feedback.dependency.broken_dependencies:
                    dimensions_used.add("dependency")

        metrics = ExperimentMetrics(
            program_id=program_id,
            initial_discharge_rate=history.iterations[0].proof_discharge_rate if history.iterations else 0.0,
            final_discharge_rate=history.iterations[-1].proof_discharge_rate if history.iterations else 0.0,
            iterations_to_convergence=history.total_iterations,
            convergence_reason=history.convergence_reason,
            improvement_achieved=history.improvement_achieved,
            feedback_dimensions_used=dimensions_used,
            total_api_calls=api_calls,
            total_cost_usd=cost_usd,
            runtime_seconds=runtime
        )

        self.experiments.append(metrics)

        # Save iteration log
        self._save_iteration_log(program_id, history)

        return metrics

    def compute_aggregate_metrics(self) -> Dict[str, float]:
        """Compute summary statistics across all experiments."""

        if not self.experiments:
            return {}

        final_rates = [e.final_discharge_rate for e in self.experiments]
        improvements = [e for e in self.experiments if e.improvement_achieved]

        return {
            "mean_final_discharge_rate": sum(final_rates) / len(final_rates),
            "median_final_discharge_rate": sorted(final_rates)[len(final_rates) // 2],
            "min_final_discharge_rate": min(final_rates),
            "max_final_discharge_rate": max(final_rates),
            "programs_with_improvement": len(improvements),
            "improvement_percentage": len(improvements) / len(self.experiments) * 100,
            "mean_iterations": sum(e.iterations_to_convergence for e in self.experiments) / len(self.experiments),
            "total_api_calls": sum(e.total_api_calls for e in self.experiments),
            "total_cost_usd": sum(e.total_cost_usd for e in self.experiments),
            "witness_dimension_usage": sum(1 for e in self.experiments if "witness" in e.feedback_dimensions_used),
            "structure_dimension_usage": sum(1 for e in self.experiments if "structure" in e.feedback_dimensions_used),
            "dependency_dimension_usage": sum(1 for e in self.experiments if "dependency" in e.feedback_dimensions_used)
        }

    def save_results(self, filename: str = "04_results.json"):
        """Save all results to JSON."""

        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "hypothesis": "H-E1",
                "total_programs": len(self.experiments)
            },
            "aggregate_metrics": self.compute_aggregate_metrics(),
            "per_program_metrics": [
                {
                    "program_id": e.program_id,
                    "initial_rate": e.initial_discharge_rate,
                    "final_rate": e.final_discharge_rate,
                    "iterations": e.iterations_to_convergence,
                    "convergence": e.convergence_reason.value,
                    "improved": e.improvement_achieved,
                    "dimensions_used": list(e.feedback_dimensions_used),
                    "cost_usd": e.total_cost_usd
                }
                for e in self.experiments
            ]
        }

        output_file = self.output_dir / filename
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

    def _save_iteration_log(self, program_id: str, history: RefinementHistory):
        """Save detailed iteration log for debugging."""

        log_dir = self.output_dir / "iteration_logs"
        log_dir.mkdir(exist_ok=True, parents=True)

        log_data = {
            "program_id": program_id,
            "total_iterations": history.total_iterations,
            "convergence_reason": history.convergence_reason.value,
            "iterations": [
                {
                    "iteration": it.iteration,
                    "discharge_rate": it.proof_discharge_rate,
                    "total_obligations": it.result.total_obligations,
                    "proved_obligations": it.result.proved_obligations,
                    "feedback_summary": it.feedback.natural_language if it.feedback else None
                }
                for it in history.iterations
            ]
        }

        log_file = log_dir / f"{program_id}_iteration_log.json"
        with log_file.open("w") as f:
            json.dump(log_data, f, indent=2)
