"""TRAK Attribution using random projections"""
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

def compute_trak_scores_simple(model: nn.Module, train_loader: DataLoader,
                                query_loader: DataLoader, proj_dim: int,
                                seed: int, device: str, n_train_sample: int = 500,
                                n_query_sample: int = 100) -> np.ndarray:
    """TRAK-style random projection scoring using last-layer gradients."""
    model.eval()
    model.to(device)

    torch.manual_seed(seed)
    np.random.seed(seed)

    train_grads = []
    train_count = 0

    for batch in tqdm(train_loader, desc="TRAK featurize train"):
        input_ids = batch["input_ids"]
        attention_mask = batch["attention_mask"]
        labels = batch["labels"]

        batch_size = input_ids.shape[0]
        for i in range(batch_size):
            if train_count >= n_train_sample:
                break
            grad = get_last_layer_grad(model, input_ids[i:i+1], attention_mask[i:i+1],
                                       labels[i:i+1], device)
            if grad is not None:
                train_grads.append(grad.cpu())
            train_count += 1
        if train_count >= n_train_sample:
            break

    train_grads = torch.stack(train_grads)
    param_dim = train_grads.shape[1]

    proj_matrix = torch.randn(param_dim, proj_dim, generator=torch.Generator().manual_seed(seed)) / np.sqrt(proj_dim)
    train_features = torch.mm(train_grads, proj_matrix)

    query_features = []
    query_count = 0

    for batch in tqdm(query_loader, desc="TRAK featurize query"):
        input_ids = batch["input_ids"]
        attention_mask = batch["attention_mask"]
        labels = batch["labels"]

        batch_size = input_ids.shape[0]
        for i in range(batch_size):
            if query_count >= n_query_sample:
                break
            grad = get_last_layer_grad(model, input_ids[i:i+1], attention_mask[i:i+1],
                                       labels[i:i+1], device)
            if grad is not None:
                feat = torch.mv(proj_matrix.T, grad.cpu())
                query_features.append(feat)
            query_count += 1
        if query_count >= n_query_sample:
            break

    query_features = torch.stack(query_features)

    scores = torch.mm(query_features, train_features.T).numpy()
    return scores

def compute_trak_scores(model: nn.Module, task: str, train_loader: DataLoader,
                         query_loader: DataLoader, proj_dim: int, seed: int,
                         train_set_size: int, device: str) -> np.ndarray:
    """Compute TRAK scores using random projection."""
    return compute_trak_scores_simple(model, train_loader, query_loader, proj_dim, seed, device)

def run_trak_seed_ensemble(model: nn.Module, task: str, train_loader: DataLoader,
                            query_loader: DataLoader, proj_dim: int,
                            seeds: List[int], train_set_size: int, device: str) -> List[np.ndarray]:
    """Run TRAK with multiple seeds for cross-seed correlation."""
    results = []
    for seed in seeds:
        print(f"Running TRAK seed {seed}")
        scores = compute_trak_scores_simple(model, train_loader, query_loader, proj_dim, seed, device,
                                            n_train_sample=1000, n_query_sample=100)
        results.append(scores)
    return results

def run_proj_dim_ablation(model: nn.Module, task: str, train_loader: DataLoader,
                           query_loader: DataLoader, seeds: List[int],
                           proj_dims: List[int], train_set_size: int, device: str) -> Dict[int, np.ndarray]:
    """Run TRAK with different projection dimensions."""
    results = {}
    for proj_dim in proj_dims:
        print(f"Running TRAK proj_dim={proj_dim}")
        seed_scores = []
        for seed in seeds[:2]:
            scores = compute_trak_scores_simple(model, train_loader, query_loader, proj_dim, seed, device,
                                                n_train_sample=500, n_query_sample=50)
            seed_scores.append(scores)

        mean_scores = np.mean(seed_scores, axis=0)
        results[proj_dim] = mean_scores
    return results
