"""Evaluate gate condition (SHOULD_WORK)."""

import json
from pathlib import Path
from typing import Dict

class GateEvaluator:
    """Evaluate gate condition (SHOULD_WORK)."""

    def __init__(
        self,
        recall_target: float = 0.70,
        recall_acceptable: float = 0.60,
        fp_rate_limit: float = 0.30
    ):
        """Initialize evaluator."""
        self.recall_target = recall_target
        self.recall_acceptable = recall_acceptable
        self.fp_rate_limit = fp_rate_limit

    def compute_metrics(self, confusion_matrix: Dict) -> Dict:
        """Compute recall, FP rate, precision."""
        tp = confusion_matrix["TP"]
        fp = confusion_matrix["FP"]
        fn = confusion_matrix["FN"]
        tn = confusion_matrix["TN"]

        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        fp_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

        return {"recall": recall, "fp_rate": fp_rate, "precision": precision}

    def check_gate_condition(self, metrics: Dict) -> Dict:
        """Check SHOULD_WORK gate."""
        passed = (metrics["recall"] >= self.recall_acceptable and
                  metrics["fp_rate"] < self.fp_rate_limit)
        target_met = (metrics["recall"] >= self.recall_target and
                      metrics["fp_rate"] < self.fp_rate_limit)

        return {
            "status": "PASS" if passed else "FAIL",
            "target_met": target_met,
            "acceptable_met": passed
        }

    def generate_metrics_report(self, metrics: Dict, gate_status: Dict) -> str:
        """Generate text report."""
        report = f"""
=== GATE EVALUATION ===
Recall: {metrics['recall']:.3f} (target ≥{self.recall_target}, acceptable ≥{self.recall_acceptable})
FP Rate: {metrics['fp_rate']:.3f} (limit <{self.fp_rate_limit})
Precision: {metrics['precision']:.3f}
Gate Status: {gate_status['status']}
Target Met: {gate_status['target_met']}
"""
        return report

    def save_results(self, results: Dict, output_path: Path) -> None:
        """Save results."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
