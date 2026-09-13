"""data_loader.py — Load H-E1 CSVs and merge ECE column for H-M1."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

import config


class DataLoader:
    def __init__(self, h_e1_outputs_dir: str = config.H_E1_OUTPUTS_DIR) -> None:
        self.h_e1_outputs_dir = Path(h_e1_outputs_dir)

    def load_model_matrix(self) -> pd.DataFrame:
        """Load h-e1/code/outputs/model_matrix.csv."""
        path = self.h_e1_outputs_dir / "model_matrix.csv"
        df = pd.read_csv(path)
        # Normalize model_id column name (H-E1 uses 'model_id' or index)
        if "model_id" not in df.columns and df.index.name == "model_id":
            df = df.reset_index()
        # Ensure model_family column present (may be named 'family' in H-E1)
        if "model_family" not in df.columns and "family" in df.columns:
            df = df.rename(columns={"family": "model_family"})
        return df

    def load_ri_scores(self) -> pd.DataFrame:
        """Load h-e1/code/outputs/ri_scores.csv. Returns DataFrame (30, ≥2)."""
        path = self.h_e1_outputs_dir / "ri_scores.csv"
        df = pd.read_csv(path)
        if "model_id" not in df.columns and "model" in df.columns:
            df = df.rename(columns={"model": "model_id"})
        return df

    def merge_with_ece(self, ece_series: pd.Series) -> pd.DataFrame:
        """Merge model_matrix + RI scores + ECE column.

        Args:
            ece_series: pd.Series with model_id as index and ECE scalars as values.
        Returns:
            DataFrame (30, 8+) with ECE column, no NaN in key cols.
        """
        matrix = self.load_model_matrix()
        ri_df = self.load_ri_scores()

        # Normalize join keys
        if "model_id" not in matrix.columns:
            raise ValueError("model_matrix.csv missing 'model_id' column")

        # Merge RI into matrix (RI may already be present from H-E1)
        if "RI" not in matrix.columns:
            ri_cols = [c for c in ri_df.columns if c not in ("model_id",)]
            matrix = matrix.merge(ri_df[["model_id"] + ri_cols], on="model_id", how="left")

        # Add ECE column
        ece_df = ece_series.rename("ECE").reset_index()
        ece_df.columns = ["model_id", "ECE"]
        matrix = matrix.merge(ece_df, on="model_id", how="left")

        return matrix

    def validate(self, df: pd.DataFrame) -> bool:
        """Assert shape, no NaN in key columns, ECE in [0,1]."""
        assert len(df) == 30, f"Expected 30 models, got {len(df)}"
        key_cols = ["RI", "ECE", "PC1", "mean_confidence"]
        for col in key_cols:
            assert col in df.columns, f"Missing column: {col}"
            assert df[col].isna().sum() == 0, f"NaN in {col}"
        assert (df["ECE"] >= 0).all() and (df["ECE"] <= 1).all(), "ECE out of [0,1]"
        return True


def load_experiment_data(
    ece_series: pd.Series,
    h_e1_outputs_dir: str = config.H_E1_OUTPUTS_DIR,
) -> pd.DataFrame:
    """Top-level entry point. Returns validated merged DataFrame."""
    loader = DataLoader(h_e1_outputs_dir=h_e1_outputs_dir)
    df = loader.merge_with_ece(ece_series)
    loader.validate(df)
    return df
