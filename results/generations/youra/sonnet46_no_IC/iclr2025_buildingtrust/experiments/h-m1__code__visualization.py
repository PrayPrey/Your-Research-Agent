"""Visualization for H-M1: 5 figures for RLHF safety-ethics co-optimization analysis."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns

from config import DIMENSIONS, ETHICS_IDX, SAFETY_IDX


def plot_gate_metrics(
    rho_safety_ethics: float,
    n_both_positive: int,
    n_pairs: int,
    out_path: str,
) -> None:
    """Figure 1: Dual-panel bar comparing rho vs 0.5 and n_pairs_both_positive vs 2/3."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))

    # Panel 1: rho vs threshold
    rho_pass = abs(rho_safety_ethics) > 0.5
    color1 = "#2E7D32" if rho_pass else "#C62828"
    ax1.bar(["ρ_partial\n(safety, ethics)"], [rho_safety_ethics], color=color1, alpha=0.85)
    ax1.axhline(0.5, color="black", linestyle="--", linewidth=1, label="threshold=0.5")
    ax1.set_ylim(0, 1)
    ax1.set_ylabel("Partial Spearman Correlation")
    ax1.set_title(f"Primary Gate: ρ={'PASS' if rho_pass else 'FAIL'}")
    ax1.legend(fontsize=8)
    ax1.text(0, rho_safety_ethics + 0.02, f"{rho_safety_ethics:.3f}", ha="center", fontsize=10)

    # Panel 2: n_pairs vs gate
    sec_pass = n_both_positive >= 2
    color2 = "#2E7D32" if sec_pass else "#C62828"
    ax2.bar(["Pairs\nboth-positive"], [n_both_positive], color=color2, alpha=0.85)
    ax2.axhline(2, color="black", linestyle="--", linewidth=1, label="gate=2/3")
    ax2.set_ylim(0, n_pairs + 0.5)
    ax2.set_yticks(range(n_pairs + 1))
    ax2.set_ylabel("Count (of 3 LLaMA-2 pairs)")
    ax2.set_title(f"Secondary Gate: {'PASS' if sec_pass else 'FAIL'}")
    ax2.legend(fontsize=8)
    ax2.text(0, n_both_positive + 0.05, str(n_both_positive), ha="center", fontsize=10)

    fig.suptitle("H-M1 MUST_WORK Gate Metrics", fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def _annotate_sign_test(ax: plt.Axes, sign_test: dict) -> None:
    gate_pass = sign_test["secondary_gate_pass"]
    label = (
        f"Sign test: {sign_test['n_both_positive']}/3 pairs both-positive\n"
        f"p = {sign_test['binom_pvalue']:.3f}  "
        f"{'PASS' if gate_pass else 'FAIL'}"
    )
    color = "#2E7D32" if gate_pass else "#C62828"
    ax.text(
        0.97, 0.97, label,
        transform=ax.transAxes,
        ha="right", va="top",
        fontsize=9, color=color,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color, linewidth=1.2),
    )


def plot_within_family_deltas(deltas: list, sign_test: dict, out_path: str) -> None:
    """Figure 2: Grouped bar — Δ_safety and Δ_ethics per LLaMA-2 scale, with sign test annotation."""
    scales = [d["scale"] for d in deltas]
    d_safety = [d["delta_safety"] for d in deltas]
    d_ethics = [d["delta_ethics"] for d in deltas]

    x = np.arange(len(scales))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(x - width / 2, d_safety, width, label="Δ Safety",
           color=["#2196F3" if v > 0 else "#EF5350" for v in d_safety])
    ax.bar(x + width / 2, d_ethics, width, label="Δ Ethics",
           color=["#FF9800" if v > 0 else "#9C27B0" for v in d_ethics])

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"LLaMA-2\n{s}" for s in scales])
    ax.set_ylabel("Score Delta (Chat − Base)")
    ax.set_title("Within-Family RLHF Effect: Δ Safety and Δ Ethics per Scale")
    ax.legend()
    _annotate_sign_test(ax, sign_test)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def _annotate_arrows(ax: plt.Axes, llama2_pairs: list, annotated_df: pd.DataFrame) -> None:
    for p in llama2_pairs:
        scale = p["scale"]
        base_mask = annotated_df.index.str.contains(f"LLaMA-2-{scale}-base", case=False)
        chat_mask = annotated_df.index.str.contains(f"LLaMA-2-{scale}-chat", case=False)
        if not base_mask.any() or not chat_mask.any():
            continue
        x0 = float(annotated_df.loc[base_mask, "safety"].iloc[0])
        y0 = float(annotated_df.loc[base_mask, "machine_ethics"].iloc[0])
        x1 = float(annotated_df.loc[chat_mask, "safety"].iloc[0])
        y1 = float(annotated_df.loc[chat_mask, "machine_ethics"].iloc[0])
        ax.annotate(
            "", xy=(x1, y1), xytext=(x0, y0),
            arrowprops=dict(arrowstyle="-|>", color="#FF6F00", lw=1.5, mutation_scale=12),
            zorder=5,
        )
        ax.text(
            (x0 + x1) / 2, (y0 + y1) / 2, scale,
            fontsize=7, color="#FF6F00", ha="center", va="bottom",
        )


