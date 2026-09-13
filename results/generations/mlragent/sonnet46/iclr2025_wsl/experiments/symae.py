"""
SymAE: Symmetry-Aware Autoencoder for Weight Space Learning.

Key components:
1. GNN-based equivariant encoder treating network weights as bipartite graphs
2. MLP decoder
3. Auxiliary property prediction heads (test accuracy regression)
4. Contrastive loss using permutation-based augmentations
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data, Batch

from model_zoo import HIDDEN_SIZE, INPUT_DIM, OUTPUT_DIM, compute_weight_dim


def build_network_graph(weight_vec, hidden_size=HIDDEN_SIZE):
    """
    Build a graph representation of a 3-layer MLP from its weight vector.
    Architecture: input(3072) -> hidden1(H) -> hidden2(H) -> output(10)

    Node features per hidden neuron: [in_weight_norm, in_weight_mean, in_weight_std,
                                       out_weight_norm, out_weight_mean, bias, layer_id]
    Edges: fully connected between hidden1 and hidden2 (H x H edges)
    Edge features: the actual weight value connecting the two neurons.
    """
    H = hidden_size
    idx = 0
    n_fc1w = H * INPUT_DIM
    n_fc1b = H
    n_fc2w = H * H
    n_fc2b = H
    n_fc3w = OUTPUT_DIM * H
    n_fc3b = OUTPUT_DIM

    fc1_w = weight_vec[idx: idx + n_fc1w].reshape(H, INPUT_DIM); idx += n_fc1w
    fc1_b = weight_vec[idx: idx + n_fc1b]; idx += n_fc1b
    fc2_w = weight_vec[idx: idx + n_fc2w].reshape(H, H); idx += n_fc2w
    fc2_b = weight_vec[idx: idx + n_fc2b]; idx += n_fc2b
    fc3_w = weight_vec[idx: idx + n_fc3w].reshape(OUTPUT_DIM, H); idx += n_fc3w
    fc3_b = weight_vec[idx: idx + n_fc3b]

    # Node features: hidden layer 1 neurons
    node_feats = []
    for i in range(H):
        w_in = fc1_w[i]         # shape: [INPUT_DIM]
        w_out = fc2_w[:, i]     # shape: [H] - outgoing connections
        feat = [
            w_in.norm().item(),
            w_in.mean().item(),
            w_in.std().item() if w_in.numel() > 1 else 0.0,
            w_out.norm().item(),
            w_out.mean().item(),
            fc1_b[i].item(),
            0.0  # layer_id
        ]
        node_feats.append(feat)

    # Node features: hidden layer 2 neurons
    for i in range(H):
        w_in = fc2_w[i]         # shape: [H]
        w_out = fc3_w[:, i]     # shape: [OUTPUT_DIM]
        feat = [
            w_in.norm().item(),
            w_in.mean().item(),
            w_in.std().item() if w_in.numel() > 1 else 0.0,
            w_out.norm().item(),
            w_out.mean().item(),
            fc2_b[i].item(),
            1.0  # layer_id
        ]
        node_feats.append(feat)

    x = torch.tensor(node_feats, dtype=torch.float)  # [2H, 7]

    # Edges: fully connected hidden1 -> hidden2
    src, dst, ew = [], [], []
    for i in range(H):       # hidden1
        for j in range(H):   # hidden2
            src.append(i)
            dst.append(H + j)
            ew.append([fc2_w[j, i].item()])

    edge_index = torch.tensor([src, dst], dtype=torch.long)
    edge_attr = torch.tensor(ew, dtype=torch.float)

    return Data(x=x, edge_index=edge_index, edge_attr=edge_attr)


class GNNEncoder(nn.Module):
    """GNN-based equivariant encoder for weight space graphs."""

    def __init__(self, node_feat_dim=7, edge_feat_dim=1,
                 hidden_dim=64, latent_dim=32, num_layers=3):
        super().__init__()
        self.node_proj = nn.Linear(node_feat_dim, hidden_dim)
        self.edge_proj = nn.Linear(edge_feat_dim, hidden_dim)

        self.convs = nn.ModuleList()
        self.norms = nn.ModuleList()
        for _ in range(num_layers):
            self.convs.append(nn.Sequential(
                nn.Linear(hidden_dim * 2, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, hidden_dim)
            ))
            self.norms.append(nn.LayerNorm(hidden_dim))

        self.readout = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim)
        )

    def forward(self, data):
        x, edge_index, edge_attr, batch = (
            data.x, data.edge_index, data.edge_attr, data.batch
        )

        h = self.node_proj(x)
        e = self.edge_proj(edge_attr)

        for conv, norm in zip(self.convs, self.norms):
            row, col = edge_index
            # Message: source node features weighted by edge features
            msg = h[col] * e
            # Aggregate messages at target nodes
            agg = torch.zeros_like(h)
            agg.index_add_(0, row, msg)
            # Update with residual
            h_new = conv(torch.cat([h, agg], dim=1))
            h = norm(h + h_new)

        # Global mean pooling (permutation-invariant readout)
        # Pool separately for layer 0 and layer 1 neurons, then concat
        N_per_graph = 2 * HIDDEN_SIZE  # 2H nodes per graph
        # Use standard global_mean_pool approach
        z = torch.zeros(batch.max().item() + 1, h.size(1), device=h.device)
        z.index_add_(0, batch, h)
        counts = torch.zeros(batch.max().item() + 1, device=h.device)
        counts.index_add_(0, batch, torch.ones(batch.size(0), device=h.device))
        z = z / counts.unsqueeze(1)

        z = self.readout(z)
        return z


class FlatMLPEncoder(nn.Module):
    """Baseline flat MLP encoder on raw weight vectors."""

    def __init__(self, input_dim, hidden_dim=256, latent_dim=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim)
        )

    def forward(self, x):
        return self.net(x)


class Decoder(nn.Module):
    """MLP decoder from latent code to weight vector."""

    def __init__(self, latent_dim=32, hidden_dim=256, output_dim=None):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, z):
        return self.net(z)


class PropertyHead(nn.Module):
    """Regression head for model property prediction."""

    def __init__(self, latent_dim=32, hidden_dim=64, output_dim=1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, z):
        return self.net(z)


class SymAE(nn.Module):
    """
    SymAE: Symmetry-Aware Autoencoder.
    Uses GNN encoder (equivariant to permutation symmetries) +
    MLP decoder + property prediction + contrastive loss.
    """

    def __init__(self, hidden_size=HIDDEN_SIZE, latent_dim=32,
                 alpha=1.0, beta=0.1):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.hidden_size = hidden_size
        self.weight_dim = compute_weight_dim(hidden_size)

        self.encoder = GNNEncoder(
            node_feat_dim=7,
            edge_feat_dim=1,
            hidden_dim=64,
            latent_dim=latent_dim,
            num_layers=3
        )

        self.decoder = Decoder(
            latent_dim=latent_dim,
            hidden_dim=256,
            output_dim=self.weight_dim
        )

        self.prop_head = PropertyHead(latent_dim=latent_dim, output_dim=1)

    def encode(self, graphs):
        return self.encoder(graphs)

    def decode(self, z):
        return self.decoder(z)

    def predict_property(self, z):
        return self.prop_head(z).squeeze(-1)

    def contrastive_loss(self, z1, z2, temperature=0.1):
        """SimCLR-style contrastive loss between z1 and z2."""
        z1 = F.normalize(z1, dim=1)
        z2 = F.normalize(z2, dim=1)
        z = torch.cat([z1, z2], dim=0)
        N = z1.size(0)

        sim = torch.mm(z, z.t()) / temperature
        mask = torch.eye(2 * N, device=z.device).bool()
        sim.masked_fill_(mask, -1e9)

        labels = torch.cat([torch.arange(N, 2 * N), torch.arange(0, N)]).to(z.device)
        return F.cross_entropy(sim, labels)

    def permute_weights(self, weight_vec):
        """
        Permute neurons in hidden layers to create a functionally equivalent
        but differently-ordered weight vector. Used for contrastive augmentation.
        """
        H = self.hidden_size
        weight_vec = weight_vec.clone()

        n_fc1w = H * INPUT_DIM
        n_fc1b = H
        n_fc2w = H * H
        n_fc2b = H
        n_fc3w = OUTPUT_DIM * H

        idx = 0
        fc1_w = weight_vec[idx: idx + n_fc1w].reshape(H, INPUT_DIM); idx += n_fc1w
        fc1_b = weight_vec[idx: idx + n_fc1b]; idx += n_fc1b
        fc2_w = weight_vec[idx: idx + n_fc2w].reshape(H, H); idx += n_fc2w
        fc2_b = weight_vec[idx: idx + n_fc2b]; idx += n_fc2b
        fc3_w = weight_vec[idx: idx + n_fc3w].reshape(OUTPUT_DIM, H); idx += n_fc3w
        fc3_b = weight_vec[idx:]

        # Permute hidden layer 1
        perm1 = torch.randperm(H, device=weight_vec.device)
        fc1_w = fc1_w[perm1]
        fc1_b = fc1_b[perm1]
        fc2_w = fc2_w[:, perm1]

        # Permute hidden layer 2
        perm2 = torch.randperm(H, device=weight_vec.device)
        fc2_w = fc2_w[perm2]
        fc2_b = fc2_b[perm2]
        fc3_w = fc3_w[:, perm2]

        return torch.cat([
            fc1_w.flatten(), fc1_b,
            fc2_w.flatten(), fc2_b,
            fc3_w.flatten(), fc3_b
        ])


class FlatMLPAutoencoder(nn.Module):
    """Baseline: Flat MLP Autoencoder on raw weight vectors."""

    def __init__(self, weight_dim, latent_dim=32, hidden_dim=256, alpha=1.0):
        super().__init__()
        self.alpha = alpha
        self.encoder = FlatMLPEncoder(weight_dim, hidden_dim=hidden_dim, latent_dim=latent_dim)
        self.decoder = Decoder(latent_dim=latent_dim, hidden_dim=hidden_dim, output_dim=weight_dim)
        self.prop_head = PropertyHead(latent_dim=latent_dim, output_dim=1)

    def encode(self, x):
        return self.encoder(x)

    def decode(self, z):
        return self.decoder(z)

    def predict_property(self, z):
        return self.prop_head(z).squeeze(-1)
