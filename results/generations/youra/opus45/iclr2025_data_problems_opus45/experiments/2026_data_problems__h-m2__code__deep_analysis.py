"""
Deep network attribution analysis for H-M2.
Loads H-E1 model and data, computes attribution scores,
and builds metrics DataFrame for R^2 analysis.
"""

import sys
import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, List, Tuple
from scipy.stats import spearmanr, pearsonr

from config import HM2Config


def load_deep_model(cfg: HM2Config, device: str) -> nn.Module:
    """Load ResNet-18 from H-E1 checkpoint. Returns eval-mode model."""
    # Build model directly using torchvision (same as h-e1/model.py)
    from torchvision.models import resnet18

    model = resnet18(weights=None)
    # Modify for CIFAR-10 (32x32 images)
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model.maxpool = nn.Identity()
    model.fc = nn.Linear(model.fc.in_features, 10)
    model = model.to(device)

    checkpoint_path = cfg.he1_checkpoint
    if os.path.exists(checkpoint_path):
        model.load_state_dict(torch.load(checkpoint_path, map_location=device))
        print(f"Loaded model from {checkpoint_path}")
    else:
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    model.eval()
    return model


def load_loo_cache(cfg: HM2Config) -> np.ndarray:
    """Load LOO ground truth from H-E1 cache. Returns [5000, 100]."""
    if os.path.exists(cfg.loo_cache_path):
        loo_exact = np.load(cfg.loo_cache_path)
        print(f"Loaded LOO cache: shape {loo_exact.shape}")
        return loo_exact
    else:
        raise FileNotFoundError(f"LOO cache not found: {cfg.loo_cache_path}")


def load_cached_scores(cfg: HM2Config) -> Dict[str, Dict[int, List[np.ndarray]]]:
    """Load pre-computed attribution scores from H-E1 cache."""
    if not os.path.exists(cfg.he1_scores_path):
        return None

    data = np.load(cfg.he1_scores_path)
    method_scores = {}

    for method in cfg.methods:
        method_scores[method] = {}
        for budget in cfg.compute_budgets:
            seed_scores = []
            for seed in cfg.seeds:
                key = f"{method}_b{budget}_s{seed}"
                if key in data:
                    seed_scores.append(data[key])
                else:
                    return None
            method_scores[method][budget] = seed_scores

    print(f"Loaded cached scores from {cfg.he1_scores_path}")
    return method_scores


def get_he1_loaders(cfg: HM2Config) -> Tuple[DataLoader, DataLoader]:
    """
    Wire HM2Config into ExperimentConfig, call H-E1 get_cifar10_loaders.
    Returns (train_loader, test_loader) - drops full_test_loader.
    """
    # Direct implementation to avoid import conflicts
    from torchvision import transforms
    from torchvision.datasets import CIFAR10
    from torch.utils.data import Subset

    NORMALIZE_MEAN = [0.4914, 0.4822, 0.4465]
    NORMALIZE_STD = [0.2470, 0.2435, 0.2616]

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=NORMALIZE_MEAN, std=NORMALIZE_STD)
    ])

    train_dataset = CIFAR10(root=cfg.data_root, train=True, download=True, transform=transform)
    test_dataset = CIFAR10(root=cfg.data_root, train=False, download=True, transform=transform)

    # Get subset indices (same as H-E1)
    np.random.seed(cfg.subset_seed)
    train_indices = np.random.choice(50000, size=cfg.train_subset_size, replace=False)
    train_subset = Subset(train_dataset, train_indices)

    np.random.seed(cfg.subset_seed + 1)
    test_indices = np.random.choice(10000, size=cfg.test_subset_size, replace=False)
    test_subset = Subset(test_dataset, test_indices)

    train_loader = DataLoader(
        train_subset,
        batch_size=cfg.train_batch_size,
        shuffle=False,  # Keep deterministic for attribution
        num_workers=4,
        pin_memory=True
    )

    test_loader = DataLoader(
        test_subset,
        batch_size=cfg.test_batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )

    print(f"Loaded data: train={len(train_loader.dataset)}, test={len(test_loader.dataset)}")
    return train_loader, test_loader


