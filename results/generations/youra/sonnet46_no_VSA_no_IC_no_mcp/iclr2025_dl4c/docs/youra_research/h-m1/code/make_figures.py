"""Task M1-6: Generate all 4 H-M1 diagnostic figures."""
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


@dataclass
class FigureConfig:
    figsize: tuple = (8, 5)
    figsize_wide: tuple = (10, 5)
    dpi: int = 150
    style: str = "seaborn-v0_8-whitegrid"
    context: str = "paper"
    font_scale: float = 1.2
    bucket_colors: Dict[str, str] = field(default_factory=lambda: {
        "introductory": "#4C9BE8",
        "interview":    "#F5A623",
        "competition":  "#E84C4C",
    })
    gate_threshold: float = 0.60
    gate_line_color: str = "#333333"
    gate_line_style: str = "--"
    gate_line_width: float = 1.5
    gate_line_label: str = "Gate (60%)"
    gate_metrics_fname: str = "gate_metrics.png"
    difficulty_gradient_fname: str = "difficulty_gradient.png"
    apps_difficulty_loss_fname: str = "apps_difficulty_loss.png"
    apps_coverage_fname: str = "apps_coverage.png"
    coverage_colors: Dict[str, str] = field(default_factory=lambda: {
        "solvable":   "#4C9BE8",
        "unsolvable": "#E84C4C",
    })


def _init_style(cfg: FigureConfig):
    try:
        plt.style.use(cfg.style)
    except OSError:
        plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_context(cfg.context, font_scale=cfg.font_scale)


def plot_gate_metrics(lcb_results: dict, figures_dir: str, cfg: FigureConfig = None) -> None:
    """Bar chart: SFT pass@1 vs 60% threshold on LCB-Hard."""
    if cfg is None:
        cfg = FigureConfig()
    _init_style(cfg)

    pass1 = lcb_results.get("pass@1", lcb_results.get("pass1", 0.0))
    if pass1 is None:
        pass1 = 0.0

    fig, ax = plt.subplots(figsize=cfg.figsize, dpi=cfg.dpi)
    bars = ax.bar(["SFT LCB-Hard"], [pass1], color="#4C9BE8", width=0.4, label="SFT pass@1")
    ax.axhline(cfg.gate_threshold, color=cfg.gate_line_color, linestyle=cfg.gate_line_style,
               linewidth=cfg.gate_line_width, label=cfg.gate_line_label)
    ax.bar_label(bars, fmt="%.3f", padding=3)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("pass@1")
    ax.set_title("SFT LCB-Hard pass@1 vs Gate Threshold")
    ax.legend()
    fig.tight_layout()
    out = Path(figures_dir) / cfg.gate_metrics_fname
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved {out}")


def plot_difficulty_gradient(lcb_results: dict, figures_dir: str, cfg: FigureConfig = None) -> None:
    """Line chart: SFT pass@1 across benchmark difficulty levels."""
    if cfg is None:
        cfg = FigureConfig()
    _init_style(cfg)

    # Use available data; fill missing with None → gap in line
    benchmarks = ["HumanEval", "MBPP", "LCB-Easy", "LCB-Medium", "LCB-Hard"]
    keys = ["humaneval", "mbpp", "lcb_easy", "lcb_medium", "lcb_hard"]

    # Merge from different result schemas
    values = []
    for k in keys:
        v = lcb_results.get(k, lcb_results.get(f"pass@1_{k}"))
        if v is None and k == "lcb_hard":
            v = lcb_results.get("pass@1", lcb_results.get("pass1"))
        values.append(v)

    fig, ax = plt.subplots(figsize=cfg.figsize_wide, dpi=cfg.dpi)
    x = list(range(len(benchmarks)))
    valid = [(i, v) for i, v in enumerate(values) if v is not None]
    if valid:
        xi, yi = zip(*valid)
        ax.plot(xi, yi, marker="o", color="#4C9BE8", linewidth=2)
        ax.set_xticks(x)
        ax.set_xticklabels(benchmarks, rotation=15)
    ax.axhline(cfg.gate_threshold, color=cfg.gate_line_color, linestyle=cfg.gate_line_style,
               linewidth=cfg.gate_line_width, label=cfg.gate_line_label)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("pass@1")
    ax.set_title("SFT Performance Across Difficulty Levels")
    ax.legend()
    fig.tight_layout()
    out = Path(figures_dir) / cfg.difficulty_gradient_fname
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved {out}")


