"""
Gate Evaluator: Validates experiment results against gate criteria
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)


class GateEvaluator:
    """Gate validation for MUST_WORK criteria"""

    def __init__(self, config):
        """Initialize with gate configuration."""
        self.gate_type = config.gate_type
        self.kappa_threshold = config.kappa_threshold
        self.probe_threshold = config.probe_threshold
        self.min_sections_pass = config.min_sections_pass

        logger.info(f"GateEvaluator initialized: {self.gate_type}")
        logger.info(f"  Kappa threshold: {self.kappa_threshold}")
        logger.info(f"  Probe threshold: {self.probe_threshold}")
        logger.info(f"  Min sections pass: {self.min_sections_pass}")

    def evaluate(self, kappa_results: Dict, probe_accuracy: float) -> Dict:
        """
        Evaluate gate criteria.
        Args:
            kappa_results: Dict of {section: {kappa, ci_lower, ci_upper, pass}}
            probe_accuracy: Linear probe accuracy
        Returns:
            {
                'result': 'PASS' | 'PARTIAL' | 'FAIL',
                'kappa_sections_passed': int,
                'probe_passed': bool,
                'details': str
            }
        """
        logger.info("Evaluating gate criteria...")

        # Count kappa sections passing threshold
        kappa_sections_passed = sum(1 for v in kappa_results.values() if v['pass'])
        kappa_criterion_met = kappa_sections_passed >= self.min_sections_pass

        # Check probe threshold
        probe_passed = probe_accuracy >= self.probe_threshold

        # Determine overall result
        if kappa_criterion_met and probe_passed:
            result = 'PASS'
            details = f"Both criteria met: κ sections={kappa_sections_passed}/{len(kappa_results)}, probe={probe_accuracy:.3f}"
        elif kappa_criterion_met or probe_passed:
            result = 'PARTIAL'
            details = f"Partial pass: κ sections={kappa_sections_passed}/{len(kappa_results)} (need {self.min_sections_pass}), probe={probe_accuracy:.3f} (need {self.probe_threshold})"
        else:
            result = 'FAIL'
            details = f"Both criteria failed: κ sections={kappa_sections_passed}/{len(kappa_results)}, probe={probe_accuracy:.3f}"

        logger.info(f"  Gate result: {result}")
        logger.info(f"  {details}")

        return {
            'result': result,
            'kappa_sections_passed': kappa_sections_passed,
            'probe_passed': probe_passed,
            'details': details
        }
