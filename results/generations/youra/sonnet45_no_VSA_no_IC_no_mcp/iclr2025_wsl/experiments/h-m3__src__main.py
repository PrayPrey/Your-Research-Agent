"""Confound detection experiment runner."""

import json
import sys
from pathlib import Path

from confound_db import ConfoundDatabase
from detector import ConfoundDetector
from evaluator import Evaluator
from baseline import RandomBaseline
from test_loader import TestLoader
from visualizer import Visualizer


def run_experiment(output_dir: str, figures_dir: str) -> dict:
    """Execute confound detection pipeline. Returns: {baseline_metrics, proposed_metrics, gate_passed}."""

    print("=== Confound Pattern Detection Experiment (h-m3) ===")

    # Setup
    print("\n[1/5] Loading confound database...")
    db = ConfoundDatabase()
    patterns = db.load_patterns()
    all_patterns = db.get_all_patterns()
    print(f"Loaded {len(all_patterns)} confound patterns across 3 domains")

    detector = ConfoundDetector(patterns)

    # Generate test set
    print("\n[2/5] Generating test set...")
    loader = TestLoader()
    test_set = loader.generate_test_set()

    hypotheses = [sample["text"] for sample in test_set]
    ground_truth = [sample["label"] for sample in test_set]

    confounded_count = sum(1 for label in ground_truth if label == "confounded")
    unconfounded_count = len(ground_truth) - confounded_count
    print(f"Generated {len(test_set)} hypotheses ({confounded_count} confounded, {unconfounded_count} unconfounded)")

    # Baseline predictions
    print("\n[3/5] Running baseline (random)...")
    baseline = RandomBaseline(seed=42)
    baseline_preds = baseline.predict(len(hypotheses))

    # Proposed predictions
    print("\n[4/5] Running proposed detector...")
    proposed_preds = []
    for h in hypotheses:
        label, pattern = detector.detect(h)
        proposed_preds.append(label)

    # Evaluate
    print("\n[5/5] Evaluating and visualizing...")
    evaluator = Evaluator()
    baseline_metrics = evaluator.compute_metrics(ground_truth, baseline_preds)
    proposed_metrics = evaluator.compute_metrics(ground_truth, proposed_preds)

    # Gate check
    GATE_THRESHOLD = 0.40
    gate_passed = proposed_metrics["precision"] > GATE_THRESHOLD
    poc_passed = proposed_metrics["precision"] > baseline_metrics["precision"]

    print("\n=== Results ===")
    print(f"Baseline Precision: {baseline_metrics['precision']:.4f}")
    print(f"Proposed Precision: {proposed_metrics['precision']:.4f}")
    print(f"Gate Threshold: {GATE_THRESHOLD}")
    print(f"\nGate Status: {'PASS' if gate_passed else 'FAIL'}")
    print(f"PoC Status: {'PASS' if poc_passed else 'FAIL'}")

    print("\nProposed Metrics:")
    print(f"  Precision: {proposed_metrics['precision']:.4f}")
    print(f"  Recall: {proposed_metrics['recall']:.4f}")
    print(f"  Accuracy: {proposed_metrics['accuracy']:.4f}")
    print(f"  F1: {proposed_metrics['f1']:.4f}")
    print(f"  TP: {proposed_metrics['tp']}, FP: {proposed_metrics['fp']}, TN: {proposed_metrics['tn']}, FN: {proposed_metrics['fn']}")

    # Visualize
    viz = Visualizer(figures_dir)

    fig1_path = viz.plot_gate_comparison(
        baseline_metrics["precision"],
        proposed_metrics["precision"],
        GATE_THRESHOLD,
        "gate_comparison.png",
    )
    print(f"\nFigure 1 saved: {fig1_path}")

    fig2_path = viz.plot_confusion_matrix(
        evaluator.confusion_matrix(ground_truth, proposed_preds),
        "Proposed Confound Detector",
        "confusion_matrix.png",
    )
    print(f"Figure 2 saved: {fig2_path}")

    fig3_path = viz.plot_domain_breakdown(test_set, proposed_preds, "domain_breakdown.png")
    print(f"Figure 3 saved: {fig3_path}")

    # Save results
    results = {
        "gate_threshold": GATE_THRESHOLD,
        "gate_passed": gate_passed,
        "poc_passed": poc_passed,
        "baseline": {
            "precision": baseline_metrics["precision"],
            "recall": baseline_metrics["recall"],
            "accuracy": baseline_metrics["accuracy"],
            "f1": baseline_metrics["f1"],
            "tp": baseline_metrics["tp"],
            "fp": baseline_metrics["fp"],
            "tn": baseline_metrics["tn"],
            "fn": baseline_metrics["fn"],
        },
        "proposed": {
            "precision": proposed_metrics["precision"],
            "recall": proposed_metrics["recall"],
            "accuracy": proposed_metrics["accuracy"],
            "f1": proposed_metrics["f1"],
            "tp": proposed_metrics["tp"],
            "fp": proposed_metrics["fp"],
            "tn": proposed_metrics["tn"],
            "fn": proposed_metrics["fn"],
        },
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results_file = output_path / "metrics.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved: {results_file}")

    # Save test set
    data_dir = output_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    test_set_file = data_dir / "test_set.json"
    with open(test_set_file, "w") as f:
        json.dump(test_set, f, indent=2)

    print(f"Test set saved: {test_set_file}")

    return results


if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    output_dir = str(base_dir)
    figures_dir = str(base_dir / "figures")

    results = run_experiment(output_dir, figures_dir)

    sys.exit(0 if results["gate_passed"] and results["poc_passed"] else 1)
