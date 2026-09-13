"""Tests for evaluate.py — spec compliance tests for H-E1."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import tempfile
import pytest
import pandas as pd
import numpy as np

from data_assembly import assemble_matrix
from compute_ri import compute_residual_instability
from evaluate import GateEvaluator, run_evaluation
import config


@pytest.fixture(scope="module")
def enriched_df_and_stats():
    df = assemble_matrix()
    df_out, stats = compute_residual_instability(df)
    return df_out, stats


class TestGateEvaluator:
    def test_check_gate_returns_dict(self, enriched_df_and_stats):
        df, stats = enriched_df_and_stats
        ev = GateEvaluator()
        gate = ev.check_gate(df, stats)
        assert isinstance(gate, dict)

    def test_check_gate_required_keys(self, enriched_df_and_stats):
        df, stats = enriched_df_and_stats
        ev = GateEvaluator()
        gate = ev.check_gate(df, stats)
        required = ["gate_passed", "gate_sd_passed", "gate_r2_passed",
                    "sd_advglue_drop", "sd_ci_lower", "sd_ci_upper",
                    "r2_residualization", "r2_ci_lower", "r2_ci_upper",
                    "n_models", "n_families", "n_scales", "n_regimes"]
        for k in required:
            assert k in gate, f"Missing gate key: {k}"

    def test_check_gate_n_models(self, enriched_df_and_stats):
        df, stats = enriched_df_and_stats
        ev = GateEvaluator()
        gate = ev.check_gate(df, stats)
        assert gate["n_models"] >= 30

    def test_check_gate_families(self, enriched_df_and_stats):
        df, stats = enriched_df_and_stats
        ev = GateEvaluator()
        gate = ev.check_gate(df, stats)
        assert gate["n_families"] >= 3

    def test_bootstrap_ci_returns_dict(self, enriched_df_and_stats):
        df, stats = enriched_df_and_stats
        ev = GateEvaluator(n_bootstrap=100)  # fast for testing
        ci = ev.bootstrap_ci(df)
        assert "sd_ci" in ci
        assert "r2_ci" in ci

    def test_bootstrap_ci_bounds_valid(self, enriched_df_and_stats):
        df, stats = enriched_df_and_stats
        ev = GateEvaluator(n_bootstrap=100)
        ci = ev.bootstrap_ci(df)
        assert ci["sd_ci"][0] <= ci["sd_ci"][1]
        assert ci["r2_ci"][0] <= ci["r2_ci"][1]

    def test_verify_mechanism_activated_returns_tuple(self, enriched_df_and_stats):
        df, stats = enriched_df_and_stats
        ev = GateEvaluator()
        passed, gate = ev.verify_mechanism_activated(df, stats)
        assert isinstance(passed, bool)
        assert isinstance(gate, dict)

    def test_export_results_creates_files(self, enriched_df_and_stats):
        df, stats = enriched_df_and_stats
        ev = GateEvaluator()
        gate = ev.check_gate(df, stats)
        with tempfile.TemporaryDirectory() as tmpdir:
            ev.export_results(df, stats, gate, tmpdir)
            assert os.path.exists(os.path.join(tmpdir, "model_matrix.csv"))
            assert os.path.exists(os.path.join(tmpdir, "gate_results.yaml"))
            assert os.path.exists(os.path.join(tmpdir, "stats_summary.json"))

    def test_export_results_json_valid(self, enriched_df_and_stats):
        df, stats = enriched_df_and_stats
        ev = GateEvaluator()
        gate = ev.check_gate(df, stats)
        with tempfile.TemporaryDirectory() as tmpdir:
            ev.export_results(df, stats, gate, tmpdir)
            with open(os.path.join(tmpdir, "stats_summary.json")) as f:
                data = json.load(f)
            assert "gate" in data
            assert "n_models" in data


class TestRunEvaluation:
    def test_run_evaluation_returns_gate(self, enriched_df_and_stats):
        df, stats = enriched_df_and_stats
        with tempfile.TemporaryDirectory() as tmpdir:
            gate = run_evaluation(df, stats, tmpdir)
        assert isinstance(gate, dict)
        assert "gate_passed" in gate
