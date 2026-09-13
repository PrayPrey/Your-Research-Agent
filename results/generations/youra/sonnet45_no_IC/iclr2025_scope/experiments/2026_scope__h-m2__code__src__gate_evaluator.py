"""
Gate Evaluator: SHOULD_WORK gate logic
"""

from typing import Tuple


class GateEvaluator:
    """Evaluate SHOULD_WORK gate criteria."""
    
    def __init__(
        self,
        pass_cv_threshold: float = 0.35,
        pass_gap_threshold: float = 0.20,
        partial_cv_threshold: float = 0.30,
        partial_gap_threshold: float = 0.25
    ):
        """
        Initialize gate evaluator.
        
        Args:
            pass_cv_threshold: Min CV accuracy for PASS
            pass_gap_threshold: Max generalization gap for PASS
            partial_cv_threshold: Min CV accuracy for PARTIAL
            partial_gap_threshold: Max generalization gap for PARTIAL
        """
        self.pass_cv_threshold = pass_cv_threshold
        self.pass_gap_threshold = pass_gap_threshold
        self.partial_cv_threshold = partial_cv_threshold
        self.partial_gap_threshold = partial_gap_threshold
    
    def evaluate(
        self,
        cv_accuracy: float,
        generalization_gap: float
    ) -> Tuple[str, str]:
        """
        Evaluate gate criteria.
        
        Args:
            cv_accuracy: Cross-validation accuracy
            generalization_gap: Mean train-test gap
        
        Returns:
            result: "PASS", "PARTIAL", or "FAIL"
            message: Human-readable explanation
        """
        # PASS criteria
        if cv_accuracy > self.pass_cv_threshold and generalization_gap < self.pass_gap_threshold:
            return "PASS", (
                f"Gate PASSED: CV accuracy {cv_accuracy:.3f} > {self.pass_cv_threshold} "
                f"AND gap {generalization_gap:.3f} < {self.pass_gap_threshold}"
            )
        
        # PARTIAL criteria
        if cv_accuracy >= self.partial_cv_threshold and generalization_gap < self.partial_gap_threshold:
            return "PARTIAL", (
                f"Gate PARTIAL: CV accuracy {cv_accuracy:.3f} >= {self.partial_cv_threshold} "
                f"AND gap {generalization_gap:.3f} < {self.partial_gap_threshold} "
                f"(marginally acceptable)"
            )
        
        # FAIL
        fail_reasons = []
        if cv_accuracy < self.partial_cv_threshold:
            fail_reasons.append(f"CV accuracy {cv_accuracy:.3f} < {self.partial_cv_threshold} (no learning)")
        if generalization_gap >= self.partial_gap_threshold:
            fail_reasons.append(f"Gap {generalization_gap:.3f} >= {self.partial_gap_threshold} (severe overfitting)")
        
        return "FAIL", f"Gate FAILED: {'; '.join(fail_reasons)}"
    
    def get_gate_message(self, result: str, cv_accuracy: float, gap: float) -> str:
        """Get detailed gate message."""
        _, message = self.evaluate(cv_accuracy, gap)
        return message
