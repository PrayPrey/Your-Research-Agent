"""Gate condition checker for hypothesis validation."""
import logging
import numpy as np
from typing import Dict, Any


logger = logging.getLogger(__name__)


class GateChecker:
    """Validates hypothesis gate conditions."""

    def __init__(self):
        """Initialize gate checker."""
        self.gate_type = "MUST_WORK"

    def check_gate(
        self,
        rho: float,
        p_value: float,
        odds_ratios: Dict[str, float]
    ) -> Dict[str, Any]:
        """Evaluate gate conditions.

        Args:
            rho: Spearman correlation coefficient
            p_value: P-value for correlation
            odds_ratios: Dictionary of odds ratios from logistic regression

        Returns:
            Dictionary with gate status and routing decision
        """
        logger.info("Evaluating gate conditions...")

        # Primary gate: Spearman correlation
        spearman_rho_met = rho >= 0.3
        spearman_p_met = p_value < 0.01
        effect_direction_met = rho > 0

        primary_pass = spearman_rho_met and spearman_p_met and effect_direction_met

        # Alternative success: Logistic regression
        doc_components = ['env_file', 'pinned_deps', 'dockerfile']
        or_values = [odds_ratios.get(k, {}).get('OR', 1.0) for k in doc_components]
        avg_or = np.mean(or_values)
        alternative_pass = avg_or >= 1.5

        # Determine status
        if primary_pass:
            status = "PASS"
            routing = "Proceed to H-M1 (Environment file mechanism)"
            next_hyp = "h-m1"
        elif alternative_pass and rho > 0:
            status = "PARTIAL"
            routing = "Analyze component-level effects, modify H-M1/M2 scope"
            next_hyp = "h-m1-modified"
        else:
            status = "FAIL"
            routing = "Route to Phase 0 (fundamental assumption violated)"
            next_hyp = None

        result = {
            'status': status,
            'criteria_met': {
                'spearman_rho': spearman_rho_met,
                'spearman_p': spearman_p_met,
                'effect_direction': effect_direction_met,
                'logistic_or': alternative_pass
            },
            'routing_decision': routing,
            'next_hypothesis': next_hyp,
            'metrics': {
                'rho': rho,
                'p_value': p_value,
                'odds_ratios': odds_ratios
            }
        }

        logger.info(f"Gate status: {status}")
        logger.info(f"Routing: {routing}")

        return result
