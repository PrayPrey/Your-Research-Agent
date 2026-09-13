"""Visualization: scatter+fit plots, gate metrics bar chart, parameter table."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
from fitting import logistic


def plot_all(
    benchmark_id: str,
    t: np.ndarray,
    y: np.ndarray,
    linear: dict,
    logistic_result: dict,
    out_dir: str,
) -> None:
    """Save scatter+fit plot and residuals panel for one benchmark."""
    os.makedirs(out_dir, exist_ok=True)
    t_smooth = np.linspace(t.min(), t.max(), 300)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: scatter + fits
    ax = axes[0]
    ax.scatter(t, y, alpha=0.5, s=20, label="Data", color="steelblue")
    lin_pred = np.polyval(linear["coeffs"], t_smooth)
    ax.plot(t_smooth, lin_pred, "--", color="orange", label=f"Linear R²={linear['r2']:.3f}")
    if logistic_result["converged"]:
        log_pred = logistic(t_smooth, *logistic_result["popt"])
        ax.plot(t_smooth, log_pred, "-", color="crimson",
                label=f"Logistic R²={logistic_result['r2']:.3f}")
    ax.axhline(0.9, color="gray", linestyle=":", linewidth=0.8, label="Target (0.9)")
    ax.set_xlabel("Months since release")
    ax.set_ylabel("Normalized score")
    ax.set_title(f"{benchmark_id} — Logistic Fit")
    ax.legend(fontsize=8)

    # Right: residuals
    ax2 = axes[1]
    if logistic_result["converged"]:
        resid = y - logistic(t, *logistic_result["popt"])
        ax2.scatter(t, resid, alpha=0.5, s=20, color="crimson")
        ax2.axhline(0, color="black", linewidth=0.8)
        ax2.set_xlabel("Months since release")
        ax2.set_ylabel("Residual")
        ax2.set_title(f"{benchmark_id} — Residuals")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"logistic_fit_{benchmark_id}.png"), dpi=120)
    plt.close()


def plot_gate_metrics(results: dict, out_dir: str) -> None:
    """Bar chart of R² per benchmark with 0.9 threshold line."""
    os.makedirs(out_dir, exist_ok=True)
    names = list(results.keys())
    r2_vals = [results[n]["logistic_result"]["r2"] for n in names]

    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ["green" if v >= 0.9 else "red" for v in r2_vals]
    bars = ax.bar(names, r2_vals, color=colors, alpha=0.8)
    ax.axhline(0.9, color="black", linestyle="--", linewidth=1, label="Threshold (0.9)")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("R²")
    ax.set_title("Gate Metrics: R² per Benchmark")
    ax.legend()
    for bar, val in zip(bars, r2_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.3f}", ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "gate_metrics.png"), dpi=120)
    plt.close()


def plot_parameter_summary(results: dict, out_dir: str) -> None:
    """Table figure of K, r, t0 with 95% CI for all benchmarks."""
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    cols = ["Benchmark", "K ± CI", "r ± CI", "t0 ± CI", "R²", "Converged"]
    for name, data in results.items():
        lr = data["logistic_result"]
        if lr["converged"]:
            K, r, t0 = lr["popt"]
            ci = lr["ci95"]
            rows.append([
                name,
                f"{K:.3f} ± {ci[0]:.3f}",
                f"{r:.3f} ± {ci[1]:.3f}",
                f"{t0:.1f} ± {ci[2]:.1f}",
                f"{lr['r2']:.4f}",
                "Yes",
            ])
        else:
            rows.append([name, "N/A", "N/A", "N/A", "N/A", "No"])

    fig, ax = plt.subplots(figsize=(10, max(2, len(rows) * 0.6 + 1.5)))
    ax.axis("off")
    tbl = ax.table(cellText=rows, colLabels=cols, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.4)
    ax.set_title("Logistic Fit Parameter Summary", fontsize=11, pad=10)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "parameter_summary.png"), dpi=120)
    plt.close()
