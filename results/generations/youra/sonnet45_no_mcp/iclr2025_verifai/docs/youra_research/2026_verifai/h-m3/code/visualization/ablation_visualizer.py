"""Ablation Visualizer for h-m3.

Generates comparison plots for ablation study.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict
from pathlib import Path


class AblationVisualizer:
    """Visualizer for ablation study results."""

    def __init__(self, output_dir: str = "./figures"):
        """Initialize visualizer.

        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def plot_ablation_comparison_bar(self, results: Dict[str, Dict[str, float]],
                                     filename: str = "ablation_comparison.png"):
        """Plot F1 comparison of all models (MANDATORY).

        Args:
            results: Results dictionary from AblationFramework
            filename: Output filename
        """
        model_names = list(results.keys())
        f1_scores = [results[m]['f1'] for m in model_names]

        fig, ax = plt.subplots(figsize=(10, 6))

        # Create bars
        bars = ax.bar(range(len(model_names)), f1_scores, color='skyblue')

        # Highlight hybrid model
        if 'hybrid_all' in model_names:
            hybrid_idx = model_names.index('hybrid_all')
            bars[hybrid_idx].set_color('orange')

        ax.set_xlabel('Model')
        ax.set_ylabel('F1 Score')
        ax.set_title('Ablation Study: F1 Comparison')
        ax.set_xticks(range(len(model_names)))
        ax.set_xticklabels(model_names, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✓ Saved: {output_path}")
        return str(output_path)
