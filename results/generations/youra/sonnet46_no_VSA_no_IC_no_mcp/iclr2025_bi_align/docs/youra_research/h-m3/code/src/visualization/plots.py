"""Visualization functions for H-M3."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_gate_metrics(results: dict, figures_dir: str, dpi: int = 150) -> str:
    metrics = {
        "β (slope)": (results["slope"],     0.0,  results["slope"] > 0),
        "p-value":   (results["p_value"],    0.05, results["p_value"] < 0.05),
        "R²":        (results["r_squared"],  0.5,  results["r_squared"] > 0.5),
    }
    fig, ax = plt.subplots(figsize=(8, 5))
    x = list(range(len(metrics)))
    colors = ["forestgreen" if v[2] else "tomato" for v in metrics.values()]
    ax.bar(x, [v[0] for v in metrics.values()], color=colors, alpha=0.75, width=0.5)
    for i, (label, (val, threshold, passed)) in enumerate(metrics.items()):
        ax.hlines(threshold, i - 0.3, i + 0.3, colors="black", linestyles="--", linewidth=1.5)
        ax.text(i, threshold + max(abs(threshold) * 0.05, 0.02),
                f"thr={threshold}", ha="center", fontsize=8)
        ax.text(i, val + max(abs(val) * 0.05, 0.02),
                f"{val:.4f}", ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(list(metrics.keys()))
    ax.set_ylabel("Metric Value")
    gate = "PASS ✓" if results.get("gate_pass") else "FAIL ✗"
    ax.set_title(f"H-M3 Gate Metrics — {gate}")
    fig.tight_layout()
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    out = str(Path(figures_dir) / "gate_metrics.png")
    fig.savefig(out, dpi=dpi)
    plt.close(fig)
    return out


def plot_regression_scatter(
    kl: np.ndarray,
    gap: np.ndarray,
    results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    slope, intercept = results["slope"], results["intercept"]
    r_squared, p_value = results["r_squared"], results["p_value"]
    ci_low, ci_high = results["ci_parametric"]

    kl_line = np.linspace(kl.min(), kl.max(), 200)
    fit_line     = slope * kl_line + intercept
    ci_band_low  = ci_low  * kl_line + intercept
    ci_band_high = ci_high * kl_line + intercept

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.scatter(kl, gap, color="steelblue", s=80, zorder=5, label="Observed gap")
    ax.plot(kl_line, fit_line, color="navy", linewidth=2,
            label=f"OLS fit (β={slope:.4f}, R²={r_squared:.4f}, p={p_value:.2e})")
    ax.fill_between(kl_line, ci_band_low, ci_band_high,
                    alpha=0.15, color="navy", label="95% CI (parametric)")
    ax.axhline(0, color="black", linestyle=":", alpha=0.4)
    ax.set_xlabel("KL Budget (nats)")
    ax.set_ylabel("gap = RM_norm − gold_preference")
    ax.set_title("H-M3: OLS Regression of Divergence Gap on KL Budget")
    ax.legend(fontsize=9)
    fig.tight_layout()
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    out = str(Path(figures_dir) / "regression_scatter.png")
    fig.savefig(out, dpi=dpi)
    plt.close(fig)
    return out


def plot_residuals(
    kl: np.ndarray,
    gap: np.ndarray,
    results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    fitted    = results["fitted"]
    residuals = results["residuals"]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(fitted, residuals, color="steelblue", s=80, zorder=5)
    ax.axhline(0, color="black", linestyle="--", alpha=0.6)
    ax.set_xlabel("Fitted values")
    ax.set_ylabel("Residuals")
    ax.set_title("H-M3: Residuals vs Fitted")
    fig.tight_layout()
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    out = str(Path(figures_dir) / "residuals.png")
    fig.savefig(out, dpi=dpi)
    plt.close(fig)
    return out


def plot_bootstrap_histogram(results: dict, figures_dir: str, dpi: int = 150) -> str:
    boot_slopes   = results["boot_slopes"]
    observed_beta = results["slope"]
    ci_low, ci_high = results["ci_bootstrap"]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(boot_slopes, bins=60, color="steelblue", alpha=0.7, edgecolor="white")
    ax.axvline(observed_beta, color="navy",   linewidth=2,
               label=f"Observed β={observed_beta:.4f}")
    ax.axvline(ci_low,        color="orange", linewidth=1.5, linestyle="--",
               label=f"95% CI [{ci_low:.4f}, {ci_high:.4f}]")
    ax.axvline(ci_high,       color="orange", linewidth=1.5, linestyle="--")
    ax.axvline(0,             color="black",  linewidth=1, linestyle=":", alpha=0.5, label="β=0")
    ax.set_xlabel("Bootstrap Slope Estimate")
    ax.set_ylabel("Count")
    ax.set_title(f"H-M3: Bootstrap Distribution of β (n={len(boot_slopes):,})")
    ax.legend(fontsize=9)
    fig.tight_layout()
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    out = str(Path(figures_dir) / "bootstrap_histogram.png")
    fig.savefig(out, dpi=dpi)
    plt.close(fig)
    return out
