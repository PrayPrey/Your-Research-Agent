"""Training loop for H-M2: NFNWithHead on accuracy prediction."""
import copy
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import numpy as np
import torch
import torch.nn as nn
from scipy.stats import spearmanr
from torch.utils.data import DataLoader

logger = logging.getLogger("h-m2")


@dataclass
class TrainHistory:
    train_loss: list = field(default_factory=list)
    val_loss: list = field(default_factory=list)
    train_spearman: list = field(default_factory=list)
    val_spearman: list = field(default_factory=list)


def _compute_spearman_epoch(model, loader, device) -> float:
    """Compute Spearman rho on a loader (NFN batch format)."""
    model.eval()
    preds, labels = [], []
    with torch.no_grad():
        for weight_list, flat_w, acc in loader:
            weight_list = [w.to(device) for w in weight_list]
            _, pred = model(weight_list)
            preds.extend(pred.squeeze(-1).cpu().numpy().tolist())
            labels.extend(acc.numpy().tolist())
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
    """Train NFNWithHead with Adam + CosineAnnealingLR, MSE loss.

    Batch format: (weight_list, flat_w, acc) — uses weight_list for forward.
    Saves best-val-loss checkpoint to cfg.results_dir/best_nfn_encoder.pt.
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

    results_dir = Path(cfg.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = results_dir / "best_nfn_encoder.pt"

    for epoch in range(1, cfg.epochs + 1):
        # --- Train ---
        model.train()
        train_losses = []
        for weight_list, flat_w, acc in train_loader:
            weight_list = [w.to(device) for w in weight_list]
            acc = acc.to(device)
            optimizer.zero_grad()
            _, pred = model(weight_list)
            loss = criterion(pred.squeeze(-1), acc)
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())
        scheduler.step()

        train_loss = float(np.mean(train_losses))

        # --- Validation ---
        model.eval()
        val_losses = []
        with torch.no_grad():
            for weight_list, flat_w, acc in val_loader:
                weight_list = [w.to(device) for w in weight_list]
                acc = acc.to(device)
                _, pred = model(weight_list)
                loss = criterion(pred.squeeze(-1), acc)
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
            torch.save(
                {
                    "encoder_state": model.encoder.state_dict(),
                    "head_state": model.head.state_dict(),
                    "epoch": epoch,
                    "val_loss": best_val_loss,
                },
                checkpoint_path,
            )

        logger.info(
            f"[H-M2] Epoch {epoch}/{cfg.epochs}: "
            f"train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, val_rho={val_rho:.4f}"
        )

    # Restore best model
    model.load_state_dict(best_state)
    logger.info(f"[H-M2] Training complete. Best val_loss={best_val_loss:.4f}")
    return model, history
