"""BatchNormFeatureExtractor: Extract 6 batch normalization features
NEW for h-m3 - tests normalization mechanism hypothesis
"""

import torch
import torch.nn as nn
import numpy as np


class BatchNormFeatureExtractor:
    """Extract 6 batch normalization features from pretrained CNNs."""

    def __init__(self):
        """Initialize extractor (stateless)."""
        pass

    def extract_features(self, model: nn.Module) -> np.ndarray:
        """Extract 6 BN features. model: nn.Module -> features: [6,]"""
        # Step 1: Collect all batch norm layers
        bn_layers = self.collect_bn_layers(model)

        # Step 2: Handle models without BN (VGG, AlexNet, SqueezeNet)
        if len(bn_layers) == 0:
            return np.zeros(6, dtype=np.float64)

        # Step 3: Extract gamma (weight) and beta (bias) statistics
        gamma_mean, gamma_std = self.extract_gamma_stats(bn_layers)
        beta_mean, beta_std = self.extract_beta_stats(bn_layers)

        # Step 4: Compute depth-weighted norm
        depth_weighted_norm = self.compute_depth_weighted_norm(bn_layers)

        # Step 5: Return feature vector
        feature_vector = np.array([
            len(bn_layers),      # Feature 1: BN layer count
            gamma_mean,          # Feature 2: Mean gamma (scale parameter)
            gamma_std,           # Feature 3: Std gamma (distribution shape)
            beta_mean,           # Feature 4: Mean beta (shift parameter)
            beta_std,            # Feature 5: Std beta (distribution shape)
            depth_weighted_norm  # Feature 6: Depth-weighted BN norm
        ], dtype=np.float64)

        return feature_vector

    def collect_bn_layers(self, model: nn.Module) -> list:
        """Collect all BatchNorm2d layers. Returns: list of nn.BatchNorm2d"""
        bn_layers = []
        for module in model.modules():
            if isinstance(module, nn.BatchNorm2d):
                bn_layers.append(module)
        return bn_layers

    def extract_gamma_stats(self, bn_layers: list) -> tuple:
        """Extract gamma (weight) statistics. Returns: (mean, std)"""
        if not bn_layers:
            return 0.0, 0.0

        # Concatenate all gamma parameters
        all_gamma = []
        for bn in bn_layers:
            gamma_values = bn.weight.data.cpu().numpy().flatten()
            all_gamma.extend(gamma_values)

        all_gamma = np.array(all_gamma)
        return float(np.mean(all_gamma)), float(np.std(all_gamma))

    def extract_beta_stats(self, bn_layers: list) -> tuple:
        """Extract beta (bias) statistics. Returns: (mean, std)"""
        if not bn_layers:
            return 0.0, 0.0

        # Concatenate all beta parameters
        all_beta = []
        for bn in bn_layers:
            beta_values = bn.bias.data.cpu().numpy().flatten()
            all_beta.extend(beta_values)

        all_beta = np.array(all_beta)
        return float(np.mean(all_beta)), float(np.std(all_beta))

    def compute_depth_weighted_norm(self, bn_layers: list) -> float:
        """Compute depth-weighted BN norm. Returns: float"""
        if not bn_layers:
            return 0.0

        # Weight later layers more heavily (tests accumulation hypothesis)
        weighted_sum = 0.0
        for i, bn in enumerate(bn_layers):
            layer_norm = bn.weight.data.abs().mean().item()
            weighted_sum += (i + 1) * layer_norm

        return float(weighted_sum)
