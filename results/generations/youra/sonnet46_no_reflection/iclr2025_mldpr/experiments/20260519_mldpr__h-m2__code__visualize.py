"""H-M2: Visualization — 5 Figures."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DOMAIN_COLORS = {"cv": "#2196F3", "nlp": "#FF5722", "tabular": "#4CAF50"}


def _ensure_dir(output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)


def plot_gate_metrics(domain_results: dict, output_dir: str,
                      threshold: float = 0.60, filename: str = "gate_metrics_fraction_leading.png") -> None:
    """Bar chart: fraction_leading per domain vs. 0.60 threshold line. [MANDATORY]"""
    _ensure_dir(output_dir)
    domains = list(domain_results.keys())
    fractions = [float(domain_results[d].get("fraction_leading") or 0.0) for d in domains]
    colors = [DOMAIN_COLORS.get(d, "#9E9E9E") for d in domains]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(domains, fractions, color=colors, alpha=0.8, edgecolor="black")
    ax.axhline(threshold, color="red", linestyle="--", linewidth=2, label=f"Gate threshold ({threshold:.0%})")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Fraction Leading (≥12 months)")
    ax.set_title("H-M2: Fraction of Benchmarks with H_d Leading Indicator ≥12 months\n(SHOULD_WORK Gate)")
    ax.legend()
    for bar, val in zip(bars, fractions):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{val:.2f}", ha="center", va="bottom", fontsize=11)
    plt.tight_layout()
    path = os.path.join(output_dir, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"✓ Saved: {path}")


def plot_km_curves(domain_onset_dfs: dict, output_dir: str,
                   filename: str = "km_lead_time_curves.png") -> None:
    """KM survival curves per domain."""
    from lifelines import KaplanMeierFitter
    _ensure_dir(output_dir)
    fig, ax = plt.subplots(figsize=(10, 6))
    for domain, onset_df in domain_onset_dfs.items():
        if len(onset_df) == 0:
            continue
        T = onset_df["lead_months"].fillna(0).clip(lower=0)
        E = onset_df["onset_observed"].astype(int)
        if E.sum() < 2:
            continue
        kmf = KaplanMeierFitter()
        kmf.fit(T, event_observed=E, label=domain)
        kmf.plot_survival_function(ax=ax, color=DOMAIN_COLORS.get(domain, "#9E9E9E"), ci_show=True)
    ax.axvline(12, color="red", linestyle="--", linewidth=1.5, label="12-month threshold")
    ax.set_xlabel("Lead Time (months)")
    ax.set_ylabel("Survival Probability")
    ax.set_title("H-M2: Kaplan-Meier Lead Time Distribution by Domain")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(output_dir, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"✓ Saved: {path}")


def plot_signal_timeline(panel_df: pd.DataFrame, collapse_df: pd.DataFrame,
                         benchmark_ids: list, output_dir: str,
                         filename: str = "signal_emergence_timeline.png") -> None:
    """Aligned time series for representative benchmarks."""
    _ensure_dir(output_dir)
    hd_cols = [c for c in ["hd_cv", "hd_nlp", "hd_tabular"] if c in panel_df.columns]
    if not hd_cols or not benchmark_ids:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.text(0.5, 0.5, "No timeline data available", ha="center", va="center", transform=ax.transAxes)
        plt.savefig(os.path.join(output_dir, filename), dpi=150)
        plt.close()
        return
    n_bm = min(3, len(benchmark_ids))
    fig, axes = plt.subplots(n_bm, 1, figsize=(12, 4 * n_bm), sharex=False)
    if n_bm == 1:
        axes = [axes]
    for i, bm_id in enumerate(benchmark_ids[:n_bm]):
        ax = axes[i]
        bm_data = panel_df[panel_df["benchmark_id"] == bm_id].sort_values("quarter")
        for hd_col in hd_cols:
            domain = hd_col.replace("hd_", "")
            if hd_col in bm_data.columns:
                ax.plot(range(len(bm_data)), bm_data[hd_col].values,
                        label=domain, color=DOMAIN_COLORS.get(domain, "#9E9E9E"), marker="o", ms=3)
        if len(collapse_df) > 0:
            cr = collapse_df[collapse_df["benchmark_id"] == bm_id]
            if not cr.empty:
                cq = str(cr["collapse_quarter"].iloc[0])
                quarters = list(bm_data["quarter"].astype(str))
                if cq in quarters:
                    ax.axvline(quarters.index(cq), color="red", linestyle="--", label="Collapse")
        ax.set_title(f"Benchmark: {bm_id}")
        ax.set_ylabel("H_d signal")
        ax.legend(fontsize=8)
    plt.suptitle("H-M2: Signal Emergence Timeline", y=1.01)
    plt.tight_layout()
    path = os.path.join(output_dir, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ Saved: {path}")


def plot_auc_comparison(auc_results: dict, output_dir: str,
                        filename: str = "auc_comparison.png") -> None:
    """Grouped bar chart: auc_lead vs auc_concurrent per domain."""
    _ensure_dir(output_dir)
    domains = list(auc_results.keys())
    auc_leads = [float(auc_results[d].get("auc_lead") or 0.0) for d in domains]
    auc_concs = [float(auc_results[d].get("auc_concurrent") or 0.0) for d in domains]
    x = np.arange(len(domains))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width / 2, auc_leads, width, label="AUC Lead (t-24mo)", alpha=0.8, color="#1976D2")
    ax.bar(x + width / 2, auc_concs, width, label="AUC Concurrent (t)", alpha=0.8, color="#F44336")
    ax.axhline(0.65, color="green", linestyle="--", label="AUC target (0.65)")
    ax.set_xticks(x)
    ax.set_xticklabels(domains)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("AUC")
    ax.set_title("H-M2: AUC Comparison — Leading vs. Concurrent H_d Signal")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(output_dir, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"✓ Saved: {path}")


def plot_mann_whitney_boxplot(panel_df: pd.DataFrame, compressed_ids,
                              output_dir: str, filename: str = "mann_whitney_boxplot.png") -> None:
    """Side-by-side boxplot: H_d magnitude compressed vs. non-compressed per domain."""
    _ensure_dir(output_dir)
    hd_cols = [c for c in ["hd_cv", "hd_nlp", "hd_tabular"] if c in panel_df.columns]
    if not hd_cols:
        return
    fig, axes = plt.subplots(1, len(hd_cols), figsize=(5 * len(hd_cols), 5))
    if len(hd_cols) == 1:
        axes = [axes]
    for ax, hd_col in zip(axes, hd_cols):
        domain = hd_col.replace("hd_", "")
        bm_means = panel_df.groupby("benchmark_id")[hd_col].mean().dropna()
        comp = bm_means[bm_means.index.isin(compressed_ids)].values
        non_comp = bm_means[~bm_means.index.isin(compressed_ids)].values
        ax.boxplot([comp, non_comp], labels=["Compressed", "Non-compressed"],
                   patch_artist=True,
                   boxprops=dict(facecolor=DOMAIN_COLORS.get(domain, "#9E9E9E"), alpha=0.6))
        ax.set_title(f"{domain.upper()}: H_d magnitude")
        ax.set_ylabel("Mean H_d signal")
    plt.suptitle("H-M2: Mann-Whitney U — H_d Magnitude Comparison")
    plt.tight_layout()
    path = os.path.join(output_dir, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"✓ Saved: {path}")


def generate_all_figures(panel_df: pd.DataFrame, collapse_df: pd.DataFrame,
                         domain_onset_dfs: dict, domain_km_results: dict,
                         stat_results: dict, ablation_results: list,
                         compressed_ids, output_dir: str) -> None:
    """Orchestrate all 5 figure outputs."""
    print("Generating figures...")
    domain_fraction_results = {
        d: {"fraction_leading": v.get("fraction_leading", 0.0)}
        for d, v in domain_km_results.items() if isinstance(v, dict)
    }
    plot_gate_metrics(domain_fraction_results, output_dir)
    plot_km_curves(domain_onset_dfs, output_dir)
    representative_ids = list(compressed_ids)[:3] if len(list(compressed_ids)) >= 1 else []
    plot_signal_timeline(panel_df, collapse_df, representative_ids, output_dir)
    auc_results = {d: stat_results.get(d, {}).get("auc", {}) for d in ["cv", "nlp", "tabular"]}
    plot_auc_comparison(auc_results, output_dir)
    plot_mann_whitney_boxplot(panel_df, compressed_ids, output_dir)
    print(f"✓ All figures saved to {output_dir}")
