"""
Evaluation module for correction routing experiment.
"""

from typing import List, Dict

class Evaluator:
    """Evaluate correction success rates and check gate conditions."""

    def __init__(self, gate_threshold_pp: float = 20.0, gate_threshold_rel: float = 50.0):
        self.gate_threshold_pp = gate_threshold_pp
        self.gate_threshold_rel = gate_threshold_rel

    def evaluate_correction(self, corrected: str, gold: str) -> float:
        """
        Evaluate single correction.

        In mock mode, uses sentinel values:
        - "MOCK_CORRECTED_SUCCESS" → 1.0
        - "MOCK_CORRECTED_FAILURE" → 0.0

        In real mode, would use exact match + GPT-judge.
        """
        if corrected == "MOCK_CORRECTED_SUCCESS":
            return 1.0
        elif corrected == "MOCK_CORRECTED_FAILURE":
            return 0.0
        else:
            # Real evaluation: exact match or GPT-judge
            if corrected.strip().lower() == gold.strip().lower():
                return 1.0
            # Would call GPT-judge here
            return 0.0

    def compute_success_rate(self, results: List[Dict]) -> float:
        """
        Compute success rate from correction results.

        Returns:
            success_rate: float (0.0 - 1.0)
        """
        if not results:
            return 0.0

        successes = sum(self.evaluate_correction(r["corrected"], r["gold_answer"]) for r in results)
        return successes / len(results)

    def check_gate(self, matched_rate: float, mismatched_rate: float, model_name: str) -> Dict:
        """
        MUST_WORK gate evaluation.

        Pass condition:
        - (matched - mismatched) ≥ 20 percentage points
        - OR relative improvement ≥ 50%

        Returns:
            {
                "model": str,
                "matched_rate": float,
                "mismatched_rate": float,
                "difference": float,
                "relative_improvement": float,
                "gate_pass": bool
            }
        """
        difference = matched_rate - mismatched_rate
        relative_improvement = ((matched_rate - mismatched_rate) / mismatched_rate * 100) if mismatched_rate > 0 else 0.0

        # Gate pass: ≥20pp OR ≥50% relative
        gate_pass = (difference >= self.gate_threshold_pp / 100) or (relative_improvement >= self.gate_threshold_rel)

        return {
            "model": model_name,
            "matched_rate": matched_rate,
            "mismatched_rate": mismatched_rate,
            "difference": difference,
            "relative_improvement": relative_improvement,
            "gate_pass": gate_pass
        }
