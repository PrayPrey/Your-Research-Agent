import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tempfile
from figures import (
    plot_longbench_comparison,
    plot_training_loss_curves,
    plot_loss_distribution,
    plot_per_task_f1,
    plot_gradient_norms,
)


def _tmppath(d, name):
    return os.path.join(d, name)


def test_longbench_comparison():
    joint = {"narrativeqa": 0.55, "qasper": 0.48, "multifieldqa_en": 0.60, "mean_f1": 0.543}
    b3 = {"narrativeqa": 0.50, "qasper": 0.44, "multifieldqa_en": 0.55, "mean_f1": 0.497}
    with tempfile.TemporaryDirectory() as d:
        path = _tmppath(d, "longbench_comparison.png")
        plot_longbench_comparison(joint, b3, save_path=path)
        assert os.path.exists(path)


def test_training_loss_curves():
    histories = {42: [1.0, 0.9, 0.8], 123: [1.1, 0.95, 0.85], 456: [1.05, 0.92, 0.82]}
    with tempfile.TemporaryDirectory() as d:
        path = _tmppath(d, "training_loss_curves.png")
        plot_training_loss_curves(histories, save_path=path)
        assert os.path.exists(path)


def test_loss_distribution():
    epoch_end = {42: [0.8, 0.79, 0.81], 123: [0.85, 0.84, 0.86], 456: [0.82, 0.81, 0.83]}
    with tempfile.TemporaryDirectory() as d:
        path = _tmppath(d, "loss_distribution.png")
        plot_loss_distribution(epoch_end, save_path=path)
        assert os.path.exists(path)


def test_per_task_f1():
    joint = {"narrativeqa": 0.55, "qasper": 0.48, "multifieldqa_en": 0.60}
    b3 = {"narrativeqa": 0.50, "qasper": 0.44, "multifieldqa_en": 0.55}
    with tempfile.TemporaryDirectory() as d:
        path = _tmppath(d, "per_task_f1.png")
        plot_per_task_f1(joint, b3, save_path=path)
        assert os.path.exists(path)


def test_gradient_norms():
    lora = {42: [0.1, 0.09, 0.08], 123: [0.11, 0.1, 0.09], 456: [0.105, 0.095, 0.085]}
    locret = {42: [0.2, 0.18, 0.16], 123: [0.21, 0.19, 0.17], 456: [0.205, 0.185, 0.165]}
    with tempfile.TemporaryDirectory() as d:
        path = _tmppath(d, "gradient_norms.png")
        plot_gradient_norms(lora, locret, save_path=path)
        assert os.path.exists(path)
