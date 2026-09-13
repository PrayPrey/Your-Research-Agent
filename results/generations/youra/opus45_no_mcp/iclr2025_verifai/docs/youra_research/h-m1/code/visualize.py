"""H-M1: Visualization for structural error analysis."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

def generate_all_figures(results: dict, figures_dir: str) -> None:
    """Generate 3 figures for H-M1 analysis."""
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    cov = results.get("coverage", {})
    dist = results.get("category_distribution", {})
    breakdown = results.get("per_benchmark", {})
    gate = results.get("gate", {})

    # 1. Gate metrics bar chart
    fig, ax = plt.subplots(figsize=(8, 6))
    metric = cov.get("structural_coverage", 0)
    threshold = gate.get("threshold", 0.60)
    ax.bar(["Structural Coverage"], [metric], color="steelblue", label="Measured")
    ax.axhline(y=threshold, color="red", linestyle="--", label=f"Threshold ({threshold:.0%})")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Coverage")
    ax.set_title("H-M1: Structural Coverage vs Gate Threshold")
    ax.legend()
    plt.tight_layout()
    plt.savefig(Path(figures_dir) / "gate_metrics.png", dpi=150)
    plt.close()

    # 2. Category distribution pie chart
    if dist:
        fig, ax = plt.subplots(figsize=(8, 8))
        labels = list(dist.keys())
        sizes = list(dist.values())
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title("H-M1: Structural Error Category Distribution")
        plt.tight_layout()
        plt.savefig(Path(figures_dir) / "category_breakdown.png", dpi=150)
        plt.close()

    # 3. Per-benchmark bar chart
    if breakdown:
        fig, ax = plt.subplots(figsize=(8, 6))
        benchmarks = list(breakdown.keys())
        coverages = [breakdown[b].get("structural_coverage", 0) for b in benchmarks]
        ax.bar(benchmarks, coverages, color=["steelblue", "coral"])
        ax.axhline(y=threshold, color="red", linestyle="--", label="Threshold")
        ax.set_ylim(0, 1)
        ax.set_ylabel("Structural Coverage")
        ax.set_title("H-M1: Per-Benchmark Structural Coverage")
        ax.legend()
        plt.tight_layout()
        plt.savefig(Path(figures_dir) / "per_benchmark.png", dpi=150)
        plt.close()

    print(f"Figures saved to {figures_dir}")
