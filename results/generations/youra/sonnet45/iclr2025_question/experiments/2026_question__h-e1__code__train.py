"""Training logic with deterministic seed control."""

import torch
import torch.nn as nn
from torch.optim import SGD, Optimizer
from torch.utils.data import DataLoader
import random
import numpy as np
import os


def set_seed_deterministic(seed: int) -> None:
    """Set all random seeds for reproducibility.

    Args:
        seed: Random seed value
    """
    # Python random
    random.seed(seed)

    # NumPy random
    np.random.seed(seed)

    # PyTorch random
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    # cuDNN determinism
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # CUBLAS determinism (for CUDA 10.2+)
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"


def train_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: Optimizer,
    criterion: nn.Module,
    device: str
) -> float:
    """Train for one epoch.

    Args:
        model: Neural network model
        train_loader: Training data loader
        optimizer: Optimizer
        criterion: Loss criterion
        device: 'cuda' or 'cpu'

    Returns:
        Average loss for the epoch
    """
    model.train()
    total_loss = 0.0
    num_batches = 0

    for data, target in train_loader:
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        num_batches += 1

    return total_loss / num_batches


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    epochs: int,
    lr: float,
    momentum: float,
    device: str
) -> None:
    """Full training loop.

    Args:
        model: Neural network model
        train_loader: Training data loader
        epochs: Number of epochs
        lr: Learning rate
        momentum: SGD momentum
        device: 'cuda' or 'cpu'

    Note:
        Modifies model in-place
    """
    optimizer = SGD(model.parameters(), lr=lr, momentum=momentum)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        avg_loss = train_epoch(model, train_loader, optimizer, criterion, device)
        # Silent training (no logging for EXISTENCE PoC)
