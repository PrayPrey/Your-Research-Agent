#!/usr/bin/env python
"""
H-M2 Experiment: Meta-Classifier Training Sufficiency

Tests whether 50-60 training datasets provide sufficient examples for 
a Random Forest meta-classifier to learn feature-method relationships.

Gate: SHOULD_WORK
  - PASS: CV Accuracy > 35% AND Generalization Gap < 20%
  - PARTIAL: CV Accuracy >= 30% AND Gap < 25%
  - FAIL: Otherwise
"""

import sys
import json
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_preprocessor import DataPreprocessor
from baseline_model import BaselineModel
from meta_classifier import MetaClassifier
from cv_trainer import CrossValidationTrainer
from metrics_calculator import MetricsCalculator
from gate_evaluator import GateEvaluator
from visualizer import Visualizer


# ============================================================================
# Configuration
# ============================================================================
CONFIG = {
    # Paths (absolute - h-m2 is at docs/youra_research/h-m2/)
    "h_e1_benchmarks": "/workspace/TEST_scope/docs/youra_research/h-e1/code/output/benchmarks_collection.jsonl",
    "h_m1_code": "/workspace/TEST_scope/docs/youra_research/h-m1/code",
    "output_dir": str(Path(__file__).parent / "output"),
    "figures_dir": "/workspace/TEST_scope/docs/youra_research/h-m2/figures",
    
    # Data preprocessing
    "nan_threshold": 0.7,  # Remove features with >70% NaN
    
    # Model hyperparameters
    "meta_classifier": {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "random_state": 42
    },
    
    # Cross-validation
    "n_splits": 13,  # Leave-5-out for 63 samples
    "cv_random_state": 42,
    
    # Gate thresholds
    "gate": {
        "pass_cv_threshold": 0.35,
        "pass_gap_threshold": 0.20,
        "partial_cv_threshold": 0.30,
        "partial_gap_threshold": 0.25
    }
}


