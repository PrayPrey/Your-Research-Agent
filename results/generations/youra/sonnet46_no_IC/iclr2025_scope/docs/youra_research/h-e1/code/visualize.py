from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

LAYER_TYPE_COLORS = {
    "attention": "#1f77b4",
    "ffn": "#ff7f0e",
    "other": "#2ca02c",
}

def _layer_type(name: str) -> str:
    n = name.lower()
    if any(k in n for k in ["query", "key", "value", "attention", "q_proj", "k_proj", "v_proj"]):
        return "attention"
    if any(k in n for k in ["dense", "intermediate", "fc", "ffn", "mlp"]):
        return "ffn"
    return "other"


def plot_scatter_erank_vs_oracle(
    erank_maps: dict[str, dict],
    oracle_maps: dict[str, dict],
    corr_results: dict[str, dict],
    save_path: Path,
) -> None:
    """3-subplot scatter (BERT, DeBERTa, ViT), color by layer type."""
    model_names = list(erank_maps.keys())
    n = len(model_names)
    fig, axes = plt.subplots(1, max(n, 1), figsize=(6 * max(n, 1), 5))
    if n == 1:
        axes = [axes]

    for ax, model_name in zip(axes, model_names):
        erank_map = erank_maps[model_name]
        oracle_map = oracle_maps[model_name]
        common = sorted(set(erank_map.keys()) & set(oracle_map.keys()))
        x = [erank_map[k] for k in common]
        y = [float(oracle_map[k]) for k in common]
        colors = [LAYER_TYPE_COLORS[_layer_type(k)] for k in common]

        ax.scatter(x, y, c=colors, alpha=0.7, s=40)
        ax.axhline(y=0.65 * max(y + [1]), color="gray", linestyle="--", alpha=0.4, label="r=0.65 ref")

        r = corr_results.get(model_name, {}).get("r", float("nan"))
        p = corr_results.get(model_name, {}).get("p_one_tailed", float("nan"))
        ax.set_title(f"{model_name.split('/')[-1]}\nr={r:.3f}, p={p:.4f}")
        ax.set_xlabel("erank(W₀)")
        ax.set_ylabel("Oracle Rank")

        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker="o", color="w", markerfacecolor=LAYER_TYPE_COLORS["attention"], label="Attention"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=LAYER_TYPE_COLORS["ffn"], label="FFN"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=LAYER_TYPE_COLORS["other"], label="Other"),
        ]
        ax.legend(handles=legend_elements, fontsize=8)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_erank_heatmap(erank_map: dict[str, float], model_name: str, save_path: Path) -> None:
    """Layer-depth heatmap of erank values."""
    names = list(erank_map.keys())
    values = list(erank_map.values())
    n = len(names)
    # arrange in 2D grid approximately square
    cols = max(1, int(np.ceil(np.sqrt(n))))
    rows = max(1, int(np.ceil(n / cols)))
    grid = np.full((rows, cols), np.nan)
    for i, v in enumerate(values):
        grid[i // cols, i % cols] = v

    fig, ax = plt.subplots(figsize=(max(8, cols), max(5, rows)))
    sns.heatmap(grid, ax=ax, cmap="viridis", mask=np.isnan(grid), cbar_kws={"label": "erank"})
    ax.set_title(f"erank heatmap — {model_name.split('/')[-1]}")
    ax.set_xlabel("Layer index (col)")
    ax.set_ylabel("Layer group (row)")
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_oracle_rank_histogram(
    oracle_rank_map: dict[str, int], model_name: str, save_path: Path
) -> None:
    """Histogram of oracle rank distribution {4,8,16,32,64} per model."""
    ranks = list(oracle_rank_map.values())
    bins = [4, 8, 16, 32, 64]
    counts = {r: ranks.count(r) for r in bins}

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar([str(r) for r in bins], [counts[r] for r in bins], color="#1f77b4", edgecolor="black")
    ax.set_xlabel("Oracle Rank")
    ax.set_ylabel("Count")
    ax.set_title(f"Oracle Rank Distribution — {model_name.split('/')[-1]}")
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_bootstrap_ci(corr_results: dict[str, dict], save_path: Path) -> None:
    """Bar plot of Pearson r ± 95% CI per model family."""
    models = list(corr_results.keys())
    rs = [corr_results[m].get("r", 0.0) for m in models]
    ci_lows = [corr_results[m].get("ci_low", 0.0) for m in models]
    ci_highs = [corr_results[m].get("ci_high", 0.0) for m in models]
    errs_low = [r - lo for r, lo in zip(rs, ci_lows)]
    errs_high = [hi - r for r, hi in zip(rs, ci_highs)]

    labels = [m.split("/")[-1] for m in models]
    x = np.arange(len(models))

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(x, rs, color="#1f77b4", alpha=0.8, edgecolor="black")
    ax.errorbar(x, rs, yerr=[errs_low, errs_high], fmt="none", color="black", capsize=5)
    ax.axhline(y=0.65, color="red", linestyle="--", label="Threshold (r=0.65)")
    ax.axhline(y=0.0, color="gray", linestyle="-", alpha=0.3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylabel("Pearson r")
    ax.set_title("Pearson r ± 95% Bootstrap CI per Model Family")
    ax.legend()
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def generate_all_figures(
    erank_maps: dict,
    oracle_maps: dict,
    corr_results: dict,
    figures_dir: Path,
) -> list[str]:
    """Generate and save all mandatory figures. Returns list of saved paths."""
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    saved = []

    scatter_path = figures_dir / "scatter_erank_vs_oracle.png"
    plot_scatter_erank_vs_oracle(erank_maps, oracle_maps, corr_results, scatter_path)
    saved.append(str(scatter_path))
    print(f"  Saved: {scatter_path}")

    for model_name, erank_map in erank_maps.items():
        slug = model_name.replace("/", "-")
        heatmap_path = figures_dir / f"erank_heatmap_{slug}.png"
        plot_erank_heatmap(erank_map, model_name, heatmap_path)
        saved.append(str(heatmap_path))
        print(f"  Saved: {heatmap_path}")

    for model_name, oracle_map in oracle_maps.items():
        slug = model_name.replace("/", "-")
        hist_path = figures_dir / f"oracle_hist_{slug}.png"
        plot_oracle_rank_histogram(oracle_map, model_name, hist_path)
        saved.append(str(hist_path))
        print(f"  Saved: {hist_path}")

    ci_path = figures_dir / "bootstrap_ci.png"
    plot_bootstrap_ci(corr_results, ci_path)
    saved.append(str(ci_path))
    print(f"  Saved: {ci_path}")

    return saved
