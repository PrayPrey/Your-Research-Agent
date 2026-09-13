"""Training utilities for h-e1 experiment."""
import logging
import random
import os

import numpy as np
import torch
import torch.nn as nn
from torch.optim.lr_scheduler import CosineAnnealingLR

logger = logging.getLogger(__name__)


def set_seed(seed: int = 42) -> None:
    """Set torch, numpy, and random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_epoch(
    model: nn.Module,
    loader,
    optimizer,
    device: torch.device,
    model_type: str = "flat",
) -> float:
    """Run one epoch of training.

    Parameters
    ----------
    model : nn.Module
        The model to train.
    loader : DataLoader
        Training data loader.
    optimizer : torch.optim.Optimizer
        Optimizer.
    device : torch.device
        Device to train on.
    model_type : str
        'flat' or 'nft'.

    Returns
    -------
    float
        Mean MSE loss for the epoch.
    """
    model.train()
    criterion = nn.MSELoss()
    total_loss = 0.0
    n_batches = 0

    for batch in loader:
        optimizer.zero_grad()

        if model_type == "flat":
            x, labels = batch[0].to(device), batch[1].to(device)
            preds = model(x).squeeze(-1)
        else:  # nft
            wms = [t.to(device) for t in batch[0]]
            labels = batch[1].to(device)
            preds = model(wms).squeeze(-1)

        loss = criterion(preds, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        n_batches += 1

    if n_batches == 0:
        return 0.0
    return total_loss / n_batches


def train_model(
    model: nn.Module,
    train_loader,
    n_epochs: int = 50,
    lr: float = 1e-3,
    device=None,
    model_type: str = "flat",
    checkpoint_path: str = None,
) -> dict:
    """Full training loop.

    Parameters
    ----------
    model : nn.Module
        Model to train.
    train_loader : DataLoader
        Training data loader.
    n_epochs : int
        Number of training epochs (default 50 for PoC).
    lr : float
        Initial learning rate.
    device : torch.device or None
        Training device; defaults to CUDA if available.
    model_type : str
        'flat' or 'nft'.
    checkpoint_path : str or None
        Path to save checkpoint after training.

    Returns
    -------
    dict
        {"train_loss_history": list[float], "final_epoch": int}

    Raises
    ------
    RuntimeError
        If NaN loss persists after lr reduction.
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = model.to(device)
    optimizer = torch.optim.Adam(
        model.parameters(), lr=lr, betas=(0.9, 0.999), weight_decay=1e-4
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=n_epochs, eta_min=1e-5)

    loss_history = []
    nan_recovery_attempted = False

    for epoch in range(n_epochs):
        epoch_loss = train_epoch(model, train_loader, optimizer, device, model_type)

        if np.isnan(epoch_loss):
            if nan_recovery_attempted:
                raise RuntimeError(
                    f"NaN loss persists after lr reduction at epoch {epoch}"
                )
            logger.warning(
                f"NaN loss at epoch {epoch}. Reducing lr to 1e-4 and retrying."
            )
            # Reset optimizer with lower lr
            for pg in optimizer.param_groups:
                pg["lr"] = 1e-4
            nan_recovery_attempted = True
            # Retry same epoch
            epoch_loss = train_epoch(model, train_loader, optimizer, device, model_type)
            if np.isnan(epoch_loss):
                raise RuntimeError(
                    f"NaN loss persists after lr reduction at epoch {epoch}"
                )

        loss_history.append(epoch_loss)
        scheduler.step()

        if (epoch + 1) % 10 == 0:
            logger.info(
                f"[{model_type}] Epoch {epoch+1}/{n_epochs} | loss={epoch_loss:.6f} "
                f"| lr={optimizer.param_groups[0]['lr']:.2e}"
            )

    if checkpoint_path is not None:
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "loss_history": loss_history,
                "n_epochs": n_epochs,
                "model_type": model_type,
            },
            checkpoint_path,
        )
        logger.info(f"Checkpoint saved to {checkpoint_path}")

    return {"train_loss_history": loss_history, "final_epoch": n_epochs}
