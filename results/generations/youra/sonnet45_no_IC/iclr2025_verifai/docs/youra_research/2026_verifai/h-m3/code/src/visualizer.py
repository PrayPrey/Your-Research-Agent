"""Generate validation figures."""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import torch
from pathlib import Path
from typing import Dict, List

class Visualizer:
    """Generate validation figures."""

    def __init__(self, output_dir: Path, dpi: int = 300):
        """Initialize visualizer."""
        self.output_dir = Path(output_dir)
        self.dpi = dpi
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def plot_gate_metrics(self, metrics: Dict, gate_status: Dict) -> None:
        """Bar chart with threshold lines."""
        fig, ax = plt.subplots(figsize=(10, 6))

        metric_names = ['Recall', 'FP Rate']
        actual_values = [metrics['recall'], metrics['fp_rate']]

        x = np.arange(len(metric_names))
        ax.bar(x, actual_values, color=['#2196F3', '#FF5722'], alpha=0.7)

        ax.axhline(y=0.70, color='green', linestyle='--', label='Target (≥0.70)')
        ax.axhline(y=0.60, color='orange', linestyle='--', label='Acceptable (≥0.60)')
        ax.axhline(y=0.30, color='red', linestyle='--', label='FP Limit (<0.30)')

        ax.set_ylabel('Value')
        ax.set_title(f'Gate Metrics (Status: {gate_status["status"]})')
        ax.set_xticks(x)
        ax.set_xticklabels(metric_names)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'fig1_gate_metrics.png', dpi=self.dpi)
        plt.close()

    def plot_similarity_distribution(
        self,
        similarity_matrix: torch.Tensor,
        threshold: float
    ) -> None:
        """Histogram with threshold line."""
        fig, ax = plt.subplots(figsize=(10, 6))

        similarities = similarity_matrix.cpu().numpy().flatten()

        ax.hist(similarities, bins=50, color='gray', alpha=0.7, edgecolor='black')
        ax.axvline(x=threshold, color='red', linestyle='--', linewidth=2,
                   label=f'Threshold (<{threshold} = contradiction)')

        ax.set_xlabel('Cosine Similarity')
        ax.set_ylabel('Frequency')
        ax.set_title('Similarity Distribution')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'fig2_similarity_distribution.png', dpi=self.dpi)
        plt.close()

    def plot_confusion_matrix(self, confusion: Dict) -> None:
        """Heatmap of TP/FP/FN/TN."""
        fig, ax = plt.subplots(figsize=(8, 6))

        matrix = np.array([
            [confusion['TP'], confusion['FP']],
            [confusion['FN'], confusion['TN']]
        ])

        sns.heatmap(matrix, annot=True, fmt='d', cmap='YlGnBu', ax=ax,
                    xticklabels=['Flagged', 'Not Flagged'],
                    yticklabels=['Actual Mismatch', 'No Mismatch'])

        ax.set_title('Confusion Matrix')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'fig3_confusion_matrix.png', dpi=self.dpi)
        plt.close()

    def plot_threshold_tuning_curve(self, tuning_results: List[Dict]) -> None:
        """Recall/FP rate vs threshold."""
        fig, ax = plt.subplots(figsize=(10, 6))

        thresholds = [r['threshold'] for r in tuning_results]
        recalls = [r['recall'] for r in tuning_results]
        fp_rates = [r['fp_rate'] for r in tuning_results]

        ax.plot(thresholds, recalls, 'o-', label='Recall', color='#2196F3', linewidth=2)
        ax.plot(thresholds, fp_rates, 's--', label='FP Rate', color='#FF5722', linewidth=2)

        ax.axhline(y=0.30, color='red', linestyle=':', label='FP Limit (0.30)')
        ax.axhline(y=0.70, color='green', linestyle=':', label='Recall Target (0.70)')

        ax.set_xlabel('Threshold')
        ax.set_ylabel('Rate')
        ax.set_title('Threshold Tuning Curve')
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'fig4_threshold_tuning.png', dpi=self.dpi)
        plt.close()

    def plot_per_case_detection(self, detected_contradictions: List[Dict]) -> None:
        """Per-case similarity scores."""
        fig, ax = plt.subplots(figsize=(10, 6))

        if detected_contradictions:
            similarities = [d['similarity'] for d in detected_contradictions[:20]]
            cases = [f"Case {i+1}" for i in range(len(similarities))]

            ax.barh(cases, similarities, color='#FF5722', alpha=0.7)
            ax.axvline(x=0.3, color='red', linestyle='--', label='Threshold (0.3)')

            ax.set_xlabel('Similarity Score')
            ax.set_ylabel('Case')
            ax.set_title('Per-Case Detection Results')
            ax.legend()
            ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'fig5_per_case_detection.png', dpi=self.dpi)
        plt.close()

    def generate_all_figures(self, results: Dict) -> None:
        """Generate all 5 figures."""
        self.plot_gate_metrics(results['metrics'], results['gate_status'])
        self.plot_similarity_distribution(
            torch.tensor(results['similarity_matrix']),
            results.get('threshold', 0.3)
        )
        self.plot_confusion_matrix(results['confusion_matrix'])

        if results.get('tuning_results'):
            self.plot_threshold_tuning_curve(results['tuning_results'])

        self.plot_per_case_detection(results['contradictions'])
