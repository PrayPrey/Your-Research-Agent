"""TracIn attribution method wrapper."""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader


def run_tracin(model, train_dataset, test_subset, checkpoints, device):
    """
    Compute TracIn influence scores using gradient dot products.
    Returns: (num_test, num_train) score matrix.

    Note: Using custom implementation since captum.influence.TracInCP
    may have compatibility issues. This follows the same math:
    score[test, train] = sum_t lr_t * dot(grad_test, grad_train)
    """
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()

    num_train = len(train_dataset)
    num_test = len(test_subset)
    scores = np.zeros((num_test, num_train), dtype=np.float32)

    # Learning rates at checkpoint epochs (from config, approximate cosine schedule)
    checkpoint_lrs = [0.05, 0.02, 0.005, 0.001]
    if len(checkpoints) != len(checkpoint_lrs):
        checkpoint_lrs = [0.01] * len(checkpoints)

    # Compute test gradients for all checkpoints
    test_loader = DataLoader(test_subset, batch_size=1, shuffle=False)
    train_loader = DataLoader(train_dataset, batch_size=1, shuffle=False)

    for ckpt_idx, ckpt_path in enumerate(checkpoints):
        print(f"  TracIn checkpoint {ckpt_idx+1}/{len(checkpoints)}")
        lr_t = checkpoint_lrs[ckpt_idx]

        ckpt = torch.load(ckpt_path, map_location=device)
        model.load_state_dict(ckpt['model_state_dict'])
        model.eval()

        # Compute and cache test gradients
        test_grads = []
        for test_idx, (img, label) in enumerate(test_loader):
            img, label = img.to(device), label.to(device)
            model.zero_grad()
            output = model(img)
            loss = criterion(output, label)
            loss.backward()
            grad = torch.cat([p.grad.flatten() for p in model.parameters() if p.grad is not None])
            test_grads.append(grad)

        # Compute train gradients and dot products
        for train_idx, (img, label) in enumerate(train_loader):
            img, label = img.to(device), label.to(device)
            model.zero_grad()
            output = model(img)
            loss = criterion(output, label)
            loss.backward()
            train_grad = torch.cat([p.grad.flatten() for p in model.parameters() if p.grad is not None])

            for test_idx, test_grad in enumerate(test_grads):
                dot = torch.dot(test_grad, train_grad).item()
                scores[test_idx, train_idx] += lr_t * dot

            if (train_idx + 1) % 5000 == 0:
                print(f"    Train sample {train_idx+1}/{num_train}")

    return scores
