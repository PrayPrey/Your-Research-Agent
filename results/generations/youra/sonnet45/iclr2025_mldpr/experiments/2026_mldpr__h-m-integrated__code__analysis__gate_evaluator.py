"""
Gate Evaluator for h-m-integrated
Gate criteria evaluation and failure action determination
"""

import numpy as np
from typing import Dict


class GateEvaluator:
    """Gate criteria evaluation logic."""

    def __init__(self, config):
        """
        Initialize gate evaluator.

        Args:
            config: ExperimentConfig instance
        """
        self.config = config
        self.gate_config = config.gate

    def evaluate_primary_criteria(
        self,
        nmi_scores: Dict[str, float],
        baseline_gap: float
    ) -> Dict[str, bool]:
        """
        Evaluate primary gate criteria.

        Args:
            nmi_scores: NMI scores for all methods
            baseline_gap: Semantic - max(baselines) gap

        Returns:
            Dict[str, bool]: Primary criteria results
        """
        semantic_nmi = nmi_scores.get('semantic', 0.0)

        primary = {
            'nmi_threshold_met': semantic_nmi > self.gate_config.nmi_threshold,
            'baseline_gap_met': baseline_gap >= self.gate_config.baseline_gap_threshold
        }

        print("\nPrimary Criteria Evaluation:")
        print(f"  NMI > {self.gate_config.nmi_threshold}: {primary['nmi_threshold_met']} "
              f"(actual: {semantic_nmi:.4f})")
        print(f"  Gap >= {self.gate_config.baseline_gap_threshold}: {primary['baseline_gap_met']} "
              f"(actual: {baseline_gap:.4f})")

        return primary

    def evaluate_secondary_criteria(
        self,
        control_results: Dict[str, float],
        probe_variance: float
    ) -> Dict[str, bool]:
        """
        Evaluate secondary gate criteria.

        Args:
            control_results: Control experiment NMI scores
            probe_variance: Variance of repository-specific probe accuracies

        Returns:
            Dict[str, bool]: Secondary criteria results
        """
        # Check if normalized NMI persists
        normalized_nmi = control_results.get('length_normalized', 0.0)
        filtered_nmi = control_results.get('modality_filtered', 0.0)

        secondary = {
            'normalized_nmi_met': normalized_nmi >= self.gate_config.normalized_nmi_threshold,
            'probe_variance_met': probe_variance < self.gate_config.probe_variance_threshold
        }

        print("\nSecondary Criteria Evaluation:")
        print(f"  Normalized NMI >= {self.gate_config.normalized_nmi_threshold}: "
              f"{secondary['normalized_nmi_met']} (actual: {normalized_nmi:.4f})")
        print(f"  Probe variance < {self.gate_config.probe_variance_threshold}: "
              f"{secondary['probe_variance_met']} (actual: {probe_variance:.4f})")

        return secondary

    def determine_gate_status(
        self,
        primary: Dict[str, bool],
        secondary: Dict[str, bool],
        nmi_scores: Dict[str, float],
        baseline_gap: float
    ) -> str:
        """
        Determine overall gate status.

        Args:
            primary: Primary criteria results
            secondary: Secondary criteria results
            nmi_scores: NMI scores
            baseline_gap: Baseline gap

        Returns:
            str: "PASS", "PARTIAL", or "FAIL"
        """
        semantic_nmi = nmi_scores.get('semantic', 0.0)

        # PASS: Both primary criteria met
        if primary['nmi_threshold_met'] and primary['baseline_gap_met']:
            status = "PASS"
        # PARTIAL: Signal exists but weak
        elif (0.5 <= semantic_nmi < self.gate_config.nmi_threshold) or \
             (0.10 <= baseline_gap < self.gate_config.baseline_gap_threshold):
            status = "PARTIAL"
        # FAIL: No mechanism effect
        else:
            status = "FAIL"

        print(f"\nGate Status: {status}")
        return status

    def generate_failure_action(
        self,
        gate_status: str,
        nmi_scores: Dict[str, float],
        control_results: Dict[str, float],
        probe_variance: float
    ) -> str:
        """
        Generate failure action based on gate status and results.

        Args:
            gate_status: Gate status (PASS/PARTIAL/FAIL)
            nmi_scores: NMI scores
            control_results: Control experiment results
            probe_variance: Probe variance

        Returns:
            str: Failure action recommendation
        """
        if gate_status == "PASS":
            return "NONE - All criteria met"

        semantic_nmi = nmi_scores.get('semantic', 0.0)
        normalized_nmi = control_results.get('length_normalized', 0.0)

        # Determine specific failure mode
        if semantic_nmi < 0.5:
            action = "EXPLORE - Embeddings insufficient, test alternative representations"
        elif normalized_nmi < 0.5 and semantic_nmi >= 0.5:
            action = "PIVOT - Amplification is stylistic not semantic"
        elif probe_variance > 0.15:
            action = "SCOPE - Lifecycle is repository-specific, not generalizable"
        else:
            action = "REFINE - Signal exists but weak, consider ensemble methods"

        print(f"Failure Action: {action}")
        return action
