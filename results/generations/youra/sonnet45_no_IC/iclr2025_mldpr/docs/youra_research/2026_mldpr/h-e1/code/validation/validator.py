"""
E1-2: Validation Module - BenchmarkValidator
Implements filtering logic and hypothesis gate validation.
"""

import pandas as pd
from typing import Dict, List


class BenchmarkValidator:
    """
    Validates benchmarks against inclusion criteria and hypothesis gates.

    Features:
    - Multi-stage filtering (result_count >= 5, metric type filter)
    - Hypothesis gate checking (N >= 100)
    - Deduplication by benchmark_id
    """

    def __init__(
        self,
        min_count: int = 100,
        min_results: int = 5,
        allowed_metrics: List[str] = None
    ):
        """
        Initialize validator.

        Args:
            min_count: Minimum benchmarks required (gate threshold)
            min_results: Minimum results per benchmark
            allowed_metrics: Allowed metric types (None = all accepted)
        """
        self.min_count = min_count
        self.min_results = min_results
        self.allowed_metrics = allowed_metrics or ["accuracy", "f1"]

    def filter_by_criteria(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply inclusion criteria filtering.

        Filtering stages:
        1. result_count >= min_results
        2. metric_type in allowed_metrics (if metric_type column exists)
        3. drop_duplicates(subset=['benchmark_id'])

        Args:
            df: Raw benchmark DataFrame

        Returns:
            Filtered DataFrame
        """
        print(f"🔍 Applying inclusion criteria...")
        print(f"  Input benchmarks: {len(df)}")

        # Stage 1: Filter by result count
        filtered = df[df['result_count'] >= self.min_results].copy()
        print(f"  After result_count >= {self.min_results}: {len(filtered)}")

        # Stage 2: Filter by metric type (if column exists)
        if 'metric_type' in filtered.columns:
            filtered = filtered[filtered['metric_type'].isin(self.allowed_metrics)]
            print(f"  After metric_type filter: {len(filtered)}")

        # Stage 3: Deduplication
        filtered = filtered.drop_duplicates(subset=['benchmark_id'])
        print(f"  After deduplication: {len(filtered)}")

        return filtered

    def validate_hypothesis(self, df: pd.DataFrame) -> Dict:
        """
        Validate hypothesis against primary gate.

        Gate condition: N >= min_count (default: 100)

        Args:
            df: Filtered benchmark DataFrame

        Returns:
            Validation result dict with passes/fails status
        """
        total_count = len(df)
        passes = self.check_primary_gate(total_count)

        result = {
            'total_benchmarks': total_count,
            'threshold': self.min_count,
            'passes': passes,
            'status': 'PASS' if passes else 'FAIL'
        }

        print(f"\n✅ Hypothesis Validation:")
        print(f"  Total benchmarks: {total_count}")
        print(f"  Threshold: {self.min_count}")
        print(f"  Gate status: {result['status']}")

        return result

    def check_primary_gate(self, count: int) -> bool:
        """
        Binary gate check.

        Args:
            count: Total benchmark count

        Returns:
            True if count >= min_count, False otherwise
        """
        return count >= self.min_count
