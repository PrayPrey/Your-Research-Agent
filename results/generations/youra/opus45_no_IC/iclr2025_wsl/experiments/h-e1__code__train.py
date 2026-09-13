import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader
from typing import Dict, Literal
import random
import numpy as np

from config import Config
from model import flatten_weights


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_optimizer(model: nn.Module, cfg: Config) -> AdamW:
    return AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)


def build_scheduler(optimizer: AdamW, cfg: Config) -> CosineAnnealingLR:
    return CosineAnnealingLR(optimizer, T_max=cfg.scheduler_t_max, eta_min=cfg.scheduler_eta_min)


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    cfg: Config,
    model_kind: Literal["nfn", "mlp"],
    device: torch.device
) -> Dict:
    """Train model and return loss history."""
    model = model.to(device)
    optimizer = build_optimizer(model, cfg)
    scheduler = build_scheduler(optimizer, cfg)
    loss_fn = nn.MSELoss()

    train_losses = []
    val_losses = []

    for epoch in range(cfg.epochs):
        model.train()
        epoch_loss = 0.0
        n_batches = 0

        for batch, labels in train_loader:
            labels = labels.to(device)

            if model_kind == "mlp":
                x = flatten_weights(batch).to(device)
                pred = model(x).squeeze(-1)
            else:
                batch = batch.to(device)
                pred = model(batch).squeeze(-1)

            loss = loss_fn(pred, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            n_batches += 1

        scheduler.step()
        train_losses.append(epoch_loss / n_batches)

        model.eval()
        val_loss = 0.0
        n_val = 0
        with torch.no_grad():
            for batch, labels in test_loader:
                labels = labels.to(device)

                if model_kind == "mlp":
                    x = flatten_weights(batch).to(device)
                    pred = model(x).squeeze(-1)
                else:
                    batch = batch.to(device)
                    pred = model(batch).squeeze(-1)

                val_loss += loss_fn(pred, labels).item()
                n_val += 1

        val_losses.append(val_loss / n_val)

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{cfg.epochs}: train_loss={train_losses[-1]:.4f}, val_loss={val_losses[-1]:.4f}")

    return {"train_loss": train_losses, "val_loss": val_losses}
