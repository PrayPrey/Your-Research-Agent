#!/usr/bin/env python3
"""Generate a real CNN Model Zoo by training on CIFAR-10.

This creates a proper model zoo where accuracy labels are derived from
actual model evaluation, not synthetic generation. Each model is trained
with different hyperparameters (lr, weight_decay, epochs) to create
diversity in performance.
"""

import os
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from torchvision import transforms
from typing import List, Dict, Tuple
import json


class SimpleCNN(nn.Module):
    """Simple CNN matching the MLP structure expected by NFN.

    Uses only Linear layers (no Conv2d) so NFN can process directly.
    This is a simple MLP classifier, which NFN is designed for.
    """
    def __init__(self, input_dim: int = 3072, hidden_dims: Tuple[int, ...] = (64, 64)):
        super().__init__()
        layers = []
        prev_dim = input_dim
        for h in hidden_dims:
            layers.append(nn.Linear(prev_dim, h))
            layers.append(nn.ReLU())
            prev_dim = h
        layers.append(nn.Linear(prev_dim, 10))  # 10 classes
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        x = x.view(x.size(0), -1)  # Flatten
        return self.net(x)


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_single_model(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    lr: float,
    weight_decay: float,
    epochs: int,
    device: torch.device
) -> float:
    """Train a single model and return test accuracy."""
    model = model.to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.CrossEntropyLoss()

    model.train()
    for epoch in range(epochs):
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

    # Evaluate
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in test_loader:
            x, y = x.to(device), y.to(device)
            out = model(x)
            pred = out.argmax(dim=1)
            correct += (pred == y).sum().item()
            total += y.size(0)

    accuracy = correct / total
    return accuracy


def convert_state_dict_to_nfn_format(state_dict: Dict) -> Dict:
    """Convert Sequential state dict to NFN-compatible format.

    NFN expects keys like 'layer0.weight', 'layer0.bias', etc.
    """
    new_sd = {}
    layer_idx = 0
    keys = list(state_dict.keys())

    i = 0
    while i < len(keys):
        key = keys[i]
        # Sequential uses 'net.0.weight', 'net.0.bias', etc.
        if 'weight' in key:
            new_sd[f'layer{layer_idx}.weight'] = state_dict[key].cpu()
            i += 1
            if i < len(keys) and 'bias' in keys[i]:
                new_sd[f'layer{layer_idx}.bias'] = state_dict[keys[i]].cpu()
                i += 1
            layer_idx += 1
        else:
            i += 1

    return new_sd


def generate_model_zoo(
    n_models: int = 1000,
    data_dir: str = None,
    zoo_dir: str = './zoo_cache',
    seed: int = 42,
    device: torch.device = None,
    train_subset_size: int = 10000,
    test_subset_size: int = 2000,
    batch_size: int = 128,
    verbose: bool = True
) -> List[Dict]:
    """Generate a model zoo by training CNNs on CIFAR-10.

    Returns list of dicts with 'state_dict' and 'label' (accuracy).
    """
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    set_seed(seed)

    # Check cache
    cache_file = os.path.join(zoo_dir, f'zoo_n{n_models}_seed{seed}.pt')
    if os.path.exists(cache_file):
        if verbose:
            print(f"Loading cached zoo from {cache_file}")
        return torch.load(cache_file)

    os.makedirs(zoo_dir, exist_ok=True)

    # Load CIFAR-10 via HuggingFace (faster CDN)
    from datasets import load_dataset
    import PIL.Image

    if verbose:
        print("Loading CIFAR-10 from HuggingFace...")

    hf_dataset = load_dataset("cifar10")

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))
    ])

    class HFDataset(torch.utils.data.Dataset):
        def __init__(self, hf_split, transform):
            self.data = hf_split
            self.transform = transform
        def __len__(self):
            return len(self.data)
        def __getitem__(self, idx):
            item = self.data[idx]
            img = item['img']
            if not isinstance(img, PIL.Image.Image):
                img = PIL.Image.fromarray(img)
            return self.transform(img), item['label']

    train_dataset = HFDataset(hf_dataset['train'], transform)
    test_dataset = HFDataset(hf_dataset['test'], transform)

    # Use subsets for faster training
    train_indices = list(range(len(train_dataset)))
    test_indices = list(range(len(test_dataset)))
    random.shuffle(train_indices)
    random.shuffle(test_indices)

    train_subset = Subset(train_dataset, train_indices[:train_subset_size])
    test_subset = Subset(test_dataset, test_indices[:test_subset_size])

    train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_subset, batch_size=batch_size, shuffle=False, num_workers=2)

    # Hyperparameter ranges for diversity
    lr_range = (1e-4, 1e-2)
    wd_range = (1e-6, 1e-2)
    epoch_range = (1, 10)  # Short training for speed

    models = []

    for i in range(n_models):
        # Sample hyperparameters
        lr = 10 ** np.random.uniform(np.log10(lr_range[0]), np.log10(lr_range[1]))
        wd = 10 ** np.random.uniform(np.log10(wd_range[0]), np.log10(wd_range[1]))
        epochs = np.random.randint(epoch_range[0], epoch_range[1] + 1)

        # Create and train model
        model = SimpleCNN(hidden_dims=(64, 64))
        accuracy = train_single_model(
            model, train_loader, test_loader,
            lr=lr, weight_decay=wd, epochs=epochs, device=device
        )

        # Convert state dict
        state_dict = convert_state_dict_to_nfn_format(model.state_dict())

        models.append({
            'state_dict': state_dict,
            'label': accuracy,
            'hyperparams': {'lr': lr, 'weight_decay': wd, 'epochs': epochs}
        })

        if verbose and (i + 1) % 50 == 0:
            print(f"Generated {i + 1}/{n_models} models, last acc: {accuracy:.4f}")

    # Save cache
    torch.save(models, cache_file)
    if verbose:
        accs = [m['label'] for m in models]
        print(f"\nZoo stats: min_acc={min(accs):.4f}, max_acc={max(accs):.4f}, mean={np.mean(accs):.4f}")
        print(f"Saved to {cache_file}")

    return models


def load_model_zoo(
    n_models: int = 1000,
    data_dir: str = None,
    zoo_dir: str = None,
    seed: int = 42,
    device: torch.device = None
) -> List[Dict]:
    """Load or generate the model zoo."""
    if data_dir is None:
        data_dir = '/home/PrayPrey/.cache/torch/datasets'
    if zoo_dir is None:
        zoo_dir = os.path.join(os.path.dirname(__file__), 'zoo_cache')

    return generate_model_zoo(
        n_models=n_models,
        data_dir=data_dir,
        zoo_dir=zoo_dir,
        seed=seed,
        device=device
    )


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_models', type=int, default=1000)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    models = load_model_zoo(n_models=args.n_models, seed=args.seed)
    print(f"Generated {len(models)} models")
