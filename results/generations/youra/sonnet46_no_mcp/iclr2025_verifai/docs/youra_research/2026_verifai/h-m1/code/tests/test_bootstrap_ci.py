import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np
from bootstrap_ci import BootstrapCI


class TestBootstrapCI(unittest.TestCase):

    def setUp(self):
        self.ci = BootstrapCI(n_bootstrap=1000, alpha=0.05)

    def test_delta_zero_p_value_near_half(self):
        rates = np.array([0.5] * 164)
        delta_mean, ci_lower, ci_upper, p_value = self.ci.compute(rates, rates)
        self.assertAlmostEqual(delta_mean, 0.0, places=5)
        self.assertGreater(p_value, 0.3)

    def test_strong_signal_pass_gate(self):
        baseline = np.array([0.5] * 164)
        syncode = np.array([0.1] * 164)
        delta_mean, ci_lower, ci_upper, p_value = self.ci.compute(baseline, syncode)
        gate = self.ci.evaluate_gate(delta_mean, ci_lower)
        self.assertEqual(gate, "PASS")
        self.assertGreater(delta_mean, 0)
        self.assertGreater(ci_lower, 0)

    def test_negative_delta_fail_gate(self):
        baseline = np.array([0.1] * 164)
        syncode = np.array([0.5] * 164)
        delta_mean, ci_lower, ci_upper, p_value = self.ci.compute(baseline, syncode)
        gate = self.ci.evaluate_gate(delta_mean, ci_lower)
        self.assertEqual(gate, "FAIL")

    def test_gate_pass(self):
        gate = self.ci.evaluate_gate(0.05, 0.01)
        self.assertEqual(gate, "PASS")

    def test_gate_partial(self):
        gate = self.ci.evaluate_gate(0.02, -0.01)
        self.assertEqual(gate, "PARTIAL")

    def test_gate_fail(self):
        gate = self.ci.evaluate_gate(-0.01, -0.05)
        self.assertEqual(gate, "FAIL")

    def test_deterministic(self):
        baseline = np.random.rand(164) * 0.5
        syncode = np.random.rand(164) * 0.3
        ci1 = BootstrapCI(n_bootstrap=100, alpha=0.05)
        ci2 = BootstrapCI(n_bootstrap=100, alpha=0.05)
        r1 = ci1.compute(baseline, syncode)
        r2 = ci2.compute(baseline, syncode)
        self.assertAlmostEqual(r1[0], r2[0], places=10)
        self.assertAlmostEqual(r1[1], r2[1], places=10)

    def test_perfect_improvement(self):
        baseline = np.array([0.8] * 164)
        syncode = np.array([0.3] * 164)
        delta_mean, ci_lower, ci_upper, p_value = self.ci.compute(baseline, syncode)
        self.assertGreater(delta_mean, 0)
        self.assertLess(p_value, 0.05)


if __name__ == "__main__":
    unittest.main()
