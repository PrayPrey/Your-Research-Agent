from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

from config import FIGURE_DPI, FIGURE_FORMAT, FIGURE_NAMES


def plot_gate_bar(
    partial_result: dict,
    threshold: float,
    figures_dir: Path,
) -> Path:
    """Fig 1: bar partial rho vs threshold; BCa CI error bar; PASS/FAIL annotation."""
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    rho = partial_result["rho_partial"]
    ci_lo = partial_result["bca_ci_low"]
    ci_hi = partial_result["bca_ci_high"]
    passes = partial_result["passes_threshold"]

    fig, ax = plt.subplots(figsize=(6, 5))
    color = "#2196F3" if passes else "#F44336"
    ax.bar(["Partial ρ"], [abs(rho)], color=color, alpha=0.85, width=0.4)
    ax.errorbar(
        ["Partial ρ"], [abs(rho)],
        yerr=[[abs(rho) - min(abs(ci_lo), abs(ci_hi))],
              [max(abs(ci_lo), abs(ci_hi)) - abs(rho)]],
        fmt="none", color="black", capsize=6, linewidth=2,
    )
    ax.axhline(threshold, color="red", linestyle="--", linewidth=1.5, label=f"Threshold = {threshold}")
    status = "PASS ✓" if passes else "FAIL ✗"
    ax.text(0, abs(rho) + 0.02, f"{status}\nρ={rho:.3f}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_ylabel("|Partial ρ| (ECE, TruthfulQA% | MMLU)", fontsize=10)
    ax.set_title("H-M1 Primary Gate: Capability-Independent Calibration-Hallucination Link", fontsize=10)
    ax.set_ylim(0, max(abs(rho) + 0.15, threshold + 0.1))
    ax.legend()
    fig.tight_layout()

    out = figures_dir / FIGURE_NAMES["gate_bar"]
    fig.savefig(out, dpi=FIGURE_DPI, format=FIGURE_FORMAT)
    plt.close(fig)
    return out


def plot_raw_vs_partial(
    raw_rho: float,
    partial_rho: float,
    confound_result: dict,
    figures_dir: Path,
) -> Path:
    """Fig 2: side-by-side bar raw rho vs partial rho; survival_fraction text."""
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    survival = confound_result.get("survival_fraction", float("nan"))

    fig, ax = plt.subplots(figsize=(6, 5))
    labels = ["Raw ρ\n(ECE–TruthfulQA%)", "Partial ρ\n(ECE–TruthfulQA%|MMLU)"]
    values = [abs(raw_rho), abs(partial_rho)]
    colors = ["#90CAF9", "#1565C0"]
    bars = ax.bar(labels, values, color=colors, alpha=0.9, width=0.5)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01, f"{val:.3f}",
                ha="center", va="bottom", fontsize=11, fontweight="bold")

    if not np.isnan(survival):
        ax.text(0.5, 0.95, f"Survival fraction: {survival:.1%}\n(MMLU confound: {1-survival:.1%})",
                transform=ax.transAxes, ha="center", va="top", fontsize=10,
                bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    ax.set_ylabel("|Spearman ρ|", fontsize=10)
    ax.set_title("Confound Decomposition: Raw vs Capability-Controlled Correlation", fontsize=10)
    ax.set_ylim(0, max(values) + 0.15)
    fig.tight_layout()

    out = figures_dir / FIGURE_NAMES["raw_vs_partial"]
    fig.savefig(out, dpi=FIGURE_DPI, format=FIGURE_FORMAT)
    plt.close(fig)
    return out


def plot_ece_brier_scatter(
    df: pd.DataFrame,
    internal_result: dict,
    figures_dir: Path,
) -> Path:
    """Fig 3: scatter ECE vs Brier N=30; model family color; rho annotated."""
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 6))
    families = df["family"].unique() if "family" in df.columns else []
    palette = plt.cm.tab10.colors
    family_colors = {f: palette[i % len(palette)] for i, f in enumerate(families)}

    if len(families) > 0:
        for fam in families:
            mask = df["family"] == fam
            ax.scatter(df.loc[mask, "ECE"], df.loc[mask, "Brier"],
                       label=fam, color=family_colors[fam], s=60, alpha=0.85)
        ax.legend(title="Model family", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    else:
        ax.scatter(df["ECE"], df["Brier"], s=60, alpha=0.85)

    rho = internal_result["rho"]
    passes = internal_result["passes_threshold"]
    status = "PASS" if passes else "FAIL"
    ax.text(0.05, 0.95, f"Spearman ρ = {rho:.3f} [{status}]",
            transform=ax.transAxes, va="top", fontsize=10,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

    ax.set_xlabel("ECE (Expected Calibration Error)", fontsize=10)
    ax.set_ylabel("Brier Score", fontsize=10)
    ax.set_title("ECE vs Brier: Internal Consistency of Calibration Metrics (N=30)", fontsize=10)
    fig.tight_layout()

    out = figures_dir / FIGURE_NAMES["ece_brier_scatter"]
    fig.savefig(out, dpi=FIGURE_DPI, format=FIGURE_FORMAT, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_discriminant_validity(
    primary_result: dict,
    discriminant_result: dict,
    figures_dir: Path,
) -> Path:
    """Fig 4: grouped bar partial rho(ECE,TruthfulQA|MMLU) vs partial rho(ECE,HumanEval|MMLU)."""
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    primary_rho = primary_result["rho_partial"]
    disc_rho = discriminant_result["rho_partial"]
    labels = ["ECE–TruthfulQA%|MMLU\n(Primary)", "ECE–HumanEval|MMLU\n(Discriminant)"]
    values = [abs(primary_rho), abs(disc_rho)]
    colors = ["#1565C0", "#FF7043"]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, values, color=colors, alpha=0.9, width=0.5)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01, f"{val:.3f}",
                ha="center", va="bottom", fontsize=11, fontweight="bold")

    from config import PRIMARY_THRESHOLD, DISCRIMINANT_THRESHOLD
    ax.axhline(PRIMARY_THRESHOLD, color="blue", linestyle="--", linewidth=1.2,
               label=f"Primary threshold ({PRIMARY_THRESHOLD})")
    ax.axhline(DISCRIMINANT_THRESHOLD, color="orange", linestyle="--", linewidth=1.2,
               label=f"Discriminant threshold ({DISCRIMINANT_THRESHOLD})")

    ax.set_ylabel("|Partial ρ|", fontsize=10)
    ax.set_title("Discriminant Validity: Epistemic Reliability Specificity", fontsize=10)
    ax.set_ylim(0, max(values) + 0.15)
    ax.legend()
    fig.tight_layout()

    out = figures_dir / FIGURE_NAMES["discriminant"]
    fig.savefig(out, dpi=FIGURE_DPI, format=FIGURE_FORMAT)
    plt.close(fig)
    return out


def plot_decoding_invariance(
    invariance_result: dict,
    figures_dir: Path,
) -> Path:
    """Fig 5: scatter greedy vs T=0.7 partial rho. Blank if skipped."""
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    out = figures_dir / FIGURE_NAMES["decoding_invariance"]
    fig, ax = plt.subplots(figsize=(6, 5))

    if invariance_result.get("skipped", True):
        ax.text(0.5, 0.5, "T=0.7 score matrix not available\n(decoding invariance test skipped)",
                transform=ax.transAxes, ha="center", va="center", fontsize=12,
                bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))
        ax.set_title("Decoding Invariance (Skipped — T=0.7 data unavailable)", fontsize=10)
    else:
        rho_g = invariance_result["rho_greedy"]
        rho_t = invariance_result["rho_t07"]
        passes = invariance_result["passes_threshold"]
        ax.scatter([rho_g], [rho_t], s=150, color="#1565C0", zorder=5, label="H-M1 (ECE–TruthfulQA%|MMLU)")
        lim = max(abs(rho_g), abs(rho_t)) + 0.1
        ax.plot([-lim, lim], [-lim, lim], "k--", linewidth=1, alpha=0.5, label="Perfect invariance")
        status = "PASS" if passes else "FAIL"
        ax.text(rho_g + 0.02, rho_t, f"  {status}\nρ_T=0.7={rho_t:.3f}", fontsize=9)
        ax.set_xlabel("Greedy partial ρ", fontsize=10)
        ax.set_ylabel("T=0.7 partial ρ", fontsize=10)
        ax.set_title("Decoding Invariance: Greedy vs T=0.7", fontsize=10)
        ax.legend()

    fig.tight_layout()
    fig.savefig(out, dpi=FIGURE_DPI, format=FIGURE_FORMAT)
    plt.close(fig)
    return out
