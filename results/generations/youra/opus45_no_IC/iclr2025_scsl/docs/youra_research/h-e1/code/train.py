"""ERM training loop with per-sample loss tracking."""
import random
import numpy as np
import torch
import torch.nn as nn
from torch.optim import SGD
from tqdm import tqdm


def set_seed(seed: int) -> None:
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def train_erm(model, loaders, tracker, n_epochs, lr, momentum, weight_decay, device):
    """Train with ERM, logging per-sample losses."""
    model = model.to(device)
    optimizer = SGD(model.parameters(), lr=lr, momentum=momentum, weight_decay=weight_decay)
    criterion = nn.CrossEntropyLoss(reduction='none')

    for epoch in range(n_epochs):
        model.train()
        epoch_losses = []
        epoch_indices = []

        pbar = tqdm(loaders["train"], desc=f"Epoch {epoch+1}/{n_epochs}", leave=False)
        for imgs, y, place, idx in pbar:
            imgs, y = imgs.to(device), y.to(device)

            optimizer.zero_grad()
            logits = model(imgs)
            per_sample_loss = criterion(logits, y)
            loss = per_sample_loss.mean()
            loss.backward()
            optimizer.step()

            epoch_losses.append(per_sample_loss.detach().cpu().numpy())
            epoch_indices.append(idx.numpy())

            pbar.set_postfix({"loss": f"{loss.item():.4f}"})

        all_losses = np.concatenate(epoch_losses)
        all_indices = np.concatenate(epoch_indices)
        tracker.update(epoch, all_indices, all_losses)

    return tracker
