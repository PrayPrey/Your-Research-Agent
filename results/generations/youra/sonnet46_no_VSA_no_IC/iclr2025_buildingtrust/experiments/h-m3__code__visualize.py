"""H-M3 visualizations."""
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from config import RANK_REVERSAL_MIN_SHIFT, RHO_THRESHOLD

log = logging.getLogger(__name__)


def plot_gate_metrics_bar(results: dict, rho_fairness: float, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ["rho_AdvGLUE", "rho_ANLI", "rho_fairness (H-M1)"]
    rhos = [results["rho_AdvGLUE"], results["rho_ANLI"], rho_fairness]
    ci_advglue = results["ci_AdvGLUE"]
    ci_anli = results["ci_ANLI"]
    errors = [
        [max(0, rhos[0] - ci_advglue[0]), max(0, ci_advglue[1] - rhos[0])],
        [max(0, rhos[1] - ci_anli[0]), max(0, ci_anli[1] - rhos[1])],
        [0, 0],
    ]
    yerr = np.array([[e[0] for e in errors], [e[1] for e in errors]])
    colors = ["#e74c3c", "#3498db", "#2ecc71"]
    bars = ax.bar(labels, rhos, color=colors, yerr=yerr, capsize=5, alpha=0.8)
    ax.axhline(RHO_THRESHOLD, linestyle="--", color="black", linewidth=1.5, label=f"threshold ρ={RHO_THRESHOLD}")
    ax.set_ylabel("Partial Spearman ρ")
    ax.set_title("H-M3 Gate Metrics: Per-Pair Adversarial Rank Disruption")
    ax.legend()
    ax.set_ylim(-1, 1)
    plt.tight_layout()
    out_path = out_dir / "gate_metrics_comparison.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    log.info("Saved %s", out_path)


def plot_rank_scatter_advglue(df: pd.DataFrame, out_dir: Path) -> None:
    df = df.copy()
    df["rank_glue"] = df["glue_score"].rank(ascending=False)
    df["rank_advglue"] = df["advglue_score"].rank(ascending=False)
    df["shift"] = abs(df["rank_glue"] - df["rank_advglue"])
    fig, ax = plt.subplots(figsize=(6, 6))
    sc = ax.scatter(df["rank_glue"], df["rank_advglue"], c=df["shift"], cmap="Reds", s=80, edgecolors="grey", linewidths=0.5)
    plt.colorbar(sc, ax=ax, label="|rank shift|")
    ax.set_xlabel("GLUE Rank")
    ax.set_ylabel("AdvGLUE Rank")
    ax.set_title("Rank Scatter: GLUE vs AdvGLUE")
    lim = max(df["rank_glue"].max(), df["rank_advglue"].max()) + 1
    ax.plot([1, lim], [1, lim], "k--", alpha=0.4)
    plt.tight_layout()
    out_path = out_dir / "rank_scatter_advglue.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    log.info("Saved %s", out_path)


def plot_rank_scatter_anli(df: pd.DataFrame, out_dir: Path) -> None:
    df = df.copy()
    df["rank_anli_r1"] = df["anli_r1_score"].rank(ascending=False)
    df["rank_anli_r3"] = df["anli_r3_score"].rank(ascending=False)
    df["shift"] = abs(df["rank_anli_r1"] - df["rank_anli_r3"])
    fig, ax = plt.subplots(figsize=(6, 6))
    sc = ax.scatter(df["rank_anli_r1"], df["rank_anli_r3"], c=df["shift"], cmap="Blues", s=80, edgecolors="grey", linewidths=0.5)
    plt.colorbar(sc, ax=ax, label="|rank shift|")
    ax.set_xlabel("ANLI R1 Rank")
    ax.set_ylabel("ANLI R3 Rank")
    ax.set_title("Rank Scatter: ANLI R1 vs ANLI R3")
    lim = max(df["rank_anli_r1"].max(), df["rank_anli_r3"].max()) + 1
    ax.plot([1, lim], [1, lim], "k--", alpha=0.4)
    plt.tight_layout()
    out_path = out_dir / "rank_scatter_anli.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    log.info("Saved %s", out_path)


def plot_rank_reversal_heatmap(df: pd.DataFrame, out_dir: Path) -> None:
    df = df.copy()
    cols = ["glue_score", "advglue_score", "anli_r1_score", "anli_r3_score"]
    rank_df = df[cols].rank(ascending=False)
    rank_df.index = df.get("model_name", df.index).values

    # highlight cells where any shift from glue or anli_r1 >= threshold
    adv_shift = abs(rank_df["glue_score"] - rank_df["advglue_score"])
    anli_shift = abs(rank_df["anli_r1_score"] - rank_df["anli_r3_score"])
    highlight = pd.DataFrame(False, index=rank_df.index, columns=cols)
    highlight["advglue_score"] = adv_shift >= RANK_REVERSAL_MIN_SHIFT
    highlight["anli_r3_score"] = anli_shift >= RANK_REVERSAL_MIN_SHIFT

    fig, ax = plt.subplots(figsize=(8, max(5, len(rank_df) * 0.35)))
    sns.heatmap(rank_df, annot=True, fmt=".0f", cmap="YlOrRd_r", ax=ax, linewidths=0.5)
    ax.set_title(f"Model Rank Positions (highlight shift≥{RANK_REVERSAL_MIN_SHIFT})")
    ax.set_xlabel("Benchmark")
    plt.tight_layout()
    out_path = out_dir / "rank_reversal_heatmap.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    log.info("Saved %s", out_path)


def plot_correlation_summary_table(results: dict, rho_fairness: float, out_dir: Path) -> None:
    rows = [
        ["rho_fairness (H-M1)", f"{rho_fairness:.3f}", "—", "—"],
        [
            "rho_AdvGLUE",
            f"{results['rho_AdvGLUE']:.3f}",
            f"[{results['ci_AdvGLUE'][0]:.3f}, {results['ci_AdvGLUE'][1]:.3f}]",
            f"{results['p_AdvGLUE']:.3f}",
        ],
        [
            "rho_ANLI",
            f"{results['rho_ANLI']:.3f}",
            f"[{results['ci_ANLI'][0]:.3f}, {results['ci_ANLI'][1]:.3f}]",
            f"{results['p_ANLI']:.3f}",
        ],
    ]
    fig, ax = plt.subplots(figsize=(8, 2.5))
    ax.axis("off")
    table = ax.table(
        cellText=rows,
        colLabels=["Metric", "ρ", "95% CI (bootstrap)", "p (asymptotic)"],
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    ax.set_title("H-M3 Correlation Summary", pad=12)
    plt.tight_layout()
    out_path = out_dir / "correlation_summary_table.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info("Saved %s", out_path)


def plot_fisher_z_distribution(results: dict, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.linspace(-5, 5, 500)
    from scipy.stats import norm as _norm
    ax.plot(x, _norm.pdf(x), "k-", label="N(0,1)")
    z_adv = results["z_AdvGLUE"]
    z_anli = results["z_ANLI"]
    ax.axvline(z_adv, color="#e74c3c", linestyle="--", label=f"z_AdvGLUE={z_adv:.2f}")
    ax.axvline(z_anli, color="#3498db", linestyle="--", label=f"z_ANLI={z_anli:.2f}")
    ax.set_xlabel("Fisher z statistic")
    ax.set_ylabel("Density")
    ax.set_title("Fisher z Distribution vs Threshold (H1: ρ < 0.4)")
    ax.legend()
    plt.tight_layout()
    out_path = out_dir / "fisher_z_distribution.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    log.info("Saved %s", out_path)


def generate_all_figures(df: pd.DataFrame, results: dict, rho_fairness: float, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_gate_metrics_bar(results, rho_fairness, out_dir)
    plot_rank_scatter_advglue(df, out_dir)
    plot_rank_scatter_anli(df, out_dir)
    plot_rank_reversal_heatmap(df, out_dir)
    plot_correlation_summary_table(results, rho_fairness, out_dir)
    plot_fisher_z_distribution(results, out_dir)
