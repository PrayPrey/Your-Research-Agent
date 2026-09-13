import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import torch
import tempfile, json
from stability import StabilityMonitor, StabilityError


def test_no_nan_stable():
    m = StabilityMonitor(seed=42)
    for i in range(10):
        loss = torch.tensor(1.0 - i * 0.05)
        assert not m.check_nan(loss)
        m.update(loss.item(), i)
    assert m.nan_events == 0
    assert m.is_stable()


def test_nan_detection():
    m = StabilityMonitor(seed=42)
    nan_loss = torch.tensor(float("nan"))
    assert m.check_nan(nan_loss)
    assert m.nan_events == 1
    assert not m.is_stable()


def test_divergence_detection():
    m = StabilityMonitor(seed=42, moving_avg_window=10, divergence_factor=2.0)
    # Fill window with stable losses
    for i in range(15):
        m.update(1.0, i)
        m._loss_deque.append(1.0)
    # Now check a diverging loss
    diverged = m.check_divergence(5.0)
    assert diverged
    assert m.divergence_events == 1


def test_moving_average():
    m = StabilityMonitor(seed=42, moving_avg_window=5)
    for v in [1.0, 2.0, 3.0, 4.0, 5.0]:
        m._loss_deque.append(v)
    assert abs(m.get_moving_average() - 3.0) < 1e-6


def test_get_report():
    m = StabilityMonitor(seed=123)
    m.update(0.5, 0)
    m.record_grad_norms(0, 0.1, 0.2)
    report = m.get_report()
    assert report["seed"] == 123
    assert report["nan_events"] == 0
    assert report["divergence_events"] == 0
    assert len(report["loss_history"]) == 1
    assert len(report["grad_norm_history"]) == 1


def test_save_report():
    m = StabilityMonitor(seed=42)
    m.update(1.0, 0)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "seed42", "stability_log.json")
        m.save_report(path)
        with open(path) as f:
            data = json.load(f)
        assert data["seed"] == 42
