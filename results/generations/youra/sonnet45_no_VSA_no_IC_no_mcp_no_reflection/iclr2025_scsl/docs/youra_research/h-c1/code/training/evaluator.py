"""Evaluation utilities for worst-group accuracy."""

import torch
import numpy as np
from torch.utils.data import DataLoader
from typing import Dict


def worst_group_accuracy(
    preds: torch.Tensor,
    labels: torch.Tensor,
    groups: torch.Tensor
) -> float:
    """
    Compute min accuracy over 4 groups.

    Args:
        preds: [N,] predicted labels
        labels: [N,] true labels
        groups: [N,] group indices {0,1,2,3}

    Returns:
        worst_acc: float (0-100%)
    """
    group_accs = []
    for g in range(4):
        mask = (groups == g)
        if mask.sum() > 0:
            acc = (preds[mask] == labels[mask]).float().mean() * 100
            group_accs.append(acc.item())

    return min(group_accs) if group_accs else 0.0


def per_group_accuracy(
    preds: torch.Tensor,
    labels: torch.Tensor,
    groups: torch.Tensor
) -> np.ndarray:
    """Returns [4,] array of per-group accuracy."""
    group_accs = []
    for g in range(4):
        mask = (groups == g)
        if mask.sum() > 0:
            acc = (preds[mask] == labels[mask]).float().mean().item() * 100
        else:
            acc = 0.0
        group_accs.append(acc)

    return np.array(group_accs)


def evaluate_model(
    model: torch.nn.Module,
    dataloader: DataLoader,
    device: str
) -> Dict[str, float]:
    """
    Full evaluation on dataloader.

    Returns:
        {avg_acc, worst_group_acc, per_group_acc: [4,]}
    """
    model.eval()
    all_preds, all_labels, all_groups = [], [], []

    with torch.no_grad():
        for x, y, g in dataloader:
            x = x.to(device)
            logits = model(x)
            preds = logits.argmax(dim=1).cpu()

            all_preds.append(preds)
            all_labels.append(y)
            all_groups.append(g)

    preds = torch.cat(all_preds)
    labels = torch.cat(all_labels)
    groups = torch.cat(all_groups)

    avg_acc = (preds == labels).float().mean().item() * 100
    wg_acc = worst_group_accuracy(preds, labels, groups)
    pg_acc = per_group_accuracy(preds, labels, groups)

    return {
        'avg_acc': avg_acc,
        'worst_group_acc': wg_acc,
        'per_group_acc': pg_acc
    }
