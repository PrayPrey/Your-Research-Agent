"""GradientFlowFeatureExtractor: Extract gradient-flow features from model weights
Core mechanism for h-m1 hypothesis testing
"""

import torch
import numpy as np
import torch.nn as nn
from typing import Tuple


class GradientFlowFeatureExtractor:
    """Extract gradient-flow features from pretrained CNN weights.

    Captures layer-wise progression patterns that reflect gradient
    accumulation effects during training (shallow vs deep networks).
    """

    def extract_layer_norms_with_positions(self, model: nn.Module) -> Tuple[np.ndarray, np.ndarray]:
        """Extract Frobenius norms with normalized layer positions.

        Args:
            model: PyTorch pretrained model

        Returns:
            layer_norms: (L,) array of Frobenius norms
            layer_positions: (L,) array of normalized positions [0, 1]
        """
        layer_norms = []
        layer_positions = []

        # Count total trainable layers first
        total_layers = sum(1 for name, param in model.named_parameters()
                          if 'weight' in name and param.requires_grad and len(param.shape) >= 2)

        if total_layers == 0:
            return np.array([]), np.array([])

        # Extract norms with position tracking
        current_idx = 0
        for name, param in model.named_parameters():
            # Filter: Only trainable Conv2d/Linear layers
            if 'weight' in name and param.requires_grad and len(param.shape) >= 2:
                # Compute Frobenius norm
                norm = torch.norm(param.data, p='fro').item()

                # Normalized position: 0.0 (input) to 1.0 (output)
                position = current_idx / (total_layers - 1) if total_layers > 1 else 0.0

                layer_norms.append(norm)
                layer_positions.append(position)
                current_idx += 1

        return np.array(layer_norms), np.array(layer_positions)

    def compute_gradient_flow_features(self, layer_norms: np.ndarray,
                                       layer_positions: np.ndarray) -> np.ndarray:
        """Compute 6 gradient-flow features from layer norms and positions.

        Args:
            layer_norms: (L,) array of layer norms
            layer_positions: (L,) array of normalized positions

        Returns:
            features: (6,) array with gradient-flow features
        """
        if len(layer_norms) == 0:
            return np.zeros(6)

        # Feature 1: Norm progression slope (captures gradient accumulation trend)
        # Uses linear regression: slope, intercept = polyfit(x, y, deg=1)
        if len(layer_norms) > 1:
            norm_slope = np.polyfit(layer_positions, layer_norms, deg=1)[0]
        else:
            norm_slope = 0.0

        # Feature 2: Norm variance (gradient stability across depth)
        norm_variance = np.var(layer_norms)

        # Feature 3: Input-layer norm (initial gradient magnitude)
        input_norm = layer_norms[0]

        # Feature 4: Output-layer norm (final gradient magnitude)
        output_norm = layer_norms[-1]

        # Feature 5: Gradient depth proxy (weighted by position)
        # Deep networks accumulate more gradient transformations → higher weighted sum
        depth_weighted_norm = np.sum(layer_norms * layer_positions)

        # Feature 6: Layer count (explicit depth signal)
        layer_count = len(layer_norms)

        return np.array([
            norm_slope,
            norm_variance,
            input_norm,
            output_norm,
            depth_weighted_norm,
            layer_count
        ])

    def extract_features(self, model: nn.Module) -> np.ndarray:
        """End-to-end extraction of gradient-flow features.

        Args:
            model: PyTorch pretrained model (e.g., resnet50, vgg16)

        Returns:
            features: (6,) numpy array with gradient-flow features:
                [0] norm_slope: Linear trend of norms across layers
                [1] norm_variance: Variance of layer norms (stability)
                [2] input_norm: First layer norm magnitude
                [3] output_norm: Last layer norm magnitude
                [4] depth_weighted_norm: Sum of (position × norm)
                [5] layer_count: Number of trainable layers
        """
        # Step 1: Extract layer-wise norms with position tracking
        layer_norms, layer_positions = self.extract_layer_norms_with_positions(model)

        # Validate layer norms
        if len(layer_norms) == 0:
            raise ValueError("No trainable weight parameters found in model")

        if not np.all(layer_norms > 0):
            raise ValueError("Invalid layer norms: some values are not positive")

        # Step 2: Compute gradient-flow features
        features = self.compute_gradient_flow_features(layer_norms, layer_positions)

        # Validate output shape
        if features.shape != (6,):
            raise ValueError(f"Invalid feature shape: {features.shape}, expected (6,)")

        return features
