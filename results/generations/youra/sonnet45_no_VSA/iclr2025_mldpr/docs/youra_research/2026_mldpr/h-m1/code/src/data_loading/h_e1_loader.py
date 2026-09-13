"""H-E1 Data Loading Module

Loads DCS_3 scores from H-E1 validation results.
"""

from pathlib import Path
from typing import Optional
import pandas as pd


class HE1DataLoader:
    """Loads and validates H-E1 DCS_3 scores."""

    def __init__(self, h_e1_path: str):
        """Initialize H-E1 data loader.

        Args:
            h_e1_path: Path to H-E1 validation_results.csv or results folder
        """
        self.h_e1_path = Path(h_e1_path)

    def load_dcs_scores(self) -> pd.DataFrame:
        """Load DCS_3 scores from H-E1 validation results.

        Returns:
            DataFrame with columns: [repo_id, dcs_3_score, t0_date]
            Expected N=100 repositories
        """
        # Try to load from validation_results.csv
        if self.h_e1_path.is_file():
            df = pd.read_csv(self.h_e1_path)
        elif self.h_e1_path.is_dir():
            # Look for CSV files in the directory
            csv_files = list(self.h_e1_path.glob("*.csv"))
            if not csv_files:
                raise FileNotFoundError(f"No CSV files found in {self.h_e1_path}")
            df = pd.read_csv(csv_files[0])
        else:
            raise FileNotFoundError(f"H-E1 data path not found: {self.h_e1_path}")

        # Validate required columns
        required_cols = ['repo_id', 'dcs_3_score']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Add t0_date if not present (use creation_date or first_release_date)
        if 't0_date' not in df.columns:
            if 'creation_date' in df.columns:
                df['t0_date'] = df['creation_date']
            elif 'first_release_date' in df.columns:
                df['t0_date'] = df['first_release_date']
            else:
                # Default: assume all repos measured at same time
                df['t0_date'] = pd.Timestamp('2022-01-01')

        return df[['repo_id', 'dcs_3_score', 't0_date']]

    def validate_dcs_data(self, df: pd.DataFrame) -> bool:
        """Validate DCS_3 data quality.

        Args:
            df: DataFrame with DCS_3 scores

        Returns:
            True if data passes validation checks
        """
        # Check sample size (expected N=100)
        if len(df) < 50:
            print(f"WARNING: Sample size {len(df)} < 50 (expected ~100)")
            return False

        # Check DCS_3 score range [0, 3]
        if df['dcs_3_score'].min() < 0 or df['dcs_3_score'].max() > 3:
            print(f"ERROR: DCS_3 scores out of range [0, 3]")
            return False

        # Check for missing values
        if df['dcs_3_score'].isnull().any():
            print(f"ERROR: Missing DCS_3 scores detected")
            return False

        # Check for duplicate repos
        if df['repo_id'].duplicated().any():
            print(f"ERROR: Duplicate repo_ids detected")
            return False

        return True
