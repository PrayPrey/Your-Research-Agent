import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE


def plot_gate_comparison(proposed_acc: float, random_acc: float, threshold: float,
                         out_path: str) -> None:
    """Bar chart comparing proposed vs random baseline accuracy."""
    fig, ax = plt.subplots(figsize=(8, 6))

    x = ["Proposed\n(InfoNCE)", "Random\nBaseline"]
    heights = [proposed_acc, random_acc]
    colors = ["#2ecc71" if proposed_acc > threshold else "#e74c3c", "#95a5a6"]

    bars = ax.bar(x, heights, color=colors, edgecolor="black", linewidth=1.2)
    ax.axhline(y=threshold, color="#e74c3c", linestyle="--", linewidth=2,
               label=f"Gate threshold ({threshold:.1%})")

    ax.set_ylabel("Linear Probe Accuracy", fontsize=12)
    ax.set_title("H-M1 Gate Check: Task Embedding Quality", fontsize=14)
    ax.set_ylim(0, max(1.0, max(heights) * 1.2))

    for bar, height in zip(bars, heights):
        ax.annotate(f"{height:.1%}", xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points", ha="center", fontsize=11)

    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_tsne(embeddings: np.ndarray, task_ids: np.ndarray, out_path: str) -> None:
    """t-SNE visualization of learned embeddings colored by task."""
    if len(embeddings) > 5000:
        idx = np.random.choice(len(embeddings), 5000, replace=False)
        embeddings = embeddings[idx]
        task_ids = task_ids[idx]

    tsne = TSNE(n_components=2, perplexity=min(30, len(embeddings) - 1),
                random_state=42, max_iter=1000)
    emb_2d = tsne.fit_transform(embeddings)

    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(emb_2d[:, 0], emb_2d[:, 1], c=task_ids, cmap="tab10",
                         alpha=0.6, s=20)

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Task ID", fontsize=11)

    ax.set_xlabel("t-SNE 1", fontsize=11)
    ax.set_ylabel("t-SNE 2", fontsize=11)
    ax.set_title("Task Embeddings t-SNE Visualization", fontsize=14)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_ablation(dim_to_acc: dict, out_path: str) -> None:
    """Ablation plot: embedding dimension vs accuracy."""
    dims = sorted(dim_to_acc.keys())
    accs = [dim_to_acc[d] for d in dims]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(dims, accs, "o-", markersize=10, linewidth=2, color="#3498db")

    for d, acc in zip(dims, accs):
        ax.annotate(f"{acc:.1%}", xy=(d, acc), xytext=(0, 8),
                    textcoords="offset points", ha="center", fontsize=10)

    ax.set_xlabel("Embedding Dimension", fontsize=12)
    ax.set_ylabel("Linear Probe Accuracy", fontsize=12)
    ax.set_title("Embedding Dimension Ablation", fontsize=14)
    ax.set_xticks(dims)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_per_task_accuracy(per_task_acc: dict, task_names: list, out_path: str) -> None:
    """Per-task accuracy bar chart."""
    tasks = list(per_task_acc.keys())
    accs = [per_task_acc[t] for t in tasks]
    labels = [task_names[t] if t < len(task_names) else f"Task {t}" for t in tasks]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, accs, color="#3498db", edgecolor="black", linewidth=1)

    ax.set_ylabel("Accuracy", fontsize=12)
    ax.set_xlabel("Task", fontsize=12)
    ax.set_title("Per-Task Probe Accuracy", fontsize=14)
    ax.set_ylim(0, 1.0)

    for bar, acc in zip(bars, accs):
        ax.annotate(f"{acc:.1%}", xy=(bar.get_x() + bar.get_width() / 2, acc),
                    xytext=(0, 5), textcoords="offset points", ha="center", fontsize=9)

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
