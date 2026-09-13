"""Generate 4 figures from H-E1 experiment results."""
import os
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

CODE_DIR = Path(__file__).parent
HYPOTHESIS_DIR = CODE_DIR.parent

from config import CATEGORIES, RETRIEVAL_HEAVY, GENERATION_HEAVY, FIGURES_DIR, RESULTS_DIR

CATEGORY_LABELS = {
    "single_doc_qa": "Single-Doc QA",
    "multi_doc_qa": "Multi-Doc QA*",
    "long_in_context_learning": "In-Context\nLearning†",
    "long_dialogue": "Long Dialogue",
    "code_repo": "Code Repo",
    "long_structured_data": "Structured Data*",
}

STRATEGY_COLORS = {
    "mohawk": "#e74c3c",
    "lawcat": "#2980b9",
    "hybrid4": "#27ae60",
}
STRATEGY_LABELS = {
    "mohawk": "MOHAWK-SSM",
    "lawcat": "LAWCAT",
    "hybrid4": "Hybrid-4",
}


def plot_delta_norm_bars(
    delta_norms: dict[str, dict[str, float]],
    output_path: str,
) -> None:
    """Fig 1: Grouped bar chart — Δ_norm per category per strategy."""
    fig, ax = plt.subplots(figsize=(12, 6))

    strategies = ["mohawk", "lawcat", "hybrid4"]
    n_cats = len(CATEGORIES)
    n_strategies = len(strategies)
    bar_width = 0.25
    x = np.arange(n_cats)

    for i, strategy in enumerate(strategies):
        values = [delta_norms.get(strategy, {}).get(cat, 0.0) for cat in CATEGORIES]
        bars = ax.bar(
            x + i * bar_width - bar_width,
            values,
            bar_width,
            label=STRATEGY_LABELS[strategy],
            color=STRATEGY_COLORS[strategy],
            alpha=0.85,
            edgecolor="black",
            linewidth=0.5,
        )

    ax.axhline(y=0, color="black", linewidth=0.8)
    ax.set_xlabel("LongBench v2 Task Category", fontsize=12)
    ax.set_ylabel("Δ_norm = (Acc_teacher − Acc_student) / Acc_teacher", fontsize=11)
    ax.set_title("H-E1: Accuracy Degradation by Task Type and Conversion Strategy", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels([CATEGORY_LABELS[c] for c in CATEGORIES], fontsize=9)
    ax.legend(fontsize=10)

    # Annotate retrieval-heavy categories
    for i, cat in enumerate(CATEGORIES):
        if cat in RETRIEVAL_HEAVY:
            ax.axvspan(i - 0.5, i + 0.5, alpha=0.08, color="red", label="retrieval-heavy" if i == 0 else "")
        elif cat in GENERATION_HEAVY:
            ax.axvspan(i - 0.5, i + 0.5, alpha=0.08, color="blue")

    retrieval_patch = mpatches.Patch(alpha=0.2, color="red", label="*Retrieval-heavy")
    generation_patch = mpatches.Patch(alpha=0.2, color="blue", label="†Generation-heavy")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles + [retrieval_patch, generation_patch], fontsize=9)

    ax.set_ylim(bottom=-0.05)
    fig.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[Fig 1] Saved: {output_path}")


