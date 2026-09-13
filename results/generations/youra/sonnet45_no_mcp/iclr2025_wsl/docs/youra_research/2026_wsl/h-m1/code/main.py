#!/usr/bin/env python3
"""
H-M1: Gradient Flow Feature Validation
Main Experiment Script

Tests whether gradient accumulation during training creates distinguishable
weight magnitude patterns between shallow and deep networks.
"""

import numpy as np
import json
import os
import sys
from sklearn.model_selection import train_test_split
from config import CONFIG
from src.model_loader import ModelLoader
from src.feature_extractor import GradientFlowFeatureExtractor
from src.classifier import DepthClassifier
from src.evaluator import Evaluator
from src.visualizer import Visualizer
from src.random_init_test import RandomInitTest


def main():
    """Execute h-m1 experiment."""
    print("="*80)
    print("H-M1: GRADIENT FLOW FEATURE VALIDATION")
    print("="*80)
    print("\nExperiment: Test gradient accumulation mechanism")
    print("Dataset: 20 pretrained ImageNet models (10 shallow + 10 deep)")
    print("Gate: MUST_WORK (test accuracy > 50%, gradient contribution)")
    print("Baseline: H-E1 achieved 100% accuracy with all weight statistics")
    print()

    # Initialize components
    loader = ModelLoader(
        shallow_names=CONFIG["shallow_models"],
        deep_names=CONFIG["deep_models"]
    )
    extractor = GradientFlowFeatureExtractor()
    classifier = DepthClassifier(random_state=CONFIG["random_state"])
    evaluator = Evaluator()
    visualizer = Visualizer(output_dir=CONFIG["figures_dir"])

    # Step 1: Load models
    print("\n[1/9] Loading Pretrained Models...")
    shallow_models, deep_models = loader.load_all_models()

    # Step 2: Extract gradient-flow features
    print(f"\n[2/9] Extracting Gradient-Flow Features...")
    print("Features: [slope, variance, input_norm, output_norm, depth_weighted, layer_count]")

    features = []
    labels = []
    layer_counts = []

    # Extract from shallow models (label=0)
    print(f"\nExtracting from {len(shallow_models)} shallow models...")
    for name, model in shallow_models.items():
        feat = extractor.extract_features(model)
        layer_norms, _ = extractor.extract_layer_norms_with_positions(model)
        features.append(feat)
        labels.append(0)
        layer_count = len(layer_norms)
        layer_counts.append(layer_count)
        print(f"  {name:20s}: {layer_count:3d} layers, features={feat[:3]} ...")

    # Extract from deep models (label=1)
    print(f"\nExtracting from {len(deep_models)} deep models...")
    for name, model in deep_models.items():
        feat = extractor.extract_features(model)
        layer_norms, _ = extractor.extract_layer_norms_with_positions(model)
        features.append(feat)
        labels.append(1)
        layer_count = len(layer_norms)
        layer_counts.append(layer_count)
        print(f"  {name:20s}: {layer_count:3d} layers, features={feat[:3]} ...")

    X = np.array(features)  # Shape: (20, 6)
    y = np.array(labels)    # Shape: (20,)

    print(f"\n✓ Gradient-flow features extracted: {X.shape}")
    print(f"  Shallow samples: {np.sum(y == 0)}")
    print(f"  Deep samples: {np.sum(y == 1)}")
    print(f"  Feature range: layers {min(layer_counts)} - {max(layer_counts)}")

    # Save features
    os.makedirs(CONFIG["results_dir"], exist_ok=True)
    np.save(f"{CONFIG['results_dir']}/features.npy", X)
    np.save(f"{CONFIG['results_dir']}/labels.npy", y)

    # Step 3: Split data
    print(f"\n[3/9] Splitting Data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=CONFIG["test_size"],
        stratify=y,
        random_state=CONFIG["random_state"]
    )

    print(f"  Train set: {len(X_train)} samples ({np.sum(y_train == 0)} shallow, {np.sum(y_train == 1)} deep)")
    print(f"  Test set:  {len(X_test)} samples ({np.sum(y_test == 0)} shallow, {np.sum(y_test == 1)} deep)")

    # Step 4: Train classifier
    print(f"\n[4/9] Training Classifier...")
    print(f"  Classifier: LogisticRegression(C={CONFIG['classifier']['C']}, solver='{CONFIG['classifier']['solver']}')")
    classifier.train(X_train, y_train)
    print("  ✓ Classifier trained")

    # Step 5: Evaluate on pretrained models
    print(f"\n[5/9] Evaluating on Pretrained Models...")
    train_accuracy = classifier.score(X_train, y_train)
    test_accuracy = classifier.score(X_test, y_test)

    y_pred = classifier.predict(X_test)
    metrics = evaluator.compute_metrics(y_test, y_pred)

    print(f"\n  Pretrained Models:")
    print(f"    Train Accuracy: {train_accuracy:.2%}")
    print(f"    Test Accuracy:  {test_accuracy:.2%}")
    print(f"\n  Confusion Matrix:")
    print(f"  {metrics['confusion_matrix']}")

    # Step 6: Random initialization test
    random_test_results = None
    if CONFIG["run_random_test"]:
        print(f"\n[6/9] Random Initialization Test...")
        random_tester = RandomInitTest(
            shallow_names=CONFIG["shallow_models"],
            deep_names=CONFIG["deep_models"],
            random_state=CONFIG["random_state"]
        )
        random_test_results = random_tester.run_random_test(test_size=CONFIG["test_size"])
    else:
        print(f"\n[6/9] Random Initialization Test... SKIPPED")

    # Step 7: Mechanism verification
    print(f"\n[7/9] Mechanism Verification...")
    results = {
        'num_models': 20,
        'feature_shape': (6,),
        'min_layer_count': min(layer_counts),
        'max_layer_count': max(layer_counts),
        'train_accuracy': train_accuracy,
        'test_accuracy': test_accuracy
    }

    indicators = evaluator.verify_mechanism(results)
    indicator_names = [
        'Features Extracted (6 gradient-flow features)',
        'Layer Positions Valid',
        'Classifier Trained',
        'Gradient Effect Detected (accuracy > 50%)'
    ]

    print("  Mechanism Indicators:")
    for name, status in zip(indicator_names, indicators):
        print(f"    {'✓' if status else '✗'} {name}")

    # Step 8: Gate check and baseline comparison
    print(f"\n[8/9] Gate Condition Check...")
    gate_passed = evaluator.check_gate_condition(
        test_accuracy,
        threshold=CONFIG["gate_threshold"]
    )

    # Compare with h-e1 baseline
    random_acc = random_test_results['test_accuracy'] if random_test_results else None
    comparison = evaluator.compare_with_baseline(
        h_m1_accuracy=test_accuracy,
        h_e1_accuracy=CONFIG["h_e1_accuracy"],
        random_accuracy=random_acc
    )

    print(f"\n  Baseline Comparison:")
    print(f"    H-E1 (all weight stats):     {comparison['h_e1_accuracy']:.2%}")
    print(f"    H-M1 (gradient-flow):        {comparison['h_m1_accuracy']:.2%}")
    print(f"    Performance gap:             {comparison['performance_gap']:.2%}")
    if random_acc:
        print(f"    Random models (untrained):   {random_acc:.2%}")
        print(f"    Training-induced patterns:   {'✓ YES' if comparison['training_induced'] else '✗ NO'}")
    print(f"\n  Interpretation: {comparison['interpretation']}")
    print(f"  Contribution:   {comparison['contribution']}")

    # Step 9: Generate visualizations
    print(f"\n[9/9] Generating Figures...")

    # 1. Accuracy comparison (MANDATORY)
    visualizer.plot_accuracy_comparison(
        h_e1_accuracy=CONFIG["h_e1_accuracy"],
        h_m1_accuracy=test_accuracy,
        random_baseline=CONFIG["baseline_accuracy"],
        random_test_accuracy=random_acc
    )
    print(f"  ✓ accuracy_comparison.png")

    # 2. Gate metrics
    visualizer.plot_gate_metrics(
        baseline=CONFIG["baseline_accuracy"],
        actual=test_accuracy,
        target=CONFIG["gate_threshold"],
        passed=gate_passed
    )
    print(f"  ✓ gate_metrics.png")

    # 3. Confusion matrix
    visualizer.plot_confusion_matrix(
        cm=metrics['confusion_matrix'],
        class_names=['shallow', 'deep']
    )
    print(f"  ✓ confusion_matrix.png")

    # 4. Feature distributions
    X_shallow = X[y == 0]
    X_deep = X[y == 1]
    feature_names = [
        'Norm Slope',
        'Norm Variance',
        'Input Norm',
        'Output Norm',
        'Depth-Weighted Norm',
        'Layer Count'
    ]
    visualizer.plot_feature_distributions(X_shallow, X_deep, feature_names)
    print(f"  ✓ feature_distributions.png")

    # 5. Feature importance
    coefficients = classifier.get_coefficients()
    visualizer.plot_feature_importance(coefficients, feature_names)
    print(f"  ✓ feature_importance.png")

    # 6. Train vs test comparison
    visualizer.plot_train_test_comparison(train_accuracy, test_accuracy)
    print(f"  ✓ train_test_comparison.png")

    # Save results
    final_results = {
        'hypothesis_id': 'h-m1',
        'experiment_name': 'Gradient Flow Feature Validation',
        'test_accuracy': float(test_accuracy),
        'train_accuracy': float(train_accuracy),
        'baseline_accuracy': CONFIG["baseline_accuracy"],
        'h_e1_accuracy': CONFIG["h_e1_accuracy"],
        'gate_threshold': CONFIG["gate_threshold"],
        'gate_passed': gate_passed,
        'confusion_matrix': metrics['confusion_matrix'].tolist(),
        'classification_report': metrics['classification_report'],
        'mechanism_indicators': {
            'features_extracted': indicators[0],
            'layer_positions_valid': indicators[1],
            'classifier_trained': indicators[2],
            'gradient_effect_detected': indicators[3]
        },
        'feature_importance': {
            'norm_slope': float(coefficients[0]),
            'norm_variance': float(coefficients[1]),
            'input_norm': float(coefficients[2]),
            'output_norm': float(coefficients[3]),
            'depth_weighted_norm': float(coefficients[4]),
            'layer_count': float(coefficients[5])
        },
        'baseline_comparison': comparison,
        'num_models': 20,
        'num_train': len(X_train),
        'num_test': len(X_test),
        'feature_count': 6,
        'layer_count_range': {
            'min': int(min(layer_counts)),
            'max': int(max(layer_counts))
        }
    }

    # Add random test results if available
    if random_test_results:
        final_results['random_test'] = {
            'test_accuracy': float(random_test_results['test_accuracy']),
            'train_accuracy': float(random_test_results['train_accuracy']),
            'interpretation': str(random_test_results['interpretation']),
            'training_required': bool(random_test_results['training_required'])
        }

    # Convert numpy types to native Python types for JSON serialization
    def convert_to_native(obj):
        """Recursively convert numpy types to native Python types."""
        if isinstance(obj, dict):
            return {k: convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_native(v) for v in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    final_results = convert_to_native(final_results)

    with open(f"{CONFIG['results_dir']}/metrics.json", 'w') as f:
        json.dump(final_results, f, indent=2)

    # Final summary
    print(f"\n{'='*80}")
    print("EXPERIMENT COMPLETE")
    print(f"{'='*80}")
    print(f"H-M1 Test Accuracy:  {test_accuracy:.2%}")
    print(f"H-E1 Baseline:       {CONFIG['h_e1_accuracy']:.2%}")
    print(f"Performance Gap:     {comparison['performance_gap']:.2%}")
    print(f"Gate Threshold:      {CONFIG['gate_threshold']:.2%}")
    print(f"Gate Status:         {'✓ PASS' if gate_passed else '✗ FAIL'}")
    print(f"\nMechanism: {comparison['interpretation']}")
    print(f"Contribution: {comparison['contribution']}")
    if random_test_results:
        print(f"\nRandom Models: {random_acc:.2%} (training-induced: {'YES' if comparison['training_induced'] else 'NO'})")
    print(f"\nResults saved to: {CONFIG['results_dir']}/metrics.json")
    print(f"Figures saved to: {CONFIG['figures_dir']}/")
    print(f"{'='*80}")

    return 0 if gate_passed else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"ERROR: Experiment failed")
        print(f"{'='*80}")
        print(f"{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
