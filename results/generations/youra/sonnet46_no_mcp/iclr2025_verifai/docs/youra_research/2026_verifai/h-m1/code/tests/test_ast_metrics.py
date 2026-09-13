import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np
from ast_metrics import ASTFailureRateComputer


def _make_pool(task_ids, ast_valids_per_task):
    """Helper: build pool dict from list of (task_id, [bool list]) pairs."""
    pool = {}
    for task_id, valids in zip(task_ids, ast_valids_per_task):
        pool[task_id] = [{"ast_valid": v, "completion": ""} for v in valids]
    return pool


class TestASTFailureRateComputer(unittest.TestCase):

    def setUp(self):
        self.computer = ASTFailureRateComputer()

    def test_all_valid_completions(self):
        pool = _make_pool(["t0", "t1"], [[True, True], [True, True]])
        rates = self.computer.compute_per_problem_rates(pool)
        for r in rates.values():
            self.assertAlmostEqual(r, 0.0)

    def test_all_invalid_completions(self):
        pool = _make_pool(["t0", "t1"], [[False, False], [False, False]])
        rates = self.computer.compute_per_problem_rates(pool)
        for r in rates.values():
            self.assertAlmostEqual(r, 1.0)

    def test_mixed_pool_compute_arrays(self):
        task_ids = [f"HumanEval/{i}" for i in range(164)]
        # baseline: half fail; syncode: all pass
        baseline_pool = _make_pool(task_ids, [[True, False] * 10 for _ in range(164)])
        syncode_pool = _make_pool(task_ids, [[True] * 20 for _ in range(164)])
        b_arr, s_arr, t_ids = self.computer.compute_arrays(baseline_pool, syncode_pool)
        self.assertEqual(b_arr.shape, (164,))
        self.assertEqual(s_arr.shape, (164,))
        self.assertEqual(len(t_ids), 164)

    def test_delta_ast_positive(self):
        task_ids = ["t0", "t1"]
        baseline = _make_pool(task_ids, [[False, False], [False, False]])
        syncode = _make_pool(task_ids, [[True, True], [True, True]])
        b_arr, s_arr, _ = self.computer.compute_arrays(baseline, syncode)
        delta = self.computer.compute_delta_ast(b_arr, s_arr)
        self.assertGreater(delta, 0)

    def test_arrays_aligned_shape(self):
        task_ids = [f"HumanEval/{i}" for i in range(164)]
        baseline_pool = _make_pool(task_ids, [[True] * 20 for _ in range(164)])
        syncode_pool = _make_pool(task_ids, [[True] * 20 for _ in range(164)])
        b_arr, s_arr, t_ids = self.computer.compute_arrays(baseline_pool, syncode_pool)
        self.assertEqual(b_arr.shape, (164,))
        self.assertEqual(s_arr.shape, (164,))


if __name__ == "__main__":
    unittest.main()
