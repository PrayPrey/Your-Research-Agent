"""FR-0.3 fallback: train NFT Condition A from scratch on zoo property prediction."""
import os
import sys
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR

from nft_encoder import build_nft, extract_embeddings


def train_nft_fallback(
    zoo_weights: list[dict],
    zoo_properties: torch.Tensor,  # (N, 3)
    save_path: str = "checkpoints/nft_condition_a_hm1.pt",
    device: str = "cpu",
    n_epochs: int = 100,
    batch_size: int = 64,
    lr: float = 1e-3,
    seed: int = 42,
    val_frac: float = 0.1,
    patience: int = 10,
) -> nn.Module:
    """Train NFT (Condition A) on zoo property prediction. Returns trained model."""
    print(f"Training NFT fallback on {len(zoo_weights)} models, {n_epochs} epochs...")
    torch.manual_seed(seed)

    N = len(zoo_weights)
    # Train/val split
    val_n = max(1, int(N * val_frac))
    perm = torch.randperm(N, generator=torch.Generator().manual_seed(seed))
    val_idx  = perm[:val_n].tolist()
    train_idx = perm[val_n:].tolist()

    # Normalize properties (mean-center, unit-variance per column)
    props_train = zoo_properties[train_idx]
    prop_mean = props_train.nanmean(dim=0)
    prop_std  = props_train.std(dim=0).clamp(min=1e-6)
    props_norm = (zoo_properties - prop_mean) / prop_std

    model = build_nft().to(device)
    opt   = Adam(model.parameters(), lr=lr, betas=(0.9, 0.999), weight_decay=1e-4)
    sched = CosineAnnealingLR(opt, T_max=n_epochs)
    loss_fn = nn.MSELoss()

    # Convert weights to device dicts
    def get_batch_weights(indices):
        return [
            {k: v.to(device) for k, v in
             {kk: zoo_weights[i][kk] for kk in zoo_weights[i]}.items()}
            for i in indices
        ]

    best_val = float("inf")
    no_improve = 0
    best_state = None

    for epoch in range(n_epochs):
        model.train()
        # Shuffle train
        idx_perm = torch.randperm(len(train_idx)).tolist()
        train_shuffled = [train_idx[i] for i in idx_perm]
        epoch_loss = 0.0
        n_batches = 0
        for b in range(0, len(train_shuffled), batch_size):
            batch_idx = train_shuffled[b:b + batch_size]
            w_batch = get_batch_weights(batch_idx)
            tgt = props_norm[batch_idx].to(device)
            pred = model(w_batch)
            loss = loss_fn(pred, tgt)
            opt.zero_grad()
            loss.backward()
            opt.step()
            epoch_loss += loss.item()
            n_batches += 1
        sched.step()

        # Validation
        model.eval()
        with torch.no_grad():
            val_batches = []
            for b in range(0, len(val_idx), batch_size):
                bidx = val_idx[b:b + batch_size]
                w_batch = get_batch_weights(bidx)
                pred = model(w_batch)
                tgt  = props_norm[bidx].to(device)
                val_batches.append(loss_fn(pred, tgt).item())
            val_loss = sum(val_batches) / len(val_batches)

        if epoch % 10 == 0 or epoch == n_epochs - 1:
            print(f"Epoch {epoch+1:3d}/{n_epochs}: train={epoch_loss/n_batches:.4f} val={val_loss:.4f}")

        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            no_improve = 0
        else:
            no_improve += 1
            if no_improve >= patience:
                print(f"Early stop at epoch {epoch+1} (no improvement for {patience} epochs)")
                break

    model.load_state_dict(best_state)
    model.eval()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"NFT saved to {save_path}")
    return model
