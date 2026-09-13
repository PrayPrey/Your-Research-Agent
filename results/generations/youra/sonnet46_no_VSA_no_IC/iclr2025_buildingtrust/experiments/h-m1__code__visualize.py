"""H-M1 visualization: 5 required figures for BBQ fairness correlation analysis."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import importlib.util as _ilu, pathlib as _pl
_cfg_spec = _ilu.spec_from_file_location("h_m1_config", _pl.Path(__file__).parent / "config.py")
_cfg = _ilu.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg)
GATE_RHO = _cfg.GATE_RHO


def plot_gate_metrics(results: dict, save_dir: Path) -> None:
    """Bar chart: partial_rho vs raw_rho with CI error bars and gate threshold."""
    raw_rho = results["raw"]["raw_rho"]
    partial_rho = results["primary"]["partial_rho"]
    ci95 = results["primary"]["ci95"]

    fig, ax = plt.subplots(figsize=(7, 5))
    bar_color = "green" if partial_rho > GATE_RHO else "red"

    bars = ax.bar(
        ["Raw ρ (no control)", "Partial ρ (MMLU control)"],
        [raw_rho, partial_rho],
        color=["steelblue", bar_color],
        alpha=0.8,
    )

    err_lo = partial_rho - ci95[0]
    err_hi = ci95[1] - partial_rho
    ax.errorbar(
        x=1, y=partial_rho,
        yerr=[[err_lo], [err_hi]],
        fmt="none", color="black", capsize=8, linewidth=2,
    )

    ax.axhline(GATE_RHO, linestyle="--", color="orange", linewidth=1.5, label=f"Gate threshold: {GATE_RHO}")
    ax.set_ylim(-0.1, 1.05)
    ax.set_ylabel("Spearman ρ")
    ax.set_title("BBQ Fairness Correlation: Raw vs Partial (MMLU-Controlled)")
    ax.legend()

    for bar, val in zip(bars, [raw_rho, partial_rho]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.02, f"{val:.3f}", ha="center", va="bottom", fontsize=11)

    save_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(save_dir / "gate_metrics_comparison.png", dpi=150)
    plt.close(fig)


def plot_rank_scatter(df: pd.DataFrame, results: dict, save_dir: Path) -> None:
    """Scatter: BBQ-Disambig rank vs BBQ-Ambig rank, model labels, correlation line."""
    df_plot = df.copy()
    df_plot["rank_dis"] = df_plot["bbq_disambig"].rank(ascending=False)
    df_plot["rank_amb"] = df_plot["bbq_ambig"].rank(ascending=False)

    partial_rho = results["primary"]["partial_rho"]

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.scatter(df_plot["rank_dis"], df_plot["rank_amb"], s=80, color="steelblue", zorder=5)

    for _, row in df_plot.iterrows():
        ax.annotate(
            row["model_name"],
            (row["rank_dis"], row["rank_amb"]),
            textcoords="offset points", xytext=(5, 3), fontsize=7,
        )

    m, b = np.polyfit(df_plot["rank_dis"], df_plot["rank_amb"], 1)
    x_fit = np.linspace(df_plot["rank_dis"].min(), df_plot["rank_dis"].max(), 100)
    ax.plot(x_fit, m * x_fit + b, "r--", alpha=0.7, label="Least-squares fit")

    ax.set_xlabel("BBQ-Disambig Rank (1=highest score)")
    ax.set_ylabel("BBQ-Ambig Rank")
    ax.set_title(f"BBQ Rank Correlation (partial ρ={partial_rho:.3f})")
    ax.legend()

    save_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(save_dir / "rank_scatter_bbq.png", dpi=150)
    plt.close(fig)


def plot_sensitivity(results: dict, save_dir: Path) -> None:
    """Bar chart: rho_mmlu vs rho_winogrande sensitivity comparison."""
    rho_mmlu = results["primary"]["partial_rho"]
    rho_wino = results["sensitivity"]["partial_rho"] if results["sensitivity"] else None

    labels = ["MMLU control"]
    values = [rho_mmlu]
    if rho_wino is not None:
        labels.append("Winogrande control")
        values.append(rho_wino)

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=["steelblue", "darkorange"][:len(labels)], alpha=0.8)
    ax.axhline(GATE_RHO, linestyle="--", color="orange", linewidth=1.5, label=f"Gate: {GATE_RHO}")
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Partial Spearman ρ")
    ax.set_title("Sensitivity Analysis: Capability Control Variable")
    ax.legend()

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.02, f"{val:.3f}", ha="center", va="bottom")

    save_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(save_dir / "sensitivity_comparison.png", dpi=150)
    plt.close(fig)


def plot_score_distributions(df: pd.DataFrame, save_dir: Path) -> None:
    """Box plots of BBQ-Disambig and BBQ-Ambig scores across models."""
    fig, ax = plt.subplots(figsize=(7, 5))
    df_melt = df[["bbq_disambig", "bbq_ambig"]].melt(
        var_name="Benchmark", value_name="Score"
    )
    df_melt["Benchmark"] = df_melt["Benchmark"].map({
        "bbq_disambig": "BBQ-Disambig",
        "bbq_ambig": "BBQ-Ambig",
    })
    sns.boxplot(data=df_melt, x="Benchmark", y="Score", palette=["lightblue", "lightsalmon"], ax=ax)
    ax.set_title("Score Distributions Across LLMs")
    ax.set_ylabel("Accuracy")

    save_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(save_dir / "score_distributions.png", dpi=150)
    plt.close(fig)


def plot_mmlu_vs_fairness(df: pd.DataFrame, save_dir: Path) -> None:
    """MMLU rank vs BBQ-Disambig rank scatter (shows capability confound)."""
    df_plot = df.copy()
    df_plot["rank_mmlu"] = df_plot["mmlu"].rank(ascending=False)
    df_plot["rank_dis"] = df_plot["bbq_disambig"].rank(ascending=False)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df_plot["rank_mmlu"], df_plot["rank_dis"], s=80, color="purple", alpha=0.7, zorder=5)

    for _, row in df_plot.iterrows():
        ax.annotate(row["model_name"], (row["rank_mmlu"], row["rank_dis"]),
                    textcoords="offset points", xytext=(5, 3), fontsize=7)

    m, b = np.polyfit(df_plot["rank_mmlu"], df_plot["rank_dis"], 1)
    x_fit = np.linspace(df_plot["rank_mmlu"].min(), df_plot["rank_mmlu"].max(), 100)
    ax.plot(x_fit, m * x_fit + b, "g--", alpha=0.7, label="Fit")

    ax.set_xlabel("MMLU Rank (1=highest capability)")
    ax.set_ylabel("BBQ-Disambig Rank (1=highest fairness)")
    ax.set_title("MMLU vs BBQ-Disambig Rank (Why Control is Needed)")
    ax.legend()

    save_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(save_dir / "mmlu_vs_fairness.png", dpi=150)
    plt.close(fig)


def generate_all_figures(df: pd.DataFrame, results: dict, save_dir: Path) -> None:
    """Generate all 5 H-M1 figures."""
    plot_gate_metrics(results, save_dir)
    plot_rank_scatter(df, results, save_dir)
    plot_sensitivity(results, save_dir)
    plot_score_distributions(df, save_dir)
    plot_mmlu_vs_fairness(df, save_dir)
    print(f"Generated 5 figures in {save_dir}")
