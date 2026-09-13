"""Data Validation and Cleaning Module

Validates data quality and handles outliers/missing values.
"""

from typing import Tuple
import pandas as pd
import numpy as np
from scipy import stats


class DataValidator:
    """Validates and cleans collected metrics data."""

    def __init__(self, quality_threshold: float = 0.95):
        """Initialize data validator.

        Args:
            quality_threshold: Minimum completeness ratio (default 0.95 = 95%)
        """
        self.quality_threshold = quality_threshold

    def check_completeness(self, df: pd.DataFrame) -> Tuple[int, int]:
        """Check data completeness.

        Args:
            df: DataFrame with collected metrics

        Returns:
            Tuple of (complete_count, total_count)
        """
        # Count rows with all required metrics (excluding median_issue_response which can be None)
        required_cols = ['commits_per_month', 'unique_contributors', 'repo_age_days']
        complete_mask = df[required_cols].notna().all(axis=1)
        complete_count = complete_mask.sum()
        total_count = len(df)

        completeness_ratio = complete_count / total_count if total_count > 0 else 0.0
        print(f"Data completeness: {complete_count}/{total_count} ({completeness_ratio:.1%})")

        if completeness_ratio < self.quality_threshold:
            print(f"WARNING: Completeness {completeness_ratio:.1%} < threshold {self.quality_threshold:.1%}")

        return (complete_count, total_count)

    def detect_outliers(self, df: pd.DataFrame, z_threshold: float = 3.0) -> pd.Series:
        """Detect outliers using z-score method.

        Args:
            df: DataFrame with metrics
            z_threshold: Z-score threshold for outlier detection (default 3.0)

        Returns:
            Boolean Series indicating outliers (True = outlier)
        """
        outlier_mask = pd.Series([False] * len(df), index=df.index)

        numeric_cols = ['commits_per_month', 'unique_contributors', 'median_issue_response', 'repo_age_days']

        for col in numeric_cols:
            if col not in df.columns:
                continue

            # Skip if too many missing values
            if df[col].isna().sum() > len(df) * 0.5:
                continue

            # Calculate z-scores (ignoring NaN)
            mean = df[col].mean()
            std = df[col].std()

            if std > 0:
                z_scores = (df[col] - mean) / std
                col_outliers = z_scores.abs() > z_threshold
                outlier_mask |= col_outliers.fillna(False)

        outlier_count = outlier_mask.sum()
        print(f"Outliers detected: {outlier_count}/{len(df)} ({outlier_count/len(df):.1%})")

        # Log outlier rows
        if outlier_count > 0:
            print(f"Outlier repo_ids: {df.loc[outlier_mask, 'repo_id'].tolist()[:5]}...")

        return outlier_mask

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in metrics data.

        Args:
            df: DataFrame with metrics

        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()

        # median_issue_response: None is expected for repos with <5 issues
        # Keep as None, don't impute

        # Other metrics: Remove rows with missing values (critical metrics)
        critical_cols = ['commits_per_month', 'unique_contributors', 'repo_age_days']
        missing_critical = df_clean[critical_cols].isna().any(axis=1)
        removed_count = missing_critical.sum()

        if removed_count > 0:
            print(f"Removing {removed_count} rows with missing critical metrics")
            df_clean = df_clean[~missing_critical].copy()

        return df_clean

    def export_cleaned_data(self, df: pd.DataFrame, output_path: str) -> None:
        """Export cleaned data to CSV.

        Args:
            df: Cleaned DataFrame
            output_path: Output CSV file path
        """
        df.to_csv(output_path, index=False)
        print(f"Cleaned data exported to: {output_path}")
        print(f"  Final sample size: {len(df)}")
