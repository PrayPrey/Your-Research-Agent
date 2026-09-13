"""Visualization: 5 figures for H-M2 correlation analysis."""
from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def fig1_gate_metrics_bar(focal_corr: dict, out_path: str) -> None:
    """Bar chart: rho(Wikipedia->MMLU) vs rho(Wikipedia->HellaSwag) x 3 sizes."""
    sizes = config.MODEL_SIZES
    rho_mmlu = [focal_corr["rho_wiki_mmlu"][s] for s in sizes]
    rho_hellaswag = [focal_corr["rho_wiki_hellaswag"][s] for s in sizes]
    ci_mmlu = [focal_corr["ci_wiki_mmlu"][s] for s in sizes]
    ci_hellaswag = [focal_corr["ci_wiki_hellaswag"][s] for s in sizes]

    x = np.arange(len(sizes))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))

    bars1 = ax.bar(x - width / 2, rho_mmlu, width, label="MMLU", color="#1f77b4")
    bars2 = ax.bar(x + width / 2, rho_hellaswag, width, label="HellaSwag", color="#ff7f0e")

    for i, (rho, ci) in enumerate(zip(rho_mmlu, ci_mmlu)):
        ax.errorbar(x[i] - width / 2, rho, yerr=[[rho - ci[0]], [ci[1] - rho]], fmt="none", color="black", capsize=4)
    for i, (rho, ci) in enumerate(zip(rho_hellaswag, ci_hellaswag)):
        ax.errorbar(x[i] + width / 2, rho, yerr=[[rho - ci[0]], [ci[1] - rho]], fmt="none", color="black", capsize=4)

    ax.set_xlabel("Model Size")
    ax.set_ylabel("Spearman ρ")
    ax.set_title("P1 Gate Metric: Wikipedia Exposure vs Benchmark Score")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Pythia-{s}" for s in sizes])
    ax.legend()
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def fig2_domain_benchmark_heatmap(
    corr_by_model: dict,
    out_path: str,
    top_k: int = 8,
) -> None:
    """3-panel heatmap: top-k domains x 2 benchmarks per model size."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))

    for ax, model_size in zip(axes, config.MODEL_SIZES):
        matrix = corr_by_model[model_size]
        domains = config.PILE_DOMAINS
        rho_data = np.array([
            [matrix[d]["mmlu"].rho, matrix[d]["hellaswag"].rho]
            for d in domains
        ])
        # top-k by sum of abs rho
        scores = np.abs(rho_data).sum(axis=1)
        top_idx = np.argsort(scores)[-top_k:][::-1]
        top_domains = [domains[i] for i in top_idx]
        top_rho = rho_data[top_idx]

        sns.heatmap(
            top_rho,
            ax=ax,
            xticklabels=["MMLU", "HellaSwag"],
            yticklabels=top_domains,
            annot=True,
            fmt=".2f",
            center=0,
            cmap="RdBu_r",
            vmin=-1,
            vmax=1,
        )
        ax.set_title(f"Pythia-{model_size}")

    plt.suptitle("Domain-Benchmark Spearman ρ Heatmap (Top-8 Domains)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def fig3_trajectories(
    exposure_by_model: dict,
    scores_by_model: dict,
    valid_steps_by_model: dict,
    out_path: str,
) -> None:
    """6-panel dual-axis line plots: Wikipedia exposure vs benchmarks."""
    wiki_idx = config.PILE_DOMAINS.index(config.FOCAL_DOMAINS["wikipedia"])
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))

    for row, model_size in enumerate(config.MODEL_SIZES):
        exposure = exposure_by_model[model_size]  # (T_valid, 22)
        scores = scores_by_model[model_size]
        steps = valid_steps_by_model[model_size]
        wiki_exp = exposure[:, wiki_idx]

        for col, (benchmark, label) in enumerate([("mmlu", "MMLU"), ("hellaswag", "HellaSwag")]):
            ax = axes[row][col]
            ax2 = ax.twinx()
            ax.plot(steps, scores[benchmark], color="#1f77b4", label=label, linewidth=1)
            ax2.plot(steps, wiki_exp, color="#d62728", label="Wikipedia Exposure", linewidth=1, linestyle="--")
            ax.set_xscale("symlog", linthresh=512)
            ax.set_xlabel("Training Step")
            ax.set_ylabel(f"{label} Score", color="#1f77b4")
            ax2.set_ylabel("Wikipedia Exposure", color="#d62728")
            ax.set_title(f"Pythia-{model_size}: Wikipedia vs {label}")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def fig4_fisher_forest(test_results: dict, focal_corr: dict, out_path: str) -> None:
    """Forest plot: P1 and P2 z-statistics + CIs per model size."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sizes = config.MODEL_SIZES

    for ax, prop, title in zip(axes, ["p1", "p2"], ["P1: rho(Wiki->MMLU) > rho(Wiki->HellaSwag)",
                                                      "P2: rho(Books->HellaSwag) > rho(Books->MMLU)"]):
        z_vals = [test_results[s][prop]["z_stat"] for s in sizes]
        colors = ["green" if test_results[s][prop].get("holm_reject", False) else "gray" for s in sizes]
        y = np.arange(len(sizes))
        ax.barh(y, z_vals, color=colors, height=0.5)
        ax.axvline(0, color="black", linewidth=1)
        ax.set_yticks(y)
        ax.set_yticklabels([f"Pythia-{s}" for s in sizes])
        ax.set_xlabel("Fisher z-statistic")
        ax.set_title(title)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def fig5_floor_filter_diagnostic(
    valid_masks: dict,
    scores_raw: dict,
    out_path: str,
) -> None:
    """Scatter showing filtered vs kept checkpoints per model size."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    steps = np.array(config.CHECKPOINT_STEPS)

    for ax, model_size in zip(axes, config.MODEL_SIZES):
        mask = valid_masks[model_size]
        mmlu = scores_raw[model_size]["mmlu"]
        colors = ["#2ca02c" if m else "#d62728" for m in mask]
        ax.scatter(steps, mmlu, c=colors, s=8, alpha=0.7)
        ax.axhline(config.FLOOR_THRESHOLD, color="orange", linestyle="--", linewidth=1.5, label=f"Floor={config.FLOOR_THRESHOLD}")
        ax.set_xscale("symlog", linthresh=512)
        ax.set_xlabel("Training Step")
        ax.set_ylabel("MMLU Score")
        ax.set_title(f"Pythia-{model_size} (N_valid={mask.sum()})")
        ax.legend(fontsize=8)

    plt.suptitle("Floor Filter Diagnostic: Green=Kept, Red=Filtered")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
