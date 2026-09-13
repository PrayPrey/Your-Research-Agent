"""MUST_WORK gate evaluation logic"""

import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class GateEvaluator:
    """Evaluate MUST_WORK gate decision"""

    def __init__(self, thresholds: Dict):
        self.thresholds = thresholds

    def evaluate_gate(self,
                     timing_results: Dict,
                     gpu_results: Dict,
                     validation_results: Dict,
                     speedup_results: Dict = None) -> Dict:
        """
        Evaluate MUST_WORK gate decision.

        Args:
            timing_results: From TimingBenchmark (checkpoint-only)
            gpu_results: From GPUMonitor
            validation_results: From FeatureValidator
            speedup_results: From TimingBenchmark.compare_methods (optional)

        Returns:
            {
                'gate_decision': str,  # 'PASS' or 'FAIL'
                'p1_passed': bool,  # total_time < 600
                'p2_passed': bool,  # gpu_memory == 0
                's1_passed': bool,  # feature_equivalence == 1.0
                's2_passed': bool,  # speedup > 3.0
                'failure_reasons': list[str],
                'recommendation': str
            }
        """
        # Primary criteria
        p1_passed = timing_results['total_time'] < self.thresholds['P1_total_time_max_seconds']
        p2_passed = gpu_results['max_gpu_memory_mb'] == 0

        # Secondary criteria
        s1_passed = validation_results['overall_match']
        s2_passed = False
        if speedup_results:
            s2_passed = speedup_results['speedup_factor'] > self.thresholds['S2_speedup_min_factor']

        # Gate decision logic
        gate_passed = p1_passed and p2_passed

        failure_reasons = []
        if not p1_passed:
            failure_reasons.append(
                f"P1 FAIL: Extraction time {timing_results['total_time']:.1f}s exceeds threshold {self.thresholds['P1_total_time_max_seconds']}s"
            )
        if not p2_passed:
            failure_reasons.append(
                f"P2 FAIL: GPU memory {gpu_results['max_gpu_memory_mb']:.1f}MB > 0MB (not CPU-only)"
            )
        if not s1_passed:
            failure_reasons.append(
                f"S1 FAIL: Feature equivalence {validation_results['cosine_similarity']:.4f} < 1.0 (mismatch rate: {validation_results['mismatch_rate']:.2%})"
            )
        if speedup_results and not s2_passed:
            failure_reasons.append(
                f"S2 FAIL: Speedup {speedup_results['speedup_factor']:.2f}x < {self.thresholds['S2_speedup_min_factor']}x"
            )

        # Recommendation
        if gate_passed:
            gate_decision = 'PASS'
            recommendation = 'Proceed to H-C1 (Edge Case Robustness)'
        else:
            gate_decision = 'FAIL'
            if not p1_passed:
                recommendation = 'EXPLORE parallel extraction OR PIVOT to relaxed threshold (15 min)'
            elif not p2_passed:
                recommendation = 'ABANDON (method not CPU-only, requires GPU infrastructure)'
            else:
                recommendation = 'Debug and retry'

        decision = {
            'gate_decision': gate_decision,
            'p1_passed': p1_passed,
            'p2_passed': p2_passed,
            's1_passed': s1_passed,
            's2_passed': s2_passed,
            'failure_reasons': failure_reasons,
            'recommendation': recommendation
        }

        logger.info(f"Gate decision: {gate_decision} (P1={p1_passed}, P2={p2_passed}, S1={s1_passed}, S2={s2_passed})")
        if failure_reasons:
            for reason in failure_reasons:
                logger.warning(reason)

        return decision

    def save_decision(self, decision: Dict, output_path: str):
        """Save gate decision to JSON"""
        with open(output_path, 'w') as f:
            json.dump(decision, f, indent=2)
        logger.info(f"Gate decision saved to {output_path}")
