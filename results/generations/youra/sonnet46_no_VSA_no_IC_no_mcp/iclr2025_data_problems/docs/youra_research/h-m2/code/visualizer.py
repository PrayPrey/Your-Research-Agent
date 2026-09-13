"""Figure generation for H-M2 min-k% memorization analysis."""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def sig_stars(p: float) -> str:
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"


def plot_mink_comparison_bar(stats: list, out: Path) -> None:
    """
    Mandatory gate figure: grouped bar chart.
    X: 4 benchmarks × 2 model sizes; Y: mean min-k% score.
    Bars: Pile (red) vs deduped (blue). Significance stars.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    for ax, size in zip(axes, ["1b", "6.9b"]):
        size_stats = [s for s in stats if s.model_size == size]
        if not size_stats:
            ax.set_title(f"Pythia-{size} (no data)")
            continue
        x = np.arange(len(size_stats))
        width = 0.35

        pile_means = [s.mean_pile for s in size_stats]
        dedup_means = [s.mean_deduped for s in size_stats]
        labels = [s.benchmark for s in size_stats]

        ax.bar(x - width / 2, pile_means, width, label="Pile", color="#d62728", alpha=0.85)
        ax.bar(x + width / 2, dedup_means, width, label="Dedup-Pile", color="#1f77b4", alpha=0.85)

        y_top = max(pile_means + dedup_means) if pile_means + dedup_means else 0
        for xi, stat in zip(x, size_stats):
            star = sig_stars(stat.p_corrected)
            ax.text(xi, y_top + 0.05, star, ha="center", fontsize=9)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
        ax.set_title(f"Pythia-{size}", fontsize=11)
        ax.set_ylabel("Mean Min-k% Score (k=20)", fontsize=10)
        ax.legend(fontsize=9)

    fig.suptitle("Min-k% Memorization: Pile vs Dedup-Pile", fontsize=13)
    plt.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {out}")


def plot_mink_heatmap(stats: list, out: Path) -> None:
    """Heatmap: rows=benchmarks, cols=model sizes, values=Pile-deduped differential."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
    SIZES = ["1b", "6.9b"]

    data = np.zeros((len(BENCHMARKS), len(SIZES)))
    for i, b in enumerate(BENCHMARKS):
        for j, sz in enumerate(SIZES):
            stat = next((s for s in stats if s.benchmark == b and s.model_size == sz), None)
            data[i, j] = stat.differential if stat else 0.0

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(data, cmap="RdBu_r", aspect="auto",
                   vmin=-abs(data).max(), vmax=abs(data).max())
    plt.colorbar(im, ax=ax, label="Differential (Pile − Dedup-Pile)")

    for i in range(len(BENCHMARKS)):
        for j in range(len(SIZES)):
            ax.text(j, i, f"{data[i, j]:.3f}", ha="center", va="center", fontsize=9)

    ax.set_xticks(range(len(SIZES)))
    ax.set_xticklabels(SIZES)
    ax.set_yticks(range(len(BENCHMARKS)))
    ax.set_yticklabels(BENCHMARKS)
    ax.set_title("Min-k% Differential (Pile − Dedup-Pile)", fontsize=12)
    ax.set_xlabel("Model Size")
    ax.set_ylabel("Benchmark")
    plt.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {out}")


