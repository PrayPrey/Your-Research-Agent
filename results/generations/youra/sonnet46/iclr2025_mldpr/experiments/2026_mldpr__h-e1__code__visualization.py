"""visualization.py — 5 Mandatory Figures for H-E1 DTS Scoring PoC."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

FIGURES_CONFIG = {
    "figures_dir": "figures",
    "dpi": 150,
    "figsize_bar": (8, 5),
    "figsize_heatmap": (10, 6),
    "figsize_violin": (10, 5),
    "figsize_scatter": (7, 7),
    "gate_metrics_path": "figures/gate_metrics_comparison.png",
    "section_heatmap_path": "figures/per_section_coverage_heatmap.png",
    "dts_distribution_path": "figures/dts_score_distribution.png",
    "human_scatter_path": "figures/human_automated_scatter.png",
    "missing_field_path": "figures/missing_field_analysis.png",
}


def _ensure_dir(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def plot_gate_metrics(results: dict, output_path: str) -> None:
    """FR-V1: Bar chart of actual vs target (0.70 threshold lines).

    Args:
        results: Results dict with gate metrics.
        output_path: Path to save PNG.
    """
    _ensure_dir(output_path)

    metrics = {
        "Overall\nCoverage": results.get("coverage_rate", 0),
        "HF\nCoverage": results.get("coverage_rate_hf", 0),
        "OpenML\nCoverage": results.get("coverage_rate_openml", 0),
        "UCI\nCoverage": results.get("coverage_rate_uci", 0),
        "Pearson r\n(human-auto)": results.get("pearson_r", 0),
    }

    fig, ax = plt.subplots(figsize=FIGURES_CONFIG["figsize_bar"])
    x = list(metrics.keys())
    y = [max(0, min(1, v)) for v in metrics.values()]

    bars = ax.bar(x, y, color=["#2196F3" if v >= 0.70 else "#F44336" for v in y], alpha=0.8, edgecolor="black")
    ax.axhline(y=0.70, color="red", linestyle="--", linewidth=2, label="Target threshold (0.70)")
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Score")
    ax.set_title("H-E1 Gate Metrics vs. Target Threshold\n(DTS-Weighted Documentation Completeness PoC)")
    ax.legend()

    for bar, val in zip(bars, y):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{val:.2f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=FIGURES_CONFIG["dpi"])
    plt.close()
    print(f"  [Fig] Saved: {output_path}")


def plot_section_coverage_heatmap(df: pd.DataFrame, output_path: str) -> None:
    """FR-V2: 6 DTS sections × 3 repositories heatmap.

    Args:
        df: Scored corpus DataFrame.
        output_path: Path to save PNG.
    """
    _ensure_dir(output_path)

    from scorer import DTS_SECTIONS
    sections = list(DTS_SECTIONS.keys())
    repos = df["repository"].unique().tolist() if "repository" in df.columns else ["all"]

    heat_data = pd.DataFrame(index=sections, columns=repos, dtype=float)

    for repo in repos:
        if repo == "all":
            sub = df
        else:
            sub = df[df["repository"] == repo]
        for section in sections:
            col = f"per_section_{section}"
            if col in sub.columns:
                heat_data.loc[section, repo] = sub[col].mean()
            else:
                heat_data.loc[section, repo] = 0.0

    heat_data = heat_data.astype(float)

    fig, ax = plt.subplots(figsize=FIGURES_CONFIG["figsize_heatmap"])
    sns.heatmap(
        heat_data,
        annot=True,
        fmt=".2f",
        cmap="YlOrRd",
        vmin=0,
        vmax=1,
        ax=ax,
        cbar_kws={"label": "Mean Section Coverage"},
    )
    ax.set_title("Per-Section DTS Coverage by Repository\n(H-E1 EXISTENCE PoC)")
    ax.set_xlabel("Repository")
    ax.set_ylabel("DTS Section")
    plt.tight_layout()
    plt.savefig(output_path, dpi=FIGURES_CONFIG["dpi"])
    plt.close()
    print(f"  [Fig] Saved: {output_path}")


def plot_dts_distribution(df: pd.DataFrame, output_path: str) -> None:
    """FR-V3: Violin/box plot of DTS score distributions per repository.

    Args:
        df: Scored corpus DataFrame.
        output_path: Path to save PNG.
    """
    _ensure_dir(output_path)

    fig, ax = plt.subplots(figsize=FIGURES_CONFIG["figsize_violin"])

    if "repository" in df.columns and "weighted_dts_score" in df.columns:
        repos = df["repository"].unique().tolist()
        data_by_repo = [df[df["repository"] == r]["weighted_dts_score"].dropna().values for r in repos]

        bp = ax.violinplot(data_by_repo, positions=range(len(repos)), showmeans=True, showmedians=True)
        ax.set_xticks(range(len(repos)))
        ax.set_xticklabels(repos)
    else:
        ax.hist(df.get("weighted_dts_score", pd.Series([])), bins=20, edgecolor="black")

    ax.axhline(y=0.70, color="red", linestyle="--", linewidth=1.5, label="Gate threshold (0.70)")
    ax.set_xlabel("Repository")
    ax.set_ylabel("Weighted DTS Score")
    ax.set_title("DTS Score Distribution by Repository\n(H-E1 EXISTENCE PoC)")
    ax.set_ylim(0, 1.1)
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=FIGURES_CONFIG["dpi"])
    plt.close()
    print(f"  [Fig] Saved: {output_path}")


def plot_human_automated_scatter(
    auto_scores: np.ndarray,
    human_scores: np.ndarray,
    pearson_r: float,
    output_path: str,
) -> None:
    """FR-V4: Scatter plot with Pearson r annotation.

    Args:
        auto_scores: Automated DTS scores.
        human_scores: Human DTS scores.
        pearson_r: Pearson r value to annotate.
        output_path: Path to save PNG.
    """
    _ensure_dir(output_path)

    fig, ax = plt.subplots(figsize=FIGURES_CONFIG["figsize_scatter"])

    ax.scatter(auto_scores, human_scores, alpha=0.6, s=40, edgecolors="black", linewidths=0.5)

    # Regression line
    if len(auto_scores) > 1:
        m, b = np.polyfit(auto_scores, human_scores, 1)
        x_line = np.linspace(min(auto_scores), max(auto_scores), 100)
        ax.plot(x_line, m * x_line + b, "r-", linewidth=2, label=f"Regression line")

    ax.set_xlabel("Automated DTS Score")
    ax.set_ylabel("Human DTS Score")
    ax.set_title(f"Human vs. Automated DTS Scores\nr = {pearson_r:.3f}")
    ax.text(0.05, 0.95, f"Pearson r = {pearson_r:.3f}", transform=ax.transAxes,
            fontsize=12, verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.5, label="Perfect agreement")
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=FIGURES_CONFIG["dpi"])
    plt.close()
    print(f"  [Fig] Saved: {output_path}")


def plot_missing_field_analysis(df: pd.DataFrame, output_path: str) -> None:
    """FR-V5: Per-repo missing field frequency bar chart.

    Args:
        df: Scored corpus DataFrame with binary field columns.
        output_path: Path to save PNG.
    """
    _ensure_dir(output_path)

    from scorer import DTS_SECTIONS
    all_fields = [f for fields in DTS_SECTIONS.values() for f in fields]

    # Calculate missing rate per field per repo
    repos = df["repository"].unique().tolist() if "repository" in df.columns else ["all"]

    field_missing = {}
    for field in all_fields:
        if field in df.columns:
            field_missing[field] = {
                repo: 1.0 - df[df["repository"] == repo][field].mean()
                for repo in repos
                if len(df[df["repository"] == repo]) > 0
            }

    if not field_missing:
        return

    # Top 10 most missing fields overall
    overall_missing = {
        f: df[f].apply(lambda x: 1 - int(bool(x))).mean()
        for f in all_fields if f in df.columns
    }
    top_fields = sorted(overall_missing.keys(), key=lambda f: overall_missing[f], reverse=True)[:10]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(top_fields))
    width = 0.8 / max(len(repos), 1)
    colors = plt.cm.Set2(np.linspace(0, 1, len(repos)))

    for i, repo in enumerate(repos):
        vals = [field_missing.get(f, {}).get(repo, 0) for f in top_fields]
        ax.bar(x + i * width, vals, width, label=repo, color=colors[i], alpha=0.8, edgecolor="black")

    ax.set_xticks(x + width * (len(repos) - 1) / 2)
    ax.set_xticklabels(top_fields, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Missing Rate")
    ax.set_title("Top 10 Most Missing DTS Fields by Repository\n(H-E1 EXISTENCE PoC)")
    ax.set_ylim(0, 1.1)
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=FIGURES_CONFIG["dpi"])
    plt.close()
    print(f"  [Fig] Saved: {output_path}")


def generate_all_figures(
    df: pd.DataFrame,
    results: dict,
    figures_dir: str = "figures",
) -> None:
    """Generate all 5 mandatory figures.

    Args:
        df: Scored corpus DataFrame.
        results: Results dict from evaluate.py.
        figures_dir: Output directory for figures.
    """
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    # FR-V1
    plot_gate_metrics(results, f"{figures_dir}/gate_metrics_comparison.png")

    # FR-V2
    plot_section_coverage_heatmap(df, f"{figures_dir}/per_section_coverage_heatmap.png")

    # FR-V3
    plot_dts_distribution(df, f"{figures_dir}/dts_score_distribution.png")

    # FR-V4 (requires human scores in results)
    auto_scores = results.get("auto_scores_for_viz", np.array([]))
    human_scores = results.get("human_scores_for_viz", np.array([]))
    pearson_r = results.get("pearson_r", 0.0)

    if len(auto_scores) > 1 and len(human_scores) > 1:
        plot_human_automated_scatter(
            np.array(auto_scores),
            np.array(human_scores),
            pearson_r,
            f"{figures_dir}/human_automated_scatter.png",
        )
    else:
        print("  [Fig] Skipping scatter plot (no human scores available)")

    # FR-V5
    plot_missing_field_analysis(df, f"{figures_dir}/missing_field_analysis.png")

    print(f"  [Fig] All figures generated in: {figures_dir}")
