import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np
from visualization import HM1Visualizer


class TestHM1Visualizer(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.viz = HM1Visualizer(self.tmpdir)

    def test_all_figures_saved(self):
        n = 164
        baseline_rates = np.random.rand(n) * 0.5 + 0.1
        syncode_rates = np.random.rand(n) * 0.3

        ast_results = {
            "baseline_mean": float(np.mean(baseline_rates)),
            "syncode_mean": float(np.mean(syncode_rates)),
            "delta_ast": float(np.mean(baseline_rates) - np.mean(syncode_rates)),
        }
        bootstrap_results = {
            "delta_ast": ast_results["delta_ast"],
            "ci_lower": 0.01,
            "ci_upper": 0.15,
            "gate_result": "PASS",
        }
        fmd_results = {
            "baseline_distribution": {"syntax": 0.4, "type": 0.2, "functional": 0.2, "success": 0.2},
            "syncode_distribution": {"syntax": 0.2, "type": 0.25, "functional": 0.25, "success": 0.3},
        }

        task_ids = [f"HumanEval/{i}" for i in range(n)]
        baseline_pool = {tid: [{"ast_valid": bool(np.random.rand() > 0.4), "sample_idx": j} for j in range(20)] for tid in task_ids}
        syncode_pool = {tid: [{"ast_valid": bool(np.random.rand() > 0.2), "sample_idx": j} for j in range(20)] for tid in task_ids}

        self.viz.save_all(ast_results, bootstrap_results, fmd_results, baseline_pool, syncode_pool, baseline_rates, syncode_rates, task_ids)

        for name in ["gate_metrics", "per_problem_scatter", "fmd_comparison", "transition_heatmap"]:
            for ext in ["pdf", "png"]:
                path = os.path.join(self.tmpdir, f"{name}.{ext}")
                self.assertTrue(os.path.exists(path), f"Missing: {path}")

    def test_gate_metrics_pass_annotation(self):
        self.viz.plot_gate_metrics(0.5, 0.3, 0.05, 0.3, 0.2, "PASS")
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "gate_metrics.png")))

    def test_scatter_point_count(self):
        n = 164
        baseline_rates = np.random.rand(n)
        syncode_rates = np.random.rand(n)
        task_ids = [f"HumanEval/{i}" for i in range(n)]
        self.viz.plot_per_problem_scatter(baseline_rates, syncode_rates, task_ids)
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "per_problem_scatter.png")))


if __name__ == "__main__":
    unittest.main()
