import time
from typing import Dict, List, Tuple

import torch
import torch.nn.functional as F
import numpy as np

from config import Config
from models import FlattenedMLP, DWSModel, NFTModel
from data import get_dataloaders, get_weight_shapes, get_fraction_loader
from train_tracked import train_model_tracked
from metrics import macro_auc_ovr


def build_model(model_type: str, weight_shapes: List[Tuple[int, int]], cfg: Config):
    """Build model by type."""
    total_dim = sum(s[0] * s[1] for s in weight_shapes)

    if model_type == 'mlp':
        return FlattenedMLP(total_dim, cfg.mlp_hidden, cfg.num_classes, cfg.dropout)
    elif model_type == 'dws':
        return DWSModel(weight_shapes, cfg.dws_hidden, cfg.num_classes)
    elif model_type == 'nft':
        return NFTModel(weight_shapes, cfg.d_model, cfg.nhead, cfg.num_layers, cfg.num_classes)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def evaluate_auc(model, test_loader, cfg: Config) -> float:
    """Evaluate macro AUC on test set."""
    model.eval()
    all_probs = []
    all_labels = []

    with torch.no_grad():
        for weight_list, labels in test_loader:
            weight_list = [w.to(cfg.device) for w in weight_list]
            logits = model(weight_list)
            probs = F.softmax(logits, dim=1).cpu().numpy()
            all_probs.append(probs)
            all_labels.append(labels.numpy())

    all_probs = np.concatenate(all_probs)
    all_labels = np.concatenate(all_labels)

    return macro_auc_ovr(all_labels, all_probs)


def run_single(
    model_type: str,
    fraction: float,
    seed: int,
    cfg: Config,
    weight_shapes: List[Tuple[int, int]],
    train_ds,
    test_loader,
) -> Dict:
    """Run single training/eval."""
    torch.manual_seed(seed)

    model = build_model(model_type, weight_shapes, cfg)
    train_loader = get_fraction_loader(train_ds, fraction, seed, cfg)

    start = time.perf_counter()
    model, _ = train_model_tracked(model, model_type, train_loader, cfg)
    train_time = time.perf_counter() - start

    auc = evaluate_auc(model, test_loader, cfg)

    return {
        'model': model_type,
        'fraction': fraction,
        'seed': seed,
        'auc': auc,
        'train_time': train_time,
    }


def run_sweep(cfg: Config) -> Dict:
    """Run full sweep: 3 models x 3 fractions x 3 seeds."""
    train_loader_full, test_loader = get_dataloaders(cfg)
    train_ds = train_loader_full.dataset
    weight_shapes = get_weight_shapes(cfg)

    results = {}
    model_types = ['mlp', 'dws', 'nft']
    total_runs = len(cfg.fractions) * len(model_types) * len(cfg.seeds)
    run_idx = 0

    for fraction in cfg.fractions:
        results[fraction] = {}
        for model_type in model_types:
            results[fraction][model_type] = []
            for seed in cfg.seeds:
                run_idx += 1
                print(f"\n[{run_idx}/{total_runs}] {model_type} @ {fraction*100:.0f}% data, seed={seed}")
                result = run_single(model_type, fraction, seed, cfg, weight_shapes, train_ds, test_loader)
                results[fraction][model_type].append(result)
                print(f"  AUC: {result['auc']:.4f}, Time: {result['train_time']:.1f}s")

    return results
