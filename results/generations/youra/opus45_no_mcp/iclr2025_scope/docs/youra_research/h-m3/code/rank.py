"""LoRA effective rank computation via SVD for H-M3"""

import torch
from config import RANK_CONFIG


def extract_lora_matrices(model):
    """
    Walk peft-wrapped model to extract lora_A/lora_B weight pairs.
    Returns {module_name: (lora_A_weight, lora_B_weight)}
    """
    import torch.nn as nn
    matrices = {}

    for name, module in model.named_modules():
        if hasattr(module, "lora_A") and hasattr(module, "lora_B"):
            lora_A = module.lora_A
            lora_B = module.lora_B

            A_weight = None
            B_weight = None

            if isinstance(lora_A, nn.ModuleDict) and "default" in lora_A:
                A_weight = lora_A["default"].weight.data.detach()
            elif isinstance(lora_A, dict) and "default" in lora_A:
                A_weight = lora_A["default"].weight.data.detach()
            elif hasattr(lora_A, "weight"):
                A_weight = lora_A.weight.data.detach()

            if isinstance(lora_B, nn.ModuleDict) and "default" in lora_B:
                B_weight = lora_B["default"].weight.data.detach()
            elif isinstance(lora_B, dict) and "default" in lora_B:
                B_weight = lora_B["default"].weight.data.detach()
            elif hasattr(lora_B, "weight"):
                B_weight = lora_B.weight.data.detach()

            if A_weight is not None and B_weight is not None:
                matrices[name] = (A_weight, B_weight)

    return matrices


def compute_effective_rank(lora_A, lora_B, threshold=0.90):
    """
    Compute effective rank from LoRA matrices.
    delta_W = lora_B @ lora_A; SVD; effective_rank = min k s.t. cumsum(S[:k])/sum(S) >= threshold.

    Returns (effective_rank: int, singular_values: list[float])
    """
    delta_W = lora_B @ lora_A

    U, S, Vh = torch.linalg.svd(delta_W.float(), full_matrices=False)

    S_sum = S.sum()
    if S_sum < 1e-12:
        return 1, S.tolist()

    S_norm = S / S_sum
    cumsum = torch.cumsum(S_norm, dim=0)

    effective_rank = int((cumsum < threshold).sum().item()) + 1

    return effective_rank, S.tolist()


def compute_model_effective_rank(model, threshold=None):
    """
    Aggregate effective rank across all LoRA modules.
    Returns {'effective_rank': int (max), 'per_module': dict, 'singular_values': dict}
    """
    if threshold is None:
        threshold = RANK_CONFIG["default_threshold"]

    matrices = extract_lora_matrices(model)

    if not matrices:
        return {
            "effective_rank": 0,
            "per_module": {},
            "singular_values": {},
        }

    per_module = {}
    singular_values = {}

    for name, (A, B) in matrices.items():
        rank, sv = compute_effective_rank(A, B, threshold)
        per_module[name] = rank
        singular_values[name] = sv

    return {
        "effective_rank": max(per_module.values()) if per_module else 0,
        "mean_effective_rank": sum(per_module.values()) / len(per_module) if per_module else 0,
        "per_module": per_module,
        "singular_values": singular_values,
    }
