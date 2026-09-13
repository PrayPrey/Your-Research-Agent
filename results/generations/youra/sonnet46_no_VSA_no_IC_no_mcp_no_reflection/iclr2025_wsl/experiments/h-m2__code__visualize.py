"""H-M2 visualization: 5 figures saved to h-m2/figures/."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ENCODER_COLORS = {
    "FlatMLP": "#4C72B0",
    "DWSNet":  "#DD8452",
    "NFT":     "#55A868",
    "GNN":     "#C44E52",
}
EQUIVARIANT = ["DWSNet", "NFT", "GNN"]


def fig1_gate_delta(delta: dict, ci: dict, threshold: float, out_path: str) -> None:
    """Bar chart: Δ per equivariant encoder + threshold line at 0.02."""
    encs = EQUIVARIANT
    vals = [delta[e] for e in encs]
    ci_low = [delta[e] - ci[e][0] for e in encs]
    ci_high = [ci[e][1] - delta[e] for e in encs]
    colors = [ENCODER_COLORS[e] for e in encs]

    fig, ax = plt.subplots(figsize=(7, 5))
    x = np.arange(len(encs))
    bars = ax.bar(x, vals, color=colors, alpha=0.85, edgecolor="white")
    ax.errorbar(x, vals, yerr=[ci_low, ci_high], fmt="none", color="black",
                capsize=4, capthick=1.2, elinewidth=1.2)
    ax.axhline(threshold, color="#E74C3C", linestyle="--", linewidth=1.5,
               label=f"gate_threshold={threshold}")
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(encs)
    ax.set_xlabel("Encoder")
    ax.set_ylabel("Δ Spearman (gap − test_acc)")
    ax.set_title("H-M2: Differential Advantage Δ per Equivariant Encoder")
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def fig2_dual_target_spearman(gap_results: dict, testacc_results: dict, out_path: str) -> None:
    """Side-by-side bars: 4 encoders × 2 targets."""
    encs = ["FlatMLP", "DWSNet", "NFT", "GNN"]
    x = np.arange(len(encs))
    w = 0.35
    gap_vals = [gap_results[e] for e in encs]
    acc_vals = [testacc_results[e] for e in encs]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - w/2, gap_vals, w, label="Spearman(gap)", color="#5B9BD5", alpha=0.85, edgecolor="white")
    ax.bar(x + w/2, acc_vals, w, label="Spearman(test_acc)", color="#ED7D31", alpha=0.85, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(encs)
    ax.set_xlabel("Encoder")
    ax.set_ylabel("Spearman ρ")
    ax.set_title("H-M2: Dual-Target Spearman Comparison (gap vs. test_acc)")
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def fig3_delta_decomposition(gap_results: dict, testacc_results: dict, out_path: str) -> None:
    """Stacked bar: gap_improvement and acc_improvement components per encoder."""
    encs = EQUIVARIANT
    flat_gap = gap_results["FlatMLP"]
    flat_acc = testacc_results["FlatMLP"]
    gap_imps = [gap_results[e] - flat_gap for e in encs]
    acc_imps = [testacc_results[e] - flat_acc for e in encs]

    x = np.arange(len(encs))
    w = 0.5
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(x, gap_imps, w, label="gap_improvement", color="#55A868", alpha=0.85, edgecolor="white")
    ax.bar(x, acc_imps, w, bottom=0, label="acc_improvement", color="#DD8452", alpha=0.85,
           edgecolor="white")
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(encs)
    ax.set_xlabel("Encoder")
    ax.set_ylabel("Improvement over FlatMLP (Spearman)")
    ax.set_title("H-M2: Δ Decomposition (gap_imp − acc_imp)")
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def fig4_partial_corr_scatter(pred_gap_resid: np.ndarray, true_gap_resid: np.ndarray,
                               r: float, p: float, out_path: str) -> None:
    """Scatter of NFT pred_gap residuals vs. true_gap residuals (P3 visualization)."""
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(pred_gap_resid, true_gap_resid, alpha=0.3, s=5, color=ENCODER_COLORS["NFT"])
    ax.set_xlabel("NFT pred_gap residual (partialling out test_acc rank)")
    ax.set_ylabel("True gap residual (partialling out test_acc rank)")
    ax.set_title(f"H-M2: Partial Correlation P3 (NFT)\nr={r:.4f}, p={p:.4f}")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def fig5_bootstrap_ci(delta: dict, ci: dict, out_path: str) -> None:
    """Error bar plot: Δ ± 95% CI for 3 equivariant encoders."""
    encs = EQUIVARIANT
    vals = [delta[e] for e in encs]
    err_low = [delta[e] - ci[e][0] for e in encs]
    err_high = [ci[e][1] - delta[e] for e in encs]
    colors = [ENCODER_COLORS[e] for e in encs]

    fig, ax = plt.subplots(figsize=(7, 5))
    x = np.arange(len(encs))
    for i, (enc, v, el, eh, c) in enumerate(zip(encs, vals, err_low, err_high, colors)):
        ax.errorbar(i, v, yerr=[[el], [eh]], fmt="o", color=c, capsize=4,
                    capthick=1.2, elinewidth=1.2, markersize=8, label=enc)
    ax.axhline(0.02, color="#E74C3C", linestyle="--", linewidth=1.5, label="gate=0.02")
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(encs)
    ax.set_xlabel("Encoder")
    ax.set_ylabel("Δ Spearman (gap − test_acc)")
    ax.set_title("H-M2: Bootstrap 95% CI on Δ")
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
