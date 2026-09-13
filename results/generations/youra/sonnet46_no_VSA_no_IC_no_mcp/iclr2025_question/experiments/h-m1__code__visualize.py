"""Visualization for H-M1."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_all(
    results: list,
    indicators: dict,
    secondary: dict,
    figures_dir: str,
    threshold: float = 0.1,
    dpi: int = 150,
) -> None:
    os.makedirs(figures_dir, exist_ok=True)
    eligible = [r for r in results if r["has_paraphrase"] and r["mean_intra_var"] is not None]
    if not eligible:
        print("[H-M1] No eligible questions for visualization")
        return

    vars_sorted = sorted([r["mean_intra_var"] for r in eligible])

    # fig1: gate bar chart
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(range(len(vars_sorted)), vars_sorted, color="steelblue", alpha=0.7)
    ax.axhline(threshold, color="red", linestyle="--", label=f"Threshold={threshold}")
    ax.set_xlabel("Question (sorted)")
    ax.set_ylabel("Mean intra-cluster TE variance (nats²)")
    ax.set_title("H-M1: Intra-cluster TE variance per eligible question")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "fig1_gate_bar.png"), dpi=dpi)
    plt.close(fig)

    # fig2: violin plot
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.violinplot([vars_sorted], positions=[0], showmedians=True)
    ax.axhline(threshold, color="red", linestyle="--", label=f"Threshold={threshold}")
    ax.set_xticks([0])
    ax.set_xticklabels(["Eligible questions"])
    ax.set_ylabel("Mean intra-cluster TE variance (nats²)")
    ax.set_title("H-M1: Variance distribution")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "fig2_violin_intra_var.png"), dpi=dpi)
    plt.close(fig)

    # fig3: scatter cluster size vs variance
    fig, ax = plt.subplots(figsize=(6, 5))
    xs = [r["n_multi_member_clusters"] for r in eligible]
    ys = [r["mean_intra_var"] for r in eligible]
    ax.scatter(xs, ys, alpha=0.6)
    ax.set_xlabel("# multi-member clusters")
    ax.set_ylabel("Mean intra-cluster TE variance (nats²)")
    ax.set_title("H-M1: Cluster count vs TE variance")
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "fig3_scatter_size_var.png"), dpi=dpi)
    plt.close(fig)

    # fig4: representative question per-sample TE distribution
    # Use 3 representative questions: low SE, high SE, borderline
    se_vals = [r["se_score"] for r in eligible]
    se_median = np.median(se_vals)
    low_se = min(eligible, key=lambda r: r["se_score"])
    high_se = max(eligible, key=lambda r: r["se_score"])
    borderline = min(eligible, key=lambda r: abs(r["se_score"] - se_median))
    reps = [("Low SE", low_se), ("High SE", high_se), ("Borderline", borderline)]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, (label, r) in zip(axes, reps):
        pste = r["per_sample_te"]
        K = len(pste)
        if K == 0:
            ax.set_title(f"{label}\n(no data)")
            continue
        K_mat = min(K, 10)
        # Build pairwise diff matrix as proxy for NLI heatmap
        mat = np.zeros((K_mat, K_mat))
        for i in range(K_mat):
            for j in range(K_mat):
                mat[i, j] = abs(pste[i] - pste[j]) if i != j else 0
        try:
            import seaborn as sns
            sns.heatmap(mat, ax=ax, cmap="viridis", square=True, cbar=True)
        except ImportError:
            im = ax.imshow(mat, cmap="viridis")
            fig.colorbar(im, ax=ax)
        ax.set_title(f"{label}\nSE={r['se_score']:.3f}, var={r['mean_intra_var']:.4f}")
    fig.suptitle("H-M1: Per-sample TE pairwise diff (representative questions)")
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "fig4_nli_heatmap.png"), dpi=dpi)
    plt.close(fig)

    # fig5: threshold sensitivity
    if secondary and "threshold_sensitivity" in secondary:
        ts = secondary["threshold_sensitivity"]
        thresholds = sorted(ts.keys())
        fractions = [ts[t] for t in thresholds]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar([str(t) for t in thresholds], fractions, color="steelblue", alpha=0.7)
        ax.set_xlabel("Variance threshold (nats²)")
        ax.set_ylabel("Fraction of eligible questions passing")
        ax.set_title("H-M1: Threshold sensitivity")
        ax.set_ylim(0, 1)
        fig.tight_layout()
        fig.savefig(os.path.join(figures_dir, "fig5_threshold_sensitivity.png"), dpi=dpi)
        plt.close(fig)

    print(f"[H-M1] Figures saved to {figures_dir}")
