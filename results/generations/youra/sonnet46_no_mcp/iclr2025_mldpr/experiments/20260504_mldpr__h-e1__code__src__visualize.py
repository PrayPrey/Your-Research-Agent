"""
A-5 Visualization Generator
Generates all required figures for H-E1 existence analysis.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

try:
    import seaborn as sns
    _HAS_SEABORN = True
except ImportError:
    _HAS_SEABORN = False


def plot_fair_distribution(
    scored: pd.DataFrame,
    score_col: str,
    threshold: float,
    out_path: str,
) -> None:
    """Histogram of FAIR scores with threshold line and group count annotations."""
    valid = scored[scored["status"].isin(["ok", "fallback"])][score_col].dropna()

    fig, ax = plt.subplots(figsize=(10, 6))

    if _HAS_SEABORN:
        sns.histplot(valid, bins=50, kde=True, ax=ax, color="#4C72B0", alpha=0.7)
    else:
        ax.hist(valid, bins=50, color="#4C72B0", alpha=0.7, edgecolor="white")

    ax.axvline(x=threshold, color="red", linestyle="--", linewidth=2,
               label=f"Threshold = {threshold}")

    n_high = int((valid >= threshold).sum())
    n_low = int((valid < threshold).sum())

    ax.text(threshold + 0.02, ax.get_ylim()[1] * 0.85,
            f"High-FAIR\nn={n_high}", color="darkgreen", fontsize=11, va="top")
    ax.text(threshold - 0.22, ax.get_ylim()[1] * 0.85,
            f"Low-FAIR\nn={n_low}", color="darkred", fontsize=11, va="top")

    ax.set_xlabel("Aggregate FAIR Score", fontsize=13)
    ax.set_ylabel("Count", fontsize=13)
    ax.set_title("H-E1: FAIR Score Distribution (OpenML Post-2018 Cohort)", fontsize=14)
    ax.legend(fontsize=11)
    ax.set_xlim(0, 1)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def plot_cv_summary(metrics: dict, out_path: str) -> None:
    """Bar chart showing CV vs 0.15 threshold, n_high vs 500, n_low vs 500."""
    cv = metrics.get("cv") or 0.0
    n_high = metrics.get("n_high", 0)
    n_low = metrics.get("n_low", 0)

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    # CV bar
    ax = axes[0]
    color = "green" if cv > 0.15 else "red"
    ax.bar(["CV (achieved)"], [cv], color=color, alpha=0.8, width=0.4)
    ax.axhline(y=0.15, color="black", linestyle="--", linewidth=1.5, label="Threshold (0.15)")
    ax.set_title("Coefficient of Variation", fontsize=12)
    ax.set_ylabel("CV", fontsize=11)
    ax.set_ylim(0, max(cv * 1.3, 0.25))
    ax.legend(fontsize=9)
    ax.text(0, cv + 0.01, f"{cv:.3f}", ha="center", fontsize=12, fontweight="bold")

    # n_high bar
    ax = axes[1]
    color = "green" if n_high >= 500 else "red"
    ax.bar(["n_high (achieved)"], [n_high], color=color, alpha=0.8, width=0.4)
    ax.axhline(y=500, color="black", linestyle="--", linewidth=1.5, label="Threshold (500)")
    ax.set_title("High-FAIR Group Size", fontsize=12)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_ylim(0, max(n_high * 1.3, 600))
    ax.legend(fontsize=9)
    ax.text(0, n_high + 10, str(n_high), ha="center", fontsize=12, fontweight="bold")

    # n_low bar
    ax = axes[2]
    color = "green" if n_low >= 500 else "red"
    ax.bar(["n_low (achieved)"], [n_low], color=color, alpha=0.8, width=0.4)
    ax.axhline(y=500, color="black", linestyle="--", linewidth=1.5, label="Threshold (500)")
    ax.set_title("Low-FAIR Group Size", fontsize=12)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_ylim(0, max(n_low * 1.3, 600))
    ax.legend(fontsize=9)
    ax.text(0, n_low + 10, str(n_low), ha="center", fontsize=12, fontweight="bold")

    gate_passed = cv > 0.15 and n_high >= 500 and n_low >= 500
    status_str = "PASS ✓" if gate_passed else "FAIL ✗"
    fig.suptitle(f"H-E1 Gate Metrics — {status_str}", fontsize=15, fontweight="bold",
                 color="darkgreen" if gate_passed else "darkred")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def plot_sub_criteria_heatmap(scored: pd.DataFrame, out_path: str) -> None:
    """Heatmap of mean FAIR dimension scores (F/A/I/R)."""
    valid = scored[scored["status"].isin(["ok", "fallback"])]
    dim_cols = [c for c in ["fair_F", "fair_A", "fair_I", "fair_R"] if c in valid.columns]

    if not dim_cols:
        return

    means = valid[dim_cols].mean().to_frame("Mean Score").T
    means.columns = [c.replace("fair_", "") for c in dim_cols]

    fig, ax = plt.subplots(figsize=(8, 3))
    if _HAS_SEABORN:
        sns.heatmap(means, annot=True, fmt=".3f", cmap="YlOrRd",
                    vmin=0, vmax=1, ax=ax, linewidths=0.5)
    else:
        im = ax.imshow(means.values, cmap="YlOrRd", vmin=0, vmax=1, aspect="auto")
        for j, val in enumerate(means.values[0]):
            ax.text(j, 0, f"{val:.3f}", ha="center", va="center", fontsize=12)
        ax.set_xticks(range(len(means.columns)))
        ax.set_xticklabels(means.columns)
        ax.set_yticks([])
        plt.colorbar(im, ax=ax)

    ax.set_title("Mean FAIR Dimension Scores (F/A/I/R)", fontsize=13)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def plot_temporal_diagnostic(scored: pd.DataFrame, out_path: str) -> None:
    """Scatter: FAIR score vs upload_date with Spearman r annotation."""
    valid = scored[scored["status"].isin(["ok", "fallback"])]
    if "upload_date_ordinal" not in valid.columns or "fair_aggregate" not in valid.columns:
        return

    paired = valid[["upload_date_ordinal", "fair_aggregate"]].dropna()
    if len(paired) < 10:
        return

    from scipy import stats as _stats
    r, p = _stats.spearmanr(paired["upload_date_ordinal"], paired["fair_aggregate"])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(paired["upload_date_ordinal"], paired["fair_aggregate"],
               alpha=0.2, s=8, color="#4C72B0")
    ax.set_xlabel("Upload Date (ordinal)", fontsize=12)
    ax.set_ylabel("Aggregate FAIR Score", fontsize=12)
    ax.set_title(f"H-E1: Temporal Diagnostic\n"
                 f"Spearman r={r:.3f} (p={p:.3g}) — threshold: r < 0.20", fontsize=13)
    ax.text(0.05, 0.95, f"r = {r:.3f}\nTarget: < 0.20\n{'✓ PASS' if abs(r) < 0.20 else '✗ FAIL'}",
            transform=ax.transAxes, va="top", fontsize=11,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def generate_figures(
    scored: pd.DataFrame,
    metrics: dict,
    figures_dir: str,
    cfg,
) -> None:
    """Generate and save all required figures to figures_dir."""
    os.makedirs(figures_dir, exist_ok=True)

    threshold = getattr(cfg, "FAIR_THRESHOLD", 0.5)

    # 1. FAIR score distribution
    plot_fair_distribution(
        scored, "fair_aggregate", threshold,
        os.path.join(figures_dir, "fair_distribution.png"),
    )

    # 2. Gate metrics summary
    plot_cv_summary(
        metrics,
        os.path.join(figures_dir, "gate_metrics_summary.png"),
    )

    # 3. Sub-criteria heatmap
    plot_sub_criteria_heatmap(
        scored,
        os.path.join(figures_dir, "sub_criteria_heatmap.png"),
    )

    # 4. Temporal diagnostic
    plot_temporal_diagnostic(
        scored,
        os.path.join(figures_dir, "temporal_diagnostic.png"),
    )

    print(f"  → Figures saved to {figures_dir}/")
