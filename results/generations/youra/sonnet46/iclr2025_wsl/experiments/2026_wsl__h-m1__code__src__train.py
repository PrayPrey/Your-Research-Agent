"""Training utilities for H-M1 experiment.

Extends H-E1 training with multi-seed orchestration for 6 encoders × 3 seeds = 18 runs.
"""
import json
import logging
import os
import random

import numpy as np
import torch
import torch.nn as nn
from torch.optim.lr_scheduler import CosineAnnealingLR
from tqdm import tqdm

from src.config import ENCODER_CONFIG, ExperimentConfig
from src.models import build_encoder

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Seed and checkpoint utilities (L-3-3)
# ---------------------------------------------------------------------------

def set_seed(seed: int = 42) -> None:
    """Set torch, numpy, and random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def save_checkpoint(model: nn.Module, path: str) -> None:
    """Save model state dict to path."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    torch.save({"model_state_dict": model.state_dict()}, path)
    logger.info(f"Checkpoint saved: {path}")


def load_checkpoint(model: nn.Module, path: str, device) -> nn.Module:
    """Load model state dict from path."""
    ckpt = torch.load(path, map_location=device)
    model.load_state_dict(ckpt["model_state_dict"])
    logger.info(f"Checkpoint loaded: {path}")
    return model


# ---------------------------------------------------------------------------
# Epoch training (H-E1 pattern reuse)
# ---------------------------------------------------------------------------

def train_epoch(
    model: nn.Module,
    loader,
    optimizer,
    device: torch.device,
    model_type: str = "flat",
) -> float:
    """Run one training epoch, returns mean MSE loss."""
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

    return total_loss / n_batches if n_batches > 0 else 0.0


# ---------------------------------------------------------------------------
# Sanity check (L-3-3)
# ---------------------------------------------------------------------------

