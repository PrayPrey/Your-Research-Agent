#!/usr/bin/env python3
"""H-M2 Main Pipeline: Architectural Constraints Mechanism Validation

10-step pipeline:
1. Load models
2. Extract architectural features (8 features)
3. Split data (80/20 stratified)
4. Train all-families classifier
5. Evaluate all-families accuracy
6. Within-family validation
7. Random initialization test
8. Mechanism verification
9. Gate check and baseline comparison
10. Generate visualizations
"""

import os
import sys
import json
import numpy as np
from sklearn.model_selection import train_test_split

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import CONFIG
from src.model_loader import ModelLoader
from src.feature_extractor import ArchitecturalFeatureExtractor
from src.classifier import DepthClassifier
from src.evaluator import Evaluator
from src.visualizer import Visualizer
from src.random_init_test import RandomInitTest
from src.within_family_validator import WithinFamilyValidator


def main() -> int:
    """Run H-M2 10-step pipeline. Returns: 0 (success) or 1 (failure)"""

    print("\n" + "="*70)
    print("H-M2: Architectural Constraints Mechanism Validation")
    print("="*70)

    # ========================================================================
    # [1/10] Load models
    # ========================================================================
    print("\n[1/10] Loading pretrained models...")
    loader = ModelLoader(
        shallow_names=CONFIG["shallow_models"],
        deep_names=CONFIG["deep_models"]
    )
    shallow_models, deep_models = loader.load_all_models()

    # ========================================================================
    # [2/10] Extract architectural features (8 features)
    # ========================================================================
    print("\n[2/10] Extracting architectural features...")
    extractor = ArchitecturalFeatureExtractor()

    features = []
    labels = []
    model_names = []

    print("  Extracting from shallow models...")
    for name, model in shallow_models.items():
        feat = extractor.extract_features(model)
        features.append(feat)
        labels.append(0)  # Shallow = 0
        model_names.append(name)
        print(f"    {name}: {feat[:3]}...")  # Print first 3 features

    print("  Extracting from deep models...")
    for name, model in deep_models.items():
        feat = extractor.extract_features(model)
        features.append(feat)
        labels.append(1)  # Deep = 1
        model_names.append(name)
        print(f"    {name}: {feat[:3]}...")

    X = np.array(features)  # [20, 8]
    y = np.array(labels)    # [20,]

    print(f"\n  ✓ Extracted features: {X.shape}")
    print(f"  ✓ Feature range: [{X.min():.2f}, {X.max():.2f}]")

    # ========================================================================
    # [3/10] Split data (80/20 stratified)
    # ========================================================================
    print("\n[3/10] Splitting data...")
    X_train, X_test, y_train, y_test, names_train, names_test = train_test_split(
        X, y, model_names,
        test_size=CONFIG["test_size"],
        stratify=y,
        random_state=CONFIG["random_state"]
    )

    print(f"  ✓ Train: {X_train.shape[0]} models ({np.sum(y_train == 0)} shallow, {np.sum(y_train == 1)} deep)")
    print(f"  ✓ Test: {X_test.shape[0]} models ({np.sum(y_test == 0)} shallow, {np.sum(y_test == 1)} deep)")
    print(f"  Test models: {names_test}")

    # ========================================================================
    # [4/10] Train all-families classifier
    # ========================================================================
    print("\n[4/10] Training all-families classifier...")
    classifier = DepthClassifier(random_state=CONFIG["classifier"]["random_state"])
    classifier.train(X_train, y_train)

    train_accuracy = classifier.score(X_train, y_train)
    print(f"  ✓ Train accuracy: {train_accuracy:.1%}")

    # ========================================================================
    # [5/10] Evaluate all-families accuracy
    # ========================================================================
    print("\n[5/10] Evaluating all-families accuracy...")
    y_pred = classifier.predict(X_test)
    test_accuracy = classifier.score(X_test, y_test)

    evaluator = Evaluator()
    metrics = evaluator.compute_metrics(y_test, y_pred)

    print(f"  ✓ Test accuracy: {test_accuracy:.1%}")
    print(f"  Confusion matrix:")
    print(f"    {metrics['confusion_matrix']}")

    # ========================================================================
    # [6/10] Within-family validation
    # ========================================================================
    print("\n[6/10] Within-family validation...")
    validator = WithinFamilyValidator(random_state=CONFIG["random_state"])
    family_results = validator.validate_within_family(X, y, model_names, test_size=CONFIG["test_size"])

    print("  Family-specific accuracies:")
    for family, result in family_results.items():
        print(f"    {family.upper()}: {result['accuracy']:.1%} ({result['num_samples']} models)")

    # Check within-family threshold
    within_family_passed = any(
        result['accuracy'] >= CONFIG["within_family_threshold"]
        for result in family_results.values()
    )
    print(f"\n  ✓ Within-family validation: {'PASS' if within_family_passed else 'FAIL'} (target: ≥65%)")

    # ========================================================================
    # [7/10] Random initialization test
    # ========================================================================
    print("\n[7/10] Random initialization test...")
    random_tester = RandomInitTest(
        shallow_names=CONFIG["shallow_models"],
        deep_names=CONFIG["deep_models"],
        random_state=CONFIG["random_state"]
    )

    # Replace feature extractor with architectural extractor
    random_tester.extractor = extractor
    random_results = random_tester.run_random_test(test_size=CONFIG["test_size"])

    print(f"  ✓ Random test accuracy: {random_results['test_accuracy']:.1%}")
    print(f"  ✓ Random train accuracy: {random_results['train_accuracy']:.1%}")

    # ========================================================================
    # [8/10] Mechanism verification
    # ========================================================================
    print("\n[8/10] Mechanism verification...")

    # Check if features are architectural vs training-induced
    random_vs_pretrained_gap = test_accuracy - random_results['test_accuracy']
    training_induced = abs(random_vs_pretrained_gap) > 0.1

    if not training_induced:
        print(f"  ✓ Features are ARCHITECTURAL (random ≈ pretrained)")
        mechanism_status = "ARCHITECTURAL"
    else:
        print(f"  ✓ Features are TRAINING-INDUCED (random << pretrained)")
        mechanism_status = "TRAINING-INDUCED"

    print(f"  Random vs Pretrained gap: {random_vs_pretrained_gap:+.1%}")

    # ========================================================================
    # [9/10] Gate check and baseline comparison
    # ========================================================================
    print("\n[9/10] Gate check and baseline comparison...")
    gate_passed = evaluator.check_gate_condition(test_accuracy, CONFIG["gate_threshold"])

    comparison = evaluator.compare_with_baseline(
        h_m1_accuracy=test_accuracy,  # H-M2 accuracy
        h_e1_accuracy=CONFIG["h_e1_accuracy"],
        random_accuracy=random_results['test_accuracy']
    )

    print(f"  Gate threshold: {CONFIG['gate_threshold']:.0%} (SHOULD_WORK)")
    print(f"  Test accuracy: {test_accuracy:.1%}")
    print(f"  Gate status: {'PASS ✓' if gate_passed else 'FAIL ✗'}")
    print(f"\n  Baseline comparison:")
    print(f"    H-E1 (Weight Stats): {CONFIG['h_e1_accuracy']:.1%}")
    print(f"    H-M1 (Gradient Flow): {CONFIG['h_m1_accuracy']:.1%}")
    print(f"    H-M2 (Architecture): {test_accuracy:.1%}")
    print(f"    Random: {CONFIG['baseline_accuracy']:.1%}")

    # ========================================================================
    # [10/10] Generate visualizations
    # ========================================================================
    print("\n[10/10] Generating visualizations...")
    visualizer = Visualizer(output_dir=CONFIG["figures_dir"])

    # Feature names
    feature_names = [
        "Residual Blocks",
        "Dense Connections",
        "Bottleneck Ratio",
        "Layer Count",
        "Skip Connections",
        "Residual Norm",
        "Transition Layers",
        "Arch Family"
    ]

    # 1. Accuracy comparison (MANDATORY)
    visualizer.plot_accuracy_comparison(
        h_e1_accuracy=CONFIG["h_e1_accuracy"],
        h_m1_accuracy=CONFIG["h_m1_accuracy"],
        h_m2_accuracy=test_accuracy,
        random_baseline=CONFIG["baseline_accuracy"],
        random_test_accuracy=random_results['test_accuracy']
    )
    print("  ✓ accuracy_comparison.png")

    # 2. Gate metrics
    visualizer.plot_gate_metrics(
        baseline=CONFIG["baseline_accuracy"],
        actual=test_accuracy,
        target=CONFIG["gate_threshold"],
        passed=gate_passed
    )
    print("  ✓ gate_metrics.png")

    # 3. Within-family comparison (NEW for H-M2)
    visualizer.plot_within_family_comparison(
        family_results=family_results,
        all_families_accuracy=test_accuracy
    )
    print("  ✓ within_family_comparison.png")

    # 4. Feature importance
    coefficients = classifier.get_coefficients()
    visualizer.plot_feature_importance(coefficients, feature_names)
    print("  ✓ feature_importance.png")

    # 5. Confusion matrix
    visualizer.plot_confusion_matrix(metrics['confusion_matrix'], ['shallow', 'deep'])
    print("  ✓ confusion_matrix.png")

    # 6. Feature distributions
    X_shallow = X[y == 0]
    X_deep = X[y == 1]
    visualizer.plot_feature_distributions(X_shallow, X_deep, feature_names)
    print("  ✓ feature_distributions.png")

    # 7. Train-test comparison
    visualizer.plot_train_test_comparison(train_accuracy, test_accuracy)
    print("  ✓ train_test_comparison.png")

    # ========================================================================
    # Save metrics
    # ========================================================================
    print("\nSaving metrics...")

    metrics_output = {
        "hypothesis_id": CONFIG["hypothesis_id"],
        "experiment_name": CONFIG["experiment_name"],
        "test_accuracy": float(test_accuracy),
        "train_accuracy": float(train_accuracy),
        "gate_passed": bool(gate_passed),
        "gate_threshold": CONFIG["gate_threshold"],
        "random_test_accuracy": float(random_results['test_accuracy']),
        "random_train_accuracy": float(random_results['train_accuracy']),
        "mechanism_status": mechanism_status,
        "training_induced": bool(training_induced),
        "within_family_results": {
            family: {
                "accuracy": float(result["accuracy"]),
                "train_accuracy": float(result["train_accuracy"]),
                "num_samples": int(result["num_samples"])
            }
            for family, result in family_results.items()
        },
        "within_family_passed": bool(within_family_passed),
        "confusion_matrix": metrics['confusion_matrix'].tolist(),
        "test_models": names_test,
        "predictions": y_pred.tolist(),
        "true_labels": y_test.tolist(),
        "feature_importance": {
            feature_names[i]: float(coefficients[i])
            for i in range(len(feature_names))
        },
        "baseline_comparison": {
            "h_e1_accuracy": CONFIG["h_e1_accuracy"],
            "h_m1_accuracy": CONFIG["h_m1_accuracy"],
            "h_m2_accuracy": float(test_accuracy),
            "random_baseline": CONFIG["baseline_accuracy"]
        }
    }

    os.makedirs(CONFIG["results_dir"], exist_ok=True)
    with open(os.path.join(CONFIG["results_dir"], "metrics.json"), 'w') as f:
        json.dump(metrics_output, f, indent=2)

    print(f"  ✓ Saved to {CONFIG['results_dir']}/metrics.json")

    # Save features and labels
    np.save(os.path.join(CONFIG["results_dir"], "features.npy"), X)
    np.save(os.path.join(CONFIG["results_dir"], "labels.npy"), y)
    print(f"  ✓ Saved features.npy and labels.npy")

    # ========================================================================
    # Final Summary
    # ========================================================================
    print("\n" + "="*70)
    print("EXPERIMENT SUMMARY")
    print("="*70)
    print(f"Test Accuracy: {test_accuracy:.1%}")
    print(f"Gate Status: {'PASS ✓' if gate_passed else 'FAIL ✗'} (threshold: {CONFIG['gate_threshold']:.0%})")
    print(f"Mechanism: {mechanism_status}")
    print(f"Within-Family Validation: {'PASS ✓' if within_family_passed else 'FAIL ✗'}")
    print(f"\nRandom vs Pretrained:")
    print(f"  Pretrained: {test_accuracy:.1%}")
    print(f"  Random: {random_results['test_accuracy']:.1%}")
    print(f"  Gap: {random_vs_pretrained_gap:+.1%}")
    print("="*70)

    return 0 if gate_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
