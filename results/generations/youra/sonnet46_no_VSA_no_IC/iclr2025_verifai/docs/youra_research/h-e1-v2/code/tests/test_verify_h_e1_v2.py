"""Integration tests for H-E1-v2 verification script."""
import pathlib
import sys

# Allow importing from parent code/ dir
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from verify_h_e1_v2 import verify_h_e1_v2

ARCHIVE = pathlib.Path(
    "docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results"
)


def test_gate_passes():
    results = verify_h_e1_v2(str(ARCHIVE))
    assert results["gate_passed"], f"Gate failed: {results}"


def test_c1_counts():
    results = verify_h_e1_v2(str(ARCHIVE))
    assert results["c1_failure_ids"]["he_count"] == 34
    assert results["c1_failure_ids"]["mbpp_count"] == 100
    assert results["c1_failure_ids"]["total"] == 134


def test_c2_full_coverage():
    results = verify_h_e1_v2(str(ARCHIVE))
    assert results["c2_stored_solutions"]["he_covered"] == 34
    assert results["c2_stored_solutions"]["mbpp_covered"] == 100


def test_c3_api_accessible():
    results = verify_h_e1_v2(str(ARCHIVE))
    assert results["c3_evalplus_api"]["he_tasks_in_api"] == 34
    assert results["c3_evalplus_api"]["mbpp_tasks_in_api"] == 100


def test_c4_deterministic():
    results = verify_h_e1_v2(str(ARCHIVE))
    assert results["c4_deterministic_test"]["plus_input_count"] > 0