def plot_delta_norm_heatmap(
    delta_norms: dict[str, dict[str, float]],
    output_path: str,
) -> None:
    """Fig 2: Heatmap — Δ_norm [strategy × category]."""
    strategies = ["mohawk", "lawcat", "hybrid4"]
    data = np.array([
        [delta_norms.get(s, {}).get(c, 0.0) for c in CATEGORIES]
        for s in strategies
    ])

    fig, ax = plt.subplots(figsize=(11, 4))
    im = ax.imshow(data, cmap="Reds", aspect="auto", vmin=0, vmax=max(0.5, data.max()))

    ax.set_xticks(range(len(CATEGORIES)))
    ax.set_xticklabels([CATEGORY_LABELS[c] for c in CATEGORIES], fontsize=9)
    ax.set_yticks(range(len(strategies)))
    ax.set_yticklabels([STRATEGY_LABELS[s] for s in strategies], fontsize=10)

    # Annotate cells
    for i in range(len(strategies)):
        for j in range(len(CATEGORIES)):
            color = "white" if data[i, j] > data.max() * 0.6 else "black"
            ax.text(j, i, f"{data[i,j]:.3f}", ha="center", va="center",
                    fontsize=8, color=color)

    plt.colorbar(im, ax=ax, label="Δ_norm")
    ax.set_title("H-E1: Δ_norm Heatmap (Strategy × Category)", fontsize=13)

    # Highlight retrieval columns
    for j, cat in enumerate(CATEGORIES):
        if cat in RETRIEVAL_HEAVY:
            ax.add_patch(plt.Rectangle((j - 0.5, -0.5), 1, len(strategies),
                                        fill=False, edgecolor="red", linewidth=2))

    fig.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[Fig 2] Saved: {output_path}")


def plot_error_bars(
    delta_norms: dict[str, dict[str, float]],
    ci_data: dict,
    output_path: str,
) -> None:
    """Fig 3: Error bar plot — Δ_norm(retrieval) vs Δ_norm(generation) per strategy."""
    strategies = ["mohawk", "lawcat", "hybrid4"]

    retrieval_cats = [c for c in CATEGORIES if c in RETRIEVAL_HEAVY]
    generation_cats = [c for c in CATEGORIES if c in GENERATION_HEAVY]

    ret_means = [np.mean([delta_norms.get(s, {}).get(c, 0.0) for c in retrieval_cats])
                 for s in strategies]
    gen_means = [np.mean([delta_norms.get(s, {}).get(c, 0.0) for c in generation_cats])
                 for s in strategies]

    # CI only available for SSM retrieval from bootstrap
    mohawk_idx = strategies.index("mohawk")
    ret_errs = [0.0] * len(strategies)
    if ci_data:
        ratio = ci_data.get("interaction_ratio", 1.0)
        ci_low = ci_data.get("interaction_ratio_ci_low", 0.0)
        ci_high = ci_data.get("interaction_ratio_ci_high", 0.0)
        # Approximate MOHAWK retrieval CI using the bootstrap ratio CI
        lawcat_ret = ret_means[strategies.index("lawcat")]
        mohawk_ci_low = ci_low * lawcat_ret
        mohawk_ci_high = ci_high * lawcat_ret
        ret_errs[mohawk_idx] = (mohawk_ci_high - mohawk_ci_low) / 2

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(strategies))
    width = 0.35

    bars1 = ax.bar(x - width/2, ret_means, width, label="Retrieval-heavy",
                   color="salmon", edgecolor="black", linewidth=0.7)
    bars2 = ax.bar(x + width/2, gen_means, width, label="Generation-heavy",
                   color="steelblue", edgecolor="black", linewidth=0.7)

    # Error bars for retrieval
    ax.errorbar(x - width/2, ret_means, yerr=ret_errs,
                fmt="none", color="black", capsize=4, linewidth=1.5)

    ax.set_xlabel("Conversion Strategy", fontsize=12)
    ax.set_ylabel("Mean Δ_norm", fontsize=12)
    ax.set_title("H-E1: Δ_norm by Task Type — Retrieval vs. Generation-Heavy", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels([STRATEGY_LABELS[s] for s in strategies], fontsize=10)
    ax.legend(fontsize=10)

    # Annotate ratio for MOHAWK
    ratio_val = ret_means[mohawk_idx] / max(gen_means[mohawk_idx], 1e-8)
    ax.text(x[mohawk_idx] - width/2 + 0.05, ret_means[mohawk_idx] + 0.01,
            f"×{ratio_val:.1f}", fontsize=8, color="darkred")

    ax.set_ylim(bottom=0)
    fig.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[Fig 3] Saved: {output_path}")


def plot_ratio_across_categories(
    delta_norm_ssm: dict[str, float],
    delta_norm_lawcat: dict[str, float],
    output_path: str,
) -> None:
    """Fig 4: Ratio Δ_norm^SSM / Δ_norm^LAWCAT across all 6 categories."""
    ratios = []
    for cat in CATEGORIES:
        ssm = delta_norm_ssm.get(cat, 0.0)
        lawcat = delta_norm_lawcat.get(cat, 0.0)
        ratios.append(ssm / max(lawcat, 1e-8))

    colors = ["#e74c3c" if cat in RETRIEVAL_HEAVY
              else "#2980b9" if cat in GENERATION_HEAVY
              else "#95a5a6"
              for cat in CATEGORIES]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(CATEGORIES)), ratios, color=colors, edgecolor="black", linewidth=0.7)

    ax.axhline(y=2.0, color="darkred", linestyle="--", linewidth=1.5, label="Gate threshold (2.0×)")
    ax.axhline(y=1.0, color="gray", linestyle=":", linewidth=1.0, label="Equal degradation (1.0×)")

    ax.set_xlabel("LongBench v2 Task Category", fontsize=12)
    ax.set_ylabel("Δ_norm^MOHAWK / Δ_norm^LAWCAT", fontsize=11)
    ax.set_title("H-E1: SSM vs. LAWCAT Degradation Ratio per Category", fontsize=13)
    ax.set_xticks(range(len(CATEGORIES)))
    ax.set_xticklabels([CATEGORY_LABELS[c] for c in CATEGORIES], fontsize=9)

    retrieval_patch = mpatches.Patch(color="#e74c3c", label="Retrieval-heavy")
    generation_patch = mpatches.Patch(color="#2980b9", label="Generation-heavy")
    neutral_patch = mpatches.Patch(color="#95a5a6", label="Neutral")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles + [retrieval_patch, generation_patch, neutral_patch], fontsize=9)

    # Annotate values
    for i, r in enumerate(ratios):
        ax.text(i, r + 0.05, f"{r:.2f}×", ha="center", fontsize=8)

    ax.set_ylim(bottom=0)
    fig.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[Fig 4] Saved: {output_path}")


