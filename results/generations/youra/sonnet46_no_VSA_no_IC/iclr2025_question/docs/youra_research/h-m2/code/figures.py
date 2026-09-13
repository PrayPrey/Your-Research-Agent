"""Figure generation for H-M2."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Dict


_DATASET_LABELS = {
    "trivia_qa":   "TriviaQA\n(peaked)",
    "nq":          "NQ-Open\n(peaked)",
    "truthful_qa": "TruthfulQA\n(flat)",
}
_MODEL_LABELS = {
    "llama2":  "LLaMA-2-7B",
    "mistral": "Mistral-7B-v0.1",
}


def plot_rho_differential_bar(results: Dict, save_path: str) -> None:
    """MANDATORY. Bar chart: rho(min)-rho(mean) per (model, dataset), 95% CI error bars."""
    models   = sorted(results.keys())
    datasets = []
    for m in models:
        for d in results[m]:
            if d not in datasets:
                datasets.append(d)

    n_ds = len(datasets)
    n_m  = len(models)
    x    = np.arange(n_ds)
    width = 0.35

    fig, ax = plt.subplots(figsize=(max(8, n_ds * 2), 5))

    colors = ["#1f77b4", "#ff7f0e"]
    for mi, model in enumerate(models):
        diffs, errs_low, errs_high = [], [], []
        for ds in datasets:
            entry = results[model].get(ds, {})
            diff     = entry.get("rho_differential", {}).get("diff", 0.0)
            ci_low   = entry.get("rho_differential", {}).get("ci_low",  diff)
            ci_high  = entry.get("rho_differential", {}).get("ci_high", diff)
            diffs.append(diff)
            errs_low.append(diff - ci_low)
            errs_high.append(ci_high - diff)

        offset = (mi - (n_m - 1) / 2) * width
        bars = ax.bar(
            x + offset, diffs, width,
            label=_MODEL_LABELS.get(model, model),
            color=colors[mi % len(colors)],
            alpha=0.8,
        )
        ax.errorbar(
            x + offset, diffs,
            yerr=[errs_low, errs_high],
            fmt="none", color="black", capsize=4, linewidth=1.5,
        )

    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels([_DATASET_LABELS.get(d, d) for d in datasets])
    ax.set_ylabel("ρ(min) − ρ(mean)")
    ax.set_title("H-M2: Spearman ρ Differential (min − mean)\nPositive = min better; Negative = mean better")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Annotate direction
    peaked_x  = [i for i, d in enumerate(datasets) if d in ("trivia_qa", "nq")]
    flat_x    = [i for i, d in enumerate(datasets) if d == "truthful_qa"]
    y_lim = ax.get_ylim()
    for xi in peaked_x:
        ax.annotate("P1: min>mean\nexpected", xy=(xi, y_lim[1] * 0.9),
                    ha="center", fontsize=7, color="#1a5276")
    for xi in flat_x:
        ax.annotate("P2: mean>min\nexpected", xy=(xi, y_lim[1] * 0.9),
                    ha="center", fontsize=7, color="#7b241c")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"[figures] rho_differential_bar saved: {save_path}")


def plot_rho_scatter(results: Dict, save_path: str) -> None:
    """Scatter: rho(min) vs rho(mean) per dataset/model."""
    fig, ax = plt.subplots(figsize=(6, 5))
    markers  = {"llama2": "o", "mistral": "s"}
    ds_color = {"trivia_qa": "#1f77b4", "nq": "#aec7e8", "truthful_qa": "#d62728"}

    for model in results:
        for ds in results[model]:
            entry = results[model][ds]
            rho_min  = entry.get("rho_min",  None)
            rho_mean = entry.get("rho_mean", None)
            if rho_min is None or rho_mean is None:
                continue
            ax.scatter(
                rho_mean, rho_min,
                marker=markers.get(model, "x"),
                color=ds_color.get(ds, "gray"),
                s=100, zorder=3,
                label=f"{_MODEL_LABELS.get(model, model)} / {_DATASET_LABELS.get(ds, ds).replace(chr(10), ' ')}",
            )

    mn = min(
        min(results[m][d].get("rho_min", 0) for d in results[m]) for m in results
    )
    mx = max(
        max(results[m][d].get("rho_mean", 0) for d in results[m]) for m in results
    )
    lims = [min(mn, mx) - 0.05, max(mn, mx) + 0.05]
    ax.plot(lims, lims, "k--", linewidth=0.8, label="min = mean")
    ax.set_xlim(lims); ax.set_ylim(lims)
    ax.set_xlabel("ρ(mean, label)")
    ax.set_ylabel("ρ(min, label)")
    ax.set_title("H-M2: Spearman ρ — min vs. mean")
    ax.legend(fontsize=7, loc="upper left")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"[figures] rho_scatter saved: {save_path}")


def plot_auroc_heatmap(results: Dict, save_path: str) -> None:
    """Heatmap: 3 aggregations x 3 datasets x 2 models."""
    models   = sorted(results.keys())
    datasets = []
    for m in models:
        for d in results[m]:
            if d not in datasets:
                datasets.append(d)
    methods  = ["min", "mean", "raw_sum"]

    fig, axes = plt.subplots(1, len(models), figsize=(5 * len(models), 4), squeeze=False)
    for mi, model in enumerate(models):
        ax   = axes[0][mi]
        data = np.full((len(methods), len(datasets)), np.nan)
        for di, ds in enumerate(datasets):
            for ji, meth in enumerate(methods):
                val = results[model].get(ds, {}).get(f"auroc_{meth}", None)
                if val is not None:
                    data[ji, di] = val

        im = ax.imshow(data, vmin=0.4, vmax=0.85, cmap="RdYlGn", aspect="auto")
        ax.set_xticks(range(len(datasets)))
        ax.set_xticklabels([_DATASET_LABELS.get(d, d).replace("\n", " ") for d in datasets], fontsize=8)
        ax.set_yticks(range(len(methods)))
        ax.set_yticklabels(methods)
        ax.set_title(_MODEL_LABELS.get(model, model))
        for ji in range(len(methods)):
            for di in range(len(datasets)):
                if not np.isnan(data[ji, di]):
                    ax.text(di, ji, f"{data[ji, di]:.3f}", ha="center", va="center",
                            fontsize=9, color="black")
        fig.colorbar(im, ax=ax, fraction=0.04)

    plt.suptitle("H-M2: AUROC — aggregation method × dataset")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"[figures] auroc_heatmap saved: {save_path}")


def save_all_figures(results: Dict, figures_dir: str) -> None:
    plot_rho_differential_bar(results, os.path.join(figures_dir, "rho_differential_bar.png"))
    try:
        plot_rho_scatter(results, os.path.join(figures_dir, "rho_scatter.png"))
    except Exception as e:
        print(f"[figures] rho_scatter skipped: {e}")
    try:
        plot_auroc_heatmap(results, os.path.join(figures_dir, "auroc_heatmap.png"))
    except Exception as e:
        print(f"[figures] auroc_heatmap skipped: {e}")
