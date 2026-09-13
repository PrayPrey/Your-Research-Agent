"""TracIn Attribution using gradient dot products across checkpoints"""
import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict
from torch.utils.data import DataLoader
from tqdm import tqdm

def get_last_layer_grad(model: nn.Module, input_ids, attention_mask, labels, device: str):
    """Compute last-layer gradient for a single sample."""
    model.zero_grad()
    outputs = model(input_ids=input_ids.to(device),
                   attention_mask=attention_mask.to(device),
                   labels=labels.to(device))
    loss = outputs.loss
    loss.backward()
    for name, p in reversed(list(model.named_parameters())):
        if p.grad is not None and 'classifier' in name:
            return p.grad.view(-1).clone()
    for p in reversed(list(model.parameters())):
        if p.grad is not None:
            return p.grad.view(-1).clone()
    return None

def compute_tracin_scores(model: nn.Module, checkpoint_paths: List[str],
                           query_loader: DataLoader, train_loader: DataLoader,
                           lr: float, device: str, n_train_sample: int = 500,
                           n_query_sample: int = 100) -> np.ndarray:
    """TracIn: Sum_t lr * <grad(query), grad(train)> over checkpoints."""
    from finetune import load_checkpoint

    scores = np.zeros((n_query_sample, n_train_sample))

    for ckpt_path in checkpoint_paths:
        print(f"Processing checkpoint: {ckpt_path}")
        model = load_checkpoint(model, ckpt_path, device)
        model.eval()

        train_grads = []
        train_count = 0
        for batch in tqdm(train_loader, desc="TracIn train grads"):
            batch_size = batch["input_ids"].shape[0]
            for i in range(batch_size):
                if train_count >= n_train_sample:
                    break
                grad = get_last_layer_grad(model, batch["input_ids"][i:i+1],
                                          batch["attention_mask"][i:i+1],
                                          batch["labels"][i:i+1], device)
                if grad is not None:
                    train_grads.append(grad.cpu())
                train_count += 1
            if train_count >= n_train_sample:
                break

        train_grads = torch.stack(train_grads)

        query_count = 0
        for batch in tqdm(query_loader, desc="TracIn query grads"):
            batch_size = batch["input_ids"].shape[0]
            for i in range(batch_size):
                if query_count >= n_query_sample:
                    break
                grad = get_last_layer_grad(model, batch["input_ids"][i:i+1],
                                          batch["attention_mask"][i:i+1],
                                          batch["labels"][i:i+1], device)
                if grad is not None:
                    query_grad = grad.cpu()
                    dot_products = torch.mv(train_grads, query_grad).numpy()
                    scores[query_count] += lr * dot_products
                query_count += 1
            if query_count >= n_query_sample:
                break

    return scores

def run_checkpoint_count_ablation(model: nn.Module, checkpoint_paths: List[str],
                                   query_loader: DataLoader, train_loader: DataLoader,
                                   lr: float, device: str, counts: List[int]) -> Dict[int, np.ndarray]:
    """Run TracIn with varying checkpoint counts."""
    results = {}
    for count in counts:
        print(f"Running TracIn with {count} checkpoints")
        paths_subset = checkpoint_paths[:count]
        scores = compute_tracin_scores(model, paths_subset, query_loader, train_loader,
                                       lr, device, n_train_sample=1000, n_query_sample=100)
        results[count] = scores
    return results
