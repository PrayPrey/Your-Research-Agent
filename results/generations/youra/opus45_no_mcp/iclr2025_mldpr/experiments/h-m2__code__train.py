import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from tqdm import tqdm

import config


def train_model(model, train_loader, test_loader, epochs, checkpoint_path, device='cuda'):
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(
        model.parameters(),
        lr=config.LR_INIT,
        momentum=config.MOMENTUM,
        weight_decay=config.WEIGHT_DECAY
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=config.LR_MIN)

    train_acc_curve = []
    test_acc_curve = []

    for epoch in range(epochs):
        model.train()
        correct = 0
        total = 0

        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
        for x, y in pbar:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

            correct += (out.argmax(1) == y).sum().item()
            total += y.size(0)
            pbar.set_postfix(loss=f"{loss.item():.3f}", acc=f"{100*correct/total:.1f}%")

        scheduler.step()
        train_acc = correct / total
        test_acc = evaluate_standard_accuracy(model, test_loader, device)

        train_acc_curve.append(train_acc)
        test_acc_curve.append(test_acc)

        print(f"Epoch {epoch+1}: Train Acc={train_acc:.4f}, Test Acc={test_acc:.4f}, LR={scheduler.get_last_lr()[0]:.6f}")

    save_checkpoint(model, checkpoint_path)

    return {
        "train_acc_curve": train_acc_curve,
        "test_acc_curve": test_acc_curve,
        "final_test_acc": test_acc_curve[-1]
    }


def evaluate_standard_accuracy(model, loader, device='cuda'):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            out = model(x)
            correct += (out.argmax(1) == y).sum().item()
            total += y.size(0)
    return correct / total


def save_checkpoint(model, path):
    torch.save(model.state_dict(), path)


def load_checkpoint(model, path):
    model.load_state_dict(torch.load(path, weights_only=True))
    return model
