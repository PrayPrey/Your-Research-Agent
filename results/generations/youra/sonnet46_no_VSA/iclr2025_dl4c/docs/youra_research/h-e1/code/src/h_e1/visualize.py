"""Visualization: heatmaps, histograms, t-SNE for H-E1."""
import os
import logging
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from .similarity import SOURCES, BENCHMARKS

logger = logging.getLogger(__name__)

SOURCE_LABELS = ["HumanEval-train", "MBPP-train", "LeetCode", "Equal-mix"]
BENCHMARK_LABELS = ["HumanEval+", "MBPP+"]


def plot_heatmaps(sim_matrices: dict, output_dir: str, threshold: float = 0.95) -> None:
    """Saves dual-encoder side-by-side 4x2 heatmaps with threshold annotated."""
    os.makedirs(output_dir, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax, (encoder, mat) in zip(axes, sim_matrices.items()):
        sns.heatmap(
            mat,
            ax=ax,
            annot=True,
            fmt=".3f",
            xticklabels=BENCHMARK_LABELS,
            yticklabels=SOURCE_LABELS,
            vmin=0.0,
            vmax=1.0,
            cmap="Blues",
        )
        ax.set_title(f"{encoder.upper()} — Mean Pairwise Cosine Similarity")
        ax.set_xlabel("Test Benchmark")
        ax.set_ylabel("SFT Training Source")

    fig.suptitle(f"Code Embedding Distinctiveness (threshold={threshold})", fontsize=13)
    fig.tight_layout()
    out_path = os.path.join(output_dir, "similarity_heatmaps.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved heatmap: {out_path}")


def plot_histograms(embeddings: dict, output_dir: str) -> None:
    """Per-source pairwise similarity distributions (optional)."""
    import torch
    os.makedirs(output_dir, exist_ok=True)

    for encoder in ["codebert", "minilm"]:
        fig, axes = plt.subplots(2, 3, figsize=(15, 8))
        axes = axes.flatten()

        names = list(embeddings.keys())
        for idx, name in enumerate(names[:6]):
            emb = embeddings[name][encoder].cpu()
            # sample at most 500 to keep it fast
            if emb.shape[0] > 500:
                idx_sample = torch.randperm(emb.shape[0])[:500]
                emb = emb[idx_sample]
            sims = (emb @ emb.T).numpy()
            upper = sims[np.triu_indices(len(sims), k=1)]
            axes[idx].hist(upper, bins=50, color="steelblue", alpha=0.7)
            axes[idx].set_title(f"{name}\n({encoder})")
            axes[idx].set_xlabel("Cosine Similarity")

        fig.tight_layout()
        out_path = os.path.join(output_dir, f"hist_{encoder}.png")
        fig.savefig(out_path, dpi=120, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved histogram: {out_path}")


def plot_tsne(embeddings: dict, output_dir: str, encoder: str = "codebert") -> None:
    """2D t-SNE projection colored by corpus source."""
    import torch
    from sklearn.manifold import TSNE

    os.makedirs(output_dir, exist_ok=True)

    all_embs = []
    all_labels = []
    names = list(embeddings.keys())

    for name in names:
        emb = embeddings[name][encoder].cpu()
        # Cap at 200 per corpus for speed
        if emb.shape[0] > 200:
            idx = torch.randperm(emb.shape[0])[:200]
            emb = emb[idx]
        all_embs.append(emb.numpy())
        all_labels.extend([name] * emb.shape[0])

    X = np.concatenate(all_embs, axis=0)
    logger.info(f"Running t-SNE on {X.shape[0]} points ({encoder})...")
    proj = TSNE(n_components=2, random_state=42, perplexity=30, n_iter=1000).fit_transform(X)

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.tab10(np.linspace(0, 1, len(names)))
    start = 0
    for i, name in enumerate(names):
        n = all_labels.count(name)
        ax.scatter(proj[start:start + n, 0], proj[start:start + n, 1],
                   label=name, alpha=0.6, s=20, color=colors[i])
        start += n

    ax.legend(loc="best", fontsize=8)
    ax.set_title(f"t-SNE: {encoder.upper()} Embeddings by Source")
    fig.tight_layout()
    out_path = os.path.join(output_dir, f"tsne_{encoder}.png")
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved t-SNE: {out_path}")
