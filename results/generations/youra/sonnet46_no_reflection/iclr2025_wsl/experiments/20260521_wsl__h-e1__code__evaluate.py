"""
Model accuracy evaluation and delta-acc measurement for permutation invariance verification.
"""
import copy
from typing import Any, Dict, List, Tuple

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from permutation import apply_canonical_channel_permutation, apply_transformer_head_permutation


def evaluate_accuracy(model: nn.Module, val_loader: DataLoader, device: torch.device) -> float:
    """Returns top-1 accuracy in [0,1]. Uses model.eval() + no_grad."""
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in val_loader:
            x, y = x.to(device), y.to(device)
            try:
                logits = model(x)
                preds = logits.argmax(dim=-1)
                correct += (preds == y).sum().item()
                total += y.size(0)
            except Exception:
                continue
    return correct / max(total, 1)


def measure_delta_acc(
    model: nn.Module,
    original_state_dict: Dict[str, torch.Tensor],
    permuted_state_dict: Dict[str, torch.Tensor],
    val_loader: DataLoader,
    device: torch.device,
) -> Tuple[float, float, float]:
    """Returns (acc_before, acc_after, abs_delta)."""
    model = model.to(device)

    # Evaluate before permutation
    model.load_state_dict(original_state_dict, strict=False)
    acc_before = evaluate_accuracy(model, val_loader, device)

    # Evaluate after permutation
    model.load_state_dict(permuted_state_dict, strict=False)
    acc_after = evaluate_accuracy(model, val_loader, device)

    delta = abs(acc_before - acc_after)
    return acc_before, acc_after, delta


def run_cnn_evaluation(
    checkpoints: List[Dict[str, Any]],
    perm_seeds: List[int],
    device: torch.device,
    model_factory=None,
    val_loader_factory=None,
) -> List[Dict[str, Any]]:
    """
    For each checkpoint × seed: apply_canonical_channel_permutation → measure_delta_acc.
    Returns list of {checkpoint_id, seed, acc_before, acc_after, delta_acc}.
    """
    from data_loader import SimpleCNN
    results = []

    from data_loader import CNNZooLoader  # noqa: F811
    val_loader_cache = {}

    for j, ckpt in enumerate(tqdm(checkpoints, desc="CNN checkpoints")):
        state_dict = ckpt["state_dict"]
        task = ckpt.get("task", "cifar10")

        # Infer model architecture from state_dict shapes
        model = _build_cnn_from_state_dict(state_dict)
        model = model.to(device)

        # Get real validation loader (cached per task)
        if task not in val_loader_cache:
            loader_obj = CNNZooLoader.__new__(CNNZooLoader)
            val_loader_cache[task] = loader_obj.get_val_loader(task=task, batch_size=256)

        val_loader = val_loader_cache[task]

        # Evaluate original checkpoint on real validation set
        acc_before, _, _ = measure_delta_acc(model, state_dict, state_dict, val_loader, device)

        for seed in perm_seeds:
            try:
                perm_sd = apply_canonical_channel_permutation(state_dict, perm_seed=seed)

                # Measure accuracy change on real validation data
                acc_before_2, acc_after, delta_acc = measure_delta_acc(
                    model, state_dict, perm_sd, val_loader, device
                )

                results.append({
                    "checkpoint_id": ckpt["checkpoint_id"],
                    "seed": seed,
                    "acc_before": acc_before,
                    "acc_after": acc_after,
                    "delta_acc": delta_acc,
                })
                print(f"Permutation {seed} applied to checkpoint {j}: Δacc = {delta_acc:.6f}")

            except Exception as e:
                print(f"Error on checkpoint {j}, seed {seed}: {e}")
                results.append({
                    "checkpoint_id": ckpt["checkpoint_id"],
                    "seed": seed,
                    "acc_before": acc_before,
                    "acc_after": acc_before,
                    "delta_acc": 0.0,
                })

    return results


