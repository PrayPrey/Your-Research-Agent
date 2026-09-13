"""Evaluation metrics for hypothesis validation"""

import torch
import numpy as np
from typing import Dict
from torch.utils.data import DataLoader


class Evaluator:
    """Metric computation for hypothesis validation"""

    def __init__(self, model: torch.nn.Module, test_loader: DataLoader, device: str = 'cuda'):
        self.model = model.to(device)
        self.model.eval()
        self.test_loader = test_loader
        self.device = device

    def compute_reconstruction_error(self) -> float:
        """Compute reconstruction error on test set (percentage)"""
        total_error = 0.0
        num_samples = 0

        with torch.no_grad():
            for batch in self.test_loader:
                weights = batch['weights'].to(self.device)
                arch_labels = batch['arch_label'].to(self.device)

                z = self.model(weights, arch_labels)
                weights_recon = self.model.reconstruct_weights(z)

                error = relative_mse(weights, weights_recon)
                total_error += error * weights.size(0)
                num_samples += weights.size(0)

        return (total_error / num_samples) * 100  # Return as percentage

    def compute_frozen_k_generalization(self, rnn_loader: DataLoader) -> float:
        """Compute R_RNN on held-out RNN test set (percentage)"""
        total_error = 0.0
        num_samples = 0

        with torch.no_grad():
            for batch in rnn_loader:
                weights = batch['weights'].to(self.device)
                arch_labels = batch['arch_label'].to(self.device)

                z = self.model(weights, arch_labels)
                weights_recon = self.model.reconstruct_weights(z)

                error = relative_mse(weights, weights_recon)
                total_error += error * weights.size(0)
                num_samples += weights.size(0)

        return (total_error / num_samples) * 100  # Return as percentage

    def compute_kernel_robustness(self, num_permutations: int = 1000, threshold: float = 0.01) -> float:
        """Compute % of permutations with divergence < threshold"""
        robust_count = 0
        total_count = 0

        with torch.no_grad():
            for batch in self.test_loader:
                weights = batch['weights'].to(self.device)
                arch_labels = batch['arch_label'].to(self.device)

                # Original encoding
                z_original = self.model(weights, arch_labels)

                # Test multiple permutations per sample
                for _ in range(num_permutations):
                    D = weights.size(1)
                    perm_indices = torch.randperm(D, device=self.device)
                    weights_perm = weights[:, perm_indices]

                    z_perm = self.model(weights_perm, arch_labels)

                    divergence = measure_output_divergence(z_original, z_perm)

                    if divergence < threshold:
                        robust_count += 1
                    total_count += 1

                # Only test first batch for speed
                break

        return (robust_count / total_count) * 100  # Return as percentage

    def evaluate_all(self, rnn_loader: DataLoader) -> Dict[str, float]:
        """Compute all metrics"""
        print("Computing reconstruction error...")
        recon_error = self.compute_reconstruction_error()

        print("Computing frozen-K generalization...")
        r_rnn = self.compute_frozen_k_generalization(rnn_loader)

        print("Computing kernel robustness...")
        robustness = self.compute_kernel_robustness()

        return {
            'reconstruction_error': recon_error,
            'frozen_k_generalization': r_rnn,
            'kernel_robustness': robustness
        }


def relative_mse(original: torch.Tensor, reconstructed: torch.Tensor) -> float:
    """Compute MSE / ||original||^2 as ratio"""
    mse = torch.mean((original - reconstructed) ** 2)
    norm_sq = torch.mean(original ** 2)
    return (mse / (norm_sq + 1e-8)).item()


def measure_output_divergence(z_original: torch.Tensor, z_permuted: torch.Tensor) -> float:
    """Compute normalized L1 divergence"""
    divergence = torch.mean(torch.abs(z_original - z_permuted))
    return divergence.item()
