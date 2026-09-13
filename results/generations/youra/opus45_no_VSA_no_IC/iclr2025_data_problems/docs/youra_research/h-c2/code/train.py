"""Multi-model training with checkpointing for h-c2."""
import os
from typing import Dict, List, Tuple

import torch
import torch.nn as nn
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader
from tqdm import tqdm

from config import ExperimentConfig, ModelTrainConfig


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    mcfg: ModelTrainConfig,
    cfg: ExperimentConfig,
    device: torch.device
) -> Tuple[List[str], float]:
    """Train single model, checkpoint every N epochs, return (ckpt_paths, final_accuracy)."""
    model.to(device)
    criterion = nn.CrossEntropyLoss()

    if mcfg.optimizer == "adamw":
        optimizer = torch.optim.AdamW(model.parameters(), lr=mcfg.lr)
    else:
        optimizer = torch.optim.SGD(model.parameters(), lr=mcfg.lr, momentum=0.9, weight_decay=5e-4)

    scheduler = CosineAnnealingLR(optimizer, T_max=mcfg.epochs)
    checkpoint_paths = []

    for epoch in range(mcfg.epochs):
        model.train()
        loss_sum = 0.0
        for x, y in tqdm(train_loader, desc=f"{mcfg.name} E{epoch+1}/{mcfg.epochs}", leave=False):
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
            loss_sum += loss.item()
        scheduler.step()

        if (epoch + 1) % cfg.checkpoint_every == 0 or (epoch + 1) == mcfg.epochs:
            ckpt_path = _save_checkpoint(model, mcfg.name, epoch + 1, cfg.ckpt_dir)
            checkpoint_paths.append(ckpt_path)

    accuracy = _evaluate(model, test_loader, device)
    print(f"{mcfg.name}: final test accuracy = {accuracy:.4f}")
    return checkpoint_paths, accuracy


def _evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> float:
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            preds = model(x).argmax(dim=1)
            correct += (preds == y).sum().item()
            total += y.size(0)
    return correct / total


def _save_checkpoint(model: nn.Module, name: str, epoch: int, ckpt_dir: str) -> str:
    os.makedirs(ckpt_dir, exist_ok=True)
    path = os.path.join(ckpt_dir, f"{name}_epoch_{epoch:03d}.pt")
    torch.save(model.state_dict(), path)
    return path


def train_all_models(
    models: Dict[str, nn.Module],
    train_loader: DataLoader,
    test_loader: DataLoader,
    mcfgs: Dict[str, ModelTrainConfig],
    cfg: ExperimentConfig,
    device: torch.device
) -> Dict[str, Tuple[List[str], float]]:
    """Train all models, return {name: (ckpt_paths, accuracy)}."""
    results = {}
    for name, model in models.items():
        ckpts, acc = train_model(model, train_loader, test_loader, mcfgs[name], cfg, device)
        results[name] = (ckpts, acc)
    return results
