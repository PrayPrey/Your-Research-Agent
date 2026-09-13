"""Main experiment runner for h-m2."""
import json
import sys
from pathlib import Path

from kb_loader import KBLoader
from verifier import ConstraintVerifier
from test_loader import TestLoader
from evaluator import Evaluator
from baseline import RandomBaseline
from visualizer import Visualizer

def run_experiment(kb_path: str, test_path: str, output_dir: str, figures_dir: str):
    """Execute full h-m2 evaluation pipeline."""
    print("=" * 60)
    print("h-m2 Experiment: Constraint-Satisfiability Verification")
    print("=" * 60)

    # Load KB from h-m1
    print("\n[1/7] Loading knowledge base...")
    kb_loader = KBLoader(kb_path)
    kb = kb_loader.load()
    print(f"  Loaded {len(kb)} triples from h-m1")

    # Load test set
    print("\n[2/7] Loading test set...")
    test_loader = TestLoader(test_path)
    hypotheses, ground_truth = test_loader.load()
    print(f"  Loaded {len(hypotheses)} expert-labeled hypotheses")
    print(f"  Balance: {sum(1 for g in ground_truth if g == 'testable')} testable, {sum(1 for g in ground_truth if g == 'not_testable')} not_testable")

    # Baseline predictions
    print("\n[3/7] Running baseline (random classifier)...")
    baseline = RandomBaseline(seed=42)
    baseline_preds = baseline.predict(len(hypotheses))

    # Proposed predictions
    print("\n[4/7] Running proposed verifier...")
    verifier = ConstraintVerifier(kb)
    proposed_preds = [verifier.verify(h) for h in hypotheses]

    # Evaluate baseline
    print("\n[5/7] Evaluating baseline...")
    evaluator = Evaluator()
    baseline_metrics = evaluator.compute_metrics(baseline_preds, ground_truth)
    print(f"  Baseline FPR: {baseline_metrics['fpr']:.3f}")
    print(f"  Baseline Precision: {baseline_metrics['precision']:.3f}")
    print(f"  Baseline Accuracy: {baseline_metrics['accuracy']:.3f}")

    # Evaluate proposed
    print("\n[6/7] Evaluating proposed verifier...")
    proposed_metrics = evaluator.compute_metrics(proposed_preds, ground_truth)
    print(f"  Proposed FPR: {proposed_metrics['fpr']:.3f}")
    print(f"  Proposed Precision: {proposed_metrics['precision']:.3f}")
    print(f"  Proposed Accuracy: {proposed_metrics['accuracy']:.3f}")
    print(f"  Proposed TNR (Specificity): {proposed_metrics['tnr']:.3f}")

    # Confusion matrix
    cm_baseline = evaluator.confusion_matrix(baseline_preds, ground_truth)
    cm_proposed = evaluator.confusion_matrix(proposed_preds, ground_truth)

    print("\nConfusion Matrix (Proposed):")
    print(f"  TP: {cm_proposed['tp']}, FP: {cm_proposed['fp']}")
    print(f"  FN: {cm_proposed['fn']}, TN: {cm_proposed['tn']}")

    # Gate check
    GATE_THRESHOLD = 0.25
    gate_passed = proposed_metrics['fpr'] < GATE_THRESHOLD
    poc_passed = proposed_metrics['fpr'] < baseline_metrics['fpr']

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Gate Threshold: FPR < {GATE_THRESHOLD}")
    print(f"Actual FPR: {proposed_metrics['fpr']:.3f}")
    print(f"Gate Status: {'PASS' if gate_passed else 'FAIL'}")
    print(f"\nPoC Check: proposed_fpr < baseline_fpr")
    print(f"  {proposed_metrics['fpr']:.3f} < {baseline_metrics['fpr']:.3f} → {'PASS' if poc_passed else 'FAIL'}")
    print("=" * 60)

    # Save results
    print("\n[7/7] Saving results and visualizations...")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = {
        "gate_threshold": GATE_THRESHOLD,
        "gate_passed": gate_passed,
        "poc_passed": poc_passed,
        "baseline": baseline_metrics,
        "proposed": proposed_metrics,
        "confusion_matrix_baseline": cm_baseline,
        "confusion_matrix_proposed": cm_proposed
    }

    with open(output_path / "metrics.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Saved metrics to {output_path / 'metrics.json'}")

    # Save predictions
    predictions_data = []
    for i in range(len(hypotheses)):
        predictions_data.append({
            "id": i + 1,
            "hypothesis": hypotheses[i],
            "ground_truth": ground_truth[i],
            "baseline_prediction": baseline_preds[i],
            "proposed_prediction": proposed_preds[i]
        })

    with open(output_path / "predictions.json", "w") as f:
        json.dump(predictions_data, f, indent=2)
    print(f"  Saved predictions to {output_path / 'predictions.json'}")

    # Visualizations
    viz = Visualizer(figures_dir)

    viz.plot_confusion_matrix(cm_baseline, "Baseline (Random) Confusion Matrix", "cm_baseline.png")
    viz.plot_confusion_matrix(cm_proposed, "Proposed Verifier Confusion Matrix", "cm_proposed.png")
    viz.plot_metrics_comparison(baseline_metrics, proposed_metrics, "metrics_comparison.png")
    viz.plot_gate_comparison(GATE_THRESHOLD, proposed_metrics['fpr'], "gate_comparison.png")

    print(f"  Saved visualizations to {figures_dir}")

    print("\n" + "=" * 60)
    print("Experiment complete.")
    print("=" * 60)

    return results


if __name__ == "__main__":
    # Default paths
    KB_PATH = "../../h-m1/data/pwc_cache/kb.yaml"
    TEST_PATH = "../data/test_hypotheses.json"
    OUTPUT_DIR = "../results"
    FIGURES_DIR = "../figures"

    results = run_experiment(KB_PATH, TEST_PATH, OUTPUT_DIR, FIGURES_DIR)

    # Exit code based on gate status
    sys.exit(0 if results["gate_passed"] else 1)
