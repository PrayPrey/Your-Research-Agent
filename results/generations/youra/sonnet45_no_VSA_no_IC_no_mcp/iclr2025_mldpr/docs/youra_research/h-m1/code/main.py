from pathlib import Path
import json
from src.clients import HuggingFaceClient, PapersWithCodeClient, GitHubClient
from src.metrics import HealthMetricsComputer
from src.collector import DataCollector
from src.validator import GroundTruthTracker
from src.evaluator import HealthMetricsEvaluator
from src.visualize import HealthMetricsVisualizer
from src.config import HEALTH_METRICS_CONFIG
import pandas as pd


def main():
    base_dir = Path(__file__).parent

    print("Step 1: Setup API clients")
    hf = HuggingFaceClient(HEALTH_METRICS_CONFIG["api"]["hf_cache_dir"])
    pwc = PapersWithCodeClient(HEALTH_METRICS_CONFIG["api"]["pwc_cache_dir"], hf_client=hf)
    gh = GitHubClient(cache_dir=HEALTH_METRICS_CONFIG["api"]["gh_cache_dir"], hf_client=hf)

    print("Step 2: Get dataset list")
    dataset_ids = hf.list_active_datasets(limit=HEALTH_METRICS_CONFIG["data"]["dataset_sample_size"])
    repos = [f"org/{ds}" for ds in dataset_ids]

    print("Step 3: Month 0 snapshot")
    tracker = GroundTruthTracker(hf, base_dir / HEALTH_METRICS_CONFIG["data"]["output_dir"])
    month0_snapshot = tracker.snapshot_dataset_status(dataset_ids, month=0)
    tracker.save_snapshot(month0_snapshot, str(base_dir / "data/month0_snapshot.json"))

    print("Step 4: Collect data")
    collector = DataCollector(hf, pwc, gh, base_dir / HEALTH_METRICS_CONFIG["data"]["output_dir"])
    raw_data = collector.collect_batch(dataset_ids, repos)
    collector.save_collected_data(raw_data, str(base_dir / "data/raw_data.json"))

    print("Step 5: Compute metrics")
    computer = HealthMetricsComputer(
        velocity_threshold=HEALTH_METRICS_CONFIG["metrics"]["velocity_threshold"],
        emergence_threshold=HEALTH_METRICS_CONFIG["metrics"]["emergence_threshold"],
        issue_threshold=HEALTH_METRICS_CONFIG["metrics"]["issue_threshold"]
    )

    metrics_list = []
    for item in raw_data:
        metrics = computer.compute_all_metrics(
            item["download_history"],
            item["successors"],
            item["issues"]
        )
        metrics["dataset_id"] = item["dataset_id"]
        metrics_list.append(metrics)

    metrics_df = pd.DataFrame(metrics_list)
    metrics_df.to_csv(base_dir / "data/health_metrics.csv", index=False)

    print("Step 6: Flag top K candidates")
    flagged_count = metrics_df['flagged'].sum()
    print(f"  Flagged {flagged_count} deprecation candidates")

    print("Step 7: Month 6 snapshot (simulated)")
    month6_snapshot = tracker.snapshot_dataset_status(dataset_ids, month=6)
    tracker.save_snapshot(month6_snapshot, str(base_dir / "data/month6_snapshot.json"))

    print("Step 8: Compute ground truth")
    ground_truth = tracker.compute_deprecation_events(month0_snapshot, month6_snapshot)
    with open(base_dir / "data/ground_truth.json", 'w') as f:
        json.dump(ground_truth, f, indent=2)
    actual_deprecations = sum(ground_truth.values())
    print(f"  Actual deprecations: {actual_deprecations}")

    print("Step 9: Evaluate")
    evaluator = HealthMetricsEvaluator(
        str(base_dir / "data/health_metrics.csv"),
        str(base_dir / "data/ground_truth.json")
    )
    report = evaluator.generate_report()

    print("Step 10: Visualize")
    viz = HealthMetricsVisualizer(base_dir / HEALTH_METRICS_CONFIG["visualization"]["figures_dir"])
    viz.plot_gate_metrics(report)
    viz.plot_health_metrics_distribution(metrics_df)
    viz.plot_confusion_matrix(report["confusion_matrix"])
    viz.plot_threshold_sensitivity(metrics_df, ground_truth)
    viz.plot_deprecation_timeline(ground_truth)

    print("Step 11: Save report")
    report_path = base_dir / "evaluation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Gate Status: {report['gate_status']}")
    print(f"  Precision: {report['precision']:.3f} (target: 0.600, {'PASS' if report['precision_pass'] else 'FAIL'})")
    print(f"  Recall: {report['recall']:.3f} (target: 0.800, {'PASS' if report['recall_pass'] else 'FAIL'})")
    print(f"\nConfusion Matrix:")
    cm = report['confusion_matrix']
    print(f"  TP: {cm['tp']}, FP: {cm['fp']}, FN: {cm['fn']}, TN: {cm['tn']}")
    print(f"\nReport: {report_path}")
    print(f"Figures: {base_dir / HEALTH_METRICS_CONFIG['visualization']['figures_dir']}")
    print(f"{'='*60}")
    print("EXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
