import sys
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

logger = logging.getLogger(__name__)


def prepare_flat_elements(flat_w: torch.Tensor, weight_shapes: List[tuple]) -> torch.Tensor:
    """Reshape flat weight vector into padded element tensor for DeepSets.
    Each layer becomes one element, padded to uniform element_dim = max(prod(shape)).

    Args:
        flat_w: (D,) flattened weight vector for a single sample
        weight_shapes: list of shape tuples per layer

    Returns:
        (N_layers, element_dim) zero-padded tensor
    """
    import math
    sizes = [int(torch.tensor(s).prod().item()) if len(s) > 0 else 1
             for s in weight_shapes]
    # Handle case where weight_shapes are already flat sizes
    actual_sizes = []
    for s in weight_shapes:
        n = 1
        for d in s:
            n *= d
        actual_sizes.append(n)

    element_dim = max(actual_sizes)
    chunks = torch.split(flat_w, actual_sizes)
    elements = []
    for chunk in chunks:
        padded = torch.zeros(element_dim, dtype=chunk.dtype, device=chunk.device)
        padded[:len(chunk)] = chunk
        elements.append(padded)
    return torch.stack(elements, dim=0)  # (N_layers, element_dim)


def prepare_flat_elements_batch(flat_w_batch: torch.Tensor, weight_shapes: List[tuple]) -> torch.Tensor:
    """Batch version: (B, D) -> (B, N_layers, element_dim)."""
    elements = [prepare_flat_elements(flat_w_batch[i], weight_shapes)
                for i in range(flat_w_batch.size(0))]
    return torch.stack(elements, dim=0)


def get_weight_shapes(dataset) -> List[tuple]:
    """Extract per-layer weight shapes from dataset first sample."""
    if hasattr(dataset, 'weight_key_order') and hasattr(dataset, 'checkpoints'):
        sample = dataset.checkpoints[0]["state_dict"]
        return [tuple(sample[k].shape) for k in dataset.weight_key_order]
    # Fallback from NFNWeightDataset item
    first = dataset[0]
    weight_list = first[0]
    return [tuple(w.shape) for w in weight_list]


def train_deep_sets(
    model: "DeepSetsWithHead",
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg,
    device: torch.device,
    checkpoint_name: str,
    weight_shapes: List[tuple],
) -> Tuple["DeepSetsWithHead", Dict]:
    """Train DeepSetsWithHead with AdamW + CosineAnnealingLR.
    Saves best checkpoint by val loss.
    Returns: (trained_model, history_dict)
    """
    model = model.to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg.lr,
        weight_decay=cfg.weight_decay,
        betas=cfg.betas,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=cfg.t_max, eta_min=cfg.eta_min
    )
    criterion = nn.MSELoss()

    best_val_loss = float("inf")
    history = {"train_loss": [], "val_loss": [], "best_val_loss": None, "best_epoch": 0}

    ckpt_path = cfg.results_dir / checkpoint_name

    for epoch in range(cfg.epochs):
        # Train
        model.train()
        train_losses = []
        for batch in train_loader:
            flat_w, acc = batch[0].to(device), batch[1].to(device)
            x_elements = prepare_flat_elements_batch(flat_w, weight_shapes).to(device)
            _, pred = model(x_elements)
            loss = criterion(pred.squeeze(), acc.float())
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())
        scheduler.step()

        # Validate
        model.eval()
        val_losses = []
        with torch.no_grad():
            for batch in val_loader:
                flat_w, acc = batch[0].to(device), batch[1].to(device)
                x_elements = prepare_flat_elements_batch(flat_w, weight_shapes).to(device)
                _, pred = model(x_elements)
                loss = criterion(pred.squeeze(), acc.float())
                val_losses.append(loss.item())

        train_loss = sum(train_losses) / len(train_losses)
        val_loss = sum(val_losses) / len(val_losses)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            history["best_val_loss"] = best_val_loss
            history["best_epoch"] = epoch + 1
            torch.save({
                "model_state_dict": model.state_dict(),
                "epoch": epoch + 1,
                "val_loss": val_loss,
            }, ckpt_path)

        if (epoch + 1) % 10 == 0:
            logger.info(f"  Epoch {epoch+1}/{cfg.epochs}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}")

    logger.info(f"Training complete. Best val_loss={best_val_loss:.4f} at epoch {history['best_epoch']}")

    # Reload best
    best_ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    model.load_state_dict(best_ckpt["model_state_dict"])
    return model, history


