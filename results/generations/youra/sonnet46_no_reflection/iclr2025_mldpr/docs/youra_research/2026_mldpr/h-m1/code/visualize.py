"""H-M1: Visualization — 6 figures for causal mechanism analysis."""
import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")


def _ensure_dir(output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)


def plot_gate_metrics(
    spearman_result: dict,
    granger_agg: dict,
    output_dir: str,
) -> None:
    """Bar chart: target vs actual Spearman rho and Granger p at lag=2. Saves: gate_metrics.png"""
    _ensure_dir(output_dir)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Spearman rho
    rho = spearman_result.get("rho", 0.0) or 0.0
    axes[0].bar(["Target (0.4)", "Actual"], [0.4, float(rho)],
                color=["#90CAF9", "#2196F3" if float(rho) > 0.4 else "#EF9A9A"])
    axes[0].axhline(0.4, color="red", linestyle="--", linewidth=1.5, label="Target")
    axes[0].set_title("Spearman ρ: Target vs Actual")
    axes[0].set_ylabel("Spearman ρ")
    axes[0].set_ylim(0, max(1.0, float(rho) * 1.2))

    # Granger p at lag=2
    min_p = granger_agg.get("min_p_lag2") or 1.0
    axes[1].bar(["Target (0.05)", "Actual Min-p"],
                [0.05, float(min_p)],
                color=["#90CAF9", "#4CAF50" if float(min_p) < 0.05 else "#EF9A9A"])
    axes[1].axhline(0.05, color="red", linestyle="--", linewidth=1.5, label="Target")
    axes[1].set_title("Granger p-value at lag=2: Target vs Actual")
    axes[1].set_ylabel("p-value")
    axes[1].set_ylim(0, min(1.0, max(0.1, float(min_p) * 1.2)))

    plt.suptitle("H-M1 Gate Metrics", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "gate_metrics.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved gate_metrics.png")


def plot_scatter_submission_compression(
    panel_df: pd.DataFrame,
    output_dir: str,
) -> None:
    """Scatter: cumulative_count vs compression_event, colored by domain. Saves: scatter_submission_compression.png"""
    _ensure_dir(output_dir)
    fig, ax = plt.subplots(figsize=(10, 6))

    domain_col = "domain" if "domain" in panel_df.columns else None
    colors = {"cv": "#2196F3", "nlp": "#FF5722", "tabular": "#4CAF50", "other": "#9E9E9E"}

    plot_df = panel_df.dropna(subset=["cumulative_count", "compression_event"])
    if domain_col and domain_col in plot_df.columns:
        for domain, grp in plot_df.groupby(domain_col):
            ax.scatter(
                grp["cumulative_count"], grp["compression_event"],
                alpha=0.3, label=domain, color=colors.get(domain, "#9E9E9E"), s=20,
            )
        ax.legend(title="Domain")
    else:
        ax.scatter(plot_df["cumulative_count"], plot_df["compression_event"], alpha=0.3, s=20)

    ax.set_xlabel("Cumulative Submission Count")
    ax.set_ylabel("Compression Event (0/1)")
    ax.set_title("Submission Count vs Score Compression Events")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "scatter_submission_compression.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved scatter_submission_compression.png")


def plot_lag_profile(
    granger_results: dict,
    reverse_results: dict,
    output_dir: str,
) -> None:
    """Median Granger p-values at lags 1-4 for forward and reverse. Saves: lag_profile.png"""
    _ensure_dir(output_dir)
    lags = [1, 2, 3, 4]

    def median_p_per_lag(results, lag):
        vals = [v[lag] for v in results.values() if v is not None and lag in v]
        return float(np.median(vals)) if vals else 1.0

    fwd_ps = [median_p_per_lag(granger_results, l) for l in lags]
    rev_ps = [median_p_per_lag(reverse_results, l) for l in lags]

    x = np.arange(len(lags))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, fwd_ps, width, label="Forward (count→compression)", color="#2196F3", alpha=0.8)
    ax.bar(x + width/2, rev_ps, width, label="Reverse (compression→count)", color="#FF5722", alpha=0.8)
    ax.axhline(0.05, color="red", linestyle="--", linewidth=1.5, label="p=0.05 threshold")
    ax.set_xlabel("Lag (quarters)")
    ax.set_ylabel("Median p-value")
    ax.set_title("Granger Causality Lag Profile (Forward vs Reverse)")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Lag {l}" for l in lags])
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "lag_profile.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved lag_profile.png")


