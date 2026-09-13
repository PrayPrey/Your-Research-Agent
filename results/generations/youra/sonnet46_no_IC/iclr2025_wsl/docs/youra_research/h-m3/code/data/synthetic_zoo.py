"""
Build a local MLP zoo for the H-M3 interpolation experiment.
Trains MLP classifiers on standard torchvision datasets (MNIST/SVHN/CIFAR-10)
with different seeds, saving state_dicts as a local zoo.
These are real trained MLP classifiers on real benchmark datasets, used as
same-task checkpoint pairs for the latent interpolation evaluation.
"""
import os
import json
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision
import torchvision.transforms as transforms

PROJECT_ROOT = os.environ.get('PROJECT_ROOT', '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl')


class SimpleMLP(nn.Module):
    def __init__(self, in_dim, hidden_dims, out_dim):
        super().__init__()
        dims = [in_dim] + hidden_dims + [out_dim]
        layers = []
        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i + 1]))
            if i < len(dims) - 2:
                layers.append(nn.ReLU())
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x.view(x.size(0), -1))


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


def get_dataset(task, data_root=None, train=True):
    root = TASK_DATA_ROOTS.get(task, os.path.join(data_root or PROJECT_ROOT, task))
    if task == 'mnist':
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
        return torchvision.datasets.MNIST(root=root, train=train, download=True, transform=transform)
    elif task == 'svhn':
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4377, 0.4438, 0.4728), (0.1980, 0.2010, 0.1970))
        ])
        split = 'train' if train else 'test'
        return torchvision.datasets.SVHN(root=root, split=split, download=False, transform=transform)
    elif task == 'cifar10':
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
        ])
        return torchvision.datasets.CIFAR10(root=root, train=train, download=True, transform=transform)
    raise ValueError(f"Unknown task: {task}")


def train_one_model(task, seed, data_root=None, device='cpu', epochs=3, batch_size=256):
    """Train a single MLP for a few epochs. Returns (state_dict, train_acc)."""
    torch.manual_seed(seed)
    np.random.seed(seed)

    cfg = TASK_CONFIGS[task]
    model = SimpleMLP(**cfg).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    dataset = get_dataset(task, train=True)
    # Use 5000 samples for fast training
    indices = list(range(len(dataset)))
    random.seed(seed)
    random.shuffle(indices)
    subset = torch.utils.data.Subset(dataset, indices[:5000])
    loader = DataLoader(subset, batch_size=batch_size, shuffle=True, num_workers=0)

    model.train()
    for _ in range(epochs):
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()

    # Compute train accuracy on the subset
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            pred = model(x).argmax(dim=1)
            correct += (pred == y).sum().item()
            total += y.size(0)
    acc = correct / total

    return model.state_dict(), acc


def build_synthetic_zoo(zoo_dir, data_root, n_per_task=50, device='cpu', tasks=None):
    """
    Train n_per_task MLPs per task and save as local MLP zoo.
    Returns metadata dict: {task: [{path, acc, seed}, ...]}
    """
    if tasks is None:
        tasks = ['mnist', 'svhn', 'cifar10']

    os.makedirs(zoo_dir, exist_ok=True)
    meta_path = os.path.join(zoo_dir, 'zoo_metadata.json')

    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        # Validate
        total = sum(len(v) for v in meta.values())
        if total >= n_per_task * len(tasks):
            print(f"  MLP zoo already exists: {total} models total")
            return meta

    meta = {}
    for task in tasks:
        task_dir = os.path.join(zoo_dir, task)
        os.makedirs(task_dir, exist_ok=True)
        meta[task] = []
        print(f"  Training {n_per_task} MLPs for task={task}...")
        for i in range(n_per_task):
            seed = 1000 * (tasks.index(task) + 1) + i
            ckpt_path = os.path.join(task_dir, f'mlp_seed{seed}.pt')
            if os.path.exists(ckpt_path):
                entry = {'path': ckpt_path, 'acc': None, 'seed': seed, 'task': task}
                meta[task].append(entry)
                continue
            sd, acc = train_one_model(task, seed, data_root, device=device)
            torch.save(sd, ckpt_path)
            entry = {'path': ckpt_path, 'acc': float(acc), 'seed': seed, 'task': task}
            meta[task].append(entry)
            if (i + 1) % 10 == 0:
                print(f"    [{task}] {i+1}/{n_per_task} done")

    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)

    total = sum(len(v) for v in meta.values())
    print(f"  MLP zoo complete: {total} models")
    return meta
