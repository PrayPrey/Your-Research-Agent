"""FR-6: Figure generation — 4 required figures."""
import pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from config import (
    FIG_STYLE, HEATMAP_FIGSIZE, FIGURES_DIR,
    BAR_KWARGS_PYTHIA, BAR_KWARGS_OLMO, SAVEFIG_KWARGS,
    BOOTSTRAP_VLINE_ZERO, BOOTSTRAP_VLINE_THRESHOLD,
    ERRORBAR_STYLE, RATIO_THRESHOLD,
)


def _savefig(fig: plt.Figure, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(path), **SAVEFIG_KWARGS)
    plt.close(fig)
    print(f"[FIG] Saved: {path}")


def fig_absolute_scores(
    pythia_results: dict,
    olmo_results: dict,
    out_dir: str,
) -> None:
    """FR-6.1: Side-by-side bar chart of 4 task absolute scores."""
    tasks = ["mmlu", "hellaswag", "arc_easy", "arc_challenge"]
    task_labels = ["MMLU\n(mean)", "HellaSwag", "ARC-Easy", "ARC-Challenge"]

    def _get_score(results: dict, task: str) -> float:
        if task == "mmlu":
            mmlu_keys = [k for k in results if k.startswith("mmlu_")]
            return float(np.mean([results[k]["acc,none"] for k in mmlu_keys]))
        elif task == "arc_challenge":
            return results[task]["acc_norm,none"]
        else:
            return results[task]["acc,none"]

    p_vals = [_get_score(pythia_results, t) for t in tasks]
    o_vals = [_get_score(olmo_results, t) for t in tasks]

    x = np.arange(len(tasks))
    fig, ax = plt.subplots(figsize=FIG_STYLE["figsize"])
    ax.bar(x - 0.2, p_vals, width=0.4, **BAR_KWARGS_PYTHIA)
    ax.bar(x + 0.2, o_vals, width=0.4, **BAR_KWARGS_OLMO)
    ax.set_xticks(x)
    ax.set_xticklabels(task_labels, fontsize=FIG_STYLE["tick_size"])
    ax.tick_params(labelsize=FIG_STYLE["tick_size"])
    ax.set_xlabel("Task", fontsize=FIG_STYLE["label_size"])
    ax.set_ylabel("Accuracy", fontsize=FIG_STYLE["label_size"])
    ax.set_title("Absolute Task Scores: Pythia-6.9B vs OLMo-7B (~300B tokens)",
                 fontsize=FIG_STYLE["title_size"])
    ax.legend(fontsize=FIG_STYLE["legend_fontsize"])
    ax.set_ylim(0, 1)
    fig.tight_layout()
    _savefig(fig, pathlib.Path(out_dir) / "absolute_scores.png")


def fig_ratio_delta(metrics: dict, out_dir: str) -> None:
    """FR-6.2: Bar chart with 95% CI error bars for ratio and ARC delta."""
    boot = metrics["bootstrap"]
    ci_lo, ci_hi = boot["ci_95"]
    mean_diff = boot["mean_diff"]
    ci_half = (ci_hi - ci_lo) / 2

    arc_delta_diff = metrics["arc_delta_olmo"] - metrics["arc_delta_pythia"]

    labels = ["MMLU/HellaSwag Ratio\n(OLMo - Pythia)", "ARC-Challenge/Easy Delta\n(OLMo - Pythia)"]
    values = [mean_diff, arc_delta_diff]
    errors = [ci_half, 0]  # only ratio has bootstrap CI

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=FIG_STYLE["figsize"])
    colors = [BAR_KWARGS_OLMO["color"], BAR_KWARGS_PYTHIA["color"]]
    bars = ax.bar(x, values, width=0.5, color=colors, alpha=0.85)
    ax.errorbar(x[:1], values[:1], yerr=errors[:1], **ERRORBAR_STYLE)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.axhline(RATIO_THRESHOLD, color=BOOTSTRAP_VLINE_THRESHOLD["color"],
               linestyle=BOOTSTRAP_VLINE_THRESHOLD["linestyle"],
               linewidth=BOOTSTRAP_VLINE_THRESHOLD["linewidth"],
               label=f"threshold ({RATIO_THRESHOLD})")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=FIG_STYLE["tick_size"])
    ax.tick_params(labelsize=FIG_STYLE["tick_size"])
    ax.set_ylabel("Difference (OLMo − Pythia)", fontsize=FIG_STYLE["label_size"])
    ax.set_title("Ratio and ARC Delta Differences with 95% CI",
                 fontsize=FIG_STYLE["title_size"])
    ax.legend(fontsize=FIG_STYLE["legend_fontsize"])
    fig.tight_layout()
    _savefig(fig, pathlib.Path(out_dir) / "ratio_delta.png")


