"""
Evaluation utilities for spurious correlation experiments
"""
import torch
import torch.nn.functional as F
import numpy as np
from collections import defaultdict


def evaluate_model(model, data_loader, device, n_groups=4):
    """Evaluate model on all groups"""
    model.eval()

    all_logits = []
    all_targets = []
    all_groups = []

    with torch.no_grad():
        for inputs, targets, groups in data_loader:
            inputs = inputs.to(device)
            logits = model(inputs)

            all_logits.append(logits.cpu())
            all_targets.append(targets)
            all_groups.append(groups)

    all_logits = torch.cat(all_logits, dim=0)
    all_targets = torch.cat(all_targets, dim=0)
    all_groups = torch.cat(all_groups, dim=0)

    # Overall accuracy
    preds = all_logits.argmax(dim=1)
    overall_acc = (preds == all_targets).float().mean().item()

    # Group-wise accuracy
    group_accs = {}
    group_counts = {}

    for g in range(n_groups):
        mask = (all_groups == g)
        if mask.sum() > 0:
            group_preds = preds[mask]
            group_targets = all_targets[mask]
            group_accs[g] = (group_preds == group_targets).float().mean().item()
            group_counts[g] = mask.sum().item()
        else:
            group_accs[g] = 0.0
            group_counts[g] = 0

    # Worst group accuracy
    worst_group_acc = min(group_accs.values())

    # Compute margins
    margins = []
    for i in range(len(all_logits)):
        target = all_targets[i]
        correct_logit = all_logits[i, target]
        other_logits = torch.cat([
            all_logits[i, :target],
            all_logits[i, target+1:]
        ])
        max_other = other_logits.max()
        margin = (correct_logit - max_other).item()
        margins.append(margin)

    avg_margin = np.mean(margins)

    results = {
        'overall_accuracy': overall_acc,
        'worst_group_accuracy': worst_group_acc,
        'group_accuracies': group_accs,
        'group_counts': group_counts,
        'avg_margin': avg_margin
    }

    return results


def compute_effective_robustness(avg_acc, worst_acc, random_baseline=0.5):
    """Compute effective robustness metric"""
    return worst_acc - (avg_acc - random_baseline)


def evaluate_all_groups(model, data_loader, device, n_groups=4):
    """Detailed evaluation across all groups"""
    model.eval()

    group_stats = defaultdict(lambda: {
        'correct': 0,
        'total': 0,
        'margins': [],
        'confidences': []
    })

    with torch.no_grad():
        for inputs, targets, groups in data_loader:
            inputs = inputs.to(device)
            logits = model(inputs)
            probs = F.softmax(logits, dim=1)

            preds = logits.argmax(dim=1).cpu()
            targets = targets.cpu()
            groups = groups.cpu()

            for i in range(len(inputs)):
                g = groups[i].item()
                target = targets[i].item()
                pred = preds[i].item()

                # Accuracy
                group_stats[g]['total'] += 1
                if pred == target:
                    group_stats[g]['correct'] += 1

                # Margin
                correct_logit = logits[i, target]
                other_logits = torch.cat([
                    logits[i, :target],
                    logits[i, target+1:]
                ])
                margin = (correct_logit - other_logits.max()).item()
                group_stats[g]['margins'].append(margin)

                # Confidence
                confidence = probs[i].max().item()
                group_stats[g]['confidences'].append(confidence)

    # Compute statistics
    results = {}
    for g in range(n_groups):
        if group_stats[g]['total'] > 0:
            acc = group_stats[g]['correct'] / group_stats[g]['total']
            avg_margin = np.mean(group_stats[g]['margins'])
            avg_conf = np.mean(group_stats[g]['confidences'])

            results[f'group_{g}_accuracy'] = acc
            results[f'group_{g}_margin'] = avg_margin
            results[f'group_{g}_confidence'] = avg_conf
            results[f'group_{g}_count'] = group_stats[g]['total']
        else:
            results[f'group_{g}_accuracy'] = 0.0
            results[f'group_{g}_margin'] = 0.0
            results[f'group_{g}_confidence'] = 0.0
            results[f'group_{g}_count'] = 0

    return results
