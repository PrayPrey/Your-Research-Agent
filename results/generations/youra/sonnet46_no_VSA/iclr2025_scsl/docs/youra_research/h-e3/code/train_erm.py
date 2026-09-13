import os
import sys
import torch
import torch.nn as nn
from torch import Tensor
from torch.utils.data import DataLoader
from torchvision.models import resnet50, ResNet50_Weights

sys.path.insert(0, os.path.dirname(__file__))
import config
from data import get_train_loader


def build_model() -> nn.Module:
    model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(2048, 2)
    return model


def save_checkpoint(model: nn.Module, seed: int, epoch: int) -> None:
    path = config.ckpt_path(seed, epoch)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save(model.state_dict(), path)


def load_checkpoint(seed: int, epoch: int, device: str) -> nn.Module:
    path = config.ckpt_path(seed, epoch)
    state_dict = torch.load(path, map_location=device)
    model = build_model()
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    scheduler,
    device: str,
) -> float:
    model.train()
    criterion = nn.CrossEntropyLoss()
    total_loss = 0.0
    for inputs, labels, _ in loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    scheduler.step()
    return total_loss / len(loader)


def run_training(
    seed: int,
    n_epochs: int,
    checkpoint_epochs: list,
    device: str,
) -> None:
    config.set_seed(seed)
    model = build_model()
    model.to(device)

    optimizer = torch.optim.SGD(
        model.parameters(), lr=config.LR,
        momentum=config.MOMENTUM, weight_decay=config.WEIGHT_DECAY
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_epochs)
    loader = get_train_loader(config.DATA_ROOT, config.BATCH_SIZE)

    # CRITICAL: save t=0 BEFORE any Waterbirds gradient step
    if 0 in checkpoint_epochs:
        save_checkpoint(model, seed, epoch=0)
        print(f"[seed={seed}] Saved checkpoint epoch=0 (pre-training)")

    for epoch in range(1, n_epochs + 1):
        loss = train_one_epoch(model, loader, optimizer, scheduler, device)
        if epoch in checkpoint_epochs:
            save_checkpoint(model, seed, epoch)
            print(f"[seed={seed}] epoch={epoch} loss={loss:.4f} → checkpoint saved")
        elif epoch % 10 == 0:
            print(f"[seed={seed}] epoch={epoch} loss={loss:.4f}")
