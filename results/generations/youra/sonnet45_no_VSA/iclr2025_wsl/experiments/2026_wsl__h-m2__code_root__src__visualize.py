"""Visualization for width-scaling experiment."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict
import json


class WidthScalingVisualizer:
    """Create visualizations for width-scaling results."""

    def __init__(self, config: dict):
        """
        Initialize visualizer.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.figures_dir = Path(config["figures_dir"])
        self.figures_dir.mkdir(parents=True, exist_ok=True)

    def plot_width_scaling_curve(
        self,
        test_errors: Dict,
        save_path: str = None
    ):
        """
        Plot test error advantage vs width.

        Args:
            test_errors: Dictionary of test errors per width
            save_path: Path to save figure
        """
        widths = sorted(test_errors.keys())
        deltas = [test_errors[w]['delta'] for w in widths]
        mlp_errors = [test_errors[w]['mlp_error'] for w in widths]
        nfn_errors = [test_errors[w]['nfn_error'] for w in widths]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Plot 1: Δ_test(d) vs width
        ax1.plot(widths, deltas, 'o-', linewidth=2, markersize=8, label='Δ_test(d)')
        ax1.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Zero line')
        ax1.set_xlabel('Hidden Width (d)', fontsize=12)
        ax1.set_ylabel('Test Error Advantage Δ_test(d)', fontsize=12)
        ax1.set_title('Test Error Advantage vs Width', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Plot 2: Individual errors
        ax2.plot(widths, mlp_errors, 's-', linewidth=2, markersize=8, label='MLP Error')
        ax2.plot(widths, nfn_errors, '^-', linewidth=2, markersize=8, label='NFN Error')
        ax2.set_xlabel('Hidden Width (d)', fontsize=12)
        ax2.set_ylabel('Test Error', fontsize=12)
        ax2.set_title('MLP vs NFN Test Error', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved width scaling curve to {save_path}")
        else:
            save_path = self.figures_dir / "width_scaling_curve.png"
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved width scaling curve to {save_path}")

        plt.close()

    def plot_training_loss_comparison(
        self,
        training_results: Dict,
        save_path: str = None
    ):
        """
        Plot training loss comparison across widths.

        Args:
            training_results: Dictionary of training results
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        widths = [r['width'] for r in training_results['results']]
        mlp_losses = [r['mlp']['train_loss'] for r in training_results['results']]
        nfn_losses = [r['nfn']['train_loss'] for r in training_results['results']]

        x = np.arange(len(widths))
        width_labels = [str(w) for w in widths]

        bar_width = 0.35
        ax.bar(x - bar_width/2, mlp_losses, bar_width, label='MLP', alpha=0.8)
        ax.bar(x + bar_width/2, nfn_losses, bar_width, label='NFN', alpha=0.8)

        ax.set_xlabel('Hidden Width', fontsize=12)
        ax.set_ylabel('Training Loss', fontsize=12)
        ax.set_title('Training Loss Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(width_labels)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved training loss comparison to {save_path}")
        else:
            save_path = self.figures_dir / "training_loss_comparison.png"
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved training loss comparison to {save_path}")

        plt.close()

    def plot_gate_metrics(
        self,
        gate_metrics: Dict,
        save_path: str = None
    ):
        """
        Plot gate metrics (mandatory visualization).

        Args:
            gate_metrics: Dictionary of gate metrics
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        metrics = ['Monotonicity\nSatisfied', 'All Deltas\nPositive', 'Gate\nPass']
        values = [
            1.0 if gate_metrics['monotonicity_satisfied'] else 0.0,
            1.0 if gate_metrics['all_deltas_positive'] else 0.0,
            1.0 if gate_metrics['gate_pass'] else 0.0
        ]
        colors = ['green' if v > 0.5 else 'red' for v in values]

        bars = ax.bar(metrics, values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)

        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            label = 'PASS' if val > 0.5 else 'FAIL'
            ax.text(bar.get_x() + bar.get_width()/2., height/2,
                   label, ha='center', va='center',
                   fontsize=14, fontweight='bold', color='white')

        ax.set_ylim([0, 1.2])
        ax.set_ylabel('Status', fontsize=12)
        ax.set_title('MUST_WORK Gate Metrics', fontsize=14, fontweight='bold')
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['FAIL', 'PASS'])
        ax.grid(True, alpha=0.3, axis='y')

        # Add mean delta as text
        plt.text(0.5, 1.1, f"Mean Δ_test: {gate_metrics['mean_delta']:.4f}",
                ha='center', transform=ax.transAxes, fontsize=12,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved gate metrics to {save_path}")
        else:
            save_path = self.figures_dir / "gate_metrics.png"
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved gate metrics to {save_path}")

        plt.close()

    def generate_all_visualizations(
        self,
        results_dir: Path
    ):
        """
        Generate all required visualizations.

        Args:
            results_dir: Directory containing results JSON files
        """
        # Load training results
        training_file = results_dir / "training_results.json"
        if training_file.exists():
            with open(training_file, 'r') as f:
                training_results = json.load(f)
            self.plot_training_loss_comparison(training_results)

        # Load test errors
        test_errors_file = results_dir / "test_errors.json"
        if test_errors_file.exists():
            with open(test_errors_file, 'r') as f:
                test_data = json.load(f)
            self.plot_width_scaling_curve(test_data['test_errors'])

        # Load gate metrics
        gate_metrics_file = results_dir / "gate_metrics.json"
        if gate_metrics_file.exists():
            with open(gate_metrics_file, 'r') as f:
                gate_metrics = json.load(f)
            self.plot_gate_metrics(gate_metrics)

        print("\nAll visualizations generated successfully!")
