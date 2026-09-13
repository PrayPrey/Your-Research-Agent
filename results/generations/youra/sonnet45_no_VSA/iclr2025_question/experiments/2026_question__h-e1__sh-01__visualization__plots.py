"""Visualization for CCP experiment results."""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict
import os


class Visualizer:
    """Create visualizations for validation report."""

    def __init__(self, figures_dir: str):
        self.figures_dir = figures_dir
        os.makedirs(figures_dir, exist_ok=True)

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 300

    def plot_gate_metrics(
        self,
        metrics: Dict,
        targets: Dict,
        save_path: str = None
    ):
        """Plot gate metrics comparison (target vs actual).

        Args:
            metrics: Dict with actual metric values
            targets: Dict with target threshold values
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        metric_names = ["Δρ_j", "R²", "p-value"]
        actual_values = [
            metrics.get("delta_rho_j", 0),
            metrics.get("r_squared", 0),
            metrics.get("p_value", 1)
        ]
        target_values = [
            targets.get("delta_rho_j", 0.15),
            targets.get("r_squared", 0.6),
            targets.get("p_value", 0.05)
        ]

        # Determine pass/fail
        # Δρ_j and R² should exceed targets, p-value should be below target
        passes = [
            actual_values[0] > target_values[0],  # Δρ_j > 0.15
            actual_values[1] > target_values[1],  # R² > 0.6
            actual_values[2] < target_values[2]   # p-value < 0.05
        ]

        x = np.arange(len(metric_names))
        width = 0.35

        # Plot bars
        bars1 = ax.bar(x - width/2, target_values, width, label='Target', color='gray', alpha=0.6)
        colors = ['green' if p else 'red' for p in passes]
        bars2 = ax.bar(x + width/2, actual_values, width, label='Actual', color=colors, alpha=0.8)

        # Labels and title
        ax.set_xlabel('Metrics', fontsize=12)
        ax.set_ylabel('Values', fontsize=12)
        ax.set_title('Gate Metrics Comparison: Target vs Actual', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(metric_names)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        if save_path is None:
            save_path = os.path.join(self.figures_dir, "gate_metrics.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved gate metrics plot to {save_path}")

    def plot_rho_distribution(
        self,
        factual_rho: List[float],
        creative_rho: List[float],
        save_path: str = None
    ):
        """Plot ρ_j distributions by domain.

        Args:
            factual_rho: ρ_j values for factual domain
            creative_rho: ρ_j values for creative domain
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        data = [factual_rho, creative_rho]
        labels = ['Factual', 'Creative']

        bp = ax.boxplot(data, labels=labels, patch_artist=True,
                        boxprops=dict(facecolor='lightblue', alpha=0.7),
                        medianprops=dict(color='red', linewidth=2),
                        whiskerprops=dict(linewidth=1.5),
                        capprops=dict(linewidth=1.5))

        ax.set_ylabel('ρ_j (Claim-Type Mass Ratio)', fontsize=12)
        ax.set_title('ρ_j Distribution by Domain', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        # Add median values as text
        medians = [np.median(d) for d in data]
        for i, (label, median) in enumerate(zip(labels, medians)):
            ax.text(i + 1, median, f'Med: {median:.3f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        plt.tight_layout()

        if save_path is None:
            save_path = os.path.join(self.figures_dir, "rho_distribution.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved ρ_j distribution plot to {save_path}")

    def plot_correlation(
        self,
        rho_j: List[float],
        roc_auc: List[float],
        r_squared: float,
        save_path: str = None
    ):
        """Plot correlation between ρ_j and ROC-AUC.

        Args:
            rho_j: ρ_j values
            roc_auc: ROC-AUC values
            r_squared: R² coefficient
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Scatter plot
        ax.scatter(rho_j, roc_auc, alpha=0.6, s=50, color='blue')

        # Regression line
        if len(rho_j) > 1:
            z = np.polyfit(rho_j, roc_auc, 1)
            p = np.poly1d(z)
            x_line = np.linspace(min(rho_j), max(rho_j), 100)
            ax.plot(x_line, p(x_line), "r--", linewidth=2, label=f'Linear fit (R²={r_squared:.3f})')

        ax.set_xlabel('ρ_j (Claim-Type Mass Ratio)', fontsize=12)
        ax.set_ylabel('ROC-AUC', fontsize=12)
        ax.set_title('Correlation: ρ_j vs ROC-AUC', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()

        if save_path is None:
            save_path = os.path.join(self.figures_dir, "correlation.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved correlation plot to {save_path}")

    def plot_degradation(
        self,
        delta_rho: float,
        delta_auc: float,
        save_path: str = None
    ):
        """Plot domain degradation metrics.

        Args:
            delta_rho: Δρ_j (factual - creative)
            delta_auc: ΔROC-AUC (factual - creative)
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        metrics = ['Δρ_j', 'ΔROC-AUC']
        values = [delta_rho, delta_auc]
        colors = ['steelblue', 'coral']

        bars = ax.bar(metrics, values, color=colors, alpha=0.7, width=0.6)

        ax.set_ylabel('Degradation (Factual - Creative)', fontsize=12)
        ax.set_title('Domain Degradation Metrics', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.3f}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')

        plt.tight_layout()

        if save_path is None:
            save_path = os.path.join(self.figures_dir, "degradation.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved degradation plot to {save_path}")

    def plot_category_heatmap(
        self,
        categories: List[str],
        rho_values: List[float],
        save_path: str = None
    ):
        """Plot heatmap of ρ_j across categories.

        Args:
            categories: Category names
            rho_values: ρ_j values per category
            save_path: Path to save figure
        """
        if not categories or not rho_values:
            print("Skipping category heatmap (no data)")
            return

        fig, ax = plt.subplots(figsize=(12, 8))

        # Create category-value mapping
        category_map = {}
        for cat, rho in zip(categories, rho_values):
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append(rho)

        # Average per category
        sorted_categories = sorted(category_map.keys())
        avg_rho = [np.mean(category_map[cat]) for cat in sorted_categories]

        # Create heatmap data
        data = np.array(avg_rho).reshape((-1, 1))

        sns.heatmap(data, annot=True, fmt='.3f', cmap='coolwarm',
                   yticklabels=sorted_categories, xticklabels=['ρ_j'],
                   cbar_kws={'label': 'ρ_j value'}, ax=ax)

        ax.set_title('ρ_j Heatmap by TruthfulQA Category', fontsize=14, fontweight='bold')

        plt.tight_layout()

        if save_path is None:
            save_path = os.path.join(self.figures_dir, "category_heatmap.png")
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved category heatmap to {save_path}")
