#!/usr/bin/env python3
"""
H-E1: Weight-Based Depth Classification
Main Experiment Script
"""

import numpy as np
import json
import os
from sklearn.model_selection import train_test_split
from config import CONFIG
from src.model_loader import ModelLoader
from src.feature_extractor import FeatureExtractor
from src.classifier import DepthClassifier
from src.evaluator import Evaluator
from src.visualizer import Visualizer


def main():
    """Execute h-e1 experiment."""
    print("="*80)
    print("H-E1: WEIGHT-BASED DEPTH CLASSIFICATION")
    print("="*80)
    print("\nExperiment: Binary classification of CNN depth from weight statistics")
    print("Dataset: 20 pretrained ImageNet models (10 shallow + 10 deep)")
    print("Gate: MUST_WORK (test accuracy >= 70%)")
    print()

    # Initialize components
    loader = ModelLoader(
        shallow_names=CONFIG["shallow_models"],
        deep_names=CONFIG["deep_models"]
    )
    extractor = FeatureExtractor()
    classifier = DepthClassifier(random_state=CONFIG["random_state"])
    evaluator = Evaluator()
    visualizer = Visualizer(output_dir=CONFIG["figures_dir"])

    # Step 1: Load models
    print("\n[1/7] Loading Models...")
    shallow_models, deep_models = loader.load_all_models()

    # Step 2: Extract features
    print(f"\n[2/7] Extracting Features...")
    features = []
    labels = []
    layer_counts = []

    # Extract from shallow models (label=0)
    print(f"\nExtracting from {len(shallow_models)} shallow models...")
    for name, model in shallow_models.items():
        feat = extractor.extract_features(model)
        features.append(feat)
        labels.append(0)
        layer_count = len(extractor.extract_layer_norms(model))
        layer_counts.append(layer_count)
        print(f"  {name}: {layer_count} layers, features={feat}")

    # Extract from deep models (label=1)
    print(f"\nExtracting from {len(deep_models)} deep models...")
    for name, model in deep_models.items():
        feat = extractor.extract_features(model)
        features.append(feat)
        labels.append(1)
        layer_count = len(extractor.extract_layer_norms(model))
        layer_counts.append(layer_count)
        print(f"  {name}: {layer_count} layers, features={feat}")

    X = np.array(features)  # Shape: (20, 4)
    y = np.array(labels)    # Shape: (20,)

    print(f"\n✓ Features extracted: {X.shape}")
    print(f"  Shallow samples: {np.sum(y == 0)}")
    print(f"  Deep samples: {np.sum(y == 1)}")

    # Save features
    os.makedirs(CONFIG["results_dir"], exist_ok=True)
    np.save(f"{CONFIG['results_dir']}/features.npy", X)
    np.save(f"{CONFIG['results_dir']}/labels.npy", y)

    # Step 3: Split data
    print(f"\n[3/7] Splitting Data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=CONFIG["test_size"],
        stratify=y,
        random_state=CONFIG["random_state"]
    )

    print(f"  Train set: {len(X_train)} samples ({np.sum(y_train == 0)} shallow, {np.sum(y_train == 1)} deep)")
    print(f"  Test set:  {len(X_test)} samples ({np.sum(y_test == 0)} shallow, {np.sum(y_test == 1)} deep)")

    # Step 4: Train classifier
    print(f"\n[4/7] Training Classifier...")
    classifier.train(X_train, y_train)
    print("  ✓ Classifier trained")

    # Step 5: Evaluate
    print(f"\n[5/7] Evaluating...")
    train_accuracy = classifier.score(X_train, y_train)
    test_accuracy = classifier.score(X_test, y_test)

    y_pred = classifier.predict(X_test)
    metrics = evaluator.compute_metrics(y_test, y_pred)

    print(f"\n  Train Accuracy: {train_accuracy:.2%}")
    print(f"  Test Accuracy:  {test_accuracy:.2%}")
    print(f"\n  Confusion Matrix:")
    print(f"  {metrics['confusion_matrix']}")

    # Step 6: Mechanism verification
    print(f"\n[6/7] Mechanism Verification...")
    results = {
        'num_models': 20,
        'feature_shape': (4,),
        'min_layer_count': min(layer_counts),
        'max_layer_count': max(layer_counts),
        'train_accuracy': train_accuracy,
        'test_accuracy': test_accuracy
    }

    indicators = evaluator.verify_mechanism(results)
    indicator_names = ['Features Extracted', 'Layer Norms Valid', 'Classifier Trained', 'Effect Detected']

    print("  Mechanism Indicators:")
    for name, status in zip(indicator_names, indicators):
        print(f"    {'✓' if status else '✗'} {name}")

    # Step 7: Gate check
    print(f"\n[7/7] Gate Condition Check...")
    gate_passed = evaluator.check_gate_condition(
        test_accuracy,
        threshold=CONFIG["gate_threshold"]
    )

    # Generate visualizations
    print(f"\nGenerating Figures...")

    # 1. Gate metrics (MANDATORY)
    visualizer.plot_gate_metrics(
        baseline=CONFIG["baseline_accuracy"],
        actual=test_accuracy,
        target=CONFIG["gate_threshold"],
        passed=gate_passed
    )
    print(f"  ✓ gate_metrics.png")

    # 2. Confusion matrix
    visualizer.plot_confusion_matrix(
        cm=metrics['confusion_matrix'],
        class_names=['shallow', 'deep']
    )
    print(f"  ✓ confusion_matrix.png")

    # 3. Feature distributions
    X_shallow = X[y == 0]
    X_deep = X[y == 1]
    visualizer.plot_feature_distributions(X_shallow, X_deep)
    print(f"  ✓ feature_distributions.png")

    # 4. Feature importance
    coefficients = classifier.get_coefficients()
    visualizer.plot_feature_importance(
        coefficients=coefficients,
        feature_names=['Mean', 'Std', 'Min', 'Max']
    )
    print(f"  ✓ feature_importance.png")

    # 5. Train vs test comparison
    visualizer.plot_train_test_comparison(train_accuracy, test_accuracy)
    print(f"  ✓ train_test_comparison.png")

    # Save results
    final_results = {
        'test_accuracy': float(test_accuracy),
        'train_accuracy': float(train_accuracy),
        'baseline_accuracy': CONFIG["baseline_accuracy"],
        'gate_threshold': CONFIG["gate_threshold"],
        'gate_passed': gate_passed,
        'confusion_matrix': metrics['confusion_matrix'].tolist(),
        'classification_report': metrics['classification_report'],
        'mechanism_indicators': {
            'features_extracted': indicators[0],
            'layer_norms_valid': indicators[1],
            'classifier_trained': indicators[2],
            'effect_detected': indicators[3]
        },
        'feature_importance': {
            'mean': float(coefficients[0]),
            'std': float(coefficients[1]),
            'min': float(coefficients[2]),
            'max': float(coefficients[3])
        },
        'num_models': 20,
        'num_train': len(X_train),
        'num_test': len(X_test)
    }

    with open(f"{CONFIG['results_dir']}/metrics.json", 'w') as f:
        json.dump(final_results, f, indent=2)

    # Final summary
    print(f"\n{'='*80}")
    print("EXPERIMENT COMPLETE")
    print(f"{'='*80}")
    print(f"Test Accuracy:  {test_accuracy:.2%}")
    print(f"Gate Threshold: {CONFIG['gate_threshold']:.2%}")
    print(f"Gate Status:    {'✓ PASS' if gate_passed else '✗ FAIL'}")
    print(f"\nResults saved to: {CONFIG['results_dir']}/metrics.json")
    print(f"Figures saved to: {CONFIG['figures_dir']}/")
    print(f"{'='*80}")

    return 0 if gate_passed else 1


if __name__ == "__main__":
    exit(main())
