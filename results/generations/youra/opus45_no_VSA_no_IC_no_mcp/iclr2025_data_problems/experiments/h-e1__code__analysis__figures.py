"""Dose-response figure generation."""

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures


def plot_dose_response(
    x: np.ndarray,
    y: np.ndarray,
    fit: dict,
    title: str,
    xlabel: str,
    save_path: str,
    peak: float = None,
):
    """Plot dose-response curve with fitted polynomial."""
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(x, y, s=80, c="steelblue", edgecolors="white", linewidth=1.5, zorder=3)

    x_smooth = np.linspace(x.min(), x.max(), 100)
    X_poly = PolynomialFeatures(fit["degree"]).fit_transform(x_smooth.reshape(-1, 1))
    y_smooth = fit["intercept"] + X_poly[:, 1:] @ np.array(fit["coef"][1:])

    ax.plot(x_smooth, y_smooth, c="coral", linewidth=2.5, label=f"Degree {fit['degree']} fit")

    if peak is not None:
        X_peak = PolynomialFeatures(fit["degree"]).fit_transform([[peak]])
        y_peak = fit["intercept"] + X_peak[:, 1:] @ np.array(fit["coef"][1:])
        ax.axvline(peak, color="forestgreen", linestyle="--", linewidth=1.5, alpha=0.7)
        ax.scatter([peak], [y_peak[0]], s=120, c="forestgreen", marker="*", zorder=4, label=f"Peak @ {peak:.1f}")

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel("Ensemble Score (PC1)", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    degree_str = f"deg={fit['degree']}, AIC={fit['aic']:.1f}, R²={fit['r2']:.3f}"
    ax.text(0.02, 0.02, degree_str, transform=ax.transAxes, fontsize=9, verticalalignment="bottom")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def generate_figures(analysis: dict, fig_dir: str = "figures/"):
    """Generate all dose-response figures."""
    os.makedirs(fig_dir, exist_ok=True)

    perp = analysis["perplexity"]
    plot_dose_response(
        np.array(perp["x"]),
        np.array(perp["y"]),
        perp["fit"],
        "Dose-Response: Perplexity Filtering",
        "Perplexity Percentile Threshold",
        os.path.join(fig_dir, "dose_response_perplexity.png"),
        perp["peak"],
    )

    dedup = analysis["dedup"]
    plot_dose_response(
        np.array(dedup["x"]),
        np.array(dedup["y"]),
        dedup["fit"],
        "Dose-Response: Deduplication Stringency",
        "Deduplication Level (0=none, 4=exact+fuzzy)",
        os.path.join(fig_dir, "dose_response_dedup.png"),
        dedup["peak"],
    )

    return [
        os.path.join(fig_dir, "dose_response_perplexity.png"),
        os.path.join(fig_dir, "dose_response_dedup.png"),
    ]
