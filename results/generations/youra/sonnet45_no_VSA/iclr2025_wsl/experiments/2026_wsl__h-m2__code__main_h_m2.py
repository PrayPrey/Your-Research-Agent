"""
H-M2 Main Experiment Runner

Orchestrates all analyses for parameter-mass ratio hypothesis validation:
- Cohen's d effect size
- Scale invariance (CV)
- Edge case analysis
- MUST_WORK gate evaluation
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

from cohens_d_analyzer import CohensDAnalyzer
from scale_invariance_validator import ScaleInvarianceValidator
from edge_case_analyzer import EdgeCaseAnalyzer
from gate_logic import GateDecisionMaker


def load_features(data_dir: Path) -> tuple:
    """Load train and validation feature sets."""
    train_df = pd.read_csv(data_dir / 'train_features.csv')
    val_df = pd.read_csv(data_dir / 'val_features.csv')
    return train_df, val_df


def run_experiment():
    """Run full H-M2 experiment."""
    print("=" * 70)
    print("H-M2 PARAMETER-MASS RATIO EXPERIMENT")
    print("=" * 70)

    # Setup paths
    code_dir = Path(__file__).parent
    data_dir = code_dir / 'data'
    output_dir = code_dir / 'outputs'
    output_dir.mkdir(exist_ok=True)

    # Load features
    print("\n1. Loading Features...")
    train_df, val_df = load_features(data_dir)
    print(f"   Train: {len(train_df)} models")
    print(f"   Val: {len(val_df)} models")

    # Use validation set for hypothesis testing
    features_df = val_df

    # Extract R distributions by family
    print("\n2. Extracting R Distributions...")
    cnn_models = features_df[features_df['family'] == 'CNN']
    transformer_models = features_df[features_df['family'] == 'Transformer']

    cnn_R = cnn_models['param_mass_ratio'].values
    transformer_R = transformer_models['param_mass_ratio'].values

    print(f"   CNN: {len(cnn_R)} models, R mean = {np.mean(cnn_R):.3f}")
    print(f"   Transformer: {len(transformer_R)} models, R mean = {np.mean(transformer_R):.3f}")

    # 3. Cohen's d Analysis
    print("\n3. Cohen's d Analysis...")
    cohens_analyzer = CohensDAnalyzer(threshold=1.0)
    cohens_result = cohens_analyzer.analyze(cnn_R, transformer_R)

    print(f"   Cohen's d: {cohens_result['cohens_d']:.3f}")
    print(f"   p-value: {cohens_result['p_value']:.6f}")
    print(f"   Effect: {cohens_result['effect_size_interpretation']}")
    print(f"   P1 (d > 1.0): {'PASS' if cohens_result['passed'] else 'FAIL'}")

    # 4. Scale Invariance (CV) Analysis
    print("\n4. Scale Invariance (CV) Analysis...")
    cv_validator = ScaleInvarianceValidator(cv_threshold=0.15)
    cv_result = cv_validator.validate_all_families(features_df)

    cnn_cv = cv_result['cnn_cv']
    transformer_cv = cv_result['transformer_cv']

    cnn_cv_val = cnn_cv.get('cv')
    transformer_cv_val = transformer_cv.get('cv')
    cnn_cv_str = f"{cnn_cv_val:.3f}" if cnn_cv_val is not None else "N/A"
    transformer_cv_str = f"{transformer_cv_val:.3f}" if transformer_cv_val is not None else "N/A"
    print(f"   CNN CV: {cnn_cv_str} ({cnn_cv.get('n_models', 0)} models)")
    print(f"   Transformer CV: {transformer_cv_str} ({transformer_cv.get('n_models', 0)} models)")
    print(f"   P2 (CV < 0.15): {'PASS' if cv_result['overall_passed'] else 'FAIL'}")

    # 5. Edge Case Analysis
    print("\n5. Edge Case Analysis...")
    edge_analyzer = EdgeCaseAnalyzer(cnn_threshold=0.6, transformer_threshold=0.2)
    edge_violations = edge_analyzer.detect_violations(features_df)

    print(f"   CNN violations: {edge_violations['cnn_violation_count']}/{edge_violations['cnn_total']} "
          f"({edge_violations['cnn_violation_rate']*100:.1f}%)")
    print(f"   Transformer violations: {edge_violations['transformer_violation_count']}/"
          f"{edge_violations['transformer_total']} ({edge_violations['transformer_violation_rate']*100:.1f}%)")

    # 6. Gate Decision
    print("\n6. MUST_WORK Gate Evaluation...")
    gate_maker = GateDecisionMaker(cohens_d_threshold=1.0, cv_threshold=0.15)
    gate_decision = gate_maker.evaluate_gate(cohens_result, cv_result)

    print(f"   Gate Result: {gate_decision['gate_result']}")
    if gate_decision['failed_criteria']:
        print(f"   Failed Criteria:")
        for criterion in gate_decision['failed_criteria']:
            print(f"     - {criterion}")

    # 7. Save Results
    print("\n7. Saving Results...")

    # Results summary
    results = {
        'hypothesis_id': 'h-m2',
        'timestamp': datetime.now().isoformat(),
        'cohens_d_analysis': cohens_result,
        'scale_invariance': cv_result,
        'edge_case_violations': edge_violations,
        'gate_decision': gate_decision,
        'dataset_info': {
            'n_train': len(train_df),
            'n_val': len(val_df),
            'n_cnn': len(cnn_models),
            'n_transformer': len(transformer_models)
        }
    }

    # Convert numpy types to native Python for JSON serialization
    def convert_numpy(obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(item) for item in obj]
        elif obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        return obj

    results = convert_numpy(results)

    # Save JSON
    results_file = output_dir / 'experiment_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"   ✓ Saved: {results_file}")

    # Save CSV for detailed analysis
    results_csv = output_dir / 'results.csv'
    summary_data = {
        'metric': ['cohens_d', 'p_value', 'cnn_cv', 'transformer_cv',
                   'cnn_violation_rate', 'transformer_violation_rate'],
        'value': [
            cohens_result['cohens_d'],
            cohens_result['p_value'],
            cnn_cv.get('cv', np.nan),
            transformer_cv.get('cv', np.nan),
            edge_violations['cnn_violation_rate'],
            edge_violations['transformer_violation_rate']
        ]
    }
    pd.DataFrame(summary_data).to_csv(results_csv, index=False)
    print(f"   ✓ Saved: {results_csv}")

    # Print final summary
    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    print(f"Gate Result: {gate_decision['gate_result']}")
    print(f"Cohen's d: {cohens_result['cohens_d']:.3f} (threshold: 1.0)")
    print(f"CNN CV: {cnn_cv_str} (threshold: 0.15)")
    print(f"Transformer CV: {transformer_cv_str} (threshold: 0.15)")
    print("=" * 70)

    return results


if __name__ == '__main__':
    run_experiment()
