"""Gate evaluation logic."""
from typing import Dict, Literal

GateStatus = Literal["PASS", "FAIL"]


class GateEvaluator:
    """Evaluate MUST_WORK gate condition."""

    def __init__(self, ner_threshold: float = 0.90, coverage_threshold: float = 0.90):
        self.ner_threshold = ner_threshold
        self.coverage_threshold = coverage_threshold

    def evaluate(self, ner_f1: float, wiki_coverage: float) -> Dict:
        """
        Evaluate MUST_WORK gate condition.

        Args:
            ner_f1: NER F1 score (0.0-1.0)
            wiki_coverage: Wikipedia coverage (0.0-1.0)

        Returns:
            {
                "status": "PASS" | "FAIL",
                "ner_pass": bool,
                "coverage_pass": bool,
                "message": str
            }
        """
        ner_pass = ner_f1 >= self.ner_threshold
        coverage_pass = wiki_coverage >= self.coverage_threshold
        gate_pass = ner_pass and coverage_pass

        status: GateStatus = "PASS" if gate_pass else "FAIL"

        ner_symbol = "✓" if ner_pass else "✗"
        coverage_symbol = "✓" if coverage_pass else "✗"

        message = (
            f"NER F1: {ner_f1:.3f} ({ner_symbol} threshold={self.ner_threshold}), "
            f"Wikipedia Coverage: {wiki_coverage:.3f} ({coverage_symbol} threshold={self.coverage_threshold})"
        )

        return {
            "status": status,
            "ner_pass": ner_pass,
            "coverage_pass": coverage_pass,
            "ner_f1": ner_f1,
            "wiki_coverage": wiki_coverage,
            "message": message
        }


if __name__ == "__main__":
    evaluator = GateEvaluator()

    # Test case: PASS
    result = evaluator.evaluate(0.92, 0.95)
    print(result["message"])
    print(f"Status: {result['status']}")

    # Test case: FAIL
    result = evaluator.evaluate(0.85, 0.88)
    print(result["message"])
    print(f"Status: {result['status']}")
