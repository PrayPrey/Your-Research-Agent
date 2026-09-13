"""Tests for compute_ri.py — spec compliance tests for H-E1."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
import numpy as np

from data_assembly import assemble_matrix
from compute_ri import RIComputer, compute_residual_instability
import config


@pytest.fixture(scope="module")
def base_df():
    return assemble_matrix()


class TestRIComputer:
    def test_compute_pc1_adds_column(self, base_df):
        comp = RIComputer()
        df_out, pc1_var = comp.compute_pc1(base_df)
        assert "PC1" in df_out.columns

    def test_compute_pc1_variance_ratio(self, base_df):
        comp = RIComputer()
        _, pc1_var = comp.compute_pc1(base_df)
        assert isinstance(pc1_var, float)
        assert 0.0 < pc1_var <= 1.0

    def test_compute_pc1_no_nan(self, base_df):
        comp = RIComputer()
        df_out, _ = comp.compute_pc1(base_df)
        assert df_out["PC1"].isna().sum() == 0

    def test_fit_ols_adds_ri_column(self, base_df):
        comp = RIComputer()
        df_pc1, _ = comp.compute_pc1(base_df)
        df_out, r2 = comp.fit_ols(df_pc1)
        assert "RI" in df_out.columns

    def test_fit_ols_r2_range(self, base_df):
        comp = RIComputer()
        df_pc1, _ = comp.compute_pc1(base_df)
        _, r2 = comp.fit_ols(df_pc1)
        assert 0.0 <= r2 <= 1.0

    def test_fit_ols_residuals_mean_near_zero(self, base_df):
        comp = RIComputer()
        df_pc1, _ = comp.compute_pc1(base_df)
        df_out, _ = comp.fit_ols(df_pc1)
        assert abs(df_out["RI"].mean()) < 1e-10

    def test_fit_ols_baseline_returns_float(self, base_df):
        comp = RIComputer()
        df_pc1, _ = comp.compute_pc1(base_df)
        comp.fit_ols(df_pc1)
        r2_base = comp.fit_ols_baseline(df_pc1)
        assert isinstance(r2_base, float)
        assert 0.0 <= r2_base <= 1.0

    def test_check_vif_returns_float(self, base_df):
        comp = RIComputer()
        df_pc1, _ = comp.compute_pc1(base_df)
        comp.fit_ols(df_pc1)
        vif = comp.check_vif(df_pc1)
        assert isinstance(vif, float)
        assert vif > 0

    def test_compute_returns_stats_dict(self, base_df):
        comp = RIComputer()
        df_out, stats = comp.compute(base_df)
        required_keys = ["pc1_var", "r2_residualization", "r2_baseline",
                         "sd_advglue_drop", "vif", "gate_sd_passed",
                         "gate_r2_passed", "gate_passed"]
        for k in required_keys:
            assert k in stats, f"Missing stats key: {k}"

    def test_compute_stats_types(self, base_df):
        comp = RIComputer()
        _, stats = comp.compute(base_df)
        assert isinstance(stats["gate_sd_passed"], bool)
        assert isinstance(stats["gate_r2_passed"], bool)
        assert isinstance(stats["gate_passed"], bool)


class TestComputeResidualInstability:
    def test_top_level_returns_tuple(self, base_df):
        df_out, stats = compute_residual_instability(base_df)
        assert isinstance(df_out, pd.DataFrame)
        assert isinstance(stats, dict)

    def test_output_has_pc1_and_ri(self, base_df):
        df_out, _ = compute_residual_instability(base_df)
        assert "PC1" in df_out.columns
        assert "RI" in df_out.columns

    def test_sd_advglue_positive(self, base_df):
        _, stats = compute_residual_instability(base_df)
        assert stats["sd_advglue_drop"] > 0

    def test_ri_nonzero_std(self, base_df):
        df_out, _ = compute_residual_instability(base_df)
        assert df_out["RI"].std() > 0.001
