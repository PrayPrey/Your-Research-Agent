import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import tempfile
from visualize import (
    plot_gate_metrics_comparison,
    plot_delta_acc_distribution,
    plot_orbit_pe_success_table,
    plot_per_seed_stability,
)


def test_plot_gate_metrics_comparison():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "gate.png")
        plot_gate_metrics_comparison(0.0001, 0.0002, 0.001, path)
        assert os.path.exists(path)


def test_plot_delta_acc_distribution():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "dist.png")
        cnn = [0.0001, 0.0002, 0.0]
        tf = [0.0, 0.0001]
        plot_delta_acc_distribution(cnn, tf, path)
        assert os.path.exists(path)


def test_plot_orbit_pe_success_table():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "table.png")
        flags = {"fc.weight": True, "conv.weight": True, "attn.queries.weight": True}
        plot_orbit_pe_success_table(flags, path)
        assert os.path.exists(path)


def test_plot_per_seed_stability():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "seeds.png")
        cnn = [{"seed": s, "delta_acc": 0.0001} for s in range(10)]
        tf = [{"seed": s, "delta_acc": 0.0002} for s in range(10)]
        plot_per_seed_stability(cnn, tf, path)
        assert os.path.exists(path)
