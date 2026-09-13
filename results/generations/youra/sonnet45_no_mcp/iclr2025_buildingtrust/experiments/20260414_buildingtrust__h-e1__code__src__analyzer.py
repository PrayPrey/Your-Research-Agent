"""Metrics Analysis Module

This module computes success metrics and evaluates gate conditions.
Provides functionality for calculating family coverage, granularity, and completeness metrics.
"""

import logging
from typing import Dict, Any
import pandas as pd


logger = logging.getLogger(__name__)


class GateMetricsAnalyzer:
    """Analyzes metrics and evaluates gate conditions."""

    def __init__(self, extracted_df: pd.DataFrame):
        """
        Initialize analyzer.

        Args:
            extracted_df: Extracted data DataFrame
        """
        self.df = extracted_df

    def compute_family_coverage(self) -> int:
        """
        Compute model family coverage metric.

        Returns:
            Number of unique model families
        """
        count = self.df['model_family'].nunique()
        logger.info(f"Family coverage: {count} families")
        return count

    def compute_granularity_metrics(self) -> Dict[str, int]:
        """
        Compute category granularity per benchmark.

        Returns:
            Dict mapping benchmark to category count
        """
        metrics = {}
        for benchmark in self.df['benchmark'].unique():
            benchmark_df = self.df[self.df['benchmark'] == benchmark]
            category_count = benchmark_df['category'].nunique()
            metrics[benchmark] = category_count

        logger.info(f"Granularity metrics: {metrics}")
        return metrics

    def compute_completeness(self) -> float:
        """
        Compute data completeness percentage.

        Returns:
            Completeness percentage (0-100)
        """
        if len(self.df) == 0:
            return 0.0

        valid_count = self.df['error_rate'].notna().sum()
        total_count = len(self.df)

        completeness = (valid_count / total_count) * 100
        logger.info(f"Completeness: {completeness:.1f}%")
        return completeness

    def evaluate_gate_condition(self) -> Dict[str, Any]:
        """
        Evaluate MUST_WORK gate condition.

        Gate condition: ≥3 model families with category-level data for both timepoints

        Returns:
            Dict with:
                - gate_passed: bool
                - family_count: int
                - families_with_both_timepoints: List[str]
                - granularity: Dict[str, int]
                - completeness: float
                - gate_message: str
        """
        # Compute metrics
        family_count = self.compute_family_coverage()
        granularity = self.compute_granularity_metrics()
        completeness = self.compute_completeness()

        # Check which families have both timepoints
        families_with_both = []
        for family in self.df['model_family'].unique():
            family_df = self.df[self.df['model_family'] == family]
            timepoints = set(family_df['timepoint'].unique())
            if 'baseline' in timepoints and 'current' in timepoints:
                families_with_both.append(family)

        # Evaluate gate
        families_ok = len(families_with_both) >= 3
        granularity_ok = all(count >= 10 for count in granularity.values()) if granularity else False
        completeness_ok = completeness >= 90.0

        gate_passed = families_ok and granularity_ok and completeness_ok

        # Generate message
        if gate_passed:
            gate_message = (
                f"GATE PASSED: {len(families_with_both)} families with both timepoints "
                f"(threshold: 3)"
            )
        else:
            issues = []
            if not families_ok:
                issues.append(f"only {len(families_with_both)} families with both timepoints (need 3)")
            if not granularity_ok:
                issues.append(f"insufficient category granularity")
            if not completeness_ok:
                issues.append(f"completeness {completeness:.1f}% < 90%")
            gate_message = f"GATE FAILED: {', '.join(issues)}"

        logger.info(gate_message)

        return {
            'gate_passed': gate_passed,
            'family_count': family_count,
            'families_with_both_timepoints': families_with_both,
            'families_with_both_count': len(families_with_both),
            'granularity': granularity,
            'granularity_ok': granularity_ok,
            'completeness': completeness,
            'completeness_ok': completeness_ok,
            'gate_message': gate_message
        }
