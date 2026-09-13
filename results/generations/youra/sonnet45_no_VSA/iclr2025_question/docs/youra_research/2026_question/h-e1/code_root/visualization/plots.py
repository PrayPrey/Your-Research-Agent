"""Visualization functions."""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os


class Visualizer:
    """Generate experiment visualizations."""

    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        sns.set_style("whitegrid")

    def plot_layer_auroc_comparison(self, layer_aurocs, baseline_aurocs, gate_threshold):
        """Plot layer-wise AUROC comparison."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Prepare data
        layers = list(layer_aurocs.keys())
        aurocs = [layer_aurocs[l] for l in layers]

        # Find peak
        peak_auroc = max(aurocs)
        peak_idx = aurocs.index(peak_auroc)

        # Colors
        colors = ['blue' if i != peak_idx and i != len(layers)-1 else
                  'green' if i == peak_idx else 'red'
                  for i in range(len(layers))]

        # Plot layer AUROCs
        x_pos = np.arange(len(layers))
        bars1 = ax.bar(x_pos, aurocs, color=colors, alpha=0.7, label='Probe')

        # Add baseline bars
        baseline_labels = list(baseline_aurocs.keys())
        baseline_values = list(baseline_aurocs.values())
        baseline_pos = np.arange(len(baseline_labels)) + len(layers) + 0.5
        bars2 = ax.bar(baseline_pos, baseline_values, color='gray', alpha=0.5, label='Baseline')

        # Gate threshold line
        ax.axhline(y=peak_auroc - gate_threshold, color='orange',
                   linestyle='--', linewidth=2, label=f'Gate (peak - {gate_threshold})')

        # Labels
        ax.set_xlabel('Layer / Method', fontsize=12)
        ax.set_ylabel('AUROC', fontsize=12)
        ax.set_title('Layer-wise AUROC Comparison (Gate Validation)', fontsize=14)

        # X-tick labels
        all_labels = [f'L{l}' for l in layers] + baseline_labels
        all_pos = list(x_pos) + list(baseline_pos)
        ax.set_xticks(all_pos)
        ax.set_xticklabels(all_labels)

        ax.legend()
        ax.grid(True, alpha=0.3)

        # Save
        save_path = os.path.join(self.output_dir, 'layer_auroc_comparison.png')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved figure: {save_path}")

    def plot_roc_curves(self, layer_roc_data):
        """Plot ROC curves for all layers."""
        fig, ax = plt.subplots(figsize=(8, 8))

        colors = ['blue', 'orange', 'green', 'red']
        for i, (layer, data) in enumerate(layer_roc_data.items()):
            fpr = data['fpr']
            tpr = data['tpr']
            auroc = data['auroc']
            ax.plot(fpr, tpr, color=colors[i % len(colors)],
                    label=f'L{layer} (AUROC={auroc:.3f})', linewidth=2)

        # Diagonal reference
        ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random')

        ax.set_xlabel('False Positive Rate', fontsize=12)
        ax.set_ylabel('True Positive Rate', fontsize=12)
        ax.set_title('ROC Curves by Layer', fontsize=14)
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)

        # Save
        save_path = os.path.join(self.output_dir, 'roc_curves.png')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved figure: {save_path}")

    def plot_confusion_matrices(self, confusion_matrices):
        """Plot confusion matrices for all layers."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()

        layers = list(confusion_matrices.keys())

        for i, layer in enumerate(layers):
            cm = confusion_matrices[layer]

            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[i],
                        xticklabels=['Incorrect', 'Correct'],
                        yticklabels=['Incorrect', 'Correct'])
            axes[i].set_title(f'Layer {layer} Confusion Matrix')
            axes[i].set_xlabel('Predicted')
            axes[i].set_ylabel('True')

        # Save
        save_path = os.path.join(self.output_dir, 'confusion_matrices.png')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved figure: {save_path}")
