"""
Converts MLP/CNN model checkpoints to PyG Data objects.
All architectures share the same graph schema: node=bias scalar, edge=weight scalar.
"""
import os
import glob
import json
import torch
import numpy as np
from torch_geometric.data import Dataset, Data


def checkpoint_to_graph(state_dict: dict) -> Data:
    """Convert a PyTorch state_dict to a PyG Data object.

    Builds a sequential layer graph: each layer is one node, with edges between
    consecutive layers. Node features = per-layer weight statistics (mean, std, norm).
    Edge features = weight matrix summary statistics between adjacent layers.
    This handles CNNs, MLPs, and ViTs uniformly (architecture-agnostic).

    For the H-E1 hypothesis: the graph structure (layers connected sequentially)
    plus scale-normalized statistics provide an architecture-agnostic representation
    that should generalize across MLP/CNN/ViT model types.
    """
    # Parse weight tensors by layer order
    weight_tensors = []
    bias_tensors = []

    # Group by layer index
    layer_data = {}
    for key, tensor in state_dict.items():
        parts = key.replace('module_list.', '').replace('layers.', '').split('.')
        for p in parts:
            if p.isdigit():
                idx = int(p)
                param_type = parts[-1]
                if idx not in layer_data:
                    layer_data[idx] = {}
                layer_data[idx][param_type] = tensor.float()
                break

    # Sort layers
    layer_keys = sorted([k for k, v in layer_data.items() if 'weight' in v])
    if len(layer_keys) == 0:
        return Data(
            x=torch.zeros(2, 4),
            edge_index=torch.tensor([[0], [1]], dtype=torch.long),
            edge_attr=torch.zeros(1, 4),
            structure={'n_layers': 1, 'layer_sizes': [1]}
        )

    # Build per-layer node features: [mean, std, l2_norm, max_abs]
    node_feats = []
    layer_sizes = []
    for idx in layer_keys:
        w = layer_data[idx]['weight'].reshape(-1).float()
        b = layer_data[idx].get('bias', torch.zeros(layer_data[idx]['weight'].shape[0])).reshape(-1).float()
        all_params = torch.cat([w, b])
        feats = torch.tensor([
            all_params.mean().item(),
            all_params.std().item() if len(all_params) > 1 else 0.0,
            all_params.norm().item(),
            all_params.abs().max().item(),
        ])
        node_feats.append(feats)
        layer_sizes.append(layer_data[idx]['weight'].shape[0])  # out_dim

    x = torch.stack(node_feats, dim=0)  # (n_layers, 4)
    n_layers = len(layer_keys)

    # Build sequential edges: layer i → layer i+1
    edge_index_list = []
    edge_attr_list = []

    for i in range(n_layers - 1):
        # Edge features: weight statistics of transition between layers i and i+1
        w_i = layer_data[layer_keys[i]]['weight'].reshape(-1).float()
        w_next = layer_data[layer_keys[i + 1]]['weight'].reshape(-1).float()
        # Cross-layer statistics
        edge_feat = torch.tensor([
            w_i.mean().item(),
            w_next.mean().item(),
            (w_i.norm() * w_next.norm()).sqrt().item(),  # geometric mean of norms
            (w_i.std() + w_next.std()).item() / 2,
        ])
        edge_index_list.append(torch.tensor([[i], [i + 1]], dtype=torch.long))
        edge_attr_list.append(edge_feat.unsqueeze(0))

    # Also add self-loops for node features to flow
    for i in range(n_layers):
        edge_index_list.append(torch.tensor([[i], [i]], dtype=torch.long))
        edge_attr_list.append(torch.zeros(1, 4))

    edge_index = torch.cat(edge_index_list, dim=1)
    edge_attr = torch.cat(edge_attr_list, dim=0)

    structure = {
        'n_layers': n_layers,
        'layer_sizes': layer_sizes,
        'layers': layer_sizes,
        'offsets': list(range(n_layers))
    }

    return Data(x=x, edge_index=edge_index, edge_attr=edge_attr, structure=structure)


def _scale_normalize_state_dict(state_dict: dict) -> dict:
    """Per-layer L2 normalization of weights for scale equivariance baseline."""
    out = {}
    for k, v in state_dict.items():
        if 'weight' in k:
            norm = v.norm() + 1e-8
            out[k] = v / norm
        else:
            out[k] = v
    return out


class MultiZooGraphDataset(Dataset):
    """Loads MLP/CNN checkpoints from a modelzoos-format directory and converts to graphs."""

    def __init__(self, root: str, max_models: int = None, normalize: bool = True,
                 split: str = 'train', val_fraction: float = 0.1, seed: int = 0):
        self.root_dir = root
        self.normalize = normalize
        self.split = split
        self.val_fraction = val_fraction
        self._seed = seed

        # Find all checkpoint files
        self._checkpoint_paths = self._discover_checkpoints(root)

        if max_models is not None:
            rng = np.random.RandomState(seed)
            idxs = rng.choice(len(self._checkpoint_paths), min(max_models, len(self._checkpoint_paths)), replace=False)
            self._checkpoint_paths = [self._checkpoint_paths[i] for i in sorted(idxs)]

        # Train/val split
        n_total = len(self._checkpoint_paths)
        n_val = max(1, int(n_total * val_fraction))
        rng = np.random.RandomState(seed + 42)
        idxs = rng.permutation(n_total)
        if split == 'val':
            self._checkpoint_paths = [self._checkpoint_paths[i] for i in idxs[:n_val]]
        else:
            self._checkpoint_paths = [self._checkpoint_paths[i] for i in idxs[n_val:]]

        super().__init__()

    def _discover_checkpoints(self, root):
        """Find checkpoint files in modelzoos directory structure."""
        paths = []
        # Pattern: root/model_dir/checkpoint_XXXXX/checkpoints
        for p in glob.glob(os.path.join(root, '**/checkpoints'), recursive=True):
            if os.path.isfile(p):
                paths.append(p)
        # Also look for .pt and .pth files
        for ext in ['*.pt', '*.pth']:
            for p in glob.glob(os.path.join(root, '**', ext), recursive=True):
                paths.append(p)
        return sorted(list(set(paths)))

    def len(self) -> int:
        return len(self._checkpoint_paths)

    def get(self, idx: int) -> Data:
        path = self._checkpoint_paths[idx]
        try:
            state_dict = torch.load(path, weights_only=False, map_location='cpu')
            if not isinstance(state_dict, dict):
                state_dict = state_dict.state_dict() if hasattr(state_dict, 'state_dict') else {}
            if self.normalize:
                state_dict = _scale_normalize_state_dict(state_dict)
            graph = checkpoint_to_graph(state_dict)
            graph.path = path
            return graph
        except Exception:
            # Return minimal valid graph on error
            return Data(
                x=torch.zeros(2, 1),
                edge_index=torch.tensor([[0], [1]], dtype=torch.long),
                edge_attr=torch.zeros(1, 1),
                structure={'layers': [1, 1], 'offsets': [0, 1]}
            )
