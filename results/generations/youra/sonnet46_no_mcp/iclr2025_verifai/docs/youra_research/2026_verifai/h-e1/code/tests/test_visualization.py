import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import pytest
from visualization import Visualizer


SAMPLE_METRICS = {
    "delta_ast": 0.15,
    "z3_eligibility_rate": 0.20,
    "mypy_structured_rate": 0.95,
    "gate_pass": True,
    "gate_checks": {
        "delta_ast_pass": True,
        "z3_rate_pass": True,
        "mypy_rate_pass": True,
    },
}

SAMPLE_ELIGIBILITY = {f"t{i}": (i % 3 != 0) for i in range(20)}

SAMPLE_MYPY_RESULTS = {
    f"t{i}": {
        "exit_code": 0 if i % 2 == 0 else 1,
        "parsed_errors": [{"error_code": "assignment", "line": 1, "col": 1, "message": "error"}]
        if i % 3 == 0 else [],
    }
    for i in range(10)
}


def test_figures_saved():
    with tempfile.TemporaryDirectory() as tmpdir:
        viz = Visualizer(tmpdir)
        baseline_pool = {f"t{i}": ["def f():\n    pass\n"] * 5 for i in range(10)}
        syncode_pool = {f"t{i}": ["def f():\n    pass\n"] * 5 for i in range(10)}
        pools = {"baseline": baseline_pool, "syncode": syncode_pool}
        viz.save_all(SAMPLE_METRICS, pools, SAMPLE_ELIGIBILITY, SAMPLE_MYPY_RESULTS)

        expected = [
            "gate_metrics.pdf", "gate_metrics.png",
            "ast_failure_heatmap.pdf", "ast_failure_heatmap.png",
            "z3_eligibility.pdf", "z3_eligibility.png",
            "mypy_error_types.pdf", "mypy_error_types.png",
        ]
        files = os.listdir(tmpdir)
        for fname in expected:
            assert fname in files, f"Missing figure: {fname}"


def test_gate_metrics_runs():
    with tempfile.TemporaryDirectory() as tmpdir:
        viz = Visualizer(tmpdir)
        viz.plot_gate_metrics(SAMPLE_METRICS)
        assert os.path.exists(os.path.join(tmpdir, "gate_metrics.png"))
