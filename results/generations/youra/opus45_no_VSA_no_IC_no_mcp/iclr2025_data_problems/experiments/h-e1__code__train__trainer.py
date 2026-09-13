"""GPT-2 training loop with checkpointing."""

import os
import math
from typing import Iterator
import torch
from torch.optim import AdamW
from torch.optim.lr_scheduler import LambdaLR
from transformers import GPT2Config, GPT2LMHeadModel

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODEL_CONFIG, TRAIN_CONFIG


def build_model(seed: int = None) -> GPT2LMHeadModel:
    """Build fresh GPT-2 125M model."""
    if seed is None:
        seed = TRAIN_CONFIG["seed"]
    torch.manual_seed(seed)

    config = GPT2Config(
        vocab_size=MODEL_CONFIG["vocab_size"],
        n_positions=MODEL_CONFIG["n_positions"],
        n_embd=MODEL_CONFIG["n_embd"],
        n_layer=MODEL_CONFIG["n_layer"],
        n_head=MODEL_CONFIG["n_head"],
    )
    model = GPT2LMHeadModel(config)
    return model


def get_cosine_schedule(
    optimizer,
    warmup_steps: int = None,
    total_steps: int = None,
    min_lr_ratio: float = None,
) -> LambdaLR:
    """Cosine learning rate schedule with warmup."""
    if warmup_steps is None:
        warmup_steps = TRAIN_CONFIG["warmup_steps"]
    if total_steps is None:
        total_steps = TRAIN_CONFIG["max_steps"]
    if min_lr_ratio is None:
        min_lr_ratio = TRAIN_CONFIG["lr_min"] / TRAIN_CONFIG["lr_peak"]

    def lr_lambda(step):
        if step < warmup_steps:
            return step / warmup_steps
        progress = (step - warmup_steps) / (total_steps - warmup_steps)
        return min_lr_ratio + (1 - min_lr_ratio) * 0.5 * (1 + math.cos(math.pi * progress))

    return LambdaLR(optimizer, lr_lambda)


def save_checkpoint(ckpt_dir: str, model, optimizer, scheduler, step: int, config_id: str):
    """Save training checkpoint."""
    os.makedirs(ckpt_dir, exist_ok=True)
    torch.save({
        "step": step,
        "config_id": config_id,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "scheduler_state_dict": scheduler.state_dict(),
    }, os.path.join(ckpt_dir, f"checkpoint_{step}.pt"))
    model.save_pretrained(os.path.join(ckpt_dir, "model"))


def load_checkpoint(ckpt_dir: str, model, optimizer, scheduler) -> int:
    """Load latest checkpoint if exists. Returns resume step."""
    if not os.path.exists(ckpt_dir):
        return 0

    checkpoints = [f for f in os.listdir(ckpt_dir) if f.startswith("checkpoint_") and f.endswith(".pt")]
    if not checkpoints:
        return 0

    latest = max(checkpoints, key=lambda x: int(x.split("_")[1].split(".")[0]))
    ckpt = torch.load(os.path.join(ckpt_dir, latest))
    model.load_state_dict(ckpt["model_state_dict"])
    optimizer.load_state_dict(ckpt["optimizer_state_dict"])
    scheduler.load_state_dict(ckpt["scheduler_state_dict"])
    return ckpt["step"] + 1


def train(
    model: GPT2LMHeadModel,
    data: Iterator[torch.Tensor],
    ckpt_dir: str,
    config_id: str,
    batch_size: int = None,
    total_steps: int = None,
    ckpt_every: int = 2000,
    device: str = "cuda",
) -> str:
    """Train model and save checkpoint."""
    if batch_size is None:
        batch_size = TRAIN_CONFIG["batch_size"]
    if total_steps is None:
        total_steps = TRAIN_CONFIG["max_steps"]

    model = model.to(device)
    if TRAIN_CONFIG["precision"] == "bf16":
        model = model.bfloat16()

    optimizer = AdamW(
        model.parameters(),
        lr=TRAIN_CONFIG["lr_peak"],
        betas=(TRAIN_CONFIG["adam_beta1"], TRAIN_CONFIG["adam_beta2"]),
        weight_decay=TRAIN_CONFIG["weight_decay"],
    )
    scheduler = get_cosine_schedule(optimizer)

    resume_step = load_checkpoint(ckpt_dir, model, optimizer, scheduler)
    if resume_step > 0:
        print(f"Resuming from step {resume_step}")

    model.train()
    batch = []
    step = resume_step

    for chunk in data:
        if step >= total_steps:
            break

        batch.append(chunk)
        if len(batch) < batch_size:
            continue

        input_ids = torch.stack(batch).to(device)
        batch = []

        with torch.cuda.amp.autocast(dtype=torch.bfloat16):
            outputs = model(input_ids, labels=input_ids)
            loss = outputs.loss

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), TRAIN_CONFIG["grad_clip"])
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()

        if step % 100 == 0:
            print(f"[{config_id}] Step {step}/{total_steps} Loss: {loss.item():.4f}")

        if step % ckpt_every == 0 or step == total_steps - 1:
            save_checkpoint(ckpt_dir, model, optimizer, scheduler, step, config_id)

        step += 1

    save_checkpoint(ckpt_dir, model, optimizer, scheduler, step, config_id)
    return os.path.join(ckpt_dir, "model")
