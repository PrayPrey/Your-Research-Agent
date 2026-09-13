"""
Visualization Generation for Clustering Results
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict
from scipy.cluster.hierarchy import dendrogram, linkage


class ResultVisualizer:
    """Generate 6 publication-quality figures."""

    def __init__(self, output_dir: str, colors: dict, dpi: int = 300, figsize: tuple = (10, 8)):
        """Initialize with output directory and style config."""
        self.output_dir = output_dir
        self.colors = colors
        self.dpi = dpi
        self.figsize = figsize

        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("colorblind")

    def plot_3d_scatter(
        self,
        X_pca: np.ndarray,
        labels: np.ndarray,
        alignment_types: List[str],
        model_names: List[str]
    ) -> None:
        """3D scatter plot of PCA space. Saves to 3d_scatter.png"""
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection='3d')

        # Plot each model
        for i, (point, atype, mname) in enumerate(zip(X_pca, alignment_types, model_names)):
            color = self.colors.get(atype, "#000000")
            ax.scatter(point[0], point[1], point[2], c=color, s=100, alpha=0.7, edgecolors='black')
            ax.text(point[0], point[1], point[2], mname.split('/')[-1][:10], fontsize=6)

        ax.set_xlabel('PC1')
        ax.set_ylabel('PC2')
        ax.set_zlabel('PC3')
        ax.set_title('3D Performance Space Clustering by Alignment Method')

        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.colors["execution"], label="Execution"),
            Patch(facecolor=self.colors["preference"], label="Preference"),
            Patch(facecolor=self.colors["baseline"], label="Baseline")
        ]
        ax.legend(handles=legend_elements, loc='upper right')

        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/3d_scatter.png", dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved: {self.output_dir}/3d_scatter.png")

    def plot_heatmap(
        self,
        signatures: List[Dict[str, float]],
        model_names: List[str]
    ) -> None:
        """Model × Dimension heatmap. Saves to heatmap.png"""
        # Prepare data
        metrics = ["correctness", "cyclomatic", "ast_depth", "runtime_ms", "memory_kb"]
        data = []
        for sig in signatures:
            data.append([sig[m] for m in metrics])

        df = pd.DataFrame(data, columns=metrics, index=[m.split('/')[-1][:15] for m in model_names])

        # Normalize columns for better visualization
        df_norm = (df - df.min()) / (df.max() - df.min())

        # Plot
        fig, ax = plt.subplots(figsize=self.figsize)
        sns.heatmap(df_norm, annot=True, fmt='.2f', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Normalized Score'})
        ax.set_title('Model Performance Heatmap (Normalized)')
        ax.set_xlabel('Metrics')
        ax.set_ylabel('Models')

        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/heatmap.png", dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved: {self.output_dir}/heatmap.png")

    def plot_boxplots(
        self,
        signatures: List[Dict[str, float]],
        alignment_types: List[str]
    ) -> None:
        """Metric distributions by alignment. Saves to boxplots.png"""
        metrics = ["correctness", "cyclomatic", "ast_depth"]

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        for i, metric in enumerate(metrics):
            data_by_type = {
                "Execution": [],
                "Preference": [],
                "Baseline": []
            }

            for sig, atype in zip(signatures, alignment_types):
                key = atype.capitalize()
                if key in data_by_type:
                    data_by_type[key].append(sig[metric])

            # Box plot
            positions = [1, 2, 3]
            bp = axes[i].boxplot(
                [data_by_type["Execution"], data_by_type["Preference"], data_by_type["Baseline"]],
                positions=positions,
                patch_artist=True,
                labels=["Execution", "Preference", "Baseline"]
            )

            # Color boxes
            for patch, atype in zip(bp['boxes'], ["execution", "preference", "baseline"]):
                patch.set_facecolor(self.colors[atype])

            axes[i].set_title(f'{metric.replace("_", " ").title()}')
            axes[i].set_ylabel('Value')
            axes[i].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/boxplots.png", dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved: {self.output_dir}/boxplots.png")

    def plot_dendrogram(
        self,
        X: np.ndarray,
        model_names: List[str]
    ) -> None:
        """Hierarchical clustering dendrogram. Saves to dendrogram.png"""
        fig, ax = plt.subplots(figsize=self.figsize)

        # Compute linkage
        Z = linkage(X, method='ward')

        # Plot dendrogram
        dendrogram(
            Z,
            labels=[m.split('/')[-1][:15] for m in model_names],
            ax=ax,
            orientation='right'
        )

        ax.set_title('Hierarchical Clustering Dendrogram')
        ax.set_xlabel('Distance')
        ax.set_ylabel('Models')

        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/dendrogram.png", dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved: {self.output_dir}/dendrogram.png")

    def plot_effect_size(
        self,
        cohens_d: float,
        threshold: float
    ) -> None:
        """Cohen's d effect size. Saves to effect_size.png"""
        fig, ax = plt.subplots(figsize=(8, 6))

        categories = ['Threshold', 'Actual']
        values = [threshold, cohens_d]
        colors_bars = ['#cccccc', '#0173B2' if cohens_d > threshold else '#cc0000']

        bars = ax.bar(categories, values, color=colors_bars, edgecolor='black', linewidth=1.5)

        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.2f}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')

        ax.set_ylabel("Cohen's d", fontsize=12)
        ax.set_title("Effect Size: Intercluster Distance", fontsize=14, fontweight='bold')
        ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({threshold})')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/effect_size.png", dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved: {self.output_dir}/effect_size.png")

    def plot_gate_metrics(
        self,
        target: float,
        actual: float
    ) -> None:
        """Gate comparison bar chart. Saves to gate_metrics.png"""
        fig, ax = plt.subplots(figsize=(8, 6))

        categories = ['Target (Threshold)', 'Actual (Cohen\'s d)']
        values = [target, actual]

        # Color: green if passed, red if failed
        passed = actual > target
        colors_bars = ['#029E73', '#0173B2' if passed else '#DE8F05']

        bars = ax.bar(categories, values, color=colors_bars, edgecolor='black', linewidth=1.5)

        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.3f}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')

        ax.set_ylabel("Cohen's d Value", fontsize=12)
        ax.set_title(f"MUST_WORK Gate: {'PASS' if passed else 'FAIL'}",
                     fontsize=14, fontweight='bold',
                     color='green' if passed else 'red')
        ax.axhline(y=target, color='red', linestyle='--', linewidth=2, label=f'Gate Threshold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/gate_metrics.png", dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved: {self.output_dir}/gate_metrics.png")
