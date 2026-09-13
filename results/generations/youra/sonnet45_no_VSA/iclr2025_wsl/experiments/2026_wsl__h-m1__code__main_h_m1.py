#!/usr/bin/env python3
"""
H-M1 Main Runner
Normalization Layer Fingerprinting - Mechanism Validation

Validates hypothesis: CNNs show predominantly BatchNorm (>80%),
Transformers show predominantly LayerNorm (>80%), and Hybrids show mixed patterns.
"""
import os
import sys
import json
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from violation_analyzer import ViolationRateAnalyzer
from distribution_analyzer import NormalizationDistributionAnalyzer
from edge_case_detector import EdgeCaseDetector
from feature_importance_extractor import FeatureImportanceExtractor


class H_M1_Runner:
    """
    Orchestrates H-M1 mechanism validation pipeline.
    """

    def __init__(self, base_dir: str = None):
        """
        Args:
            base_dir: Base directory for h-m1 code (default: current script directory)
        """
        if base_dir is None:
            base_dir = Path(__file__).parent
        else:
            base_dir = Path(base_dir)

        self.base_dir = base_dir
        self.data_dir = base_dir / 'data'
        self.models_dir = base_dir / 'models'
        self.outputs_dir = base_dir / 'outputs'

        # Create outputs directory
        self.outputs_dir.mkdir(exist_ok=True)

    def load_features(self) -> tuple:
        """Load train and validation features from h-e1."""
        train_path = self.data_dir / 'train_features.csv'
        val_path = self.data_dir / 'val_features.csv'

        print(f"Loading features from h-e1...")
        print(f"  Train: {train_path}")
        print(f"  Val: {val_path}")

        train_df = pd.read_csv(train_path)
        val_df = pd.read_csv(val_path)

        print(f"  ✓ Loaded {len(train_df)} train samples, {len(val_df)} val samples")

        return train_df, val_df

    def run_mechanism_validation(self) -> dict:
        """
        Run full H-M1 mechanism validation pipeline.

        Returns:
            {
                'violation_results': {...},
                'distribution_results': {...},
                'edge_case_results': {...},
                'importance_results': {...},
                'gate_decision': 'PASS' | 'FAIL'
            }
        """
        print("=" * 70)
        print("H-M1 MECHANISM VALIDATION")
        print("=" * 70)
        print()

        # Step 1: Load h-e1 features
        train_df, val_df = self.load_features()

        # Use validation set for analysis (as per hypothesis plan)
        features_df = val_df

        # Step 2: Violation Rate Analysis
        print("\n[1] Violation Rate Analysis...")
        print("-" * 70)
        violation_analyzer = ViolationRateAnalyzer(threshold=0.15)
        violation_results = violation_analyzer.compute_violation_rates(features_df)

        print(f"  CNN Violation Rate: {violation_results['cnn_violation_rate']:.2%}")
        print(f"    Violators: {violation_results['cnn_violations']}")
        print(f"    Status: {'✓ PASS' if violation_results['cnn_passed'] else '✗ FAIL'} (threshold: 15%)")
        print()
        print(f"  Transformer Violation Rate: {violation_results['transformer_violation_rate']:.2%}")
        print(f"    Violators: {violation_results['transformer_violations']}")
        print(f"    Status: {'✓ PASS' if violation_results['transformer_passed'] else '✗ FAIL'} (threshold: 15%)")
        print()
        print(f"  Gate Decision: {violation_results['gate_decision']}")

        # Save violation report
        violation_output = self.outputs_dir / 'h-m1_violation_rates.csv'
        violation_analyzer.save_violation_report(violation_results, str(violation_output))
        print(f"  ✓ Saved to: {violation_output}")

        # Step 3: Normalization Distribution Analysis
        print("\n[2] Normalization Distribution Analysis...")
        print("-" * 70)
        distribution_analyzer = NormalizationDistributionAnalyzer()
        distribution_results = distribution_analyzer.compute_distributions(features_df)

        for family, stats in distribution_results.items():
            print(f"  {family}:")
            print(f"    BatchNorm: mean={stats['bn_count']['mean']:.1f}, median={stats['bn_count']['median']:.1f}")
            print(f"    LayerNorm: mean={stats['ln_count']['mean']:.1f}, median={stats['ln_count']['median']:.1f}")
            print(f"    Dominant: {stats['dominant_norm']}")

        # Save distribution results
        distribution_output = self.outputs_dir / 'h-m1_norm_distributions.json'
        distribution_analyzer.save_distributions(distribution_results, str(distribution_output))
        print(f"  ✓ Saved to: {distribution_output}")

        # Step 4: Edge Case Detection
        print("\n[3] Edge Case Detection...")
        print("-" * 70)
        edge_case_detector = EdgeCaseDetector()
        edge_case_results = edge_case_detector.detect_edge_cases(features_df)

        print(f"  NormFree: {len(edge_case_results['NormFree'])} models")
        for model in edge_case_results['NormFree']:
            print(f"    - {model['model']} ({model['family']})")

        print(f"  MetaFormer: {len(edge_case_results['MetaFormer'])} models")
        for model in edge_case_results['MetaFormer']:
            print(f"    - {model['model']} ({model['family']})")

        print(f"  ConvNeXt: {len(edge_case_results['ConvNeXt'])} models")
        for model in edge_case_results['ConvNeXt']:
            print(f"    - {model['model']} ({model['family']})")

        print(f"  Total Edge Cases: {edge_case_results['total_edge_cases']} ({edge_case_results['edge_case_rate']:.1%})")

        # Save edge case results
        edge_case_output = self.outputs_dir / 'h-m1_edge_cases.json'
        edge_case_detector.save_edge_cases(edge_case_results, str(edge_case_output))
        print(f"  ✓ Saved to: {edge_case_output}")

        # Step 5: Feature Importance Extraction
        print("\n[4] Feature Importance Extraction...")
        print("-" * 70)
        classifier_path = self.models_dir / 'classifier.pkl'
        importance_extractor = FeatureImportanceExtractor(str(classifier_path))
        importance_results = importance_extractor.extract_importance()

        print(f"  Feature Ranking:")
        for feature, coef, rank in importance_results['feature_ranking']:
            print(f"    {rank}. {feature}: {coef:.4f}")

        print()
        print(f"  S1 Criterion (bn_count & ln_count > 0.1):")
        print(f"    bn_count: {importance_results['bn_count_coef']:.4f} - {'✓ PASS' if importance_results['bn_passed'] else '✗ FAIL'}")
        print(f"    ln_count: {importance_results['ln_count_coef']:.4f} - {'✓ PASS' if importance_results['ln_passed'] else '✗ FAIL'}")
        print(f"    S1 Status: {'✓ PASS' if importance_results['s1_criterion_passed'] else '✗ FAIL'}")

        # Save feature importance
        importance_output = self.outputs_dir / 'h-m1_feature_importance.csv'
        importance_extractor.save_importance(importance_results, str(importance_output))
        print(f"  ✓ Saved to: {importance_output}")

        # Step 6: Overall Gate Decision
        print("\n" + "=" * 70)
        print("GATE DECISION")
        print("=" * 70)
        gate_decision = violation_results['gate_decision']
        print(f"  Primary Criteria (MUST_WORK gate):")
        print(f"    P1 (CNN violation ≤15%): {'✓ PASS' if violation_results['cnn_passed'] else '✗ FAIL'}")
        print(f"    P2 (Transformer violation ≤15%): {'✓ PASS' if violation_results['transformer_passed'] else '✗ FAIL'}")
        print(f"  Secondary Criteria:")
        print(f"    S1 (Feature importance): {'✓ PASS' if importance_results['s1_criterion_passed'] else '✗ FAIL'}")
        print()
        print(f"  FINAL GATE DECISION: {gate_decision}")
        print("=" * 70)

        # Compile results
        results = {
            'violation_results': violation_results,
            'distribution_results': distribution_results,
            'edge_case_results': edge_case_results,
            'importance_results': importance_results,
            'gate_decision': gate_decision
        }

        # Save experiment results
        results_output = self.outputs_dir / 'experiment_results.json'
        with open(results_output, 'w') as f:
            # Convert numpy types to Python types for JSON serialization
            serializable_results = self._make_serializable(results)
            json.dump(serializable_results, f, indent=2)
        print(f"\n✓ Experiment results saved to: {results_output}")

        return results

    def _make_serializable(self, obj):
        """Convert numpy types to Python types for JSON serialization."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='H-M1 Mechanism Validation')
    parser.add_argument(
        '--base-dir',
        type=str,
        default=None,
        help='Base directory for h-m1 code (default: current directory)'
    )

    args = parser.parse_args()

    runner = H_M1_Runner(base_dir=args.base_dir)
    results = runner.run_mechanism_validation()

    # Exit with code based on gate decision
    exit_code = 0 if results['gate_decision'] == 'PASS' else 1
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
