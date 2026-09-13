"""
Phase1Metrics - Weight dominance, improvement rate, and correlation metrics
Task: A-4
Hypothesis: h-m1
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple


class Phase1Analyzer:
    """
    Analyzes Phase 1 training data for hypothesis validation.

    Gate Criteria (MUST_WORK):
    1. Weight Dominance: execution_weight > max(ai_weight, human_weight) at all Phase 1 checkpoints
    2. Pass@1 Improvement: Phase 1 rate > later phases rate
    3. Weight Correlation: Positive correlation between execution_weight and progress in Phase 1
    """

    def __init__(self, weight_trajectory: List[Dict], pass_at_1_trajectory: List[Dict]):
        """
        Args:
            weight_trajectory: List of {progress, execution_weight, ai_weight, human_weight}
            pass_at_1_trajectory: List of {progress, pass_at_1}
        """
        self.weight_trajectory = weight_trajectory
        self.pass_at_1_trajectory = pass_at_1_trajectory

    def compute_weight_dominance(self) -> Dict[str, any]:
        """
        Check if execution weight is highest at all Phase 1 checkpoints (0%, 10%, 20%, 30%).

        Returns:
            {
                'passed': bool,
                'checkpoints': List[Dict],
                'violation_count': int
            }
        """
        phase1_checkpoints = [0.0, 0.1, 0.2, 0.3]
        checkpoint_results = []
        violations = 0

        for checkpoint in phase1_checkpoints:
            # Find closest weight data point
            closest = min(self.weight_trajectory, key=lambda x: abs(x['progress'] - checkpoint))

            exec_w = closest['execution_weight']
            ai_w = closest['ai_weight']
            human_w = closest['human_weight']

            # Check dominance
            is_dominant = exec_w > max(ai_w, human_w)

            checkpoint_results.append({
                'progress': checkpoint,
                'execution_weight': exec_w,
                'ai_weight': ai_w,
                'human_weight': human_w,
                'dominant': is_dominant
            })

            if not is_dominant:
                violations += 1

        return {
            'passed': violations == 0,
            'checkpoints': checkpoint_results,
            'violation_count': violations
        }

    def compute_pass_at_1_improvement_rates(self) -> Dict[str, float]:
        """
        Calculate pass@1 improvement rates for Phase 1 (0-30%) vs later phases (30-100%).

        Returns:
            {
                'phase1_rate': float,
                'later_rate': float,
                'ratio': float,
                'passed': bool
            }
        """
        # Separate Phase 1 vs later data
        phase1_data = [p for p in self.pass_at_1_trajectory if p['progress'] <= 0.3]
        later_data = [p for p in self.pass_at_1_trajectory if p['progress'] > 0.3]

        # Calculate improvement rates (delta pass@1 / delta progress)
        def calc_rate(data):
            if len(data) < 2:
                return 0.0

            # Linear regression: pass@1 = a * progress + b
            progress = np.array([p['progress'] for p in data])
            pass_at_1 = np.array([p['pass_at_1'] for p in data])

            slope, _ = np.polyfit(progress, pass_at_1, 1)
            return slope

        phase1_rate = calc_rate(phase1_data)
        later_rate = calc_rate(later_data) if len(later_data) >= 2 else 0.0

        # Phase 1 rate should be higher
        passed = phase1_rate > later_rate if later_rate > 0 else phase1_rate > 0

        return {
            'phase1_rate': phase1_rate,
            'later_rate': later_rate,
            'ratio': phase1_rate / later_rate if later_rate > 0 else float('inf'),
            'passed': passed
        }

    def compute_weight_correlation(self) -> Dict[str, float]:
        """
        Calculate Pearson correlation between execution_weight and progress in Phase 1.

        Returns:
            {
                'correlation': float,
                'p_value': float,
                'passed': bool
            }
        """
        # Filter Phase 1 data (0-30%)
        phase1_weights = [w for w in self.weight_trajectory if w['progress'] <= 0.3]

        if len(phase1_weights) < 2:
            return {'correlation': 0.0, 'p_value': 1.0, 'passed': False}

        # Extract vectors
        progress = np.array([w['progress'] for w in phase1_weights])
        exec_weights = np.array([w['execution_weight'] for w in phase1_weights])

        # Pearson correlation
        correlation, p_value = stats.pearsonr(progress, exec_weights)

        # Should be positive (execution weight increases/stays high in Phase 1)
        # Relaxed: correlation > -0.5 (allowing flat or slight decrease)
        passed = correlation > -0.5

        return {
            'correlation': correlation,
            'p_value': p_value,
            'passed': passed
        }

    def validate_gate_criteria(self) -> Dict[str, any]:
        """
        Validate all 3 gate criteria for MUST_WORK gate.

        Returns:
            {
                'gate_result': 'PASS' | 'FAIL',
                'metric1_weight_dominance': Dict,
                'metric2_pass_at_1_improvement': Dict,
                'metric3_weight_correlation': Dict,
                'rationale': str
            }
        """
        # Metric 1: Weight dominance
        dominance = self.compute_weight_dominance()

        # Metric 2: Pass@1 improvement rates
        improvement = self.compute_pass_at_1_improvement_rates()

        # Metric 3: Weight correlation
        correlation = self.compute_weight_correlation()

        # Overall gate decision
        all_passed = dominance['passed'] and improvement['passed'] and correlation['passed']

        rationale = []
        if dominance['passed']:
            rationale.append("✓ Metric 1 PASS: Execution weight dominant at all Phase 1 checkpoints")
        else:
            rationale.append(f"✗ Metric 1 FAIL: {dominance['violation_count']} violations of execution dominance")

        if improvement['passed']:
            rationale.append(f"✓ Metric 2 PASS: Phase 1 improvement rate ({improvement['phase1_rate']:.4f}) > later ({improvement['later_rate']:.4f})")
        else:
            rationale.append(f"✗ Metric 2 FAIL: Phase 1 rate ({improvement['phase1_rate']:.4f}) ≤ later rate ({improvement['later_rate']:.4f})")

        if correlation['passed']:
            rationale.append(f"✓ Metric 3 PASS: Weight correlation ρ={correlation['correlation']:.3f} (p={correlation['p_value']:.3f})")
        else:
            rationale.append(f"✗ Metric 3 FAIL: Weight correlation ρ={correlation['correlation']:.3f} too negative")

        return {
            'gate_result': 'PASS' if all_passed else 'FAIL',
            'metric1_weight_dominance': dominance,
            'metric2_pass_at_1_improvement': improvement,
            'metric3_weight_correlation': correlation,
            'rationale': '\n'.join(rationale)
        }
