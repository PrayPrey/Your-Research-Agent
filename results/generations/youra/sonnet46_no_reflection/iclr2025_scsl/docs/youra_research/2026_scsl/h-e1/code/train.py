"""ERM training with epoch-5 checkpoint saving."""
import os
import sys
import argparse
import random
import numpy as np
import torch
import torch.nn as nn
import yaml
from torch.optim import SGD
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data.datasets import WaterBirdsDataset, CelebADataset, get_dataloader
from models.resnet import ERMModel, save_checkpoint, load_checkpoint


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def train_epoch(model: ERMModel, optimizer, dataloader, criterion, device) -> Dict[str, float]:
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for x, y, g in dataloader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * x.size(0)
        preds = logits.argmax(dim=1)
        correct += (preds == y).sum().item()
        total += x.size(0)
    return {'loss': total_loss / total, 'acc': correct / total}


def train(config_path: str, dataset_name: str, output_dir: str,
          stop_after_epoch: int = 5) -> str:
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    set_seed(cfg['training']['seed'])
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    data_root = cfg['dataset']['root']
    aug = cfg['dataset'].get('augment', True)
    bs = cfg['training']['batch_size']
    lr = cfg['training']['lr']
    wd = cfg['training']['weight_decay']
    momentum = cfg['training']['momentum']

    if dataset_name == 'waterbirds':
        train_dataset = WaterBirdsDataset(data_root, 'train', augment=aug)
    elif dataset_name == 'celeba':
        train_dataset = CelebADataset(data_root, 'train', augment=aug)
    else:
        raise ValueError(f'Unknown dataset: {dataset_name}')

    loader = get_dataloader(train_dataset, bs, shuffle=True, num_workers=4)
    model = ERMModel(num_classes=cfg['dataset']['num_classes'],
                     pretrained=cfg['training'].get('pretrained', True))
    model = model.to(device)

    optimizer = SGD(model.parameters(), lr=lr, momentum=momentum, weight_decay=wd)
    criterion = nn.CrossEntropyLoss()

    os.makedirs(output_dir, exist_ok=True)
    last_ckpt = None
    for epoch in range(1, stop_after_epoch + 1):
        metrics = train_epoch(model, optimizer, loader, criterion, device)
        ckpt_path = os.path.join(output_dir, f'epoch_{epoch:03d}.pt')
        save_checkpoint(model, optimizer, epoch, ckpt_path)
        last_ckpt = ckpt_path
        print(f'Epoch {epoch}: loss={metrics["loss"]:.4f}, acc={metrics["acc"]:.4f}')

    return last_ckpt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--dataset', required=True, choices=['waterbirds', 'celeba'])
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--stop_epoch', type=int, default=5)
    args = parser.parse_args()
    ckpt = train(args.config, args.dataset, args.output_dir, args.stop_epoch)
    print(f'Checkpoint saved: {ckpt}')


if __name__ == '__main__':
    main()
