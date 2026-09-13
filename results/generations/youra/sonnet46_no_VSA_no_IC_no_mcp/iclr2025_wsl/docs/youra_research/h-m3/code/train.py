"""H-M3 training: condition × seed training loop with early stopping."""
import os
import random
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau
from scipy.stats import spearmanr

from config import ExperimentConfig
from model import CanonicalWeightEncoder


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


class WeightZooDataset(Dataset):
    def __init__(self, X, Y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.Y = torch.tensor(Y, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, i):
        return self.X[i], self.Y[i]


def make_dataloaders(X_train, Y_train, X_val, Y_val, batch_size=64, seed=42):
    g = torch.Generator()
    g.manual_seed(seed)
    loader_train = DataLoader(
        WeightZooDataset(X_train, Y_train),
        batch_size=batch_size, shuffle=True, generator=g
    )
    loader_val = DataLoader(
        WeightZooDataset(X_val, Y_val),
        batch_size=batch_size, shuffle=False
    )
    return loader_train, loader_val


def _val_spearman(encoder, loader, device):
    encoder.eval()
    preds, trues = [], []
    with torch.no_grad():
        for X_batch, Y_batch in loader:
            pred = encoder(X_batch.to(device))
            preds.append(pred.cpu().numpy())
            trues.append(Y_batch.numpy())
    preds = np.concatenate(preds, axis=0)
    trues = np.concatenate(trues, axis=0)
    rhos = []
    for i in range(trues.shape[1]):
        mask = np.isfinite(trues[:, i]) & np.isfinite(preds[:, i])
        if mask.sum() > 1:
            rho = spearmanr(preds[mask, i], trues[mask, i]).statistic
            rhos.append(float(rho))
    return float(np.mean(rhos)) if rhos else 0.0


def train_condition(encoder, loader_train, loader_val, config: ExperimentConfig,
                    seed: int = 42, checkpoint_path: str = None):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    encoder = encoder.to(device)
    set_seed(seed)

    optimizer = Adam(encoder.parameters(), lr=config.lr,
                     betas=config.adam_betas, weight_decay=config.weight_decay)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', patience=config.lr_patience,
                                  factor=config.lr_factor, min_lr=config.min_lr)
    criterion = nn.MSELoss()

    best_val_rho = float('-inf')
    patience_counter = 0
    best_state = None
    history = []

    for epoch in range(config.max_epochs):
        encoder.train()
        total_loss = 0.0
        n_batches = 0
        for X_batch, Y_batch in loader_train:
            X_batch = X_batch.to(device)
            Y_batch = Y_batch.to(device)
            pred = encoder(X_batch)
            loss = criterion(pred, Y_batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            n_batches += 1

        val_rho = _val_spearman(encoder, loader_val, device)
        scheduler.step(-val_rho)
        history.append({'epoch': epoch, 'train_loss': total_loss / max(n_batches, 1),
                        'val_rho': val_rho})

        if val_rho > best_val_rho:
            best_val_rho = val_rho
            best_state = {k: v.clone() for k, v in encoder.state_dict().items()}
            patience_counter = 0
            if checkpoint_path:
                os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
                torch.save(best_state, checkpoint_path)
        else:
            patience_counter += 1
            if patience_counter >= config.es_patience:
                print(f"  Early stop at epoch {epoch+1} (best val_rho={best_val_rho:.4f})")
                break

        if epoch % 10 == 0:
            print(f"  Epoch {epoch+1:3d}: train_loss={total_loss/max(n_batches,1):.4f} "
                  f"val_rho={val_rho:.4f} patience={patience_counter}")

    if best_state is not None:
        encoder.load_state_dict(best_state)

    return {
        'best_val_rho': best_val_rho,
        'best_epoch': len(history),
        'checkpoint_path': checkpoint_path,
        'train_history': history,
    }


def train_frozen_regressor(encoder, loader_train, loader_val, config: ExperimentConfig):
    """Train only regressor head (encoder frozen)."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    encoder = encoder.to(device)

    # Only train regressor params
    optimizer = Adam(encoder.regressor.parameters(), lr=config.lr,
                     betas=config.adam_betas, weight_decay=config.weight_decay)
    criterion = nn.MSELoss()
    best_val_rho = float('-inf')
    patience_counter = 0
    best_state = None

    for epoch in range(config.max_epochs):
        encoder.train()
        # Keep NFT in eval mode (frozen)
        encoder.nft_encoder.eval()
        total_loss = 0.0
        n_batches = 0
        for X_batch, Y_batch in loader_train:
            pred = encoder(X_batch.to(device))
            loss = criterion(pred, Y_batch.to(device))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            n_batches += 1

        val_rho = _val_spearman(encoder, loader_val, device)
        if val_rho > best_val_rho:
            best_val_rho = val_rho
            best_state = {k: v.clone() for k, v in encoder.state_dict().items()}
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= config.es_patience:
                break

    if best_state is not None:
        encoder.load_state_dict(best_state)

    return {'best_val_rho': best_val_rho}


def run_frozen_encoder_experiment(cond_a_checkpoint, X_train, Y_train,
                                   X_val, Y_val, X_test, Y_test,
                                   config: ExperimentConfig, full_rhos: dict):
    """
    Load Condition A checkpoint, freeze encoder, retrain regressor on B/C/D.
    Returns {condition: {rho_frozen, rho_full}}
    """
    from evaluate import bootstrap_spearman

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    results = {}

    for cond in config.frozen_conditions:
        print(f"  Frozen encoder experiment: condition {cond}")
        encoder = CanonicalWeightEncoder(
            condition=cond,
            embed_dim=config.embed_dim, n_layers=config.n_layers,
            nhead=config.nhead, dim_feedforward=config.dim_feedforward,
            dropout=config.dropout,
        )
        # Load condition A weights into NFT
        state = torch.load(cond_a_checkpoint, map_location='cpu', weights_only=True)
        # Only load NFT encoder portion
        nft_state = {k[len('nft_encoder.'):]: v for k, v in state.items()
                     if k.startswith('nft_encoder.')}
        encoder.nft_encoder.load_state_dict(nft_state)
        encoder.freeze_encoder()

        loader_train, loader_val = make_dataloaders(
            X_train, Y_train, X_val, Y_val,
            batch_size=config.batch_size, seed=42
        )
        train_frozen_regressor(encoder, loader_train, loader_val, config)

        # Evaluate on test
        encoder.eval()
        with torch.no_grad():
            X_te_t = torch.tensor(X_test, dtype=torch.float32)
            preds = encoder(X_te_t).cpu().numpy()

        rho_frozen_per_label = {}
        for i, label in enumerate(config.label_names):
            rho, _, _ = bootstrap_spearman(preds[:, i], Y_test[:, i], seed=42)
            rho_frozen_per_label[label] = rho

        rho_full_per_label = full_rhos.get(cond, {})
        results[cond] = {
            'rho_frozen': rho_frozen_per_label,
            'rho_full': rho_full_per_label,
        }

    return results
