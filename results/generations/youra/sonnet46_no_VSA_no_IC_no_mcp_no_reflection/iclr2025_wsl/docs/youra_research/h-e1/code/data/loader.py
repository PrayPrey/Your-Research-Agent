from dataclasses import dataclass
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader


@dataclass
class ZooData:
    weights: np.ndarray      # [N, D] flat weights
    gap: np.ndarray          # [N]
    train_acc: np.ndarray    # [N]
    test_acc: np.ndarray     # [N]
    idx_train: np.ndarray
    idx_val: np.ndarray
    idx_test: np.ndarray
    weight_shapes: list      # list of (fan_in, fan_out) per layer (2D only)
    layer_sizes: list        # flat size per param tensor


class WeightDataset(Dataset):
    def __init__(self, zoo: ZooData, indices: np.ndarray, encoder_type: str = "flat"):
        self.weights = zoo.weights[indices]   # [N_split, D]
        self.gap = zoo.gap[indices].astype(np.float32)
        self.encoder_type = encoder_type
        self.weight_shapes = zoo.weight_shapes
        self.layer_sizes = zoo.layer_sizes

    def __len__(self):
        return len(self.gap)

    def __getitem__(self, idx):
        w_flat = torch.from_numpy(self.weights[idx])  # [D]
        g = torch.tensor(self.gap[idx])
        return w_flat, g


def load_zoo(path: str, idx_train=None, idx_val=None, idx_test=None, seed=42) -> ZooData:
    data = np.load(path)
    weights = data["weights"].astype(np.float32)  # [N, D]
    train_acc = data["train_acc"].astype(np.float32)
    test_acc = data["test_acc"].astype(np.float32)
    gap = (train_acc - test_acc).astype(np.float32)
    N = len(gap)

    if idx_train is None:
        rng = np.random.RandomState(seed)
        idx = rng.permutation(N)
        n_train = int(0.8 * N)
        n_val = int(0.1 * N)
        idx_train = idx[:n_train]
        idx_val = idx[n_train:n_train + n_val]
        idx_test = idx[n_train + n_val:]

    # Build weight_shapes from param sizes stored in npz (or infer from D)
    # We store layer boundary info if present, else treat as single flat layer
    if "layer_sizes" in data:
        layer_sizes = list(data["layer_sizes"])
    else:
        layer_sizes = [weights.shape[1]]

    # Build (fan_in, fan_out) shapes for 2D layers only (skip bias)
    if "weight_shapes" in data:
        weight_shapes = [tuple(s) for s in data["weight_shapes"]]
    else:
        weight_shapes = []

    return ZooData(
        weights=weights,
        gap=gap,
        train_acc=train_acc,
        test_acc=test_acc,
        idx_train=idx_train,
        idx_val=idx_val,
        idx_test=idx_test,
        weight_shapes=weight_shapes,
        layer_sizes=layer_sizes,
    )


def make_loader(zoo: ZooData, split: str, batch_size: int, shuffle: bool = True,
                encoder_type: str = "flat", num_workers: int = 0) -> DataLoader:
    idx = {"train": zoo.idx_train, "val": zoo.idx_val, "test": zoo.idx_test}[split]
    dataset = WeightDataset(zoo, idx, encoder_type=encoder_type)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle,
                      num_workers=num_workers, pin_memory=False)
