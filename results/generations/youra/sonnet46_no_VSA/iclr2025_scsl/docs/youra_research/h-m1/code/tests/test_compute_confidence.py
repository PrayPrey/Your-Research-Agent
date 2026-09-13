"""Spec compliance tests for compute_confidence.py"""
import sys
import os
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
sys.path.insert(0, config.H_E3_CODE)


def test_extract_confidence_shape_and_range():
    """extract_confidence_by_group returns correct shapes and valid probabilities."""
    from compute_confidence import extract_confidence_by_group
    import torch.nn as nn

    # Dummy model that outputs logits favoring class 0
    class DummyModel(nn.Module):
        def forward(self, x):
            B = x.shape[0]
            return torch.stack([torch.ones(B), torch.zeros(B)], dim=1)

    # Minimal fake loader: 10 samples, 240 minority
    N = 4795
    minority_mask = torch.zeros(N, dtype=torch.bool)
    minority_mask[:240] = True

    class FakeLoader:
        def __iter__(self):
            # Yield 2 batches: 240 and 4555 samples
            y = torch.zeros(240, dtype=torch.long)
            x = torch.zeros(240, 3, 224, 224)
            yield x, y, torch.zeros(240)
            y2 = torch.zeros(4555, dtype=torch.long)
            x2 = torch.zeros(4555, 3, 224, 224)
            yield x2, y2, torch.zeros(4555)

    model = DummyModel()
    p_per_sample, p_min, p_maj = extract_confidence_by_group(
        model, FakeLoader(), minority_mask, "cpu"
    )
    assert p_per_sample.shape == (N,), f"Expected ({N},), got {p_per_sample.shape}"
    assert 0.0 <= p_min <= 1.0, f"p_min={p_min} out of [0,1]"
    assert 0.0 <= p_maj <= 1.0, f"p_maj={p_maj} out of [0,1]"


def test_check_gate_logic():
    """check_gate returns correct booleans per gate thresholds."""
    from compute_confidence import check_gate

    # Primary pass: p_min in [0.3, 0.7]
    p1, s1 = check_gate(0.5, 0.85)
    assert p1 is True, "0.5 should be in [0.3, 0.7]"
    assert s1 is True, "0.85 > 0.80"

    # Primary fail: p_min < 0.3
    p2, s2 = check_gate(0.1, 0.90)
    assert p2 is False, "0.1 should not be in [0.3, 0.7]"
    assert s2 is True

    # Secondary fail: p_maj <= 0.80
    p3, s3 = check_gate(0.5, 0.75)
    assert p3 is True
    assert s3 is False, "0.75 <= 0.80"


def test_verify_mechanism_activated():
    """verify_mechanism_activated returns True when >=4 seeds pass primary gate."""
    from compute_confidence import verify_mechanism_activated

    def make_traj(p_min, p_maj, tstar=20):
        return {
            tstar: {"p_min": p_min, "p_maj": p_maj, "p_per_sample": torch.tensor([p_min])},
            "tstar": tstar,
        }

    # 4 seeds pass, 1 fails → mechanism_active = True
    results = {
        1: make_traj(0.45, 0.88),
        2: make_traj(0.55, 0.91),
        3: make_traj(0.40, 0.85),
        4: make_traj(0.60, 0.83),
        5: make_traj(0.20, 0.90),  # primary fails: 0.20 < 0.3
    }
    active, indicators = verify_mechanism_activated(results)
    assert active is True, f"Expected True, got {active}"
    assert indicators[5]["minority_boundary"] is False

    # 3 seeds pass → mechanism_active = False
    results[4] = make_traj(0.15, 0.90)  # also fails
    active2, _ = verify_mechanism_activated(results)
    assert active2 is False, f"Expected False, got {active2}"
