"""FeatureExtractor: Extract layer-wise Frobenius norm statistics"""

import torch
import numpy as np
import torch.nn as nn
from typing import List


class FeatureExtractor:
    """Extract layer-wise Frobenius norm statistics from model weights."""

    def extract_layer_norms(self, model: nn.Module) -> np.ndarray:
        """Extract Frobenius norm per layer. Returns: [L,] array"""
        layer_norms = []
        for name, param in model.named_parameters():
            if 'weight' in name and param.requires_grad:
                # Compute Frobenius norm for this layer
                norm = torch.norm(param.data, p='fro').item()
                layer_norms.append(norm)
        return np.array(layer_norms)

    def compute_statistics(self, layer_norms: np.ndarray) -> np.ndarray:
        """Compute [mean, std, min, max]. Returns: [4,] array"""
        if len(layer_norms) == 0:
            return np.zeros(4)

        stats = np.array([
            np.mean(layer_norms),
            np.std(layer_norms),
            np.min(layer_norms),
            np.max(layer_norms)
        ])
        return stats

    def extract_features(self, model: nn.Module) -> np.ndarray:
        """End-to-end extraction. Returns: [4,] feature vector"""
        layer_norms = self.extract_layer_norms(model)

        # Validate layer norms
        if len(layer_norms) == 0:
            raise ValueError("No trainable weight parameters found in model")

        if not np.all(layer_norms > 0):
            raise ValueError("Invalid layer norms: some values are not positive")

        features = self.compute_statistics(layer_norms)

        # Validate output shape
        if features.shape != (4,):
            raise ValueError(f"Invalid feature shape: {features.shape}, expected (4,)")

        return features
