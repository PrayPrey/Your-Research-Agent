"""LLM-generated figure script for h-e1 experiment."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

RESULTS_JSONL = Path("docs/youra_research/h-e1/results/results.jsonl")
FIGURES_DIR = Path("docs/youra_research/h-e1/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def load_results():
    results = []
    with open(RESULTS_JSONL) as f:
        for line in f:
            results.append(json.loads(line))
    return results

def fig1_mypy_fraction_by_benchmark(results):
    """Bar chart: fraction of failing solutions with mypy errors per benchmark."""
    from collections import defaultdict
    bm_stats = defaultdict(lambda: {"failing": 0, "mypy_errors": 0})
    for r in results:
        bm = r["benchmark"]
        bm_stats[bm]["failing"] += 1
        if r["has_mypy_error"]:
            bm_stats[bm]["mypy_errors"] += 1

    benchmarks = sorted(bm_stats.keys())
    fractions = [bm_stats[b]["mypy_errors"] / bm_stats[b]["failing"] for b in benchmarks]
    totals_failing = [bm_stats[b]["failing"] for b in benchmarks]

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["#e74c3c" if f < 0.10 else "#2ecc71" for f in fractions]
    bars = ax.bar(benchmarks, fractions, color=colors, width=0.5, edgecolor="black", linewidth=0.8)

    ax.axhline(0.10, color="navy", linestyle="--", linewidth=1.5, label="Gate threshold (10%)")
    ax.set_ylabel("Fraction of failing solutions with mypy errors")
    ax.set_title("H-E1: Mypy Error Fraction in Failing Solutions\n(GPT-4o-mini, temp=0.8, seed=42)")
    ax.set_ylim(0, 1.0)
    ax.legend()

    for bar, frac, n in zip(bars, fractions, totals_failing):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{frac:.0%}\n(n={n})", ha="center", va="bottom", fontsize=11, fontweight="bold")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig1_mypy_fraction_by_benchmark.png", dpi=150)
    plt.close()
    print("Saved fig1_mypy_fraction_by_benchmark.png")

def fig2_error_category_breakdown(results):
    """Bar chart: mypy error category breakdown for HumanEval+."""
    from collections import Counter
    categories = Counter()
    for r in results:
        if r["benchmark"] == "humaneval+" and r["has_mypy_error"]:
            for cat, cnt in r["error_categories"].items():
                if cnt > 0:
                    categories[cat] += cnt

    if not categories:
        print("No error categories to plot.")
        return

    cats = list(categories.keys())
    counts = [categories[c] for c in cats]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(cats, counts, color="#3498db", edgecolor="black", linewidth=0.8)
    ax.set_ylabel("Total error occurrences")
    ax.set_title("H-E1: Mypy Error Categories in HumanEval+ Failing Solutions")

    for i, (cat, cnt) in enumerate(zip(cats, counts)):
        ax.text(i, cnt + 0.3, str(cnt), ha="center", va="bottom", fontweight="bold")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig2_error_category_breakdown.png", dpi=150)
    plt.close()
    print("Saved fig2_error_category_breakdown.png")

def main():
    results = load_results()
    print(f"Loaded {len(results)} failing solution records")
    fig1_mypy_fraction_by_benchmark(results)
    fig2_error_category_breakdown(results)
    print("All figures generated.")

if __name__ == "__main__":
    main()
