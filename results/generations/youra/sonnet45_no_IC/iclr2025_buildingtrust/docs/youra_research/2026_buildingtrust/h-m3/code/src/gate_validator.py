"""
Gate Validator for H-M3 SHOULD_WORK Criteria
"""

from typing import Dict


class MechanismGateValidator:
    """Validate SHOULD_WORK gate criteria for mechanism hypothesis."""

    def __init__(
        self,
        p_threshold: float = 0.05,
        delta_r_threshold: float = 0.1
    ):
        """
        Initialize gate validator.

        Args:
            p_threshold: Significance threshold (default: 0.05)
            delta_r_threshold: Minimum correlation difference (default: 0.1)
        """
        self.p_threshold = p_threshold
        self.delta_r_threshold = delta_r_threshold

    def validate_primary_criterion(self, fisher_result: Dict) -> bool:
        """
        Fisher z-test p < 0.05.

        Args:
            fisher_result: Fisher test results dict

        Returns:
            True if passed
        """
        return fisher_result["p_value"] < self.p_threshold

    def validate_secondary_criterion(self, r_factual: float, r_misinfo: float) -> bool:
        """
        |r_factual - r_misinfo| >= 0.1.

        Args:
            r_factual: Factual stratum correlation
            r_misinfo: Misinformation stratum correlation

        Returns:
            True if passed
        """
        delta_r = abs(r_factual - r_misinfo)
        return delta_r >= self.delta_r_threshold

    def validate_tertiary_criterion(self, r_factual: float, r_misinfo: float) -> bool:
        """
        r_factual > 0.4 AND r_misinfo < 0.3.

        Args:
            r_factual: Factual stratum correlation
            r_misinfo: Misinformation stratum correlation

        Returns:
            True if passed
        """
        return (r_factual > 0.4) and (r_misinfo < 0.3)

    def evaluate_gate(
        self,
        fisher_result: Dict,
        r_factual: float,
        r_misinfo: float
    ) -> Dict:
        """
        Evaluate SHOULD_WORK gate.

        Args:
            fisher_result: Fisher z-test results
            r_factual: Factual stratum correlation
            r_misinfo: Misinformation stratum correlation

        Returns:
            {
                "passed": bool,
                "gate_type": "SHOULD_WORK",
                "primary": bool,
                "secondary": bool,
                "tertiary": bool,
                "p_value": float,
                "delta_r": float,
                "result": str  # "PASS", "PARTIAL", "FAIL"
            }
        """
        primary = self.validate_primary_criterion(fisher_result)
        secondary = self.validate_secondary_criterion(r_factual, r_misinfo)
        tertiary = self.validate_tertiary_criterion(r_factual, r_misinfo)

        # SHOULD_WORK gate: all criteria must pass for PASS
        passed = primary and secondary and tertiary

        # Determine result string
        if passed:
            result = "PASS"
        elif primary or secondary:
            result = "PARTIAL"
        else:
            result = "FAIL"

        return {
            "passed": bool(passed),
            "gate_type": "SHOULD_WORK",
            "primary": bool(primary),
            "secondary": bool(secondary),
            "tertiary": bool(tertiary),
            "p_value": float(fisher_result["p_value"]),
            "delta_r": float(abs(r_factual - r_misinfo)),
            "result": result,
            "criteria": {
                "p_threshold": self.p_threshold,
                "delta_r_threshold": self.delta_r_threshold,
                "factual_r_threshold": 0.4,
                "misinfo_r_threshold": 0.3
            }
        }
