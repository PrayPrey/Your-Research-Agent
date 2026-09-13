from typing import List, Tuple
import torch
from torch import Tensor
from torch.utils.data import Dataset, DataLoader


def normalize_weights(weight_list: List[Tensor]) -> List[Tensor]:
    normalized = []
    for w in weight_list:
        w_flat = w.flatten()
        mean, std = w_flat.mean(), w_flat.std()
        if std > 1e-8:
            w_norm = (w - mean) / std
        else:
            w_norm = w - mean
        normalized.append(w_norm)
    return normalized


def collate_fn(batch):
    weight_lists, labels = zip(*batch)
    num_layers = len(weight_lists[0])
    batched_weights = []
    for layer_idx in range(num_layers):
        layer_weights = torch.stack([wl[layer_idx] for wl in weight_lists], dim=0)
        batched_weights.append(layer_weights)
    if isinstance(labels[0], (int, float)):
        if isinstance(labels[0], int):
            labels = torch.tensor(labels, dtype=torch.long)
        else:
            labels = torch.tensor(labels, dtype=torch.float32)
    else:
        labels = torch.tensor(labels, dtype=torch.float32)
    return batched_weights, labels


def default_weight_shapes(hidden_dim: int = 128, n_layers: int = 4) -> List[Tuple[int, int]]:
    shapes = [
        (32, hidden_dim),
        (hidden_dim, hidden_dim),
        (hidden_dim, hidden_dim),
        (hidden_dim, 10),
    ]
    return shapes[:n_layers]


def make_backdoor_dataset(n: int, weight_shapes: List[Tuple[int, int]], seed: int) -> Tuple[List[List[Tensor]], List[int]]:
    rng = torch.Generator().manual_seed(seed)
    weight_lists = []
    labels = []

    for i in range(n):
        weights = [torch.randn(in_c, out_c, generator=rng) for (in_c, out_c) in weight_shapes]
        label = i % 2

        if label == 1:
            layer_idx = torch.randint(0, len(weight_shapes), (1,), generator=rng).item()
            row = torch.randint(0, weight_shapes[layer_idx][0], (1,), generator=rng).item()
            perturbation = 5.0 * torch.randn(weight_shapes[layer_idx][1], generator=rng)
            weights[layer_idx][row, :] += perturbation

        weight_lists.append(normalize_weights(weights))
        labels.append(label)

    perm = torch.randperm(n, generator=rng).tolist()
    weight_lists = [weight_lists[i] for i in perm]
    labels = [labels[i] for i in perm]

    return weight_lists, labels


def make_accuracy_dataset(n: int, weight_shapes: List[Tuple[int, int]], seed: int) -> Tuple[List[List[Tensor]], List[float]]:
    rng = torch.Generator().manual_seed(seed)
    weight_lists = []
    targets = []

    for i in range(n):
        scale = 0.5 + 2.0 * torch.rand(1, generator=rng).item()
        weights = [scale * torch.randn(in_c, out_c, generator=rng) for (in_c, out_c) in weight_shapes]

        global_norm = sum(w.norm().item() for w in weights) / len(weights)
        global_mean = sum(w.mean().item() for w in weights) / len(weights)

        raw_target = 0.3 * global_norm + 0.1 * global_mean
        target = torch.sigmoid(torch.tensor(raw_target)).item() * 100 + 2.0 * torch.randn(1, generator=rng).item()

        weight_lists.append(normalize_weights(weights))
        targets.append(target)

    return weight_lists, targets


class WeightDataset(Dataset):
    def __init__(self, weight_lists: List[List[Tensor]], labels: List):
        self.weight_lists = weight_lists
        self.labels = labels

    def __len__(self) -> int:
        return len(self.weight_lists)

    def __getitem__(self, idx: int):
        return self.weight_lists[idx], self.labels[idx]


def build_dataloader(weight_lists: List[List[Tensor]], labels: List, batch_size: int, shuffle: bool) -> DataLoader:
    dataset = WeightDataset(weight_lists, labels)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, collate_fn=collate_fn)
