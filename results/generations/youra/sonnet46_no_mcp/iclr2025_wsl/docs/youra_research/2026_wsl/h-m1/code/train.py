"""Training loop for H-M1: FlatMLPWithHead on accuracy prediction."""
import copy
import logging
from dataclasses import dataclass, field
from typing import Tuple

import numpy as np
import torch
import torch.nn as nn
from scipy.stats import spearmanr
from torch.utils.data import DataLoader

logger = logging.getLogger("h-m1")


@dataclass
class TrainHistory:
    train_loss: list = field(default_factory=list)
    val_loss: list = field(default_factory=list)
    train_spearman: list = field(default_factory=list)
    val_spearman: list = field(default_factory=list)


def _compute_spearman_epoch(model, loader, device) -> float:
    """Compute Spearman rho on a loader for monitoring."""
    model.eval()
    preds, labels = [], []
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            _, pred = model(x)
            preds.extend(pred.squeeze(-1).cpu().numpy().tolist())
            labels.extend(y.numpy().tolist())
    if len(set(labels)) < 2:
        return 0.0
    rho = spearmanr(preds, labels).statistic
    return float(rho) if not np.isnan(rho) else 0.0


def train_encoder(
    model,
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg,
    device: torch.device,
) -> Tuple[object, TrainHistory]:
    """Train FlatMLPWithHead with Adam + CosineAnnealingLR, MSE loss.

    Returns best-val-loss model and training history.
    """
    model = model.to(device)
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=cfg.lr,
        weight_decay=cfg.weight_decay,
        betas=cfg.betas,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=cfg.t_max, eta_min=cfg.eta_min
    )
    criterion = nn.MSELoss()
    history = TrainHistory()

    best_val_loss = float("inf")
    best_state = copy.deepcopy(model.state_dict())

    for epoch in range(1, cfg.epochs + 1):
        # --- Train ---
        model.train()
        train_losses = []
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            _, pred = model(x)
            loss = criterion(pred.squeeze(-1), y)
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())
        scheduler.step()

        train_loss = float(np.mean(train_losses))

        # --- Validation ---
        model.eval()
        val_losses = []
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                _, pred = model(x)
                loss = criterion(pred.squeeze(-1), y)
                val_losses.append(loss.item())
        val_loss = float(np.mean(val_losses))

        # --- Spearman (every 10 epochs to save time) ---
        if epoch % 10 == 0 or epoch == 1 or epoch == cfg.epochs:
            train_rho = _compute_spearman_epoch(model, train_loader, device)
            val_rho = _compute_spearman_epoch(model, val_loader, device)
        else:
            train_rho = history.train_spearman[-1] if history.train_spearman else 0.0
            val_rho = history.val_spearman[-1] if history.val_spearman else 0.0

        history.train_loss.append(train_loss)
        history.val_loss.append(val_loss)
        history.train_spearman.append(train_rho)
        history.val_spearman.append(val_rho)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = copy.deepcopy(model.state_dict())

        logger.info(
            f"[H-M1] Epoch {epoch}/{cfg.epochs}: "
            f"train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, val_rho={val_rho:.4f}"
        )

    # Restore best model
    model.load_state_dict(best_state)
    logger.info(f"[H-M1] Training complete. Best val_loss={best_val_loss:.4f}")
    return model, history