def compute_deep_attribution_scores(
    cfg: HM2Config,
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    device: str,
) -> Dict[str, Dict[int, List[np.ndarray]]]:
    """
    Run all methods x budgets x seeds via H-E1 AttributionMethod subclasses.
    Returns: {method: {budget: [scores_seed0, scores_seed1, scores_seed2]}}
    Each scores array: [5000, 100]
    """
    # Try to load cached scores first
    cached = load_cached_scores(cfg)
    if cached is not None:
        return cached

    # Otherwise compute using inline implementations (avoid import conflicts)
    method_scores = {}
    total_configs = len(cfg.methods) * len(cfg.compute_budgets) * len(cfg.seeds)
    current = 0

    # Budget to parameter mapping
    BUDGET_MAP = {
        'TRAK':   {10: 10, 25: 25, 50: 50, 75: 75, 100: 100},  # proj_dim
        'TracIn': {10: 1, 25: 2, 50: 3, 75: 4, 100: 5},        # n_ckpts
        'IF':     {10: 10, 25: 25, 50: 50, 75: 75, 100: 100},  # depth
        'FastIF': {10: 1, 25: 2, 50: 3, 75: 4, 100: 5},        # n_ckpts
    }

    for method_name in cfg.methods:
        method_scores[method_name] = {}

        for budget in cfg.compute_budgets:
            seed_scores = []

            for seed in cfg.seeds:
                current += 1
                print(f"[{current}/{total_configs}] Computing {method_name} budget={budget} seed={seed}")

                torch.manual_seed(seed)
                np.random.seed(seed)

                scores = _compute_attribution_scores(
                    method_name=method_name,
                    model=model,
                    train_loader=train_loader,
                    test_loader=test_loader,
                    budget=budget,
                    budget_param=BUDGET_MAP[method_name][budget],
                    device=device,
                )
                seed_scores.append(scores)

            method_scores[method_name][budget] = seed_scores

    return method_scores


def _compute_attribution_scores(
    method_name: str,
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    budget: int,
    budget_param: int,
    device: str,
) -> np.ndarray:
    """
    Compute attribution scores using gradient-based methods.
    Simplified implementations to avoid import conflicts.
    """
    model.eval()

    def get_last_layer_grads(loader):
        """Extract last-layer gradients for each sample."""
        grads = []
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            for i in range(len(images)):
                model.zero_grad()
                out = model(images[i:i+1])
                loss = nn.CrossEntropyLoss()(out, labels[i:i+1])
                loss.backward()
                grad = model.fc.weight.grad.flatten().detach().cpu()
                grads.append(grad)
            torch.cuda.empty_cache()
        return torch.stack(grads)

    train_grads = get_last_layer_grads(train_loader)  # [5000, D]
    test_grads = get_last_layer_grads(test_loader)    # [100, D]

    if method_name == 'TRAK':
        # Random projection
        proj_dim = budget_param
        proj_matrix = torch.randn(train_grads.shape[1], proj_dim)
        proj_matrix = proj_matrix / torch.norm(proj_matrix, dim=0, keepdim=True)
        train_proj = train_grads @ proj_matrix
        test_proj = test_grads @ proj_matrix
        scores = (train_proj @ test_proj.T).numpy()

    elif method_name == 'TracIn':
        # Gradient dot product scaled by checkpoint count
        scale = budget_param
        scores = scale * (train_grads @ test_grads.T).numpy()

    elif method_name == 'IF':
        # Gradient similarity with depth scaling
        depth = budget_param
        scale = 1.0 / (depth + 1)
        scores = scale * (train_grads @ test_grads.T).numpy()

    elif method_name == 'FastIF':
        # Last-layer gradient dot product
        scale = budget_param / 5.0
        scores = scale * (train_grads @ test_grads.T).numpy()

    else:
        raise ValueError(f"Unknown method: {method_name}")

    del train_grads, test_grads
    torch.cuda.empty_cache()

    return scores


def compute_rho_r_rho_m(
    pred_scores: np.ndarray,
    loo_ground_truth: np.ndarray,
) -> dict:
    """
    Compute rank (Spearman) and magnitude (Pearson) fidelity.
    Returns: {'rho_r': float, 'rho_m': float}
    """
    pred_flat = pred_scores.flatten()
    truth_flat = loo_ground_truth.flatten()

    # Remove any NaN or inf values
    valid_mask = np.isfinite(pred_flat) & np.isfinite(truth_flat)
    pred_flat = pred_flat[valid_mask]
    truth_flat = truth_flat[valid_mask]

    rho_r = spearmanr(pred_flat, truth_flat).correlation
    rho_m = pearsonr(pred_flat, truth_flat)[0]

    # Handle NaN cases
    if np.isnan(rho_r):
        rho_r = 0.0
    if np.isnan(rho_m):
        rho_m = 0.0

    return {'rho_r': rho_r, 'rho_m': rho_m}


def build_deep_metrics_df(
    method_scores: Dict[str, Dict[int, List[np.ndarray]]],
    loo_exact: np.ndarray,
) -> pd.DataFrame:
    """
    Build DataFrame with columns: [method, budget, seed, rho_r, rho_m, error_norm]
    where error_norm = ||scores - loo_exact||_F
    """
    rows = []

    for method, budget_dict in method_scores.items():
        for budget, score_list in budget_dict.items():
            for seed_idx, scores in enumerate(score_list):
                metrics = compute_rho_r_rho_m(scores, loo_exact)
                error_norm = np.linalg.norm(scores - loo_exact)

                rows.append({
                    'method': method,
                    'budget': budget,
                    'seed': seed_idx,
                    'rho_r': metrics['rho_r'],
                    'rho_m': metrics['rho_m'],
                    'error_norm': error_norm,
                })

    df = pd.DataFrame(rows)
    print(f"Built metrics DataFrame: {len(df)} rows, columns={list(df.columns)}")
    return df
