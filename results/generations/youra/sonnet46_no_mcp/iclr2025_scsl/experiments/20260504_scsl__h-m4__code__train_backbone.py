import os
import random
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from typing import Dict

from config import ExperimentConfig
from data.waterbirds import get_waterbirds_loader


def build_model(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    model = models.resnet50(pretrained=pretrained)
    model.fc = nn.Linear(2048, num_classes)
    return model


def get_transforms(augment: bool):
    if augment:
        return transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])
    else:
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])


class BackboneTrainer:
    def __init__(self, cfg: ExperimentConfig, device: str):
        self.cfg = cfg
        self.device = device

    def train_seed(self, seed: int) -> Dict[int, str]:
        torch.manual_seed(seed)
        np.random.seed(seed)
        random.seed(seed)

        ckpt_dir = os.path.join(self.cfg.paths.checkpoint_dir, f"seed_{seed}")
        os.makedirs(ckpt_dir, exist_ok=True)

        # Skip if all checkpoints already exist
        if all(self._checkpoint_exists(epoch, seed)
               for epoch in self.cfg.train.checkpoint_epochs):
            print(f"Seed {seed}: all checkpoints exist, skipping training")
            return {epoch: self._checkpoint_path(epoch, seed)
                    for epoch in self.cfg.train.checkpoint_epochs}

        model = build_model(num_classes=2, pretrained=True).to(self.device)
        optimizer = torch.optim.SGD(
            model.parameters(),
            lr=self.cfg.train.lr,
            momentum=self.cfg.train.momentum,
            weight_decay=self.cfg.train.weight_decay,
        )
        criterion = nn.CrossEntropyLoss()

        train_loader = get_waterbirds_loader(
            root=self.cfg.train.data_root,
            split="train",
            batch_size=self.cfg.train.batch_size,
            num_workers=self.cfg.train.num_workers,
            augment=True,
        )

        result = {}
        checkpoint_epochs_set = set(self.cfg.train.checkpoint_epochs)

        for epoch in range(1, self.cfg.train.max_epochs + 1):
            model.train()
            total_loss = 0.0
            for batch in train_loader:
                imgs = batch["image"].to(self.device)
                labels = batch["core_label"].to(self.device)
                optimizer.zero_grad()
                outputs = model(imgs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            if epoch in checkpoint_epochs_set:
                path = self._save_checkpoint(model, epoch, seed, ckpt_dir)
                result[epoch] = path
                avg_loss = total_loss / len(train_loader)
                print(f"Checkpoint saved: epoch {epoch} → {path} (loss={avg_loss:.4f})")

        return result

    def _save_checkpoint(self, model: nn.Module, epoch: int,
                         seed: int, ckpt_dir: str) -> str:
        path = os.path.join(ckpt_dir, f"epoch_{epoch:03d}.pt")
        torch.save(model.state_dict(), path)
        assert os.path.exists(path), f"Checkpoint not saved: {path}"
        return os.path.abspath(path)

    def _checkpoint_exists(self, epoch: int, seed: int) -> bool:
        return os.path.exists(self._checkpoint_path(epoch, seed))

    def _checkpoint_path(self, epoch: int, seed: int) -> str:
        return os.path.abspath(os.path.join(
            self.cfg.paths.checkpoint_dir, f"seed_{seed}", f"epoch_{epoch:03d}.pt"
        ))
