"""Figure generation for H-M3 repair loop experiment."""
import json
import os
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

CATEGORY_ORDER = ["pyright", "execution", "mypy", "z3"]
CATEGORY_LABELS = {
    "pyright": "Pyright\n(static, rank 1)",
    "execution": "Execution\n(monitoring, rank 2)",
    "mypy": "Mypy\n(type check, rank 3)",
    "z3": "Z3 SMT\n(formal, rank 4)",
}
COLORS = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0"]


def _ordered_cats(iter_rates: dict) -> list:
    return [c for c in CATEGORY_ORDER if c in iter_rates]


def plot_bar_iter1_rate(iter_rates: dict, figures_dir: str) -> None:
    cats = _ordered_cats(iter_rates)
    rates = [iter_rates[c]["iter1_rate"] for c in cats]
    ci_lo = [iter_rates[c].get("iter1_ci_lo", 0) for c in cats]
    ci_hi = [iter_rates[c].get("iter1_ci_hi", 0) for c in cats]
    errors = [[r - lo for r, lo in zip(rates, ci_lo)],
               [hi - r for r, hi in zip(rates, ci_hi)]]
    labels = [CATEGORY_LABELS.get(c, c) for c in cats]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, rates, color=COLORS[:len(cats)], alpha=0.85, edgecolor="black", linewidth=0.8)
    ax.errorbar(range(len(cats)), rates, yerr=errors, fmt="none", color="black", capsize=5, linewidth=1.5)
    ax.set_ylabel("Iteration-1 Repair Success Rate", fontsize=12)
    ax.set_xlabel("Feedback Category (ordered by H-M2 specificity rank)", fontsize=11)
    ax.set_title("H-M3: Per-Category Iteration-1 Repair Success Rate\n(Higher specificity rank = higher bar predicted)", fontsize=13)
    ax.set_ylim(0, min(1.0, max(rates) * 1.3 + 0.1))
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{rate:.3f}", ha="center", va="bottom", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "bar_iter1_rate.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved bar_iter1_rate.png")


def plot_line_cumulative_repair(results: list, figures_dir: str) -> None:
    """Cumulative repair rate across iterations 1-3 per category."""
    by_cat = defaultdict(list)
    for r in results:
        by_cat[r.category].append(r)

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, cat in enumerate(CATEGORY_ORDER):
        if cat not in by_cat:
            continue
        recs = by_cat[cat]
        n = len(recs)
        cum_rates = []
        for it in range(1, 4):
            passes = sum(1 for r in recs if (
                (it == 1 and r.iter1_pass) or
                (it == 2 and r.iter2_pass) or
                (it == 3 and r.iter3_pass)
            ))
            # Cumulative: include passes from earlier iters
            all_passes = sum(1 for r in recs if r.iterations_to_pass is not None and r.iterations_to_pass <= it)
            cum_rates.append(all_passes / n if n > 0 else 0)
        ax.plot([1, 2, 3], cum_rates, marker="o", label=CATEGORY_LABELS.get(cat, cat),
                color=COLORS[i], linewidth=2)

    ax.set_xlabel("Repair Iteration", fontsize=12)
    ax.set_ylabel("Cumulative Repair Success Rate", fontsize=12)
    ax.set_title("H-M3: Cumulative Repair Rate by Iteration and Feedback Category", fontsize=13)
    ax.set_xticks([1, 2, 3])
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1.05)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "line_cumulative_repair.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved line_cumulative_repair.png")


def plot_heatmap_mean_iterations(results: list, figures_dir: str) -> None:
    """Heatmap: bug_type × category of mean iterations to first pass."""
    bug_types = sorted(set(r.bug_type for r in results))
    cats = [c for c in CATEGORY_ORDER if any(r.category == c for r in results)]

    data = np.full((len(bug_types), len(cats)), np.nan)
    for i, bt in enumerate(bug_types):
        for j, cat in enumerate(cats):
            recs = [r for r in results if r.bug_type == bt and r.category == cat and r.iterations_to_pass is not None]
            if recs:
                data[i, j] = np.mean([r.iterations_to_pass for r in recs])

    fig, ax = plt.subplots(figsize=(max(8, len(cats) * 2), max(6, len(bug_types) * 0.6 + 2)))
    mask = np.isnan(data)
    sns.heatmap(data, annot=True, fmt=".2f", mask=mask, ax=ax,
                xticklabels=[CATEGORY_LABELS.get(c, c).replace("\n", " ") for c in cats],
                yticklabels=bug_types, cmap="YlOrRd_r",
                vmin=1, vmax=3, cbar_kws={"label": "Mean Iterations to Pass"})
    ax.set_title("H-M3: Mean Iterations to First Pass (Bug Type × Feedback Category)", fontsize=12)
    ax.set_xlabel("Feedback Category")
    ax.set_ylabel("Bug Type")
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "heatmap_mean_iterations.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved heatmap_mean_iterations.png")


