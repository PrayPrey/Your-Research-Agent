"""
Phase 2 Metrics Module
Computes gate validation metrics for h-m2
"""

from typing import Dict, List, Tuple
import numpy as np


class Phase2Metrics:
    """
    Compute Phase 2 gate validation metrics.

    Gate Criteria (SHOULD_WORK):
    1. AI weight is highest in Phase 2
    2. Quality improvement rate > 0
    3. Correctness maintained (≥95%)
    """

    def __init__(self, config: dict = None):
        """
        Initialize Phase 2 metrics computer.

        Args:
            config: Configuration dict (optional)
        """
        self.config = config or {}
        self.phase2_range = (0.30, 0.70)

    def compute_ai_weight_dominance(
        self,
        weight_trajectory: List[Dict]
    ) -> Tuple[bool, Dict]:
        """
        Gate 1: Check if AI weight is highest in Phase 2.

        Args:
            weight_trajectory: List of checkpoint data with weights

        Returns:
            Tuple of (passed, metrics_dict)
        """
        # Find AI weight peak
        max_ai_weight = 0.0
        peak_checkpoint = None

        for checkpoint in weight_trajectory:
            progress = checkpoint.get('progress', 0)
            weights = checkpoint.get('weights', {})

            # Only consider Phase 2 range
            if self.phase2_range[0] <= progress <= self.phase2_range[1]:
                ai_weight = weights.get('ai', 0)
                if ai_weight > max_ai_weight:
                    max_ai_weight = ai_weight
                    peak_checkpoint = checkpoint

        if not peak_checkpoint:
            return False, {'error': 'No Phase 2 checkpoints found'}

        # Check if AI is dominant at peak
        peak_weights = peak_checkpoint['weights']
        ai_dominant = (
            peak_weights['ai'] > peak_weights['execution'] and
            peak_weights['ai'] > peak_weights['human']
        )

        # Count violations (checkpoints where AI is not highest)
        violations = 0
        for checkpoint in weight_trajectory:
            progress = checkpoint.get('progress', 0)
            if self.phase2_range[0] <= progress <= self.phase2_range[1]:
                w = checkpoint['weights']
                if not (w['ai'] > w['execution'] and w['ai'] > w['human']):
                    violations += 1

        metrics = {
            'ai_weight_peak': max_ai_weight,
            'peak_progress': peak_checkpoint['progress'],
            'ai_dominant_at_peak': ai_dominant,
            'dominance_violations': violations,
            'passed': ai_dominant and violations == 0
        }

        return metrics['passed'], metrics

    def compute_quality_improvement(
        self,
        checkpoints: Dict
    ) -> Tuple[bool, Dict]:
        """
        Gate 2: Check if quality scores improve from 30% → 70%.

        Args:
            checkpoints: Dict of checkpoint data keyed by progress

        Returns:
            Tuple of (passed, metrics_dict)
        """
        # Get quality scores at 30% and 70%
        checkpoint_30 = checkpoints.get('0.30', {})
        checkpoint_70 = checkpoints.get('0.70', {})

        if not checkpoint_30 or not checkpoint_70:
            return False, {'error': 'Missing 30% or 70% checkpoint'}

        quality_30 = checkpoint_30.get('metrics', {}).get('quality', 0)
        quality_70 = checkpoint_70.get('metrics', {}).get('quality', 0)

        # Compute improvement rate
        improvement = quality_70 - quality_30
        improvement_rate = improvement / 0.40  # Over 40% progress range

        passed = improvement_rate > 0

        metrics = {
            'quality_30': quality_30,
            'quality_70': quality_70,
            'improvement': improvement,
            'improvement_rate': improvement_rate,
            'passed': passed
        }

        return passed, metrics

    def compute_correctness_maintenance(
        self,
        checkpoints: Dict
    ) -> Tuple[bool, Dict]:
        """
        Gate 3: Check if correctness is maintained (≥95% of initial).

        Args:
            checkpoints: Dict of checkpoint data keyed by progress

        Returns:
            Tuple of (passed, metrics_dict)
        """
        # Get pass@1 scores at 30% and 70%
        checkpoint_30 = checkpoints.get('0.30', {})
        checkpoint_70 = checkpoints.get('0.70', {})

        if not checkpoint_30 or not checkpoint_70:
            return False, {'error': 'Missing 30% or 70% checkpoint'}

        pass1_30 = checkpoint_30.get('metrics', {}).get('pass@1', 0)
        pass1_70 = checkpoint_70.get('metrics', {}).get('pass@1', 0)

        # Compute maintenance ratio
        if pass1_30 == 0:
            return False, {'error': 'Zero pass@1 at 30%'}

        maintenance_ratio = pass1_70 / pass1_30
        passed = maintenance_ratio >= 0.95  # Max 5% regression allowed

        metrics = {
            'pass1_30': pass1_30,
            'pass1_70': pass1_70,
            'maintenance_ratio': maintenance_ratio,
            'regression': 1.0 - maintenance_ratio,
            'passed': passed
        }

        return passed, metrics

    def compute_all_gates(
        self,
        results: Dict
    ) -> Dict:
        """
        Compute all gate metrics.

        Args:
            results: Training results with checkpoints and trajectories

        Returns:
            Dict with all gate results
        """
        checkpoints = results.get('checkpoints', {})
        weight_trajectory = results.get('weight_trajectory', [])

        # Gate 1: AI Weight Dominance
        gate1_passed, gate1_metrics = self.compute_ai_weight_dominance(weight_trajectory)

        # Gate 2: Quality Improvement
        gate2_passed, gate2_metrics = self.compute_quality_improvement(checkpoints)

        # Gate 3: Correctness Maintenance
        gate3_passed, gate3_metrics = self.compute_correctness_maintenance(checkpoints)

        # Overall gate result
        all_passed = gate1_passed and gate2_passed and gate3_passed

        gate_results = {
            'gate_type': 'SHOULD_WORK',
            'gate_result': 'PASS' if all_passed else 'FAIL',
            'gates': {
                'gate1_ai_dominance': {
                    'passed': gate1_passed,
                    'metrics': gate1_metrics
                },
                'gate2_quality_improvement': {
                    'passed': gate2_passed,
                    'metrics': gate2_metrics
                },
                'gate3_correctness_maintenance': {
                    'passed': gate3_passed,
                    'metrics': gate3_metrics
                }
            },
            'summary': {
                'total_gates': 3,
                'passed_gates': sum([gate1_passed, gate2_passed, gate3_passed]),
                'all_passed': all_passed
            }
        }

        return gate_results
