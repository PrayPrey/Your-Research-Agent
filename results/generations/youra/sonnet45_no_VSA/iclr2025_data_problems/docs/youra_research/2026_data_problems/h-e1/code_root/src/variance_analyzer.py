"""Compute variance metrics for coupling scores."""

import logging
import statistics
from typing import Dict, List

from .coupling_extractor import CouplingMetrics

logger = logging.getLogger(__name__)


class VarianceAnalyzer:
    """Compute variance metrics for coupling scores."""

    def compute_cv(self, scores: List[float]) -> float:
        """Compute Coefficient of Variation (CV = σ / μ)."""
        if len(scores) < 2:
            return 0.0

        mean = statistics.mean(scores)
        if mean == 0:
            return 0.0

        stdev = statistics.stdev(scores)
        cv = stdev / mean
        return cv

    def analyze_per_problem_variance(
        self, metrics: List[CouplingMetrics]
    ) -> Dict[str, float]:
        """Compute CV per problem."""
        # Group scores by problem
        problem_scores = {}
        for metric in metrics:
            if metric.problem_id not in problem_scores:
                problem_scores[metric.problem_id] = []
            problem_scores[metric.problem_id].append(metric.coupling_score)

        # Compute CV per problem
        per_problem_cv = {}
        for problem_id, scores in problem_scores.items():
            cv = self.compute_cv(scores)
            per_problem_cv[problem_id] = cv

        return per_problem_cv

    def compute_average_cv(self, per_problem_cv: Dict[str, float]) -> float:
        """Compute average CV across all problems."""
        if not per_problem_cv:
            return 0.0
        return statistics.mean(per_problem_cv.values())

    def validate_gate(
        self, average_cv: float, extraction_rate: float
    ) -> Dict[str, bool]:
        """Check gate conditions."""
        cv_passed = average_cv > 0.3
        extraction_passed = extraction_rate > 0.95

        logger.info(f"Gate validation: CV={average_cv:.3f} (>0.3: {cv_passed}), "
                   f"Extraction={extraction_rate:.3f} (>0.95: {extraction_passed})")

        return {"cv_passed": cv_passed, "extraction_passed": extraction_passed}

    def get_statistics(
        self, metrics: List[CouplingMetrics], per_problem_cv: Dict[str, float]
    ) -> Dict:
        """Get comprehensive statistics."""
        coupling_scores = [m.coupling_score for m in metrics]
        fan_ins = [m.fan_in for m in metrics]
        fan_outs = [m.fan_out for m in metrics]
        centralities = [m.centrality for m in metrics]

        return {
            "total_submissions": len(metrics),
            "total_problems": len(per_problem_cv),
            "coupling_score": {
                "mean": statistics.mean(coupling_scores) if coupling_scores else 0.0,
                "median": statistics.median(coupling_scores) if coupling_scores else 0.0,
                "stdev": statistics.stdev(coupling_scores) if len(coupling_scores) > 1 else 0.0,
                "min": min(coupling_scores) if coupling_scores else 0.0,
                "max": max(coupling_scores) if coupling_scores else 0.0,
            },
            "fan_in": {
                "mean": statistics.mean(fan_ins) if fan_ins else 0.0,
                "median": statistics.median(fan_ins) if fan_ins else 0.0,
            },
            "fan_out": {
                "mean": statistics.mean(fan_outs) if fan_outs else 0.0,
                "median": statistics.median(fan_outs) if fan_outs else 0.0,
            },
            "centrality": {
                "mean": statistics.mean(centralities) if centralities else 0.0,
                "median": statistics.median(centralities) if centralities else 0.0,
            },
            "cv": {
                "per_problem": per_problem_cv,
                "average": self.compute_average_cv(per_problem_cv),
                "min": min(per_problem_cv.values()) if per_problem_cv else 0.0,
                "max": max(per_problem_cv.values()) if per_problem_cv else 0.0,
            },
        }
