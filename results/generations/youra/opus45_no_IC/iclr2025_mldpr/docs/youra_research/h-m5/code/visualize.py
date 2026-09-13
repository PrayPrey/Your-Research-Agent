"""H-M5 Visualization: Required figures."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats


def plot_gate_metrics(fe_result: dict, out_path: str) -> None:
    """Beta coefficient with 95% CI errorbar."""
    fig, ax = plt.subplots(figsize=(8, 6))
    beta = fe_result["beta"]
    ci_lower = fe_result["conf_int_lower"]
    ci_upper = fe_result["conf_int_upper"]
    ax.errorbar([0], [beta], yerr=[[beta - ci_lower], [ci_upper - beta]], fmt="o", capsize=5, markersize=10)
    ax.axhline(0, color="red", linestyle="--", label="Null (β=0)")
    ax.set_xlim(-0.5, 0.5)
    ax.set_xticks([])
    ax.set_ylabel("β(HHI_{t-1})")
    ax.set_title(f"H-M5: Panel FE Coefficient\nβ = {beta:.4f}, p = {fe_result['p_value']:.4f}")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_hhi_entropy_scatter(df: pd.DataFrame, out_path: str) -> None:
    """Scatter hhi_lag1 vs entropy, colored by venue."""
    fig, ax = plt.subplots(figsize=(8, 6))
    df_plot = df.reset_index()
    sns.scatterplot(data=df_plot, x="hhi_lag1", y="entropy", hue="venue", ax=ax, s=80)
    sns.regplot(data=df_plot, x="hhi_lag1", y="entropy", scatter=False, ax=ax, color="gray", line_kws={"linestyle": "--"})
    ax.set_xlabel("HHI_{t-1}")
    ax.set_ylabel("Entropy_t")
    ax.set_title("H-M5: Lagged HHI vs Entropy")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_time_series(df: pd.DataFrame, out_path: str) -> None:
    """Dual y-axis: HHI and entropy per venue over years."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=False)
    df_plot = df.reset_index()
    for i, venue in enumerate(df_plot["venue"].unique()):
        vdf = df_plot[df_plot["venue"] == venue].sort_values("year")
        ax1 = axes[i]
        ax2 = ax1.twinx()
        ax1.plot(vdf["year"], vdf["hhi"], "b-o", label="HHI")
        ax2.plot(vdf["year"], vdf["entropy"], "r-s", label="Entropy")
        ax1.set_xlabel("Year")
        ax1.set_ylabel("HHI", color="blue")
        ax2.set_ylabel("Entropy", color="red")
        ax1.set_title(venue)
        ax1.tick_params(axis="y", labelcolor="blue")
        ax2.tick_params(axis="y", labelcolor="red")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_granger_heatmap(granger_result: dict, out_path: str) -> None:
    """Heatmap of p-values for both directions."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    for i, (key, title) in enumerate([("hhi_to_entropy", "HHI → Entropy"), ("entropy_to_hhi", "Entropy → HHI")]):
        data = granger_result[key]
        if not data:
            axes[i].text(0.5, 0.5, "No data", ha="center", va="center")
            axes[i].set_title(title)
            continue
        venues = list(data.keys())
        lags = list(range(1, 3))
        matrix = [[data.get(v, {}).get(l, np.nan) for l in lags] for v in venues]
        sns.heatmap(matrix, ax=axes[i], annot=True, fmt=".3f", xticklabels=lags, yticklabels=venues, cmap="RdYlGn_r", vmin=0, vmax=0.1)
        axes[i].set_xlabel("Lag")
        axes[i].set_ylabel("Venue")
        axes[i].set_title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_residual_diagnostics(fe_result: dict, out_path: str) -> None:
    """QQ plot + residuals vs fitted."""
    res = fe_result["results_obj"]
    resids = res.resids.values.flatten()
    fitted = res.fitted_values.values.flatten()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    stats.probplot(resids, dist="norm", plot=axes[0])
    axes[0].set_title("Q-Q Plot")
    axes[1].scatter(fitted, resids, alpha=0.7)
    axes[1].axhline(0, color="red", linestyle="--")
    axes[1].set_xlabel("Fitted Values")
    axes[1].set_ylabel("Residuals")
    axes[1].set_title("Residuals vs Fitted")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def generate_all(fe_result: dict, granger_result: dict, df: pd.DataFrame, out_dir: str) -> None:
    """Generate all figures."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    plot_gate_metrics(fe_result, str(out / "gate_metrics.png"))
    plot_hhi_entropy_scatter(df, str(out / "hhi_entropy_scatter.png"))
    plot_time_series(df, str(out / "time_series.png"))
    plot_granger_heatmap(granger_result, str(out / "granger_heatmap.png"))
    plot_residual_diagnostics(fe_result, str(out / "residual_diagnostics.png"))
