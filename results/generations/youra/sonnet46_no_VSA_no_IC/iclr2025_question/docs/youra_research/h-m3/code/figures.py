import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Dict


DATASETS = ["trivia_qa", "nq", "truthful_qa"]
MODELS   = ["llama2", "mistral"]
AGGS     = ["min", "mean", "raw_sum"]
AGG_COLORS = {"min": "#1f77b4", "mean": "#ff7f0e", "raw_sum": "#2ca02c"}


def fig1_auroc_bar(auroc_table: Dict, out_dir: str) -> str:
    auroc = auroc_table["auroc"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    x = np.arange(len(DATASETS))
    width = 0.25

    for ax_i, model in enumerate(MODELS):
        ax = axes[ax_i]
        for j, agg in enumerate(AGGS):
            vals, lo_errs, hi_errs = [], [], []
            for ds in DATASETS:
                entry = auroc.get((model, ds, agg))
                if entry:
                    vals.append(entry["auroc"])
                    lo_errs.append(entry["auroc"] - entry["ci_lower"])
                    hi_errs.append(entry["ci_upper"] - entry["auroc"])
                else:
                    vals.append(0)
                    lo_errs.append(0)
                    hi_errs.append(0)
            offset = (j - 1) * width
            bars = ax.bar(x + offset, vals, width, label=agg, color=AGG_COLORS[agg], alpha=0.8)
            ax.errorbar(x + offset, vals, yerr=[lo_errs, hi_errs],
                        fmt="none", color="black", capsize=3, linewidth=1)
        ax.set_title(f"{model}", fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(DATASETS, rotation=15)
        ax.set_ylabel("AUROC")
        ax.set_ylim(0, 1)
        ax.legend(title="Aggregation")
        ax.axhline(0.5, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)

    fig.suptitle("AUROC by Aggregation Method (with 95% Bootstrap CI)", fontsize=14)
    plt.tight_layout()
    path = os.path.join(out_dir, "fig1_auroc_bar.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def fig2_diff_heatmap(auroc_table: Dict, out_dir: str) -> str:
    diff = auroc_table["diff"]
    data_matrix = np.full((len(MODELS), len(DATASETS)), np.nan)
    annots = [["" for _ in DATASETS] for _ in MODELS]

    for i, model in enumerate(MODELS):
        for j, ds in enumerate(DATASETS):
            d = diff.get((model, ds))
            if d:
                data_matrix[i, j] = d["diff"]
                annots[i][j] = f"{d['diff']:+.3f}\n[{d['ci_lower']:.3f},{d['ci_upper']:.3f}]"

    fig, ax = plt.subplots(figsize=(9, 4))
    im = ax.imshow(data_matrix, cmap="RdBu_r", vmin=-0.15, vmax=0.15, aspect="auto")
    plt.colorbar(im, ax=ax, label="AUROC(min) - AUROC(mean)")
    ax.set_xticks(range(len(DATASETS)))
    ax.set_xticklabels(DATASETS)
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels(MODELS)
    for i in range(len(MODELS)):
        for j in range(len(DATASETS)):
            if annots[i][j]:
                ax.text(j, i, annots[i][j], ha="center", va="center", fontsize=7.5)
    ax.set_title("AUROC(min) − AUROC(mean) Heatmap\nBlue = min wins, Red = mean wins")
    plt.tight_layout()
    path = os.path.join(out_dir, "fig2_diff_heatmap.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def fig3_bootstrap_dists(auroc_table: Dict, out_dir: str) -> str:
    diff    = auroc_table["diff"]
    samples = auroc_table.get("bootstrap_samples", {})

    # 4 panels: each model × (trivia_qa, nq)
    panels = [(m, ds) for m in MODELS for ds in ["trivia_qa", "nq"]]
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes = axes.flatten()

    for idx, (model, ds) in enumerate(panels):
        ax = axes[idx]
        d  = diff.get((model, ds))

        # Compute diff bootstrap dist from stored per-agg samples
        key_min  = (model, ds, "min")
        key_mean = (model, ds, "mean")
        smin  = samples.get(key_min)
        smean = samples.get(key_mean)

        if smin is not None and smean is not None:
            n = min(len(smin), len(smean))
            diff_dist = smin[:n] - smean[:n]
            ax.hist(diff_dist, bins=50, color="#4878cf", alpha=0.7, edgecolor="white")
            if d:
                ax.axvline(d["diff"], color="black", linewidth=1.5, label=f"obs={d['diff']:+.3f}")
                ax.axvspan(d["ci_lower"], d["ci_upper"], alpha=0.2, color="orange", label="95% CI")
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)

        ax.axvline(0, color="red", linewidth=1, linestyle="--")
        ax.set_title(f"{model} × {ds}")
        ax.set_xlabel("AUROC(min) − AUROC(mean)")
        ax.set_ylabel("Count")
        ax.legend(fontsize=8)

    fig.suptitle("Bootstrap Distribution of AUROC Differences (P1 conditions)", fontsize=12)
    plt.tight_layout()
    path = os.path.join(out_dir, "fig3_bootstrap_dists.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def fig4_summary_table(gate_result: Dict, auroc_table: Dict, out_dir: str) -> str:
    diff = auroc_table["diff"]
    rows = []
    col_labels = ["Condition", "Model", "Dataset", "Diff", "CI Lower", "CI Upper", "Met"]

    # P1 rows
    for model in MODELS:
        for ds in ["trivia_qa", "nq"]:
            d = diff.get((model, ds), {})
            rows.append([
                "P1: min>mean",
                model, ds,
                f"{d.get('diff', 'N/A'):+.4f}" if isinstance(d.get('diff'), float) else "N/A",
                f"{d.get('ci_lower', 'N/A'):.4f}" if isinstance(d.get('ci_lower'), float) else "N/A",
                f"{d.get('ci_upper', 'N/A'):.4f}" if isinstance(d.get('ci_upper'), float) else "N/A",
                "✓" if gate_result["p1_evidence"].get(model, {}).get(ds, {}).get("met") else "✗",
            ])

    # P2 rows
    for model in MODELS:
        ev = gate_result["p2_evidence"].get(model, {}).get("truthful_qa", {})
        rows.append([
            "P2: mean>min",
            model, "truthful_qa",
            f"{ev.get('diff', 'N/A'):+.4f}" if isinstance(ev.get('diff'), float) else "N/A",
            f"{ev.get('ci_lower', 'N/A'):.4f}" if isinstance(ev.get('ci_lower'), float) else "N/A",
            f"{ev.get('ci_upper', 'N/A'):.4f}" if isinstance(ev.get('ci_upper'), float) else "N/A",
            "✓" if ev.get("met") else "✗",
        ])

    fig, ax = plt.subplots(figsize=(13, 4))
    ax.axis("off")
    tbl = ax.table(cellText=rows, colLabels=col_labels, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.5)

    green = "#d4f0d4"
    red   = "#f0d4d4"
    for row_idx, row in enumerate(rows):
        met = row[-1] == "✓"
        for col_idx in range(len(col_labels)):
            tbl[row_idx + 1, col_idx].set_facecolor(green if met else red)

    ax.set_title(
        f"Gate: {gate_result['gate']} ({gate_result['n_gates_met']}/3 conditions met)",
        fontsize=12, pad=12
    )
    plt.tight_layout()
    path = os.path.join(out_dir, "fig4_summary_table.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def save_all_figures(auroc_table: Dict, gate_result: Dict, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    p1 = fig1_auroc_bar(auroc_table, out_dir)
    p2 = fig2_diff_heatmap(auroc_table, out_dir)
    p3 = fig3_bootstrap_dists(auroc_table, out_dir)
    p4 = fig4_summary_table(gate_result, auroc_table, out_dir)
    for p in [p1, p2, p3, p4]:
        print(f"  Saved: {p}")
