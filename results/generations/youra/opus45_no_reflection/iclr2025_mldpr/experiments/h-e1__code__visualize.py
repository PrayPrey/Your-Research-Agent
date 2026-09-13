"""H-E1 Visualization: Required Figures"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from config import EXPERIMENT, EVAL
import os


def plot_gini_timeseries_with_changepoints(
    dates: pd.DatetimeIndex,
    gini_series: np.ndarray,
    change_points: list,
    save_path: str = None
) -> None:
    """Plot Gini time series with detected change points as vertical lines."""
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(dates, gini_series, "b-", linewidth=1.5, label="Gini coefficient")

    # Mark change points
    for i, cp in enumerate(change_points):
        if cp < len(dates):
            ax.axvline(dates[cp], color="red", linestyle="--", linewidth=2,
                      label="Change point" if i == 0 else None)
            ax.annotate(f"CP: {dates[cp].strftime('%Y-%m')}",
                       xy=(dates[cp], gini_series[cp]),
                       xytext=(10, 10), textcoords="offset points",
                       fontsize=9, color="red")

    # Shade target window
    window_start = pd.Timestamp(f"{EVAL.target_window[0]}-01-01")
    window_end = pd.Timestamp(f"{EVAL.target_window[1]}-12-31")
    ax.axvspan(window_start, window_end, alpha=0.1, color="green",
              label=f"Target window ({EVAL.target_window[0]}-{EVAL.target_window[1]})")

    ax.set_xlabel("Date")
    ax.set_ylabel("Gini Coefficient")
    ax.set_title("Benchmark Concentration (Gini) Over Time")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator())

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {save_path}")

    plt.close()


def plot_segmented_vs_monotonic_fit(
    dates: pd.DatetimeIndex,
    gini_series: np.ndarray,
    mono_pred: np.ndarray,
    seg_pred: np.ndarray,
    save_path: str = None
) -> None:
    """Overlay of single trend vs segmented trends."""
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(dates, gini_series, "ko", markersize=4, alpha=0.5, label="Data")
    ax.plot(dates, mono_pred, "b-", linewidth=2, label="Monotonic trend (H0)")
    ax.plot(dates, seg_pred, "r-", linewidth=2, label="Segmented trend (H1)")

    ax.set_xlabel("Date")
    ax.set_ylabel("Gini Coefficient")
    ax.set_title("Model Comparison: Monotonic vs Segmented Fit")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator())

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {save_path}")

    plt.close()


def plot_gate_metrics_bar(gate_results: dict, save_path: str = None) -> None:
    """Bar chart showing gate pass/fail status."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Gate status
    ax1 = axes[0]
    gates = ["G-1: CP in Window", "G-2/G-3: BIC Improved", "Overall"]
    values = [
        1 if gate_results["cp_in_window"] else 0,
        1 if gate_results["bic_improved"] else 0,
        1 if gate_results["overall"] == "PASS" else 0
    ]
    colors = ["green" if v else "red" for v in values]

    bars = ax1.bar(gates, values, color=colors, edgecolor="black")
    ax1.set_ylim(0, 1.5)
    ax1.set_ylabel("Pass (1) / Fail (0)")
    ax1.set_title("Gate Results")

    for bar, v in zip(bars, values):
        label = "PASS" if v else "FAIL"
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                label, ha="center", fontsize=10, fontweight="bold")

    # Right: BIC comparison
    ax2 = axes[1]
    bic_labels = ["Monotonic (H0)", "Segmented (H1)"]
    bic_values = [gate_results["bic_mono"], gate_results["bic_seg"]]
    bic_colors = ["blue", "red"]

    bars2 = ax2.bar(bic_labels, bic_values, color=bic_colors, edgecolor="black", alpha=0.7)
    ax2.set_ylabel("BIC (lower is better)")
    ax2.set_title(f"BIC Comparison (Δ = {gate_results['bic_delta']:.2f})")

    for bar, v in zip(bars2, bic_values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{v:.2f}", ha="center", fontsize=10)

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {save_path}")

    plt.close()


if __name__ == "__main__":
    # Test with mock data
    dates = pd.date_range("2018-01-01", periods=72, freq="MS")
    gini = np.linspace(0.6, 0.7, 72) + np.random.normal(0, 0.02, 72)
    change_points = [36]
    mono_pred = np.linspace(0.6, 0.7, 72)
    seg_pred = np.where(np.arange(72) < 36, 0.62, 0.68)

    gate_results = {
        "overall": "PASS",
        "cp_in_window": True,
        "bic_improved": True,
        "bic_mono": -150.0,
        "bic_seg": -170.0,
        "bic_delta": 20.0
    }

    plot_gini_timeseries_with_changepoints(dates, gini, change_points, "test_ts.png")
    plot_segmented_vs_monotonic_fit(dates, gini, mono_pred, seg_pred, "test_fit.png")
    plot_gate_metrics_bar(gate_results, "test_gate.png")
    print("Test plots saved.")
