"""Training loop with checkpoint/resume."""
import os
import math
import torch
from torch.nn.utils import clip_grad_norm_
from typing import Dict, List, Tuple, Optional
from model import build_gpt2_model
from config import ScaledExperimentConfig

def build_optimizer(model, cfg) -> torch.optim.AdamW:
    """Build AdamW optimizer."""
    return torch.optim.AdamW(
        model.parameters(),
        lr=cfg.lr,
        betas=(cfg.beta1, cfg.beta2),
        weight_decay=cfg.weight_decay
    )

def build_scheduler(optimizer, cfg, total_steps: int):
    """Linear warmup + cosine decay scheduler."""
    def lr_lambda(step):
        if step < cfg.warmup_steps:
            return step / max(1, cfg.warmup_steps)
        progress = (step - cfg.warmup_steps) / max(1, total_steps - cfg.warmup_steps)
        return 0.5 * (1.0 + math.cos(math.pi * progress))
    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

def save_checkpoint(model, optimizer, scheduler, step: int, loss_history: List[float], ckpt_dir: str) -> str:
    """Save training checkpoint."""
    os.makedirs(ckpt_dir, exist_ok=True)
    path = os.path.join(ckpt_dir, f"step_{step}.pt")
    torch.save({
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "scheduler": scheduler.state_dict(),
        "step": step,
        "loss_history": loss_history
    }, path)
    return path

def find_latest_checkpoint(ckpt_dir: str) -> Optional[str]:
    """Find latest checkpoint in directory."""
    if not os.path.exists(ckpt_dir):
        return None
    checkpoints = [f for f in os.listdir(ckpt_dir) if f.startswith("step_") and f.endswith(".pt")]
    if not checkpoints:
        return None
    latest = max(checkpoints, key=lambda x: int(x.split("_")[1].split(".")[0]))
    return os.path.join(ckpt_dir, latest)

def resume_from_checkpoint(ckpt_dir: str, model, optimizer, scheduler) -> Tuple[int, List[float]]:
    """Resume from latest checkpoint."""
    ckpt_path = find_latest_checkpoint(ckpt_dir)
    if ckpt_path is None:
        return 0, []
    state = torch.load(ckpt_path, map_location="cpu")
    model.load_state_dict(state["model"])
    optimizer.load_state_dict(state["optimizer"])
    scheduler.load_state_dict(state["scheduler"])
    print(f"Resumed from {ckpt_path} at step {state['step']}")
    return state["step"], state.get("loss_history", [])

def train_one_config(
    level: str,
    seed: int,
    tokens: torch.Tensor,
    cfg: ScaledExperimentConfig,
    ckpt_dir: str
) -> Tuple[str, List[float]]:
    """Train GPT-2 from scratch on packed tokens."""
    torch.manual_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = build_gpt2_model(cfg).to(device)
    optimizer = build_optimizer(model, cfg)

    total_steps = cfg.total_tokens // (cfg.batch_size * cfg.seq_len)
    ckpt_interval = max(1, cfg.checkpoint_every_tokens // (cfg.batch_size * cfg.seq_len))

    scheduler = build_scheduler(optimizer, cfg, total_steps)

    start_step, loss_history = resume_from_checkpoint(ckpt_dir, model, optimizer, scheduler)

    if start_step >= total_steps:
        print(f"Training already complete for {level}/seed{seed}")
        return find_latest_checkpoint(ckpt_dir), loss_history

    print(f"Training {level}/seed{seed}: {total_steps} steps on {device}")
    num_seqs = tokens.shape[0]

    for step in range(start_step, total_steps):
        # Sample batch
        indices = torch.randint(0, num_seqs, (cfg.batch_size,))
        batch = tokens[indices].to(device)

        # Forward + backward
        outputs = model(input_ids=batch, labels=batch)
        loss = outputs.loss

        loss.backward()
        clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()

        loss_history.append(loss.item())

        if step % 100 == 0:
            print(f"  step {step}/{total_steps}, loss={loss.item():.4f}, lr={scheduler.get_last_lr()[0]:.6f}")

        if (step + 1) % ckpt_interval == 0:
            save_checkpoint(model, optimizer, scheduler, step + 1, loss_history, ckpt_dir)

    final_path = save_checkpoint(model, optimizer, scheduler, total_steps, loss_history, ckpt_dir)
    print(f"Training complete: {level}/seed{seed}, final loss={loss_history[-1]:.4f}")
    return final_path, loss_history
