from typing import Dict
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchmetrics import Accuracy

from config import Config


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
