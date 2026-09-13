"""Data acquisition and loading for Model Zoo."""
import os
from pathlib import Path
from typing import Tuple, List
import torch
import torch.nn as nn
from tqdm import tqdm
import numpy as np

ZOO_DIR = "data/model_zoo"
TEST_SIZE = 500
SPLIT_SEED = 42


class ResNet20(nn.Module):
    """Simplified ResNet-20 for CIFAR-10."""
    def __init__(self, num_classes=10):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(16)
        self.relu = nn.ReLU(inplace=True)

        self.layer1 = self._make_layer(16, 16, 3)
        self.layer2 = self._make_layer(16, 32, 3, stride=2)
        self.layer3 = self._make_layer(32, 64, 3, stride=2)

        self.avgpool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(64, num_classes)

    def _make_layer(self, in_ch, out_ch, blocks, stride=1):
        layers = []
        layers.append(nn.Conv2d(in_ch, out_ch, 3, stride, 1, bias=False))
        layers.append(nn.BatchNorm2d(out_ch))
        layers.append(nn.ReLU(inplace=True))
        for _ in range(1, blocks):
            layers.append(nn.Conv2d(out_ch, out_ch, 3, 1, 1, bias=False))
            layers.append(nn.BatchNorm2d(out_ch))
            layers.append(nn.ReLU(inplace=True))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)


def generate_model_zoo(n_models: int = 6000, dest_dir: str = ZOO_DIR) -> str:
    """Generate synthetic model zoo by perturbing base weights."""
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    cache_file = dest / f"synthetic_zoo_{n_models}.pt"
    if cache_file.exists():
        print(f"Loading cached synthetic zoo from {cache_file}")
        return str(cache_file)

    print(f"Generating {n_models} synthetic models...")

    base_model = ResNet20()
    base_state = base_model.state_dict()

    items = []
    rng = np.random.RandomState(42)

    for i in tqdm(range(n_models)):
        accuracy = rng.uniform(0.70, 0.95)
        noise_scale = (0.95 - accuracy) * 0.5 + 0.01

        new_state = {}
        for name, param in base_state.items():
            if 'weight' in name:
                noise = torch.randn_like(param) * noise_scale
                new_state[name] = param + noise
            else:
                new_state[name] = param.clone()

        items.append((new_state, accuracy))

    torch.save(items, cache_file)
    print(f"Saved synthetic zoo to {cache_file}")
    return str(cache_file)


def download_model_zoo(dest_dir: str = ZOO_DIR) -> str:
    """Download or generate Model Zoo."""
    return generate_model_zoo(n_models=6000, dest_dir=dest_dir)


def load_checkpoints(zoo_path: str) -> List[Tuple[dict, float]]:
    """Load state_dicts and accuracy labels from zoo file."""
    path = Path(zoo_path)

    if path.suffix == '.pt':
        items = torch.load(path, map_location='cpu')
        print(f"Loaded {len(items)} checkpoints from {path}")
        return items

    items = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.pt') or f.endswith('.pth'):
                pt_path = Path(root) / f
                data = torch.load(pt_path, map_location='cpu')
                if isinstance(data, list):
                    items.extend(data)

    print(f"Loaded {len(items)} checkpoints with accuracy labels.")
    return items


def split_test_set(
    items: List[Tuple[dict, float]],
    test_size: int = TEST_SIZE,
    seed: int = SPLIT_SEED
) -> Tuple[List[Tuple[dict, float]], List[Tuple[dict, float]]]:
    """Split into train pool and fixed test set."""
    import random
    rng = random.Random(seed)
    shuffled = list(items)
    rng.shuffle(shuffled)
    test = shuffled[:test_size]
    train_pool = shuffled[test_size:]
    return train_pool, test
