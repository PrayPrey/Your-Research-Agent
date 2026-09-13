"""Data Validation Module

This module validates extracted data against quality and coverage requirements.
Implements checks for model family coverage, category granularity, and data completeness.
"""

import logging
from typing import Dict, Tuple, Any
import pandas as pd


logger = logging.getLogger(__name__)


class DataAvailabilityValidator:
    """Validates data extraction results against success criteria."""

    def __init__(self, extracted_df: pd.DataFrame):
        """
        Initialize validator.

        Args:
            extracted_df: Extracted data with schema
                [model_family, timepoint, benchmark, category, error_rate]
        """
        self.df = extracted_df

    def check_model_family_coverage(self) -> Tuple[bool, int]:
        """
        Check if we have ≥3 model families with data.

        Returns:
            Tuple of (passed, count)
        """
        unique_families = self.df['model_family'].nunique()
        passed = unique_families >= 3

        logger.info(f"Model family coverage: {unique_families} families (threshold: 3)")
        return passed, unique_families

    def check_timepoint_coverage(self) -> Dict[str, bool]:
        """
        Check if each family has both baseline AND current timepoints.

        Returns:
            Dict mapping family name to boolean (has both timepoints)
        """
        results = {}

        for family in self.df['model_family'].unique():
            family_df = self.df[self.df['model_family'] == family]
            timepoints = set(family_df['timepoint'].unique())
            has_both = 'baseline' in timepoints and 'current' in timepoints
            results[family] = has_both

            logger.info(f"{family}: timepoints = {timepoints}, has_both = {has_both}")

        return results

    def check_category_granularity(self) -> Dict[str, int]:
        """
        Check if each benchmark has ≥10 categories.

        Returns:
            Dict mapping benchmark name to category count
        """
        results = {}

        for benchmark in self.df['benchmark'].unique():
            benchmark_df = self.df[self.df['benchmark'] == benchmark]
            category_count = benchmark_df['category'].nunique()
            results[benchmark] = category_count

            threshold_met = "✓" if category_count >= 10 else "✗"
            logger.info(f"{benchmark}: {category_count} categories {threshold_met} (threshold: 10)")

        return results

    def check_data_completeness(self) -> float:
        """
        Compute data completeness percentage.

        Returns:
            Completeness percentage (0-100)
        """
        # Expected cells: families × timepoints × benchmarks × avg_categories
        # Actual cells: non-null error_rate values

        total_cells = len(self.df)
        if total_cells == 0:
            return 0.0

        # Count non-null error rates
        valid_cells = self.df['error_rate'].notna().sum()

        completeness = (valid_cells / total_cells) * 100

        logger.info(f"Data completeness: {completeness:.1f}% ({valid_cells}/{total_cells} cells)")
        return completeness

    def validate_all(self) -> Dict[str, Any]:
        """
        Run all validation checks.

        Returns:
            Validation results dictionary with:
                - family_coverage_passed: bool
                - family_count: int
                - timepoint_coverage: Dict[str, bool]
                - category_granularity: Dict[str, int]
                - granularity_passed: bool
                - completeness: float
                - completeness_passed: bool
                - overall_passed: bool
        """
        # Check family coverage
        family_passed, family_count = self.check_model_family_coverage()

        # Check timepoint coverage
        timepoint_coverage = self.check_timepoint_coverage()
        timepoint_passed = all(timepoint_coverage.values())

        # Check category granularity
        category_granularity = self.check_category_granularity()
        granularity_passed = all(count >= 10 for count in category_granularity.values())

        # Check data completeness
        completeness = self.check_data_completeness()
        completeness_passed = completeness >= 90.0

        # Overall validation
        overall_passed = (
            family_passed and
            timepoint_passed and
            granularity_passed and
            completeness_passed
        )

        results = {
            'family_coverage_passed': family_passed,
            'family_count': family_count,
            'timepoint_coverage': timepoint_coverage,
            'timepoint_coverage_passed': timepoint_passed,
            'category_granularity': category_granularity,
            'granularity_passed': granularity_passed,
            'completeness': completeness,
            'completeness_passed': completeness_passed,
            'overall_passed': overall_passed
        }

        logger.info(f"Validation overall: {'PASSED' if overall_passed else 'FAILED'}")
        return results


class GateFailureError(Exception):
    """Raised when gate condition is not met."""
    pass