def plot_mink_violin(raw_scores: dict, out: Path, model_size: str = "6.9b") -> None:
    """Violin plot: per-benchmark item-level score distributions (Pile vs deduped)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
    pile_key = f"pile_{model_size}"
    dedup_key = f"deduped_{model_size}"

    fig, axes = plt.subplots(1, 4, figsize=(16, 5))
    for ax, bench in zip(axes, BENCHMARKS):
        pile_scores = [s for s in raw_scores.get(pile_key, {}).get(bench, [])
                       if not (s != s or s == float("-inf"))]  # filter nan/neginf
        dedup_scores = [s for s in raw_scores.get(dedup_key, {}).get(bench, [])
                        if not (s != s or s == float("-inf"))]

        if pile_scores and dedup_scores:
            parts = ax.violinplot([pile_scores, dedup_scores],
                                  positions=[0, 1], showmedians=True)
            parts["bodies"][0].set_facecolor("#d62728")
            parts["bodies"][1].set_facecolor("#1f77b4")
            ax.set_xticks([0, 1])
            ax.set_xticklabels(["Pile", "Dedup"])
        else:
            ax.text(0.5, 0.5, "no data", ha="center", va="center", transform=ax.transAxes)

        ax.set_title(bench, fontsize=10)
        ax.set_xlabel("")
        if bench == BENCHMARKS[0]:
            ax.set_ylabel("Min-k% Score")

    fig.suptitle(f"Score Distributions — Pythia-{model_size}", fontsize=12)
    plt.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {out}")


def plot_cross_hypothesis(hm2_stats: list, hm1_results_path, out: Path,
                          model_size: str = "6.9b") -> None:
    """Scatter: H-M1 contamination differential vs H-M2 memorization differential."""
    import json
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from pathlib import Path as P
    from scipy.stats import spearmanr

    BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]

    hm1_path = P(hm1_results_path)
    if not hm1_path.exists():
        logger.warning(f"H-M1 results not found at {hm1_path}, skipping cross-hypothesis plot")
        return

    hm1_data = json.loads(hm1_path.read_text())

    x_vals, y_vals, labels = [], [], []
    for bench in BENCHMARKS:
        if bench not in hm1_data:
            continue
        hm1_diff = hm1_data[bench].get("mean_removed", 0) - hm1_data[bench].get("mean_retained", 0)
        hm2_stat = next((s for s in hm2_stats if s.benchmark == bench
                         and s.model_size == model_size), None)
        if hm2_stat is None:
            continue
        x_vals.append(hm1_diff)
        y_vals.append(hm2_stat.differential)
        labels.append(bench)

    if len(x_vals) < 2:
        logger.warning("Not enough data for cross-hypothesis scatter")
        return

    rho, p_val = spearmanr(x_vals, y_vals) if len(x_vals) >= 3 else (float("nan"), float("nan"))

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(x_vals, y_vals, color="#2ca02c", s=80, zorder=3)
    for x, y, lab in zip(x_vals, y_vals, labels):
        ax.annotate(lab, (x, y), textcoords="offset points", xytext=(5, 5), fontsize=9)

    ax.set_xlabel("H-M1: Contamination Differential (removed − retained)", fontsize=10)
    ax.set_ylabel(f"H-M2: Memorization Differential (Pile − Deduped, k=20, {model_size})", fontsize=9)
    rho_str = f"{rho:.2f}" if rho == rho else "n/a"
    ax.set_title(f"Cross-Hypothesis: Contamination → Memorization\nSpearman ρ = {rho_str}", fontsize=11)
    ax.axhline(0, color="gray", lw=0.8, ls="--")
    ax.axvline(0, color="gray", lw=0.8, ls="--")

    plt.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {out}")


def plot_k_sensitivity(ablation_results: dict, out: Path, benchmark: str = "mmlu") -> None:
    """Plot mean min-k% differential across k values for robustness check."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    k_vals = sorted(int(k) for k in ablation_results.keys())
    diffs = [ablation_results[k]["differential"] for k in k_vals]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(k_vals, diffs, marker="o", color="#2ca02c", linewidth=2)
    ax.axhline(0, color="gray", lw=0.8, ls="--")
    ax.set_xlabel("k (%)", fontsize=11)
    ax.set_ylabel("Mean Differential (Pile − Dedup-Pile)", fontsize=10)
    ax.set_title(f"k-Sensitivity — Min-k% Differential on {benchmark}", fontsize=11)
    ax.set_xticks(k_vals)
    plt.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {out}")


def generate_all_figures(raw_scores: dict, stats: list, ablation_results: dict,
                         figures_dir: Path, hm1_results_path=None) -> list[str]:
    """Generate all required figures. Returns list of created filenames."""
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    created = []

    try:
        f1 = figures_dir / "mink_comparison_bar.png"
        plot_mink_comparison_bar(stats, f1)
        created.append(str(f1))
    except Exception as e:
        logger.error(f"plot_mink_comparison_bar failed: {e}")

    try:
        f2 = figures_dir / "mink_heatmap.png"
        plot_mink_heatmap(stats, f2)
        created.append(str(f2))
    except Exception as e:
        logger.error(f"plot_mink_heatmap failed: {e}")

    try:
        f3 = figures_dir / "mink_violin.png"
        plot_mink_violin(raw_scores, f3, model_size="6.9b")
        created.append(str(f3))
    except Exception as e:
        logger.error(f"plot_mink_violin failed: {e}")

    if hm1_results_path:
        try:
            f4 = figures_dir / "cross_hypothesis_scatter.png"
            plot_cross_hypothesis(stats, hm1_results_path, f4)
            created.append(str(f4))
        except Exception as e:
            logger.error(f"plot_cross_hypothesis failed: {e}")

    if ablation_results:
        try:
            f5 = figures_dir / "k_sensitivity.png"
            ablation_int = {int(k): v for k, v in ablation_results.items()}
            plot_k_sensitivity(ablation_int, f5)
            created.append(str(f5))
        except Exception as e:
            logger.error(f"plot_k_sensitivity failed: {e}")

    logger.info(f"Generated {len(created)} figures")
    return created
