from __future__ import annotations
import json
from pathlib import Path

import torch
import torch.nn as nn
from torch.cuda.amp import GradScaler, autocast
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    ViTForImageClassification,
    ViTImageProcessor,
    get_linear_schedule_with_warmup,
)
from torch.optim import AdamW
from peft import LoraConfig, get_peft_model

from config import MODEL_CONFIGS, ExperimentConfig
from oracle import get_checkpoint_path, layer_to_safe, save_result
from data import get_data_loaders


def _get_dtype(model_name: str) -> torch.dtype:
    # DeBERTa: FP32 mandatory (FP16 causes classifier overflow per FIM-LoRA)
    # Use FP32 for all models: PEFT LoRA adds FP32 adapters regardless of base dtype,
    # causing GradScaler unscale errors with FP16 base on H100.
    return torch.float32


def _get_epochs(cfg: ExperimentConfig, model_name: str) -> int:
    return cfg.epochs_vit if "vit" in model_name.lower() else cfg.epochs_nlp


def _get_lr(cfg: ExperimentConfig, model_name: str) -> float:
    return cfg.lr_vit if "vit" in model_name.lower() else cfg.lr_nlp


def _evaluate(model: nn.Module, loader, device: torch.device) -> float:
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for batch in loader:
            if isinstance(batch, (list, tuple)) and len(batch) == 2:
                # torchvision style: (images, labels)
                inputs, labels = batch
                inputs = inputs.to(device)
                labels = labels.to(device)
                outputs = model(pixel_values=inputs)
                preds = outputs.logits.argmax(dim=-1)
            else:
                batch = {k: v.to(device) for k, v in batch.items()}
                labels = batch["labels"]
                outputs = model(**batch)
                preds = outputs.logits.argmax(dim=-1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    model.train()
    return correct / total if total > 0 else 0.0


def build_oracle_model(
    model_name: str,
    target_layer: str,
    target_rank: int,
    baseline_rank: int = 8,
    cfg: ExperimentConfig = None,
):
    """
    Build PEFT model with dual adapters:
      'target': target_layer at target_rank (trainable)
      'baseline': remaining target_modules at baseline_rank (frozen)
    Returns (peft_model, tokenizer_or_processor).
    """
    model_cfg = MODEL_CONFIGS[model_name]
    dtype = _get_dtype(model_name)

    if model_cfg["task"] == "cifar10":
        base = ViTForImageClassification.from_pretrained(
            model_name, num_labels=10, ignore_mismatched_sizes=True, torch_dtype=dtype
        )
        proc = ViTImageProcessor.from_pretrained(model_name)
    else:
        base = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=model_cfg["num_labels"], torch_dtype=dtype
        )
        proc = AutoTokenizer.from_pretrained(model_name)

    base = base.to(dtype)

    task_type = "FEATURE_EXTRACTION" if model_cfg["task"] == "cifar10" else "SEQ_CLS"

    # erank_map keys end with '.weight'; PEFT needs the module path without it
    target_module_path = target_layer.removesuffix(".weight")

    # Adapter 1: target layer at target_rank (trainable)
    lora_target = LoraConfig(
        r=target_rank,
        lora_alpha=2 * target_rank,
        target_modules=[target_module_path],
        lora_dropout=0.0,
        bias="none",
        task_type=task_type,
    )
    model = get_peft_model(base, lora_target, adapter_name="target")

    # Adapter 2: remaining target_module_types at baseline_rank (frozen)
    # Use short module names for baseline (all other module types)
    target_short = target_module_path.split(".")[-1]
    other_modules = [m for m in model_cfg["target_modules"] if m != target_short]
    if other_modules:
        lora_baseline = LoraConfig(
            r=baseline_rank,
            lora_alpha=2 * baseline_rank,
            target_modules=other_modules,
            lora_dropout=0.0,
            bias="none",
            task_type=task_type,
        )
        model.add_adapter("baseline", lora_baseline)
        for name, param in model.named_parameters():
            if "baseline" in name:
                param.requires_grad_(False)

    model.set_adapter("target")
    return model, proc


def train_one_run(
    model_name: str,
    target_layer: str,
    target_rank: int,
    seed: int,
    cfg: ExperimentConfig,
) -> float:
    """Full training run for one (model, layer, rank, seed). Returns val_accuracy."""
    layer_safe = layer_to_safe(target_layer)
    ckpt_path = get_checkpoint_path(cfg, layer_safe, target_rank, seed)
    if ckpt_path.exists():
        try:
            data = json.loads(ckpt_path.read_text())
            if "val_acc" in data:
                return data["val_acc"]
        except Exception:
            pass

    torch.manual_seed(seed)
    model, proc = build_oracle_model(model_name, target_layer, target_rank, cfg.baseline_rank, cfg)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    train_loader, val_loader = get_data_loaders(model_name, proc, cfg)
    epochs = _get_epochs(cfg, model_name)
    total_steps = len(train_loader) * epochs
    warmup_steps = int(total_steps * cfg.warmup_ratio)

    trainable = [p for p in model.parameters() if p.requires_grad]
    optimizer = AdamW(trainable, lr=_get_lr(cfg, model_name), weight_decay=cfg.weight_decay)
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)

    use_amp = (_get_dtype(model_name) == torch.float16)
    scaler = GradScaler(enabled=use_amp)

    model.train()
    for epoch in range(epochs):
        for batch in train_loader:
            if isinstance(batch, (list, tuple)) and len(batch) == 2:
                inputs, labels = batch
                inputs = inputs.to(device)
                labels = labels.to(device)
                with autocast(enabled=use_amp):
                    loss = model(pixel_values=inputs, labels=labels).loss
            else:
                batch = {k: v.to(device) for k, v in batch.items()}
                with autocast(enabled=use_amp):
                    loss = model(**batch).loss

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()
            optimizer.zero_grad()

    val_acc = _evaluate(model, val_loader, device)
    save_result(cfg, target_layer, target_rank, seed, val_acc)
    return val_acc
