"""Training and checkpoint management."""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
import config


def train_model(model, train_loader, device):
    """Train model and save checkpoints at specified epochs."""
    os.makedirs(config.CHECKPOINT_DIR, exist_ok=True)

    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(
        model.parameters(), lr=config.LR,
        momentum=config.MOMENTUM, weight_decay=config.WEIGHT_DECAY
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=config.EPOCHS)

    checkpoints = []
    for epoch in range(1, config.EPOCHS + 1):
        model.train()
        total_loss, correct, total = 0, 0, 0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * images.size(0)
            correct += (outputs.argmax(1) == labels).sum().item()
            total += images.size(0)
        scheduler.step()

        if epoch in config.CHECKPOINT_EPOCHS:
            ckpt_path = os.path.join(config.CHECKPOINT_DIR, f"ckpt_epoch{epoch}.pt")
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'lr': scheduler.get_last_lr()[0],
            }, ckpt_path)
            checkpoints.append(ckpt_path)
            print(f"Epoch {epoch}: loss={total_loss/total:.4f}, acc={correct/total:.4f}, saved {ckpt_path}")
        elif epoch % 20 == 0:
            print(f"Epoch {epoch}: loss={total_loss/total:.4f}, acc={correct/total:.4f}")

    return checkpoints


def load_checkpoints():
    """Load existing checkpoint paths."""
    checkpoints = []
    for epoch in config.CHECKPOINT_EPOCHS:
        ckpt_path = os.path.join(config.CHECKPOINT_DIR, f"ckpt_epoch{epoch}.pt")
        if os.path.exists(ckpt_path):
            checkpoints.append(ckpt_path)
    return checkpoints


def train_or_load(model, train_loader, device):
    """Train if no checkpoints exist, otherwise load."""
    checkpoints = load_checkpoints()
    if len(checkpoints) == len(config.CHECKPOINT_EPOCHS):
        print(f"Found {len(checkpoints)} checkpoints, skipping training")
        # Load final checkpoint weights
        ckpt = torch.load(checkpoints[-1], map_location=device)
        model.load_state_dict(ckpt['model_state_dict'])
        return checkpoints
    print("Training model...")
    return train_model(model, train_loader, device)