def plot_apps_difficulty_loss(loss_results: dict, figures_dir: str, cfg: FigureConfig = None) -> None:
    """Bar chart: mean SFT loss per APPS difficulty bucket with error bars."""
    if cfg is None:
        cfg = FigureConfig()
    _init_style(cfg)

    buckets = ["introductory", "interview", "competition"]
    means = [loss_results.get(b, {}).get("mean") for b in buckets]
    stds = [loss_results.get(b, {}).get("std", 0) for b in buckets]
    counts = [loss_results.get(b, {}).get("count", 0) for b in buckets]

    valid_means = [m if m is not None else 0 for m in means]
    valid_stds = [s if s is not None else 0 for s in stds]
    colors = [cfg.bucket_colors[b] for b in buckets]

    fig, ax = plt.subplots(figsize=cfg.figsize, dpi=cfg.dpi)
    bars = ax.bar(buckets, valid_means, yerr=valid_stds, color=colors, capsize=4,
                  error_kw={"elinewidth": 1.5})
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(valid_stds) * 0.05,
                f"n={count}", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Mean Cross-Entropy Loss (nats)")
    ax.set_title("SFT Training Loss by APPS Difficulty Bucket")
    fig.tight_layout()
    out = Path(figures_dir) / cfg.apps_difficulty_loss_fname
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved {out}")


def plot_apps_coverage(coverage_results: dict, figures_dir: str, cfg: FigureConfig = None) -> None:
    """Stacked bar: solvable vs unsolvable APPS-Competition problems."""
    if cfg is None:
        cfg = FigureConfig()
    _init_style(cfg)

    total = coverage_results.get("total", 0)
    solvable = coverage_results.get("solvable", 0)
    unsolvable = total - solvable

    fig, ax = plt.subplots(figsize=cfg.figsize, dpi=cfg.dpi)
    ax.bar(["Competition"], [solvable], color=cfg.coverage_colors["solvable"], label="Solvable")
    ax.bar(["Competition"], [unsolvable], bottom=[solvable],
           color=cfg.coverage_colors["unsolvable"], label="No solution")
    ax.set_ylabel("Number of problems")
    ax.set_title("APPS Competition-Level Coverage (Signal Void Evidence)")
    ax.legend()
    pct = coverage_results.get("coverage_pct", 0)
    ax.text(0, total * 1.02, f"{pct:.1f}% covered", ha="center")
    fig.tight_layout()
    out = Path(figures_dir) / cfg.apps_coverage_fname
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved {out}")


def make_all(results_dir: str, figures_dir: str) -> None:
    """Entry point: loads all results JSONs, calls all 4 plot functions."""
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    cfg = FigureConfig()
    base = Path(results_dir)

    lcb_path = base / "sft_lcb_hard.json"
    lcb = json.loads(lcb_path.read_text()) if lcb_path.exists() else {}

    loss_path = base / "apps_difficulty_loss.json"
    loss = json.loads(loss_path.read_text()) if loss_path.exists() else {}

    cov_path = base / "apps_hard_coverage.json"
    cov = json.loads(cov_path.read_text()) if cov_path.exists() else {}

    plot_gate_metrics(lcb, figures_dir, cfg)
    plot_difficulty_gradient(lcb, figures_dir, cfg)
    if loss:
        plot_apps_difficulty_loss(loss, figures_dir, cfg)
    if cov:
        plot_apps_coverage(cov, figures_dir, cfg)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", default="results/h-m1")
    parser.add_argument("--figures_dir", default="docs/youra_research/h-m1/figures")
    args = parser.parse_args()

    make_all(args.results_dir, args.figures_dir)
    print("All figures generated.")
