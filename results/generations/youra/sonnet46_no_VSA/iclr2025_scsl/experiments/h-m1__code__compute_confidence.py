import os
import sys
import json
from typing import Tuple

import torch
import torch.nn.functional as F
from torch import Tensor

import config

# Inject H-E3 code path so we can import from train_erm and data
sys.path.insert(0, config.H_E3_CODE)


def build_model() -> torch.nn.Module:
    """ResNet-50 skeleton with fc replaced by Linear(2048, 2). No weights loaded."""
    from torchvision.models import resnet50, ResNet50_Weights
    import torch.nn as nn
    model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(2048, 2)
    return model


def load_checkpoint(seed: int, epoch: int, device: str) -> torch.nn.Module:
    """Load H-E3 checkpoint; returns model.eval() on device."""
    from train_erm import load_checkpoint as h_e3_load
    return h_e3_load(seed, epoch, device)


def extract_confidence_by_group(
    model: torch.nn.Module,
    loader,
    minority_mask: Tensor,
    device: str,
) -> Tuple[Tensor, float, float]:
    """
    Forward pass on full training set; softmax; index by true class.
    Returns: (p_per_sample [N], p_minority scalar, p_majority scalar)
    """
    model.eval()
    all_conf = []
    with torch.no_grad():
        for x, y, _g in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)                           # [B, 2]
            probs = F.softmax(logits, dim=1)            # [B, 2]
            conf = probs[torch.arange(len(y)), y]       # [B]
            all_conf.append(conf.cpu())
    p_per_sample = torch.cat(all_conf)                  # [N=4795]
    p_min = p_per_sample[minority_mask].mean().item()
    p_maj = p_per_sample[~minority_mask].mean().item()
    return p_per_sample, p_min, p_maj


def compute_trajectory(
    seed: int,
    loader,
    minority_mask: Tensor,
    device: str,
) -> dict:
    """
    Load each checkpoint epoch for one seed; extract confidence.
    Returns: {epoch: {'p_min': float, 'p_maj': float, 'p_per_sample': Tensor[N]}}
    """
    results = {}
    for epoch in config.CHECKPOINT_EPOCHS:
        model = load_checkpoint(seed, epoch, device)
        p_per_sample, p_min, p_maj = extract_confidence_by_group(
            model, loader, minority_mask, device
        )
        results[epoch] = {
            "p_min": p_min,
            "p_maj": p_maj,
            "p_per_sample": p_per_sample,  # [4795] CPU tensor
        }
        del model
        torch.cuda.empty_cache()
    return results


def check_gate(p_min: float, p_maj: float) -> Tuple[bool, bool]:
    """Returns (primary_pass, secondary_pass) per gate thresholds."""
    primary = config.GATE_P_MIN_LOW <= p_min <= config.GATE_P_MIN_HIGH
    secondary = p_maj > config.GATE_P_MAJ
    return primary, secondary


def verify_mechanism_activated(
    results_per_seed: dict,
) -> Tuple[bool, dict]:
    """
    Args: {seed: {epoch: {'p_min', 'p_maj', 'p_per_sample'}, 'tstar': int}}
    Returns: (mechanism_active bool, per-seed indicators dict)
    mechanism_active if >=4 seeds pass primary gate.
    """
    indicators = {}
    for seed, traj in results_per_seed.items():
        tstar = traj["tstar"]
        p_min = traj[tstar]["p_min"]
        p_maj = traj[tstar]["p_maj"]
        primary, secondary = check_gate(p_min, p_maj)
        indicators[seed] = {
            "minority_boundary": primary,
            "majority_saturated": secondary,
            "gap": p_maj - p_min,
            "both_pass": primary and secondary,
        }
    n_pass = sum(v["both_pass"] for v in indicators.values())
    mechanism_active = n_pass >= config.GATE_N_SEEDS
    return mechanism_active, indicators


def save_results(
    results_per_seed: dict,
    mechanism_active: bool,
    gate_pass_count: int,
) -> None:
    """Serialize results to RESULTS_PATH JSON (C-8-2 schema)."""
    seeds_data = {}
    p_min_at_tstar_list = []
    p_maj_at_tstar_list = []

    for seed, traj in results_per_seed.items():
        tstar = traj["tstar"]
        trajectory_serialized = {}
        for epoch, vals in traj.items():
            if not isinstance(epoch, int):
                continue
            trajectory_serialized[str(epoch)] = {
                "p_min": vals["p_min"],
                "p_maj": vals["p_maj"],
            }

        p_min_t = traj[tstar]["p_min"]
        p_maj_t = traj[tstar]["p_maj"]
        primary, secondary = check_gate(p_min_t, p_maj_t)
        p_min_at_tstar_list.append(p_min_t)
        p_maj_at_tstar_list.append(p_maj_t)

        seeds_data[str(seed)] = {
            "tstar": tstar,
            "trajectory": trajectory_serialized,
            "gate": {
                "p_min_at_tstar": p_min_t,
                "p_maj_at_tstar": p_maj_t,
                "minority_boundary": primary,
                "majority_saturated": secondary,
                "gap": p_maj_t - p_min_t,
                "both_pass": primary and secondary,
            },
        }

    output = {
        "metadata": {
            "hypothesis": "H-M1",
            "date": "2026-08-04",
            "checkpoint_epochs": config.CHECKPOINT_EPOCHS,
            "seeds": config.SEEDS,
        },
        "seeds": seeds_data,
        "summary": {
            "n_seeds_pass": gate_pass_count,
            "gate_pass": mechanism_active,
            "mean_p_min_at_tstar": sum(p_min_at_tstar_list) / len(p_min_at_tstar_list),
            "mean_p_maj_at_tstar": sum(p_maj_at_tstar_list) / len(p_maj_at_tstar_list),
        },
    }

    config.ensure_dirs()
    with open(config.RESULTS_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to {config.RESULTS_PATH}")
