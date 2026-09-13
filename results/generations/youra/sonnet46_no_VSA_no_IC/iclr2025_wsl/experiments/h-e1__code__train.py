"""Shared training loop for all encoder types."""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np


def train_one(
    encoder: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    encoder_name: str,
    epochs: int = 100,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    seed: int = 42,
    device: str = "cuda",
) -> dict:
    """
    Train encoder with Adam + CosineAnnealingLR + MSE.
    Returns {"train_loss": [...], "val_loss": [...]}.
    """
    torch.manual_seed(seed)
    encoder = encoder.to(device)
    opt = torch.optim.Adam(encoder.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    loss_fn = nn.MSELoss()

    train_losses, val_losses = [], []

    for epoch in range(epochs):
        encoder.train()
        epoch_loss = 0.0
        n_batches = 0

        for batch in train_loader:
            inputs, targets = batch
            targets = targets.to(device)
            pred = _forward(encoder, inputs, encoder_name, device, training=True)
            loss = loss_fn(pred, targets)
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(encoder.parameters(), 1.0)
            opt.step()
            epoch_loss += loss.item()
            n_batches += 1

        scheduler.step()
        avg_train = epoch_loss / max(n_batches, 1)
        train_losses.append(avg_train)

        # Validation
        if (epoch + 1) % 10 == 0 or epoch == epochs - 1:
            val_loss = evaluate_loss(encoder, val_loader, encoder_name, loss_fn, device)
            val_losses.append(val_loss)
            if (epoch + 1) % 20 == 0:
                print(f"  Epoch {epoch+1}/{epochs}: train_loss={avg_train:.4f} val_loss={val_loss:.4f}")

    return {"train_loss": train_losses, "val_loss": val_losses}


def evaluate_loss(encoder, loader, encoder_name, loss_fn, device):
    encoder.eval()
    total_loss, n = 0.0, 0
    with torch.no_grad():
        for batch in loader:
            inputs, targets = batch
            targets = targets.to(device)
            pred = _forward(encoder, inputs, encoder_name, device, training=False)
            loss = loss_fn(pred, targets)
            total_loss += loss.item() * targets.shape[0]
            n += targets.shape[0]
    return total_loss / max(n, 1)


def _forward(encoder, inputs, encoder_name: str, device: str, training: bool = False):
    """Dispatch forward pass based on encoder type."""
    if encoder_name in ("flat_mlp",):
        x = inputs.to(device)
        return encoder(x)
    elif encoder_name == "flat_mlp_perm_aug":
        x = inputs.to(device)
        return encoder(x, training=training)
    elif encoder_name == "nfn":
        wsfeat = _move_wsfeat(inputs, device)
        return encoder(wsfeat)
    elif encoder_name == "gnn_nfn":
        batch = inputs.to(device)
        return encoder(batch)
    else:
        raise ValueError(f"Unknown encoder_name: {encoder_name}")


def _move_wsfeat(wsfeat, device):
    """Move WeightSpaceFeatures to device."""
    # WeightSpaceFeatures has .to() method
    if hasattr(wsfeat, 'to'):
        return wsfeat.to(device)
    # Fallback for namedtuple-like
    import torch
    fields = {}
    for field in wsfeat._fields:
        val = getattr(wsfeat, field)
        if isinstance(val, (list, tuple)):
            val = type(val)(v.to(device) if isinstance(v, torch.Tensor) else v for v in val)
        elif isinstance(val, torch.Tensor):
            val = val.to(device)
        fields[field] = val
    return type(wsfeat)(**fields)


def get_predictions(encoder, loader, encoder_name: str, device: str):
    """Return (y_true, y_pred) numpy arrays from loader."""
    encoder.eval()
    all_pred, all_true = [], []
    with torch.no_grad():
        for batch in loader:
            inputs, targets = batch
            targets = targets.to(device)
            pred = _forward(encoder, inputs, encoder_name, device, training=False)
            all_pred.append(pred.cpu().numpy())
            all_true.append(targets.cpu().numpy())
    return np.concatenate(all_true), np.concatenate(all_pred)