def generate_all_figures(
    delta_norms: dict[str, dict[str, float]],
    analysis_results: dict,
    figures_dir: str | None = None,
) -> None:
    """Generate all 4 figures."""
    if figures_dir is None:
        figures_dir = str(FIGURES_DIR)
    os.makedirs(figures_dir, exist_ok=True)

    plot_delta_norm_bars(delta_norms, os.path.join(figures_dir, "fig1_bar.png"))
    plot_delta_norm_heatmap(delta_norms, os.path.join(figures_dir, "fig2_heatmap.png"))
    plot_error_bars(delta_norms, analysis_results, os.path.join(figures_dir, "fig3_errorbars.png"))
    plot_ratio_across_categories(
        delta_norm_ssm=delta_norms.get("mohawk", {}),
        delta_norm_lawcat=delta_norms.get("lawcat", {}),
        output_path=os.path.join(figures_dir, "fig4_ratio.png"),
    )
    print(f"\nAll figures saved to {figures_dir}/")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--results-dir", type=str, default=str(RESULTS_DIR))
    p.add_argument("--figures-dir", type=str, default=str(FIGURES_DIR))
    args = p.parse_args()

    analysis_path = os.path.join(args.results_dir, "analysis_results.json")
    if not os.path.exists(analysis_path):
        summary_path = os.path.join(args.results_dir, "evaluation_summary.json")
        with open(summary_path) as f:
            summary = json.load(f)
        delta_norms = summary["delta_norms"]
        analysis_results = {}
    else:
        with open(analysis_path) as f:
            analysis_results = json.load(f)
        delta_norms = analysis_results.get("delta_norms", {})

    generate_all_figures(delta_norms, analysis_results, args.figures_dir)
