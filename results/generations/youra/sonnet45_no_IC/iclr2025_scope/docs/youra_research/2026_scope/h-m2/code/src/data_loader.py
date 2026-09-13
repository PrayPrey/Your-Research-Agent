"""
Data Loading Module for H-M1 Correlation Analysis
Loads benchmark data from H-E1 output and extracts method rankings.
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple


class BenchmarkDataLoader:
    """Load and parse benchmark data from H-E1 collection."""

    def __init__(self, data_path: str):
        """
        Args:
            data_path: Path to benchmarks_collection.jsonl from H-E1
        """
        self.data_path = Path(data_path)
        if not self.data_path.exists():
            raise FileNotFoundError(f"Benchmark data not found: {data_path}")

    def load_benchmarks(self) -> List[Dict]:
        """
        Load all benchmarks from JSONL file.

        Returns:
            List of benchmark dictionaries
        """
        benchmarks = []
        with open(self.data_path, 'r') as f:
            for line in f:
                if line.strip():
                    benchmarks.append(json.loads(line))

        print(f"✓ Loaded {len(benchmarks)} benchmarks from {self.data_path.name}")
        return benchmarks

    def extract_method_rankings(self, benchmarks: List[Dict]) -> pd.DataFrame:
        """
        Extract method family rankings and convert to DataFrame.

        Args:
            benchmarks: List of benchmark dictionaries

        Returns:
            DataFrame with shape (N_benchmarks, N_method_families)
            Columns: method family names
            Values: ranking percentiles (0-100)
        """
        rankings_data = []
        benchmark_ids = []

        for benchmark in benchmarks:
            benchmark_id = benchmark.get('benchmark_id', benchmark.get('dataset_name', 'unknown'))
            benchmark_ids.append(benchmark_id)

            # Extract method_rankings field
            method_rankings = benchmark.get('method_rankings', {})

            # Aggregate by family
            family_rankings = {}
            for method_name, method_data in method_rankings.items():
                if isinstance(method_data, dict):
                    # Extract family and percentile
                    family = method_data.get('family', method_name)
                    percentile = method_data.get('ranking_percentile', method_data.get('percentile', 50))

                    # Aggregate multiple methods in same family (take mean)
                    if family in family_rankings:
                        family_rankings[family].append(percentile)
                    else:
                        family_rankings[family] = [percentile]

            # Convert lists to means
            family_rankings = {
                family: sum(percentiles) / len(percentiles)
                for family, percentiles in family_rankings.items()
            }

            rankings_data.append(family_rankings)

        # Create DataFrame
        rankings_df = pd.DataFrame(rankings_data, index=benchmark_ids)

        # Fill missing values with NaN (will be dropped in correlation)
        # Don't fill with median - let correlation handle missing data

        print(f"✓ Extracted rankings for {len(rankings_df.columns)} method families")
        print(f"  Families: {list(rankings_df.columns)}")
        print(f"  Non-null counts per family:")
        for col in rankings_df.columns[:5]:  # Show first 5
            count = rankings_df[col].notna().sum()
            print(f"    {col}: {count}/{len(rankings_df)}")

        return rankings_df
