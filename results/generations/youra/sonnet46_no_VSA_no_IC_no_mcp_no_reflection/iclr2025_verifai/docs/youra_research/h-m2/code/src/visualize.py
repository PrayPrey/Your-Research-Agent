"""Visualization for H-M2 feedback specificity analysis."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

VERIFIER_ORDER = ["execution", "mypy", "pyright", "z3"]
PALETTE = {"execution": "#4393c3", "mypy": "#92c5de", "pyright": "#f4a582", "z3": "#d6604d"}


def _prep(records: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    df["verifier"] = pd.Categorical(df["verifier"], categories=VERIFIER_ORDER, ordered=True)
    return df


def plot_bar_mean_char_count(df: pd.DataFrame, out_dir: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    verifiers = VERIFIER_ORDER
    means, cis = [], []
    for v in verifiers:
        vals = df[(df["verifier"] == v) & (~df["timeout"])]["char_count"].values
        if len(vals) > 1:
            sem = np.std(vals, ddof=1) / np.sqrt(len(vals))
            means.append(np.mean(vals))
            cis.append(1.96 * sem)
        else:
            means.append(0); cis.append(0)
    colors = [PALETTE[v] for v in verifiers]
    bars = ax.bar(verifiers, means, yerr=cis, color=colors, capsize=5, edgecolor="black", linewidth=0.7)
    ax.set_ylabel("Mean Feedback Char Count")
    ax.set_title("Feedback Specificity by Verifier Category\n(mean ± 95% CI, excluding timeouts)")
    for bar, m in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(cis) * 0.05,
                f"{m:.0f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "bar_mean_char_count.png"), dpi=150)
    plt.close()


def plot_box_char_count(df: pd.DataFrame, out_dir: str) -> None:
    df_plot = df[~df["timeout"]].copy()
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.boxplot(data=df_plot, x="verifier", y="char_count", order=VERIFIER_ORDER,
                palette=PALETTE, ax=ax, showfliers=True, flierprops={"markersize": 3})
    ax.set_title("Char Count Distribution per Verifier")
    ax.set_ylabel("Feedback Char Count")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "box_char_count.png"), dpi=150)
    plt.close()


def plot_heatmap_char_bug_type(df: pd.DataFrame, out_dir: str) -> None:
    df_plot = df[~df["timeout"]].copy()
    pivot = df_plot.groupby(["bug_type", "verifier"])["char_count"].mean().unstack(fill_value=0)
    # Reorder columns
    cols = [c for c in VERIFIER_ORDER if c in pivot.columns]
    pivot = pivot[cols]
    fig, ax = plt.subplots(figsize=(8, max(4, len(pivot) * 0.6)))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax, linewidths=0.5)
    ax.set_title("Mean Char Count by Bug Type × Verifier")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "heatmap_char_bug_type.png"), dpi=150)
    plt.close()


def plot_cdf_char_count(df: pd.DataFrame, out_dir: str) -> None:
    df_plot = df[~df["timeout"]].copy()
    fig, ax = plt.subplots(figsize=(7, 5))
    for v in VERIFIER_ORDER:
        vals = np.sort(df_plot[df_plot["verifier"] == v]["char_count"].values)
        if len(vals) == 0:
            continue
        cdf = np.arange(1, len(vals) + 1) / len(vals)
        ax.plot(vals, cdf, label=v, color=PALETTE[v], linewidth=2)
    ax.set_xlabel("Char Count")
    ax.set_ylabel("CDF")
    ax.set_title("Cumulative Distribution of Feedback Char Count")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "cdf_char_count.png"), dpi=150)
    plt.close()


def plot_scatter_char_field(df: pd.DataFrame, out_dir: str) -> None:
    df_plot = df[~df["timeout"]].copy()
    fig, ax = plt.subplots(figsize=(7, 5))
    for v in VERIFIER_ORDER:
        sub = df_plot[df_plot["verifier"] == v]
        ax.scatter(sub["char_count"], sub["field_count"], label=v,
                   color=PALETTE[v], alpha=0.5, s=20, edgecolors="none")
    ax.set_xlabel("Char Count")
    ax.set_ylabel("Field Count")
    ax.set_title("Char Count vs Field Count per Verifier")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "scatter_char_field.png"), dpi=150)
    plt.close()


def generate_all_figures(records: list[dict], out_dir: str = "figures/") -> None:
    os.makedirs(out_dir, exist_ok=True)
    df = _prep(records)
    plot_bar_mean_char_count(df, out_dir)
    plot_box_char_count(df, out_dir)
    plot_heatmap_char_bug_type(df, out_dir)
    plot_cdf_char_count(df, out_dir)
    plot_scatter_char_field(df, out_dir)
    print(f"Saved 5 figures to {out_dir}")
