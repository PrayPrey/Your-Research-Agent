"""
Model definition and training for H-E1 experiment.
ResNet-18 modified for CIFAR-10 (32x32 images).
"""

import os
import torch
import torch.nn as nn
from torch.optim import SGD
from torch.optim.lr_scheduler import MultiStepLR
from torch.utils.data import DataLoader
from torchvision.models import resnet18
from tqdm import tqdm

from config import ExperimentConfig


def build_model(device: str = 'cuda') -> nn.Module:
    """
    ResNet-18 modified for CIFAR-10:
    - conv1: kernel=3, stride=1, padding=1 (no downsampling)
    - maxpool: removed (Identity)
    - fc: 512 -> 10 classes
    """
    model = resnet18(weights=None)

    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model.maxpool = nn.Identity()
    model.fc = nn.Linear(model.fc.in_features, 10)

    return model.to(device)


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    cfg: ExperimentConfig,
    seed: int,
    device: str = 'cuda',
    save_checkpoints: bool = True,
    checkpoint_prefix: str = 'model',
) -> nn.Module:
    """
    Train ResNet-18 for cfg.epochs with SGD + MultiStepLR.
    Saves checkpoints every 25 epochs if save_checkpoints=True.
    """
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)

    model.train()
    model = model.to(device)

    optimizer = SGD(
        model.parameters(),
        lr=cfg.lr,
        momentum=cfg.momentum,
        weight_decay=cfg.weight_decay
    )
    scheduler = MultiStepLR(
        optimizer,
        milestones=cfg.lr_milestones,
        gamma=cfg.lr_gamma
    )
    criterion = nn.CrossEntropyLoss()

    os.makedirs(cfg.checkpoint_dir, exist_ok=True)

    for epoch in range(cfg.epochs):
        model.train()
        total_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        scheduler.step()

        if save_checkpoints and (epoch + 1) % 25 == 0:
            ckpt_path = os.path.join(
                cfg.checkpoint_dir,
                f'{checkpoint_prefix}_seed{seed}_epoch{epoch+1}.pt'
            )
            torch.save(model.state_dict(), ckpt_path)

    if save_checkpoints:
        final_path = os.path.join(
            cfg.checkpoint_dir,
            f'{checkpoint_prefix}_seed{seed}_final.pt'
        )
        torch.save(model.state_dict(), final_path)

    return model


def load_checkpoint(path: str, device: str = 'cuda') -> nn.Module:
    """Load a model checkpoint."""
    model = build_model(device)
    model.load_state_dict(torch.load(path, map_location=device))
    model.eval()
    return model


def get_checkpoint_paths(cfg: ExperimentConfig, seed: int = 0, n_ckpts: int = 5) -> list:
    """Get evenly spaced checkpoint paths for attribution methods."""
    available_epochs = [25, 50, 75, 100, 125, 150, 175, 200]
    if n_ckpts == 1:
        selected = [200]
    else:
        step = len(available_epochs) // n_ckpts
        selected = [available_epochs[i * step] for i in range(n_ckpts)]

    paths = []
    for epoch in selected:
        path = os.path.join(
            cfg.checkpoint_dir,
            f'model_seed{seed}_epoch{epoch}.pt'
        )
        if os.path.exists(path):
            paths.append(path)

    if not paths:
        final_path = os.path.join(cfg.checkpoint_dir, f'model_seed{seed}_final.pt')
        if os.path.exists(final_path):
            paths = [final_path]

    return paths