def _import_hm1_models(cfg):
    import importlib.util
    p = Path(cfg.hm1_code_dir).resolve() / "models.py"
    spec = importlib.util.spec_from_file_location("hm1_models_train", str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _import_hm2_models(cfg):
    import importlib.util
    p = Path(cfg.hm2_code_dir).resolve() / "models.py"
    spec = importlib.util.spec_from_file_location("hm2_models_train", str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def train_flat_mlp_fresh(cfg, device: torch.device, train_loader, val_loader,
                          input_dim: int, checkpoint_name: str) -> Tuple[nn.Module, Dict]:
    """Train FlatMLPEncoder fresh (for CIFAR-10)."""
    hm1 = _import_hm1_models(cfg)
    FlatMLPEncoder = hm1.FlatMLPEncoder
    FlatMLPWithHead = hm1.FlatMLPWithHead

    encoder = FlatMLPEncoder(input_dim=input_dim, hidden_dims=[193], embed_dim=cfg.embed_dim)
    model = FlatMLPWithHead(encoder, embed_dim=cfg.embed_dim).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr,
                                   weight_decay=cfg.weight_decay, betas=cfg.betas)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.t_max, eta_min=cfg.eta_min)
    criterion = nn.MSELoss()

    best_val_loss = float("inf")
    history = {"best_val_loss": None, "best_epoch": 0, "param_count": sum(p.numel() for p in model.parameters())}
    ckpt_path = cfg.results_dir / checkpoint_name

    for epoch in range(cfg.epochs):
        model.train()
        for flat_w, acc in train_loader:
            flat_w, acc = flat_w.to(device), acc.to(device)
            _, pred = model(flat_w)
            loss = criterion(pred.squeeze(), acc.float())
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        scheduler.step()

        model.eval()
        val_losses = []
        with torch.no_grad():
            for flat_w, acc in val_loader:
                flat_w, acc = flat_w.to(device), acc.to(device)
                _, pred = model(flat_w)
                val_losses.append(criterion(pred.squeeze(), acc.float()).item())
        val_loss = sum(val_losses) / len(val_losses)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            history["best_val_loss"] = val_loss
            history["best_epoch"] = epoch + 1
            torch.save({"model_state_dict": model.state_dict(), "epoch": epoch + 1,
                        "val_loss": val_loss}, ckpt_path)

        if (epoch + 1) % 20 == 0:
            logger.info(f"  FlatMLP CIFAR epoch {epoch+1}: val_loss={val_loss:.4f}")

    best = torch.load(ckpt_path, map_location=device, weights_only=False)
    model.load_state_dict(best["model_state_dict"])
    return model, history


def train_nfn_fresh(cfg, device: torch.device, train_loader, val_loader,
                     weight_shapes: List[tuple], checkpoint_name: str) -> Tuple[nn.Module, Dict]:
    """Train NFNEncoder fresh on a new zoo (for CIFAR-10)."""
    hm2 = _import_hm2_models(cfg)
    NFNEncoder = hm2.NFNEncoder
    NFNWithHead = hm2.NFNWithHead

    encoder = NFNEncoder(weight_shapes=weight_shapes, channel_dim=112,
                          embed_dim=cfg.embed_dim, n_layers=3)
    model = NFNWithHead(encoder, embed_dim=cfg.embed_dim).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr,
                                   weight_decay=cfg.weight_decay, betas=cfg.betas)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.t_max, eta_min=cfg.eta_min)
    criterion = nn.MSELoss()

    best_val_loss = float("inf")
    history = {"best_val_loss": None, "best_epoch": 0}
    ckpt_path = cfg.results_dir / checkpoint_name

    for epoch in range(cfg.epochs):
        model.train()
        for batch in train_loader:
            weight_list, flat_w, acc = batch
            weight_list = [w.to(device) for w in weight_list]
            acc = acc.to(device)
            _, pred = model(weight_list)
            loss = criterion(pred.squeeze(), acc.float())
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        scheduler.step()

        model.eval()
        val_losses = []
        with torch.no_grad():
            for batch in val_loader:
                weight_list, flat_w, acc = batch
                weight_list = [w.to(device) for w in weight_list]
                acc = acc.to(device)
                _, pred = model(weight_list)
                val_losses.append(criterion(pred.squeeze(), acc.float()).item())
        val_loss = sum(val_losses) / len(val_losses)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            history["best_val_loss"] = val_loss
            history["best_epoch"] = epoch + 1
            torch.save({"encoder_state": model.encoder.state_dict(),
                        "head_state": model.head.state_dict(),
                        "epoch": epoch + 1, "val_loss": val_loss}, ckpt_path)

        if (epoch + 1) % 20 == 0:
            logger.info(f"  NFN CIFAR epoch {epoch+1}: val_loss={val_loss:.4f}")

    best = torch.load(ckpt_path, map_location=device, weights_only=False)
    model.encoder.load_state_dict(best["encoder_state"])
    model.head.load_state_dict(best["head_state"])
    return model, history
