import os
import random
import numpy as np
import torch
import torch.nn as nn
from torch.optim import SGD
from torchvision import models, transforms
from tqdm import tqdm

from config import TrainConfig
from data.waterbirds import get_waterbirds_loader
from data.celeba import get_celeba_loader


def get_transforms(augment: bool) -> transforms.Compose:
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    if augment:
        return transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ])
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])


def build_model(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    model = models.resnet50(pretrained=pretrained)
    model.fc = nn.Linear(2048, num_classes)
    return model


def train_one_seed(cfg: TrainConfig, seed: int, device: str) -> None:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)

    ckpt_dir = os.path.join(cfg.checkpoint_dir, f"seed_{seed}")
    os.makedirs(ckpt_dir, exist_ok=True)

    if cfg.dataset == "waterbirds":
        train_loader = get_waterbirds_loader(
            cfg.data_root, "train", cfg.batch_size, cfg.num_workers, augment=True
        )
    elif cfg.dataset == "celeba":
        train_loader = get_celeba_loader(
            cfg.data_root, "train", cfg.batch_size, cfg.num_workers, augment=True
        )
    else:
        raise ValueError(f"Unknown dataset: {cfg.dataset}")

    model = build_model().to(device)
    optimizer = SGD(
        model.parameters(),
        lr=cfg.lr,
        momentum=cfg.momentum,
        weight_decay=cfg.weight_decay,
    )
    criterion = nn.CrossEntropyLoss()

    print(f"  Seed {seed}: training {cfg.epochs} epochs on {cfg.dataset}")
    for epoch in range(1, cfg.epochs + 1):
        model.train()
        total_loss = 0.0
        for batch in train_loader:
            images = batch["image"].to(device)
            labels = batch["core_label"].to(device)
            optimizer.zero_grad()
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if epoch % cfg.checkpoint_interval == 0:
            ckpt_path = os.path.join(ckpt_dir, f"epoch_{epoch:03d}.pt")
            torch.save(model.state_dict(), ckpt_path)

        if epoch % 10 == 0:
            avg_loss = total_loss / len(train_loader)
            print(f"    Epoch {epoch}/{cfg.epochs}  loss={avg_loss:.4f}")

    print(f"  Seed {seed}: done. Checkpoints in {ckpt_dir}")


def main(cfg: TrainConfig, device: str) -> None:
    print(f"Training ERM on {cfg.dataset} | seeds={cfg.seeds} | epochs={cfg.epochs}")
    for seed in cfg.seeds:
        train_one_seed(cfg, seed, device)
