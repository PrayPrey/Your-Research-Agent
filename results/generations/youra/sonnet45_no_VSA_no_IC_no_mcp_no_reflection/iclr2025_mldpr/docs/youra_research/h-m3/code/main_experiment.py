"""Main experiment pipeline for h-m3 citation velocity correlation."""
import json
import sys
from pathlib import Path
import pandas as pd
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    H1_RESULTS_PATH, GROUND_TRUTH_PATH, OUTPUT_DIR, FIGURES_DIR,
    BENCHMARKS, TARGET_PRECISION, TARGET_RECALL, DATA_DIR
)
from ground_truth_loader import GroundTruthLoader
from velocity_detector import VelocityDetector
from correlation_detector import CorrelationDetector
from precision_recall_evaluator import PrecisionRecallEvaluator
from visualizer import MetricsVisualizer


def load_saturation_dates(h1_results_path: Path) -> Dict[str, str]:
    """Load saturation dates from h-m1 results."""
    with open(h1_results_path) as f:
        results = json.load(f)
    saturation_dates = {
        benchmark: data['convergence_date']
        for benchmark, data in results['results'].items()
    }
    print(f"Loaded {len(saturation_dates)} saturation dates from h-m1")
    return saturation_dates


def load_citation_data(benchmarks: list, citation_dir: Path) -> Dict[str, pd.DataFrame]:
    """Load citation time series for benchmarks."""
    citation_data = {}
    for benchmark in benchmarks:
        citation_path = citation_dir / f'{benchmark}.json'
        if citation_path.exists():
            with open(citation_path) as f:
                data = json.load(f)
            citation_data[benchmark] = pd.DataFrame(data)
            print(f"Loaded {len(data)} citation records for {benchmark}")
        else:
            print(f"Warning: No citation data for {benchmark}")
    return citation_data


def run_correlation_experiment() -> Dict[str, Any]:
    """Run full h-m3 correlation experiment."""
    print("=" * 60)
    print("h-m3 Citation Velocity Correlation Experiment")
    print("=" * 60)

    # 1. Load saturation dates from h-m1
    saturation_dates = load_saturation_dates(H1_RESULTS_PATH)

    # 2. Load ground truth paradigm shifts
    gt_loader = GroundTruthLoader()
    shift_dates = gt_loader.load_paradigm_shifts(GROUND_TRUTH_PATH)
    print(f"Loaded {len(shift_dates)} paradigm shift dates")

    # 3. Create binary labels
    y_true_dict = gt_loader.create_labels(saturation_dates, shift_dates)
    print(f"Ground truth labels: {y_true_dict}")

    # 4. Initialize detectors
    velocity_detector = VelocityDetector(velocity_window=3, spike_threshold=2.0)
    correlation_detector = CorrelationDetector(saturation_dates, velocity_detector)

    # 5. Load citation data
    citation_dir = DATA_DIR / 'citations'
    citation_data = load_citation_data(BENCHMARKS, citation_dir)

    # 6. Run detection
    print("\n" + "=" * 60)
    print("Running correlation detection...")
    y_pred_dict = correlation_detector.detect_all(BENCHMARKS, citation_data)
    print(f"Predictions: {y_pred_dict}")

    # 7. Compute metrics
    evaluator = PrecisionRecallEvaluator()
    y_true = [y_true_dict[b] for b in BENCHMARKS]
    y_pred = [y_pred_dict[b] for b in BENCHMARKS]
    metrics = evaluator.compute_metrics(y_true, y_pred)

    print("\n" + "=" * 60)
    print("Metrics:")
    print(f"  Precision: {metrics['precision']:.3f}")
    print(f"  Recall: {metrics['recall']:.3f}")
    print(f"  F1-Score: {metrics['f1']:.3f}")
    print(f"  Confusion Matrix: TP={metrics['tp']}, FP={metrics['fp']}, TN={metrics['tn']}, FN={metrics['fn']}")

    # 8. Gate evaluation
    gate_pass = metrics['precision'] >= TARGET_PRECISION and metrics['recall'] >= TARGET_RECALL
    print(f"\nGate Evaluation: {'PASS' if gate_pass else 'FAIL'}")
    print(f"  Target: Precision >= {TARGET_PRECISION}, Recall >= {TARGET_RECALL}")

    # 9. Classification report
    report = evaluator.generate_classification_report(y_true, y_pred)
    print("\nClassification Report:")
    print(report)

    # 10. Visualization
    print("\n" + "=" * 60)
    print("Generating visualizations...")
    visualizer = MetricsVisualizer(FIGURES_DIR)

    # Gate metrics plot
    visualizer.plot_gate_metrics(
        precision=metrics['precision'],
        recall=metrics['recall'],
        baseline_precision=0.0,
        baseline_recall=0.0,
        target_precision=TARGET_PRECISION,
        target_recall=TARGET_RECALL
    )
    print("  - gate_metrics.png")

    # Confusion matrix
    visualizer.plot_confusion_matrix(y_true, y_pred)
    print("  - confusion_matrix.png")

    # Timeline plots
    for benchmark in BENCHMARKS:
        if benchmark in citation_data and benchmark in saturation_dates:
            velocity_series = velocity_detector.compute_velocity(citation_data[benchmark])
            shift_date = shift_dates.get(benchmark)
            visualizer.plot_citation_velocity_timeline(
                benchmark=benchmark,
                citations_df=citation_data[benchmark],
                velocity_series=velocity_series,
                saturation_date=saturation_dates[benchmark],
                shift_date=shift_date
            )
            print(f"  - timeline_{benchmark}.png")

    # 11. Save results
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

    # Save predictions
    predictions_df = pd.DataFrame([
        {
            'benchmark': b,
            'saturation_date': saturation_dates.get(b),
            'shift_date': shift_dates.get(b),
            'ground_truth': y_true_dict.get(b),
            'prediction': y_pred_dict.get(b)
        }
        for b in BENCHMARKS
    ])
    predictions_path = OUTPUT_DIR / 'predictions.csv'
    predictions_df.to_csv(predictions_path, index=False)
    print(f"\nSaved predictions to {predictions_path}")

    # Save metrics
    metrics['gate_pass'] = gate_pass
    metrics_path = OUTPUT_DIR / 'metrics.json'
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {metrics_path}")

    print("\n" + "=" * 60)
    print("Experiment complete!")
    print("=" * 60)

    return {
        'predictions': y_pred_dict,
        'metrics': metrics,
        'gate_pass': gate_pass
    }


if __name__ == '__main__':
    result = run_correlation_experiment()
    sys.exit(0 if result['gate_pass'] else 1)
