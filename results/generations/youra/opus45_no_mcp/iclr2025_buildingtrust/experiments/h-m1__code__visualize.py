"""A-8: Visualization - Gate chart, step histogram, example comparison, pattern pie"""
import json
import os
import random
import matplotlib.pyplot as plt
from config import CONFIG


def plot_gate_metrics(baseline_rate: float, cot_rate: float, out_dir: str) -> None:
    """Bar chart: baseline vs CoT reasoning_presence_rate."""
    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(["Baseline", "CoT"], [baseline_rate, cot_rate], color=["#3498db", "#2ecc71"])
    ax.axhline(y=0.90, color="red", linestyle="--", label="Threshold (0.90)")
    ax.set_ylabel("Reasoning Presence Rate")
    ax.set_title("H-M1: Reasoning Chain Detection Rate")
    ax.set_ylim(0, 1.1)
    ax.legend()

    for bar, val in zip(bars, [baseline_rate, cot_rate]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", va="bottom", fontsize=12)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "gate_metrics.png"), dpi=150)
    plt.close()


def plot_step_count_histogram(cot_results: list[dict], out_dir: str) -> None:
    """Histogram of step_count across CoT results."""
    step_counts = [r["step_count"] for r in cot_results]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(step_counts, bins=range(0, max(step_counts) + 2), edgecolor="black", alpha=0.7, color="#9b59b6")
    ax.axvline(x=2.0, color="red", linestyle="--", label="Threshold (2.0)")
    ax.set_xlabel("Number of Reasoning Steps")
    ax.set_ylabel("Count")
    ax.set_title("H-M1: Distribution of CoT Reasoning Steps")
    ax.legend()

    mean_steps = sum(step_counts) / len(step_counts)
    ax.axvline(x=mean_steps, color="green", linestyle=":", label=f"Mean ({mean_steps:.2f})")
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "step_count_histogram.png"), dpi=150)
    plt.close()


def plot_example_comparison(baseline_results: list[dict], cot_results: list[dict], out_dir: str) -> None:
    """Side-by-side text panel: 3 example question/baseline/cot triples."""
    random.seed(42)
    indices = random.sample(range(len(baseline_results)), 3)

    fig, axes = plt.subplots(3, 1, figsize=(14, 18))

    for ax, idx in zip(axes, indices):
        question = baseline_results[idx]["question"]
        baseline_out = baseline_results[idx]["raw_output"][:300] + "..." if len(baseline_results[idx]["raw_output"]) > 300 else baseline_results[idx]["raw_output"]
        cot_out = cot_results[idx]["raw_output"][:500] + "..." if len(cot_results[idx]["raw_output"]) > 500 else cot_results[idx]["raw_output"]

        text = f"Question: {question}\n\n--- Baseline ---\n{baseline_out}\n\n--- CoT ---\n{cot_out}"
        ax.text(0.02, 0.98, text, transform=ax.transAxes, fontsize=8, verticalalignment="top",
                fontfamily="monospace", wrap=True)
        ax.axis("off")
        ax.set_title(f"Example {idx + 1}", fontsize=10, loc="left")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "example_comparison.png"), dpi=150)
    plt.close()


def plot_pattern_breakdown(cot_results: list[dict], out_dir: str) -> None:
    """Pie chart: numbered/ordinal/logical pattern frequency across CoT results."""
    counts = {"numbered": 0, "ordinal": 0, "logical": 0}

    for r in cot_results:
        patterns = r["patterns"]
        for key in counts:
            if patterns.get(key, False):
                counts[key] += 1

    fig, ax = plt.subplots(figsize=(8, 6))

    labels = list(counts.keys())
    sizes = list(counts.values())
    colors = ["#e74c3c", "#3498db", "#2ecc71"]
    explode = (0.05, 0.05, 0.05)

    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct="%1.1f%%",
           shadow=True, startangle=90)
    ax.set_title("H-M1: Reasoning Pattern Breakdown in CoT Outputs")
    ax.axis("equal")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "pattern_breakdown.png"), dpi=150)
    plt.close()


def main():
    with open(CONFIG.paths.results_file) as f:
        results = json.load(f)

    os.makedirs(CONFIG.paths.figures_dir, exist_ok=True)

    baseline_rate = results["baseline_metrics"]["reasoning_presence_rate"]
    cot_rate = results["cot_metrics"]["reasoning_presence_rate"]

    print("Generating gate_metrics.png...")
    plot_gate_metrics(baseline_rate, cot_rate, CONFIG.paths.figures_dir)

    print("Generating step_count_histogram.png...")
    plot_step_count_histogram(results["cot"], CONFIG.paths.figures_dir)

    print("Generating example_comparison.png...")
    plot_example_comparison(results["baseline"], results["cot"], CONFIG.paths.figures_dir)

    print("Generating pattern_breakdown.png...")
    plot_pattern_breakdown(results["cot"], CONFIG.paths.figures_dir)

    print(f"All figures saved to: {CONFIG.paths.figures_dir}")


if __name__ == "__main__":
    main()