def main():
    """Run H-M2 experiment."""
    
    print("=" * 80)
    print("H-M2 EXPERIMENT: Meta-Classifier Training Sufficiency")
    print("=" * 80)
    print()
    
    # Create output directories
    Path(CONFIG["output_dir"]).mkdir(parents=True, exist_ok=True)
    Path(CONFIG["figures_dir"]).mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # Step 1: Load and Preprocess Data
    # ========================================================================
    print("Step 1: Loading and preprocessing data...")
    
    preprocessor = DataPreprocessor(
        h_e1_path=CONFIG["h_e1_benchmarks"],
        h_m1_code_path=CONFIG["h_m1_code"]
    )
    
    X, y, feature_names, benchmark_ids, class_names = preprocessor.load_and_prepare(
        nan_threshold=CONFIG["nan_threshold"]
    )
    
    print(f"  Dataset shape: {X.shape}")
    print(f"  Features: {len(feature_names)}")
    print(f"  Classes: {class_names}")
    print(f"  Class distribution: {np.bincount(y)}")
    print()
    
    # ========================================================================
    # Step 2: Train Baseline Model
    # ========================================================================
    print("Step 2: Training baseline model...")
    
    baseline = BaselineModel(strategy="most_frequent")
    baseline.fit(X, y)
    baseline_accuracy = baseline.score(X, y)
    
    print(f"  Baseline accuracy: {baseline_accuracy:.3f}")
    print()
    
    # ========================================================================
    # Step 3: Cross-Validation with Meta-Classifier
    # ========================================================================
    print("Step 3: Running cross-validation...")
    
    cv_trainer = CrossValidationTrainer(
        n_splits=CONFIG["n_splits"],
        random_state=CONFIG["cv_random_state"]
    )
    
    cv_results = cv_trainer.run_cv(
        model_class=MetaClassifier,
        model_params=CONFIG["meta_classifier"],
        X=X,
        y=y
    )
    
    print(f"  Folds: {CONFIG['n_splits']}")
    print(f"  Train accuracy: {np.mean(cv_results['train_scores']):.3f} ± {np.std(cv_results['train_scores']):.3f}")
    print(f"  Test accuracy:  {np.mean(cv_results['test_scores']):.3f} ± {np.std(cv_results['test_scores']):.3f}")
    print()
    
    # ========================================================================
    # Step 4: Calculate Metrics
    # ========================================================================
    print("Step 4: Calculating metrics...")
    
    calculator = MetricsCalculator()
    
    cv_accuracy = calculator.compute_cv_accuracy(cv_results)
    generalization_gap = calculator.compute_generalization_gap(cv_results)
    baseline_delta = calculator.compute_baseline_delta(cv_accuracy, baseline_accuracy)
    
    # Dummy domain mapping for per-domain accuracy (would come from benchmarks in full implementation)
    benchmark_domains = ["Vision"] * len(y)  # Simplified
    domain_accuracies = calculator.compute_per_domain_accuracy(
        y_true=y,
        y_pred=cv_results["predictions"],
        benchmark_domains=benchmark_domains
    )
    
    cm = calculator.generate_confusion_matrix(
        y_true=y,
        y_pred=cv_results["predictions"],
        class_names=class_names
    )
    
    print(f"  CV Accuracy: {cv_accuracy:.3f}")
    print(f"  Generalization Gap: {generalization_gap:.3f}")
    print(f"  Baseline Delta: {baseline_delta:+.3f}")
    print(f"  Per-domain accuracies: {domain_accuracies}")
    print()
    
    # ========================================================================
    # Step 5: Gate Evaluation
    # ========================================================================
    print("Step 5: Evaluating gate criteria...")
    
    gate = GateEvaluator(**CONFIG["gate"])
    gate_result, gate_message = gate.evaluate(cv_accuracy, generalization_gap)
    
    print(f"  {gate_message}")
    print()
    
    # ========================================================================
    # Step 6: Generate Visualizations
    # ========================================================================
    print("Step 6: Generating visualizations...")
    
    visualizer = Visualizer(output_dir=CONFIG["figures_dir"])
    
    # MANDATORY: Gate metrics comparison
    visualizer.plot_gate_metrics_comparison(
        cv_accuracy=cv_accuracy,
        generalization_gap=generalization_gap,
        baseline_accuracy=baseline_accuracy,
        gate_result=gate_result
    )
    print("  ✓ gate_metrics_comparison.png")
    
    # Learning curve (skip if too few samples or gate already failed)
    try:
        if X.shape[0] >= 30:
            visualizer.plot_learning_curve(
                X=X, y=y,
                model_class=MetaClassifier,
                model_params=CONFIG["meta_classifier"]
            )
            print("  ✓ learning_curve.png")
        else:
            print("  ⊘ learning_curve.png (skipped: insufficient samples)")
    except Exception as e:
        print(f"  ⊘ learning_curve.png (error: {e})")
    
    # Confusion matrix
    visualizer.plot_confusion_matrix(cm, class_names)
    print("  ✓ confusion_matrix.png")
    
    # Per-domain accuracy
    visualizer.plot_per_domain_accuracy(domain_accuracies)
    print("  ✓ per_domain_accuracy.png")
    
    # Feature importance (train on full dataset to get importances)
    full_model = MetaClassifier(**CONFIG["meta_classifier"])
    full_model.fit(X, y)
    importances = full_model.get_feature_importances()
    visualizer.plot_feature_importance(importances, feature_names)
    print("  ✓ feature_importance.png")
    
    # Generalization gap per fold
    visualizer.plot_generalization_gap_per_fold(cv_results)
    print("  ✓ generalization_gap_per_fold.png")
    print()
    
    # ========================================================================
    # Step 7: Save Results
    # ========================================================================
    print("Step 7: Saving results...")
    
    results = {
        "experiment": "H-M2: Meta-Classifier Training Sufficiency",
        "gate_type": "SHOULD_WORK",
        "gate_result": gate_result,
        "gate_satisfied": gate_result == "PASS",
        "metrics": {
            "cv_accuracy": float(cv_accuracy),
            "generalization_gap": float(generalization_gap),
            "baseline_accuracy": float(baseline_accuracy),
            "baseline_delta": float(baseline_delta),
            "train_accuracy_mean": float(np.mean(cv_results["train_scores"])),
            "train_accuracy_std": float(np.std(cv_results["train_scores"])),
            "test_accuracy_mean": float(np.mean(cv_results["test_scores"])),
            "test_accuracy_std": float(np.std(cv_results["test_scores"]))
        },
        "domain_accuracies": domain_accuracies,
        "config": CONFIG,
        "dataset_info": {
            "n_samples": int(X.shape[0]),
            "n_features": int(X.shape[1]),
            "feature_names": feature_names,
            "class_names": class_names,
            "class_distribution": np.bincount(y).tolist()
        }
    }
    
    # Save metrics
    metrics_path = Path(CONFIG["output_dir"]) / "metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  ✓ {metrics_path}")
    
    # Save gate result
    gate_path = Path(CONFIG["output_dir"]) / "gate_result.txt"
    with open(gate_path, 'w') as f:
        f.write(f"{gate_result}\n")
        f.write(f"{gate_message}\n")
    print(f"  ✓ {gate_path}")
    
    # Save CV results
    cv_path = Path(CONFIG["output_dir"]) / "cv_results.json"
    with open(cv_path, 'w') as f:
        json.dump({
            "train_scores": [float(s) for s in cv_results["train_scores"]],
            "test_scores": [float(s) for s in cv_results["test_scores"]],
            "predictions": cv_results["predictions"].tolist()
        }, f, indent=2)
    print(f"  ✓ {cv_path}")
    
    print()
    print("=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    print(f"Gate Result: {gate_result}")
    print(f"CV Accuracy: {cv_accuracy:.3f}")
    print(f"Generalization Gap: {generalization_gap:.3f}")
    print("=" * 80)
    
    # Exit code: 0 for PASS, 1 for PARTIAL/FAIL
    return 0 if gate_result == "PASS" else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
