"""Training loop with checkpointing for h-m1."""
import os

import torch
import torch.nn as nn
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader
from tqdm import tqdm

from config import ExperimentConfig


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    cfg: ExperimentConfig,
    device: torch.device
) -> list:
    """Train model with SGD + cosine annealing, checkpoint every N epochs.

    Returns list of checkpoint paths.
    """
    model.to(device)
    model.train()

    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=cfg.lr,
        momentum=cfg.momentum,
        weight_decay=cfg.weight_decay
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=cfg.epochs)
    criterion = nn.CrossEntropyLoss()

    checkpoint_paths = []

    for epoch in range(cfg.epochs):
        loss_sum = 0.0
        for x, y in tqdm(train_loader, desc=f"Epoch {epoch+1}/{cfg.epochs}", leave=False):
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            loss_sum += loss.item()

        scheduler.step()
        avg_loss = loss_sum / len(train_loader)

        if (epoch + 1) % cfg.checkpoint_every == 0:
            ckpt_path = _save_checkpoint(model, epoch + 1, cfg.ckpt_dir)
            checkpoint_paths.append(ckpt_path)
            print(f"Epoch {epoch+1}: loss={avg_loss:.4f}, saved {ckpt_path}")

    return checkpoint_paths


def _save_checkpoint(model: nn.Module, epoch: int, ckpt_dir: str) -> str:
    path = os.path.join(ckpt_dir, f"ckpt_epoch_{epoch:03d}.pt")
    torch.save(model.state_dict(), path)
    return path
