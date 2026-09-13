import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from run_experiment import compute_summary_metrics, evaluate_gate, save_results
import tempfile, json


def test_compute_summary_metrics():
    results = [{"delta_acc": 0.0001}, {"delta_acc": 0.0002}, {"delta_acc": 0.0}]
    m = compute_summary_metrics(results)
    assert "mean" in m and "std" in m and "max" in m
    assert m["mean"] >= 0.0


def test_evaluate_gate_pass():
    metrics = {
        "mean_delta_acc_cnn": 0.0001,
        "mean_delta_acc_transformer": 0.0002,
        "orbit_pe_success_rate": 1.0,
    }
    assert evaluate_gate(metrics) is True


def test_evaluate_gate_fail_cnn():
    metrics = {
        "mean_delta_acc_cnn": 0.005,
        "mean_delta_acc_transformer": 0.0,
        "orbit_pe_success_rate": 1.0,
    }
    assert evaluate_gate(metrics) is False


def test_evaluate_gate_fail_orbit():
    metrics = {
        "mean_delta_acc_cnn": 0.0,
        "mean_delta_acc_transformer": 0.0,
        "orbit_pe_success_rate": 0.5,
    }
    assert evaluate_gate(metrics) is False


def test_save_results():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "results.json")
        metrics = {
            "mean_delta_acc_cnn": 0.0001,
            "mean_delta_acc_transformer": 0.0002,
            "orbit_pe_success_rate": 1.0,
        }
        save_results(metrics, gate_pass=True, path=path)
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert data["gate_pass"] is True
        assert "mean_delta_acc_cnn" in data
