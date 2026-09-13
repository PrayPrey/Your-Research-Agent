"""Tests for data_assembly.py — spec compliance tests for H-E1."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
import numpy as np

from data_assembly import DataAssembler, assemble_matrix, COLUMNS


REQUIRED_COLS = ["model_id", "model_family", "scale", "training_regime",
                 "advglue_drop", "mmlu", "gsm8k", "bbh", "hellaswag",
                 "winogrande", "mean_confidence"]


class TestDataAssembler:
    def setup_method(self):
        self.assembler = DataAssembler(
            trustllm_data_dir="nonexistent_dir",
            lmeval_results_dir="nonexistent_dir",
        )

    def test_load_trustllm_scores_returns_dataframe(self):
        df = self.assembler.load_trustllm_scores()
        assert isinstance(df, pd.DataFrame)

    def test_load_trustllm_scores_has_required_columns(self):
        df = self.assembler.load_trustllm_scores()
        required = ["model_id", "model_family", "scale", "training_regime", "advglue_drop"]
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    def test_load_trustllm_scores_nonempty(self):
        df = self.assembler.load_trustllm_scores()
        assert len(df) >= 10, f"Expected ≥10 rows, got {len(df)}"

    def test_load_lmeval_scores_returns_dataframe(self):
        df = self.assembler.load_lmeval_scores()
        assert isinstance(df, pd.DataFrame)

    def test_load_lmeval_scores_has_required_columns(self):
        df = self.assembler.load_lmeval_scores()
        required = ["model_id", "mmlu", "gsm8k", "bbh", "hellaswag", "winogrande", "mean_confidence"]
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    def test_merge_matrix_returns_dataframe(self):
        df = self.assembler.merge_matrix()
        assert isinstance(df, pd.DataFrame)

    def test_merge_matrix_has_all_columns(self):
        df = self.assembler.merge_matrix()
        for col in REQUIRED_COLS:
            assert col in df.columns, f"Missing merged column: {col}"

    def test_merge_matrix_min_models(self):
        df = self.assembler.merge_matrix()
        assert len(df) >= 30, f"Expected ≥30 models, got {len(df)}"

    def test_validate_matrix_passes(self):
        df = self.assembler.merge_matrix()
        result = self.assembler.validate_matrix(df)
        assert result is True

    def test_validate_matrix_family_diversity(self):
        df = self.assembler.merge_matrix()
        assert df["model_family"].nunique() >= 3

    def test_validate_matrix_scale_diversity(self):
        df = self.assembler.merge_matrix()
        assert df["scale"].nunique() >= 2

    def test_validate_matrix_regime_diversity(self):
        df = self.assembler.merge_matrix()
        assert df["training_regime"].nunique() >= 2

    def test_validate_matrix_missing_data(self):
        df = self.assembler.merge_matrix()
        for col in ["advglue_drop", "mmlu", "gsm8k"]:
            if col in df.columns:
                missing_rate = df[col].isna().mean()
                assert missing_rate <= 0.30, f"Column '{col}' has {missing_rate:.1%} missing"

    def test_advglue_drop_range(self):
        df = self.assembler.merge_matrix()
        assert df["advglue_drop"].between(0.0, 1.0).all(), "advglue_drop must be in [0, 1]"

    def test_capability_cols_range(self):
        df = self.assembler.merge_matrix()
        for col in ["mmlu", "gsm8k", "bbh", "hellaswag", "winogrande"]:
            if col in df.columns:
                assert df[col].between(0.0, 1.0).all(), f"{col} must be in [0, 1]"


class TestAssembleMatrix:
    def test_assemble_matrix_returns_validated_df(self):
        df = assemble_matrix()
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 30

    def test_assemble_matrix_columns(self):
        df = assemble_matrix()
        for col in REQUIRED_COLS:
            assert col in df.columns
