"""Training loop for NFN model."""
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau
from sklearn.metrics import r2_score, mean_absolute_error
import numpy as np
from typing import Dict, List, Tuple
from tqdm import tqdm

from nfn_model import NFNAccuracyPredictor, collate_weights
import config


def set_seed(seed: int):
    import random
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_nfn(
    model: NFNAccuracyPredictor,
    train_items: list,
    val_items: list,
    cfg: config.Config = config.CONFIG,
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
) -> Dict[str, List[float]]:
    """Train NFN model with early stopping."""
    model = model.to(device)
    optimizer = Adam(model.parameters(), lr=cfg.train.lr, weight_decay=cfg.train.weight_decay)
    scheduler = ReduceLROnPlateau(optimizer, factor=0.5, patience=cfg.train.lr_patience, verbose=True)
    criterion = nn.MSELoss()

    history = {"train_loss": [], "val_loss": [], "val_r2": [], "val_mae": []}
    best_val_loss = float("inf")
    best_state = None
    epochs_no_improve = 0

    batch_size = cfg.train.batch_size

    for epoch in range(cfg.train.epochs):
        # Training
        model.train()
        train_losses = []

        indices = torch.randperm(len(train_items)).tolist()
        for start in range(0, len(indices), batch_size):
            batch_idx = indices[start:start + batch_size]
            batch_items = [train_items[i] for i in batch_idx]

            weights, targets = collate_weights(batch_items)
            weights = [w.to(device) for w in weights]
            targets = targets.to(device)

            optimizer.zero_grad()
            pred = model(weights)
            loss = criterion(pred, targets)

            if torch.isnan(loss):
                print(f"NaN loss at epoch {epoch}, stopping")
                return history

            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())

        # Validation
        model.eval()
        val_preds, val_targets = [], []
        with torch.no_grad():
            for start in range(0, len(val_items), batch_size):
                batch_items = val_items[start:start + batch_size]
                weights, targets = collate_weights(batch_items)
                weights = [w.to(device) for w in weights]
                pred = model(weights)
                val_preds.extend(pred.cpu().numpy())
                val_targets.extend(targets.numpy())

        val_preds = np.array(val_preds)
        val_targets = np.array(val_targets)
        val_r2 = r2_score(val_targets, val_preds)
        val_mae = mean_absolute_error(val_targets, val_preds)
        val_loss = ((val_preds - val_targets) ** 2).mean()

        history["train_loss"].append(np.mean(train_losses))
        history["val_loss"].append(val_loss)
        history["val_r2"].append(val_r2)
        history["val_mae"].append(val_mae)

        scheduler.step(val_loss)

        if epoch % 5 == 0:
            print(f"Epoch {epoch}: train_loss={np.mean(train_losses):.4f}, val_r2={val_r2:.4f}, val_mae={val_mae:.4f}")

        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1

        if epochs_no_improve >= cfg.train.early_stop_patience:
            print(f"Early stopping at epoch {epoch}")
            break

    # Restore best model
    if best_state is not None:
        model.load_state_dict(best_state)

    return history


def evaluate_nfn(
    model: NFNAccuracyPredictor,
    test_items: list,
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
) -> Dict[str, float]:
    """Evaluate NFN on test set."""
    model = model.to(device)
    model.eval()

    preds, targets = [], []
    batch_size = 32

    with torch.no_grad():
        for start in range(0, len(test_items), batch_size):
            batch_items = test_items[start:start + batch_size]
            weights, tgt = collate_weights(batch_items)
            weights = [w.to(device) for w in weights]
            pred = model(weights)
            preds.extend(pred.cpu().numpy())
            targets.extend(tgt.numpy())

    preds = np.array(preds)
    targets = np.array(targets)

    return {
        "r2": r2_score(targets, preds),
        "mae": mean_absolute_error(targets, preds),
        "y_true": targets,
        "y_pred": preds,
    }
