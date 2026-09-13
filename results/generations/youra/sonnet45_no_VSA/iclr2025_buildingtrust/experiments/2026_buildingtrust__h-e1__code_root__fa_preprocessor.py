"""Data preprocessing for H-E1 Factor Analysis."""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from typing import Tuple
import warnings


class DataPreprocessor:
    """Handle missing data and standardization for factor analysis."""

    def __init__(self, min_coverage: float = 0.6):
        """
        Initialize preprocessor.

        Args:
            min_coverage: Minimum fraction of non-missing benchmarks per model (default 0.6 = 60%)
        """
        self.min_coverage = min_coverage
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean')  # Simpler than EM for PoC

    def filter_models(self, matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Filter models by benchmark coverage.

        Args:
            matrix: [N, M] raw benchmark matrix

        Returns:
            pd.DataFrame: [N', M] filtered matrix (N' >= 15 required)
        """
        print("\n[Preprocessor] Filtering models by coverage...")

        # Calculate coverage per model
        coverage = matrix.notna().sum(axis=1) / len(matrix.columns)
        print(f"[Preprocessor] Coverage range: {coverage.min():.2%} - {coverage.max():.2%}")

        # Filter by minimum coverage
        valid_models = coverage >= self.min_coverage
        filtered = matrix[valid_models]

        print(f"[Preprocessor] Kept {len(filtered)}/{len(matrix)} models (≥{self.min_coverage:.0%} coverage)")

        if len(filtered) < 15:
            warnings.warn(f"Only {len(filtered)} models after filtering, minimum 15 required for FA")

        return filtered

    def handle_missing(self, matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing data via mean imputation.

        Args:
            matrix: [N, M] filtered matrix

        Returns:
            pd.DataFrame: [N, M] imputed matrix
        """
        print("\n[Preprocessor] Handling missing data...")

        missing_count = matrix.isna().sum().sum()
        missing_pct = missing_count / matrix.size

        print(f"[Preprocessor] Missing values: {missing_count} ({missing_pct:.2%})")

        if missing_pct > 0.4:
            warnings.warn(f"High missing data rate ({missing_pct:.2%}), results may be unstable")

        if missing_count == 0:
            print("[Preprocessor] No missing data, skipping imputation")
            return matrix

        # Simple mean imputation (EM would be better but adds complexity)
        imputed_values = self.imputer.fit_transform(matrix)
        imputed = pd.DataFrame(
            imputed_values,
            index=matrix.index,
            columns=matrix.columns
        )

        print(f"[Preprocessor] Imputed {missing_count} missing values with column means")
        return imputed

    def standardize(self, matrix: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Z-score normalization within each benchmark column.

        Args:
            matrix: [N, M] imputed matrix

        Returns:
            Tuple[np.ndarray, pd.DataFrame]:
                - X_scaled: [N, M] standardized array (mean=0, std=1 per column)
                - matrix_unstandardized: Original matrix for reference
        """
        print("\n[Preprocessor] Standardizing matrix...")

        # Store column means and stds for reference
        col_means = matrix.mean(axis=0)
        col_stds = matrix.std(axis=0)

        print(f"[Preprocessor] Mean range: {col_means.min():.3f} - {col_means.max():.3f}")
        print(f"[Preprocessor] Std range: {col_stds.min():.3f} - {col_stds.max():.3f}")

        # Z-score standardization
        X_scaled = self.scaler.fit_transform(matrix)

        print(f"[Preprocessor] Standardized matrix shape: {X_scaled.shape}")
        print(f"[Preprocessor] Post-standardization mean: {X_scaled.mean():.6f} (should be ~0)")
        print(f"[Preprocessor] Post-standardization std: {X_scaled.std():.6f} (should be ~1)")

        return X_scaled, matrix
