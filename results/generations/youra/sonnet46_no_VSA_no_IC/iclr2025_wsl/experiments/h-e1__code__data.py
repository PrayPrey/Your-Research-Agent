"""Data pipeline: load ModelZooDataset, diversity check, subsampling, loaders."""
import sys
import os
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset, Subset
from torch import Tensor

import config

sys.path.insert(0, config.MZDATASET_CODE_PATH)


class ZooDataset(Dataset):
    """Wraps ModelZooDataset split into a torch Dataset returning (weights, target)."""

    def __init__(self, mz_dataset, zoo_arch: str = "cnn"):
        self.mz = mz_dataset
        self.zoo_arch = zoo_arch
        # Cache all test_acc values (final epoch per model)
        test_acc_list = mz_dataset.properties.get("test_acc", [])
        # properties['test_acc'] is a flat list: each model has epoch_lst values
        epoch_lst = mz_dataset.epoch_lst
        n_models = len(mz_dataset)
        # Reshape: (n_models, epoch_lst) → take last epoch
        if len(test_acc_list) == n_models * epoch_lst:
            arr = np.array(test_acc_list).reshape(n_models, epoch_lst)
            self.targets = torch.tensor(arr[:, -1], dtype=torch.float32)
        elif len(test_acc_list) == n_models:
            self.targets = torch.tensor(test_acc_list, dtype=torch.float32)
        else:
            # Fallback: try last value per stride
            stride = max(1, len(test_acc_list) // n_models)
            self.targets = torch.tensor(
                [test_acc_list[i * stride + stride - 1] for i in range(n_models)],
                dtype=torch.float32
            )

    def __len__(self):
        return len(self.mz)

    def __getitem__(self, idx):
        state_dict = self.mz[idx]
        target = self.targets[idx]
        return state_dict, target


def load_zoo(zoo_name: str) -> tuple:
    """Load train/val/test splits from .pt file. Returns (train, val, test) ZooDatasets."""
    path = config.ZOO_PATHS[zoo_name]
    data = torch.load(path, map_location="cpu", weights_only=False)
    zoo_arch = detect_zoo_arch(data["trainset"][0])
    train_ds = ZooDataset(data["trainset"], zoo_arch)
    val_ds = ZooDataset(data["valset"], zoo_arch)
    test_ds = ZooDataset(data["testset"], zoo_arch)
    return train_ds, val_ds, test_ds


def detect_zoo_arch(state_dict: dict) -> str:
    """Detect 'mlp' or 'cnn' from a sample state_dict."""
    for key, val in state_dict.items():
        if isinstance(val, Tensor) and val.dim() == 4:
            return "cnn"
    return "mlp"


def diversity_check(dataset: ZooDataset) -> dict:
    """Return variance and pass/fail. Passes if variance >= 0.05."""
    accs = dataset.targets.numpy()
    variance = float(np.var(accs))
    mean = float(np.mean(accs))
    passed = variance >= 0.05
    if not passed:
        print(f"  ⚠ Diversity check FAILED: variance={variance:.4f} < 0.05")
    else:
        print(f"  ✓ Diversity check passed: mean={mean:.3f} var={variance:.4f}")
    return {"mean": mean, "variance": variance, "passed": passed, "accs": accs.tolist()}


def subsample(dataset: ZooDataset, n, seed: int = 42) -> ZooDataset:
    """Subsample dataset. n='full' returns unchanged."""
    if n == "full" or n >= len(dataset):
        return dataset
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(dataset), size=n, replace=False)
    subset = Subset(dataset, idx.tolist())
    # Wrap so Subset has targets attr
    subset.targets = dataset.targets[idx]
    subset.zoo_arch = dataset.zoo_arch
    return subset


def _extract_structured(state_dict: dict):
    """Extract (weights, biases) as lists of tensors from state_dict."""
    weights, biases = [], []
    # Sort keys to maintain layer order
    weight_keys = sorted([k for k in state_dict if 'weight' in k])
    for wk in weight_keys:
        bk = wk.replace('weight', 'bias')
        w = state_dict[wk]
        b = state_dict.get(bk, torch.zeros(w.shape[0]))
        weights.append(w)
        biases.append(b)
    return weights, biases


