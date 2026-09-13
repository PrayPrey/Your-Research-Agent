"""
Feature Extraction Module
Extracts operation-agnostic statistics from model weights
"""

import numpy as np
import torch
from typing import Dict, Tuple, List


class FeatureExtractor:
    """Extract operation-agnostic statistics from model weights"""

    def __init__(self, include_spectral: bool = True):
        self.include_spectral = include_spectral

    def extract_from_state_dict(self, state_dict: Dict) -> np.ndarray:
        """
        Extract full feature vector from model state_dict.
        Returns: [F] where F = num_layers × (1 L2 + 5 spectral + 1 mean + 1 std)
        """
        features = []

        for name, param in state_dict.items():
            # Skip biases
            if 'bias' in name.lower():
                continue

            # Convert to tensor if not already
            if not isinstance(param, torch.Tensor):
                param = torch.tensor(param)

            # L2 norm (operation-agnostic)
            l2_norm = torch.norm(param).item()
            features.append(l2_norm)

            # Top-5 spectral norms (if 2D or higher)
            if self.include_spectral and len(param.shape) >= 2:
                # Reshape to 2D for SVD
                param_2d = param.reshape(param.shape[0], -1)
                try:
                    spectral_norms = torch.linalg.svdvals(param_2d.float())[:5]
                    # Pad if less than 5 singular values
                    if len(spectral_norms) < 5:
                        spectral_norms = torch.cat([
                            spectral_norms,
                            torch.zeros(5 - len(spectral_norms))
                        ])
                    features.extend(spectral_norms.tolist())
                except:
                    # If SVD fails, use zeros
                    features.extend([0.0] * 5)

            # Mean and std
            features.append(param.mean().item())
            features.append(param.std().item())

        return np.array(features)

    def extract_norms_only(self, state_dict: Dict) -> np.ndarray:
        """
        Extract norms-only baseline features.
        Returns: [F_baseline] where F_baseline = num_layers × (1 L2 + 1 mean + 1 std)
        """
        features = []

        for name, param in state_dict.items():
            # Skip biases
            if 'bias' in name.lower():
                continue

            # Convert to tensor if not already
            if not isinstance(param, torch.Tensor):
                param = torch.tensor(param)

            # L2 norm
            l2_norm = torch.norm(param).item()
            features.append(l2_norm)

            # Mean and std (no spectral norms)
            features.append(param.mean().item())
            features.append(param.std().item())

        return np.array(features)

    def extract_batch(self, model_list: List[Dict]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Batch process multiple models.
        Returns: (X_full, X_baseline, y) where:
            X_full: [N, F] with spectral norms
            X_baseline: [N, F_baseline] norms-only
            y: [N] binary labels (0=ResNet, 1=ViT)
        """
        X_full_list = []
        X_baseline_list = []
        y_list = []

        for model_info in model_list:
            state_dict = model_info["state_dict"]
            architecture = model_info["architecture"]

            # Extract features
            features_full = self.extract_from_state_dict(state_dict)
            features_baseline = self.extract_norms_only(state_dict)

            X_full_list.append(features_full)
            X_baseline_list.append(features_baseline)

            # Label: 0 for ResNet, 1 for ViT
            y_list.append(0 if "resnet" in architecture.lower() else 1)

        # Find max length for padding (different architectures have different layer counts)
        max_len_full = max(len(f) for f in X_full_list)
        max_len_baseline = max(len(f) for f in X_baseline_list)

        # Pad features to same length
        X_full_padded = []
        X_baseline_padded = []

        for feat_full, feat_baseline in zip(X_full_list, X_baseline_list):
            # Pad with zeros
            if len(feat_full) < max_len_full:
                feat_full = np.pad(feat_full, (0, max_len_full - len(feat_full)))
            if len(feat_baseline) < max_len_baseline:
                feat_baseline = np.pad(feat_baseline, (0, max_len_baseline - len(feat_baseline)))

            X_full_padded.append(feat_full)
            X_baseline_padded.append(feat_baseline)

        return (
            np.array(X_full_padded),
            np.array(X_baseline_padded),
            np.array(y_list)
        )
