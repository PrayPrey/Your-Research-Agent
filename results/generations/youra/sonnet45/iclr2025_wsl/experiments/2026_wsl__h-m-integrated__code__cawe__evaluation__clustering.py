"""Clustering Validation Module for h-m-integrated.

Evaluates whether CAWE embeddings preserve architecture-family structure
by measuring silhouette score with architecture labels as ground truth.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import silhouette_score
from sklearn.manifold import TSNE
import numpy as np
from typing import Dict, Tuple
import matplotlib.pyplot as plt


class ClusteringEvaluator:
    """Evaluator for architecture clustering validation."""

    def __init__(self, model: nn.Module, device: str = 'cuda'):
        """Initialize evaluator.

        Args:
            model: CAWE model
            device: Device to use
        """
        self.model = model.to(device)
        self.device = device

    def extract_embeddings(self, loader: DataLoader) -> Tuple[np.ndarray, np.ndarray]:
        """Extract CAWE embeddings for all models.

        Args:
            loader: DataLoader with all models

        Returns:
            embeddings: [N, embed_dim] numpy array
            labels: [N] numpy array of architecture family indices (0=cnn, 1=transformer, 2=mlp)
        """
        self.model.eval()
        embeddings_list = []
        labels_list = []

        family_to_idx = {'cnn': 0, 'transformer': 1, 'mlp': 2}

        with torch.no_grad():
            for batch in loader:
                weights, arch_family_batch, _ = batch
                weights = {k: v.to(self.device) for k, v in weights.items()}

                # Get embeddings before regression head
                # Assuming CAWE has a method to extract embeddings
                for i, arch_family in enumerate(arch_family_batch):
                    single_weights = {k: v[i:i+1] for k, v in weights.items()}
                    embedding = self._extract_single_embedding(single_weights, arch_family)
                    embeddings_list.append(embedding.cpu().numpy())
                    labels_list.append(family_to_idx[arch_family])

        embeddings = np.vstack(embeddings_list)
        labels = np.array(labels_list)

        print(f"Extracted {len(embeddings)} embeddings, shape: {embeddings.shape}")
        return embeddings, labels

    def _extract_single_embedding(self, weights: Dict[str, torch.Tensor], arch_family: str) -> torch.Tensor:
        """Extract embedding for a single model.

        This accesses the NFT backbone's output before the regression head.
        """
        # Tokenize
        if arch_family == 'cnn':
            tokens = self.model.cnn_tokenizer(weights)
        elif arch_family == 'transformer':
            tokens = self.model.transformer_tokenizer(weights)
        else:  # mlp
            tokens = self.model.mlp_tokenizer(weights)

        # Pass through NFT backbone
        nft_output = self.model.nft(tokens.unsqueeze(0))  # [1, L, C]

        # Global average pooling to get embedding
        embedding = nft_output.mean(dim=1)  # [1, C]

        return embedding.squeeze(0)

    def compute_silhouette(self, embeddings: np.ndarray, labels: np.ndarray) -> float:
        """Compute silhouette score.

        Args:
            embeddings: [N, embed_dim] embeddings
            labels: [N] architecture family labels

        Returns:
            silhouette_score: Clustering quality metric (-1 to 1, higher better)
        """
        score = silhouette_score(embeddings, labels, metric='euclidean')
        print(f"Silhouette score: {score:.4f}")
        return float(score)

    def visualize_tsne(
        self,
        embeddings: np.ndarray,
        labels: np.ndarray,
        output_path: str = 'clustering_tsne.png'
    ):
        """Visualize embeddings with t-SNE.

        Args:
            embeddings: [N, embed_dim] embeddings
            labels: [N] architecture family labels
            output_path: Path to save figure
        """
        # t-SNE projection
        tsne = TSNE(n_components=2, random_state=42, perplexity=30)
        embeddings_2d = tsne.fit_transform(embeddings)

        # Plot
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = ['red', 'blue', 'green']
        labels_map = {0: 'CNN', 1: 'Transformer', 2: 'MLP'}

        for label_idx in range(3):
            mask = labels == label_idx
            ax.scatter(
                embeddings_2d[mask, 0],
                embeddings_2d[mask, 1],
                c=colors[label_idx],
                label=labels_map[label_idx],
                alpha=0.6,
                s=50
            )

        ax.set_xlabel('t-SNE Component 1')
        ax.set_ylabel('t-SNE Component 2')
        ax.set_title('CAWE Embeddings - Architecture Clustering')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"t-SNE visualization saved to {output_path}")
