import torch
import torch.nn as nn
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import mean_squared_error

from data.loader import ZooData, make_loader
from training.train import predict_all


def eval_spearman(model: nn.Module, zoo: ZooData, split: str, batch_size: int,
                  device: str) -> tuple:
    loader = make_loader(zoo, split, batch_size, shuffle=False)
    preds, targets = predict_all(model, loader, device)
    r, p = spearmanr(preds, targets)
    return float(r), float(p)


def eval_mse(model: nn.Module, zoo: ZooData, split: str, batch_size: int,
             device: str) -> float:
    loader = make_loader(zoo, split, batch_size, shuffle=False)
    preds, targets = predict_all(model, loader, device)
    return float(mean_squared_error(targets, preds))


def gate_check(results: dict, threshold: float = 0.5) -> bool:
    """results: {name: {"test_r": float, ...}}. True if any r > threshold."""
    return any(v["test_r"] > threshold for v in results.values())


def print_results_table(results: dict, threshold: float = 0.5):
    print("\n" + "="*70)
    print(f"{'Encoder':<12} {'Val r':>10} {'Test r':>10} {'Test MSE':>12} {'Gate':>8}")
    print("-"*70)
    for name, v in results.items():
        gate_str = "PASS" if v["test_r"] > threshold else "FAIL"
        print(f"{name:<12} {v['val_r']:>10.4f} {v['test_r']:>10.4f} "
              f"{v['test_mse']:>12.6f} {gate_str:>8}")
    print("-"*70)
    gate = gate_check(results, threshold)
    print(f"H-E1 Gate: {'PASS ✓' if gate else 'FAIL ✗'}  (threshold r > {threshold})")
    print("="*70)
