import os
import json
from typing import Dict

import torch
import torch.nn.functional as F
from safetensors.torch import load_file as load_safetensors


def load_adapter_state_dict(adapter_dir: str) -> Dict[str, torch.Tensor]:
    """Load LoRA adapter weights from safetensors or pytorch_model.bin."""
    safetensors_path = os.path.join(adapter_dir, "adapter_model.safetensors")
    bin_path = os.path.join(adapter_dir, "adapter_model.bin")

    if os.path.exists(safetensors_path):
        return load_safetensors(safetensors_path, device="cpu")
    elif os.path.exists(bin_path):
        return torch.load(bin_path, map_location="cpu")
    else:
        raise FileNotFoundError(
            f"No adapter weights found in {adapter_dir}. "
            f"Expected adapter_model.safetensors or adapter_model.bin"
        )


def compute_layer_cosine_similarity(
    baseline_sd: Dict[str, torch.Tensor],
    proposed_sd: Dict[str, torch.Tensor],
) -> Dict[str, float]:
    """Compute per-layer cosine similarity between baseline and proposed LoRA weights."""
    results = {}
    for key in baseline_sd:
        if "lora_A" in key or "lora_B" in key:
            if key not in proposed_sd:
                continue
            b = baseline_sd[key].float().flatten()
            p = proposed_sd[key].float().flatten()
            sim = F.cosine_similarity(b.unsqueeze(0), p.unsqueeze(0)).item()
            results[key] = sim
    return results


def evaluate_gate(results: Dict[str, float], threshold: float = 0.95) -> dict:
    """Evaluate MUST_WORK gate: pass if any layer cosine similarity < threshold."""
    if not results:
        return {
            "gate_pass": False,
            "min_sim": None,
            "mean_sim": None,
            "layers_below_threshold": [],
            "total_layers": 0,
            "threshold": threshold,
            "error": "No LoRA layers found in state dict",
        }

    values = list(results.values())
    min_sim = min(values)
    mean_sim = sum(values) / len(values)
    layers_below = [k for k, v in results.items() if v < threshold]

    return {
        "gate_pass": min_sim < threshold,
        "min_sim": min_sim,
        "mean_sim": mean_sim,
        "layers_below_threshold": layers_below,
        "total_layers": len(values),
        "threshold": threshold,
    }


def save_results(results: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
