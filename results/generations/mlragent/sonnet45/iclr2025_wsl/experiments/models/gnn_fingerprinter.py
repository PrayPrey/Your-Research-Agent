"""
GNN-based permutation-invariant fingerprinting model.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv, global_mean_pool, global_max_pool, global_add_pool
from torch_geometric.data import Data, Batch
import numpy as np
from typing import Dict, List, Tuple

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class GNNLayer(nn.Module):
    """Single GNN layer with message passing."""
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.message_net = nn.Sequential(
            nn.Linear(in_dim * 2, out_dim),
            nn.ReLU(),
            nn.Linear(out_dim, out_dim)
        )
        self.update_net = nn.Sequential(
            nn.Linear(in_dim + out_dim, out_dim),
            nn.LayerNorm(out_dim),
            nn.ReLU()
        )

    def forward(self, x, edge_index, edge_attr):
        row, col = edge_index

        # Aggregate messages
        messages = []
        for i in range(x.size(0)):
            neighbors = col[row == i]
            if len(neighbors) == 0:
                msg = torch.zeros(x.size(1), device=x.device)
            else:
                neighbor_features = x[neighbors]
                node_features = x[i].unsqueeze(0).expand(len(neighbors), -1)
                combined = torch.cat([node_features, neighbor_features], dim=-1)
                msg = self.message_net(combined).mean(dim=0)
            messages.append(msg)

        messages = torch.stack(messages)

        # Update node features
        combined = torch.cat([x, messages], dim=-1)
        x_new = self.update_net(combined)

        return x_new


class AttentionPooling(nn.Module):
    """Self-attention based graph pooling."""
    def __init__(self, dim):
        super().__init__()
        self.attention_net = nn.Sequential(
            nn.Linear(dim, dim),
            nn.Tanh(),
            nn.Linear(dim, 1)
        )

    def forward(self, x, batch):
        # Compute attention weights
        attention_weights = self.attention_net(x)
        attention_weights = torch.softmax(attention_weights, dim=0)

        # Weighted sum
        weighted_x = x * attention_weights

        # Pool by batch
        unique_batches = torch.unique(batch)
        pooled = []
        for b in unique_batches:
            mask = batch == b
            pooled.append(weighted_x[mask].sum(dim=0))

        return torch.stack(pooled)


class GNNFingerprinter(nn.Module):
    """GNN-based model fingerprinting network."""
    def __init__(
        self,
        node_feature_dim,
        edge_feature_dim,
        hidden_dim=128,
        num_layers=4,
        embedding_dim=128,
        pooling='attention'
    ):
        super().__init__()

        self.node_encoder = nn.Sequential(
            nn.Linear(node_feature_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        self.edge_encoder = nn.Sequential(
            nn.Linear(edge_feature_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        # GNN layers
        self.gnn_layers = nn.ModuleList([
            GNNLayer(hidden_dim, hidden_dim)
            for _ in range(num_layers)
        ])

        # Pooling
        self.pooling_type = pooling
        if pooling == 'attention':
            self.attention_pool = AttentionPooling(hidden_dim)

        # Projection head
        self.projection = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim * 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim * 2, embedding_dim)
        )

    def forward(self, data):
        x, edge_index, edge_attr, batch = data.x, data.edge_index, data.edge_attr, data.batch

        # Encode node and edge features
        x = self.node_encoder(x)
        edge_attr = self.edge_encoder(edge_attr)

        # Apply GNN layers
        for gnn_layer in self.gnn_layers:
            x = gnn_layer(x, edge_index, edge_attr)

        # Global pooling
        mean_pool = global_mean_pool(x, batch)
        max_pool = global_max_pool(x, batch)

        if self.pooling_type == 'attention':
            att_pool = self.attention_pool(x, batch)
            pooled = torch.cat([mean_pool, max_pool, att_pool], dim=-1)
        else:
            sum_pool = global_add_pool(x, batch)
            pooled = torch.cat([mean_pool, max_pool, sum_pool], dim=-1)

        # Generate fingerprint
        fingerprint = self.projection(pooled)

        # L2 normalize
        fingerprint = F.normalize(fingerprint, p=2, dim=-1)

        return fingerprint


def model_to_graph(model_state_dict: Dict[str, torch.Tensor], architecture: str) -> Data:
    """Convert a neural network model to a graph representation."""
    nodes = []
    edges = []
    edge_features = []

    node_id = 0
    layer_node_ids = {}

    # Extract layers
    layer_params = {}
    for name, param in model_state_dict.items():
        layer_name = name.split('.')[0]
        if layer_name not in layer_params:
            layer_params[layer_name] = {}
        if 'weight' in name:
            layer_params[layer_name]['weight'] = param
        elif 'bias' in name:
            layer_params[layer_name]['bias'] = param

    prev_layer_nodes = None

    for layer_name, params in layer_params.items():
        if 'weight' not in params:
            continue

        weight = params['weight']
        bias = params.get('bias', None)

        # Handle different layer types
        if len(weight.shape) == 2:  # Linear layer
            out_features, in_features = weight.shape

            # Create nodes for output neurons
            layer_nodes = []
            for i in range(out_features):
                node_feature = [
                    bias[i].item() if bias is not None else 0.0,
                    weight[i].norm().item(),
                    weight[i].mean().item(),
                    weight[i].std().item()
                ]
                nodes.append(node_feature)
                layer_nodes.append(node_id)
                node_id += 1

            # Create edges from previous layer
            if prev_layer_nodes is not None:
                for i, out_node in enumerate(layer_nodes):
                    for j, in_node in enumerate(prev_layer_nodes):
                        if j < weight.shape[1]:
                            edges.append([in_node, out_node])
                            w_val = weight[i, j].item()
                            edge_features.append([
                                w_val,
                                1.0 if w_val > 0 else -1.0,
                                abs(w_val)
                            ])

            prev_layer_nodes = layer_nodes
            layer_node_ids[layer_name] = layer_nodes

        elif len(weight.shape) == 4:  # Conv layer
            out_channels, in_channels, kh, kw = weight.shape

            # Create nodes for output channels
            layer_nodes = []
            for i in range(out_channels):
                node_feature = [
                    bias[i].item() if bias is not None else 0.0,
                    weight[i].norm().item(),
                    weight[i].mean().item(),
                    weight[i].std().item()
                ]
                nodes.append(node_feature)
                layer_nodes.append(node_id)
                node_id += 1

            # Create edges
            if prev_layer_nodes is not None:
                for i, out_node in enumerate(layer_nodes):
                    for j, in_node in enumerate(prev_layer_nodes):
                        if j < in_channels:
                            edges.append([in_node, out_node])
                            w_val = weight[i, j].mean().item()
                            edge_features.append([
                                w_val,
                                1.0 if w_val > 0 else -1.0,
                                abs(w_val)
                            ])

            prev_layer_nodes = layer_nodes
            layer_node_ids[layer_name] = layer_nodes

    # Convert to tensors
    x = torch.tensor(nodes, dtype=torch.float32)
    if len(edges) > 0:
        edge_index = torch.tensor(edges, dtype=torch.long).t()
        edge_attr = torch.tensor(edge_features, dtype=torch.float32)
    else:
        edge_index = torch.zeros((2, 0), dtype=torch.long)
        edge_attr = torch.zeros((0, 3), dtype=torch.float32)

    return Data(x=x, edge_index=edge_index, edge_attr=edge_attr)


if __name__ == "__main__":
    # Test the model
    node_feature_dim = 4
    edge_feature_dim = 3

    model = GNNFingerprinter(
        node_feature_dim=node_feature_dim,
        edge_feature_dim=edge_feature_dim,
        hidden_dim=128,
        num_layers=4,
        embedding_dim=128
    )

    # Create dummy graph data
    x = torch.randn(10, node_feature_dim)
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 3]], dtype=torch.long)
    edge_attr = torch.randn(3, edge_feature_dim)
    batch = torch.zeros(10, dtype=torch.long)

    data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr, batch=batch)

    output = model(data)
    print(f"Output shape: {output.shape}")
    print(f"Output norm: {output.norm(dim=-1)}")
