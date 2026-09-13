"""Statistical validation and gate checking."""

from typing import List, Dict
from scipy import stats


class StatisticalValidator:
    """Compute success rates and validate against gates."""

    def __init__(self, gate_threshold: float = 0.65, baseline: float = 0.50):
        self.gate_threshold = gate_threshold
        self.baseline = baseline

    def compute_success_rate(self, p_values: List[float], alpha: float = 0.05) -> float:
        """Calculate proportion of p < alpha results."""
        successes = sum(1 for p in p_values if p < alpha)
        return successes / len(p_values)

    def binomial_test(self, successes: int, n: int, p0: float = 0.50) -> float:
        """Test if success rate significantly exceeds random baseline.

        Returns: p-value for binomial test
        """
        # One-sided binomial test (H1: p > p0)
        p_value = stats.binomtest(successes, n, p0, alternative='greater').pvalue
        return p_value

    def check_gate(self, success_rate: float, p_values: List[float]) -> Dict:
        """Validate against MUST_WORK gate.

        Returns: {success_rate, gate_passed, poc_passed, binomial_p, status}
        """
        gate_passed = success_rate >= self.gate_threshold
        poc_passed = success_rate > self.baseline

        # Binomial test
        successes = sum(1 for p in p_values if p < 0.05)
        n = len(p_values)
        binomial_p = self.binomial_test(successes, n, self.baseline)

        # Determine status
        if gate_passed:
            status = "PASS"
        elif poc_passed:
            status = "PARTIAL"
        else:
            status = "FAIL"

        return {
            "success_rate": success_rate,
            "gate_passed": gate_passed,
            "poc_passed": poc_passed,
            "binomial_p": binomial_p,
            "status": status,
            "successes": successes,
            "n_samples": n,
        }
