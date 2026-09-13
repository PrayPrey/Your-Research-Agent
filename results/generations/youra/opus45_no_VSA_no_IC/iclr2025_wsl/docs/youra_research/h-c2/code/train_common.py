"""Generic training loop for NFN and MLP."""
import torch
import torch.nn as nn
from torch.optim import Adam
from sklearn.metrics import r2_score, mean_absolute_error
import numpy as np
from typing import Dict, List, Any, Callable
import random

import config


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_model(
    model: nn.Module,
    train_items: list,
    collate_fn: Callable,
    cfg: config.Config = config.CONFIG,
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
) -> Dict[str, List[float]]:
    """Train model for fixed epochs (no val split for small N)."""
    model = model.to(device)
    optimizer = Adam(model.parameters(), lr=cfg.train.lr)
    criterion = nn.MSELoss()

    history = {"train_loss": []}
    batch_size = cfg.train.batch_size

    for epoch in range(cfg.train.epochs):
        model.train()
        train_losses = []

        indices = torch.randperm(len(train_items)).tolist()
        for start in range(0, len(indices), batch_size):
            batch_idx = indices[start:start + batch_size]
            batch_items = [train_items[i] for i in batch_idx]

            inputs, targets = collate_fn(batch_items)

            # Handle NFN (list of tensors) vs MLP (single tensor)
            if isinstance(inputs, list):
                inputs = [w.to(device) for w in inputs]
            else:
                inputs = inputs.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            pred = model(inputs)
            loss = criterion(pred, targets)

            if torch.isnan(loss):
                print(f"NaN loss at epoch {epoch}")
                return history

            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())

        history["train_loss"].append(np.mean(train_losses))

    return history


def evaluate_model(
    model: nn.Module,
    test_items: list,
    collate_fn: Callable,
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
) -> Dict[str, Any]:
    """Evaluate model on test set."""
    model = model.to(device)
    model.eval()

    preds, targets_list = [], []
    batch_size = 32

    with torch.no_grad():
        for start in range(0, len(test_items), batch_size):
            batch_items = test_items[start:start + batch_size]
            inputs, targets = collate_fn(batch_items)

            if isinstance(inputs, list):
                inputs = [w.to(device) for w in inputs]
            else:
                inputs = inputs.to(device)

            pred = model(inputs)
            preds.extend(pred.cpu().numpy())
            targets_list.extend(targets.numpy())

    preds = np.array(preds)
    targets_arr = np.array(targets_list)

    return {
        "r2": r2_score(targets_arr, preds),
        "mae": mean_absolute_error(targets_arr, preds),
        "y_true": targets_arr,
        "y_pred": preds,
    }