def plot_scatter_length_vs_rate(iter_rates: dict, figures_dir: str) -> None:
    """Scatter: H-M2 char_count vs iter1_rate per category with regression."""
    from src.analyze import H_M2_CHAR_COUNTS
    cats = [c for c in CATEGORY_ORDER if c in iter_rates]
    x = [H_M2_CHAR_COUNTS.get(c, 0) for c in cats]
    y = [iter_rates[c]["iter1_rate"] for c in cats]

    fig, ax = plt.subplots(figsize=(8, 6))
    for i, (cat, xi, yi) in enumerate(zip(cats, x, y)):
        ax.scatter(xi, yi, color=COLORS[i], s=120, zorder=3, label=cat)
        ax.annotate(cat, (xi, yi), textcoords="offset points", xytext=(8, 4), fontsize=10)

    if len(x) >= 2:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        xline = np.linspace(min(x) * 0.8, max(x) * 1.1, 100)
        ax.plot(xline, p(xline), "k--", alpha=0.5, label="Regression")

    ax.set_xlabel("Mean Feedback Length (chars, from H-M2)", fontsize=12)
    ax.set_ylabel("Iteration-1 Repair Success Rate", fontsize=12)
    ax.set_title("H-M3: Feedback Specificity vs Repair Success\n(Expects positive correlation)", fontsize=12)
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "scatter_length_vs_rate.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved scatter_length_vs_rate.png")


def plot_scatter_z3_subgroup(results: list, figures_dir: str) -> None:
    """Z3 subgroup scatter — small N with annotation."""
    z3_results = [r for r in results if r.category == "z3"]
    cats_present = {r.category for r in results}
    from src.analyze import SPECIFICITY_RANKS

    fig, ax = plt.subplots(figsize=(8, 6))
    for i, cat in enumerate(CATEGORY_ORDER):
        cat_res = [r for r in z3_results] if cat == "z3" else []
        all_cat = [r for r in results if r.category == cat and r.problem_id in {r2.problem_id for r2 in z3_results}]
        if not all_cat:
            continue
        rate = np.mean([r.iter1_pass for r in all_cat])
        ax.scatter(SPECIFICITY_RANKS[cat], rate, color=COLORS[i], s=100, label=cat)
        ax.annotate(f"{cat}\n(n={len(all_cat)})", (SPECIFICITY_RANKS[cat], rate),
                    textcoords="offset points", xytext=(8, 4), fontsize=9)

    ax.set_xlabel("Specificity Rank (H-M2)", fontsize=12)
    ax.set_ylabel("Iter-1 Repair Rate (Z3-subset problems)", fontsize=12)
    ax.set_title(f"H-M3: Z3 Subgroup Analysis (n≈8 problems)\n(Low N — supplementary; interpret with caution)", fontsize=11)
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(["pyright\n(1)", "execution\n(2)", "mypy\n(3)", "z3\n(4)"])
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "scatter_z3_subgroup.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved scatter_z3_subgroup.png")


def generate_all_figures(iter_rates: dict, results: list, figures_dir: str) -> None:
    os.makedirs(figures_dir, exist_ok=True)
    print("Generating figures...")
    try:
        plot_bar_iter1_rate(iter_rates, figures_dir)
    except Exception as e:
        print(f"  Warning: bar_iter1_rate failed: {e}")
    try:
        plot_line_cumulative_repair(results, figures_dir)
    except Exception as e:
        print(f"  Warning: line_cumulative_repair failed: {e}")
    try:
        plot_heatmap_mean_iterations(results, figures_dir)
    except Exception as e:
        print(f"  Warning: heatmap_mean_iterations failed: {e}")
    try:
        plot_scatter_length_vs_rate(iter_rates, figures_dir)
    except Exception as e:
        print(f"  Warning: scatter_length_vs_rate failed: {e}")
    try:
        plot_scatter_z3_subgroup(results, figures_dir)
    except Exception as e:
        print(f"  Warning: scatter_z3_subgroup failed: {e}")
    print("Figure generation complete.")
