import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fmd_classifier import FMDClassifier


class TestFMDClassifier(unittest.TestCase):

    def setUp(self):
        self.clf = FMDClassifier()

    def test_syntax_category(self):
        invalid_python = "def foo(:\n    pass"
        cat = self.clf.classify_completion(invalid_python, "t0", {})
        self.assertEqual(cat, "syntax")

    def test_success_or_type_or_functional_for_valid(self):
        valid_python = "def foo(x):\n    return x + 1\n"
        cat = self.clf.classify_completion(valid_python, "t0", {})
        self.assertIn(cat, ["type", "functional", "success"])

    def test_distribution_sums_to_one(self):
        classifications = {
            "t0": ["syntax", "type", "functional", "success"],
            "t1": ["syntax", "success"],
        }
        dist = self.clf.compute_distribution(classifications)
        self.assertAlmostEqual(sum(dist.values()), 1.0, places=6)

    def test_distribution_has_four_categories(self):
        classifications = {"t0": ["syntax"]}
        dist = self.clf.compute_distribution(classifications)
        self.assertIn("syntax", dist)
        self.assertIn("type", dist)
        self.assertIn("functional", dist)
        self.assertIn("success", dist)

    def test_syntax_shift_positive(self):
        b = {"syntax": 0.5, "type": 0.3, "functional": 0.1, "success": 0.1}
        s = {"syntax": 0.2, "type": 0.4, "functional": 0.2, "success": 0.2}
        shift = self.clf.compute_syntax_shift(b, s)
        self.assertGreater(shift, 0)


if __name__ == "__main__":
    unittest.main()
