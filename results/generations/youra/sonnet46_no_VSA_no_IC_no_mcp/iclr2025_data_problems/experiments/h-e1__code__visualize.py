"""E5: 4-panel visualization of Pile vs dedup-Pile benchmark comparison."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

BASE_DIR = Path(__file__).parent.parent
MATRIX_FILE = BASE_DIR / "results_matrix.json"
STATS_FILE = BASE_DIR / "statistical_results.json"
FIGURES_DIR = BASE_DIR / "figures"

SIZES = ["160m", "410m", "1b", "6.9b"]
BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
CORRECTED_ALPHA = 0.0125


def sig_stars(p_value) -> str:
    if p_value is None:
        return ""
    if p_value < 0.001:
        return "***"
    if p_value < 0.01:
        return "**"
    if p_value < CORRECTED_ALPHA:
        return "*"
    return ""


def plot_differential_bar(matrix: dict, stats: dict, out: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(BENCHMARKS))
    width = 0.18
    colors = plt.cm.tab10(np.linspace(0, 0.6, len(SIZES)))

    for i, size in enumerate(SIZES):
        diffs = []
        for bench in BENCHMARKS:
            p = matrix.get(size, {}).get("pile", {}).get(bench)
            d = matrix.get(size, {}).get("dedup", {}).get(bench)
            diffs.append((d - p) if (p is not None and d is not None) else 0.0)
        offset = (i - len(SIZES) / 2 + 0.5) * width
        bars = ax.bar(x + offset, diffs, width, label=size, color=colors[i], alpha=0.85)

    # Significance markers per benchmark
    for j, bench in enumerate(BENCHMARKS):
        r = stats.get(bench, {})
        stars = sig_stars(r.get("p_value"))
        if stars:
            ax.text(j, ax.get_ylim()[1] * 0.95 if ax.get_ylim()[1] > 0 else 0.01,
                    stars, ha="center", va="bottom", fontsize=13, color="crimson")

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([b.replace("_", "\n") for b in BENCHMARKS])
    ax.set_ylabel("Δ Accuracy (dedup − pile)")
    ax.set_title("Dedup vs Pile Accuracy Difference per Benchmark\n(* p<0.0125 Bonferroni)")
    ax.legend(title="Model size", fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


def plot_scaling(matrix: dict, out: str) -> None:
    fig, axes = plt.subplots(1, len(BENCHMARKS), figsize=(14, 4), sharey=False)
    size_labels = [s.upper() for s in SIZES]
    x = np.arange(len(SIZES))

    for ax, bench in zip(axes, BENCHMARKS):
        pile_accs = [matrix.get(s, {}).get("pile", {}).get(bench) or 0 for s in SIZES]
        dedup_accs = [matrix.get(s, {}).get("dedup", {}).get(bench) or 0 for s in SIZES]
        ax.plot(x, pile_accs, "o-", label="Pile", color="steelblue")
        ax.plot(x, dedup_accs, "s--", label="dedup-Pile", color="darkorange")
        ax.set_xticks(x)
        ax.set_xticklabels(size_labels, fontsize=7)
        ax.set_title(bench.replace("_", "\n"), fontsize=9)
        ax.set_xlabel("Model size")
        ax.set_ylabel("Accuracy")
        ax.legend(fontsize=7)

    fig.suptitle("Accuracy Scaling: Pile vs dedup-Pile", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


def plot_paired_scatter(matrix: dict, out: str) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(8, 8))
    axes = axes.flatten()

    for ax, bench in zip(axes, BENCHMARKS):
        pile_accs = []
        dedup_accs = []
        for size in SIZES:
            p = matrix.get(size, {}).get("pile", {}).get(bench)
            d = matrix.get(size, {}).get("dedup", {}).get(bench)
            if p is not None and d is not None:
                pile_accs.append(p)
                dedup_accs.append(d)

        ax.scatter(pile_accs, dedup_accs, zorder=3, s=60)
        for i, size in enumerate(SIZES):
            if i < len(pile_accs):
                ax.annotate(size, (pile_accs[i], dedup_accs[i]), fontsize=7,
                            xytext=(3, 3), textcoords="offset points")

        all_vals = pile_accs + dedup_accs
        if all_vals:
            lo, hi = min(all_vals) * 0.98, max(all_vals) * 1.02
            ax.plot([lo, hi], [lo, hi], "k--", linewidth=0.8, alpha=0.5, label="y=x")
        ax.set_xlabel("Pile accuracy")
        ax.set_ylabel("dedup-Pile accuracy")
        ax.set_title(bench.replace("_", " "))
        ax.legend(fontsize=7)

    fig.suptitle("Paired Scatter: Pile vs dedup-Pile per Benchmark", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


def plot_pvalue_heatmap(stats: dict, out: str) -> None:
    # Build p-value matrix: rows=benchmarks, cols=n/a (only 1 p-value per benchmark from paired t-test)
    # Use horizontal bar chart of -log10(p) instead
    fig, ax = plt.subplots(figsize=(7, 4))
    pvals = []
    labels = []
    for bench in BENCHMARKS:
        r = stats.get(bench, {})
        p = r.get("p_value")
        if p is not None:
            pvals.append(-np.log10(max(p, 1e-10)))
            labels.append(bench.replace("_", " "))

    colors = ["crimson" if p >= -np.log10(CORRECTED_ALPHA) else "steelblue" for p in pvals]
    ax.barh(labels, pvals, color=colors, alpha=0.85)
    ax.axvline(-np.log10(CORRECTED_ALPHA), color="red", linestyle="--",
               linewidth=1.2, label=f"Bonferroni α={CORRECTED_ALPHA}")
    ax.set_xlabel("-log₁₀(p-value)")
    ax.set_title("Statistical Significance by Benchmark\n(red = significant)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    matrix = json.loads(MATRIX_FILE.read_text())
    stats = json.loads(STATS_FILE.read_text())

    print("Generating figures...")
    plot_differential_bar(matrix, stats, str(FIGURES_DIR / "differential_bar.png"))
    plot_scaling(matrix, str(FIGURES_DIR / "scaling_plot.png"))
    plot_paired_scatter(matrix, str(FIGURES_DIR / "paired_scatter.png"))
    plot_pvalue_heatmap(stats, str(FIGURES_DIR / "pvalue_heatmap.png"))
    print("Done.")


if __name__ == "__main__":
    main()
