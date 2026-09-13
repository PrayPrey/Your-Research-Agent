"""
Visualizer for h-m-integrated
Generate figures for gate metrics, embedding space, confusion matrix, etc.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.metrics import confusion_matrix
from pathlib import Path
from typing import Dict


class Visualizer:
    """Visualization suite for h-m-integrated."""

    def __init__(self, config):
        """
        Initialize visualizer.

        Args:
            config: ExperimentConfig instance
        """
        self.config = config
        self.viz_config = config.visualization
        self.figures_dir = Path(self.viz_config.figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        sns.set_style("whitegrid")

    def plot_gate_metrics(
        self,
        nmi_scores: Dict[str, float],
        threshold: float = None,
        gap_threshold: float = None,
        save_path: str = None
    ):
        """
        Plot NMI bar chart with threshold line.

        Args:
            nmi_scores: Dict mapping method name to NMI score
            threshold: NMI threshold line (default from config)
            gap_threshold: Baseline gap threshold (default from config)
            save_path: Save path (default: figures/gate_metrics.png)
        """
        if threshold is None:
            threshold = self.config.gate.nmi_threshold
        if gap_threshold is None:
            gap_threshold = self.config.gate.baseline_gap_threshold
        if save_path is None:
            save_path = self.figures_dir / "gate_metrics.png"

        # Prepare data
        methods = ['semantic', 'permutation', 'lda', 'lexical']
        nmis = [nmi_scores.get(m, 0.0) for m in methods]
        colors = ['#2ecc71' if m == 'semantic' else '#95a5a6' for m in methods]

        # Create figure
        fig, ax = plt.subplots(figsize=self.viz_config.figsize_bar)

        # Bar chart
        bars = ax.bar(methods, nmis, color=colors, alpha=0.8, edgecolor='black')

        # Threshold line
        ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2,
                   label=f'NMI Threshold ({threshold})')

        # Add baseline gap annotation
        if len(nmis) >= 4:
            semantic_nmi = nmis[0]
            baseline_nmis = nmis[1:]
            max_baseline = max(baseline_nmis)
            gap = semantic_nmi - max_baseline

            # Arrow showing gap
            ax.annotate('', xy=(0, semantic_nmi), xytext=(0, max_baseline),
                       arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
            ax.text(0.3, (semantic_nmi + max_baseline) / 2,
                   f'Gap: {gap:.3f}\n(threshold: {gap_threshold})',
                   fontsize=10, color='blue', weight='bold')

        # Labels
        ax.set_xlabel('Method', fontsize=12, weight='bold')
        ax.set_ylabel('Normalized Mutual Information (NMI)', fontsize=12, weight='bold')
        ax.set_title('Gate Metrics: NMI Comparison', fontsize=14, weight='bold')
        ax.legend(loc='upper right')
        ax.set_ylim(0, 1.0)

        # Value labels on bars
        for bar, nmi in zip(bars, nmis):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 0.02,
                   f'{nmi:.3f}', ha='center', va='bottom', fontsize=10, weight='bold')

        plt.tight_layout()
        plt.savefig(save_path, dpi=self.viz_config.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved gate metrics plot: {save_path}")

    def plot_embedding_space(
        self,
        embeddings: np.ndarray,
        labels_true: np.ndarray,
        labels_pred: np.ndarray = None,
        save_path: str = None
    ):
        """
        Plot t-SNE projection of embedding space.

        Args:
            embeddings: [N, 384] embeddings
            labels_true: True lifecycle labels
            labels_pred: Predicted cluster labels (optional)
            save_path: Save path (default: figures/embedding_space.png)
        """
        if save_path is None:
            save_path = self.figures_dir / "embedding_space.png"

        print("Computing t-SNE projection...")
        tsne = TSNE(
            n_components=2,
            perplexity=self.viz_config.tsne_perplexity,
            random_state=self.viz_config.tsne_random_state,
            n_iter=self.viz_config.tsne_n_iter
        )
        embeddings_2d = tsne.fit_transform(embeddings)

        # Create figure
        fig, ax = plt.subplots(figsize=self.viz_config.figsize_scatter)

        # Scatter plot colored by true labels
        label_names = ['General Information', 'Responsible AI']
        for label_idx, label_name in enumerate(label_names):
            mask = labels_true == label_idx
            ax.scatter(
                embeddings_2d[mask, 0],
                embeddings_2d[mask, 1],
                label=label_name,
                alpha=0.6,
                s=50
            )

        ax.set_xlabel('t-SNE Dimension 1', fontsize=12, weight='bold')
        ax.set_ylabel('t-SNE Dimension 2', fontsize=12, weight='bold')
        ax.set_title('Embedding Space (t-SNE Projection)', fontsize=14, weight='bold')
        ax.legend(loc='best')

        plt.tight_layout()
        plt.savefig(save_path, dpi=self.viz_config.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved embedding space plot: {save_path}")

    def plot_confusion_matrix(
        self,
        labels_true: np.ndarray,
        labels_pred: np.ndarray,
        save_path: str = None
    ):
        """
        Plot confusion matrix.

        Args:
            labels_true: True labels
            labels_pred: Predicted labels
            save_path: Save path (default: figures/confusion_matrix.png)
        """
        if save_path is None:
            save_path = self.figures_dir / "confusion_matrix.png"

        # Compute confusion matrix
        cm = confusion_matrix(labels_true, labels_pred)
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

        # Create figure
        fig, ax = plt.subplots(figsize=self.viz_config.figsize_matrix)

        # Heatmap
        sns.heatmap(
            cm_normalized,
            annot=True,
            fmt='.2%',
            cmap='Blues',
            cbar=True,
            square=True,
            ax=ax
        )

        # Add counts
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j + 0.5, i + 0.7, f'n={cm[i, j]}',
                       ha='center', va='center', fontsize=9, color='gray')

        ax.set_xlabel('Predicted Cluster', fontsize=12, weight='bold')
        ax.set_ylabel('True Lifecycle Label', fontsize=12, weight='bold')
        ax.set_title('Confusion Matrix', fontsize=14, weight='bold')
        ax.set_xticklabels(['Cluster 0', 'Cluster 1'])
        ax.set_yticklabels(['General Info', 'Responsible AI'])

        plt.tight_layout()
        plt.savefig(save_path, dpi=self.viz_config.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved confusion matrix plot: {save_path}")

    def plot_repository_stratification(
        self,
        repository_nmis: Dict[str, float],
        save_path: str = None
    ):
        """
        Plot NMI by repository.

        Args:
            repository_nmis: Dict mapping repository to NMI
            save_path: Save path (default: figures/repository_stratification.png)
        """
        if save_path is None:
            save_path = self.figures_dir / "repository_stratification.png"

        if not repository_nmis:
            print("Warning: No repository NMI data to plot")
            return

        # Prepare data
        repos = list(repository_nmis.keys())
        nmis = list(repository_nmis.values())

        # Create figure
        fig, ax = plt.subplots(figsize=self.viz_config.figsize_bar)

        # Bar chart
        bars = ax.bar(repos, nmis, color='steelblue', alpha=0.8, edgecolor='black')

        # Labels
        ax.set_xlabel('Repository', fontsize=12, weight='bold')
        ax.set_ylabel('NMI', fontsize=12, weight='bold')
        ax.set_title('Repository Stratification: NMI by Repository', fontsize=14, weight='bold')
        ax.set_ylim(0, 1.0)

        # Value labels
        for bar, nmi in zip(bars, nmis):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 0.02,
                   f'{nmi:.3f}', ha='center', va='bottom', fontsize=10, weight='bold')

        plt.tight_layout()
        plt.savefig(save_path, dpi=self.viz_config.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved repository stratification plot: {save_path}")

    def plot_scaffolding_effect(
        self,
        scaffolding_results: Dict[str, float],
        save_path: str = None
    ):
        """
        Plot scaffolding effect comparison.

        Args:
            scaffolding_results: Dict with 'scaffolded', 'unscaffolded', 'gap'
            save_path: Save path (default: figures/scaffolding_effect.png)
        """
        if save_path is None:
            save_path = self.figures_dir / "scaffolding_effect.png"

        # Prepare data
        categories = ['Scaffolded', 'Unscaffolded']
        nmis = [
            scaffolding_results.get('scaffolded', 0.0),
            scaffolding_results.get('unscaffolded', 0.0)
        ]
        gap = scaffolding_results.get('gap', 0.0)

        # Create figure
        fig, ax = plt.subplots(figsize=self.viz_config.figsize_bar)

        # Bar chart
        bars = ax.bar(categories, nmis, color=['#3498db', '#e74c3c'], alpha=0.8, edgecolor='black')

        # Gap annotation
        if len(nmis) == 2:
            ax.annotate('', xy=(0, nmis[0]), xytext=(1, nmis[1]),
                       arrowprops=dict(arrowstyle='<->', color='green', lw=2))
            ax.text(0.5, max(nmis) + 0.05,
                   f'Gap: {gap:.3f}',
                   ha='center', fontsize=11, color='green', weight='bold')

        # Labels
        ax.set_ylabel('NMI', fontsize=12, weight='bold')
        ax.set_title('Scaffolding Effect: Interface Amplification', fontsize=14, weight='bold')
        ax.set_ylim(0, 1.0)

        # Value labels
        for bar, nmi in zip(bars, nmis):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 0.02,
                   f'{nmi:.3f}', ha='center', va='bottom', fontsize=10, weight='bold')

        plt.tight_layout()
        plt.savefig(save_path, dpi=self.viz_config.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved scaffolding effect plot: {save_path}")
