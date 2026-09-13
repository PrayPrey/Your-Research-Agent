"""
Augmentations for contrastive SSL on neural network layer-graph representations.

Since we use layer-level nodes (each node = one layer of the network, with
weight statistics as features), augmentations add noise to statistics rather
than permuting neurons. This is scale+noise invariant: the encoder must learn
representations robust to weight scaling and Gaussian noise.
"""
import torch
from torch_geometric.data import Data
import copy


def scale_augment(graph: Data, alpha: torch.Tensor = None,
                  alpha_range: tuple = (0.5, 2.0)) -> Data:
    """
    Scale augmentation: multiply node weight statistics by a random scale factor.
    Simulates the effect of neuron rescaling on layer-level statistics.
    """
    x = graph.x.clone().float()
    edge_attr = graph.edge_attr.clone().float()
    n_layers = x.shape[0]

    if alpha is None:
        log_lo = torch.tensor(alpha_range[0]).log()
        log_hi = torch.tensor(alpha_range[1]).log()
        alpha = torch.exp(torch.FloatTensor(n_layers).uniform_(log_lo.item(), log_hi.item()))

    # Scale node features (weight statistics) by per-layer scale factor
    # This simulates monomial group action on layer statistics
    for i in range(n_layers):
        a = alpha[i].item()
        # mean and norm scale with alpha; std scales too; max_abs scales
        x[i, 0] *= a   # mean
        x[i, 1] *= a   # std
        x[i, 2] *= a   # l2_norm
        x[i, 3] *= a   # max_abs

    new_graph = Data(
        x=x,
        edge_index=graph.edge_index.clone(),
        edge_attr=edge_attr,
        structure=graph.structure
    )
    return new_graph


def perm_augment(graph: Data) -> Data:
    """
    Noise augmentation: add small Gaussian noise to weight statistics.
    Simulates augmentation diversity (different random seeds of the same architecture).
    """
    x = graph.x.clone().float()
    edge_attr = graph.edge_attr.clone().float()

    # Add small noise to statistics (1% of their magnitude)
    noise_x = torch.randn_like(x) * 0.01 * x.abs().clamp(min=1e-6)
    noise_e = torch.randn_like(edge_attr) * 0.01 * edge_attr.abs().clamp(min=1e-6)
    x = x + noise_x
    edge_attr = edge_attr + noise_e

    new_graph = Data(
        x=x,
        edge_index=graph.edge_index.clone(),
        edge_attr=edge_attr,
        structure=graph.structure
    )
    return new_graph


def make_positive_pair(graph: Data, scale_alpha_range: tuple = (0.5, 2.0)) -> tuple:
    """Return two independently augmented views of the same graph."""
    view_a = perm_augment(scale_augment(graph, alpha=None, alpha_range=scale_alpha_range))
    view_b = perm_augment(scale_augment(graph, alpha=None, alpha_range=scale_alpha_range))
    return view_a, view_b
