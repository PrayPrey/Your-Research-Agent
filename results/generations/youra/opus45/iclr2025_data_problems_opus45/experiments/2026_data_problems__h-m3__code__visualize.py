"""
Visualization for H-M3: Method disagreement analysis figures.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage
from typing import Dict, List, Set, Any
import os

from config import H3Config


class Visualizer:
    """Generates figures for H-M3 method disagreement analysis."""

    def __init__(self, cfg: H3Config):
        self.cfg = cfg
        plt.style.use('seaborn-v0_8-whitegrid')

    def plot_jaccard_heatmap(
        self,
        jaccard_matrix: np.ndarray,
        method_names: List[str],
        budget: int,
        save_path: str,
        min_jaccard: float = None,
    ) -> None:
        """
        Gate figure: pairwise Jaccard heatmap with 0.70 threshold annotation.
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        mask = np.zeros_like(jaccard_matrix, dtype=bool)
        np.fill_diagonal(mask, True)

        sns.heatmap(
            jaccard_matrix,
            annot=True,
            fmt='.3f',
            cmap='RdYlGn',
            vmin=0,
            vmax=1,
            xticklabels=method_names,
            yticklabels=method_names,
            ax=ax,
            mask=mask,
            cbar_kws={'label': 'Jaccard Similarity'},
        )

        ax.set_title(f'Top-k Jaccard Similarity (Budget={budget})\nGate: min < 0.70')

        # Add gate annotation
        if min_jaccard is not None:
            gate_pass = min_jaccard < self.cfg.jaccard_threshold
            status = 'PASS' if gate_pass else 'FAIL'
            color = 'green' if gate_pass else 'red'
            ax.text(
                0.02, 0.98,
                f'min(Jaccard) = {min_jaccard:.3f} [{status}]',
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment='top',
                color=color,
                fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            )

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

    def plot_jaccard_by_budget(
        self,
        jaccard_by_budget: Dict[int, Dict],
        budgets: List[int],
        save_path: str,
    ) -> None:
        """Line plot: min/mean Jaccard vs budget with 0.70 threshold."""
        fig, ax = plt.subplots(figsize=(10, 6))

        sorted_budgets = sorted(budgets)
        min_values = [jaccard_by_budget[b]['min'] for b in sorted_budgets]
        mean_values = [jaccard_by_budget[b]['mean'] for b in sorted_budgets]

        ax.plot(sorted_budgets, min_values, 'o-', label='Min Jaccard', linewidth=2, markersize=8)
        ax.plot(sorted_budgets, mean_values, 's--', label='Mean Jaccard', linewidth=2, markersize=8)
        ax.axhline(y=self.cfg.jaccard_threshold, color='red', linestyle=':', linewidth=2, label=f'Threshold ({self.cfg.jaccard_threshold})')

        ax.fill_between(sorted_budgets, 0, self.cfg.jaccard_threshold, alpha=0.1, color='green', label='Gate Pass Region')

        ax.set_xlabel('Compute Budget', fontsize=12)
        ax.set_ylabel('Jaccard Similarity', fontsize=12)
        ax.set_title('Method Disagreement vs Compute Budget', fontsize=14)
        ax.legend(loc='best')
        ax.set_ylim(0, 1)
        ax.set_xticks(sorted_budgets)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

    def plot_topk_overlap(
        self,
        topk_sets: Dict[str, List[Set[int]]],
        test_sample_indices: List[int],
        save_path: str,
    ) -> None:
        """Bar chart showing overlap counts between methods for representative test samples."""
        methods = list(topk_sets.keys())
        n_methods = len(methods)

        fig, axes = plt.subplots(1, len(test_sample_indices), figsize=(5 * len(test_sample_indices), 5))
        if len(test_sample_indices) == 1:
            axes = [axes]

        for ax, test_idx in zip(axes, test_sample_indices):
            # Compute pairwise overlaps for this test sample
            overlaps = np.zeros((n_methods, n_methods))
            for i, m1 in enumerate(methods):
                for j, m2 in enumerate(methods):
                    set1 = topk_sets[m1][test_idx]
                    set2 = topk_sets[m2][test_idx]
                    overlaps[i, j] = len(set1 & set2)

            sns.heatmap(
                overlaps,
                annot=True,
                fmt='.0f',
                cmap='Blues',
                xticklabels=methods,
                yticklabels=methods,
                ax=ax,
            )
            ax.set_title(f'Top-k Overlap (Test #{test_idx})')

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

    def plot_method_ranking_persistence(
        self,
        advantages: Dict[int, Dict[str, str]],
        budgets: List[int],
        methods: List[str],
        save_path: str,
    ) -> None:
        """Stacked bar showing which method has lowest average Jaccard per budget."""
        sorted_budgets = sorted(budgets)

        # Count wins per method
        method_counts = {m: [] for m in methods}
        for budget in sorted_budgets:
            winner = advantages[budget]['lowest_avg_jaccard_method']
            for m in methods:
                method_counts[m].append(1 if m == winner else 0)

        fig, ax = plt.subplots(figsize=(10, 6))

        x = np.arange(len(sorted_budgets))
        width = 0.6
        colors = plt.cm.Set2(np.linspace(0, 1, len(methods)))

        bottom = np.zeros(len(sorted_budgets))
        for i, method in enumerate(methods):
            values = method_counts[method]
            ax.bar(x, values, width, label=method, bottom=bottom, color=colors[i])
            bottom += values

        ax.set_xlabel('Compute Budget', fontsize=12)
        ax.set_ylabel('Method with Lowest Avg Jaccard', fontsize=12)
        ax.set_title('Method Disagreement Leadership by Budget', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(sorted_budgets)
        ax.legend(loc='upper right')
        ax.set_ylim(0, 1.5)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

    def plot_paradigm_clustering(
        self,
        jaccard_matrix: np.ndarray,
        method_names: List[str],
        save_path: str,
    ) -> None:
        """Dendrogram based on Jaccard distance (1 - Jaccard)."""
        # Convert Jaccard similarity to distance
        distance_matrix = 1 - jaccard_matrix

        # Use condensed distance matrix (upper triangle)
        n = len(method_names)
        condensed = []
        for i in range(n):
            for j in range(i + 1, n):
                condensed.append(distance_matrix[i, j])

        fig, ax = plt.subplots(figsize=(8, 6))

        linkage_matrix = linkage(condensed, method='average')
        dendrogram(
            linkage_matrix,
            labels=method_names,
            ax=ax,
            leaf_rotation=0,
            leaf_font_size=12,
        )

        ax.set_title('Method Clustering by Top-k Disagreement\n(Distance = 1 - Jaccard)', fontsize=14)
        ax.set_xlabel('Method', fontsize=12)
        ax.set_ylabel('Distance (1 - Jaccard)', fontsize=12)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

    def plot_gate_summary(
        self,
        jaccard_by_budget: Dict[int, Dict],
        budgets: List[int],
        gate_result: Dict[str, Any],
        save_path: str,
    ) -> None:
        """Summary figure showing gate result prominently."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Left: Jaccard by budget
        sorted_budgets = sorted(budgets)
        min_values = [jaccard_by_budget[b]['min'] for b in sorted_budgets]

        colors = ['green' if v < self.cfg.jaccard_threshold else 'red' for v in min_values]
        ax1.bar(range(len(sorted_budgets)), min_values, color=colors, alpha=0.7)
        ax1.axhline(y=self.cfg.jaccard_threshold, color='red', linestyle='--', linewidth=2)
        ax1.set_xticks(range(len(sorted_budgets)))
        ax1.set_xticklabels(sorted_budgets)
        ax1.set_xlabel('Compute Budget')
        ax1.set_ylabel('Min Pairwise Jaccard')
        ax1.set_title('Gate Check: min(Jaccard) < 0.70')
        ax1.set_ylim(0, 1)

        # Right: Gate summary text
        ax2.axis('off')
        gate_pass = gate_result['gate_pass']
        status_color = 'green' if gate_pass else 'red'
        status_text = 'PASS' if gate_pass else 'FAIL'

        summary_text = f"""
        GATE RESULT: {status_text}

        Minimum Jaccard: {gate_result['min_jaccard']:.4f}
        Threshold: {self.cfg.jaccard_threshold}
        Best Budget: {gate_result['min_budget']}

        Condition: min(Jaccard) < {self.cfg.jaccard_threshold}
        Interpretation: {'>30%' if gate_pass else '<30%'} disagreement
        on influential examples between methods
        """

        ax2.text(
            0.1, 0.5,
            summary_text,
            transform=ax2.transAxes,
            fontsize=14,
            verticalalignment='center',
            fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor=status_color, alpha=0.2),
        )

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
