"""Data loader for h-e1 execution trace features."""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional


class ExecutionTraceLoader:
    """Load execution trace features from h-e1 outputs."""

    def __init__(self, h_e1_path: str = "../h-e1/code/outputs/features.csv"):
        """Initialize loader with h-e1 data path."""
        self.h_e1_path = Path(h_e1_path)
        self.features_df: Optional[pd.DataFrame] = None

    def load_features(self) -> pd.DataFrame:
        """
        Load features.csv from h-e1.

        Returns:
            DataFrame with columns [model, benchmark, pass@1, ..., error_timeout]
        """
        if not self.h_e1_path.exists():
            raise FileNotFoundError(f"h-e1 features not found: {self.h_e1_path}")

        self.features_df = pd.read_csv(self.h_e1_path)
        return self.features_df

    def validate_data_quality(self) -> Dict[str, any]:
        """
        Validate loaded data quality.

        Returns:
            Dictionary with validation results
        """
        if self.features_df is None:
            raise ValueError("Data not loaded. Call load_features() first.")

        required_cols = ['model', 'benchmark', 'pass@1']
        missing_cols = [col for col in required_cols if col not in self.features_df.columns]

        return {
            'valid': len(missing_cols) == 0,
            'model_count': len(self.features_df['model'].unique()),
            'benchmark_count': len(self.features_df['benchmark'].unique()),
            'missing_features': missing_cols,
            'total_pairs': len(self.features_df)
        }

    def get_benchmark_subset(self, benchmark: str) -> pd.DataFrame:
        """
        Extract subset for specific benchmark.

        Args:
            benchmark: "HumanEval" or "MBPP"

        Returns:
            Filtered DataFrame
        """
        if self.features_df is None:
            raise ValueError("Data not loaded. Call load_features() first.")

        return self.features_df[self.features_df['benchmark'] == benchmark].copy()

    def get_model_list(self) -> List[str]:
        """Get list of all models in dataset."""
        if self.features_df is None:
            raise ValueError("Data not loaded. Call load_features() first.")

        return sorted(self.features_df['model'].unique().tolist())
