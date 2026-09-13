"""Visualization Suite for H-M2 experiment.

Produces 5 required figures:
1. gate_metrics_comparison.png   — bar chart Δρ at s=1.0, CI, threshold lines
2. delta_rho_heatmap.png        — 4×4 encoder×severity heatmap (RdBu_r)
3. rho_degradation_curves.png   — ρ vs severity line plot with seed error bands
4. threeway_ranking_scatter.png — per-seed Δρ scatter with threshold zones
5. bootstrap_distributions.png  — overlapping bootstrap distributions
"""
import logging
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENCODER_COLORS = {
    "flat-MLP":        "red",
    "flat-MLP+aug":    "orange",
    "flat-MLP+canon":  "green",
    "NFT-base":        "blue",
}

THRESHOLD_LINES = [0.02, 0.03, 0.05]

ENCODERS_HM2 = ["flat-MLP", "flat-MLP+aug", "flat-MLP+canon", "NFT-base"]

DPI = 150
STYLE = "seaborn-v0_8-whitegrid"


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


# ---------------------------------------------------------------------------
# Figure 1: Gate Metrics Comparison
# ---------------------------------------------------------------------------

def plot_gate_metrics_comparison(
    eval_df: pd.DataFrame,
    gate_result: dict,
    out_path: str,
) -> None:
    """Bar chart: mean Δρ at s=1.0 for 4 encoders with 95% CI and threshold lines.

    Parameters
    ----------
    eval_df : pd.DataFrame
        Evaluation results DataFrame
    gate_result : dict
        Gate evaluation result from evaluate_gate_hm2()
    out_path : str
        Output path for the figure
    """
    _ensure_dir(out_path)
    s1_df = eval_df[eval_df["severity"] == 1.0].copy()

    # Aggregate mean Δρ and 95% CI per encoder
    agg = s1_df.groupby("encoder")["delta_rho"].agg(["mean", "sem"]).reset_index()
    agg.columns = ["encoder", "mean_dr", "sem_dr"]
    # 95% CI: ±1.96 * sem
    agg["ci95"] = 1.96 * agg["sem_dr"]

    # Reorder encoders
    enc_order = [e for e in ENCODERS_HM2 if e in agg["encoder"].values]
    agg = agg.set_index("encoder").loc[enc_order].reset_index()

    try:
        plt.style.use(STYLE)
    except Exception:
        pass

    fig, ax = plt.subplots(figsize=(10, 6), dpi=DPI)

    x = np.arange(len(enc_order))
    colors = [ENCODER_COLORS.get(e, "gray") for e in enc_order]
    bars = ax.bar(x, agg["mean_dr"], color=colors, alpha=0.8, width=0.6,
                  yerr=agg["ci95"], capsize=5, ecolor="black", error_kw={"linewidth": 1.5})

    # Threshold lines
    threshold_colors = {"0.02": "purple", "0.03": "darkblue", "0.05": "darkorange"}
    threshold_labels = {0.02: "NFT threshold (0.02)", 0.03: "Canon threshold (0.03)", 0.05: "Aug threshold (0.05)"}
    for thr in THRESHOLD_LINES:
        ax.axhline(thr, color=threshold_colors.get(str(thr), "gray"), linestyle="--", linewidth=1.5,
                   alpha=0.8, label=threshold_labels.get(thr, f"threshold={thr}"))

    ax.set_xticks(x)
    ax.set_xticklabels(enc_order, rotation=15, ha="right")
    ax.set_xlabel("Encoder", fontsize=12)
    ax.set_ylabel("Mean Δρ at severity=1.0", fontsize=12)
    ax.set_title("H-M2: Encoder Δρ Comparison — SHOULD_WORK Gate", fontsize=13)
    ax.legend(fontsize=9)
    ax.set_ylim(bottom=0)

    gate_str = "PASS" if gate_result.get("passed") else "FAIL"
    ax.text(0.02, 0.97, f"SHOULD_WORK: {gate_str}",
            transform=ax.transAxes, fontsize=10, verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved gate_metrics_comparison: {out_path}")


# ---------------------------------------------------------------------------
# Figure 2: Delta_rho Heatmap
# ---------------------------------------------------------------------------

def plot_delta_rho_heatmap(
    eval_df: pd.DataFrame,
    out_path: str,
) -> None:
    """4-encoder × 4-severity heatmap (blue=robust, red=degraded).

    Parameters
    ----------
    eval_df : pd.DataFrame
    out_path : str
    """
    _ensure_dir(out_path)

    # Mean Δρ per encoder × severity
    pivot = eval_df.groupby(["encoder", "severity"])["delta_rho"].mean().reset_index()
    pivot_table = pivot.pivot(index="encoder", columns="severity", values="delta_rho")

    # Order rows
    enc_order = [e for e in ENCODERS_HM2 if e in pivot_table.index]
    pivot_table = pivot_table.loc[enc_order]

    fig, ax = plt.subplots(figsize=(10, 5), dpi=DPI)

    sns.heatmap(
        pivot_table,
        ax=ax,
        cmap="RdBu_r",
        center=0.02,
        annot=True,
        fmt=".4f",
        linewidths=0.5,
        cbar_kws={"label": "Δρ (mean across seeds)"},
    )
    ax.set_title("H-M2: Δρ Heatmap — Encoder × Severity", fontsize=13)
    ax.set_xlabel("Permutation Severity", fontsize=11)
    ax.set_ylabel("Encoder", fontsize=11)

    plt.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved delta_rho_heatmap: {out_path}")


# ---------------------------------------------------------------------------
# Figure 3: Rho Degradation Curves
# ---------------------------------------------------------------------------

def plot_rho_degradation_curves(
    eval_df: pd.DataFrame,
    out_path: str,
) -> None:
    """Line plot: mean Spearman ρ vs severity, with seed-level error bands.

    Parameters
    ----------
    eval_df : pd.DataFrame
    out_path : str
    """
    _ensure_dir(out_path)

    try:
        plt.style.use(STYLE)
    except Exception:
        pass

    fig, ax = plt.subplots(figsize=(10, 6), dpi=DPI)

    severities = sorted(eval_df["severity"].unique())

    for enc in ENCODERS_HM2:
        enc_df = eval_df[eval_df["encoder"] == enc]
        if enc_df.empty:
            continue

        mean_rho = enc_df.groupby("severity")["rho"].mean()
        std_rho = enc_df.groupby("severity")["rho"].std()

        color = ENCODER_COLORS.get(enc, "gray")
        ax.plot(severities, mean_rho[severities], marker="o", color=color,
                linewidth=2, label=enc)
        ax.fill_between(
            severities,
            mean_rho[severities] - std_rho[severities],
            mean_rho[severities] + std_rho[severities],
            alpha=0.15, color=color,
        )

    ax.set_xlabel("Permutation Severity", fontsize=12)
    ax.set_ylabel("Spearman ρ", fontsize=12)
    ax.set_title("H-M2: ρ Degradation Curves by Encoder", fontsize=13)
    ax.legend(fontsize=9)
    ax.set_xticks(severities)
    ax.set_xlim(-0.05, 1.05)

    plt.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved rho_degradation_curves: {out_path}")


# ---------------------------------------------------------------------------
# Figure 4: Three-way Ranking Scatter
# ---------------------------------------------------------------------------

def plot_threeway_ranking_scatter(
    eval_df: pd.DataFrame,
    out_path: str,
) -> None:
    """Per-seed Δρ scatter at s=1.0 with threshold zones.

    Parameters
    ----------
    eval_df : pd.DataFrame
    out_path : str
    """
    _ensure_dir(out_path)

    try:
        plt.style.use(STYLE)
    except Exception:
        pass

    s1_df = eval_df[eval_df["severity"] == 1.0].copy()

    fig, ax = plt.subplots(figsize=(10, 6), dpi=DPI)

    for i, enc in enumerate(ENCODERS_HM2):
        enc_df = s1_df[s1_df["encoder"] == enc]
        if enc_df.empty:
            continue
        color = ENCODER_COLORS.get(enc, "gray")
        x = np.full(len(enc_df), i)
        ax.scatter(x, enc_df["delta_rho"].values, color=color, s=60, alpha=0.8, label=enc, zorder=3)

        # Mean line
        mean_val = enc_df["delta_rho"].mean()
        ax.hlines(mean_val, i - 0.2, i + 0.2, color=color, linewidth=2.5, zorder=4)

    # Threshold zones
    ax.axhspan(0, 0.02, alpha=0.08, color="blue", label="NFT zone (<0.02)")
    ax.axhspan(0.02, 0.03, alpha=0.08, color="green", label="Canon zone (0.02-0.03)")
    ax.axhspan(0.03, 0.05, alpha=0.08, color="orange", label="Aug zone (0.03-0.05)")

    for thr in THRESHOLD_LINES:
        ax.axhline(thr, color="gray", linestyle="--", linewidth=1, alpha=0.6)
        ax.text(len(ENCODERS_HM2) - 0.5, thr + 0.002, f"{thr}", fontsize=8, color="gray")

    ax.set_xticks(range(len(ENCODERS_HM2)))
    ax.set_xticklabels(ENCODERS_HM2, rotation=15, ha="right")
    ax.set_xlabel("Encoder", fontsize=12)
    ax.set_ylabel("Δρ at severity=1.0", fontsize=12)
    ax.set_title("H-M2: Per-Seed Δρ Scatter — Three-way Ranking", fontsize=13)
    ax.legend(fontsize=8, loc="upper left")

    plt.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved threeway_ranking_scatter: {out_path}")


# ---------------------------------------------------------------------------
# Figure 5: Bootstrap Distributions
# ---------------------------------------------------------------------------

def plot_bootstrap_distributions(
    bootstrap_results: dict,
    out_path: str,
) -> None:
    """Overlapping bootstrap Δρ distributions: aug vs NFT-base, canon vs NFT-base.

    Parameters
    ----------
    bootstrap_results : dict
        Dict from run_pairwise_bootstrap_tests() with keys like "flat-MLP+aug_vs_NFT-base"
    out_path : str
    """
    _ensure_dir(out_path)

    try:
        plt.style.use(STYLE)
    except Exception:
        pass

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=DPI)

    pairs_to_plot = [
        ("flat-MLP+aug_vs_NFT-base",   "flat-MLP+aug vs NFT-base",   "orange", "blue"),
        ("flat-MLP+canon_vs_NFT-base", "flat-MLP+canon vs NFT-base", "green",  "blue"),
    ]

    for ax, (pair_key, title, color_a, color_b) in zip(axes, pairs_to_plot):
        result = bootstrap_results.get(pair_key)
        if result is None:
            ax.text(0.5, 0.5, f"No data for\n{pair_key}", ha="center", va="center",
                    transform=ax.transAxes)
            ax.set_title(title)
            continue

        boot_deltas = result.get("boot_deltas", np.array([]))
        p_corr = result.get("p_value_corrected", result.get("p_value", float("nan")))
        delta_obs = result.get("delta_rho_obs", float("nan"))

        ax.hist(boot_deltas, bins=60, color=color_a, alpha=0.7,
                density=True, label=f"Bootstrap Δρ dist")
        ax.axvline(delta_obs, color="black", linestyle="-", linewidth=2, label=f"Observed Δρ={delta_obs:.4f}")
        ax.axvline(0, color="red", linestyle="--", linewidth=1.5, alpha=0.7, label="H0: Δρ=0")

        ci_lo = result.get("ci_lower", float("nan"))
        ci_hi = result.get("ci_upper", float("nan"))
        ax.axvspan(ci_lo, ci_hi, alpha=0.15, color="gray", label=f"95% CI [{ci_lo:.4f}, {ci_hi:.4f}]")

        sig = "YES" if p_corr < 0.05 else "NO"
        ax.set_title(f"{title}\np_holm={p_corr:.4f}, Sig: {sig}", fontsize=10)
        ax.set_xlabel("Bootstrap Δρ", fontsize=10)
        ax.set_ylabel("Density", fontsize=10)
        ax.legend(fontsize=7)

    plt.suptitle("H-M2: Bootstrap Distributions (Holm-corrected)", fontsize=12)
    plt.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved bootstrap_distributions: {out_path}")
