import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import CONFIG
from edit_metrics import aggregate_edit_metrics

def compute_pass_at_1(results: list[dict], feedback_type: str = None) -> float:
    """Compute pass@1 for results, optionally filtered by feedback_type."""
    filtered = results if feedback_type is None else [r for r in results if r["feedback_type"] == feedback_type]
    if not filtered:
        return 0.0
    return sum(1 for r in filtered if r["passed"]) / len(filtered)

def plot_edit_scope_boxplot(detailed_lines: list[int], binary_lines: list[int], out_path: str):
    """Boxplot comparing lines changed between conditions."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.boxplot([detailed_lines, binary_lines], labels=["Detailed", "Binary"])
    ax.set_ylabel("Lines Changed")
    ax.set_title("Edit Scope by Feedback Type")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  Saved: {out_path}")

def plot_change_ratio_histogram(detailed_ratios: list[float], binary_ratios: list[float], out_path: str):
    """Histogram of change ratios."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(detailed_ratios, bins=20, alpha=0.5, label="Detailed", color="blue")
    ax.hist(binary_ratios, bins=20, alpha=0.5, label="Binary", color="orange")
    ax.set_xlabel("Change Ratio")
    ax.set_ylabel("Frequency")
    ax.set_title("Edit Change Ratio Distribution")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  Saved: {out_path}")

def plot_global_rewrite_bar(metrics: dict, out_path: str):
    """Bar chart of global rewrite rates."""
    fig, ax = plt.subplots(figsize=(8, 6))
    conditions = ["Detailed", "Binary"]
    rates = [metrics["detailed_global_rewrite_rate"], metrics["binary_global_rewrite_rate"]]
    ax.bar(conditions, rates, color=["blue", "orange"])
    ax.set_ylabel("Global Rewrite Rate")
    ax.set_title("Global Rewrite Rate by Feedback Type")
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  Saved: {out_path}")

def main():
    print("H-M2 Evaluation: Edit Scope Analysis\n")

    # Load results
    with open(CONFIG.results_path, "r") as f:
        data = json.load(f)

    results = data["results"]
    edit_records = data.get("edit_records", [])

    # Compute pass@1 per condition
    detailed_pass = compute_pass_at_1(results, "detailed")
    binary_pass = compute_pass_at_1(results, "binary")
    print(f"Pass@1 - Detailed: {detailed_pass:.3f}")
    print(f"Pass@1 - Binary: {binary_pass:.3f}")

    # Aggregate edit metrics
    metrics = aggregate_edit_metrics(edit_records)
    print(f"\nEdit Metrics:")
    print(f"  Detailed avg lines changed: {metrics['detailed_avg_lines_changed']:.2f}")
    print(f"  Binary avg lines changed: {metrics['binary_avg_lines_changed']:.2f}")
    print(f"  Edit scope ratio (d/b): {metrics['edit_scope_ratio']:.3f}")
    print(f"  Detailed global rewrite rate: {metrics['detailed_global_rewrite_rate']:.3f}")
    print(f"  Binary global rewrite rate: {metrics['binary_global_rewrite_rate']:.3f}")
    print(f"  t-test p-value: {metrics['p_value']:.4f}")

    # Gate check: edit_scope_ratio < 0.9 means detailed edits are more targeted
    gate_passed = metrics['edit_scope_ratio'] < 0.9
    print(f"\nGate Check (edit_scope_ratio < 0.9): {'PASS' if gate_passed else 'FAIL'}")

    # Create figures directory
    os.makedirs(CONFIG.figures_dir, exist_ok=True)

    # Generate figures
    print("\nGenerating figures...")
    detailed_recs = [e for e in edit_records if e.get("feedback_type") == "detailed"]
    binary_recs = [e for e in edit_records if e.get("feedback_type") == "binary"]

    detailed_lines = [e["lines_changed"] for e in detailed_recs] if detailed_recs else [0]
    binary_lines = [e["lines_changed"] for e in binary_recs] if binary_recs else [0]
    detailed_ratios = [e["change_ratio"] for e in detailed_recs] if detailed_recs else [0]
    binary_ratios = [e["change_ratio"] for e in binary_recs] if binary_recs else [0]

    plot_edit_scope_boxplot(detailed_lines, binary_lines, os.path.join(CONFIG.figures_dir, "edit_scope_boxplot.png"))
    plot_change_ratio_histogram(detailed_ratios, binary_ratios, os.path.join(CONFIG.figures_dir, "change_ratio_histogram.png"))
    plot_global_rewrite_bar(metrics, os.path.join(CONFIG.figures_dir, "global_rewrite_bar.png"))

    # Save evaluation summary
    summary = {
        "pass_at_1": {
            "detailed": detailed_pass,
            "binary": binary_pass
        },
        "edit_metrics": metrics,
        "gate_check": {
            "criterion": "edit_scope_ratio < 0.9",
            "value": metrics['edit_scope_ratio'],
            "passed": gate_passed
        },
        "mechanism_verified": gate_passed and metrics['detailed_global_rewrite_rate'] < metrics['binary_global_rewrite_rate']
    }

    summary_path = CONFIG.results_path.replace("results.json", "evaluation_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved to {summary_path}")

    return summary

if __name__ == "__main__":
    main()
