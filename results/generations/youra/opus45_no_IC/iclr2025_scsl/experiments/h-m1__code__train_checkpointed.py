"""Checkpointed ERM training for H-M1."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code"))

import torch
import torch.nn as nn
from torch.optim import SGD
from tqdm import tqdm


def train_with_checkpoints(
    model: nn.Module,
    loaders: dict,
    n_epochs: int,
    checkpoint_epochs: list,
    lr: float,
    momentum: float,
    weight_decay: float,
    device: str,
    ckpt_dir: str,
) -> dict:
    os.makedirs(ckpt_dir, exist_ok=True)
    model = model.to(device)
    optimizer = SGD(model.parameters(), lr=lr, momentum=momentum, weight_decay=weight_decay)
    criterion = nn.CrossEntropyLoss()
    ckpt_paths = {}

    for epoch in range(1, n_epochs + 1):
        model.train()
        total_loss = 0.0
        for imgs, y, place, idx in tqdm(loaders["train"], desc=f"Epoch {epoch}/{n_epochs}", leave=False):
            imgs, y = imgs.to(device), y.to(device)
            logits = model(imgs)
            loss = criterion(logits, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(loaders["train"])
        print(f"Epoch {epoch}: loss={avg_loss:.4f}")

        if epoch in checkpoint_epochs:
            path = os.path.join(ckpt_dir, f"epoch_{epoch}.pt")
            torch.save(model.state_dict(), path)
            ckpt_paths[epoch] = path
            print(f"  Checkpoint saved: {path}")

    return ckpt_paths
