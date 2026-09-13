"""ECE computation and visualization for calibration evaluation."""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Tuple, Dict


class ECELoss(nn.Module):
    """Expected Calibration Error with uniform binning."""

    def __init__(self, n_bins: int = 15):
        """
        Args:
            n_bins: Number of uniform bins in [0,1]
        """
        super().__init__()
        bin_boundaries = torch.linspace(0, 1, n_bins + 1)
        self.bin_lowers = bin_boundaries[:-1]  # [n_bins]
        self.bin_uppers = bin_boundaries[1:]   # [n_bins]
        self.n_bins = n_bins

    def forward(
        self,
        confidences: torch.Tensor,
        correctness: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute ECE = Σ b_i |p_i - c_i|

        Args:
            confidences: [N] predicted confidence per sample
            correctness: [N] actual correctness (0 or 1)

        Returns:
            ece: Scalar ECE value in [0, 1]
        """
        ece = torch.zeros(1, device=confidences.device)

        for bin_lower, bin_upper in zip(self.bin_lowers, self.bin_uppers):
            # Find samples in current bin
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            prop_in_bin = in_bin.float().mean()

            if prop_in_bin > 0:
                # Compute bin statistics
                accuracy_in_bin = correctness[in_bin].float().mean()
                avg_conf_in_bin = confidences[in_bin].mean()

                # Accumulate weighted calibration error
                ece += torch.abs(avg_conf_in_bin - accuracy_in_bin) * prop_in_bin

        return ece

    def get_bin_statistics(
        self,
        confidences: torch.Tensor,
        correctness: torch.Tensor
    ) -> Dict[str, List]:
        """
        Get per-bin statistics for visualization.

        Returns:
            stats: Dict with 'bin_centers', 'accuracies', 'confidences', 'counts'
        """
        bin_centers = []
        accuracies = []
        avg_confidences = []
        counts = []

        for bin_lower, bin_upper in zip(self.bin_lowers, self.bin_uppers):
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            count = in_bin.sum().item()

            bin_center = (bin_lower + bin_upper) / 2
            bin_centers.append(bin_center.item())
            counts.append(count)

            if count > 0:
                accuracies.append(correctness[in_bin].float().mean().item())
                avg_confidences.append(confidences[in_bin].mean().item())
            else:
                accuracies.append(0.0)
                avg_confidences.append(0.0)

        return {
            'bin_centers': bin_centers,
            'accuracies': accuracies,
            'confidences': avg_confidences,
            'counts': counts
        }


def extract_confidence(logits: torch.Tensor, temperature: float = 1.0) -> torch.Tensor:
    """
    Extract max softmax probability from logits.

    Args:
        logits: [N, V] or [V] raw or scaled logits
        temperature: T for scaling (if not already applied)

    Returns:
        confidences: [N] or scalar max probability per sample
    """
    if logits.dim() == 1:
        logits = logits.unsqueeze(0)  # [1, V]

    scaled_logits = logits / temperature
    probs = F.softmax(scaled_logits, dim=-1)  # [N, V]
    confidences = probs.max(dim=-1).values    # [N]

    return confidences.squeeze()


def compute_ece(
    confidences: torch.Tensor,
    correctness: torch.Tensor,
    n_bins: int = 15
) -> float:
    """
    Convenience function to compute ECE.

    Args:
        confidences: [N] confidence scores
        correctness: [N] binary labels
        n_bins: Number of bins

    Returns:
        ece: ECE value
    """
    ece_metric = ECELoss(n_bins=n_bins)
    return ece_metric(confidences, correctness).item()


class ResultVisualizer:
    """Generate all required figures for validation report."""

    def __init__(self, output_dir: str = "./figures", dpi: int = 300):
        """
        Args:
            output_dir: Directory to save figures
            dpi: Resolution for PNG output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi

    def generate_ece_comparison(
        self,
        ece_before: float,
        ece_after: float,
        threshold: float = 0.30,
        save_path: str = None
    ):
        """
        Figure 1: ECE Comparison Bar Chart (MANDATORY).

        Args:
            ece_before: ECE before calibration
            ece_after: ECE after calibration
            threshold: Gate threshold (30% reduction)
            save_path: Output file path
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(
            ['Uncalibrated', 'Calibrated'],
            [ece_before, ece_after],
            color=['#fc8d59', '#91bfdb'],
            width=0.6
        )

        # Add threshold line
        reduction_pct = (ece_before - ece_after) / ece_before * 100
        target_ece = ece_before * (1 - threshold)
        ax.axhline(y=target_ece, color='#2ca02c', linestyle='--', linewidth=2,
                   label=f'30% reduction target')

        # Annotate bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')

        # Add reduction percentage
        ax.text(0.5, max(ece_before, ece_after) * 0.9,
                f'Reduction: {reduction_pct:.1f}%',
                ha='center', fontsize=14, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        ax.set_ylabel('Expected Calibration Error (ECE)', fontsize=12)
        ax.set_title('ECE Comparison: Before vs. After Temperature Scaling', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3)

        if save_path is None:
            save_path = self.output_dir / "01_ece_comparison.png"
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def generate_reliability_diagram(
        self,
        stats_before: Dict,
        stats_after: Dict,
        save_path: str = None
    ):
        """
        Figure 2: Reliability Diagram.

        Args:
            stats_before: Bin statistics before calibration
            stats_after: Bin statistics after calibration
            save_path: Output file path
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Plot before/after lines
        ax.plot(stats_before['confidences'], stats_before['accuracies'],
                'o-', color='#d73027', linewidth=2, markersize=8,
                label='Uncalibrated')
        ax.plot(stats_after['confidences'], stats_after['accuracies'],
                's-', color='#4575b4', linewidth=2, markersize=8,
                label='Calibrated')

        # Perfect calibration line
        ax.plot([0, 1], [0, 1], 'k--', linewidth=2, alpha=0.5,
                label='Perfect Calibration')

        # Histogram overlay (sample counts per bin)
        ax2 = ax.twinx()
        ax2.bar(stats_after['bin_centers'], stats_after['counts'],
                width=0.05, alpha=0.3, color='gray', label='Sample Count')
        ax2.set_ylabel('Sample Count', fontsize=12)

        ax.set_xlabel('Confidence', fontsize=12)
        ax.set_ylabel('Accuracy', fontsize=12)
        ax.set_title('Reliability Diagram: Confidence vs. Accuracy', fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=10)
        ax2.legend(loc='upper right', fontsize=10)
        ax.grid(alpha=0.3)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        if save_path is None:
            save_path = self.output_dir / "02_reliability_diagram.png"
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def generate_calibration_curve(
        self,
        confidences_before: torch.Tensor,
        confidences_after: torch.Tensor,
        save_path: str = None
    ):
        """
        Figure 3: Calibration Curve (confidence distribution).

        Args:
            confidences_before: Confidence scores before calibration
            confidences_after: Confidence scores after calibration
            save_path: Output file path
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.hist(confidences_before.numpy(), bins=20, alpha=0.7,
                color='#fee090', label='Uncalibrated', edgecolor='black')
        ax.hist(confidences_after.numpy(), bins=20, alpha=0.7,
                color='#abd9e9', label='Calibrated', edgecolor='black')

        ax.set_xlabel('Confidence Score', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Confidence Distribution: Before vs. After', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3)

        if save_path is None:
            save_path = self.output_dir / "03_calibration_curve.png"
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def generate_convergence_plot(
        self,
        loss_history: List[float],
        optimal_temp: float,
        save_path: str = None
    ):
        """
        Figure 4: Temperature Optimization Convergence.

        Args:
            loss_history: NLL loss per iteration
            optimal_temp: Final temperature value
            save_path: Output file path
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(loss_history, linewidth=2, color='#4575b4')
        ax.set_xlabel('LBFGS Iteration', fontsize=12)
        ax.set_ylabel('NLL Loss', fontsize=12)
        ax.set_title('Temperature Optimization Convergence', fontsize=14, fontweight='bold')
        ax.grid(alpha=0.3)

        # Annotate final temperature
        ax.text(0.7, 0.95, f'Optimal T* = {optimal_temp:.3f}',
                transform=ax.transAxes, fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        if save_path is None:
            save_path = self.output_dir / "04_convergence.png"
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def generate_per_bin_error(
        self,
        stats_before: Dict,
        stats_after: Dict,
        save_path: str = None
    ):
        """
        Figure 5: Per-Bin Calibration Error.

        Args:
            stats_before: Bin statistics before calibration
            stats_after: Bin statistics after calibration
            save_path: Output file path
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        bin_centers = np.array(stats_before['bin_centers'])
        errors_before = np.abs(np.array(stats_before['confidences']) - np.array(stats_before['accuracies']))
        errors_after = np.abs(np.array(stats_after['confidences']) - np.array(stats_after['accuracies']))

        width = 0.03
        ax.bar(bin_centers - width/2, errors_before, width=width,
               color='#fdae61', label='Uncalibrated', edgecolor='black')
        ax.bar(bin_centers + width/2, errors_after, width=width,
               color='#abd9e9', label='Calibrated', edgecolor='black')

        ax.set_xlabel('Confidence Bin', fontsize=12)
        ax.set_ylabel('|Confidence - Accuracy|', fontsize=12)
        ax.set_title('Per-Bin Calibration Error', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3)

        if save_path is None:
            save_path = self.output_dir / "05_per_bin_error.png"
        plt.tight_layout()
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def generate_all_figures(
        self,
        ece_before: float,
        ece_after: float,
        confidences_before: torch.Tensor,
        confidences_after: torch.Tensor,
        correctness: torch.Tensor,
        loss_history: List[float],
        optimal_temp: float,
        n_bins: int = 15
    ):
        """
        Generate all 5 required figures.

        Args:
            ece_before: ECE before calibration
            ece_after: ECE after calibration
            confidences_before: Confidence scores before
            confidences_after: Confidence scores after
            correctness: Binary correctness labels
            loss_history: LBFGS loss history
            optimal_temp: Optimal temperature
            n_bins: Number of bins for ECE
        """
        # Get bin statistics
        ece_metric = ECELoss(n_bins=n_bins)
        stats_before = ece_metric.get_bin_statistics(confidences_before, correctness)
        stats_after = ece_metric.get_bin_statistics(confidences_after, correctness)

        # Generate all figures
        self.generate_ece_comparison(ece_before, ece_after)
        self.generate_reliability_diagram(stats_before, stats_after)
        self.generate_calibration_curve(confidences_before, confidences_after)
        self.generate_convergence_plot(loss_history, optimal_temp)
        self.generate_per_bin_error(stats_before, stats_after)

        print(f"All figures saved to {self.output_dir}")
