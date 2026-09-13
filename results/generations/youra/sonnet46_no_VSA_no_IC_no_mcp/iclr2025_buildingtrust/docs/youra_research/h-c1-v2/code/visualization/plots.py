"""5 required figures for h-c1-v2."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from typing import List, Dict


def _color_ddece(ddece: float, threshold: float = 0.01) -> str:
    if ddece > threshold:
        return "green"
    elif ddece < 0:
        return "red"
    return "gray"


def fig1_ddece_bar(anli_results: List, advglue_results: List,
                   pair_label: str, out_path: str) -> None:
    """ΔΔECE per cell, color-coded green/red/gray."""
    all_results = list(anli_results) + list(advglue_results)
    if not all_results:
        print(f"⚠ No results for fig1 ({pair_label}) — skipping")
        return

    cell_ids = [r.cell_id for r in all_results]
    ddece_vals = [r.ddece for r in all_results]
    colors = [_color_ddece(d) for d in ddece_vals]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(range(len(cell_ids)), ddece_vals, color=colors, edgecolor="black", linewidth=0.5)
    ax.axhline(0.01, color="darkgreen", linestyle="--", linewidth=1, label="Threshold (0.01)")
    ax.axhline(0, color="black", linestyle="-", linewidth=0.5)
    ax.set_xticks(range(len(cell_ids)))
    ax.set_xticklabels(cell_ids, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("ΔΔECE (base − chat)")
    ax.set_title(f"ΔΔECE by Cell — {pair_label}")
    patches = [
        mpatches.Patch(color="green", label="Moderation (ΔΔECE > 0.01)"),
        mpatches.Patch(color="red", label="Reversal (ΔΔECE < 0)"),
        mpatches.Patch(color="gray", label="|ΔΔECE| ≤ 0.01"),
    ]
    ax.legend(handles=patches, fontsize=8)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"✓ Saved {out_path}")


def fig2_reliability_diagrams(base_results: Dict, chat_results: Dict,
                               cells: List[str], out_path: str) -> None:
    """Side-by-side reliability diagrams for specified cells (15-bin)."""
    valid_cells = [c for c in cells if c in base_results and c in chat_results]
    if not valid_cells:
        print("⚠ No valid cells for fig2 — skipping")
        return

    ncols = 2
    nrows = len(valid_cells)
    fig, axes = plt.subplots(nrows, ncols, figsize=(10, 4 * nrows))
    if nrows == 1:
        axes = axes[np.newaxis, :]

    n_bins = 15
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    for row, cell_id in enumerate(valid_cells):
        for col, (label, res_dict) in enumerate([("Base", base_results), ("Chat", chat_results)]):
            ax = axes[row, col]
            cell = res_dict[cell_id]
            # Plot diagonal
            ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Perfect")
            ax.set_xlabel("Confidence")
            ax.set_ylabel("Accuracy")
            ax.set_title(f"{cell_id} — {label}\nECE_adv={cell.ece_adv:.3f}")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.text(0.05, 0.9, f"ECE={cell.ece_adv:.3f}", transform=ax.transAxes, fontsize=9)

    fig.suptitle("Reliability Diagrams (adversarial splits)", fontsize=11)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"✓ Saved {out_path}")


def fig3_confidence_histogram(base_results: Dict, chat_results: Dict,
                               adv_cell: str, out_path: str) -> None:
    """base vs chat confidence distribution on adversarial split."""
    fig, ax = plt.subplots(figsize=(7, 4))
    if adv_cell in base_results and adv_cell in chat_results:
        base = base_results[adv_cell]
        chat = chat_results[adv_cell]
        ax.bar(["Base ECE_adv", "Chat ECE_adv"],
               [base.ece_adv, chat.ece_adv],
               color=["steelblue", "darkorange"], edgecolor="black")
        ax.set_ylabel("ECE (adversarial split)")
        ax.set_title(f"Confidence Calibration: {adv_cell}")
        ax.text(0, base.ece_adv + 0.005, f"{base.ece_adv:.4f}", ha="center", fontsize=9)
        ax.text(1, chat.ece_adv + 0.005, f"{chat.ece_adv:.4f}", ha="center", fontsize=9)
    else:
        ax.text(0.5, 0.5, "Data not available", ha="center", va="center")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"✓ Saved {out_path}")


def fig4_moderation_heatmap(all_cell_results: Dict[str, Dict[str, "CellECE"]],
                             row_models: List[str],
                             col_cells: List[str],
                             out_path: str) -> None:
    """ΔECE heatmap: rows=models, cols=cells."""
    model_labels = [m.split("/")[-1] for m in row_models]
    data = np.full((len(row_models), len(col_cells)), np.nan)

    for i, model_id in enumerate(row_models):
        if model_id in all_cell_results:
            for j, cell_id in enumerate(col_cells):
                if cell_id in all_cell_results[model_id]:
                    data[i, j] = all_cell_results[model_id][cell_id].delta_ece

    fig, ax = plt.subplots(figsize=(9, 3 + 0.8 * len(row_models)))
    mask = np.isnan(data)
    sns.heatmap(data, ax=ax, annot=True, fmt=".3f",
                xticklabels=col_cells, yticklabels=model_labels,
                cmap="RdYlGn_r", center=0, mask=mask,
                linewidths=0.5, cbar_kws={"label": "ΔECE"})
    ax.set_title("ΔECE Heatmap (adversarial vs. clean)\nRed=high degradation, Green=low/negative")
    ax.set_xlabel("Cell")
    ax.set_ylabel("Model")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"✓ Saved {out_path}")


def fig5_ddece_vs_difficulty(anli_results: List,
                              pair_label: str, out_path: str) -> None:
    """Scatter: x=ANLI round difficulty, y=ΔΔECE."""
    round_map = {"NLI-ANLI-R1": 1, "NLI-ANLI-R2": 2, "NLI-ANLI-R3": 3}
    xs, ys, labels = [], [], []
    for r in anli_results:
        if r.cell_id in round_map:
            xs.append(round_map[r.cell_id])
            ys.append(r.ddece)
            labels.append(r.cell_id)

    fig, ax = plt.subplots(figsize=(6, 4))
    if xs:
        ax.scatter(xs, ys, s=80, c="steelblue", zorder=3)
        for x, y, lbl in zip(xs, ys, labels):
            ax.annotate(lbl, (x, y), textcoords="offset points", xytext=(5, 5), fontsize=8)
        ax.axhline(0.01, color="green", linestyle="--", label="Threshold (0.01)")
        ax.axhline(0, color="black", linestyle="-", linewidth=0.5)
        # Fit line
        if len(xs) >= 2:
            z = np.polyfit(xs, ys, 1)
            p = np.poly1d(z)
            ax.plot([1, 2, 3], p([1, 2, 3]), "r--", linewidth=1, label=f"Trend")
        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(["R1 (easy)", "R2 (medium)", "R3 (hard)"])
        ax.set_xlabel("ANLI Round Difficulty")
        ax.set_ylabel("ΔΔECE")
        ax.set_title(f"ΔΔECE vs Adversarial Difficulty — {pair_label}")
        ax.legend(fontsize=8)
    else:
        ax.text(0.5, 0.5, "No ANLI data", ha="center", va="center")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"✓ Saved {out_path}")
