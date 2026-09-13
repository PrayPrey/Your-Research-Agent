"""Generalization gap evaluation for H-M3"""

import torch
from torch.utils.data import DataLoader

from config import BENCHMARKS, TRAIN_CONFIG


def evaluate_accuracy(model, dataloader, device=None):
    """
    Token-level top-1 accuracy on non-padded positions.
    """
    if device is None:
        device = next(model.parameters()).device

    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            attention_mask = batch.get("attention_mask")
            if attention_mask is not None:
                attention_mask = attention_mask.to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)

            preds = outputs.logits[..., :-1, :].argmax(-1)
            target = labels[..., 1:]

            mask = target != -100
            if attention_mask is not None:
                mask = mask & (attention_mask[..., 1:].bool())

            correct += ((preds == target) & mask).sum().item()
            total += mask.sum().item()

    return correct / max(total, 1)


def compute_generalization_gap(model, train_loader, test_loader, device=None):
    """
    Compute train/test accuracy and generalization gap.
    Returns {'train_acc', 'test_acc', 'gen_gap': train_acc - test_acc}
    """
    train_acc = evaluate_accuracy(model, train_loader, device)
    test_acc = evaluate_accuracy(model, test_loader, device)

    return {
        "train_acc": train_acc,
        "test_acc": test_acc,
        "gen_gap": train_acc - test_acc,
    }
