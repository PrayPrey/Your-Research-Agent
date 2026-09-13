"""
Load MLP checkpoint pairs from the local MLP zoo used in H-E1/M1 training.
The zoo contains real MLP classifiers trained on MNIST/SVHN/CIFAR-10 with
varying seeds, stored at ZOO_DIR. If not present, trains and caches them.
"""
import itertools
import json
import os
import random

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader

PROJECT_ROOT = os.environ.get('PROJECT_ROOT', '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl')

TASK_CONFIGS = {
    'mnist':   {'in_dim': 784,  'hidden_dims': [256, 256], 'out_dim': 10},
    'svhn':    {'in_dim': 3072, 'hidden_dims': [256, 256], 'out_dim': 10},
    'cifar10': {'in_dim': 3072, 'hidden_dims': [256, 256], 'out_dim': 10},
}

TASK_DATA_ROOTS = {
    'mnist':   os.path.join(PROJECT_ROOT, 'data/mnist'),
    'svhn':    os.path.join(PROJECT_ROOT, 'data/svhn'),
    'cifar10': os.path.join(PROJECT_ROOT, 'data/cifar10'),
}


class SimpleMLP(nn.Module):
    def __init__(self, in_dim, hidden_dims, out_dim):
        super().__init__()
        dims = [in_dim] + list(hidden_dims) + [out_dim]
        layers = []
        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i + 1]))
            if i < len(dims) - 2:
                layers.append(nn.ReLU())
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x.view(x.size(0), -1))


def _get_train_dataset(task):
    root = TASK_DATA_ROOTS[task]
    if task == 'mnist':
        t = transforms.Compose([transforms.ToTensor(),
                                 transforms.Normalize((0.1307,), (0.3081,))])
        return torchvision.datasets.MNIST(root=root, train=True, download=True, transform=t)
    elif task == 'svhn':
        t = transforms.Compose([transforms.ToTensor(),
                                 transforms.Normalize((0.4377, 0.4438, 0.4728),
                                                      (0.1980, 0.2010, 0.1970))])
        return torchvision.datasets.SVHN(root=root, split='train', download=True, transform=t)
    elif task == 'cifar10':
        t = transforms.Compose([transforms.ToTensor(),
                                 transforms.Normalize((0.4914, 0.4822, 0.4465),
                                                      (0.2023, 0.1994, 0.2010))])
        return torchvision.datasets.CIFAR10(root=root, train=True, download=True, transform=t)
    raise ValueError(f"Unknown task: {task}")


def _train_mlp(task, seed, device='cpu', epochs=5, batch_size=256):
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)

    cfg = TASK_CONFIGS[task]
    model = SimpleMLP(**cfg).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    dataset = _get_train_dataset(task)
    indices = list(range(len(dataset)))
    random.Random(seed).shuffle(indices)
    subset = torch.utils.data.Subset(dataset, indices[:10000])
    loader = DataLoader(subset, batch_size=batch_size, shuffle=True, num_workers=0)

    model.train()
    for _ in range(epochs):
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            criterion(model(x), y).backward()
            optimizer.step()

    model.eval()
    correct = total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            pred = model(x).argmax(dim=1)
            correct += (pred == y).sum().item()
            total += y.size(0)

    return model.state_dict(), correct / total


def load_mlp_zoo(zoo_dir, n_per_task=50, device='cpu', tasks=None):
    """
    Load MLP zoo from zoo_dir. Trains and caches if not present.
    Returns metadata: {task: [{path, acc, seed, task}, ...]}
    """
    if tasks is None:
        tasks = ['mnist', 'svhn', 'cifar10']

    os.makedirs(zoo_dir, exist_ok=True)
    meta_path = os.path.join(zoo_dir, 'zoo_metadata.json')

    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        total = sum(len(v) for v in meta.values())
        all_exist = all(
            os.path.exists(m['path'])
            for models in meta.values() for m in models
        )
        if total >= n_per_task * len(tasks) and all_exist:
            print(f"  MLP zoo loaded: {total} models from {zoo_dir}")
            return meta

    print(f"  Building MLP zoo at {zoo_dir} ({n_per_task} models/task)...")
    meta = {}
    for task in tasks:
        task_dir = os.path.join(zoo_dir, task)
        os.makedirs(task_dir, exist_ok=True)
        meta[task] = []
        for i in range(n_per_task):
            seed = 1000 * (tasks.index(task) + 1) + i
            ckpt_path = os.path.join(task_dir, f'mlp_seed{seed}.pt')
            if os.path.exists(ckpt_path):
                meta[task].append({'path': ckpt_path, 'acc': None, 'seed': seed, 'task': task})
                continue
            sd, acc = _train_mlp(task, seed, device=device)
            torch.save(sd, ckpt_path)
            meta[task].append({'path': ckpt_path, 'acc': float(acc), 'seed': seed, 'task': task})
            if (i + 1) % 10 == 0:
                print(f"    [{task}] {i+1}/{n_per_task}")

    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)
    total = sum(len(v) for v in meta.values())
    print(f"  MLP zoo ready: {total} models")
    return meta


def build_mlp_pairs(zoo_meta, min_pairs=500, seed=42, tasks=None):
    """Build same-task checkpoint pairs from zoo metadata."""
    if tasks is None:
        tasks = list(zoo_meta.keys())

    rng = random.Random(seed)
    all_pairs = []

    for task in tasks:
        models = zoo_meta.get(task, [])
        for i, (ia, ib) in enumerate(itertools.combinations(range(len(models)), 2)):
            ma, mb = models[ia], models[ib]
            all_pairs.append({
                'pair_id': f'{task}_{i}',
                'task': task,
                'path_a': ma['path'],
                'path_b': mb['path'],
                'acc_a': ma.get('acc'),
                'acc_b': mb.get('acc'),
            })

    if len(all_pairs) > min_pairs * 3:
        per_task_target = min_pairs // len(tasks) + 1
        sampled = []
        for task in tasks:
            task_pairs = [p for p in all_pairs if p['task'] == task]
            rng.shuffle(task_pairs)
            sampled.extend(task_pairs[:per_task_target])
        all_pairs = sampled

    rng.shuffle(all_pairs)
    for i, p in enumerate(all_pairs):
        p['pair_id'] = f"pair_{i:04d}"

    return all_pairs
