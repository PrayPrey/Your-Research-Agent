"""Tests for orbit_statistics.py (task-007, task-014, task-015-subtask)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from orbit_statistics import compute_orbit_statistics, per_decile_proportions, evaluate_gate


def _make_pair(decile=0, dist_override=None):
    """Make a mock pair with known cosine distance."""
    w1 = torch.ones(100)
    if dist_override is not None and dist_override > 0.01:
        w2 = torch.randn(100)
    else:
        w2 = torch.ones(100)

    sd1 = {"weights_flat": w1}
    sd2 = {"weights_flat": w2}
    m1 = {"state_dict": sd1, "test_accuracy": 0.9, "_flat_weights": True}
    m2 = {"state_dict": sd2, "test_accuracy": 0.91, "_flat_weights": True}
    return (m1, m2, decile)


def test_compute_orbit_statistics_returns_tuple():
    pairs = [_make_pair(d) for d in range(10)]
    distances, proportion = compute_orbit_statistics(pairs, cosine_dist_threshold=0.1)
    assert isinstance(distances, list)
    assert isinstance(proportion, float)
    assert 0.0 <= proportion <= 1.0
    assert len(distances) == len(pairs)


def test_compute_orbit_statistics_keys():
    pairs = [_make_pair(0)]
    distances, _ = compute_orbit_statistics(pairs)
    assert "decile" in distances[0]
    assert "cosine_dist" in distances[0]
    assert "is_orbit_candidate" in distances[0]


def test_per_decile_proportions_keys():
    distances = [{"decile": d, "cosine_dist": 0.2, "is_orbit_candidate": True} for d in range(10)]
    result = per_decile_proportions(distances)
    assert set(result.keys()) == set(range(10))


def test_evaluate_gate_pass():
    result = evaluate_gate(bn_free=True, orbit_proportion=0.5, threshold=0.05)
    assert result["passed"] is True
    assert result["message"] == "PASS"


def test_evaluate_gate_fail_bn():
    result = evaluate_gate(bn_free=False, orbit_proportion=0.5, threshold=0.05)
    assert result["passed"] is False
    assert result["message"] == "FAIL"


def test_evaluate_gate_fail_proportion():
    result = evaluate_gate(bn_free=True, orbit_proportion=0.01, threshold=0.05)
    assert result["passed"] is False


def test_evaluate_gate_result_schema():
    result = evaluate_gate(bn_free=True, orbit_proportion=0.3)
    assert "passed" in result
    assert "bn_free" in result
    assert "orbit_proportion" in result
    assert "threshold" in result
    assert "message" in result
    assert result["message"] in ("PASS", "FAIL")