def plot_safety_ethics_scatter(
    annotated_df: pd.DataFrame,
    llama2_pairs: list,
    out_path: str,
) -> None:
    """Figure 3: 16-model safety vs ethics scatter, colored by is_RLHF, arrows for LLaMA-2 pairs."""
    fig, ax = plt.subplots(figsize=(7, 6))

    base_mask = annotated_df["is_RLHF"] == 0
    chat_mask = annotated_df["is_RLHF"] == 1

    ax.scatter(
        annotated_df.loc[base_mask, "safety"],
        annotated_df.loc[base_mask, "machine_ethics"],
        c="#1565C0", marker="o", s=60, label="Base (no RLHF)", zorder=3,
    )
    ax.scatter(
        annotated_df.loc[chat_mask, "safety"],
        annotated_df.loc[chat_mask, "machine_ethics"],
        c="#C62828", marker="s", s=60, label="Chat (RLHF)", zorder=3,
    )
    _annotate_arrows(ax, llama2_pairs, annotated_df)

    ax.set_xlabel("Safety Score")
    ax.set_ylabel("Machine Ethics Score")
    ax.set_title("Safety vs. Ethics: All 16 Models (colored by RLHF)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def plot_delta_2d(deltas: list, out_path: str) -> None:
    """Figure 4: (Δ_safety, Δ_ethics) scatter for 3 LLaMA-2 pairs with quadrant lines."""
    fig, ax = plt.subplots(figsize=(6, 5))

    xs = [d["delta_safety"] for d in deltas]
    ys = [d["delta_ethics"] for d in deltas]
    scales = [d["scale"] for d in deltas]

    ax.axvline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")

    # Shade positive quadrant
    xlim = max(abs(min(xs)), abs(max(xs))) * 1.5 or 0.1
    ylim = max(abs(min(ys)), abs(max(ys))) * 1.5 or 0.1
    ax.fill_between([0, xlim], [0, 0], [ylim, ylim], alpha=0.1, color="green", label="Both positive")

    colors = ["#1565C0", "#C62828", "#2E7D32"]
    for x, y, scale, color in zip(xs, ys, scales, colors):
        ax.scatter(x, y, c=color, s=80, zorder=3)
        ax.text(x, y + ylim * 0.03, scale, ha="center", fontsize=9)

    n_both = sum(1 for d in deltas if d["both_positive"])
    ax.set_xlabel("Δ Safety (Chat − Base)")
    ax.set_ylabel("Δ Ethics (Chat − Base)")
    ax.set_title(f"2D Delta Space: LLaMA-2 RLHF Effect\n({n_both}/3 pairs in positive quadrant)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def plot_rho_heatmap_highlighted(
    rho_partial: np.ndarray,
    dimensions: list,
    out_path: str,
) -> None:
    """Figure 5: 6x6 rho_partial heatmap with safety-ethics cell highlighted."""
    fig, ax = plt.subplots(figsize=(7, 6))
    short_dims = [d.replace("machine_ethics", "ethics").replace("truthfulness", "truth") for d in dimensions]

    sns.heatmap(
        rho_partial,
        annot=True, fmt=".2f",
        cmap="RdBu_r", vmin=-1, vmax=1,
        xticklabels=short_dims,
        yticklabels=short_dims,
        ax=ax,
        linewidths=0.3,
    )
    # Highlight safety-ethics cell (SAFETY_IDX=1 row, ETHICS_IDX=5 col)
    for (row, col) in [(SAFETY_IDX, ETHICS_IDX), (ETHICS_IDX, SAFETY_IDX)]:
        rect = mpatches.Rectangle(
            (col, row), 1, 1,
            linewidth=2.5, edgecolor="#FF6F00", facecolor="none",
        )
        ax.add_patch(rect)

    ax.set_title(f"Partial Spearman Correlation Matrix\n(safety-ethics highlighted: ρ={rho_partial[SAFETY_IDX][ETHICS_IDX]:.3f})")
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
