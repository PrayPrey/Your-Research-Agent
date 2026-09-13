"""Mechanism Validator for h-m1."""

from typing import Dict, Any, Tuple
import numpy as np

from .analyzer import LowRankAnalyzer
from .stability import ContextStabilityTester
from .metrics import MetricsComputer


class MechanismValidator:
    """Validates mechanism hypothesis: low-rank compression with decreasing entropy."""

    def __init__(self, analyzer: LowRankAnalyzer, stability_tester: ContextStabilityTester):
        """
        Initialize validator.

        Args:
            analyzer: LowRankAnalyzer instance
            stability_tester: ContextStabilityTester instance
        """
        self.analyzer = analyzer
        self.stability_tester = stability_tester

    def verify_mechanism_activated(self, results: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify that analysis actually ran (sanity check).

        Args:
            results: Output from analyzer.analyze_layers()

        Returns:
            Tuple of (is_activated, activation_details)
        """
        # Check that we have results for all expected layers
        expected_layers = list(self.analyzer.target_layers)
        actual_layers = list(results.keys())

        all_layers_present = all(layer in actual_layers for layer in expected_layers)

        # Check that each layer has required metrics
        has_rank = all('effective_rank' in results[layer] for layer in actual_layers)
        has_entropy = all('operator_entropy' in results[layer] for layer in actual_layers)

        is_activated = all_layers_present and has_rank and has_entropy

        activation_details = {
            'all_layers_present': all_layers_present,
            'has_rank': has_rank,
            'has_entropy': has_entropy,
            'expected_layers': expected_layers,
            'actual_layers': actual_layers,
            'missing_layers': [l for l in expected_layers if l not in actual_layers]
        }

        return is_activated, activation_details

    def verify_compression_mechanism(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify compression mechanism: early vs deep layer ranks.

        Args:
            results: Output from analyzer.analyze_layers()

        Returns:
            Dictionary with compression validation results
        """
        # Get layer indices and ranks
        layer_indices = sorted(results.keys())
        ranks = [results[layer]['effective_rank'] for layer in layer_indices]

        # Split into early (L<20) and deep (L≥20) layers
        early_layers = [i for i in layer_indices if i < 20]
        deep_layers = [i for i in layer_indices if i >= 20]

        early_ranks = [results[i]['effective_rank'] for i in early_layers] if early_layers else []
        deep_ranks = [results[i]['effective_rank'] for i in deep_layers] if deep_layers else []

        # Compute averages
        avg_early_rank = np.mean(early_ranks) if early_ranks else 0.0
        avg_deep_rank = np.mean(deep_ranks) if deep_ranks else 0.0

        # Check if deep layers have lower rank (compression)
        compression_detected = avg_deep_rank < avg_early_rank if early_ranks else True

        return {
            'compression_detected': compression_detected,
            'avg_early_rank': avg_early_rank,
            'avg_deep_rank': avg_deep_rank,
            'early_layer_count': len(early_ranks),
            'deep_layer_count': len(deep_ranks),
            'rank_reduction': avg_early_rank - avg_deep_rank
        }

    def validate_gate_criteria(
        self,
        results: Dict[str, Any],
        stability_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate MUST_WORK gate criteria.

        Criteria:
        1. All deep layers (L≥20) have r_eff < 256
        2. Entropy slope β < 0 with p < 0.01
        3. Entropy stable across context lengths (variance ≤ 1.2× baseline)

        Args:
            results: Base analysis results
            stability_results: Stability test results

        Returns:
            Dictionary with gate validation results
        """
        # Criterion 1: r_eff < 256 for all deep layers
        deep_layers = [layer_idx for layer_idx in results.keys() if layer_idx >= 20]
        ranks = [results[layer]['effective_rank'] for layer in deep_layers]
        max_rank = max(ranks) if ranks else 0.0
        criterion_1_pass = all(r < 256 for r in ranks)

        # Criterion 2: Entropy slope β < 0, p < 0.01
        layer_indices = sorted(results.keys())
        entropies = [results[layer]['operator_entropy'] for layer in layer_indices]

        regression_results = MetricsComputer.entropy_regression(layer_indices, entropies)
        slope = regression_results['slope']
        p_value = regression_results['p_value']

        criterion_2_pass = (slope < 0) and (p_value < 0.01)

        # Criterion 3: Stability (variance ≤ 1.2× baseline)
        variance_metrics = self.stability_tester.compute_variance_metrics(stability_results)
        baseline_variance = 0.01  # Placeholder baseline variance
        stability_valid, stability_details = self.stability_tester.validate_stability(
            variance_metrics, baseline_variance, threshold=1.2
        )
        criterion_3_pass = stability_valid

        # Overall gate result
        gate_pass = criterion_1_pass and criterion_2_pass and criterion_3_pass

        return {
            'gate_result': 'PASS' if gate_pass else 'FAIL',
            'criterion_1': {
                'description': 'All deep layers (L≥20) have r_eff < 256',
                'pass': criterion_1_pass,
                'max_rank': max_rank,
                'deep_layer_count': len(deep_layers)
            },
            'criterion_2': {
                'description': 'Entropy slope β < 0 with p < 0.01',
                'pass': criterion_2_pass,
                'slope': slope,
                'p_value': p_value
            },
            'criterion_3': {
                'description': 'Entropy stable across context lengths (variance ≤ 1.2× baseline)',
                'pass': criterion_3_pass,
                **stability_details
            }
        }

    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """
        Generate human-readable validation report.

        Args:
            validation_results: Output from validate_gate_criteria()

        Returns:
            Formatted validation report string
        """
        gate_result = validation_results['gate_result']
        c1 = validation_results['criterion_1']
        c2 = validation_results['criterion_2']
        c3 = validation_results['criterion_3']

        report = []
        report.append("=" * 80)
        report.append("MECHANISM VALIDATION REPORT (h-m1)")
        report.append("=" * 80)
        report.append(f"\nGate Result: {gate_result}\n")

        report.append("Criterion 1: Low-Rank Structure (r_eff < 256)")
        report.append(f"  Status: {'✓ PASS' if c1['pass'] else '✗ FAIL'}")
        report.append(f"  Max rank in deep layers: {c1['max_rank']:.2f}")
        report.append(f"  Deep layer count: {c1['deep_layer_count']}")
        report.append("")

        report.append("Criterion 2: Decreasing Operator Entropy (β < 0, p < 0.01)")
        report.append(f"  Status: {'✓ PASS' if c2['pass'] else '✗ FAIL'}")
        report.append(f"  Slope (β): {c2['slope']:.6f}")
        report.append(f"  P-value: {c2['p_value']:.6f}")
        report.append("")

        report.append("Criterion 3: Context Stability (variance ≤ 1.2× baseline)")
        report.append(f"  Status: {'✓ PASS' if c3['pass'] else '✗ FAIL'}")
        report.append(f"  Max rank variance: {c3['max_rank_variance']:.6f}")
        report.append(f"  Max entropy variance: {c3['max_entropy_variance']:.6f}")
        report.append(f"  Threshold: {c3['threshold_value']:.6f}")
        report.append("")

        report.append("=" * 80)

        return "\n".join(report)
