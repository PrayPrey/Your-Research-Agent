"""Unit tests for src/serialize.py"""
import os, sys
import json
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.serialize import build_results_dict, save_results, save_gate_result


def make_results():
    return {
        "log_rank_p": 0.02,
        "cox_hr": 1.5,
        "cox_ci_lower": 1.1,
        "cox_ci_upper": 2.0,
        "cox_p": 0.01,
        "median_ttfr_high": 100.0,
        "median_ttfr_low": 200.0,
        "n_matched_pairs": 150,
        "smd_max": 0.08,
        "n_cohort_filtered": 800,
        "baseline_log_rank_p": 0.01,
        "baseline_cox_hr": None,
        "ablations": {},
        "sensitivity": {},
    }


def test_build_results_dict_has_required_keys():
    primary = {"log_rank_p": 0.02, "cox_hr": 1.5, "cox_ci_lower": 1.1, "cox_ci_upper": 2.0,
               "cox_p": 0.01, "median_ttfr_high": 100.0, "median_ttfr_low": 200.0, "n_cohort_filtered": 800}
    unadjusted = {"baseline_log_rank_p": 0.01}
    meta = {"n_matched_pairs": 150, "smd_max": 0.08}
    result = build_results_dict(primary, unadjusted, meta, {}, {})
    assert "log_rank_p" in result
    assert "cox_hr" in result
    assert "n_matched_pairs" in result


def test_save_gate_result_pass(tmp_path):
    results = make_results()
    path = save_gate_result(results, str(tmp_path), log_rank_alpha=0.05, cox_hr_gate=1.2)
    with open(path) as f:
        gate = json.load(f)
    assert gate["result"] == "PASS"
    assert gate["primary_gate"]["passed"] == True


def test_save_gate_result_fail(tmp_path):
    results = make_results()
    results["log_rank_p"] = 0.3  # fails primary gate
    path = save_gate_result(results, str(tmp_path), log_rank_alpha=0.05, cox_hr_gate=1.2)
    with open(path) as f:
        gate = json.load(f)
    assert gate["result"] == "FAIL"


def test_save_results_creates_files(tmp_path):
    results = make_results()
    paths = save_results(results, str(tmp_path))
    assert os.path.exists(paths["json_path"])
    assert os.path.exists(paths["csv_path"])
