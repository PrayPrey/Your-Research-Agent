"""
Cached Data Loader for H-M3 Fisher z-Test
Loads and validates correlation results from H-M1
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional


class CachedResultsLoader:
    """Load and validate H-M1 correlation results."""

    def __init__(self, h_m1_output_path: str):
        """
        Initialize loader.

        Args:
            h_m1_output_path: Path to h-m1/code/outputs/results.csv
        """
        self.output_path = Path(h_m1_output_path)

    def load_correlation_results(self) -> pd.DataFrame:
        """
        Load cached correlation results from H-M1.

        Returns:
            DataFrame with columns [stratum, r, p_value, ci_lower, ci_upper, n]
        """
        if not self.output_path.exists():
            raise FileNotFoundError(
                f"H-M1 results not found at {self.output_path}. "
                "Run H-M1 experiment first."
            )

        df = pd.read_csv(self.output_path)
        return df

    def validate_cached_data(self, df: pd.DataFrame) -> bool:
        """
        Validate cached data format and contents.

        Args:
            df: DataFrame to validate

        Returns:
            True if data has required columns and valid values
        """
        required_columns = ["stratum", "r", "p_value", "ci_lower", "ci_upper", "n"]

        # Check columns exist
        if not all(col in df.columns for col in required_columns):
            print(f"Error: Missing required columns. Found: {df.columns.tolist()}")
            return False

        # Check we have exactly 2 rows (factual and misinformation)
        if len(df) != 2:
            print(f"Error: Expected 2 rows (factual, misinformation), found {len(df)}")
            return False

        # Check stratum labels
        strata = set(df['stratum'].values)
        expected_strata = {'factual', 'misinformation'}
        if strata != expected_strata:
            print(f"Error: Expected strata {expected_strata}, found {strata}")
            return False

        # Check sample sizes are reasonable
        if (df['n'] < 10).any():
            print("Error: Sample size < 10 for at least one stratum")
            return False

        return True

    def get_factual_correlation(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Extract factual stratum correlation.

        Args:
            df: DataFrame with correlation results

        Returns:
            {"r": float, "p_value": float, "ci_lower": float, "ci_upper": float, "n": int}
        """
        factual_row = df[df['stratum'] == 'factual'].iloc[0]
        return {
            "r": float(factual_row['r']),
            "p_value": float(factual_row['p_value']),
            "ci_lower": float(factual_row['ci_lower']),
            "ci_upper": float(factual_row['ci_upper']),
            "n": int(factual_row['n'])
        }

    def get_misinfo_correlation(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Extract misinformation stratum correlation.

        Args:
            df: DataFrame with correlation results

        Returns:
            {"r": float, "p_value": float, "ci_lower": float, "ci_upper": float, "n": int}
        """
        misinfo_row = df[df['stratum'] == 'misinformation'].iloc[0]
        return {
            "r": float(misinfo_row['r']),
            "p_value": float(misinfo_row['p_value']),
            "ci_lower": float(misinfo_row['ci_lower']),
            "ci_upper": float(misinfo_row['ci_upper']),
            "n": int(misinfo_row['n'])
        }
