"""
Phase 3 Metrics and Gate Validation

Validates SHOULD_WORK gate criteria:
1. Human weight increases (w_human(100%) > w_human(70%))
2. Conflict case non-collapse (median ∈ [0.1, 0.4])
3. Correctness maintenance (pass@1 ratio ≥ 0.95)
"""

import json
from pathlib import Path
from typing import Dict, Tuple
import numpy as np


class Phase3Metrics:
    """
    Phase 3 gate validation metrics.

    SHOULD_WORK gate requires all 3 criteria:
    - Human weight trajectory (positive correlation)
    - Conflict case preference scores (no collapse)
    - Correctness maintenance (no regression)
    """

    def __init__(self):
        self.weight_history = []
        self.conflict_results = {}
        self.checkpoint_metrics = {}

    def load_weight_history(self, weight_history_path: str):
        """Load weight trajectory from aggregator."""
        with open(weight_history_path, 'r') as f:
            self.weight_history = json.load(f)

    def load_conflict_results(self, conflict_results_path: str):
        """Load conflict case evaluation results."""
        with open(conflict_results_path, 'r') as f:
            self.conflict_results = json.load(f)

    def validate_human_weight_increase(self) -> Tuple[bool, Dict]:
        """
        Gate Criterion 1: Human weight increases from 70% to 100%.

        Returns:
            (passed, details)
        """
        if len(self.weight_history) < 2:
            return False, {"error": "Insufficient weight history"}

        # Extract human weights
        human_weights = [w.get("human", 0) for w in self.weight_history]

        # Get weights at 70% and 100%
        w_70 = human_weights[0]
        w_100 = human_weights[-1]

        passed = w_100 > w_70

        details = {
            "w_human_70": round(w_70, 4),
            "w_human_100": round(w_100, 4),
            "increase": round(w_100 - w_70, 4),
            "trajectory": [round(w, 3) for w in human_weights],
            "passed": passed
        }

        return passed, details

    def validate_conflict_case_non_collapse(self,
                                             target_range: Tuple[float, float] = (0.1, 0.4)) -> Tuple[bool, Dict]:
        """
        Gate Criterion 2: Conflict cases resolve to intermediate preference scores.

        Target: median ∈ [0.1, 0.4] (not collapsed to [0.0, 0.1])

        Returns:
            (passed, details)
        """
        preference_scores = self.conflict_results.get("preference_scores", [])

        if len(preference_scores) == 0:
            return False, {"error": "No conflict case results"}

        median_pref = float(np.median(preference_scores))
        mean_pref = float(np.mean(preference_scores))
        std_pref = float(np.std(preference_scores))

        passed = target_range[0] <= median_pref <= target_range[1]

        details = {
            "median_preference": round(median_pref, 4),
            "mean_preference": round(mean_pref, 4),
            "std_preference": round(std_pref, 4),
            "target_range": target_range,
            "collapsed": median_pref < target_range[0],
            "passed": passed,
            "n_samples": len(preference_scores)
        }

        return passed, details

    def validate_correctness_maintenance(self,
                                          min_ratio: float = 0.95) -> Tuple[bool, Dict]:
        """
        Gate Criterion 3: Correctness maintained (no regression).

        Target: pass@1(100%) / pass@1(70%) ≥ 0.95

        Returns:
            (passed, details)
        """
        pass_70 = self.checkpoint_metrics.get("pass_at_1_70", 0.0)
        pass_100 = self.checkpoint_metrics.get("pass_at_1_100", 0.0)

        if pass_70 == 0:
            return False, {"error": "No 70% checkpoint metrics"}

        ratio = pass_100 / pass_70 if pass_70 > 0 else 0.0
        passed = ratio >= min_ratio

        details = {
            "pass_at_1_70": round(pass_70, 4),
            "pass_at_1_100": round(pass_100, 4),
            "ratio": round(ratio, 4),
            "min_ratio": min_ratio,
            "passed": passed
        }

        return passed, details

    def validate_all_criteria(self) -> Dict:
        """
        Validate all 3 SHOULD_WORK gate criteria.

        Returns:
            Complete gate validation report
        """
        print("\n" + "="*70)
        print("Phase 3 Gate Validation (SHOULD_WORK)")
        print("="*70 + "\n")

        # Criterion 1: Human weight increase
        w_passed, w_details = self.validate_human_weight_increase()
        print(f"1. Human Weight Increase: {'✅ PASS' if w_passed else '❌ FAIL'}")
        print(f"   w_human(70%) = {w_details.get('w_human_70', 'N/A')}")
        print(f"   w_human(100%) = {w_details.get('w_human_100', 'N/A')}")
        print(f"   Increase: +{w_details.get('increase', 0):.4f}\n")

        # Criterion 2: Conflict case non-collapse
        c_passed, c_details = self.validate_conflict_case_non_collapse()
        print(f"2. Conflict Case Non-Collapse: {'✅ PASS' if c_passed else '❌ FAIL'}")
        print(f"   Median preference: {c_details.get('median_preference', 'N/A')}")
        print(f"   Target range: {c_details.get('target_range', 'N/A')}")
        print(f"   Collapsed: {c_details.get('collapsed', False)}\n")

        # Criterion 3: Correctness maintenance
        m_passed, m_details = self.validate_correctness_maintenance()
        print(f"3. Correctness Maintenance: {'✅ PASS' if m_passed else '❌ FAIL'}")
        print(f"   pass@1(70%) = {m_details.get('pass_at_1_70', 'N/A')}")
        print(f"   pass@1(100%) = {m_details.get('pass_at_1_100', 'N/A')}")
        print(f"   Ratio: {m_details.get('ratio', 'N/A')}\n")

        # Overall gate result
        all_passed = w_passed and c_passed and m_passed

        print("="*70)
        print(f"Gate Result: {'✅ PASS' if all_passed else '❌ FAIL'}")
        if not all_passed:
            print("(SHOULD_WORK gate - Document limitations, continue pipeline)")
        print("="*70 + "\n")

        return {
            "gate_type": "SHOULD_WORK",
            "gate_result": "PASS" if all_passed else "FAIL",
            "criteria": {
                "human_weight_increase": {"passed": w_passed, **w_details},
                "conflict_case_non_collapse": {"passed": c_passed, **c_details},
                "correctness_maintenance": {"passed": m_passed, **m_details}
            },
            "all_passed": all_passed
        }

    def save_results(self, output_path: str):
        """Save validation results to JSON."""
        results = self.validate_all_criteria()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"✓ Validation results saved: {output_path}")

        return results
