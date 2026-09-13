"""
Multi-Method Evaluator (M-4)
Unified evaluation framework with gate validation.

Runs all 4 methods (HBC + 3 baselines), computes ECE, cost, coverage,
and validates against MUST_WORK gate criteria.

Author: Anonymous
Date: 2026-07-13
Hypothesis: h-m-integrated
"""

import numpy as np
from typing import List, Dict, Optional
import json
from dataclasses import dataclass, asdict

from src.hbc_calibrator import HierarchicalBayesianCalibrator
from src.baseline_suite import BaselineEvaluationWrapper
from src.ece_metric import ECEMetric, ComputationalCostTracker, compute_statistical_significance


@dataclass
class MethodResult:
    """Results for a single method on a single dataset."""
    method_name: str
    dataset_name: str
    ece: float
    coverage: float
    forward_passes: int
    n_samples: int
    predictions: List[int]
    confidences: List[float]
    ground_truth: List[int]


@dataclass
class GateValidationResult:
    """MUST_WORK gate validation outcome."""
    gate_type: str = "MUST_WORK"
    passed: bool = False
    criteria_results: Dict = None
    failure_reason: Optional[str] = None
    recommendations: List[str] = None


class MultiMethodEvaluator:
    """
    Unified evaluation pipeline for HBC + baselines.

    MUST_WORK criteria:
    1. ECE_HBC < 0.05 AND significantly lower than all baselines (p<0.05)
    2. Cost reduction 30-50% vs COIN-only
    3. Coverage ≥ 90%
    4. (Handled by M-5) Ablation shows sweet spot dependency
    """

    def __init__(
        self,
        hbc: HierarchicalBayesianCalibrator,
        baselines: BaselineEvaluationWrapper,
        ece_metric: Optional[ECEMetric] = None,
        cost_tracker: Optional[ComputationalCostTracker] = None
    ):
        self.hbc = hbc
        self.baselines = baselines
        self.ece_metric = ece_metric or ECEMetric(n_bins=10)
        self.cost_tracker = cost_tracker or ComputationalCostTracker()

        self.results: Dict[str, Dict[str, MethodResult]] = {}  # {dataset: {method: result}}

    def evaluate_all_methods(
        self,
        test_datasets: Dict[str, List[Dict]],  # {dataset_name: [{'question', 'correct_answer', 'is_correct_fn'}]}
        methods: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, MethodResult]]:
        """
        Run all methods on all datasets.

        Args:
            test_datasets: Dict mapping dataset name to test samples
            methods: List of method names to evaluate (default: all 4)

        Returns:
            Nested dict: {dataset_name: {method_name: MethodResult}}
        """
        if methods is None:
            methods = ['HBC', 'SelfCheckGPT-only', 'COIN-only', 'IndependentCascade']

        print("="*60)
        print("MULTI-METHOD EVALUATION")
        print("="*60)

        for dataset_name, test_data in test_datasets.items():
            print(f"\n📊 Dataset: {dataset_name} (n={len(test_data)})")
            self.results[dataset_name] = {}

            for method_name in methods:
                print(f"  Evaluating {method_name}...")
                result = self._evaluate_single_method(method_name, dataset_name, test_data)
                self.results[dataset_name][method_name] = result

                print(f"    ECE: {result.ece:.4f}, Coverage: {result.coverage:.2%}, FP: {result.forward_passes}")

        return self.results

    def _evaluate_single_method(
        self,
        method_name: str,
        dataset_name: str,
        test_data: List[Dict]
    ) -> MethodResult:
        """Evaluate a single method on a single dataset."""
        predictions = []
        confidences = []
        ground_truth = []

        # Select method
        if method_name == 'HBC':
            method = self.hbc
        else:
            baseline_methods = self.baselines.get_methods()
            method = baseline_methods.get(method_name)

        if method is None:
            raise ValueError(f"Unknown method: {method_name}")

        # Run predictions
        for sample in test_data:
            question = sample['question']
            correct_answer = sample['correct_answer']
            is_correct_fn = sample['is_correct_fn']

            # Get prediction
            result = method.predict_with_uncertainty(question, correct_answer)

            predictions.append(result.interval_membership)

            # Use consistency score as confidence proxy
            if hasattr(result, 'consistency_score') and result.consistency_score is not None:
                confidences.append(result.consistency_score)
            else:
                confidences.append(0.5)  # Default

            # Ground truth
            is_correct = is_correct_fn(result.prediction, correct_answer)
            ground_truth.append(1 if is_correct else 0)

        # Compute ECE
        ece = self.ece_metric.compute_ece(predictions, confidences, ground_truth)

        # Compute coverage
        coverage = sum(predictions) / len(predictions) if len(predictions) > 0 else 0.0

        # Track cost
        if method_name == 'HBC':
            samples_per_query = self.hbc.n_samples
        elif 'SelfCheckGPT' in method_name or 'Cascade' in method_name:
            samples_per_query = 5
        else:
            samples_per_query = 1

        self.cost_tracker.track_method(
            method_name,
            n_queries=len(test_data),
            samples_per_query=samples_per_query
        )
        forward_passes = self.cost_tracker.forward_pass_counts[method_name]

        return MethodResult(
            method_name=method_name,
            dataset_name=dataset_name,
            ece=ece,
            coverage=coverage,
            forward_passes=forward_passes,
            n_samples=len(test_data),
            predictions=predictions,
            confidences=confidences,
            ground_truth=ground_truth
        )

    def validate_gate(self) -> GateValidationResult:
        """
        Validate MUST_WORK gate criteria.

        Returns:
            GateValidationResult with pass/fail and details
        """
        print("\n" + "="*60)
        print("GATE VALIDATION (MUST_WORK)")
        print("="*60)

        criteria_results = {}
        failure_reasons = []
        passed = True

        # Criterion 1: ECE_HBC < 0.05 AND significantly lower than all baselines
        hbc_eces = []
        baseline_eces = {method: [] for method in ['SelfCheckGPT-only', 'COIN-only', 'IndependentCascade']}

        for dataset_name in self.results:
            if 'HBC' in self.results[dataset_name]:
                hbc_eces.append(self.results[dataset_name]['HBC'].ece)
            for baseline_name in baseline_eces.keys():
                if baseline_name in self.results[dataset_name]:
                    baseline_eces[baseline_name].append(self.results[dataset_name][baseline_name].ece)

        mean_hbc_ece = np.mean(hbc_eces) if hbc_eces else 1.0

        criterion_1_passed = mean_hbc_ece < 0.05
        criteria_results['ece_under_005'] = {
            'passed': criterion_1_passed,
            'value': mean_hbc_ece,
            'threshold': 0.05
        }

        if not criterion_1_passed:
            passed = False
            failure_reasons.append(f"ECE={mean_hbc_ece:.4f} >= 0.05")

        # Statistical significance
        sig_results = {}
        for baseline_name, baseline_ece_vals in baseline_eces.items():
            if len(hbc_eces) > 0 and len(baseline_ece_vals) > 0:
                sig_test = compute_statistical_significance(baseline_ece_vals, hbc_eces)
                sig_results[baseline_name] = sig_test
                if not sig_test['significant'] or sig_test['mean_difference'] <= 0:
                    passed = False
                    failure_reasons.append(f"Not significantly better than {baseline_name}")

        criteria_results['statistical_significance'] = sig_results

        # Criterion 2: Cost reduction 30-50% vs COIN
        cost_report = self.cost_tracker.get_reduction_report(baseline="COIN-only")
        if 'HBC' in cost_report:
            reduction_pct = cost_report['HBC']['reduction_pct']
            criterion_2_passed = 30 <= reduction_pct <= 50
            criteria_results['cost_reduction'] = {
                'passed': criterion_2_passed,
                'value': reduction_pct,
                'threshold': (30, 50)
            }
            if not criterion_2_passed:
                passed = False
                failure_reasons.append(f"Cost reduction {reduction_pct:.1f}% not in [30%, 50%]")
        else:
            passed = False
            failure_reasons.append("Cost tracking incomplete")

        # Criterion 3: Coverage ≥ 90%
        hbc_coverages = []
        for dataset_name in self.results:
            if 'HBC' in self.results[dataset_name]:
                hbc_coverages.append(self.results[dataset_name]['HBC'].coverage)

        mean_coverage = np.mean(hbc_coverages) if hbc_coverages else 0.0
        criterion_3_passed = mean_coverage >= 0.90

        criteria_results['coverage_above_90'] = {
            'passed': criterion_3_passed,
            'value': mean_coverage,
            'threshold': 0.90
        }

        if not criterion_3_passed:
            passed = False
            failure_reasons.append(f"Coverage {mean_coverage:.2%} < 90%")

        # Generate recommendations
        recommendations = []
        if not passed:
            recommendations.append("MUST_WORK gate FAILED - hypothesis cannot proceed")
            if mean_hbc_ece >= 0.05:
                recommendations.append("Refine calibration mechanism (ECE too high)")
            if mean_coverage < 0.90:
                recommendations.append("Adjust coverage target or nonconformity scoring")

        print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")
        print(f"  ECE: {mean_hbc_ece:.4f} (threshold: 0.05)")
        print(f"  Coverage: {mean_coverage:.2%} (threshold: 90%)")
        if 'HBC' in cost_report:
            print(f"  Cost reduction: {cost_report['HBC']['reduction_pct']:.1f}% (target: 30-50%)")

        return GateValidationResult(
            gate_type="MUST_WORK",
            passed=passed,
            criteria_results=criteria_results,
            failure_reason="; ".join(failure_reasons) if failure_reasons else None,
            recommendations=recommendations if recommendations else None
        )

    def save_results(self, output_path: str):
        """Save evaluation results to JSON."""
        output = {
            'results': {
                dataset: {method: asdict(result) for method, result in methods.items()}
                for dataset, methods in self.results.items()
            },
            'cost_summary': self.cost_tracker.get_summary(),
            'cost_reductions': self.cost_tracker.get_reduction_report(baseline="COIN-only")
        }

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n✓ Results saved to {output_path}")
