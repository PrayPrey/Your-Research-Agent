"""Visualization for boundary detection results."""

import os
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np


class Visualizer:
    """Generate figures for h-c1 results."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_gate_comparison(self, baseline_metrics: Dict, proposed_metrics: Dict, threshold: float) -> str:
        """Gate metrics bar chart (mandatory figure)."""
        fig, ax = plt.subplots(figsize=(10, 6))

        metrics = ['accuracy', 'precision', 'recall']
        x = np.arange(len(metrics))
        width = 0.35

        baseline_vals = [baseline_metrics.get(m, 0.0) for m in metrics]
        proposed_vals = [proposed_metrics.get(m, 0.0) for m in metrics]

        ax.bar(x - width/2, baseline_vals, width, label='Baseline (No Boundary Check)', alpha=0.8)
        ax.bar(x + width/2, proposed_vals, width, label='Proposed (With Boundary Check)', alpha=0.8)

        # Gate threshold line
        ax.axhline(y=threshold, color='r', linestyle='--', label=f'Gate Threshold ({threshold})')

        ax.set_xlabel('Metric')
        ax.set_ylabel('Score')
        ax.set_title('h-c1: Domain Boundary Detection - Gate Metrics Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels([m.capitalize() for m in metrics])
        ax.legend()
        ax.set_ylim([0, 1.0])
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        save_path = os.path.join(self.output_dir, 'gate_metrics_comparison.png')
        plt.savefig(save_path, dpi=300)
        plt.close()

        return save_path

    def plot_confusion_matrix(self, y_true: List[bool], y_pred: List[bool]) -> str:
        """Confusion matrix for boundary classification."""
        # Convert to boundary labels: False = boundary, True = in-scope
        true_boundary = [not t for t in y_true]
        pred_boundary = [not p for p in y_pred]

        # Compute confusion matrix
        tp = sum(1 for t, p in zip(true_boundary, pred_boundary) if t and p)
        tn = sum(1 for t, p in zip(true_boundary, pred_boundary) if not t and not p)
        fp = sum(1 for t, p in zip(true_boundary, pred_boundary) if not t and p)
        fn = sum(1 for t, p in zip(true_boundary, pred_boundary) if t and not p)

        cm = np.array([[tn, fp], [fn, tp]])

        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(cm, cmap='Blues')

        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['In-Scope', 'Boundary'])
        ax.set_yticklabels(['In-Scope', 'Boundary'])

        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        ax.set_title('h-c1: Confusion Matrix - Boundary Detection')

        # Add text annotations
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(cm[i, j]), ha='center', va='center', color='white' if cm[i, j] > cm.max()/2 else 'black', fontsize=20)

        plt.colorbar(im)
        plt.tight_layout()
        save_path = os.path.join(self.output_dir, 'confusion_matrix.png')
        plt.savefig(save_path, dpi=300)
        plt.close()

        return save_path

    def plot_domain_coverage_heatmap(self, test_cases: List[Dict], kb_domains: List[Dict], similarity_scores: Dict) -> str:
        """Test cases × KB domains similarity heatmap."""
        n_cases = len(test_cases)
        n_domains = len(kb_domains)

        # Build similarity matrix
        sim_matrix = np.zeros((n_cases, n_domains))
        for i, case in enumerate(test_cases):
            case_id = case['id']
            for j, domain in enumerate(kb_domains):
                domain_name = domain['name']
                sim_matrix[i, j] = similarity_scores.get((case_id, domain_name), 0.0)

        fig, ax = plt.subplots(figsize=(12, 10))
        im = ax.imshow(sim_matrix, cmap='viridis', aspect='auto')

        ax.set_xticks(range(n_domains))
        ax.set_yticks(range(n_cases))
        ax.set_xticklabels([d['name'] for d in kb_domains], rotation=45, ha='right')
        ax.set_yticklabels([c['id'] for c in test_cases])

        ax.set_xlabel('KB Domains')
        ax.set_ylabel('Boundary Test Cases')
        ax.set_title('h-c1: Domain Coverage Similarity Heatmap')

        plt.colorbar(im, label='Jaccard Similarity')
        plt.tight_layout()
        save_path = os.path.join(self.output_dir, 'domain_coverage_heatmap.png')
        plt.savefig(save_path, dpi=300)
        plt.close()

        return save_path
