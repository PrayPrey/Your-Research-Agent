"""test_data_loader.py — Unit tests for DataLoader."""
from __future__ import annotations

import pandas as pd
import pytest

from data_loader import DataLoader, load_experiment_data
import config


class TestDataLoader:
    def test_merge_with_ece_shape(self, mock_model_df, mock_ece_series, tmp_path, monkeypatch):
        """merge_with_ece returns DataFrame with ECE column and 30 rows."""
        # Write mock CSVs to tmp_path
        matrix = mock_model_df.drop(columns=["ECE"])
        ri_df = mock_model_df[["model_id", "RI", "PC1"]]
        matrix.to_csv(tmp_path / "model_matrix.csv", index=False)
        ri_df.to_csv(tmp_path / "ri_scores.csv", index=False)

        loader = DataLoader(h_e1_outputs_dir=str(tmp_path))
        merged = loader.merge_with_ece(mock_ece_series)
        assert len(merged) == 30
        assert "ECE" in merged.columns

    def test_validate_passes(self, mock_model_df, mock_ece_series, tmp_path):
        """validate() returns True for well-formed DataFrame."""
        matrix = mock_model_df.drop(columns=["ECE"])
        matrix.to_csv(tmp_path / "model_matrix.csv", index=False)
        mock_model_df[["model_id", "RI", "PC1"]].to_csv(tmp_path / "ri_scores.csv", index=False)

        loader = DataLoader(h_e1_outputs_dir=str(tmp_path))
        merged = loader.merge_with_ece(mock_ece_series)
        assert loader.validate(merged) is True

    def test_validate_fails_wrong_n(self, mock_model_df):
        """validate() raises AssertionError when n != 30."""
        loader = DataLoader()
        small_df = mock_model_df.head(10)
        with pytest.raises(AssertionError, match="30 models"):
            loader.validate(small_df)

    def test_validate_fails_out_of_range_ece(self, mock_model_df, tmp_path):
        """validate() raises AssertionError when ECE out of [0,1]."""
        bad_df = mock_model_df.copy()
        bad_df.loc[0, "ECE"] = 1.5
        loader = DataLoader()
        with pytest.raises(AssertionError, match="ECE out"):
            loader.validate(bad_df)

    def test_load_model_matrix_columns(self, mock_model_df, tmp_path):
        """load_model_matrix returns DataFrame with required columns."""
        mock_model_df.drop(columns=["ECE"]).to_csv(tmp_path / "model_matrix.csv", index=False)
        loader = DataLoader(h_e1_outputs_dir=str(tmp_path))
        df = loader.load_model_matrix()
        assert "model_id" in df.columns or df.index.name == "model_id"
        assert len(df) == 30
