"""Visualization for H-Z1 experiment results."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _ensure_matplotlib():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        logger.warning("matplotlib not available, skipping figures")
        return None


def plot_gate_metrics(summary: dict, figures_dir: Path) -> None:
    """Bar chart: pass@1 Condition B vs C. Saves gate_metrics.png."""
    plt = _ensure_matplotlib()
    if plt is None:
        return

    figures_dir.mkdir(parents=True, exist_ok=True)

    pass_b = summary.get("pass_rate_b", 0.0)
    pass_c = summary.get("pass_rate_c", 0.0)
    n = summary.get("n_problems", 0)

    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(["Condition B\n(exec+mypy)", "Condition C\n(exec+mypy+Z3)"],
                  [pass_b * 100, pass_c * 100],
                  color=["#4C72B0", "#DD8452"], edgecolor="black", linewidth=0.8)

    for bar, val in zip(bars, [pass_b, pass_c]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val * 100:.1f}%", ha="center", va="bottom", fontsize=12, fontweight="bold")

    delta = pass_c - pass_b
    ax.set_title(f"Pass@1: Condition B vs C (n={n})\nΔ = {delta*100:+.1f} pp", fontsize=13)
    ax.set_ylabel("Pass@1 (%)", fontsize=12)
    ax.set_ylim(0, max(pass_b, pass_c) * 100 + 15)
    ax.axhline(y=pass_b * 100, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)

    plt.tight_layout()
    out_path = figures_dir / "gate_metrics.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")


def plot_z3_funnel(counts: dict, figures_dir: Path) -> None:
    """Stacked bar: curated → spec generated → spec validated → used."""
    plt = _ensure_matplotlib()
    if plt is None:
        return

    figures_dir.mkdir(parents=True, exist_ok=True)

    stages = ["HumanEval+\n(full)", "Curated\n(arithmetic)", "Z3 spec\ngenerated", "Z3 spec\nvalidated"]
    values = [
        counts.get("total_problems", 164),
        counts.get("curated", 0),
        counts.get("spec_generated", 0),
        counts.get("spec_valid", 0),
    ]

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
    bars = ax.bar(stages, values, color=colors, edgecolor="black", linewidth=0.8)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                str(val), ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_title("Z3 Spec Validation Funnel", fontsize=13)
    ax.set_ylabel("Number of Problems", fontsize=12)
    ax.set_ylim(0, max(values) * 1.2)

    plt.tight_layout()
    out_path = figures_dir / "z3_funnel.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")


def plot_per_round_curve(b_results: list, c_results: list, figures_dir: Path) -> None:
    """Line chart: cumulative pass@1 per repair round k=1..5, B vs C."""
    plt = _ensure_matplotlib()
    if plt is None:
        return

    figures_dir.mkdir(parents=True, exist_ok=True)

    max_rounds = 5
    n_b = len(b_results)
    n_c = len(c_results)

    if n_b == 0 or n_c == 0:
        return

    b_cumpass = []
    c_cumpass = []
    for k in range(1, max_rounds + 2):  # include after-last-repair
        b_pass = sum(1 for r in b_results if r.get("passed") and r.get("rounds_to_pass", 999) <= k)
        c_pass = sum(1 for r in c_results if r.get("passed") and r.get("rounds_to_pass", 999) <= k)
        b_cumpass.append(b_pass / n_b * 100)
        c_cumpass.append(c_pass / n_c * 100)

    x = list(range(1, max_rounds + 2))
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(x, b_cumpass, marker="o", label="Condition B (exec+mypy)", color="#4C72B0", linewidth=2)
    ax.plot(x, c_cumpass, marker="s", label="Condition C (exec+mypy+Z3)", color="#DD8452", linewidth=2)
    ax.set_xlabel("Repair Round k", fontsize=12)
    ax.set_ylabel("Cumulative Pass@k (%)", fontsize=12)
    ax.set_title("Pass@k Curve: Condition B vs C", fontsize=13)
    ax.legend(fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(["Round 1", "Round 2", "Round 3", "Round 4", "Round 5", "Final"])
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out_path = figures_dir / "per_round_curve.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")


def plot_ce_found_rate(c_results: list, figures_dir: Path) -> None:
    """Histogram: z3_ce_found_count distribution across problems."""
    plt = _ensure_matplotlib()
    if plt is None:
        return

    if not c_results:
        return

    figures_dir.mkdir(parents=True, exist_ok=True)

    ce_counts = [r.get("z3_ce_found_count", 0) for r in c_results]
    max_count = max(ce_counts) if ce_counts else 0

    fig, ax = plt.subplots(figsize=(6, 5))

    if max_count == 0:
        ax.bar(["0 CEs found"], [len(ce_counts)], color="#4C72B0", edgecolor="black")
    else:
        from collections import Counter
        count_dist = Counter(ce_counts)
        keys = list(range(max_count + 1))
        vals = [count_dist.get(k, 0) for k in keys]
        ax.bar([str(k) for k in keys], vals, color="#55A868", edgecolor="black")
        ax.set_xlabel("Z3 CEs found per problem", fontsize=12)

    n_with_ce = sum(1 for c in ce_counts if c > 0)
    rate = n_with_ce / len(ce_counts) * 100 if ce_counts else 0

    ax.set_title(f"Z3 CE Found Rate: {n_with_ce}/{len(ce_counts)} problems ({rate:.1f}%)", fontsize=12)
    ax.set_ylabel("Number of Problems", fontsize=12)

    plt.tight_layout()
    out_path = figures_dir / "ce_found_rate.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")
