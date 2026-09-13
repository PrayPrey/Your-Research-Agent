import os
import torch
from torch import nn
from tqdm import tqdm

from model import build_resnet50
from data import get_loaders
from evaluate import evaluate_epoch
from detector import CrystallizationDetector
from config import Config

def train_one_epoch(model, loader, optimizer, criterion, device) -> float:
    model.train()
    total_loss = 0.0
    n_batches = 0
    for x, y, _ in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        n_batches += 1
    return total_loss / max(n_batches, 1)

def train(dataset_name: str, cfg: Config) -> dict:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(cfg.seed)

    model = build_resnet50(num_classes=2, pretrained=True).to(device)
    optimizer = torch.optim.SGD(
        model.parameters(), lr=cfg.lr, momentum=cfg.momentum, weight_decay=cfg.weight_decay
    )
    criterion = nn.CrossEntropyLoss()
    loaders = get_loaders(dataset_name, cfg.batch_size, cfg.data_root)

    n_epochs = cfg.epochs_waterbirds if dataset_name == "waterbirds" else cfg.epochs_celeba
    detector = CrystallizationDetector(cfg.smoothing_window)

    wga_history = []
    group_acc_history = []

    os.makedirs(cfg.checkpoint_dir, exist_ok=True)

    for epoch in tqdm(range(n_epochs), desc=f"Training {dataset_name}"):
        train_one_epoch(model, loaders["train"], optimizer, criterion, device)
        wga, group_acc = evaluate_epoch(model, loaders["val"], device)
        wga_history.append(wga)
        group_acc_history.append(group_acc)
        detector.log_epoch(wga)

        if (epoch + 1) % cfg.checkpoint_every == 0:
            ckpt_path = os.path.join(cfg.checkpoint_dir, f"{dataset_name}_epoch{epoch}.pt")
            torch.save(model.state_dict(), ckpt_path)

    return {
        "wga_history": wga_history,
        "group_acc_history": group_acc_history,
        "detector": detector
    }
