"""Stream 1: Joint rank sensitivity sweep — 320-run budget-neutral perturbation engine."""
import re
import numpy as np
from typing import Dict, List
import torch
import gc


def build_joint_rank_pattern(
    perturbed_layer_idx: int,
    delta_r: int,
    r_base: int,
    n_layers: int,
    target_modules: List[str],
) -> Dict[str, int]:
    """Build budget-neutral rank_pattern: reduce target layer by delta_r,
    redistribute freed budget proportionally to remaining layers.

    Budget-neutral: sum of all ranks unchanged.
    """
    n_modules = len(target_modules)
    n_other = n_layers - 1

    # Freed budget from perturbed layer: delta_r per module
    freed_total = n_modules * delta_r

    extra_per_pair = freed_total // (n_other * n_modules)
    remainder = freed_total % (n_other * n_modules)

    rank_pattern = {}
    bonus_assigned = 0

    for layer_idx in range(n_layers):
        for mod in target_modules:
            key = f"model.layers.{layer_idx}.mlp.{mod}"
            if "proj" not in mod:
                key = f"model.layers.{layer_idx}.self_attn.{mod}"
            # Use generic key format for PEFT rank_pattern
            peft_key = f"base_model.model.model.layers.{layer_idx}.{_module_to_peft_key(mod)}"

            if layer_idx == perturbed_layer_idx:
                rank_pattern[peft_key] = max(1, r_base - delta_r)
            else:
                bonus = 1 if bonus_assigned < remainder else 0
                rank_pattern[peft_key] = r_base + extra_per_pair + bonus
                bonus_assigned += bonus

    return rank_pattern


def _module_to_peft_key(mod: str) -> str:
    """Map module name to PEFT internal key."""
    attn_mods = {"q_proj", "k_proj", "v_proj", "o_proj"}
    if mod in attn_mods:
        return f"self_attn.{mod}"
    else:
        return f"mlp.{mod}"


def run_sensitivity_sweep(
    task: str,
    cfg,
    baseline_accs: Dict[int, float],
) -> np.ndarray:
    """Run 32 × 5 = 160 perturbed fine-tuning runs for one task.
    Returns: accuracy_drop[32] averaged over 5 seeds.
    """
    from lora_trainer import train_uniform_lora
    from data_utils import load_glue_dataloader, load_tokenizer

    tokenizer = load_tokenizer(cfg)
    drops = np.zeros((cfg.n_layers, len(cfg.seeds)))

    for l in range(cfg.n_layers):
        rank_pattern = build_joint_rank_pattern(
            perturbed_layer_idx=l,
            delta_r=cfg.delta_r,
            r_base=cfg.lora_r,
            n_layers=cfg.n_layers,
            target_modules=cfg.target_modules,
        )
        for s_idx, seed in enumerate(cfg.seeds):
            baseline_acc = baseline_accs.get(seed, 0.0)
            result = train_uniform_lora(
                task=task,
                seed=seed,
                cfg=cfg,
                return_delta_w=False,
                return_grad_norms=False,
                rank_pattern=rank_pattern,
                tokenizer=tokenizer,
            )
            drop = baseline_acc - result["accuracy"]
            drops[l, s_idx] = drop
            print(f"[SWEEP] Layer {l}, Seed {seed}: drop={drop:.4f}")

    return drops.mean(axis=1)


def run_all_sensitivity_sweeps(
    cfg,
    baseline_accs: Dict[str, Dict[int, float]],
) -> Dict[str, np.ndarray]:
    """Run sweeps for both sst2 and mnli.
    Returns: {"sst2": np.ndarray(32,), "mnli": np.ndarray(32,)}
    """
    results = {}
    for task in cfg.tasks:
        print(f"\n[SWEEP] Starting sensitivity sweep for task={task}")
        results[task] = run_sensitivity_sweep(task, cfg, baseline_accs.get(task, {}))
    return results


def identify_sensitive_layers(
    accuracy_drops: np.ndarray,
    threshold: float,
) -> np.ndarray:
    """Returns boolean mask of sensitive layers (drop >= threshold)."""
    sensitive_mask = accuracy_drops >= threshold
    for l, (drop, sens) in enumerate(zip(accuracy_drops, sensitive_mask)):
        print(f"[SENSITIVITY] Layer {l}: accuracy_drop={drop:.4f}, sensitive={sens}")
    n_sensitive = sensitive_mask.sum()
    print(f"[SENSITIVITY] Total sensitive layers: {n_sensitive}/{len(accuracy_drops)}")
    return sensitive_mask


def check_delta_r_fallback(
    accuracy_drops: np.ndarray,
    threshold: float,
    cfg,
) -> int:
    """Return delta_r=4 if no sensitive layers found, else delta_r from config."""
    sensitive_mask = accuracy_drops >= threshold
    if sensitive_mask.sum() == 0:
        print("[FALLBACK] No sensitive layers found, increasing delta_r to 4")
        return 4
    return cfg.delta_r