def _flatten_state_dict(state_dict: dict) -> Tensor:
    """Flatten all weights+biases into 1D vector."""
    parts = []
    for key in sorted(state_dict.keys()):
        parts.append(state_dict[key].flatten())
    return torch.cat(parts)


class FlatCollator:
    """Collate state_dicts into flat (B, D) tensor + scalar targets."""
    def __init__(self, scaler=None):
        self.scaler = scaler  # (mean, std) for standardization

    def __call__(self, batch):
        flat_list, targets = [], []
        for sd, t in batch:
            flat_list.append(_flatten_state_dict(sd))
            targets.append(t)
        X = torch.stack(flat_list)  # (B, D)
        if self.scaler is not None:
            mean, std = self.scaler
            X = (X - mean) / (std + 1e-8)
        return X, torch.stack(targets)


def _to_wsfeat(state_dict_batch: list):
    """Convert batch of state_dicts to WeightSpaceFeatures for NFN.

    state_dict_to_tensors returns (weights, biases) where each weight is
    (1, out, in) for linear or (1, out, in, kH, kW) for conv layers.
    NFN expects (batch, out, in) for linear (dim=4) or (batch, ch, out, in, kH, kW)
    for conv (dim=6). We add a channels dim for conv layers.
    """
    from nfn.common import state_dict_to_tensors, WeightSpaceFeatures
    import torch
    all_w_lists, all_b_lists = [], []
    for sd in state_dict_batch:
        w_list, b_list = state_dict_to_tensors(sd)
        all_w_lists.append(w_list)
        all_b_lists.append(b_list)

    n_layers = len(all_w_lists[0])
    batched_w = []
    batched_b = []

    for i in range(n_layers):
        w_samples = [all_w_lists[b][i] for b in range(len(state_dict_batch))]
        b_samples = [all_b_lists[b][i] for b in range(len(state_dict_batch))]

        w0 = w_samples[0]  # (1, out, in) or (1, out, in, kH, kW)
        if w0.dim() == 5:
            # Conv: (1, out, in, kH, kW) → add channel dim → (1, 1, out, in, kH, kW)
            # Then cat along batch dim → (B, 1, out, in, kH, kW) = 6D
            w_stacked = torch.cat([w.unsqueeze(1) for w in w_samples], dim=0)
        else:
            # Linear: (1, out, in) → cat → (B, out, in) = 3D; NFN needs (B, ch, out, in) = 4D
            # Add channel dim
            w_stacked = torch.cat([w.unsqueeze(1) for w in w_samples], dim=0)

        b0 = b_samples[0]  # (1, n_out) or (1, out, kH, kW)
        if b0.dim() == 2:
            # Linear bias: (1, n_out) → (B, 1, n_out) → 3D; NFN expects (B, ch, n_out) = 3D
            b_stacked = torch.cat([b.unsqueeze(1) for b in b_samples], dim=0)
        else:
            b_stacked = torch.cat([b.unsqueeze(1) for b in b_samples], dim=0)

        batched_w.append(w_stacked)
        batched_b.append(b_stacked)

    return WeightSpaceFeatures(tuple(batched_w), tuple(batched_b))


class NFNCollator:
    """Collate state_dicts into WeightSpaceFeatures for NFN."""
    def __call__(self, batch):
        sds, targets = zip(*batch)
        wsfeat = _to_wsfeat(list(sds))
        return wsfeat, torch.stack(list(targets))


class GNNCollator:
    """Collate state_dicts into PyG Batch for GNN-NFN."""
    def __call__(self, batch):
        from torch_geometric.data import Data, Batch
        sds, targets = zip(*batch)
        graphs = [state_dict_to_graph(sd) for sd in sds]
        pyg_batch = Batch.from_data_list(graphs)
        return pyg_batch, torch.stack(list(targets))


