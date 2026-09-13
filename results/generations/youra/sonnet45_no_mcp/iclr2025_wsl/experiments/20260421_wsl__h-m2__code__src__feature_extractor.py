"""ArchitecturalFeatureExtractor: Extract 8 architectural constraint features
NEW for h-m2 - replaces gradient-flow features with architectural patterns
"""

import torch
import torch.nn as nn
import numpy as np


class ArchitecturalFeatureExtractor:
    """Extract 8 architectural constraint features from pretrained CNNs."""

    def __init__(self):
        """Initialize extractor (no state needed)."""
        pass

    def extract_features(self, model: nn.Module) -> np.ndarray:
        """Extract 8 architectural features. model: nn.Module -> features: [8,]"""
        # Count residual blocks (ResNet)
        residual_blocks = self.count_residual_blocks(model)

        # Count dense connections (DenseNet)
        dense_connections = self.count_dense_connections(model)

        # Compute bottleneck ratio
        bottleneck_ratio = self.compute_bottleneck_ratio(model)

        # Count total Conv2d layers
        layer_count = sum(1 for m in model.modules() if isinstance(m, nn.Conv2d))

        # Check if skip connections are present
        skip_present = 1 if (residual_blocks > 0 or dense_connections > 0) else 0

        # Extract residual path norms
        residual_norm = self.extract_residual_path_norms(model)

        # Count transition layers (DenseNet)
        transition_count = self.count_transition_layers(model)

        # Detect architecture family (ResNet/DenseNet=1, VGG/other=0)
        arch_family = self.detect_architecture_family(model)

        # Return as array (8 features)
        feature_vector = np.array([
            residual_blocks,
            dense_connections,
            bottleneck_ratio,
            layer_count,
            skip_present,
            residual_norm,
            transition_count,
            arch_family
        ], dtype=np.float64)

        return feature_vector

    def count_residual_blocks(self, model: nn.Module) -> int:
        """Count modules with 'downsample' attribute. Returns: int"""
        count = 0
        for module in model.modules():
            if hasattr(module, 'downsample') and module.downsample is not None:
                count += 1
        return count

    def count_dense_connections(self, model: nn.Module) -> int:
        """Count 'denselayer' modules. Returns: int"""
        count = 0
        for name, module in model.named_modules():
            if 'denselayer' in name.lower():
                count += 1
        return count

    def compute_bottleneck_ratio(self, model: nn.Module) -> float:
        """Compute (1x1 convs) / (total convs). Returns: float in [0, 1]"""
        total_convs = 0
        bottleneck_convs = 0

        for module in model.modules():
            if isinstance(module, nn.Conv2d):
                total_convs += 1
                if module.kernel_size == (1, 1):
                    bottleneck_convs += 1

        return bottleneck_convs / total_convs if total_convs > 0 else 0.0

    def extract_residual_path_norms(self, model: nn.Module) -> float:
        """Mean Frobenius norm of downsample layers. Returns: float"""
        residual_norms = []

        for name, module in model.named_modules():
            if hasattr(module, 'downsample') and module.downsample is not None:
                # Extract norms from downsample parameters
                for param in module.downsample.parameters():
                    # Flatten to handle 4D conv weights
                    norm = torch.linalg.norm(param.data.flatten(), ord=2).item()
                    residual_norms.append(norm)

        return np.mean(residual_norms) if residual_norms else 0.0

    def count_transition_layers(self, model: nn.Module) -> int:
        """Count DenseNet transition layers. Returns: int"""
        count = 0
        for name, module in model.named_modules():
            if 'transition' in name.lower():
                count += 1
        return count

    def detect_architecture_family(self, model: nn.Module) -> int:
        """Detect ResNet/DenseNet (1) vs VGG/other (0). Returns: int"""
        model_name = model.__class__.__name__.lower()

        # ResNet and DenseNet have architectural constraints (skip connections)
        if 'resnet' in model_name or 'densenet' in model_name:
            return 1
        else:
            return 0
