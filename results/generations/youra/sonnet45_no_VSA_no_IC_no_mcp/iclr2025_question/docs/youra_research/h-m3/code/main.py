"""Main experiment pipeline for H-M3 viability classification."""

import json
import pandas as pd
from pathlib import Path

from data_loader import ViabilityCorpusLoader
from classifier import Gate1ViabilityClassifier, RandomBaseline
from evaluator import ClassificationEvaluator
from visualizer import ViabilityVisualizer


def main():
    """Run H-M3 viability classification experiment."""
    print("=" * 60)
    print("H-M3: Gate 1 Viability Classification")
    print("=" * 60)

    # Paths
    results_dir = Path(__file__).parent.parent / "results"
    figures_dir = Path(__file__).parent.parent / "figures"
    results_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)

    # Step 1: Load corpus
    print("\n[1/5] Loading corpus...")
    loader = ViabilityCorpusLoader()
    df = loader.load()
    assert loader.validate_schema(df), "Schema validation failed"
    print(f"  Loaded {len(df)} hypotheses")

    y_true = loader.get_labels(df)
    print(f"  Labels: {y_true.count('viable')} viable, {y_true.count('non-viable')} non-viable")

    # Step 2: Load scaling factor k from H-M1
    print("\n[2/5] Loading scaling factor k from H-M1...")
    k = 1.0  # From H-M1 validation (perfect correlation r=1.000)
    threshold = 0.10
    print(f"  k = {k:.3f}, threshold = {threshold:.1%}")

    # Step 3: Run classifiers
    print("\n[3/5] Running classifiers...")

    # Baseline
    baseline = RandomBaseline(seed=42)
    y_pred_baseline = baseline.predict(len(df))
    print(f"  Baseline predictions: {len(y_pred_baseline)}")

    # Gate 1
    gate1 = Gate1ViabilityClassifier(k=k, threshold=threshold)
    y_pred_gate1, O_preds = gate1.predict_batch(df["O_10"].values)
    print(f"  Gate 1 predictions: {len(y_pred_gate1)}")

    # Step 4: Evaluate
    print("\n[4/5] Evaluating predictions...")
    evaluator = ClassificationEvaluator()
    metrics = evaluator.generate_metrics_dict(y_true, y_pred_baseline, y_pred_gate1)

    print("\n  Baseline Results:")
    print(f"    Accuracy: {metrics['baseline']['accuracy']:.1%} ({metrics['baseline']['n_correct']}/{metrics['baseline']['n_total']})")
    print(f"    Binomial test: p={metrics['baseline']['p_value']:.4f}, significant={metrics['baseline']['significant']}")

    print("\n  Gate 1 Results:")
    print(f"    Accuracy: {metrics['gate1']['accuracy']:.1%} ({metrics['gate1']['n_correct']}/{metrics['gate1']['n_total']})")
    print(f"    Binomial test: p={metrics['gate1']['p_value']:.4f}, significant={metrics['gate1']['significant']}")
    print(f"    Confusion Matrix: TP={metrics['gate1']['confusion_matrix']['TP']}, "
          f"TN={metrics['gate1']['confusion_matrix']['TN']}, "
          f"FP={metrics['gate1']['confusion_matrix']['FP']}, "
          f"FN={metrics['gate1']['confusion_matrix']['FN']}")

    # Step 5: Visualize
    print("\n[5/5] Generating visualizations...")
    visualizer = ViabilityVisualizer(output_dir=figures_dir)
    visualizer.save_all_figures(df, metrics, y_pred_gate1, y_true)
    print(f"  Saved 4 figures to {figures_dir}")

    # Save results
    results_file = results_dir / "metrics.json"
    with open(results_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n  Saved metrics to {results_file}")

    predictions_file = results_dir / "predictions.csv"
    df_out = df.copy()
    df_out["y_true"] = y_true
    df_out["y_pred_baseline"] = y_pred_baseline
    df_out["y_pred_gate1"] = y_pred_gate1
    df_out["O_pred"] = O_preds
    df_out.to_csv(predictions_file, index=False)
    print(f"  Saved predictions to {predictions_file}")

    # Gate verdict
    print("\n" + "=" * 60)
    print("GATE VERDICT")
    print("=" * 60)

    acc_gate1 = metrics["gate1"]["accuracy"]
    p_gate1 = metrics["gate1"]["p_value"]

    if acc_gate1 > 0.80 and p_gate1 < 0.05:
        print("✓ PASS (MUST_WORK gate satisfied)")
        print(f"  Accuracy {acc_gate1:.1%} > 80% threshold")
        print(f"  Binomial test p={p_gate1:.4f} < 0.05 (statistically significant)")
        return "PASS"
    elif acc_gate1 > 0.60:
        print("⚠ PARTIAL (60% < accuracy ≤ 80%)")
        print(f"  Accuracy {acc_gate1:.1%} beats random but below target")
        print("  Recommendation: Investigate per-type threshold calibration")
        return "PARTIAL"
    else:
        print("✗ FAIL (MUST_WORK gate violated)")
        print(f"  Accuracy {acc_gate1:.1%} ≤ 60% threshold")
        print("  Framework doesn't beat random + margin. Core claim unsupported.")
        return "FAIL"


if __name__ == "__main__":
    verdict = main()
    print("\n" + "=" * 60)
    print(f"Experiment complete. Verdict: {verdict}")
    print("=" * 60)
