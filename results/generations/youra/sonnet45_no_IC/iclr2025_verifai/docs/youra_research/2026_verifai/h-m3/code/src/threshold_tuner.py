"""Threshold tuning for optimal recall-FP tradeoff."""

import torch
from typing import List, Dict
from .contradiction_detector import ContradictionDetector
from .ground_truth_validator import GroundTruthValidator

class ThresholdTuner:
    """Threshold tuning for optimal recall-FP tradeoff."""

    def __init__(self, thresholds: List[float] = [0.2, 0.25, 0.3, 0.35, 0.4]):
        """Initialize tuner."""
        self.thresholds = thresholds

    def tune_threshold(
        self,
        similarity_matrix: torch.Tensor,
        pairs: List[Dict],
        ground_truth: List[Dict],
        validator: GroundTruthValidator,
        total_pairs: int
    ) -> List[Dict]:
        """Test thresholds and compute metrics."""
        results = []

        for threshold in self.thresholds:
            detector = ContradictionDetector(similarity_threshold=threshold)
            contradictions = detector.detect_contradictions(similarity_matrix, pairs)

            matches = validator.match_detected_to_ground_truth(contradictions, ground_truth)
            confusion_matrix = validator.compute_confusion_matrix(matches, total_pairs)

            tp = confusion_matrix["TP"]
            fp = confusion_matrix["FP"]
            fn = confusion_matrix["FN"]
            tn = confusion_matrix["TN"]

            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            fp_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0

            results.append({
                "threshold": threshold,
                "recall": recall,
                "fp_rate": fp_rate
            })

        return results

    def find_optimal_threshold(
        self,
        tuning_results: List[Dict],
        fp_rate_limit: float = 0.30
    ) -> Dict:
        """Find threshold that maximizes recall while FP rate < limit."""
        valid_results = [r for r in tuning_results if r["fp_rate"] < fp_rate_limit]

        if not valid_results:
            return {"threshold": None, "recall": 0.0, "fp_rate": 1.0}

        optimal = max(valid_results, key=lambda r: r["recall"])
        return optimal