def fig_mmlu_heatmap(
    pythia_results: dict,
    olmo_results: dict,
    out_dir: str,
) -> None:
    """FR-6.3: 57×2 heatmap of per-subject MMLU accuracy."""
    mmlu_keys = sorted([k for k in pythia_results if k.startswith("mmlu_")])
    subject_labels = [k.replace("mmlu_", "").replace("_", " ") for k in mmlu_keys]

    p_accs = [pythia_results[k]["acc,none"] for k in mmlu_keys]
    o_accs = [olmo_results[k]["acc,none"] for k in mmlu_keys]

    data = np.array([p_accs, o_accs]).T  # shape (57, 2)

    fig, ax = plt.subplots(figsize=HEATMAP_FIGSIZE)
    sns.heatmap(
        data,
        ax=ax,
        xticklabels=["Pythia-6.9B", "OLMo-7B"],
        yticklabels=subject_labels,
        vmin=0, vmax=1,
        cmap="RdYlGn",
        annot=False,
        cbar_kws={"label": "Accuracy"},
    )
    ax.tick_params(axis="y", labelsize=8)
    ax.tick_params(axis="x", labelsize=FIG_STYLE["tick_size"])
    ax.set_title("Per-subject MMLU Accuracy Heatmap", fontsize=FIG_STYLE["title_size"])
    fig.tight_layout()
    _savefig(fig, pathlib.Path(out_dir) / "mmlu_heatmap.png")


def fig_bootstrap_dist(metrics: dict, out_dir: str) -> None:
    """FR-6.4: Histogram of bootstrap ratio diffs."""
    diffs = metrics["bootstrap"]["bootstrap_diffs"]
    ci_lo, ci_hi = metrics["bootstrap"]["ci_95"]
    mean_diff = metrics["bootstrap"]["mean_diff"]

    fig, ax = plt.subplots(figsize=FIG_STYLE["figsize"])
    ax.hist(diffs, bins=40, color=BAR_KWARGS_OLMO["color"], alpha=0.75, label="Bootstrap diffs")
    ax.axvline(0, **BOOTSTRAP_VLINE_ZERO)
    ax.axvline(RATIO_THRESHOLD, **BOOTSTRAP_VLINE_THRESHOLD)
    ax.axvline(mean_diff, color="#009E73", linestyle="-", linewidth=1.5, label=f"mean ({mean_diff:.4f})")
    ax.axvspan(ci_lo, ci_hi, alpha=0.15, color="grey", label="95% CI")
    ax.tick_params(labelsize=FIG_STYLE["tick_size"])
    ax.set_xlabel("OLMo ratio − Pythia ratio", fontsize=FIG_STYLE["label_size"])
    ax.set_ylabel("Count", fontsize=FIG_STYLE["label_size"])
    ax.set_title("Bootstrap Distribution of Ratio Differences (n=1000)",
                 fontsize=FIG_STYLE["title_size"])
    ax.legend(fontsize=FIG_STYLE["legend_fontsize"])
    fig.tight_layout()
    _savefig(fig, pathlib.Path(out_dir) / "bootstrap_dist.png")


def generate_all(
    pythia_results: dict,
    olmo_results: dict,
    metrics: dict,
    out_dir: str = None,
) -> None:
    """Generate all 4 figures."""
    if out_dir is None:
        out_dir = FIGURES_DIR
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig_absolute_scores(pythia_results, olmo_results, out_dir)
    fig_ratio_delta(metrics, out_dir)
    fig_mmlu_heatmap(pythia_results, olmo_results, out_dir)
    fig_bootstrap_dist(metrics, out_dir)
    print(f"[FIG] All 4 figures saved to {out_dir}")
