"""
Evaluation utilities for spurious correlation experiments.
"""
import torch
import numpy as np
from collections import defaultdict


def evaluate(model, dataloader, device, n_groups=4):
    """
    Evaluate model on dataloader.
    Returns: dict with overall accuracy, worst-group accuracy, per-group accuracies.
    """
    model.eval()

    group_correct = defaultdict(int)
    group_total = defaultdict(int)
    total_correct = 0
    total_samples = 0

    with torch.no_grad():
        for batch in dataloader:
            if len(batch) == 3:
                inputs, targets, groups = batch
            else:
                inputs, targets = batch
                groups = torch.zeros(len(targets), dtype=torch.long)

            inputs = inputs.to(device)
            targets = targets.to(device)
            groups = groups.to(device)

            logits = model(inputs)
            preds = logits.argmax(1)
            correct = (preds == targets)

            for g in range(n_groups):
                mask = (groups == g)
                if mask.sum() > 0:
                    group_correct[g] += correct[mask].sum().item()
                    group_total[g] += mask.sum().item()

            total_correct += correct.sum().item()
            total_samples += len(targets)

    overall_acc = total_correct / max(total_samples, 1)

    per_group_acc = {}
    for g in range(n_groups):
        if group_total[g] > 0:
            per_group_acc[g] = group_correct[g] / group_total[g]
        else:
            per_group_acc[g] = 0.0

    worst_group_acc = min(per_group_acc.values()) if per_group_acc else 0.0

    return {
        'overall_acc': overall_acc,
        'worst_group_acc': worst_group_acc,
        'per_group_acc': per_group_acc,
        'group_sizes': {g: group_total[g] for g in range(n_groups)},
    }


def compute_group_gap(per_group_acc):
    """Gap between best and worst group accuracy."""
    accs = list(per_group_acc.values())
    return max(accs) - min(accs)
