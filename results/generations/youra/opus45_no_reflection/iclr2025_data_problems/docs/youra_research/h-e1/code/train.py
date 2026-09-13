"""Training loop for H-E1 experiment."""

import os
import random
from typing import Dict, List

import numpy as np
import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader
from tqdm import tqdm
from transformers import PreTrainedModel, get_linear_schedule_with_warmup

from model import build_bert, build_gpt2


def set_seed(seed: int):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_model(
    model: PreTrainedModel,
    train_loader: DataLoader,
    seed: int,
    epochs: int = 3,
    lr: float = 2e-5,
    device: str = "cuda",
) -> PreTrainedModel:
    """Fine-tune model with AdamW optimizer."""
    set_seed(seed)
    model = model.to(device)
    model.train()

    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    total_steps = epochs * len(train_loader)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=int(0.1 * total_steps), num_training_steps=total_steps
    )

    for epoch in range(epochs):
        total_loss = 0
        for batch in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
            batch = {k: v.to(device) for k, v in batch.items()}

            outputs = model(**batch)
            loss = outputs.loss

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch+1}: avg_loss = {avg_loss:.4f}")

    return model


def run_all_seeds(
    model_name: str,
    train_loader: DataLoader,
    seeds: List[int] = [42, 43, 44, 45, 46],
    ckpt_dir: str = "checkpoints",
    device: str = "cuda",
) -> Dict[int, PreTrainedModel]:
    """Train model for all seeds and save checkpoints."""
    os.makedirs(ckpt_dir, exist_ok=True)
    models = {}

    for seed in seeds:
        print(f"\n{'='*60}")
        print(f"Training {model_name} with seed {seed}")
        print(f"{'='*60}")

        set_seed(seed)
        if model_name == "bert":
            model, _ = build_bert()
        else:
            model, _ = build_gpt2()

        model = train_model(model, train_loader, seed, device=device)

        ckpt_path = os.path.join(ckpt_dir, f"{model_name}_seed{seed}.pt")
        torch.save(model.state_dict(), ckpt_path)
        print(f"Saved checkpoint: {ckpt_path}")

        models[seed] = model

    return models
