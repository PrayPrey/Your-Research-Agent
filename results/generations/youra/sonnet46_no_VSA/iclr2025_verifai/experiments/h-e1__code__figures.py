"""Visualization for H-E1 contract-strength gap experiment."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path


def _ensure_dir(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def plot_gap_vs_baseline(
    mean_gap: float,
    ci_lower: float,
    ci_upper: float,
    out_path: str = "figures/gap_vs_baseline.png",
) -> None:
    """Bar chart: mean contract-strength gap vs 0 baseline with 95% CI."""
    _ensure_dir(out_path)
    fig, ax = plt.subplots(figsize=(6, 5))
    err_lower = mean_gap - ci_lower
    err_upper = ci_upper - mean_gap
    ax.bar(
        ["Contract-Strength Gap"],
        [mean_gap],
        yerr=[[err_lower], [err_upper]],
        color="#4472C4",
        capsize=8,
        width=0.4,
        error_kw={"elinewidth": 2, "ecolor": "black"},
    )
    ax.axhline(0, color="red", linestyle="--", linewidth=1.5, label="Baseline (0)")
    ax.axhline(0.01, color="orange", linestyle=":", linewidth=1.5, label="Gate threshold (0.01)")
    ax.set_ylabel("Mean Contract-Strength Gap", fontsize=12)
    ax.set_title("H-E1: Contract-Strength Gap vs Baseline", fontsize=13)
    ax.set_ylim(bottom=-0.02)
    ax.legend(fontsize=10)
    ci_text = f"95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]"
    ax.text(0, mean_gap + err_upper + 0.01, ci_text, ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_per_model_boxplot(
    pbt_results: list[dict],
    out_path: str = "figures/per_model_gap.png",
) -> None:
    """Box plot: per-model contract-strength gap distribution."""
    _ensure_dir(out_path)
    from collections import defaultdict
    model_gaps: dict[str, list[float]] = defaultdict(list)
    for r in pbt_results:
        if r.get("error") and r.get("n_total", 0) == 0:
            continue
        model_gaps[r["model"]].append(float(r["violated"]))

    if not model_gaps:
        return

    models = sorted(model_gaps.keys())
    # Shorten model names for display
    short_names = [m.split("/")[-1][:20] for m in models]
    data = [model_gaps[m] for m in models]

    fig, ax = plt.subplots(figsize=(10, 5))
    bp = ax.boxplot(data, patch_artist=True, labels=short_names)
    colors = ["#4472C4", "#ED7D31", "#A9D18E", "#FF0000", "#FFC000"]
    for patch, color in zip(bp["boxes"], colors[:len(data)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_xlabel("Model", fontsize=11)
    ax.set_ylabel("Contract Violation Rate", fontsize=11)
    ax.set_title("H-E1: Per-Model Contract-Strength Gap", fontsize=13)
    ax.tick_params(axis="x", rotation=15)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_per_task_histogram(
    per_task_gap: dict[str, float],
    out_path: str = "figures/per_task_histogram.png",
) -> None:
    """Histogram of per-task contract-strength gap."""
    _ensure_dir(out_path)
    if not per_task_gap:
        return
    gaps = list(per_task_gap.values())
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(gaps, bins=20, color="#4472C4", edgecolor="white", alpha=0.8)
    ax.axvline(np.mean(gaps), color="red", linestyle="--", linewidth=2,
               label=f"Mean: {np.mean(gaps):.3f}")
    ax.set_xlabel("Contract-Strength Gap", fontsize=11)
    ax.set_ylabel("Number of Tasks", fontsize=11)
    ax.set_title(f"H-E1: Per-Task Gap Distribution (n={len(gaps)} tasks)", fontsize=13)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_cumulative_gap(
    per_task_gap: dict[str, float],
    out_path: str = "figures/cumulative_gap.png",
) -> None:
    """Cumulative fraction of tasks with gap > threshold."""
    _ensure_dir(out_path)
    if not per_task_gap:
        return
    gaps = sorted(per_task_gap.values(), reverse=True)
    n = len(gaps)
    thresholds = np.linspace(0, 1, 200)
    cumulative = [sum(1 for g in gaps if g > t) / n for t in thresholds]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(thresholds, cumulative, color="#4472C4", linewidth=2)
    ax.axvline(0.01, color="orange", linestyle=":", linewidth=1.5, label="Gate threshold (0.01)")
    ax.set_xlabel("Contract-Strength Gap Threshold", fontsize=11)
    ax.set_ylabel("Fraction of Tasks with Gap > Threshold", fontsize=11)
    ax.set_title("H-E1: Cumulative Contract-Strength Gap", fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_soundness_summary(
    valid_ids: set[str],
    quarantined_ids: set[str],
    out_path: str = "figures/soundness_summary.png",
) -> None:
    """Pie chart: oracle soundness pre-check results."""
    _ensure_dir(out_path)
    n_valid = len(valid_ids)
    n_quarantined = len(quarantined_ids)
    n_total = n_valid + n_quarantined
    if n_total == 0:
        return
    fig, ax = plt.subplots(figsize=(6, 5))
    sizes = [n_valid, n_quarantined]
    labels = [f"Valid ({n_valid})", f"Quarantined ({n_quarantined})"]
    colors = ["#4472C4", "#FF6B6B"]
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%",
           startangle=90, textprops={"fontsize": 11})
    ax.set_title(
        f"Oracle Soundness Pre-check\n(N={n_total} tasks, "
        f"{n_quarantined/n_total:.1%} quarantine rate)",
        fontsize=12,
    )
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
