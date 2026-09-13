"""
Baseline fingerprinting methods for comparison.
"""

import torch
import torch.nn as nn
import numpy as np
from sklearn.decomposition import PCA
from scipy.stats import skew, kurtosis
from typing import Dict, List
import hashlib

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class WeightStatisticsFingerprinter:
    """Baseline: Extract statistical features from weights."""
    def __init__(self, feature_types=['mean', 'std', 'min', 'max', 'skew', 'kurtosis']):
        self.feature_types = feature_types

    def extract_features(self, model_state_dict: Dict[str, torch.Tensor]) -> np.ndarray:
        """Extract statistical features from model weights."""
        features = []

        for name, param in model_state_dict.items():
            if 'weight' in name or 'bias' in name:
                weights = param.cpu().numpy().flatten()

                layer_features = []
                if 'mean' in self.feature_types:
                    layer_features.append(np.mean(weights))
                if 'std' in self.feature_types:
                    layer_features.append(np.std(weights))
                if 'min' in self.feature_types:
                    layer_features.append(np.min(weights))
                if 'max' in self.feature_types:
                    layer_features.append(np.max(weights))
                if 'skew' in self.feature_types:
                    layer_features.append(skew(weights))
                if 'kurtosis' in self.feature_types:
                    layer_features.append(kurtosis(weights))

                features.extend(layer_features)

        return np.array(features, dtype=np.float32)

    def __call__(self, model_state_dict: Dict[str, torch.Tensor]) -> np.ndarray:
        return self.extract_features(model_state_dict)


class PCAFingerprinter:
    """Baseline: PCA on flattened weights."""
    def __init__(self, n_components=128):
        self.n_components = n_components
        self.pca = None

    def fit(self, weight_matrices: List[np.ndarray]):
        """Fit PCA on a collection of weight matrices."""
        self.pca = PCA(n_components=self.n_components)
        self.pca.fit(weight_matrices)

    def extract_features(self, model_state_dict: Dict[str, torch.Tensor]) -> np.ndarray:
        """Extract PCA features from model weights."""
        # Flatten all weights
        weights = []
        for name, param in sorted(model_state_dict.items()):
            if 'weight' in name or 'bias' in name:
                weights.append(param.cpu().numpy().flatten())

        flat_weights = np.concatenate(weights)

        # Pad or truncate to fixed size
        target_size = 10000
        if len(flat_weights) < target_size:
            flat_weights = np.pad(flat_weights, (0, target_size - len(flat_weights)))
        else:
            flat_weights = flat_weights[:target_size]

        if self.pca is None:
            # Return raw features if PCA not fitted
            return flat_weights[:self.n_components]

        # Apply PCA
        features = self.pca.transform(flat_weights.reshape(1, -1))
        return features.flatten().astype(np.float32)

    def __call__(self, model_state_dict: Dict[str, torch.Tensor]) -> np.ndarray:
        return self.extract_features(model_state_dict)


