import torch
import torch.nn as nn
from torch.utils.data import DataLoader


def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> float:
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            out = model(x)
            correct += (out.argmax(dim=1) == y).sum().item()
            total += x.size(0)
    return 100.0 * correct / total


def compute_generalization_gap(model: nn.Module, in_domain_loader: DataLoader,
                                held_out_loader: DataLoader, device: torch.device) -> dict:
    in_acc = evaluate(model, in_domain_loader, device)
    held_acc = evaluate(model, held_out_loader, device)
    return {
        "in_domain_acc": in_acc,
        "held_out_acc": held_acc,
        "gap": in_acc - held_acc,
    }
