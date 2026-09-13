import os
import json
import argparse
import random
import numpy as np
import torch
import torch.nn as nn
from torch.optim import SGD
from torch.optim.lr_scheduler import MultiStepLR
from torch.utils.data import DataLoader

from config import CONFIG
from data import load_cifar10, load_svhn, make_loader
from model import build_resnet18


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def train_epoch(model: nn.Module, loader: DataLoader, optimizer, criterion, device) -> tuple:
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        out = model(x)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * x.size(0)
        correct += (out.argmax(dim=1) == y).sum().item()
        total += x.size(0)
    return total_loss / total, 100.0 * correct / total


def train_one_condition(condition: str, config: dict) -> str:
    device = torch.device(config['device'] if torch.cuda.is_available() else 'cpu')
    set_seed(config['seed'])

    if condition == 'cifar10':
        mean, std = config['cifar10_norm']
        train_ds, _ = load_cifar10(config['data_root'], mean, std)
    else:
        mean, std = config['svhn_norm']
        train_ds, _, _ = load_svhn(config['data_root'], mean, std)

    train_loader = make_loader(train_ds, config['batch_size'], shuffle=True)
    model = build_resnet18(config['num_classes']).to(device)
    optimizer = SGD(model.parameters(), lr=config['lr'], momentum=config['momentum'],
                    weight_decay=config['weight_decay'])
    scheduler = MultiStepLR(optimizer, milestones=config['lr_milestones'], gamma=config['lr_gamma'])
    criterion = nn.CrossEntropyLoss()

    history = []
    for epoch in range(config['epochs']):
        loss, acc = train_epoch(model, train_loader, optimizer, criterion, device)
        scheduler.step()
        history.append({"epoch": epoch, "loss": loss, "acc": acc})
        if (epoch + 1) % 20 == 0:
            print(f"[{condition}] Epoch {epoch+1}/{config['epochs']}: loss={loss:.4f}, acc={acc:.2f}%")

    os.makedirs(config['checkpoint_dir'], exist_ok=True)
    ckpt_path = os.path.join(config['checkpoint_dir'], f"{condition}.pt")
    torch.save(model.state_dict(), ckpt_path)

    hist_path = os.path.join(config['checkpoint_dir'], f"{condition}_history.json")
    with open(hist_path, 'w') as f:
        json.dump(history, f, indent=2)

    return ckpt_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--condition', required=True, choices=['cifar10', 'svhn'])
    args = parser.parse_args()
    ckpt = train_one_condition(args.condition, CONFIG)
    print(f"Checkpoint saved: {ckpt}")


if __name__ == '__main__':
    main()
