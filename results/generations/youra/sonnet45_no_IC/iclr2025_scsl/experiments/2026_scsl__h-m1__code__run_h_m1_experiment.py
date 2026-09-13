"""End-to-end H-M1 Mechanism Analysis Pipeline."""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import json

# Add H-E1 to path
sys.path.insert(0, '../h-e1/code')

from src.model_loader import ModelLoader
from src.mechanism_analyzer import MechanismAnalyzer
from src.gb_baseline import GradientBoostingBaseline
from src.comparator import ModelComparator
from src.mechanism_visualizer import MechanismVisualizer
from src.mechanism_evaluator import MechanismEvaluator


def main():
    """Execute H-M1 mechanism analysis pipeline."""
    print("=" * 70)
    print(" H-M1 Mechanism Analysis: Linear Separability Investigation")
    print("=" * 70)

    # Feature names (REAL DATA ONLY - 6 features)
    # Removed tautological features: commit_freq_weekly, issue_resolution_rate
    feature_names = [
        'stars_log', 'forks_log', 'contributors_log',
        'commits_log', 'issues_log', 'days_since_last',
    ]

    # Expected signs (REAL FEATURES ONLY)
    expected_signs = {
        'days_since_last': 'negative',
        'stars_log': 'positive',
        'forks_log': 'positive',
        'contributors_log': 'positive',
        'commits_log': 'positive',
        'issues_log': 'positive',
    }

    # ========================================================================
    # 1. Load H-E1 Data and Model
    # ========================================================================
    print("\n[1/8] Loading H-E1 model and dataset...")

    # Use absolute path for H-E1
    # Script is in h-m1/code/, H-E1 is in ../h-e1/code/
    script_dir = Path(__file__).parent.resolve()  # h-m1/code/
    h_m1_folder = script_dir.parent  # h-m1/
    research_folder = h_m1_folder.parent  # youra_research/
    h_e1_base = research_folder / 'h-e1' / 'code'

    print(f"  H-E1 base path: {h_e1_base}")
    loader = ModelLoader(h_e1_base_path=str(h_e1_base))
    lr_model, scaler = loader.load_trained_lr()

    # Load H-E1 dataset
    data_path = h_e1_base / 'data' / 'raw_metadata.csv'
    if not data_path.exists():
        raise FileNotFoundError(f"H-E1 dataset not found: {data_path}")

    raw_data = pd.read_csv(data_path)

    # Feature engineering (using H-E1 pipeline)
    from src.feature_engineer import FeatureEngineer
    engineer = FeatureEngineer()
    X = engineer.transform_features(raw_data)
    y = engineer.create_labels(raw_data, threshold_days=180)

    # Train/test split (same as H-E1)
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Scale features
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print(f"✓ Dataset loaded: {len(X_train)} train, {len(X_test)} test")

    # ========================================================================
    # 2. Extract Coefficients and Verify Signs
    # ========================================================================
    print("\n[2/8] Extracting coefficients and verifying signs...")

    analyzer = MechanismAnalyzer(lr_model, feature_names)
    coefficients = analyzer.extract_coefficients()
    signs_correct, sign_report = analyzer.verify_coefficient_signs(coefficients)

    print(f"✓ Coefficients extracted:")
    for feat, coef in coefficients.items():
        sign = '+' if coef > 0 else '-'
        print(f"  {sign} {feat:25s}: {coef:+.4f}")

    print(f"\n✓ Sign verification: {'PASS' if signs_correct else 'FAIL'}")

    # ========================================================================
    # 3. Train Gradient Boosting Baseline
    # ========================================================================
    print("\n[3/8] Training Gradient Boosting baseline...")

    gb = GradientBoostingBaseline(n_estimators=50, max_depth=6, random_state=42)
    gb_info = gb.train(X_train_scaled, y_train)

    print(f"✓ GB trained: {gb_info['n_estimators_used']} estimators")
    print(f"  Train accuracy: {gb_info['train_score']:.4f}")

    # ========================================================================
    # 4. Compare LR vs GB Performance
    # ========================================================================
    print("\n[4/8] Comparing LR vs GB performance...")

    comparator = ModelComparator(lr_model, gb.model, scaler, feature_names)
    performance = comparator.compute_performance_gap(X_test, y_test)

    print(f"✓ Performance comparison:")
    print(f"  LR Accuracy: {performance['lr_accuracy']:.4f}")
    print(f"  GB Accuracy: {performance['gb_accuracy']:.4f}")
    print(f"  Gap:         {performance['gap']:.4f}")
    print(f"  LR F1:       {performance['lr_f1']:.4f}")
    print(f"  GB F1:       {performance['gb_f1']:.4f}")

    linear_sufficient = comparator.check_linear_sufficiency(performance['gap'])
    print(f"\n  Linear sufficient: {linear_sufficient} (threshold: 0.05)")

    # ========================================================================
    # 5. Feature Importance Comparison
    # ========================================================================
    print("\n[5/8] Comparing feature importance...")

    lr_importance = analyzer.compute_feature_importance(use_abs=True)
    gb_importance = gb.get_feature_importance()

    feature_alignment = comparator.compare_feature_importance(
        lr_importance, gb_importance
    )

    print(f"✓ Feature importance:")
    print(f"  LR top-3: {feature_alignment['lr_top3']}")
    print(f"  GB top-3: {feature_alignment['gb_top3']}")
    print(f"  Overlap:  {feature_alignment['overlap_count']}/3 features")
    print(f"  Shared:   {feature_alignment['overlap_features']}")

    # ========================================================================
    # 6. PCA Decision Boundary Visualization
    # ========================================================================
    print("\n[6/8] Generating PCA projection and decision boundary...")

    X_2d, pca = analyzer.pca_projection(X_test_scaled, n_components=2)
    xx, yy, Z = analyzer.generate_decision_boundary_mesh(X_2d, pca, lr_model)

    pca_variance = (pca.explained_variance_ratio_[0], pca.explained_variance_ratio_[1])
    print(f"✓ PCA projection complete (variance explained: {sum(pca_variance):.1%})")

    # ========================================================================
    # 7. Generate Visualizations
    # ========================================================================
    print("\n[7/8] Generating figures...")

    visualizer = MechanismVisualizer(output_dir='../figures/', dpi=300)

    visualizer.plot_coefficients(
        coefficients, expected_signs,
        save_path='coefficient_bar_chart.png'
    )

    visualizer.plot_performance_comparison(
        performance, performance,
        save_path='performance_comparison.png'
    )

    visualizer.plot_decision_boundary_pca(
        X_2d, y_test, Z, xx, yy, pca_variance,
        save_path='decision_boundary_pca.png'
    )

    visualizer.plot_feature_importance_comparison(
        lr_importance, feature_alignment['gb_importance'], feature_names,
        save_path='feature_importance_comparison.png'
    )

    visualizer.plot_confusion_matrices(
        y_test, performance['lr_pred'], performance['gb_pred'],
        save_path='confusion_matrix_comparison.png'
    )

    print("✓ All figures generated")

    # ========================================================================
    # 8. Gate Evaluation and Report Generation
    # ========================================================================
    print("\n[8/8] Evaluating mechanism gates...")

    evaluator = MechanismEvaluator(
        accuracy_gap_threshold=0.05,
        feature_overlap_threshold=2
    )

    # Extract sign correctness per feature
    sign_correctness = {f: sign_report[f]['correct'] for f in feature_names}

    mechanism_validated, detailed_report = evaluator.evaluate_mechanism(
        sign_correctness,
        performance['gap'],
        feature_alignment['overlap_count']
    )

    print(f"\n{'='*70}")
    print(f" GATE RESULT: {detailed_report['overall']['result']}")
    print(f"{'='*70}")

    # Generate validation report
    report_text = evaluator.generate_mechanism_report(detailed_report)

    # Save validation report
    report_path = Path('../04_validation.md')
    with open(report_path, 'w') as f:
        f.write(report_text)

    print(f"✓ Validation report saved: {report_path}")

    # Save experiment results (for Phase 5)
    results = {
        'hypothesis_id': 'h-m1',
        'gate_type': 'MUST_WORK',
        'gate_satisfied': mechanism_validated,
        'metrics': {
            'coefficient_signs_correct': signs_correct,
            'performance_gap': performance['gap'],
            'feature_overlap': feature_alignment['overlap_count'],
            'lr_accuracy': performance['lr_accuracy'],
            'gb_accuracy': performance['gb_accuracy'],
            'lr_f1': performance['lr_f1'],
            'gb_f1': performance['gb_f1']
        },
        'coefficients': coefficients,
        'feature_importance': {
            'lr': lr_importance,
            'gb': feature_alignment['gb_importance']
        }
    }

    results_path = Path('../experiment_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✓ Experiment results saved: {results_path}")

    print("\n" + "="*70)
    print(" H-M1 Mechanism Analysis Complete")
    print("="*70)

    return mechanism_validated


if __name__ == '__main__':
    try:
        result = main()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
