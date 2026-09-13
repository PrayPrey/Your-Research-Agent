from typing import List, Tuple, Dict
import time

import numpy as np
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader

from models import FlattenedMLP, DWSModel, NFTModel
from config import ExperimentConfig


def build_model(architecture: str, weight_shapes: List[Tuple[int, int]], hidden_dim: int, num_classes: int = 1) -> nn.Module:
    if architecture == "mlp":
        input_dim = sum(in_c * out_c for (in_c, out_c) in weight_shapes)
        return FlattenedMLP(input_dim=input_dim, hidden_dims=[hidden_dim * 2, hidden_dim, hidden_dim // 2], num_classes=num_classes, dropout=0.1)
    elif architecture == "dws":
        return DWSModel(weight_shapes=weight_shapes, hidden=hidden_dim, num_classes=num_classes)
    elif architecture == "nft":
        return NFTModel(weight_shapes=weight_shapes, d_model=hidden_dim, nhead=4, num_layers=2, num_classes=num_classes)
    else:
        raise ValueError(f"Unknown architecture: {architecture}")


def train_task(model: nn.Module, train_loader: DataLoader, cfg: ExperimentConfig, loss_fn: nn.Module) -> Tuple[nn.Module, Dict[int, float]]:
    device = torch.device(cfg.device if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    optimizer = AdamW(model.parameters(), lr=cfg.lr)
    scheduler = CosineAnnealingLR(optimizer, T_max=cfg.epochs)

    history = {}
    model.train()

    for epoch in range(cfg.epochs):
        epoch_loss = 0.0
        n_batches = 0

        for weight_list, labels in train_loader:
            weight_list = [w.to(device) for w in weight_list]
            labels = labels.to(device).float()

            optimizer.zero_grad()
            preds = model(weight_list).squeeze(-1)
            loss = loss_fn(preds, labels)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            n_batches += 1

        scheduler.step()
        history[epoch] = epoch_loss / max(n_batches, 1)

    return model, history


def predict(model: nn.Module, loader: DataLoader, device: str = "cuda") -> Tuple[np.ndarray, np.ndarray]:
    device = torch.device(device if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()

    all_preds = []
    all_labels = []

    with torch.no_grad():
        for weight_list, labels in loader:
            weight_list = [w.to(device) for w in weight_list]
            preds = model(weight_list).squeeze(-1)
            all_preds.append(preds.cpu().numpy())
            all_labels.append(labels.numpy())

    return np.concatenate(all_preds), np.concatenate(all_labels)