def plot_timeseries_overlay(
    panel_df: pd.DataFrame,
    output_dir: str,
    example_benchmark: str = None,
) -> None:
    """Dual-panel time series for one benchmark. Saves: timeseries_overlay.png"""
    _ensure_dir(output_dir)
    if example_benchmark is None:
        # Auto-select benchmark with most quarters and non-null variance
        counts = panel_df.dropna(subset=["score_var_top10"]).groupby("benchmark_id").size()
        if len(counts) == 0:
            plt.figure()
            plt.text(0.5, 0.5, "No data available", ha="center")
            plt.savefig(os.path.join(output_dir, "timeseries_overlay.png"), dpi=150)
            plt.close()
            return
        example_benchmark = counts.idxmax()

    bm_df = panel_df[panel_df["benchmark_id"] == example_benchmark].sort_values("quarter")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ax1.plot(range(len(bm_df)), bm_df["cumulative_count"], "b-o", markersize=4)
    ax1.set_ylabel("Cumulative Submissions")
    ax1.set_title(f"Benchmark: {example_benchmark[:60]}")

    ax2.plot(range(len(bm_df)), bm_df["score_var_top10"], "r-o", markersize=4)
    ax2.set_ylabel("Score Variance (top-10)")
    ax2.set_xlabel("Quarter Index")
    quarter_labels = bm_df["quarter"].tolist()
    tick_step = max(1, len(quarter_labels) // 8)
    ax2.set_xticks(range(0, len(quarter_labels), tick_step))
    ax2.set_xticklabels(quarter_labels[::tick_step], rotation=45)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "timeseries_overlay.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved timeseries_overlay.png")


def plot_compression_distribution(
    panel_df: pd.DataFrame,
    output_dir: str,
) -> None:
    """Histogram of cumulative_count at first compression event. Saves: compression_distribution.png"""
    _ensure_dir(output_dir)
    if "compression_event" not in panel_df.columns:
        return

    first_compression = (
        panel_df[panel_df["compression_event"] == 1.0]
        .groupby("benchmark_id")["cumulative_count"]
        .first()
        .dropna()
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    if len(first_compression) > 0:
        ax.hist(first_compression, bins=30, color="#2196F3", alpha=0.7, edgecolor="white")
    ax.set_xlabel("Cumulative Submission Count at First Compression Event")
    ax.set_ylabel("Number of Benchmarks")
    ax.set_title(f"Distribution of First Compression Event ({len(first_compression)} benchmarks)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "compression_distribution.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved compression_distribution.png")


def plot_reverse_causality(
    forward_results: dict,
    reverse_results: dict,
    output_dir: str,
) -> None:
    """Bar chart: forward vs reverse Granger p-values at lag=2. Saves: reverse_causality.png"""
    _ensure_dir(output_dir)

    def median_p_lag2(results):
        vals = [v.get(2, 1.0) for v in results.values() if v is not None]
        return float(np.median(vals)) if vals else 1.0

    fwd_p = median_p_lag2(forward_results)
    rev_p = median_p_lag2(reverse_results)

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(
        ["Forward\n(count→compression)", "Reverse\n(compression→count)"],
        [fwd_p, rev_p],
        color=["#4CAF50" if fwd_p < 0.05 else "#EF9A9A",
               "#EF9A9A" if rev_p >= 0.05 else "#FF5722"],
        alpha=0.8,
    )
    ax.axhline(0.05, color="red", linestyle="--", linewidth=1.5, label="p=0.05 threshold")
    ax.set_ylabel("Median Granger p-value at Lag=2")
    ax.set_title("Causal Direction: Forward vs Reverse Granger Test")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "reverse_causality.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved reverse_causality.png")


def generate_all_figures(
    panel_df: pd.DataFrame,
    spearman_result: dict,
    granger_results: dict,
    reverse_results: dict,
    granger_agg: dict,
    output_dir: str,
) -> None:
    """Call all 6 plot functions. Creates output_dir if not exists."""
    _ensure_dir(output_dir)
    print(f"Generating figures in {output_dir}...")
    plot_gate_metrics(spearman_result, granger_agg, output_dir)
    plot_scatter_submission_compression(panel_df, output_dir)
    plot_lag_profile(granger_results, reverse_results, output_dir)
    plot_timeseries_overlay(panel_df, output_dir)
    plot_compression_distribution(panel_df, output_dir)
    plot_reverse_causality(granger_results, reverse_results, output_dir)
    print("All figures generated.")