def train_model(
    model: nn.Module,
    train_loader,
    n_epochs: int = 100,
    lr: float = 1e-3,
    device=None,
    model_type: str = "flat",
    checkpoint_path: str = None,
) -> dict:
    """Full training loop (H-E1 compatible API).

    Returns
    -------
    dict
        {"train_loss_history": list[float], "final_epoch": int}
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
                raise RuntimeError(f"NaN loss persists after lr reduction at epoch {epoch}")
            for pg in optimizer.param_groups:
                pg["lr"] = 1e-4
            nan_recovery_attempted = True
            epoch_loss = train_epoch(model, train_loader, optimizer, device, model_type)
            if np.isnan(epoch_loss):
                raise RuntimeError(f"NaN loss persists after lr reduction at epoch {epoch}")

        loss_history.append(epoch_loss)
        scheduler.step()

        if (epoch + 1) % 10 == 0:
            logger.info(f"[{model_type}] Epoch {epoch+1}/{n_epochs} | loss={epoch_loss:.6f}")

    if checkpoint_path is not None:
        save_checkpoint(model, checkpoint_path)

    return {"train_loss_history": loss_history, "final_epoch": n_epochs}


def run_sanity_check(
    flat_loader,
    nft_loader,
    cfg: ExperimentConfig,
    flat_input_dim: int,
    layer_fan_ins: list,
    n_samples: int = 10,
) -> None:
    """Quick forward-pass sanity check for all 6 encoders.

    Loads n_samples models, runs forward pass, checks output shape and no NaNs.

    Raises
    ------
    ValueError
        If any encoder produces NaN or wrong shape.
    """
    device = torch.device(cfg.device if torch.cuda.is_available() else "cpu")
    logger.info(f"Running sanity check ({n_samples} samples per encoder)...")

    for enc_name in cfg.encoder_names:
        enc_cfg = ENCODER_CONFIG[enc_name]
        model_type = enc_cfg["model_type"]
        model = build_encoder(enc_name, flat_input_dim, layer_fan_ins).to(device)
        model.eval()

        # Get one batch from appropriate loader
        loader = nft_loader if model_type == "nft" else flat_loader
        batch = next(iter(loader))

        with torch.no_grad():
            if model_type == "flat":
                x = batch[0][:n_samples].to(device)
                out = model(x)
            else:
                wms = [t[:n_samples].to(device) for t in batch[0]]
                out = model(wms)

        if out.shape != (min(n_samples, out.shape[0]), 1):
            raise ValueError(f"[{enc_name}] Wrong output shape: {out.shape}")
        if torch.isnan(out).any():
            raise ValueError(f"[{enc_name}] NaN in output")

        logger.info(f"  ✓ {enc_name}: output shape {out.shape}, no NaNs")

    logger.info("Sanity check passed for all 6 encoders.")


# ---------------------------------------------------------------------------
# Single-seed training (L-3-1)
# ---------------------------------------------------------------------------

def train_encoder_one_seed(
    encoder_name: str,
    seed: int,
    cfg: ExperimentConfig,
    flat_train_loader,
    nft_train_loader,
    flat_input_dim: int,
    layer_fan_ins: list,
) -> dict:
    """Train one encoder for one seed.

    Parameters
    ----------
    encoder_name : str
        Name from ENCODER_NAMES.
    seed : int
        Random seed for this run.
    cfg : ExperimentConfig
        Experiment configuration.
    flat_train_loader : DataLoader
        Training loader for flat encoders.
    nft_train_loader : DataLoader
        Training loader for NFT encoders.
    flat_input_dim : int
        Input dimension for flat encoders.
    layer_fan_ins : list[int]
        Fan-in dimensions for NFT encoders.

    Returns
    -------
    dict
        {"encoder": str, "seed": int, "final_val_loss": float, "checkpoint_path": str,
         "train_loss_history": list[float]}
    """
    # Set seed BEFORE model creation for full reproducibility
    set_seed(seed)

    enc_cfg = ENCODER_CONFIG[encoder_name]
    model_type = enc_cfg["model_type"]
    device = torch.device(cfg.device if torch.cuda.is_available() else "cpu")

    model = build_encoder(encoder_name, flat_input_dim, layer_fan_ins).to(device)

    # Use H-E1 verified field names
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=cfg.lr,
        betas=cfg.betas,
        weight_decay=cfg.weight_decay,
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=cfg.T_max, eta_min=cfg.eta_min)

    train_loader = nft_train_loader if model_type == "nft" else flat_train_loader
    loss_history = []
    nan_recovery_attempted = False

    for epoch in range(cfg.n_epochs):
        epoch_loss = train_epoch(model, train_loader, optimizer, device, model_type)

        if np.isnan(epoch_loss):
            if nan_recovery_attempted:
                logger.error(f"[{encoder_name}][seed={seed}] NaN persists, stopping.")
                break
            logger.warning(f"[{encoder_name}][seed={seed}] NaN at epoch {epoch}, using nan_recovery_lr={cfg.nan_recovery_lr}")
            for pg in optimizer.param_groups:
                pg["lr"] = cfg.nan_recovery_lr
            nan_recovery_attempted = True
            epoch_loss = train_epoch(model, train_loader, optimizer, device, model_type)
            if np.isnan(epoch_loss):
                logger.error(f"[{encoder_name}][seed={seed}] NaN persists after recovery.")
                break

        loss_history.append(epoch_loss)
        scheduler.step()

        if (epoch + 1) % 20 == 0:
            logger.info(
                f"[{encoder_name}][seed={seed}] Epoch {epoch+1}/{cfg.n_epochs} "
                f"| loss={epoch_loss:.6f} | lr={optimizer.param_groups[0]['lr']:.2e}"
            )

    # Save checkpoint
    enc_safe = encoder_name.replace("/", "_").replace("+", "plus")
    ckpt_path = os.path.join(cfg.checkpoint_dir, f"{enc_safe}_seed{seed}.pt")
    save_checkpoint(model, ckpt_path)

    final_loss = loss_history[-1] if loss_history else float("nan")
    logger.info(f"[{encoder_name}][seed={seed}] Training complete. Final loss={final_loss:.6f}")

    return {
        "encoder": encoder_name,
        "seed": seed,
        "final_val_loss": final_loss,
        "checkpoint_path": ckpt_path,
        "train_loss_history": loss_history,
    }


# ---------------------------------------------------------------------------
# Multi-seed training orchestration (L-3-2)
# ---------------------------------------------------------------------------

def run_all_training(
    cfg: ExperimentConfig,
    flat_train_loader,
    nft_train_loader,
    flat_input_dim: int,
    layer_fan_ins: list,
) -> list:
    """Run all 18 training runs: 6 encoders × 3 seeds.

    Parameters
    ----------
    cfg : ExperimentConfig
    flat_train_loader : DataLoader
    nft_train_loader : DataLoader
    flat_input_dim : int
    layer_fan_ins : list[int]

    Returns
    -------
    list[dict]
        18 result dicts from train_encoder_one_seed().
    """
    os.makedirs(cfg.checkpoint_dir, exist_ok=True)
    os.makedirs(cfg.results_dir, exist_ok=True)

    all_results = []
    total_runs = len(cfg.seeds) * len(cfg.encoder_names)
    run_idx = 0

    with tqdm(total=total_runs, desc="Training 6 encoders × 3 seeds") as pbar:
        for seed in cfg.seeds:
            for enc_name in cfg.encoder_names:
                run_idx += 1
                pbar.set_description(f"[{run_idx}/{total_runs}] {enc_name} seed={seed}")
                logger.info(f"Training {enc_name} seed {seed} [{run_idx}/{total_runs}]")

                try:
                    result = train_encoder_one_seed(
                        enc_name, seed, cfg,
                        flat_train_loader, nft_train_loader,
                        flat_input_dim, layer_fan_ins,
                    )
                    all_results.append(result)
                except Exception as e:
                    logger.error(f"[{enc_name}][seed={seed}] Failed: {e}")
                    all_results.append({
                        "encoder": enc_name,
                        "seed": seed,
                        "final_val_loss": float("nan"),
                        "checkpoint_path": None,
                        "train_loss_history": [],
                        "error": str(e),
                    })

                pbar.update(1)

    # Save aggregate training results
    training_results_path = os.path.join(cfg.results_dir, "training_results.json")
    with open(training_results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    logger.info(f"Training results saved: {training_results_path}")

    return all_results
