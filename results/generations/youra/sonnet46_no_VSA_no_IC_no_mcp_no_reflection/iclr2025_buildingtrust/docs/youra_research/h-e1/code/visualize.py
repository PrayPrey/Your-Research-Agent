"""FR-5: Visualization — 5 figures for H-E1."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.decomposition import PCA

FIGURES_DIR = "../figures"
TASK_NAMES = ["TruthfulQA MC2", "BBQ", "WinoGrande", "WinoGender (all)"]
COLORS = {0: "#2196F3", 1: "#F44336"}  # SFT=blue, DPO=red
LABELS = {0: "SFT", 1: "DPO"}


def _save(fig: plt.Figure, out_dir: str, name: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Saved: {path}")


def plot_gate_metrics(loo_accuracy: float, p_value: float, out_dir: str = FIGURES_DIR) -> None:
    """FR-5.1: Gate metrics bar chart."""
    fig, ax = plt.subplots(figsize=(7, 5))
    values = [loo_accuracy, 0.67, 0.50]
    labels = [f"LOO Acc\n(k=1)\n{loo_accuracy:.3f}", "Threshold\n(≥0.67)", "Chance\n(0.50)"]
    colors = ["#4CAF50" if loo_accuracy >= 0.67 else "#FF9800", "#9C27B0", "#9E9E9E"]
    bars = ax.bar(labels, values, color=colors, edgecolor="black", linewidth=0.8, width=0.5)
    ax.axhline(0.67, color="#9C27B0", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.axhline(0.50, color="#9E9E9E", linestyle=":", linewidth=1.5, alpha=0.7)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.01, f"{val:.3f}",
                ha="center", va="bottom", fontsize=11, fontweight="bold")
    gate = "PASS ✓" if loo_accuracy >= 0.67 and p_value <= 0.05 else (
           "FAIL ✗" if loo_accuracy < 0.50 else "INCONCLUSIVE")
    ax.set_title(f"H-E1 Gate Metrics\np-value={p_value:.4f}  |  Gate: {gate}", fontsize=13)
    ax.set_ylabel("Accuracy", fontsize=12)
    ax.set_ylim(0, 1.1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    _save(fig, out_dir, "fig1_gate_metrics.png")


def plot_pca_scatter(X: np.ndarray, y: np.ndarray, out_dir: str = FIGURES_DIR) -> None:
    """FR-5.2: PCA 2D projection."""
    pca = PCA(n_components=2, random_state=42)
    Z = pca.fit_transform(X)
    var = pca.explained_variance_ratio_

    fig, ax = plt.subplots(figsize=(7, 6))
    for label in [0, 1]:
        mask = y == label
        ax.scatter(Z[mask, 0], Z[mask, 1], c=COLORS[label], label=LABELS[label],
                   s=100, edgecolors="black", linewidths=0.6, zorder=3)
    ax.set_xlabel(f"PC1 ({var[0]*100:.1f}% var)", fontsize=11)
    ax.set_ylabel(f"PC2 ({var[1]*100:.1f}% var)", fontsize=11)
    ax.set_title("PCA Projection of 4D Benchmark Score Vectors\nDPO vs SFT Models", fontsize=12)
    ax.legend(fontsize=11, framealpha=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    _save(fig, out_dir, "fig2_pca_scatter.png")


def plot_benchmark_boxplots(X: np.ndarray, y: np.ndarray, out_dir: str = FIGURES_DIR) -> None:
    """FR-5.3: Per-benchmark boxplots DPO vs SFT."""
    fig, axes = plt.subplots(1, 4, figsize=(14, 5), sharey=False)
    for i, (ax, task) in enumerate(zip(axes, TASK_NAMES)):
        data = {LABELS[0]: X[y == 0, i], LABELS[1]: X[y == 1, i]}
        bp = ax.boxplot(data.values(), patch_artist=True, widths=0.5,
                        medianprops={"color": "black", "linewidth": 2})
        for patch, label in zip(bp["boxes"], data.keys()):
            patch.set_facecolor(COLORS[0] if label == "SFT" else COLORS[1])
            patch.set_alpha(0.7)
        ax.set_xticklabels(data.keys(), fontsize=10)
        ax.set_title(task, fontsize=11)
        ax.set_ylabel("Score" if i == 0 else "", fontsize=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.suptitle("Benchmark Score Distributions: DPO vs SFT", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, out_dir, "fig3_benchmark_boxplots.png")


def plot_permutation_histogram(
    perm_scores: np.ndarray, loo_accuracy: float, p_value: float, out_dir: str = FIGURES_DIR
) -> None:
    """FR-5.4: Permutation null distribution vs observed."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(perm_scores, bins=30, color="#90A4AE", edgecolor="white",
            linewidth=0.5, label="Null distribution", density=True)
    ax.axvline(loo_accuracy, color="#F44336", linewidth=2.5, linestyle="-",
               label=f"Observed LOO acc = {loo_accuracy:.3f}")
    ax.axvline(0.67, color="#9C27B0", linewidth=1.5, linestyle="--",
               label="Threshold = 0.67")
    ax.set_xlabel("LOO Accuracy", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)
    ax.set_title(f"Permutation Test (n=1000)\np = {p_value:.4f}", fontsize=13)
    ax.legend(fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    _save(fig, out_dir, "fig4_permutation_histogram.png")


def plot_model_heatmap(
    X: np.ndarray, y: np.ndarray, model_ids: list[str], out_dir: str = FIGURES_DIR
) -> None:
    """FR-5.5: Model × benchmark heatmap."""
    short_ids = [mid.split("/")[-1][:25] for mid in model_ids]
    alignment = ["DPO" if yi == 1 else "SFT" for yi in y]
    row_labels = [f"{al} | {sid}" for al, sid in zip(alignment, short_ids)]

    fig, ax = plt.subplots(figsize=(10, max(5, len(model_ids) * 0.55)))
    im = ax.imshow(X, aspect="auto", cmap="RdYlGn", vmin=0.3, vmax=0.9)
    ax.set_xticks(range(4))
    ax.set_xticklabels(TASK_NAMES, fontsize=10, rotation=15, ha="right")
    ax.set_yticks(range(len(model_ids)))
    ax.set_yticklabels(row_labels, fontsize=8)
    # Color row labels by alignment
    for tick, yi in zip(ax.get_yticklabels(), y):
        tick.set_color(COLORS[yi])
    plt.colorbar(im, ax=ax, label="Score", shrink=0.8)
    ax.set_title("Model × Benchmark Score Heatmap\n(red=SFT, blue=DPO labels)", fontsize=12)
    fig.tight_layout()
    _save(fig, out_dir, "fig5_model_heatmap.png")


def main(
    X: np.ndarray,
    y: np.ndarray,
    results: dict,
    model_ids: list[str],
    out_dir: str = FIGURES_DIR,
) -> None:
    """Generate all 5 figures."""
    perm_scores = np.array(results["perm_scores"])
    print("Generating figures...")
    plot_gate_metrics(results["loo_accuracy"], results["p_value"], out_dir)
    plot_pca_scatter(X, y, out_dir)
    plot_benchmark_boxplots(X, y, out_dir)
    plot_permutation_histogram(perm_scores, results["loo_accuracy"], results["p_value"], out_dir)
    plot_model_heatmap(X, y, model_ids, out_dir)
    print(f"✓ All 5 figures saved to {out_dir}/")


if __name__ == "__main__":
    # Self-test
    rng = np.random.default_rng(42)
    X = np.vstack([rng.normal([0.4, 0.5, 0.6, 0.5], 0.05, (6, 4)),
                   rng.normal([0.6, 0.7, 0.7, 0.6], 0.05, (6, 4))])
    y = np.array([0]*6 + [1]*6)
    model_ids = [f"org/sft-model-{i}" for i in range(6)] + [f"org/dpo-model-{i}" for i in range(6)]
    perm_scores = rng.uniform(0.4, 0.6, 1000)
    results = {"loo_accuracy": 0.75, "p_value": 0.02, "perm_scores": perm_scores.tolist()}
    main(X, y, results, model_ids, out_dir="/tmp/test_figs")
    print("✓ Self-test passed")
