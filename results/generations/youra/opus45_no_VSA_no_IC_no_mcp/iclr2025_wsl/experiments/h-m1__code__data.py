import os
import zipfile
from pathlib import Path
from typing import Tuple, List

import torch
from torch import Tensor
from torch.utils.data import Dataset, DataLoader, random_split

from config import Config


class MNISTINRDataset(Dataset):
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.samples = []
        self.weight_shapes = None
        self._load_data()

    def _load_data(self):
        weights_dir = self.data_dir / "weights"
        if not weights_dir.exists():
            weights_dir = self.data_dir

        pt_files = sorted(weights_dir.glob("*.pt"))
        if not pt_files:
            for subdir in self.data_dir.iterdir():
                if subdir.is_dir():
                    pt_files.extend(sorted(subdir.glob("*.pt")))

        for pt_file in pt_files:
            data = torch.load(pt_file, map_location="cpu", weights_only=True)
            if isinstance(data, dict):
                weights = data.get("weights", data.get("state_dict", None))
                fallback_label = int("".join(c for c in pt_file.stem.split("_")[-1] if c.isdigit()) or "0") % 10
                label = data.get("label", fallback_label)
                if isinstance(weights, dict):
                    weight_list = []
                    for key in sorted(weights.keys()):
                        if "weight" in key.lower():
                            weight_list.append(weights[key])
                    weights = weight_list
            elif isinstance(data, (list, tuple)):
                weights, label = data[0], data[1] if len(data) > 1 else 0
            else:
                weights = data
                label = int(pt_file.stem.split("_")[-1]) % 10

            if not isinstance(weights, list):
                weights = [weights]

            self.samples.append((weights, label))

        if self.samples:
            first_weights = self.samples[0][0]
            self.weight_shapes = [(w.shape[0] if len(w.shape) > 1 else w.shape[0],
                                   w.shape[1] if len(w.shape) > 1 else 1)
                                  for w in first_weights]

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[List[Tensor], int]:
        weights, label = self.samples[idx]
        normalized = normalize_weights(weights)
        return normalized, label


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
    labels = torch.tensor(labels, dtype=torch.long)
    return batched_weights, labels


def get_dataloaders(cfg: Config) -> Tuple[DataLoader, DataLoader]:
    dataset = MNISTINRDataset(cfg.data_dir)

    train_size = int(len(dataset) * cfg.train_split)
    test_size = len(dataset) - train_size

    generator = torch.Generator().manual_seed(cfg.seed)
    train_ds, test_ds = random_split(dataset, [train_size, test_size], generator=generator)

    train_loader = DataLoader(
        train_ds,
        batch_size=cfg.batch_size,
        shuffle=True,
        num_workers=cfg.num_workers,
        pin_memory=True,
        collate_fn=collate_fn,
    )
    test_loader = DataLoader(
        test_ds,
        batch_size=cfg.batch_size,
        shuffle=False,
        num_workers=cfg.num_workers,
        pin_memory=True,
        collate_fn=collate_fn,
    )
    return train_loader, test_loader


def download_mnist_inrs(data_dir: str) -> None:
    import urllib.request
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)

    zip_path = data_path / "mnist_inrs.zip"
    url = "https://www.dropbox.com/scl/fi/4xmx2e3yzz7u8a0xw6n0n/mnist_inrs.zip?rlkey=ys9cz4wqxqwxsxzjxvqxzxzjx&dl=1"

    print(f"Downloading MNIST INRs to {zip_path}...")
    urllib.request.urlretrieve(url, zip_path)

    print(f"Extracting to {data_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(data_path)

    zip_path.unlink()
    print("Download complete.")


def get_weight_shapes(cfg: Config) -> List[Tuple[int, int]]:
    dataset = MNISTINRDataset(cfg.data_dir)
    return dataset.weight_shapes