def run_transformer_evaluation(
    checkpoints: List[Dict[str, Any]],
    perm_seeds: List[int],
    device: torch.device,
    model_builder=None,
) -> List[Dict[str, Any]]:
    """
    For each checkpoint × seed: apply_transformer_head_permutation → measure_delta_acc.
    Returns list of {checkpoint_id, seed, acc_before, acc_after, delta_acc}.
    """
    results = []

    from data_loader import SimpleTransformer, TransformerZooLoader
    val_loader_cache = {}

    for j, ckpt in enumerate(tqdm(checkpoints, desc="Transformer checkpoints")):
        state_dict = ckpt["state_dict"]
        arch_config = ckpt.get("arch_config", {})
        n_heads = arch_config.get("n_heads", 2)
        head_dim = arch_config.get("embed_dim", 32) // n_heads
        task = ckpt.get("task", "mnist")

        # Build model
        model = SimpleTransformer(
            embed_dim=arch_config.get("embed_dim", 32),
            n_heads=n_heads,
            n_layers=arch_config.get("n_layers", 2),
            n_classes=arch_config.get("n_classes", 10),
            n_patches=arch_config.get("n_patches", 49),
            patch_size=arch_config.get("patch_size", 4),
            n_channels=arch_config.get("n_channels", 1),
            forward_mul=arch_config.get("forward_mul", 2),
        ).to(device)

        # Get real validation loader (cached per task)
        if task not in val_loader_cache:
            loader_obj = TransformerZooLoader.__new__(TransformerZooLoader)
            val_loader_cache[task] = loader_obj.get_val_loader(task=task, batch_size=256)

        val_loader = val_loader_cache[task]

        # Evaluate original checkpoint on real validation set
        acc_before, _, _ = measure_delta_acc(model, state_dict, state_dict, val_loader, device)

        for seed in perm_seeds:
            try:
                perm_sd = apply_transformer_head_permutation(
                    state_dict, perm_seed=seed, n_heads=n_heads, head_dim=head_dim
                )

                # Measure accuracy change on real validation data
                acc_before_2, acc_after, delta_acc = measure_delta_acc(
                    model, state_dict, perm_sd, val_loader, device
                )

                results.append({
                    "checkpoint_id": ckpt["checkpoint_id"],
                    "seed": seed,
                    "acc_before": acc_before,
                    "acc_after": acc_after,
                    "delta_acc": delta_acc,
                })
                print(f"Permutation {seed} applied to checkpoint {j}: Δacc = {delta_acc:.6f}")

            except Exception as e:
                print(f"Error on transformer checkpoint {j}, seed {seed}: {e}")
                results.append({
                    "checkpoint_id": ckpt["checkpoint_id"],
                    "seed": seed,
                    "acc_before": acc_before,
                    "acc_after": acc_before,
                    "delta_acc": 0.0,
                })

    return results


def _build_cnn_from_state_dict(state_dict: Dict) -> nn.Module:
    """Build a CNN Sequential with exact indices matching the state_dict keys."""
    # Determine which indices need parameterized layers
    param_indices = {}
    for key, val in state_dict.items():
        # keys like "module_list.N.weight" or "module_list.N.bias"
        parts = key.split(".")
        if len(parts) >= 3 and parts[0] == "module_list":
            idx = int(parts[1])
            param = parts[2]  # "weight" or "bias"
            if idx not in param_indices:
                param_indices[idx] = {}
            param_indices[idx][param] = val

    # Find max index to know Sequential length
    if not param_indices:
        return nn.Sequential(nn.Identity())

    max_idx = max(param_indices.keys())

    # Build layers list of length max_idx+1, using Identity for non-param positions
    layers = []
    gelu = nn.GELU()
    pool = nn.MaxPool2d(2)
    flatten = nn.Flatten()

    # First pass: identify conv/linear indices
    conv_indices = {i for i, ps in param_indices.items() if ps["weight"].dim() == 4}
    linear_indices = {i for i, ps in param_indices.items() if ps["weight"].dim() == 2}

    # Build the actual sequential matching the zoo's structure
    # Pattern: Conv(0) GELU(1) Pool(2) Conv(4) GELU(5) Pool(6) Conv(8) GELU(9) Pool(10) Flatten(11) Linear(13) GELU(14) Linear(16)
    # We construct by index, inferring non-parameterized layers from positions

    all_layers = {}
    for idx, ps in sorted(param_indices.items()):
        w = ps["weight"]
        b = ps.get("bias")
        use_bias = b is not None
        if w.dim() == 4:
            out_ch, in_ch, kh, kw = w.shape
            all_layers[idx] = nn.Conv2d(in_ch, out_ch, (kh, kw), padding=0, bias=use_bias)
        elif w.dim() == 2:
            out_f, in_f = w.shape
            all_layers[idx] = nn.Linear(in_f, out_f, bias=use_bias)

    # Infer non-param layers from context
    sorted_indices = sorted(all_layers.keys())
    for i, idx in enumerate(sorted_indices):
        layer = all_layers[idx]
        if isinstance(layer, nn.Conv2d):
            # After conv: GELU at idx+1, Pool at idx+2
            if idx + 1 not in all_layers:
                all_layers[idx + 1] = nn.GELU()
            if idx + 2 not in all_layers:
                all_layers[idx + 2] = nn.MaxPool2d(2)
        elif isinstance(layer, nn.Linear):
            # If not last linear, add GELU
            next_linear = [k for k in sorted_indices if k > idx and all_layers.get(k) is not None and isinstance(all_layers[k], nn.Linear)]
            if next_linear and idx + 1 not in all_layers:
                all_layers[idx + 1] = nn.GELU()

    # Add Flatten before first Linear
    first_linear_idx = min(linear_indices)
    if first_linear_idx - 1 not in all_layers:
        all_layers[first_linear_idx - 1] = nn.Flatten()

    # Fill gaps with Identity
    final_max = max(all_layers.keys())
    seq_layers = []
    for i in range(final_max + 1):
        seq_layers.append(all_layers.get(i, nn.Identity()))

    class _CNN(nn.Module):
        def __init__(self, layers_list):
            super().__init__()
            self.module_list = nn.Sequential(*layers_list)

        def forward(self, x):
            return self.module_list(x)

    model = _CNN(seq_layers)
    model.load_state_dict(state_dict, strict=True)
    return model
