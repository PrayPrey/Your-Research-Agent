import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from transition_extractor import TransitionExtractor


def _pool(task_ids, ast_valids_list):
    pool = {}
    for task_id, valids in zip(task_ids, ast_valids_list):
        pool[task_id] = [
            {"task_id": task_id, "ast_valid": v, "sample_idx": i, "problem_idx": None}
            for i, v in enumerate(valids)
        ]
    return pool


class TestTransitionExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = TransitionExtractor()

    def test_transition_detected(self):
        baseline = _pool(["t0"], [[False, True]])
        syncode = _pool(["t0"], [[True, True]])
        transitions = self.extractor.extract(baseline, syncode)
        # sample 0: baseline=False, syncode=True -> transition
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0]["task_id"], "t0")
        self.assertEqual(transitions[0]["sample_idx"], 0)

    def test_no_false_positive(self):
        baseline = _pool(["t0"], [[True, True]])
        syncode = _pool(["t0"], [[True, True]])
        transitions = self.extractor.extract(baseline, syncode)
        self.assertEqual(len(transitions), 0)

    def test_transition_rate_in_range(self):
        task_ids = [f"HumanEval/{i}" for i in range(5)]
        baseline = _pool(task_ids, [[False] * 5 for _ in range(5)])
        syncode = _pool(task_ids, [[True] * 5 for _ in range(5)])
        transitions = self.extractor.extract(baseline, syncode)
        result = self.extractor.save_results(transitions, [], "/tmp/test_transitions.json")
        self.assertGreaterEqual(result["transition_rate"], 0.0)
        self.assertLessEqual(result["transition_rate"], 1.0)

    def test_json_keys(self):
        baseline = _pool(["t0"], [[False]])
        syncode = _pool(["t0"], [[True]])
        transitions = self.extractor.extract(baseline, syncode)
        coverage = self.extractor.compute_coverage_by_problem(transitions)
        result = self.extractor.save_results(transitions, coverage, "/tmp/test_transitions2.json")
        for key in ["transitions", "transition_count", "transition_rate", "coverage_by_problem"]:
            self.assertIn(key, result)


if __name__ == "__main__":
    unittest.main()
