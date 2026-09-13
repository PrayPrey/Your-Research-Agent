from typing import Tuple, List

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from config import Config
from tracker import TrainingDynamicsTracker


def train_model_tracked(
    model: nn.Module,
    model_type: str,
    train_loader: DataLoader,
    cfg: Config,
    sample_input: List[torch.Tensor] = None
) -> Tuple[nn.Module, TrainingDynamicsTracker]:
    """Train model with gradient/weight/attention tracking."""
    model = model.to(cfg.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.cosine_t_max)
    criterion = nn.CrossEntropyLoss()

    tracker = TrainingDynamicsTracker(model, model_type)

    # Get sample input for attention tracking (first batch)
    if sample_input is None:
        for weight_list, _ in train_loader:
            sample_input = [w[:1].to(cfg.device) for w in weight_list]
            break

    # Initial weight snapshot
    prev_weights = tracker.snapshot_weights()

    model.train()
    for epoch in range(cfg.epochs):
        total_loss = 0.0
        for weight_list, labels in train_loader:
            weight_list = [w.to(cfg.device) for w in weight_list]
            labels = labels.to(cfg.device)

            optimizer.zero_grad()
            logits = model(weight_list)
            loss = criterion(logits, labels)
            loss.backward()

            # Track gradients before optimizer step
            if (epoch + 1) % cfg.track_every == 0:
                tracker.track_gradients(epoch)

            optimizer.step()
            total_loss += loss.item()

        scheduler.step()

        # Track weight updates at snapshot intervals
        if (epoch + 1) % cfg.snapshot_every == 0:
            tracker.track_weight_updates(prev_weights, epoch)
            prev_weights = tracker.snapshot_weights()

        # Track attention for NFT
        if model_type == "nft" and (epoch + 1) % cfg.track_every == 0:
            model.eval()
            tracker.track_attention(sample_input)
            model.train()

        if (epoch + 1) % 20 == 0:
            print(f"  Epoch {epoch+1}/{cfg.epochs}, Loss: {total_loss/len(train_loader):.4f}")

    return model, tracker
