import copy
import random
from typing import Type

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from scipy.stats import spearmanr

from data.loader import ZooData, make_loader


def predict_all(model: nn.Module, loader, device: str) -> tuple:
    model.eval()
    preds, targets = [], []
    with torch.no_grad():
        for weights, gap in loader:
            weights = weights.to(device)
            out = model(weights).cpu().numpy()
            preds.extend(out.tolist())
            targets.extend(gap.numpy().tolist())
    return preds, targets


def train_encoder(
    encoder: nn.Module,
    zoo: ZooData,
    lr: float,
    batch_size: int,
    epochs: int,
    seed: int = 42,
    lr_schedule: str = "none",
    device: str = "cuda:0",
    verbose: bool = False,
) -> tuple:
    """Train encoder with MSE on gap; select checkpoint by val Spearman.
    Returns (best_model, best_val_spearman, val_curve)."""
    torch.manual_seed(seed)
    encoder = encoder.to(device)

    train_loader = make_loader(zoo, "train", batch_size, shuffle=True)
    val_loader = make_loader(zoo, "val", batch_size, shuffle=False)

    optimizer = optim.Adam(encoder.parameters(), lr=lr)
    if lr_schedule == "cosine":
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, epochs)
    else:
        scheduler = None

    best_r = -float("inf")
    best_state = None
    curve = []

    for epoch in range(epochs):
        encoder.train()
        for weights, gap in train_loader:
            weights, gap = weights.to(device), gap.to(device)
            optimizer.zero_grad()
            pred = encoder(weights)
            loss = F.mse_loss(pred, gap)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(encoder.parameters(), 1.0)
            optimizer.step()
        if scheduler:
            scheduler.step()

        preds, targets = predict_all(encoder, val_loader, device)
        r = spearmanr(preds, targets).statistic if len(preds) > 2 else 0.0
        if not (r == r):  # nan check
            r = 0.0
        curve.append(r)

        if r > best_r:
            best_r = r
            best_state = copy.deepcopy(encoder.state_dict())

        if verbose and epoch % 20 == 0:
            print(f"    epoch {epoch:3d}: val_r={r:.4f} best={best_r:.4f}")

    encoder.load_state_dict(best_state)
    return encoder, best_r, curve


def random_search(
    encoder_cls: Type[nn.Module],
    arch_kwargs: dict,
    zoo: ZooData,
    lr_candidates: list,
    batch_size: int,
    epochs: int,
    n_trials: int = 3,
    device: str = "cuda:0",
    lr_schedule: str = "none",
    encoder_name: str = "",
) -> tuple:
    """Random search over lr_candidates; select by best val Spearman.
    Returns (best_model, best_config, best_curve)."""
    rng = random.Random(42)
    best_r = -float("inf")
    best_model = None
    best_cfg = None
    best_curve = None

    for trial in range(n_trials):
        lr = rng.choice(lr_candidates)
        print(f"  [{encoder_name}] trial {trial+1}/{n_trials} lr={lr:.2e} epochs={epochs}")
        encoder = encoder_cls(**arch_kwargs)
        model, val_r, curve = train_encoder(
            encoder, zoo, lr=lr, batch_size=batch_size, epochs=epochs,
            seed=42, lr_schedule=lr_schedule, device=device, verbose=True,
        )
        print(f"  [{encoder_name}] trial {trial+1} best val_r={val_r:.4f}")
        if val_r > best_r:
            best_r = val_r
            best_model = model
            best_cfg = {"lr": lr}
            best_curve = curve

    return best_model, best_cfg, best_curve
