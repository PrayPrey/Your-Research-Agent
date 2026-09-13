"""Finetuning with per-epoch checkpoints for TracIn"""
import torch
import torch.nn as nn
from torch.optim import AdamW
from tqdm import tqdm
import os
from typing import List

def finetune(model, train_loader, epochs, lr, device):
    model = model.to(device)
    model.train()
    optimizer = AdamW(model.parameters(), lr=lr)

    for epoch in range(epochs):
        total_loss = 0
        for batch in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"Epoch {epoch+1} avg loss: {total_loss / len(train_loader):.4f}")

    return model

def finetune_with_checkpoints(model: nn.Module, train_loader, epochs: int, lr: float,
                               device: str, ckpt_dir: str, ckpt_prefix: str) -> List[str]:
    """Train epochs, save state_dict after each. Returns list of checkpoint paths."""
    model = model.to(device)
    model.train()
    optimizer = AdamW(model.parameters(), lr=lr)
    os.makedirs(ckpt_dir, exist_ok=True)
    paths = []

    for epoch in range(epochs):
        total_loss = 0
        for batch in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch+1} avg loss: {avg_loss:.4f}")

        path = os.path.join(ckpt_dir, f"{ckpt_prefix}_epoch{epoch+1}.pt")
        save_checkpoint(model, path)
        paths.append(path)

    return paths

def save_checkpoint(model, path):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    torch.save(model.state_dict(), path)

def load_checkpoint(model, path, device):
    model.load_state_dict(torch.load(path, map_location=device, weights_only=True))
    return model
