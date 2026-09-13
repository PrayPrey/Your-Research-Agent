"""Stream 2: AdaLoRA reference runner with rank_pattern extraction."""
import re
import gc
import torch
import numpy as np
from typing import Dict
from transformers import get_linear_schedule_with_warmup
from torch.optim import AdamW
from peft import AdaLoraConfig, get_peft_model, TaskType


def extract_rank_pattern(model) -> Dict[str, int]:
    """Extract per-layer effective rank from AdaLoRA model."""
    rank_pattern = {}
    # Try model.base_model.rank_pattern first
    if hasattr(model, "base_model") and hasattr(model.base_model, "rank_pattern"):
        rank_pattern = dict(model.base_model.rank_pattern)
    elif hasattr(model, "rank_pattern"):
        rank_pattern = dict(model.rank_pattern)
    else:
        # Fallback: compute from singular values stored in lora_E
        for name, module in model.named_modules():
            if hasattr(module, "lora_E"):
                try:
                    e = module.lora_E["default"]
                    effective_rank = (e.abs() > 1e-6).sum().item()
                    rank_pattern[name] = int(effective_rank)
                except (KeyError, AttributeError):
                    pass
    return rank_pattern


def rank_pattern_to_array(
    rank_pattern: Dict[str, int],
    n_layers: int = 32,
) -> np.ndarray:
    """Convert rank_pattern dict to ordered (32,) array by layer index."""
    layer_ranks: Dict[int, list] = {}
    for key, val in rank_pattern.items():
        m = re.search(r"layers\.(\d+)\.", key)
        if m:
            layer_idx = int(m.group(1))
            if layer_idx not in layer_ranks:
                layer_ranks[layer_idx] = []
            layer_ranks[layer_idx].append(val)

    result = np.zeros(n_layers)
    for idx in range(n_layers):
        if idx in layer_ranks:
            result[idx] = np.mean(layer_ranks[idx])
    return result


def check_uniform_allocation(rank_pattern_array: np.ndarray) -> bool:
    """Returns True if all allocations equal — AdaLoRA failed to learn heterogeneous."""
    return float(np.std(rank_pattern_array)) < 0.1


def run_adalora(
    task: str,
    seed: int,
    cfg,
    tokenizer=None,
) -> Dict[str, int]:
    """Train AdaLoRA at 60% budget; return model.base_model.rank_pattern."""
    torch.manual_seed(seed)
    np.random.seed(seed)

    from data_utils import load_glue_dataloader, get_num_labels, load_tokenizer as _load_tokenizer
    from lora_trainer import load_base_model, evaluate_model

    num_labels = get_num_labels(task)
    if tokenizer is None:
        tokenizer = _load_tokenizer(cfg)

    model = load_base_model(cfg, num_labels)

    adalora_config = AdaLoraConfig(
        target_r=cfg.adalora_target_r,
        init_r=cfg.adalora_init_r,
        tinit=cfg.adalora_tinit,
        tfinal=cfg.adalora_tfinal,
        deltaT=cfg.adalora_deltaT,
        beta1=cfg.adalora_beta1,
        beta2=cfg.adalora_beta2,
        orth_reg_weight=cfg.adalora_orth_reg_weight,
        target_modules=cfg.target_modules,
        task_type=TaskType.SEQ_CLS,
    )
    model = get_peft_model(model, adalora_config)

    train_loader = load_glue_dataloader(task, "train", tokenizer, cfg)

    optimizer = AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=cfg.lr,
        weight_decay=cfg.weight_decay,
        betas=(cfg.adam_beta1, cfg.adam_beta2),
    )

    num_training_steps = len(train_loader) * cfg.num_epochs
    num_warmup_steps = int(num_training_steps * cfg.warmup_ratio)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=num_warmup_steps, num_training_steps=num_training_steps
    )

    device = next(model.parameters()).device
    model.train()
    global_step = 0

    for epoch in range(cfg.num_epochs):
        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()

            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

            # AdaLoRA rank update
            if hasattr(model, "base_model") and hasattr(model.base_model, "update_and_mask"):
                model.base_model.update_and_mask(global_step)

            global_step += 1

    rank_pattern = extract_rank_pattern(model)
    rank_array = rank_pattern_to_array(rank_pattern, n_layers=cfg.n_layers)
    if check_uniform_allocation(rank_array):
        print(f"[WARNING] AdaLoRA task={task} seed={seed}: uniform allocation detected (std<0.1)")

    del model
    torch.cuda.empty_cache()
    gc.collect()

    return rank_pattern


def run_all_adalora(cfg) -> Dict[str, np.ndarray]:
    """Run AdaLoRA for sst2 + mnli, 5 seeds each.
    Returns: {"sst2": ndarray(32,), "mnli": ndarray(32,)}
    """
    from data_utils import load_tokenizer
    results = {}
    for task in cfg.tasks:
        print(f"\n[ADALORA] Starting AdaLoRA for task={task}")
        tokenizer = load_tokenizer(cfg)
        all_arrays = []
        for seed in cfg.seeds:
            rank_pattern = run_adalora(task, seed, cfg, tokenizer=tokenizer)
            arr = rank_pattern_to_array(rank_pattern, n_layers=cfg.n_layers)
            all_arrays.append(arr)
            print(f"[ADALORA] task={task}, seed={seed}: mean_rank={arr.mean():.2f}")
        results[task] = np.mean(all_arrays, axis=0)
    return results
