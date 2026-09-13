from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from config import FIGURE_DPI, FIGURE_FORMAT, FIGURE_NAMES, GATE_THRESHOLD, INDICATORS


def _save(fig: plt.Figure, out_dir: Path, name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    fig.savefig(path, dpi=FIGURE_DPI, format=FIGURE_FORMAT, bbox_inches="tight")
    plt.close(fig)


def plot_gate_bar(
    corr_df: pd.DataFrame,
    gate_pairs: list[tuple],
    threshold: float,
    out_dir: Path,
) -> None:
    labels, rhos, ci_los, ci_his = [], [], [], []
    for x, y in gate_pairs:
        row = corr_df[(corr_df["x"] == x) & (corr_df["y"] == y)]
        if row.empty:
            row = corr_df[(corr_df["x"] == y) & (corr_df["y"] == x)]
        if row.empty:
            continue
        labels.append(f"{x}\nvs\n{y}")
        rhos.append(float(row["rho"].values[0]))
        ci_los.append(float(row["ci_low"].values[0]))
        ci_his.append(float(row["ci_high"].values[0]))

    fig, ax = plt.subplots(figsize=(6, 4))
    x_pos = np.arange(len(labels))
    yerr_lo = [r - lo for r, lo in zip(rhos, ci_los)]
    yerr_hi = [hi - r for r, hi in zip(rhos, ci_his)]
    colors = ["green" if r >= threshold else "red" for r in rhos]
    ax.bar(x_pos, rhos, color=colors, alpha=0.7,
           yerr=[yerr_lo, yerr_hi], capsize=6, error_kw={"elinewidth": 1.5})
    ax.axhline(threshold, color="black", linestyle="--", linewidth=1.2, label=f"threshold={threshold}")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Partial Spearman ρ")
    ax.set_title("Gate Pairs: Partial ρ vs. Threshold (with BCa 95% CI)")
    ax.legend()
    _save(fig, out_dir, FIGURE_NAMES["partial_corr_heatmap"].replace("heatmap", "gate_bar"))


def plot_corr_heatmap(corr_df: pd.DataFrame, out_dir: Path) -> None:
    n = len(INDICATORS)
    matrix = pd.DataFrame(np.eye(n), index=INDICATORS, columns=INDICATORS)
    pval_matrix = pd.DataFrame(np.ones((n, n)), index=INDICATORS, columns=INDICATORS)

    for _, row in corr_df.iterrows():
        x, y = row["x"], row["y"]
        if x in matrix.index and y in matrix.columns:
            matrix.loc[x, y] = row["rho"]
            matrix.loc[y, x] = row["rho"]
            pval_matrix.loc[x, y] = row["p_value"]
            pval_matrix.loc[y, x] = row["p_value"]

    annot = matrix.copy().astype(str)
    for i in INDICATORS:
        for j in INDICATORS:
            rho_val = matrix.loc[i, j]
            p = pval_matrix.loc[i, j]
            stars = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ""))
            annot.loc[i, j] = f"{rho_val:.2f}{stars}"

    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(matrix, annot=annot, fmt="s", cmap="RdBu_r", center=0,
                vmin=-1, vmax=1, ax=ax, square=True, linewidths=0.5)
    ax.set_title("Partial Spearman ρ Matrix (controlling for MMLU_acc)")
    _save(fig, out_dir, FIGURE_NAMES["partial_corr_heatmap"])


def plot_factor_loadings(fa: object, indicators: list[str], out_dir: Path) -> None:
    loadings = fa.loadings_[:, 0]
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ["steelblue" if v >= 0 else "salmon" for v in loadings]
    ax.barh(indicators, loadings, color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Factor Loading (Factor 1)")
    ax.set_title("Factor Analysis Loadings — Epistemic Reliability Factor")
    _save(fig, out_dir, FIGURE_NAMES["factor_loadings"])


def plot_tucker_congruence(
    loadings_g: np.ndarray,
    loadings_s: np.ndarray,
    congruence: float,
    indicators: list[str],
    out_dir: Path,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, loadings, label in zip(axes, [loadings_g, loadings_s], ["Greedy", "T=0.7"]):
        vals = loadings.flatten()
        colors = ["steelblue" if v >= 0 else "salmon" for v in vals]
        ax.barh(indicators, vals, color=colors)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel("Factor Loading")
        ax.set_title(f"Factor 1 Loadings ({label})")
    axes[0].set_ylabel("Indicator")
    fig.suptitle(f"Tucker's Congruence = {congruence:.3f} (threshold ≥ 0.85)", fontsize=12)
    plt.tight_layout()
    _save(fig, out_dir, FIGURE_NAMES["factor_loadings"].replace("fig2", "fig2b_tucker"))


def plot_family_scatter(df: pd.DataFrame, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    families = df["family"].unique() if "family" in df.columns else ["unknown"]
    palette = sns.color_palette("tab10", n_colors=len(families))
    for fam, color in zip(families, palette):
        sub = df[df["family"] == fam] if "family" in df.columns else df
        ax.scatter(sub["ECE"], sub["TruthfulQA_pct"], label=fam, color=color, alpha=0.8, s=60)
    ax.set_xlabel("ECE (↓ better)")
    ax.set_ylabel("TruthfulQA %")
    ax.set_title("ECE vs TruthfulQA% by Model Family")
    ax.legend(fontsize=8, bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.tight_layout()
    _save(fig, out_dir, FIGURE_NAMES["ece_truthfulqa_scatter"])


def plot_decoding_invariance(
    corr_greedy: pd.DataFrame,
    corr_stochastic: pd.DataFrame,
    out_dir: Path,
) -> None:
    merged = corr_greedy.merge(corr_stochastic, on=["x", "y"], suffixes=("_greedy", "_stoch"))
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(merged["rho_greedy"], merged["rho_stoch"], alpha=0.8, s=60, color="steelblue")
    lim = [min(merged["rho_greedy"].min(), merged["rho_stoch"].min()) - 0.05,
           max(merged["rho_greedy"].max(), merged["rho_stoch"].max()) + 0.05]
    ax.plot(lim, lim, "k--", linewidth=1, label="y=x (perfect invariance)")
    for _, row in merged.iterrows():
        ax.annotate(f"{row['x'][:3]}-{row['y'][:3]}", (row["rho_greedy"], row["rho_stoch"]),
                    fontsize=7, alpha=0.7)
    ax.set_xlabel("Partial ρ (Greedy)")
    ax.set_ylabel("Partial ρ (T=0.7)")
    ax.set_title("Decoding Invariance: Greedy vs. Stochastic Partial ρ")
    ax.legend()
    plt.tight_layout()
    _save(fig, out_dir, FIGURE_NAMES["loo_roc_curve"].replace("fig6", "fig6b_decoding"))
