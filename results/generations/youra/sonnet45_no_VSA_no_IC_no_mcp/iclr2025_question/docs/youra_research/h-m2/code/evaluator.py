"""Success criteria evaluation."""


class SuccessEvaluator:
    """Evaluate results against H-M2 success criteria."""

    def __init__(self, reduction_threshold: float = 40.0, p_threshold: float = 0.05):
        """Initialize with success thresholds."""
        self.reduction_threshold = reduction_threshold
        self.p_threshold = p_threshold

    def evaluate(self, mean_reduction: float, p_value: float) -> dict:
        """
        Classify result as PASS/PARTIAL/FAIL.
        Returns: {
            "result": str ("PASS" | "PARTIAL" | "FAIL"),
            "reduction_ok": bool,
            "significance_ok": bool
        }
        """
        reduction_ok = mean_reduction > self.reduction_threshold
        significance_ok = p_value < self.p_threshold

        if reduction_ok and significance_ok:
            result = "PASS"
        elif 20.0 <= mean_reduction < self.reduction_threshold and significance_ok:
            result = "PARTIAL"
        else:
            result = "FAIL"

        return {
            "result": result,
            "reduction_ok": reduction_ok,
            "significance_ok": significance_ok
        }

    def classify_result(self, reduction: float, p_value: float) -> str:
        """One-line classification helper."""
        return self.evaluate(reduction, p_value)["result"]
