"""Tests for token_estimator.py, results.py, gate.py."""
import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from token_estimator import estimate_tokens, sum_tokens
from results import build_aggregate, write_json, write_jsonl, FULL_SUBSET_SIZE
from gate import run_gate_check


SAMPLE_PER_FILE = [
    {"file_id": "0", "content_len": 100, "phase_a": True, "phase_b": True, "n_doctest_examples": 2,
     "phase_c": True, "error_type": None, "parse_error": None, "estimated_tokens": 50},
    {"file_id": "1", "content_len": 50, "phase_a": False, "phase_b": False, "n_doctest_examples": 0,
     "phase_c": None, "error_type": None, "parse_error": None, "estimated_tokens": 0},
] * 5000  # 10000 total


def test_estimate_tokens():
    assert estimate_tokens("hello world") == int(2 * 1.3)


def test_sum_tokens():
    assert sum_tokens(["hello world", "foo bar baz"]) == int(2*1.3) + int(3*1.3)


def test_build_aggregate_fields():
    agg = build_aggregate(SAMPLE_PER_FILE, 10.0)
    for key in ["n_sampled", "n_pattern_positive", "n_ast_positive", "n_executable_positive",
                "doctest_pattern_rate", "doctest_ast_rate", "doctest_executable_rate",
                "estimated_full_subset_executable_files", "estimated_token_pool_M",
                "scan_duration_seconds", "seed", "dataset", "filter"]:
        assert key in agg


def test_build_aggregate_values():
    agg = build_aggregate(SAMPLE_PER_FILE, 10.0)
    assert agg["n_sampled"] == 10000
    assert agg["n_executable_positive"] == 5000
    assert abs(agg["doctest_executable_rate"] - 0.5) < 0.001


def test_write_json():
    agg = build_aggregate(SAMPLE_PER_FILE, 1.0)
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    write_json(agg, path)
    with open(path) as f:
        loaded = json.load(f)
    assert loaded["n_sampled"] == 10000
    os.unlink(path)


def test_write_jsonl():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = f.name
    write_jsonl(SAMPLE_PER_FILE[:10], path)
    with open(path) as f:
        lines = f.readlines()
    assert len(lines) == 10
    os.unlink(path)


def test_gate_pass():
    agg = {"doctest_executable_rate": 0.05, "doctest_pattern_rate": 0.10, "n_sampled": 10000}
    assert run_gate_check(agg) == "PASS"


def test_gate_scope():
    agg = {"doctest_executable_rate": 0.02, "doctest_pattern_rate": 0.10, "n_sampled": 10000}
    assert run_gate_check(agg) == "SCOPE"


def test_gate_pivot():
    agg = {"doctest_executable_rate": 0.005, "doctest_pattern_rate": 0.10, "n_sampled": 10000}
    assert run_gate_check(agg) == "PIVOT"
