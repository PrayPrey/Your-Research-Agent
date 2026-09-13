"""4 figures: tau bar, time series, p-value heatmap, cohort diagnostics."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from pathlib import Path


def _savefig(fig, outdir: str, name: str) -> str:
    path = Path(outdir) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def plot_tau_bar(results: dict, outdir: str) -> str:
    """Figure 1: bar chart of tau values with significance markers."""
    proxies = [k for k in results if k not in ("overall_pass", "n_passing", "effect_pass")]
    taus = [results[p]["tau"] for p in proxies]
    colors = ["#2196F3" if results[p]["pass"] else "#9E9E9E" for p in proxies]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(proxies, taus, color=colors, edgecolor="black", linewidth=0.8)
    ax.axhline(0, color="black", linewidth=1)
    ax.axhline(0.2, color="red", linewidth=1, linestyle="--", label="|τ|=0.2 threshold")
    ax.axhline(-0.2, color="red", linewidth=1, linestyle="--")

    for bar, p_name in zip(bars, proxies):
        if results[p_name]["pass"]:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.01 * np.sign(bar.get_height() + 1e-9),
                    "*", ha="center", va="bottom", fontsize=14, color="darkblue")

    ax.set_ylabel("Kendall τ")
    ax.set_title("H-E1: Mann-Kendall τ per Behavioral Proxy\n(* = p<0.05, blue = passing)")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return _savefig(fig, outdir, "fig1_tau_bar.png")


def plot_time_series(
    token_series: dict,
    correction_series: dict,
    entropy_series: dict,
    outdir: str,
) -> str:
    """Figure 2: monthly mean per proxy with linear trend overlay."""
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=False)

    series_map = [
        (token_series, "Mean Prompt Token Count", "Token Count", "tab:blue"),
        (correction_series, "Mean Correction Frequency", "Freq", "tab:orange"),
        (entropy_series, "Mean Shannon Entropy (LMSYS)", "Entropy (bits)", "tab:green"),
    ]

    for ax, (series, title, ylabel, color) in zip(axes, series_map):
        if not series:
            ax.set_title(f"{title} — no data")
            continue
        bins = sorted(series.keys())
        vals = [series[b] for b in bins]
        x = np.arange(len(bins))
        ax.plot(x, vals, "o-", color=color, linewidth=1.5, markersize=4)
        # Trend line
        if len(x) >= 2:
            z = np.polyfit(x, vals, 1)
            ax.plot(x, np.poly1d(z)(x), "--", color="red", linewidth=1, alpha=0.7)
        ax.set_xticks(x)
        ax.set_xticklabels(bins, rotation=45, ha="right", fontsize=7)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_title(title, fontsize=10)

    fig.suptitle("H-E1: Behavioral Proxy Time Series (2023-01 to 2024-12)", fontsize=11)
    fig.tight_layout()
    return _savefig(fig, outdir, "fig2_time_series.png")


def plot_pvalue_heatmap(results: dict, outdir: str) -> str:
    """Figure 3: p-value heatmap (proxies × significance)."""
    proxies = [k for k in results if k not in ("overall_pass", "n_passing", "effect_pass")]
    p_values = [[results[p]["p_value"]] for p in proxies]

    fig, ax = plt.subplots(figsize=(4, max(3, len(proxies))))
    im = ax.imshow(p_values, aspect="auto", cmap="RdYlGn_r", vmin=0, vmax=0.1)
    ax.set_yticks(range(len(proxies)))
    ax.set_yticklabels(proxies)
    ax.set_xticks([0])
    ax.set_xticklabels(["p-value"])
    ax.axhline(-0.5, color="black")

    for i, p in enumerate(proxies):
        pv = results[p]["p_value"]
        ax.text(0, i, f"{pv:.4f}", ha="center", va="center",
                color="black", fontsize=10, fontweight="bold")

    plt.colorbar(im, ax=ax, fraction=0.05, label="p-value")
    ax.set_title("H-E1: Mann-Kendall p-values\n(green<0.05 = significant)")
    fig.tight_layout()
    return _savefig(fig, outdir, "fig3_pvalue_heatmap.png")


def plot_cohort_diagnostics(
    cohort_df: pd.DataFrame,
    lmsys_df: pd.DataFrame,
    outdir: str,
) -> str:
    """Figure 4: cohort size histogram + LMSYS vote count per bin."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Left: cohort size distribution
    ax = axes[0]
    if not cohort_df.empty and "cohort_size" in cohort_df.columns:
        sizes = cohort_df.drop_duplicates("hashed_ip")["cohort_size"]
        ax.hist(sizes, bins=min(20, sizes.nunique()), color="#2196F3", edgecolor="black")
        ax.set_xlabel("Number of Monthly Bins per User")
        ax.set_ylabel("Number of Users")
        ax.set_title(f"WildChat Cohort Size Distribution\n(n={sizes.shape[0]:,} unique IPs)")
    else:
        ax.set_title("WildChat Cohort — no data")

    # Right: LMSYS vote count per bin
    ax = axes[1]
    if not lmsys_df.empty:
        bin_counts = lmsys_df.groupby("monthly_bin").size().sort_index()
        ax.bar(range(len(bin_counts)), bin_counts.values, color="#4CAF50", edgecolor="black")
        ax.set_xticks(range(len(bin_counts)))
        ax.set_xticklabels(bin_counts.index, rotation=45, ha="right", fontsize=7)
        ax.set_ylabel("Vote Count")
        ax.set_title("LMSYS Vote Count per Monthly Bin")
    else:
        ax.set_title("LMSYS — no data")

    fig.suptitle("H-E1: Dataset Diagnostics", fontsize=11)
    fig.tight_layout()
    return _savefig(fig, outdir, "fig4_cohort_diagnostics.png")