class NaiveHashFingerprinter:
    """Baseline: Cryptographic hash of weights (not permutation invariant)."""
    def __init__(self):
        pass

    def extract_features(self, model_state_dict: Dict[str, torch.Tensor]) -> np.ndarray:
        """Extract hash-based features from model weights."""
        # Flatten all weights in sorted order
        weights = []
        for name, param in sorted(model_state_dict.items()):
            if 'weight' in name or 'bias' in name:
                weights.append(param.cpu().numpy().flatten())

        flat_weights = np.concatenate(weights)

        # Compute hash
        hash_obj = hashlib.sha256(flat_weights.tobytes())
        hash_bytes = hash_obj.digest()

        # Convert to feature vector
        features = np.frombuffer(hash_bytes, dtype=np.uint8).astype(np.float32)
        # Normalize to [0, 1]
        features = features / 255.0

        # Expand to target dimension
        target_dim = 128
        features = np.tile(features, target_dim // len(features) + 1)[:target_dim]

        return features

    def __call__(self, model_state_dict: Dict[str, torch.Tensor]) -> np.ndarray:
        return self.extract_features(model_state_dict)


class NeuronEmbeddingFingerprinter:
    """
    Baseline: Simple permutation-invariant representation using neuron statistics.
    This is a simplified version inspired by neuron embedding methods.
    """
    def __init__(self, embedding_dim=128):
        self.embedding_dim = embedding_dim

    def extract_features(self, model_state_dict: Dict[str, torch.Tensor]) -> np.ndarray:
        """Extract permutation-invariant features from neurons."""
        layer_features = []

        for name, param in sorted(model_state_dict.items()):
            if 'weight' in name:
                weights = param.cpu().numpy()

                if len(weights.shape) == 2:  # Linear layer
                    # Compute statistics for each neuron (row)
                    neuron_stats = []
                    for i in range(weights.shape[0]):
                        neuron_weights = weights[i, :]
                        stats = [
                            np.mean(neuron_weights),
                            np.std(neuron_weights),
                            np.max(np.abs(neuron_weights)),
                            np.sum(neuron_weights > 0) / len(neuron_weights)  # Sparsity
                        ]
                        neuron_stats.append(stats)

                    neuron_stats = np.array(neuron_stats)

                    # Aggregate across neurons (permutation-invariant)
                    layer_feat = [
                        np.mean(neuron_stats, axis=0),
                        np.std(neuron_stats, axis=0),
                        np.min(neuron_stats, axis=0),
                        np.max(neuron_stats, axis=0)
                    ]
                    layer_features.append(np.concatenate(layer_feat))

                elif len(weights.shape) == 4:  # Conv layer
                    # Compute statistics for each filter
                    filter_stats = []
                    for i in range(weights.shape[0]):
                        filter_weights = weights[i].flatten()
                        stats = [
                            np.mean(filter_weights),
                            np.std(filter_weights),
                            np.max(np.abs(filter_weights)),
                            np.sum(filter_weights > 0) / len(filter_weights)
                        ]
                        filter_stats.append(stats)

                    filter_stats = np.array(filter_stats)

                    # Aggregate across filters
                    layer_feat = [
                        np.mean(filter_stats, axis=0),
                        np.std(filter_stats, axis=0),
                        np.min(filter_stats, axis=0),
                        np.max(filter_stats, axis=0)
                    ]
                    layer_features.append(np.concatenate(layer_feat))

        if len(layer_features) == 0:
            return np.zeros(self.embedding_dim, dtype=np.float32)

        # Concatenate all layer features
        features = np.concatenate(layer_features)

        # Pad or truncate to target dimension
        if len(features) < self.embedding_dim:
            features = np.pad(features, (0, self.embedding_dim - len(features)))
        else:
            features = features[:self.embedding_dim]

        return features.astype(np.float32)

    def __call__(self, model_state_dict: Dict[str, torch.Tensor]) -> np.ndarray:
        return self.extract_features(model_state_dict)


if __name__ == "__main__":
    # Test baseline methods
    dummy_state_dict = {
        'fc1.weight': torch.randn(128, 784),
        'fc1.bias': torch.randn(128),
        'fc2.weight': torch.randn(10, 128),
        'fc2.bias': torch.randn(10)
    }

    print("Testing WeightStatisticsFingerprinter...")
    stats_fp = WeightStatisticsFingerprinter()
    features = stats_fp(dummy_state_dict)
    print(f"Features shape: {features.shape}")

    print("\nTesting PCAFingerprinter...")
    pca_fp = PCAFingerprinter(n_components=128)
    features = pca_fp(dummy_state_dict)
    print(f"Features shape: {features.shape}")

    print("\nTesting NaiveHashFingerprinter...")
    hash_fp = NaiveHashFingerprinter()
    features = hash_fp(dummy_state_dict)
    print(f"Features shape: {features.shape}")

    print("\nTesting NeuronEmbeddingFingerprinter...")
    neuron_fp = NeuronEmbeddingFingerprinter(embedding_dim=128)
    features = neuron_fp(dummy_state_dict)
    print(f"Features shape: {features.shape}")
