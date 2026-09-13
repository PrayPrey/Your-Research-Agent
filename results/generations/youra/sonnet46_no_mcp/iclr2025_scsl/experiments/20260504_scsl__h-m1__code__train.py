import os
import random
import numpy as np
import torch
import torch.nn as nn
from torch.optim import SGD
from torchvision import models
from tqdm import tqdm
from typing import Dict, Any, TYPE_CHECKING

from config import TrainConfig
from data.waterbirds import get_waterbirds_loader  # H-M1 uses Waterbirds only

if TYPE_CHECKING:
    from gradient_analyzer import GradientAlignmentAnalyzer


def build_model(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    model = models.resnet50(pretrained=pretrained)
    model.fc = nn.Linear(2048, num_classes)
    return model


def train_one_seed(
    cfg: TrainConfig,
    seed: int,
    device: str,
    analyzer: "GradientAlignmentAnalyzer",
) -> Dict[str, Any]:
    """Trains ResNet-50 ERM with gradient logging at checkpoint epochs."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)

    ckpt_dir = os.path.join(cfg.checkpoint_dir, f"seed_{seed}")
    os.makedirs(ckpt_dir, exist_ok=True)

    train_loader = get_waterbirds_loader(
        cfg.data_root, "train", cfg.batch_size, cfg.num_workers, augment=True
    )

    model = build_model().to(device)
    # Share model with analyzer
    analyzer.model = model

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
            result = analyzer.log_epoch_gradients(train_loader, criterion)
            if epoch % 10 == 0:
                avg_loss = total_loss / len(train_loader)
                print(f"    Epoch {epoch}/{cfg.epochs}  loss={avg_loss:.4f}  GDR={result['gdr']:.4f}")

    history = analyzer.get_history()
    print(f"  Seed {seed}: done. GDR checkpoints: {len(history['gdr_series'])}")

    return {
        "seed": seed,
        "gdr_series": history["gdr_series"],
        "spurious_grad_norms": history["spurious_grad_norms"],
        "core_grad_norms": history["core_grad_norms"],
    }


def main(cfg: TrainConfig, device: str) -> Dict[int, Dict[str, Any]]:
    """Runs train_one_seed for each seed. Returns {seed: result_dict}."""
    from gradient_analyzer import GradientAlignmentAnalyzer

    print(f"Training ERM on {cfg.dataset} | seeds={cfg.seeds} | epochs={cfg.epochs}")
    results = {}
    for seed in cfg.seeds:
        # Create fresh analyzer per seed
        placeholder_model = build_model().to(device)
        analyzer = GradientAlignmentAnalyzer(placeholder_model, device)
        results[seed] = train_one_seed(cfg, seed, device, analyzer)
    return results
