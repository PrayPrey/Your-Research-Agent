"""Generate coverage visualizations."""

from typing import List, Dict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from ..data_structures import Mapping


class Visualizer:
    """Generate coverage visualizations."""

    def __init__(self, output_dir: str = "figures", dpi: int = 300):
        self.output_dir = output_dir
        self.dpi = dpi
        plt.style.use('seaborn-v0_8-darkgrid')

    def plot_verifier_coverage_bars(
        self,
        per_verifier_coverage: Dict[str, float],
        threshold: float,
        output_path: str
    ) -> None:
        """Bar chart with threshold line."""
        fig, ax = plt.subplots(figsize=(10, 6))

        verifiers = list(per_verifier_coverage.keys())
        coverages = list(per_verifier_coverage.values())

        bars = ax.bar(verifiers, coverages, color=['#2ecc71', '#3498db', '#e74c3c'])
        ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({threshold}%)')

        ax.set_xlabel('Verifier', fontsize=12, fontweight='bold')
        ax.set_ylabel('Coverage (%)', fontsize=12, fontweight='bold')
        ax.set_title('Per-Verifier Taxonomy Coverage', fontsize=14, fontweight='bold')
        ax.legend()
        ax.set_ylim(0, 105)

        # Add value labels on bars
        for bar, coverage in zip(bars, coverages):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{coverage:.1f}%',
                   ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def plot_primitive_frequencies(
        self,
        frequencies: Dict[str, int],
        output_path: str
    ) -> None:
        """Bar chart of error counts per primitive."""
        fig, ax = plt.subplots(figsize=(12, 6))

        primitives = list(frequencies.keys())
        counts = list(frequencies.values())

        # Sort by count
        sorted_pairs = sorted(zip(primitives, counts), key=lambda x: x[1], reverse=True)
        primitives, counts = zip(*sorted_pairs) if sorted_pairs else ([], [])

        bars = ax.barh(primitives, counts, color='#3498db')

        ax.set_xlabel('Number of Mapped Categories', fontsize=12, fontweight='bold')
        ax.set_ylabel('Semantic Primitive', fontsize=12, fontweight='bold')
        ax.set_title('Primitive Frequency Distribution', fontsize=14, fontweight='bold')

        # Add value labels
        for bar, count in zip(bars, counts):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f' {count}',
                   ha='left', va='center', fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def plot_mapping_heatmap(
        self,
        mappings: List[Mapping],
        output_path: str
    ) -> None:
        """Heatmap: verifier × primitive."""
        # Build matrix
        verifiers = sorted(set(m.verifier for m in mappings))
        primitives = sorted(set(m.semantic_primitive for m in mappings if m.semantic_primitive))

        # Create DataFrame
        matrix = pd.DataFrame(0, index=verifiers, columns=primitives)

        for mapping in mappings:
            if mapping.semantic_primitive:
                matrix.loc[mapping.verifier, mapping.semantic_primitive] += 1

        # Plot
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(matrix, annot=True, fmt='d', cmap='YlOrRd', ax=ax,
                   cbar_kws={'label': 'Number of Mappings'})

        ax.set_xlabel('Semantic Primitive', fontsize=12, fontweight='bold')
        ax.set_ylabel('Verifier', fontsize=12, fontweight='bold')
        ax.set_title('Category-to-Primitive Mapping Heatmap', fontsize=14, fontweight='bold')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def plot_gate_comparison(
        self,
        aggregate_coverage: float,
        per_verifier_coverage: Dict[str, float],
        threshold: float,
        output_path: str
    ) -> None:
        """Side-by-side comparison of aggregate vs per-verifier coverage."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Aggregate coverage gauge
        ax1.bar(['Aggregate'], [aggregate_coverage], color='#3498db', width=0.5)
        ax1.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({threshold}%)')
        ax1.set_ylabel('Coverage (%)', fontsize=12, fontweight='bold')
        ax1.set_title('Aggregate Coverage', fontsize=14, fontweight='bold')
        ax1.set_ylim(0, 105)
        ax1.legend()
        ax1.text(0, aggregate_coverage, f'{aggregate_coverage:.1f}%',
                ha='center', va='bottom', fontweight='bold')

        # Per-verifier breakdown
        verifiers = list(per_verifier_coverage.keys())
        coverages = list(per_verifier_coverage.values())
        colors = ['#2ecc71' if c >= threshold else '#e74c3c' for c in coverages]

        ax2.bar(verifiers, coverages, color=colors)
        ax2.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({threshold}%)')
        ax2.set_ylabel('Coverage (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Per-Verifier Coverage', fontsize=14, fontweight='bold')
        ax2.set_ylim(0, 105)
        ax2.legend()

        for i, (verifier, coverage) in enumerate(zip(verifiers, coverages)):
            ax2.text(i, coverage, f'{coverage:.1f}%',
                    ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
