"""Uniform LoRA trainer with delta-W extraction and gradient norm capture."""
import os
import gc
import torch
import numpy as np
from typing import Dict, Optional
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup
from peft import LoraConfig, get_peft_model, TaskType
from torch.optim import AdamW


def _resolve_model_path(cfg) -> str:
    """Resolve HF model name to local snapshot path if cached."""
    import glob as _glob
    hf_cache = os.path.expanduser("~/.cache/huggingface/hub")
    pattern = os.path.join(hf_cache, "models--" + cfg.model_name.replace("/", "--"), "snapshots", "*")
    snapshots = _glob.glob(pattern)
    if snapshots:
        return snapshots[0]
    return cfg.model_name


def load_tokenizer(cfg):
    """Load LlamaTokenizer from local cache."""
    local_path = _resolve_model_path(cfg)
    tokenizer = AutoTokenizer.from_pretrained(
        local_path,
        local_files_only=cfg.local_files_only,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def load_base_model(cfg, num_labels: int):
    """Load LLaMA-3.1-8B from local cache with bfloat16."""
    dtype_map = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}
    dtype = dtype_map.get(cfg.torch_dtype, torch.bfloat16)

    local_path = _resolve_model_path(cfg)
    model = AutoModelForSequenceClassification.from_pretrained(
        local_path,
        num_labels=num_labels,
        local_files_only=cfg.local_files_only,
        torch_dtype=dtype,
        device_map=cfg.device_map,
    )
    if model.config.pad_token_id is None:
        model.config.pad_token_id = model.config.eos_token_id
    return model


def compute_delta_w(model) -> Dict[str, torch.Tensor]:
    """Extract ΔW = B @ A for each LoRA adapter layer post-training."""
    delta_w = {}
    for name, module in model.named_modules():
        if hasattr(module, "lora_A") and hasattr(module, "lora_B"):
            try:
                A = module.lora_A["default"].weight   # (r, d_in)
                B = module.lora_B["default"].weight   # (d_out, r)
                dw = (B @ A).detach().cpu()
                clean_key = name.replace("base_model.model.", "")
                delta_w[clean_key] = dw
            except (KeyError, AttributeError):
                pass
    return delta_w


def compute_grad_norms(stored_grads: Dict[str, torch.Tensor]) -> Dict[str, float]:
    """Compute Frobenius norm of gradients per layer."""
    grad_norms = {}
    for name, grad in stored_grads.items():
        if grad is not None:
            grad_norms[name] = torch.norm(grad.float(), "fro").item()
    return grad_norms


def evaluate_model(model, dataloader, task: str, cfg) -> float:
    """Evaluate on validation set; return accuracy."""
    model.eval()
    correct = 0
    total = 0
    device = "cpu"
    for p in model.parameters():
        if p.device.type != "meta":
            device = p.device
            break
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = outputs.logits.argmax(dim=-1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    return correct / total if total > 0 else 0.0


def train_uniform_lora(
    task: str,
    seed: int,
    cfg,
    return_delta_w: bool = True,
    return_grad_norms: bool = True,
    rank_pattern: Optional[Dict[str, int]] = None,
    train_dataloader=None,
    val_dataloader=None,
    tokenizer=None,
) -> Dict:
    """Fine-tune uniform r=16 LoRA on task with seed.

    Returns: {
        "accuracy": float,
        "delta_w": Dict[str, torch.Tensor],
        "grad_norms": Dict[str, float],
    }
    """
    torch.manual_seed(seed)
    np.random.seed(seed)

    from data_utils import load_glue_dataloader, get_num_labels, load_tokenizer as _load_tokenizer

    num_labels = get_num_labels(task)

    if tokenizer is None:
        tokenizer = _load_tokenizer(cfg)

    model = load_base_model(cfg, num_labels)

    lora_kwargs = dict(
        r=cfg.lora_r,
        lora_alpha=cfg.lora_alpha,
        target_modules=cfg.target_modules,
        lora_dropout=cfg.lora_dropout,
        bias="none",
        task_type=TaskType.SEQ_CLS,
    )
    if rank_pattern is not None:
        lora_kwargs["rank_pattern"] = rank_pattern
    lora_config = LoraConfig(**lora_kwargs)
    model = get_peft_model(model, lora_config)
    if cfg.gradient_checkpointing:
        model.enable_input_require_grads()
        model.gradient_checkpointing_enable()

    stored_grads: Dict[str, torch.Tensor] = {}
    if return_grad_norms:
        for name, param in model.named_parameters():
            if "lora_A" in name and param.requires_grad:
                def make_hook(n):
                    def hook_fn(grad):
                        stored_grads[n] = grad.detach().cpu()
                    return hook_fn
                param.register_hook(make_hook(name))

    if train_dataloader is None:
        train_dataloader = load_glue_dataloader(task, "train", tokenizer, cfg)
    if val_dataloader is None:
        val_dataloader = load_glue_dataloader(task, "validation", tokenizer, cfg)

    optimizer = AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=cfg.lr,
        weight_decay=cfg.weight_decay,
        betas=(cfg.adam_beta1, cfg.adam_beta2),
    )

    num_training_steps = len(train_dataloader) * cfg.num_epochs
    num_warmup_steps = int(num_training_steps * cfg.warmup_ratio)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=num_warmup_steps, num_training_steps=num_training_steps
    )

    # With device_map="auto", find the device of the first non-meta, non-cpu parameter
    device = "cpu"
    for p in model.parameters():
        if p.device.type != "meta":
            device = p.device
            break
    model.train()

    for epoch in range(cfg.num_epochs):
        for batch in train_dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            if torch.isnan(loss) or torch.isinf(loss):
                print(f"[WARN] NaN/Inf loss detected, skipping batch")
                optimizer.zero_grad()
                continue
            loss.backward()

            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

    accuracy = evaluate_model(model, val_dataloader, task, cfg)

    result = {"accuracy": accuracy}

    if return_delta_w:
        result["delta_w"] = compute_delta_w(model)
    else:
        result["delta_w"] = {}

    if return_grad_norms:
        result["grad_norms"] = compute_grad_norms(stored_grads)
    else:
        result["grad_norms"] = {}

    del model
    torch.cuda.empty_cache()
    gc.collect()

    return result