def state_dict_to_graph(state_dict: dict):
    """Convert zoo model state_dict to PyG Data (nodes=neurons, edges=weights)."""
    from torch_geometric.data import Data
    node_feats, edge_indices, edge_feats = [], [], []
    node_offset = 0

    weight_keys = sorted([k for k in state_dict if 'weight' in k])
    bias_dict = {k.replace('weight', 'bias'): v for k, v in state_dict.items() if 'bias' in k}

    for i, wk in enumerate(weight_keys):
        bk = wk.replace('weight', 'bias')
        W = state_dict[wk]
        b = bias_dict.get(bk, torch.zeros(W.shape[0]))

        # Flatten conv filters to 2D (n_out, n_in_flat)
        if W.dim() == 4:
            n_out = W.shape[0]
            W_2d = W.reshape(n_out, -1)
        else:
            n_out = W.shape[0]
            W_2d = W

        n_in = W_2d.shape[1]

        # Nodes: output neurons of this layer, feature = bias
        node_feats.append(b.unsqueeze(-1).float())  # (n_out, 1)

        if i > 0:
            # Edges: every input neuron → every output neuron
            prev_offset = node_offset - prev_n_out
            src = torch.arange(prev_offset, node_offset).repeat_interleave(n_out)
            dst = torch.arange(node_offset, node_offset + n_out).repeat(prev_n_out)
            # Use mean weight per connection (for conv: average over spatial)
            w_vals = W_2d[:, :prev_n_out].T if W_2d.shape[1] >= prev_n_out else W_2d.T
            # Simpler: just use flattened W row-mean per output neuron × input neuron pair
            # For simplicity: one edge per (in, out) pair with scalar weight value
            # Recompute: edges from last layer's neurons to this layer's neurons
            src2 = torch.arange(node_offset - prev_n_out, node_offset).repeat_interleave(n_out)
            dst2 = torch.arange(node_offset, node_offset + n_out).repeat(prev_n_out)
            # Edge feature: mean weight (handles conv where n_in != prev_n_out due to spatial)
            # Use W reshaped to (n_out, prev_n_out) via average over remaining dims
            W_avg = W.reshape(n_out, -1).mean(dim=1, keepdim=True)  # (n_out, 1)
            # One edge per out node from all prev nodes (simplified)
            edge_w = W_avg.expand(n_out, prev_n_out).reshape(-1).unsqueeze(-1)  # (n_out*prev_n_out, 1)
            edge_indices.append(torch.stack([src2, dst2]))
            edge_feats.append(edge_w.float())

        prev_n_out = n_out
        node_offset += n_out

    x = torch.cat(node_feats, dim=0)
    if edge_indices:
        edge_index = torch.cat(edge_indices, dim=1)
        edge_attr = torch.cat(edge_feats, dim=0)
    else:
        edge_index = torch.zeros(2, 0, dtype=torch.long)
        edge_attr = torch.zeros(0, 1)

    return Data(x=x, edge_index=edge_index, edge_attr=edge_attr)


def compute_flat_scaler(dataset) -> tuple:
    """Compute mean/std over training set for flat standardization."""
    flat_vecs = []
    for i in range(min(1000, len(dataset))):
        sd, _ = dataset[i]
        flat_vecs.append(_flatten_state_dict(sd))
    X = torch.stack(flat_vecs)
    return X.mean(dim=0), X.std(dim=0)


def make_flat_loader(dataset, batch_size: int, shuffle: bool, scaler=None) -> DataLoader:
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle,
                      collate_fn=FlatCollator(scaler), num_workers=0)


def make_nfn_loader(dataset, batch_size: int, shuffle: bool) -> DataLoader:
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle,
                      collate_fn=NFNCollator(), num_workers=0)


def make_gnn_loader(dataset, batch_size: int, shuffle: bool) -> DataLoader:
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle,
                      collate_fn=GNNCollator(), num_workers=0)
