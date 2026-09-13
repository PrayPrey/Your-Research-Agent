"""
Weight Feature Extractor
Converts real model state_dicts into operation-grouped features
"""

import torch
import numpy as np
from typing import Dict, List, Tuple
from collections import OrderedDict


class WeightFeatureExtractor:
    """Extract operation-specific features from model weights"""

    def __init__(self, d_feature: int = 256):
        self.d_feature = d_feature

    def extract_features(self, state_dict: OrderedDict) -> Dict:
        """
        Extract features from real model state_dict.

        Args:
            state_dict: Real model weights from HuggingFace/timm

        Returns:
            Dict with keys: conv, attention, mlp, graph_nodes, graph_edges
        """
        # Group layers by operation type
        conv_layers = []
        attn_layers = []
        mlp_layers = []

        for name, param in state_dict.items():
            param_np = param.detach().cpu().numpy()

            # Skip non-weight tensors (biases, norms, etc.)
            if len(param_np.shape) < 2:
                continue

            # Classify layer type by shape and name
            if self._is_conv_layer(name, param_np.shape):
                conv_layers.append(param_np)
            elif self._is_attention_layer(name, param_np.shape):
                attn_layers.append(param_np)
            elif self._is_mlp_layer(name, param_np.shape):
                mlp_layers.append(param_np)

        # Extract statistics for each operation type
        conv_features = self._extract_operation_features(conv_layers, "conv")
        attn_features = self._extract_operation_features(attn_layers, "attention")
        mlp_features = self._extract_operation_features(mlp_layers, "mlp")

        # Build architecture graph
        graph_nodes, graph_edges = self._build_architecture_graph(state_dict)

        return {
            "conv": conv_features,
            "attention": attn_features,
            "mlp": mlp_features,
            "graph_nodes": graph_nodes,
            "graph_edges": graph_edges
        }

    def _is_conv_layer(self, name: str, shape: Tuple) -> bool:
        """Check if layer is convolutional"""
        # Conv layers have 4D tensors (out_ch, in_ch, h, w) or conv in name
        return len(shape) == 4 or "conv" in name.lower()

    def _is_attention_layer(self, name: str, shape: Tuple) -> bool:
        """Check if layer is attention"""
        # Attention layers typically have qkv, attn, or self_attn in name
        keywords = ["attn", "query", "key", "value", "qkv"]
        return any(kw in name.lower() for kw in keywords)

    def _is_mlp_layer(self, name: str, shape: Tuple) -> bool:
        """Check if layer is MLP"""
        # MLP layers have 2D tensors and fc/linear/mlp in name
        keywords = ["fc", "linear", "mlp", "dense", "classifier"]
        return len(shape) == 2 and any(kw in name.lower() for kw in keywords)

    def _extract_operation_features(self, layers: List[np.ndarray], op_type: str) -> np.ndarray:
        """
        Extract statistical features from operation layers.

        Args:
            layers: List of weight tensors for this operation type
            op_type: "conv", "attention", or "mlp"

        Returns:
            Feature vector (d_feature,)
        """
        if len(layers) == 0:
            # Return zero features if no layers of this type
            return np.zeros(self.d_feature, dtype=np.float32)

        # Compute per-layer statistics
        layer_stats = []
        for layer in layers:
            # Normalize by Frobenius norm
            layer_norm = layer / (np.linalg.norm(layer) + 1e-8)

            # Extract statistics
            stats = {
                "mean": np.mean(layer_norm),
                "std": np.std(layer_norm),
                "min": np.min(layer_norm),
                "max": np.max(layer_norm),
                "frobenius_norm": np.linalg.norm(layer),
                "spectral_norm": self._compute_spectral_norm(layer),
                "sparsity": np.mean(np.abs(layer) < 1e-6)
            }

            # Flatten stats to vector
            stat_vec = np.array([
                stats["mean"],
                stats["std"],
                stats["min"],
                stats["max"],
                np.log(stats["frobenius_norm"] + 1e-8),
                np.log(stats["spectral_norm"] + 1e-8),
                stats["sparsity"]
            ])

            layer_stats.append(stat_vec)

        # Aggregate across layers
        layer_stats = np.array(layer_stats)  # (n_layers, n_stats)

        # Compute aggregate statistics
        aggregate_features = np.concatenate([
            np.mean(layer_stats, axis=0),  # Mean stats across layers
            np.std(layer_stats, axis=0),   # Std stats across layers
            np.min(layer_stats, axis=0),   # Min stats
            np.max(layer_stats, axis=0)    # Max stats
        ])

        # Pad or truncate to d_feature
        if len(aggregate_features) < self.d_feature:
            # Pad with zeros
            aggregate_features = np.pad(
                aggregate_features,
                (0, self.d_feature - len(aggregate_features)),
                mode='constant'
            )
        else:
            # Truncate
            aggregate_features = aggregate_features[:self.d_feature]

        return aggregate_features.astype(np.float32)

    def _compute_spectral_norm(self, weight: np.ndarray) -> float:
        """Compute largest singular value (spectral norm)"""
        # Reshape to 2D for SVD
        if len(weight.shape) > 2:
            weight_2d = weight.reshape(weight.shape[0], -1)
        else:
            weight_2d = weight

        try:
            # Compute largest singular value
            u, s, vh = np.linalg.svd(weight_2d, full_matrices=False)
            return s[0]
        except:
            # Fallback to Frobenius norm if SVD fails
            return np.linalg.norm(weight_2d)

    def _build_architecture_graph(self, state_dict: OrderedDict) -> Tuple[np.ndarray, np.ndarray]:
        """
        Build architecture DAG representation.

        Returns:
            node_features: (n_nodes, d_arch) - one node per layer
            edge_index: (2, n_edges) - directed edges between layers
        """
        # Create node for each layer
        nodes = []
        layer_names = []

        for name, param in state_dict.items():
            if len(param.shape) < 2:
                continue

            # Node features: layer type encoding + shape info
            layer_type = self._encode_layer_type(name, param.shape)
            shape_features = self._encode_shape(param.shape)

            node_feature = np.concatenate([layer_type, shape_features])
            nodes.append(node_feature)
            layer_names.append(name)

        # Pad nodes to consistent size (d_arch = 64)
        d_arch = 64
        node_features = []
        for node in nodes:
            if len(node) < d_arch:
                node = np.pad(node, (0, d_arch - len(node)), mode='constant')
            else:
                node = node[:d_arch]
            node_features.append(node)

        node_features = np.array(node_features, dtype=np.float32)  # (n_nodes, d_arch)

        # Build edges (sequential connections)
        n_nodes = len(nodes)
        edges = []
        for i in range(n_nodes - 1):
            edges.append([i, i + 1])  # Forward edge

        if len(edges) == 0:
            # Single node graph
            edges = [[0, 0]]

        edge_index = np.array(edges, dtype=np.int64).T  # (2, n_edges)

        return node_features, edge_index

    def _encode_layer_type(self, name: str, shape: Tuple) -> np.ndarray:
        """One-hot encoding of layer type"""
        # [conv, attn, mlp, other]
        encoding = np.zeros(4, dtype=np.float32)

        if self._is_conv_layer(name, shape):
            encoding[0] = 1.0
        elif self._is_attention_layer(name, shape):
            encoding[1] = 1.0
        elif self._is_mlp_layer(name, shape):
            encoding[2] = 1.0
        else:
            encoding[3] = 1.0

        return encoding

    def _encode_shape(self, shape: Tuple) -> np.ndarray:
        """Encode tensor shape as log-scaled features"""
        # Take log of dimensions for scale-invariance
        shape_features = np.log(np.array(shape, dtype=np.float32) + 1.0)

        # Pad to max 4 dimensions
        if len(shape_features) < 4:
            shape_features = np.pad(
                shape_features,
                (0, 4 - len(shape_features)),
                mode='constant'
            )

        return shape_features[:4]
