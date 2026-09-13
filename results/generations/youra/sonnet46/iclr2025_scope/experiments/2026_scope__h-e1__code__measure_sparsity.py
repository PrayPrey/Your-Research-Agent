from typing import List
import numpy as np
import torch
from torch.utils.data import DataLoader
from config import ExperimentConfig


def register_hooks(
    model,
    epsilon: float,
    layer_counts: List[List[float]],
) -> List:
    """Register gate_proj forward hooks on all 32 MLP layers using closure factory."""
    hooks = []
    for i in range(len(model.model.layers)):
        layer_module = model.model.layers[i].mlp.gate_proj

        def make_hook(layer_idx):
            def hook_fn(module, input, output):
                # output: [B, seq_len, 14336]
                sparsity_val = (output.abs() < epsilon).float().mean().item()
                layer_counts[layer_idx].append(sparsity_val)
            return hook_fn

        handle = layer_module.register_forward_hook(make_hook(i))
        hooks.append(handle)

    return hooks


def measure_layer_sparsity(
    model,
    dataloader: DataLoader,
    epsilon: float,
    cfg: ExperimentConfig,
) -> np.ndarray:
    """Run forward passes with hooks; return per-layer mean sparsity. Returns shape (32,)."""
    n_layers = cfg.n_layers
    layer_counts = [[] for _ in range(n_layers)]
    hooks = register_hooks(model, epsilon, layer_counts)

    try:
        model.eval()
        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch["input_ids"].to(model.device)
                model(input_ids)
    finally:
        for h in hooks:
            h.remove()

    layer_sparsity = np.array([np.mean(layer_counts[i]) if layer_counts[i] else 0.0
                                for i in range(n_layers)])
    assert len(layer_sparsity) == n_layers, "Not all hooks fired"
    assert layer_sparsity.mean() > 0.0, "Zero sparsity detected — check epsilon value"

    return layer_sparsity


def run_all_conditions(
    model,
    alpaca_short: DataLoader,
    alpaca_long: DataLoader,
    wikitext_long: DataLoader,
    cfg: ExperimentConfig,
) -> dict:
    """Sweep 3 datasets × 4 epsilons = 12 measurements."""
    results = {}

    dataset_configs = [
        ("alpaca",   alpaca_short,   cfg.short_length),
        ("alpaca",   alpaca_long,    cfg.long_length),
        ("wikitext", wikitext_long,  cfg.long_length),
    ]

    for eps in cfg.epsilons:
        for (dataset_name, dataloader, length) in dataset_configs:
            key = (dataset_name, eps, length)
            print(f"  Measuring: dataset={dataset_name}, eps={eps}, length={length}")
            layer_sparsity = measure_layer_sparsity(model, dataloader, eps, cfg)
            results[key] = layer_sparsity

    return results


def verify_mechanism(layer_sparsity: np.ndarray, cfg: ExperimentConfig):
    """Basic sanity check on sparsity measurement output."""
    indicators = {
        "len_ok": len(layer_sparsity) == cfg.n_layers,
        "mean_positive": float(layer_sparsity.mean()) > 0,
        "std_nonzero": float(layer_sparsity.std()) > 0.01,
        "mean_value": float(layer_sparsity.mean()),
        "std_value": float(layer_sparsity.std()),
    }
    all_passed = indicators["len_ok"] and indicators["mean_positive"] and indicators["std_nonzero"]
    return all_passed, indicators
