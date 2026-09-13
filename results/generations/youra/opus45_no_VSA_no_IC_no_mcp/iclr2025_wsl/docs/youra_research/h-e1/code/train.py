from typing import Dict

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchmetrics import Accuracy

from config import Config


def train_model(model: nn.Module, train_loader: DataLoader, cfg: Config) -> nn.Module:
    model = model.to(cfg.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.cosine_t_max)
    criterion = nn.CrossEntropyLoss()

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
            optimizer.step()
            total_loss += loss.item()

        scheduler.step()

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{cfg.epochs}, Loss: {total_loss/len(train_loader):.4f}")

    return model


def evaluate(model: nn.Module, test_loader: DataLoader, cfg: Config) -> Dict:
    model.eval()
    accuracy_metric = Accuracy(task="multiclass", num_classes=cfg.num_classes).to(cfg.device)

    with torch.no_grad():
        for weight_list, labels in test_loader:
            weight_list = [w.to(cfg.device) for w in weight_list]
            labels = labels.to(cfg.device)
            logits = model(weight_list)
            accuracy_metric.update(logits, labels)

    acc = accuracy_metric.compute().item()
    return {"accuracy": acc}
