"""H-M3 Training Loop - Distillation for 6 conditions (2 objectives x 3 lengths)"""
import torch
from torch import nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from typing import Dict, Optional
import os
from tqdm import tqdm

from config import ExperimentConfig
from model import load_teacher, load_student_base, AttentionBridge, get_student_dim
from losses import compute_loss
from data_train import get_c4_stream

def train_condition(
    config: ExperimentConfig,
    objective: str,
    length: int,
    teacher: nn.Module,
    tokenizer,
) -> nn.Module:
    """Train one condition: fresh student + (bridge if CAB)."""
    print(f"\n{'='*60}")
    print(f"Training: {objective.upper()} @ {length} tokens")
    print(f"{'='*60}")

    student = load_student_base(config)
    student_dim = get_student_dim(student)
    bridge = AttentionBridge(student_dim).cuda() if objective == "cab" else None

    params = list(student.parameters())
    if bridge:
        params += list(bridge.parameters())

    opt = AdamW(params, lr=config.lr, weight_decay=config.weight_decay)
    total_steps = config.tokens_per_condition // (config.batch_size * length)
    sched = CosineAnnealingLR(opt, T_max=max(1, total_steps))

    ckpt_dir = os.path.join(config.checkpoint_dir, f"{objective}_{length}")
    os.makedirs(ckpt_dir, exist_ok=True)

    tokens_seen = load_checkpoint(ckpt_dir, student, bridge, opt)
    next_ckpt_at = ((tokens_seen // config.checkpoint_every_tokens) + 1) * config.checkpoint_every_tokens

    stream = get_c4_stream(config, tokenizer, length)
    pbar = tqdm(total=config.tokens_per_condition, initial=tokens_seen, desc=f"{objective}@{length}")

    for step, batch in enumerate(stream):
        if tokens_seen >= config.tokens_per_condition:
            break

        try:
            with torch.amp.autocast('cuda', dtype=torch.bfloat16):
                with torch.no_grad():
                    teacher_out = teacher(batch["input_ids"], output_attentions=True, output_hidden_states=True)
                student_out = student(batch["input_ids"], output_hidden_states=True)

                hidden = teacher_out.hidden_states[0] if hasattr(teacher_out, 'hidden_states') else batch["input_ids"].float()
                loss = compute_loss(objective, teacher_out, student_out, teacher, student, hidden, bridge) / config.grad_accum
            loss.backward()

        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            opt.zero_grad()
            continue

        if (step + 1) % config.grad_accum == 0:
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step()
            sched.step()
            opt.zero_grad()

        batch_tokens = batch["input_ids"].numel()
        tokens_seen += batch_tokens
        pbar.update(batch_tokens)

        if tokens_seen >= next_ckpt_at:
            save_checkpoint(student, bridge, opt, step, tokens_seen, ckpt_dir)
            next_ckpt_at += config.checkpoint_every_tokens

    pbar.close()
    save_checkpoint(student, bridge, opt, step, tokens_seen, ckpt_dir)
    print(f"Completed: {objective}@{length} - {tokens_seen:,} tokens")

    return student

def train_all_conditions(config: ExperimentConfig) -> Dict[str, nn.Module]:
    """Train all 6 conditions (2 objectives x 3 lengths)."""
    teacher, tokenizer = load_teacher(config)
    models = {}

    for objective in config.objectives:
        for length in config.lengths:
            key = f"{objective}_{length}"
            models[key] = train_condition(config, objective, length, teacher, tokenizer)

    return models, tokenizer

def save_checkpoint(model, bridge, opt, step, tokens_seen, ckpt_dir):
    """Save training checkpoint."""
    state = {
        "model": model.state_dict(),
        "optimizer": opt.state_dict(),
        "step": step,
        "tokens_seen": tokens_seen,
    }
    if bridge:
        state["bridge"] = bridge.state_dict()
    torch.save(state, os.path.join(ckpt_dir, "latest.pt"))

def load_checkpoint(ckpt_dir, model, bridge, opt) -> int:
    """Load checkpoint if exists, return tokens_seen."""
    ckpt_path = os.path.join(ckpt_dir, "latest.pt")
    if os.path.exists(ckpt_path):
        try:
            state = torch.load(ckpt_path)
            model.load_state_dict(state["model"])
            opt.load_state_dict(state["optimizer"])
            if bridge and "bridge" in state:
                bridge.load_state_dict(state["bridge"])
            print(f"Resumed from {state['tokens_seen']:,} tokens")
            return state["tokens_seen"]
        except Exception as e:
            print(f"Checkpoint load failed: {e}")
    return 0
