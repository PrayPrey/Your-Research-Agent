"""visualize.py — Generate 6 figures for H-M1 RI→ECE mechanism verification."""
from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

import config


class Visualizer:
    def __init__(
        self,
        figures_dir: str = config.FIGURES_DIR,
        dpi: int = config.FIGURE_DPI,
    ) -> None:
        self.figures_dir = Path(figures_dir)
        self.dpi = dpi
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        sns.set_theme(style="whitegrid")

    def _save(self, fig: "plt.Figure", filename: str) -> Path:
        path = self.figures_dir / filename
        fig.savefig(path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        return path

    def fig1_partial_regression_scatter(
        self, df: pd.DataFrame, rho: float, p_val: float
    ) -> Path:
        """Scatter RI vs ECE with regression line. Saves fig1_ri_ece_scatter.png."""
        fig, ax = plt.subplots(figsize=config.FIGURE_SIZE_SCATTER)
        fam_col = "model_family" if "model_family" in df.columns else "family"
        families = df[fam_col].unique()
        palette = dict(zip(families, config.COLOR_PALETTE[: len(families)]))
        for fam, grp in df.groupby(fam_col):
            ax.scatter(grp["RI"], grp["ECE"], label=fam, color=palette.get(fam, "gray"), alpha=0.8, s=60)

        # Regression line
        slope, intercept, *_ = stats.linregress(df["RI"], df["ECE"])
        x_line = np.linspace(df["RI"].min(), df["RI"].max(), 100)
        ax.plot(x_line, slope * x_line + intercept, "k--", lw=1.5, alpha=0.7)

        p_str = f"{p_val:.4f}" if p_val >= 0.001 else f"{p_val:.2e}"
        ax.set_title(f"RI vs ECE  (ρ={rho:.3f}, p={p_str})")
        ax.set_xlabel("Residual Instability (RI)")
        ax.set_ylabel("Expected Calibration Error (ECE)")
        ax.legend(fontsize=8)
        return self._save(fig, config.FIG1_FILENAME)

    def fig2_residuals_scatter(self, df: pd.DataFrame) -> Path:
        """RI_residual vs ECE_residual after removing PC1, mean_confidence."""
        from sklearn.linear_model import LinearRegression  # type: ignore[import]

        fig, ax = plt.subplots(figsize=config.FIGURE_SIZE_SCATTER)
        covars = df[["PC1", "mean_confidence"]].values
        ri_arr = df["RI"].values.astype(float)
        ece_arr = df["ECE"].values.astype(float)
        ri_resid = ri_arr - LinearRegression().fit(covars, ri_arr).predict(covars)
        ece_resid = ece_arr - LinearRegression().fit(covars, ece_arr).predict(covars)
        ax.scatter(ri_resid, ece_resid, alpha=0.8, s=60, color=config.COLOR_PALETTE[0])
        slope, intercept, *_ = stats.linregress(ri_resid, ece_resid)
        x_line = np.linspace(ri_resid.min(), ri_resid.max(), 100)
        ax.plot(x_line, slope * x_line + intercept, "k--", lw=1.5)
        ax.set_xlabel("RI residual (controlling PC1, mean_confidence)")
        ax.set_ylabel("ECE residual")
        ax.set_title("Partial Regression Residuals Plot")
        return self._save(fig, config.FIG2_FILENAME)

    def fig3_family_subplots(
        self, df: pd.DataFrame, family_results: pd.DataFrame
    ) -> Path:
        """3-panel family subplot with per-family rho annotation."""
        fam_col = "model_family" if "model_family" in df.columns else "family"
        families = config.TARGET_FAMILIES
        fig, axes = plt.subplots(1, 3, figsize=config.FIGURE_SIZE_FAMILY)
        for ax, fam, color in zip(axes, families, config.COLOR_PALETTE):
            sub = df[df[fam_col] == fam]
            ax.scatter(sub["RI"], sub["ECE"], color=color, alpha=0.8, s=60)
            if len(sub) >= 3:
                slope, intercept, *_ = stats.linregress(sub["RI"], sub["ECE"])
                x_line = np.linspace(sub["RI"].min(), sub["RI"].max(), 50)
                ax.plot(x_line, slope * x_line + intercept, "--", color=color, lw=1.5)
            fam_row = family_results[family_results["family"] == fam]
            rho_str = f"ρ={fam_row['rho'].values[0]:.3f}" if len(fam_row) > 0 else "n<5"
            ax.set_title(f"{fam}\n{rho_str} (n={len(sub)})")
            ax.set_xlabel("RI")
            ax.set_ylabel("ECE")
        fig.tight_layout()
        return self._save(fig, config.FIG3_FILENAME)

    def fig4_reliability_diagram(self, df: pd.DataFrame, ece_df: pd.DataFrame) -> Path:
        """Average reliability diagram sorted by RI quartile."""
        fig, ax = plt.subplots(figsize=config.FIGURE_SIZE_RELIABILITY)
        quartiles = pd.qcut(df["RI"], q=4, labels=["Q1 (low RI)", "Q2", "Q3", "Q4 (high RI)"])
        ece_col = "ECE" if "ECE" in ece_df.columns else "ece"
        for q_label, color in zip(["Q1 (low RI)", "Q4 (high RI)"], [config.COLOR_PALETTE[0], config.COLOR_PALETTE[2]]):
            idx = (quartiles == q_label).values
            if idx.sum() > 0:
                ece_vals = df.loc[idx, "ECE"].values.astype(float)
                ax.scatter([q_label] * len(ece_vals), ece_vals, color=color, alpha=0.7, s=50)
                ax.hlines(float(ece_vals.mean()), -0.5, 1.5, colors=color, linewidth=2, label=f"{q_label} mean={ece_vals.mean():.3f}")
        # Overall mean ECE line
        overall_mean = float(df["ECE"].mean())
        ax.axhline(y=overall_mean, linestyle="--", color="gray", lw=1, label="Overall mean ECE")
        ax.set_ylabel("ECE")
        ax.set_title("ECE by RI Quartile (Reliability Summary)")
        ax.legend(fontsize=8)
        return self._save(fig, config.FIG4_FILENAME)

    def fig5_rho_comparison_bar(
        self,
        rho_baseline: float,
        rho_partial: float,
        ci_baseline: tuple,
        ci_partial: tuple,
    ) -> Path:
        """Bar: ρ(PC1, ECE) vs ρ(RI, ECE | PC1) with CI error bars."""
        fig, ax = plt.subplots(figsize=config.FIGURE_SIZE_BAR)
        labels = ["ρ(PC1, ECE)\n(baseline)", "ρ(RI, ECE | PC1)\n(partial)"]
        rhos = [rho_baseline, rho_partial]
        colors = [config.COLOR_PALETTE[1], config.COLOR_PALETTE[0]]
        yerr_low = [rho_baseline - ci_baseline[0], rho_partial - ci_partial[0]]
        yerr_high = [ci_baseline[1] - rho_baseline, ci_partial[1] - rho_partial]
        yerr = [yerr_low, yerr_high]
        bars = ax.bar(labels, rhos, color=colors, alpha=0.8, width=0.5)
        ax.errorbar(labels, rhos, yerr=yerr, fmt="none", color="black", capsize=5)
        ax.axhline(y=config.RHO_THRESHOLD, linestyle="--", color="red", lw=1.5, label=f"Gate threshold ρ={config.RHO_THRESHOLD}")
        ax.set_ylabel("Spearman ρ")
        ax.set_title("Capability vs RI Partial Correlation with ECE")
        ax.legend()
        ax.set_ylim(0, max(rho_baseline, rho_partial) * 1.3 + 0.1)
        return self._save(fig, config.FIG5_FILENAME)

    def fig6_gate_summary(
        self, rho_actual: float, rho_target: float, ci: tuple
    ) -> Path:
        """Gate summary: target ρ vs actual with CI."""
        fig, ax = plt.subplots(figsize=config.FIGURE_SIZE_BAR)
        ax.barh(["Actual ρ"], [rho_actual], color=config.COLOR_PALETTE[0], alpha=0.8, height=0.4)
        ax.errorbar([rho_actual], ["Actual ρ"], xerr=[[rho_actual - ci[0]], [ci[1] - rho_actual]],
                    fmt="none", color="black", capsize=5)
        ax.axvline(x=rho_target, linestyle="--", color="red", lw=2, label=f"Gate threshold ρ={rho_target}")
        passed = rho_actual >= rho_target
        ax.set_title(f"Gate Summary: {'PASS ✓' if passed else 'FAIL ✗'}")
        ax.set_xlabel("Spearman partial ρ(RI, ECE | PC1, mean_confidence)")
        ax.legend()
        ax.set_xlim(-0.1, 1.0)
        return self._save(fig, config.FIG6_FILENAME)

    def generate_all(
        self,
        df: pd.DataFrame,
        ece_df: pd.DataFrame,
        partial_corr_results: dict,
        secondary_results: dict,
    ) -> list[Path]:
        """Generate all 6 figures. Returns list of saved paths."""
        paths = []
        full = partial_corr_results["full"]
        family_df = partial_corr_results["family_df"]
        rho = full["rho"]
        p_val = full["p_value"]
        ci_partial = (full["ci_low"], full["ci_high"])
        baseline_rho = secondary_results["baseline_corr"]["rho"]
        ci_baseline = (baseline_rho - 0.1, baseline_rho + 0.1)  # approx

        paths.append(self.fig1_partial_regression_scatter(df, rho, p_val))
        try:
            paths.append(self.fig2_residuals_scatter(df))
        except Exception:
            pass
        paths.append(self.fig3_family_subplots(df, family_df))
        paths.append(self.fig4_reliability_diagram(df, ece_df))
        paths.append(self.fig5_rho_comparison_bar(baseline_rho, rho, ci_baseline, ci_partial))
        paths.append(self.fig6_gate_summary(rho, config.RHO_THRESHOLD, ci_partial))
        return [p for p in paths if p is not None]
