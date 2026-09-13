"""
visualize.py — FR-5: Generate 5 Required Figures for H-E1.

Produces publication-quality figures at 300 DPI PNG.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression

import config


class Visualizer:
    def __init__(self, figures_dir: str = config.FIGURES_DIR) -> None:
        self.figures_dir = Path(figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        # Use a style that works across seaborn versions
        try:
            plt.style.use("seaborn-v0_8-whitegrid")
        except OSError:
            try:
                plt.style.use("seaborn-whitegrid")
            except OSError:
                pass  # use default

    def _save(self, fig: plt.Figure, name: str) -> str:
        path = str(self.figures_dir / name)
        fig.savefig(path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved figure: {path}")
        return path

    def plot_gate_metrics(self, gate: dict) -> str:
        """Bar chart: SD vs 0.05 threshold; R² vs 0.80 threshold."""
        fig, ax = plt.subplots(figsize=(10, 5))

        metrics = ["SD(AdvGLUE_drop)", "R²_residualization"]
        values = [gate["sd_advglue_drop"], gate["r2_residualization"]]
        thresholds = [config.SD_THRESHOLD, config.R2_THRESHOLD]
        colors = ["#2196F3", "#4CAF50"]

        bars = ax.bar(metrics, values, color=colors, alpha=0.8, width=0.5)
        for i, (thresh, label) in enumerate(zip(thresholds, ["SD threshold (>0.05)", "R² threshold (<0.80)"])):
            ax.axhline(y=thresh, xmin=i * 0.5, xmax=(i + 1) * 0.5,
                       color="red", linestyle="--", linewidth=2, label=label)

        # Add CI error bars
        sd_err = [[gate["sd_advglue_drop"] - gate["sd_ci_lower"]],
                  [gate["sd_ci_upper"] - gate["sd_advglue_drop"]]]
        r2_err = [[gate["r2_residualization"] - gate["r2_ci_lower"]],
                  [gate["r2_ci_upper"] - gate["r2_residualization"]]]
        ax.errorbar([0], [gate["sd_advglue_drop"]], yerr=sd_err, fmt="none",
                    color="black", capsize=5, linewidth=2)
        ax.errorbar([1], [gate["r2_residualization"]], yerr=r2_err, fmt="none",
                    color="black", capsize=5, linewidth=2)

        # Value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f"{val:.4f}", ha="center", va="bottom", fontweight="bold")

        gate_str = "PASS ✓" if gate["gate_passed"] else "FAIL ✗"
        ax.set_title(f"H-E1 Gate Metrics — {gate_str} (N={gate['n_models']} models)",
                     fontsize=13, fontweight="bold")
        ax.set_ylabel("Metric Value")
        ax.legend(loc="upper right")
        ax.set_ylim(0, max(max(values) * 1.3, 1.0))

        return self._save(fig, "fig_gate_metrics.png")

    def plot_ri_distribution(self, df: pd.DataFrame) -> str:
        """Violin plot of RI by model_family."""
        if "RI" not in df.columns:
            df = df.copy()
            df["RI"] = df["advglue_drop"] - df["advglue_drop"].mean()

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.violinplot(
            data=df, x="model_family", y="RI",
            hue="training_regime", inner="box",
            palette="muted", ax=ax,
        )
        ax.axhline(y=0, color="red", linestyle="--", linewidth=1, alpha=0.7)
        ax.set_title("Residual Instability Distribution by Model Family", fontsize=12)
        ax.set_xlabel("Model Family")
        ax.set_ylabel("Residual Instability (RI)")
        ax.legend(title="Training Regime", loc="upper right", fontsize=9)
        plt.xticks(rotation=15)

        return self._save(fig, "fig_ri_distribution.png")

    def plot_advglue_hist(self, df: pd.DataFrame) -> str:
        """Histogram of raw advglue_drop distribution."""
        fig, ax = plt.subplots(figsize=(7, 5))

        vals = df["advglue_drop"].dropna()
        mean_v = vals.mean()
        std_v = vals.std()

        ax.hist(vals, bins=20, color="#2196F3", alpha=0.7, edgecolor="white", density=True)

        # KDE overlay
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(vals)
        x_range = np.linspace(vals.min(), vals.max(), 200)
        ax.plot(x_range, kde(x_range), color="navy", linewidth=2, label="KDE")

        ax.axvline(mean_v, color="red", linestyle="--", linewidth=2,
                   label=f"Mean={mean_v:.3f}")
        ax.axvline(mean_v + std_v, color="orange", linestyle=":", linewidth=1.5,
                   label=f"±1 SD ({std_v:.3f})")
        ax.axvline(mean_v - std_v, color="orange", linestyle=":", linewidth=1.5)
        ax.axvline(config.SD_THRESHOLD, color="green", linestyle="-.", linewidth=2,
                   label=f"SD threshold (0.05)")

        ax.set_title(f"AdvGLUE Drop Distribution (N={len(df)}, SD={std_v:.4f})",
                     fontsize=12)
        ax.set_xlabel("AdvGLUE Accuracy Drop")
        ax.set_ylabel("Density")
        ax.legend(fontsize=9)

        return self._save(fig, "fig_advglue_hist.png")

    def plot_pc1_scatter(self, df: pd.DataFrame) -> str:
        """Scatter plot: PC1 vs advglue_drop with OLS fit line."""
        if "PC1" not in df.columns:
            from sklearn.decomposition import PCA
            from sklearn.preprocessing import StandardScaler
            X = StandardScaler().fit_transform(df[config.CAP_COLS].values)
            df = df.copy()
            df["PC1"] = PCA(n_components=1).fit_transform(X).flatten()

        fig, ax = plt.subplots(figsize=(7, 6))

        families = df["model_family"].unique()
        palette = sns.color_palette("muted", len(families))
        for fam, color in zip(families, palette):
            mask = df["model_family"] == fam
            ax.scatter(df.loc[mask, "PC1"], df.loc[mask, "advglue_drop"],
                       color=color, label=fam, s=60, alpha=0.8)

        # OLS fit line
        x_vals = df["PC1"].values.reshape(-1, 1)
        y_vals = df["advglue_drop"].values
        ols = LinearRegression().fit(x_vals, y_vals)
        x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
        ax.plot(x_line, ols.predict(x_line.reshape(-1, 1)),
                color="red", linewidth=2, linestyle="--",
                label=f"OLS fit (R²={ols.score(x_vals, y_vals):.3f})")

        ax.set_title("PC1 (Capability) vs AdvGLUE Drop", fontsize=12)
        ax.set_xlabel("Capability PC1 Score")
        ax.set_ylabel("AdvGLUE Accuracy Drop")
        ax.legend(fontsize=9, loc="upper right")

        return self._save(fig, "fig_pc1_scatter.png")

    def plot_ri_regime(self, df: pd.DataFrame) -> str:
        """Box plot of RI by training_regime, grouped by scale."""
        if "RI" not in df.columns:
            df = df.copy()
            df["RI"] = df["advglue_drop"] - df["advglue_drop"].mean()

        fig, ax = plt.subplots(figsize=(9, 6))
        sns.boxplot(
            data=df, x="scale", y="RI",
            hue="training_regime", palette="muted",
            showfliers=True, ax=ax,
        )
        ax.axhline(y=0, color="red", linestyle="--", linewidth=1, alpha=0.7)
        ax.set_title("Residual Instability by Scale and Training Regime", fontsize=12)
        ax.set_xlabel("Model Scale")
        ax.set_ylabel("Residual Instability (RI)")
        ax.legend(title="Training Regime", loc="upper right", fontsize=9)

        return self._save(fig, "fig_ri_regime.png")

    def generate_all(self, df: pd.DataFrame, gate: dict) -> List[str]:
        """Generate all 5 figures; return list of saved paths."""
        print("Generating figures...")
        paths = [
            self.plot_gate_metrics(gate),
            self.plot_ri_distribution(df),
            self.plot_advglue_hist(df),
            self.plot_pc1_scatter(df),
            self.plot_ri_regime(df),
        ]
        print(f"  ✓ Generated {len(paths)} figures")
        return paths


def generate_figures(
    df: pd.DataFrame,
    gate: dict,
    figures_dir: str,
) -> List[str]:
    """Top-level entry point. Returns list of 5 saved figure paths."""
    viz = Visualizer(figures_dir=figures_dir)
    return viz.generate_all(df, gate)
