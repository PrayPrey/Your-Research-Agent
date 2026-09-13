"""H-M1: Five required figures for proxy-gold divergence mechanism verification."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats as _stats


def plot_trajectory_dual_axis(
    df: pd.DataFrame,
    results: dict,
    out_dir: str,
    dpi: int = 150,
) -> str:
    fig, ax1 = plt.subplots(figsize=(9, 5))

    ax1.set_xlabel("KL Divergence (nats)")
    ax1.set_ylabel("RM Score (proxy)", color="steelblue")
    ax1.plot(df["kl_budget"], df["rm_score"],
             marker="o", color="steelblue", label="RM Score")
    ax1.tick_params(axis="y", labelcolor="steelblue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Gold Preference Rate", color="crimson")
    ax2.plot(df["kl_budget"], df["gold_preference"],
             marker="s", linestyle="--", color="crimson", label="Gold Preference")
    ax2.tick_params(axis="y", labelcolor="crimson")

    peak_kl = results["peak_kl"]
    ax1.axvline(x=peak_kl, color="gray", linestyle=":", alpha=0.7,
                label=f"Peak KL = {peak_kl:.1f} nats")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)

    status = "PASS" if results["gate_pass"] else "FAIL"
    ax1.set_title(f"H-M1: Proxy-Gold Trajectory — Coste 2023 [{status}]")
    fig.tight_layout()

    out_path = Path(out_dir) / "trajectory_dual_axis.png"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return str(out_path)


def plot_divergence_gap(
    kl: np.ndarray,
    divergence_curve: np.ndarray,
    out_dir: str,
    dpi: int = 150,
) -> str:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(kl, divergence_curve, marker="D", color="darkorange", linewidth=2,
            label="RM - Gold Preference")
    ax.axhline(y=0, color="black", linestyle="--", alpha=0.5, label="Zero line")
    ax.fill_between(kl, divergence_curve, 0,
                    where=(divergence_curve > 0), alpha=0.15, color="darkorange")
    ax.set_xlabel("KL Divergence (nats)")
    ax.set_ylabel("Divergence (RM Score - Gold Preference)")
    ax.set_title("H-M1: Proxy-Gold Divergence Gap vs KL Budget")
    ax.legend()
    ax.annotate(
        f"Final: {divergence_curve[-1]:.3f}",
        xy=(kl[-1], divergence_curve[-1]),
        xytext=(-60, 10), textcoords="offset points",
        fontsize=9, arrowprops=dict(arrowstyle="->", color="gray"),
    )
    fig.tight_layout()
    out_path = Path(out_dir) / "divergence_gap.png"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return str(out_path)


def plot_spearman_scatter(
    kl: np.ndarray,
    rm: np.ndarray,
    rho: float,
    p_rho: float,
    out_dir: str,
    dpi: int = 150,
) -> str:
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(kl, rm, color="steelblue", zorder=5, s=60, label="Observations")

    slope, intercept, *_ = _stats.linregress(kl, rm)
    kl_line = np.linspace(kl.min(), kl.max(), 100)
    ax.plot(kl_line, slope * kl_line + intercept,
            color="navy", linestyle="--", alpha=0.6, label="OLS trend")

    ax.set_xlabel("KL Divergence (nats)")
    ax.set_ylabel("RM Score")
    p_str = f"p={p_rho:.4f}" if p_rho >= 0.001 else "p<0.001"
    ax.set_title(f"H-M1: RM Score vs KL Budget\nSpearman rho={rho:.3f}, {p_str}")
    ax.legend()
    fig.tight_layout()
    out_path = Path(out_dir) / "spearman_scatter.png"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return str(out_path)


def plot_gao_overlay(
    gao_df: pd.DataFrame,
    out_dir: str,
    dpi: int = 150,
) -> str:
    fig, ax1 = plt.subplots(figsize=(9, 5))

    ax1.set_xlabel("KL Divergence (nats)")
    ax1.set_ylabel("RM Score (proxy)", color="steelblue")
    ax1.plot(gao_df["kl_budget"], gao_df["rm_score"],
             marker="o", color="steelblue", label="RM Score")
    ax1.tick_params(axis="y", labelcolor="steelblue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Gold Preference Rate", color="crimson")
    ax2.plot(gao_df["kl_budget"], gao_df["gold_preference"],
             marker="s", linestyle="--", color="crimson", label="Gold Preference")
    ax2.tick_params(axis="y", labelcolor="crimson")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=9)

    ax1.set_title("H-M1: Gao 2023 Preliminary Check [Dual-Axis]")
    fig.tight_layout()
    out_path = Path(out_dir) / "gao_overlay.png"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return str(out_path)


def plot_gate_metrics(results: dict, out_dir: str, dpi: int = 150) -> str:
    metrics = {
        "rho(KL,RM)": (results["rho_rm_kl"], 0.8, results["monotone_pass"]),
        "Reversal\nConfirmed": (float(results["reversal_confirmed"]), 1.0, results["reversal_confirmed"]),
        "Divergence\nFinal": (results["divergence_final"], 0.0, results["divergence_positive"]),
    }

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["forestgreen" if v[2] else "tomato" for v in metrics.values()]
    x = list(range(len(metrics)))
    ax.bar(x, [v[0] for v in metrics.values()], color=colors, alpha=0.7, width=0.5)

    for i, (label, (val, threshold, passed)) in enumerate(metrics.items()):
        ax.hlines(y=threshold, xmin=i - 0.3, xmax=i + 0.3,
                  colors="black", linestyles="--", linewidth=1.5)
        ax.text(i, threshold + max(abs(threshold) * 0.05, 0.03),
                f"threshold={threshold}", ha="center", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(list(metrics.keys()))
    ax.set_ylabel("Value")
    gate = "PASS" if results["gate_pass"] else "FAIL"
    ax.set_title(f"H-M1 Gate Metrics — {gate}")
    fig.tight_layout()

    out_path = Path(out_dir) / "gate_metrics.png"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return str(out_path)
