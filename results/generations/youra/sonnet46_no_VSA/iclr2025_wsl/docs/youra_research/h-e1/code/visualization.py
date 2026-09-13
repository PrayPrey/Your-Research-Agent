"""Visualization: bar chart, PCA scatter, violin plot for OrbitVar results."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_orbitvar_bar(
    results: dict,
    threshold: float = 1e-6,
    save_path: str = "figures/orbitvar_comparison.png",
) -> None:
    """Log-scale bar chart with horizontal threshold line."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    encoders = ["C2\n(DeepSets)", "C3\n(NFN)", "CISE\n(baseline)"]
    values = [
        results["mean_orbitvar_c2"],
        results["mean_orbitvar_c3"],
        results["cise_baseline"],
    ]
    # Add tiny epsilon for log-scale if exactly 0
    values = [max(v, 1e-20) for v in values]
    colors = ["#2196F3", "#4CAF50", "#F44336"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(encoders, values, color=colors, width=0.5, alpha=0.85)
    ax.set_yscale("log")
    ax.axhline(threshold, color="black", linestyle="--", linewidth=1.2,
               label=f"Threshold (1e-6)")
    ax.set_ylabel("Mean OrbitVar (log scale)")
    ax.set_title("OrbitVar Comparison: DeepSets vs NFN vs CISE baseline\n(H-E1: Architecturally Invariant Encoders)")
    ax.legend()

    # Annotate bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val * 2,
                f"{val:.2e}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_pca_scatter(
    embeddings: dict,
    n_models: int = 10,
    save_path: str = "figures/pca_scatter.png",
) -> None:
    """
    PCA of encoder outputs for n_models × K permutations.
    embeddings: {encoder_name: list of (K+1, embed_dim) tensors per model}
    """
    from scipy.linalg import svd
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, axes = plt.subplots(1, len(embeddings), figsize=(5 * len(embeddings), 5))
    if len(embeddings) == 1:
        axes = [axes]

    colors_map = {"C2": "#2196F3", "C3": "#4CAF50", "CISE": "#F44336"}

    for ax, (name, emb_list) in zip(axes, embeddings.items()):
        # emb_list: list of (K+1, embed_dim) arrays/tensors
        n = min(n_models, len(emb_list))
        all_embs = np.vstack([e[:n].numpy() if hasattr(e, "numpy") else e[:n]
                              for e in emb_list[:n]])  # (n*(K+1), embed_dim)

        # PCA via SVD
        all_embs_centered = all_embs - all_embs.mean(0)
        if all_embs_centered.std() < 1e-15:
            # Perfectly invariant: all points same
            ax.scatter([0], [0], c=colors_map.get(name, "blue"), s=30, alpha=0.7)
            ax.set_title(f"{name} — perfectly invariant (OrbitVar≈0)")
        else:
            _, _, Vt = svd(all_embs_centered, full_matrices=False)
            pc = all_embs_centered @ Vt[:2].T  # (n*(K+1), 2)
            model_labels = np.repeat(np.arange(n), all_embs.shape[0] // n)
            scatter = ax.scatter(pc[:, 0], pc[:, 1], c=model_labels,
                                 cmap="tab10", s=15, alpha=0.6)
            ax.set_title(f"{name} — PCA of {n} models × K perms")

        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")

    plt.suptitle("Orbit Embedding Scatter (each color = one model, each dot = one permutation)")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_violin(
    per_model_vars: dict,
    save_path: str = "figures/violin_orbitvar.png",
) -> None:
    """Violin plot of per-model OrbitVar distributions."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    names = list(per_model_vars.keys())
    data = [per_model_vars[n] for n in names]
    colors_map = {"C2": "#2196F3", "C3": "#4CAF50", "CISE": "#F44336"}

    fig, ax = plt.subplots(figsize=(8, 5))
    parts = ax.violinplot(data, positions=range(len(names)), showmeans=True)
    for i, (pc, name) in enumerate(zip(parts["bodies"], names)):
        pc.set_facecolor(colors_map.get(name, "gray"))
        pc.set_alpha(0.75)

    ax.set_yscale("log")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names)
    ax.axhline(1e-6, color="black", linestyle="--", linewidth=1.2, label="Threshold (1e-6)")
    ax.set_ylabel("OrbitVar (log scale)")
    ax.set_title("Per-model OrbitVar Distribution (H-E1)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")
