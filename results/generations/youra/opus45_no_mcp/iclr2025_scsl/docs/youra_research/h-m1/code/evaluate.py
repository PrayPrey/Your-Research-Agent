import torch
from torch import Tensor

def compute_wga(predictions: Tensor, labels: Tensor, groups: Tensor) -> float:
    unique_groups = torch.unique(groups)
    group_accs = []
    for g in unique_groups:
        mask = groups == g
        if mask.sum() > 0:
            acc = (predictions[mask] == labels[mask]).float().mean().item()
            group_accs.append(acc)
    return min(group_accs) if group_accs else 0.0

def compute_group_accuracies(predictions: Tensor, labels: Tensor, groups: Tensor) -> dict:
    unique_groups = torch.unique(groups)
    group_accs = {}
    for g in unique_groups:
        g_int = g.item()
        mask = groups == g
        if mask.sum() > 0:
            group_accs[g_int] = (predictions[mask] == labels[mask]).float().mean().item()
    return group_accs

@torch.no_grad()
def evaluate_epoch(model, loader, device) -> tuple:
    model.eval()
    all_preds, all_labels, all_groups = [], [], []
    for x, y, metadata in loader:
        x, y = x.to(device), y.to(device)
        groups = metadata[:, 0]
        logits = model(x)
        preds = logits.argmax(dim=1).cpu()
        all_preds.append(preds)
        all_labels.append(y.cpu())
        all_groups.append(groups)

    preds = torch.cat(all_preds)
    labels = torch.cat(all_labels)
    groups = torch.cat(all_groups)

    wga = compute_wga(preds, labels, groups)
    group_acc = compute_group_accuracies(preds, labels, groups)
    return wga, group_acc
