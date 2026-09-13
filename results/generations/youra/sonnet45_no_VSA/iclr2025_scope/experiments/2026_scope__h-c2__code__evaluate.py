"""
Evaluation and Visualization for H-C2
Generates charts and analysis
"""

import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import numpy as np
from pathlib import Path

from config import CONFIG


def load_results(results_path: str = "experiment_results.json"):
    """Load experiment results from JSON."""
    with open(results_path, 'r') as f:
        return json.load(f)


def generate_detection_chart(results: dict, output_path: Path):
    """Generate detection rate comparison chart."""
    summary = results["summary"]

    methods = ['Baseline\n(End-to-End)', 'H-C2\n(Contracts)']
    detection_rates = [
        summary["baseline_detection_rate"] * 100,
        summary["h_c2_detection_rate"] * 100
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(methods, detection_rates, color=['#FFA500', '#45B7D1'], width=0.6)

    # Add threshold line
    threshold = CONFIG["detection_rate_threshold"] * 100
    ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2,
               label=f'SHOULD_WORK Threshold ({threshold:.0f}%)')

    # Add value labels on bars
    for bar, rate in zip(bars, detection_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{rate:.1f}%',
                ha='center', va='bottom', fontsize=14, fontweight='bold')

    ax.set_ylabel('Detection Rate (%)', fontsize=12)
    ax.set_title('H-C2 Cross-Framework Contract Validation\nDetection Rate Comparison', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


def generate_contract_breakdown(results: dict, output_path: Path):
    """Generate per-contract detection breakdown."""
    summary = results["summary"]
    contract_data = summary["per_contract_detection"]

    contracts = [
        'Dtype\nPreservation',
        'Shape\nConsistency',
        'Numerical\nTolerance'
    ]
    rates = [
        contract_data.get("dtype_preserved", 0) * 100,
        contract_data.get("shape_consistent", 0) * 100,
        contract_data.get("numerical_tolerance", 0) * 100
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(contracts, rates, color=['#FF6B6B', '#4ECDC4', '#95E1D3'], width=0.6)

    # Add value labels
    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{rate:.1f}%',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel('Detection Rate (%)', fontsize=12)
    ax.set_title('Per-Contract Detection Breakdown', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


def generate_confusion_matrix(results: dict, output_path: Path):
    """Generate confusion matrix for H-C2."""
    test_results = results["test_results"]

    # Calculate confusion matrix
    tp = sum(1 for r in test_results if r["ground_truth"] == "defect" and r["h_c2_detected"])
    fp = sum(1 for r in test_results if r["ground_truth"] == "valid" and r["h_c2_detected"])
    tn = sum(1 for r in test_results if r["ground_truth"] == "valid" and not r["h_c2_detected"])
    fn = sum(1 for r in test_results if r["ground_truth"] == "defect" and not r["h_c2_detected"])

    confusion = np.array([[tp, fn], [fp, tn]])

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(confusion, cmap='Blues', aspect='auto')

    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Count', rotation=-90, va="bottom")

    # Add labels
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Detected', 'Not Detected'])
    ax.set_yticklabels(['Defect', 'Valid'])
    ax.set_xlabel('Predicted', fontsize=12)
    ax.set_ylabel('Ground Truth', fontsize=12)
    ax.set_title('H-C2 Confusion Matrix', fontsize=14, fontweight='bold')

    # Add text annotations
    for i in range(2):
        for j in range(2):
            text = ax.text(j, i, str(confusion[i, j]),
                          ha="center", va="center", color="black",
                          fontsize=20, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


def generate_validation_time_distribution(results: dict, output_path: Path):
    """Generate validation time distribution."""
    test_results = results["test_results"]
    times = [r["h_c2_validation_time"] * 1000 for r in test_results]  # Convert to ms

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(times, bins=20, color='#45B7D1', edgecolor='black', alpha=0.7)

    # Add statistics
    mean_time = np.mean(times)
    median_time = np.median(times)
    p95_time = np.percentile(times, 95)

    ax.axvline(mean_time, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_time:.2f}ms')
    ax.axvline(median_time, color='green', linestyle='--', linewidth=2, label=f'Median: {median_time:.2f}ms')
    ax.axvline(p95_time, color='orange', linestyle='--', linewidth=2, label=f'P95: {p95_time:.2f}ms')

    ax.set_xlabel('Validation Time (ms)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('H-C2 Validation Time Distribution', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


def main():
    """Generate all visualizations."""
    print("Generating visualizations...")

    # Load results
    results = load_results(CONFIG["results_path"])

    # Create figures directory
    figures_dir = Path(CONFIG["figures_dir"])
    figures_dir.mkdir(exist_ok=True)

    # Generate charts
    generate_detection_chart(results, figures_dir / "detection_rate_comparison.png")
    generate_contract_breakdown(results, figures_dir / "contract_breakdown.png")
    generate_confusion_matrix(results, figures_dir / "confusion_matrix.png")
    generate_validation_time_distribution(results, figures_dir / "validation_time_distribution.png")

    print("\n✓ All visualizations generated successfully")


if __name__ == "__main__":
    main()
