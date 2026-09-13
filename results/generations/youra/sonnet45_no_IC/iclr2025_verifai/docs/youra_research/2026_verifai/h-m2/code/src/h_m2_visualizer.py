"""Visualization for h-m2 extraction evaluation results."""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List

class Visualizer:
    """Generate figures for extraction evaluation."""
    
    def __init__(self, figures_folder: Path):
        """Initialize visualizer."""
        self.figures_folder = figures_folder
        self.figures_folder.mkdir(exist_ok=True)
    
    def plot_gate_metrics(self, results: Dict, thresholds: Dict):
        """Bar chart with precision, recall, kappa vs thresholds."""
        metrics = ["Precision", "Recall", "Kappa"]
        values = [results["precision"], results["recall"], results["kappa"]]
        thresholds_vals = [thresholds["precision"], thresholds["recall"], thresholds["kappa"]]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(metrics))
        width = 0.35
        
        ax.bar(x - width/2, values, width, label='Actual', color='steelblue')
        ax.bar(x + width/2, thresholds_vals, width, label='Threshold', color='coral', alpha=0.7)
        
        ax.set_ylabel('Score')
        ax.set_title('H-M2 Gate Metrics: Extraction Quality')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        ax.set_ylim(0, 1.0)
        ax.axhline(y=0.7, color='red', linestyle='--', alpha=0.5)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figures_folder / "gate_metrics.png", dpi=300)
        plt.close()
    
    def plot_confusion_matrix(self, sample_results: List[Dict]):
        """Heatmap of TP, FP, FN aggregated."""
        total_tp = sum(r["tp"] for r in sample_results)
        total_fp = sum(r["fp"] for r in sample_results)
        total_fn = sum(r["fn"] for r in sample_results)
        total_tn = 0  # Not applicable for extraction
        
        matrix = np.array([[total_tp, total_fp], [total_fn, total_tn]])
        
        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(matrix, cmap='Blues')
        
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Predicted Positive', 'Predicted Negative'])
        ax.set_yticklabels(['Actual Positive', 'Actual Negative'])
        
        for i in range(2):
            for j in range(2):
                text = ax.text(j, i, int(matrix[i, j]), ha="center", va="center", color="black", fontsize=20)
        
        ax.set_title("Confusion Matrix (Aggregated)")
        plt.colorbar(im, ax=ax)
        plt.tight_layout()
        plt.savefig(self.figures_folder / "confusion_matrix.png", dpi=300)
        plt.close()
    
    def plot_per_category_performance(self, results_by_type: Dict):
        """Bar chart comparing assumptions vs claims."""
        categories = list(results_by_type.keys())
        precisions = [results_by_type[cat]["precision"] for cat in categories]
        recalls = [results_by_type[cat]["recall"] for cat in categories]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(categories))
        width = 0.35
        
        ax.bar(x - width/2, precisions, width, label='Precision', color='steelblue')
        ax.bar(x + width/2, recalls, width, label='Recall', color='coral')
        
        ax.set_ylabel('Score')
        ax.set_title('Performance by Category (Assumptions vs Claims)')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.set_ylim(0, 1.0)
        ax.axhline(y=0.7, color='red', linestyle='--', alpha=0.5, label='Threshold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figures_folder / "per_category_performance.png", dpi=300)
        plt.close()
    
    def plot_error_examples(self, error_samples: List[Dict]):
        """Text plot showing false positive/negative examples."""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')
        
        y_pos = 0.95
        ax.text(0.5, y_pos, "Error Analysis Examples", ha='center', fontsize=16, fontweight='bold')
        y_pos -= 0.08
        
        for i, sample in enumerate(error_samples[:5]):
            ax.text(0.05, y_pos, f"{i+1}. {sample['type'].upper()}: {sample['error_type']}", fontsize=10, fontweight='bold')
            y_pos -= 0.05
            ax.text(0.10, y_pos, f"Text: {sample['text'][:100]}...", fontsize=8, style='italic')
            y_pos -= 0.05
            ax.text(0.10, y_pos, f"Issue: {sample['description']}", fontsize=8, color='red')
            y_pos -= 0.10
        
        plt.tight_layout()
        plt.savefig(self.figures_folder / "error_examples.png", dpi=300)
        plt.close()
