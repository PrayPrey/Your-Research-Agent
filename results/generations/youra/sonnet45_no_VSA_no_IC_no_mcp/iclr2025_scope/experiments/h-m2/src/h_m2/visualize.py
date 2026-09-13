from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


class Visualizer:
    """Generate required gate metrics chart."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_gate_metrics(self, similarity: float, threshold: float):
        """REQUIRED: Similarity vs threshold bar chart."""
        fig, ax = plt.subplots(figsize=(8, 6))

        labels = ['Achieved', 'Threshold']
        values = [similarity, threshold]
        colors = ['green' if similarity >= threshold else 'red', 'blue']

        bars = ax.bar(labels, values, color=colors, alpha=0.7)

        # Annotate values
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.3f}', ha='center', va='bottom', fontsize=12)

        ax.set_ylabel('Intra-Family Similarity', fontsize=12)
        ax.set_title('H-M2 Gate Metrics: Clustering Quality', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.0)
        ax.axhline(y=threshold, color='gray', linestyle='--', alpha=0.5, label='Pass Threshold')
        ax.legend()

        plt.tight_layout()
        plt.savefig(self.output_dir / 'gate_metrics.png', dpi=150, bbox_inches='tight')
        plt.close()

    def plot_embedding_space(self, embeddings: np.ndarray, labels: np.ndarray):
        """Optional: 2D UMAP projection."""
        try:
            from umap import UMAP
            reducer = UMAP(n_components=2, random_state=42)
            embedding_2d = reducer.fit_transform(embeddings)
        except ImportError:
            from sklearn.manifold import TSNE
            reducer = TSNE(n_components=2, random_state=42, perplexity=min(5, len(embeddings)-1))
            embedding_2d = reducer.fit_transform(embeddings)

        fig, ax = plt.subplots(figsize=(10, 8))
        scatter = ax.scatter(embedding_2d[:, 0], embedding_2d[:, 1],
                           c=labels, cmap='tab10', s=100, alpha=0.7)
        ax.set_title('Embedding Space (2D Projection)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Dim 1')
        ax.set_ylabel('Dim 2')
        plt.colorbar(scatter, ax=ax, label='Cluster')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'embedding_space.png', dpi=150, bbox_inches='tight')
        plt.close()

    def plot_similarity_heatmap(self, similarity_matrix: np.ndarray, labels: np.ndarray):
        """Optional: Pairwise similarity heatmap."""
        # Order by cluster
        order = np.argsort(labels)
        ordered_sim = similarity_matrix[order][:, order]

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(ordered_sim, cmap='RdYlGn', vmin=0, vmax=1, square=True,
                   cbar_kws={'label': 'Cosine Similarity'}, ax=ax)
        ax.set_title('Pairwise Similarity (Ordered by Cluster)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'similarity_heatmap.png', dpi=150, bbox_inches='tight')
        plt.close()
