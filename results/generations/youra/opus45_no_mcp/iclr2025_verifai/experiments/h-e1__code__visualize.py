"""A-8: Visualization suite."""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from pathlib import Path

def plot_gate_metrics(results: dict, path: str, gate: float = 0.3) -> None:
    """Bar chart: threshold vs actual mean Jaccard."""
    fig, ax = plt.subplots(figsize=(8, 6))
    values = [gate, results["mean_jaccard"]]
    labels = ["Threshold", "Actual"]
    colors = ["#2ecc71" if results["mean_jaccard"] < gate else "#e74c3c", "#3498db"]
    ax.bar(labels, values, color=colors[::-1])
    ax.axhline(y=gate, color='red', linestyle='--', label=f'Gate: {gate}')
    ax.set_ylabel("Jaccard Similarity")
    ax.set_title(f"H-E1 Gate: Mean Jaccard < {gate}")
    ax.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

def plot_jaccard_histogram(results: dict, path: str) -> None:
    """Histogram of Jaccard scores."""
    fig, ax = plt.subplots(figsize=(10, 6))
    scores = results.get("jaccard_scores", [])
    ax.hist(scores, bins=30, edgecolor='black', alpha=0.7)
    ax.axvline(x=0.3, color='red', linestyle='--', label='Gate (0.3)')
    ax.axvline(x=results["mean_jaccard"], color='blue', linestyle='-', label=f'Mean ({results["mean_jaccard"]:.3f})')
    ax.set_xlabel("Jaccard Similarity")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Jaccard Similarity Scores")
    ax.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

def plot_category_breakdown(results: dict, path: str) -> None:
    """Stacked bar: category counts."""
    fig, ax = plt.subplots(figsize=(10, 6))
    categories = ["static_only", "exec_only", "both", "neither"]
    counts = [results.get(c, 0) for c in categories]
    colors = ["#3498db", "#e74c3c", "#9b59b6", "#95a5a6"]
    ax.bar(categories, counts, color=colors)
    ax.set_xlabel("Error Category")
    ax.set_ylabel("Problem Count")
    ax.set_title("Error Category Distribution")
    for i, v in enumerate(counts):
        ax.text(i, v + 5, str(v), ha='center')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

def plot_per_benchmark(results: dict, path: str) -> None:
    """Jaccard distribution by benchmark."""
    fig, ax = plt.subplots(figsize=(10, 6))
    per_problem = results.get("per_problem", [])
    he_scores = [p["jaccard"] for p in per_problem if p.get("benchmark") == "humaneval"]
    mb_scores = [p["jaccard"] for p in per_problem if p.get("benchmark") == "mbpp"]

    ax.boxplot([he_scores, mb_scores], tick_labels=["HumanEval+", "MBPP+"])
    ax.axhline(y=0.3, color='red', linestyle='--', label='Gate (0.3)')
    ax.set_ylabel("Jaccard Similarity")
    ax.set_title("Jaccard Distribution by Benchmark")
    ax.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

def generate_all_figures(results: dict, figures_dir: str) -> None:
    """Generate all figures."""
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    plot_gate_metrics(results, f"{figures_dir}/gate_metrics.png")
    plot_jaccard_histogram(results, f"{figures_dir}/jaccard_histogram.png")
    plot_category_breakdown(results, f"{figures_dir}/category_breakdown.png")
    plot_per_benchmark(results, f"{figures_dir}/per_benchmark.png")
    print(f"Figures saved to {figures_dir}")
