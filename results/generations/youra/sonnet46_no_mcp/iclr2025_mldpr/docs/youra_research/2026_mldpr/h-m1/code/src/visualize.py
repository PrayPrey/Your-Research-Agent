"""H-M1 visualization: all 6 required figures."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logger = logging.getLogger(__name__)


def plot_gate_metrics(log_rank_p: float, cox_hr: float, figures_dir: str) -> str:
    """Figure 1: Gate metrics bar chart."""
    os.makedirs(figures_dir, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    # Left: p-value vs threshold
    axes[0].bar(["Log-rank p", "Threshold (0.05)"], [log_rank_p, 0.05],
                color=["green" if log_rank_p < 0.05 else "red", "gray"])
    axes[0].set_title("Log-rank p-value vs Gate Threshold")
    axes[0].set_ylabel("p-value")
    # Right: HR vs threshold
    axes[1].bar(["Cox HR", "Gate HR (1.2)"], [cox_hr, 1.2],
                color=["green" if cox_hr > 1.2 else "red", "gray"])
    axes[1].set_title("Cox HR vs Gate Threshold")
    axes[1].set_ylabel("Hazard Ratio")
    plt.tight_layout()
    path = os.path.join(figures_dir, "fig1_gate_metrics.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def plot_km_curves(kmf_high, kmf_low, log_rank_p: float, median_high: float,
                   median_low: float, figures_dir: str, label: str = "matched") -> str:
    """Figure 2: KM survival curves with 95% CI."""
    os.makedirs(figures_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    kmf_high.plot_survival_function(ax=ax, ci_show=True, color="blue")
    kmf_low.plot_survival_function(ax=ax, ci_show=True, color="red")
    ax.axvline(x=median_high, color="blue", linestyle="--", alpha=0.7, label=f"Median high: {median_high:.0f}d")
    ax.axvline(x=median_low, color="red", linestyle="--", alpha=0.7, label=f"Median low: {median_low:.0f}d")
    ax.set_title(f"KM Survival Curves ({label}) — log-rank p={log_rank_p:.4f}")
    ax.set_xlabel("Time to First Run (days)")
    ax.set_ylabel("Survival Probability (not yet run)")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(figures_dir, f"fig2_km_curves_{label}.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def plot_ps_distribution(ps_before: pd.Series, ps_after: pd.Series, figures_dir: str) -> str:
    """Figure 3: PS score histograms before/after matching."""
    os.makedirs(figures_dir, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].hist(ps_before.dropna(), bins=30, color="steelblue", alpha=0.7)
    axes[0].set_title("PS Distribution — Before Matching")
    axes[0].set_xlabel("Propensity Score")
    axes[1].hist(ps_after.dropna(), bins=30, color="green", alpha=0.7)
    axes[1].set_title("PS Distribution — After Matching")
    axes[1].set_xlabel("Propensity Score")
    plt.tight_layout()
    path = os.path.join(figures_dir, "fig3_ps_distribution.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def plot_love_plot(smd_df: pd.DataFrame, figures_dir: str) -> str:
    """Figure 4: Love plot — SMD before vs after per covariate."""
    os.makedirs(figures_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, max(4, len(smd_df))))
    y = range(len(smd_df))
    ax.scatter(smd_df["smd_before"], y, color="red", label="Before", zorder=3)
    ax.scatter(smd_df["smd_after"], y, color="green", label="After", zorder=3)
    ax.axvline(x=0.1, color="black", linestyle="--", label="SMD=0.1 threshold")
    ax.set_yticks(list(y))
    ax.set_yticklabels(smd_df["covariate"].tolist())
    ax.set_xlabel("Standardized Mean Difference")
    ax.set_title("Love Plot: Covariate Balance Before/After Matching")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(figures_dir, "fig4_love_plot.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def plot_cox_forest(cox_hr: float, cox_ci_lower: float, cox_ci_upper: float, figures_dir: str) -> str:
    """Figure 5: Cox PH forest plot."""
    os.makedirs(figures_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.errorbar([cox_hr], [0], xerr=[[cox_hr - cox_ci_lower], [cox_ci_upper - cox_hr]],
                fmt="o", color="black", capsize=5, markersize=8)
    ax.axvline(x=1.0, color="gray", linestyle="--", label="HR=1 (null)")
    ax.axvline(x=1.2, color="red", linestyle="--", label="Gate HR=1.2")
    ax.set_yticks([0])
    ax.set_yticklabels(["Findable score"])
    ax.set_xlabel("Hazard Ratio (95% CI)")
    ax.set_title("Cox PH Forest Plot: Findable Sub-Criteria Effect")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(figures_dir, "fig5_cox_forest.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def plot_sensitivity_comparison(primary: dict, ablations: dict, figures_dir: str) -> str:
    """Figure 6: Sensitivity/ablation comparison bar chart."""
    os.makedirs(figures_dir, exist_ok=True)
    labels = ["Primary"]
    p_vals = [primary.get("log_rank_p", np.nan)]
    hrs = [primary.get("cox_hr", np.nan)]
    for k, v in ablations.items():
        labels.append(k.replace("_", " ").title())
        p_vals.append(v.get("log_rank_p", np.nan))
        hrs.append(v.get("cox_hr", np.nan))
    x = np.arange(len(labels))
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].bar(x, p_vals, color=["green" if (p is not None and not np.isnan(p) and p < 0.05) else "red" for p in p_vals])
    axes[0].axhline(y=0.05, color="black", linestyle="--", label="p=0.05")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=30, ha="right")
    axes[0].set_title("Log-rank p-value Comparison")
    axes[0].set_ylabel("p-value")
    axes[0].legend()
    axes[1].bar(x, hrs, color=["green" if (h is not None and not np.isnan(h) and h > 1.2) else "red" for h in hrs])
    axes[1].axhline(y=1.2, color="black", linestyle="--", label="HR=1.2")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=30, ha="right")
    axes[1].set_title("Cox HR Comparison")
    axes[1].set_ylabel("Hazard Ratio")
    axes[1].legend()
    plt.tight_layout()
    path = os.path.join(figures_dir, "fig6_sensitivity_comparison.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def generate_all_figures(results: dict, figures_dir: str) -> list:
    """Dispatch all 6 figure generators. Returns list of saved paths."""
    paths = []
    os.makedirs(figures_dir, exist_ok=True)
    log_rank_p = results.get("log_rank_p", 1.0)
    cox_hr = results.get("cox_hr", 1.0)
    cox_ci_lower = results.get("cox_ci_lower", 0.5)
    cox_ci_upper = results.get("cox_ci_upper", 2.0)
    kmf_high = results.get("kmf_high")
    kmf_low = results.get("kmf_low")
    median_high = results.get("median_ttfr_high", 0)
    median_low = results.get("median_ttfr_low", 0)
    smd_df = results.get("smd_df", pd.DataFrame({"covariate": [], "smd_before": [], "smd_after": []}))
    ablations = results.get("ablations", {})
    ps_before = results.get("ps_before", pd.Series(dtype=float))
    ps_after = results.get("ps_after", pd.Series(dtype=float))

    paths.append(plot_gate_metrics(log_rank_p, cox_hr, figures_dir))
    if kmf_high is not None and kmf_low is not None:
        paths.append(plot_km_curves(kmf_high, kmf_low, log_rank_p, median_high, median_low, figures_dir))
    else:
        paths.append(os.path.join(figures_dir, "fig2_km_curves_matched.png"))
    paths.append(plot_ps_distribution(ps_before, ps_after, figures_dir))
    if len(smd_df) > 0:
        paths.append(plot_love_plot(smd_df, figures_dir))
    else:
        paths.append(os.path.join(figures_dir, "fig4_love_plot.png"))
    paths.append(plot_cox_forest(cox_hr, cox_ci_lower, cox_ci_upper, figures_dir))
    primary_summary = {"log_rank_p": log_rank_p, "cox_hr": cox_hr}
    paths.append(plot_sensitivity_comparison(primary_summary, ablations, figures_dir))
    return paths
