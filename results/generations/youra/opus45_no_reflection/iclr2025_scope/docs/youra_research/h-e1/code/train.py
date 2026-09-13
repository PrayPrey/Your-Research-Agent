"""H-E1 Training Loop with MOHAWK and CAB objectives"""
import os
import sys
import json
import math
import random
import torch
import numpy as np
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
import torch.amp
from tqdm import tqdm

from config import ExperimentConfig
from data import get_dataloader, get_tokenizer
from model import Teacher, PhiMambaStudent, init_student_from_teacher
from objectives import UnifiedDistillationFramework


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def check_nan_inf(loss: torch.Tensor, grad_norm: float, metrics: dict) -> bool:
    """Check for NaN/Inf values. Returns True if values are valid."""
    if torch.isnan(loss) or torch.isinf(loss):
        metrics["nan_count"] += 1
        return False
    if math.isnan(grad_norm) or math.isinf(grad_norm):
        metrics["inf_count"] += 1
        return False
    return True


def run_stage(framework: UnifiedDistillationFramework, dataloader, config: ExperimentConfig,
              stage: int, token_budget: int, lr: float, metrics: dict) -> dict:
    """Run a single training stage."""
    device = next(framework.student.parameters()).device
    framework.freeze_for_stage(stage)
    trainable_params = framework.get_trainable_params(stage)

    if not trainable_params:
        print(f"  No trainable params for stage {stage}, skipping")
        return metrics

    optimizer = AdamW(trainable_params, lr=lr, weight_decay=config.weight_decay)
    total_steps = token_budget // (config.batch_size * config.seq_len * config.grad_accum)
    scheduler = CosineAnnealingLR(optimizer, T_max=max(1, total_steps))

    tokens_seen = 0
    step = 0
    accum_loss = 0.0
    layer_idx = 0

    pbar = tqdm(total=token_budget, desc=f"Stage {stage}", unit="tok")

    for batch in dataloader:
        if tokens_seen >= token_budget:
            break

        input_ids = batch["input_ids"].to(device)
        batch_tokens = input_ids.numel()

        with torch.amp.autocast('cuda', dtype=torch.bfloat16):
            loss = framework.compute_loss(input_ids, layer_idx, stage)
            loss = loss / config.grad_accum

        loss.backward()
        accum_loss += loss.item()

        if (step + 1) % config.grad_accum == 0:
            grad_norm = torch.nn.utils.clip_grad_norm_(trainable_params, config.grad_clip).item()

            if check_nan_inf(loss * config.grad_accum, grad_norm, metrics):
                optimizer.step()
            optimizer.zero_grad()
            scheduler.step()

            if step % (config.log_every_steps * config.grad_accum) == 0:
                metrics["loss_history"].append(accum_loss * config.grad_accum)
                metrics["grad_norm_history"].append(grad_norm)
                metrics["token_history"].append(tokens_seen)
                print(f"  Step {step//config.grad_accum}: loss={accum_loss * config.grad_accum:.4f}, grad_norm={grad_norm:.4f}")
                accum_loss = 0.0

        tokens_seen += batch_tokens
        step += 1
        layer_idx = (layer_idx + 1) % config.num_layers
        pbar.update(batch_tokens)

    pbar.close()
    return metrics


def train_mohawk(framework: UnifiedDistillationFramework, dataloader, config: ExperimentConfig) -> dict:
    """Run MOHAWK 3-stage training."""
    metrics = {
        "loss_history": [],
        "grad_norm_history": [],
        "token_history": [],
        "nan_count": 0,
        "inf_count": 0,
        "objective": "matrix"
    }

    print("MOHAWK Stage 1: Matrix alignment (mixer only)")
    metrics = run_stage(framework, dataloader, config, stage=1,
                        token_budget=config.mohawk_stage1_tokens, lr=config.lr_stage12, metrics=metrics)

    print("MOHAWK Stage 2: Hidden state alignment (full block)")
    metrics = run_stage(framework, dataloader, config, stage=2,
                        token_budget=config.mohawk_stage2_tokens, lr=config.lr_stage12, metrics=metrics)

    print("MOHAWK Stage 3: KL distillation (full model)")
    metrics = run_stage(framework, dataloader, config, stage=3,
                        token_budget=config.mohawk_stage3_tokens, lr=config.lr_stage3, metrics=metrics)

    metrics["final_loss"] = metrics["loss_history"][-1] if metrics["loss_history"] else float("inf")
    metrics["initial_loss"] = metrics["loss_history"][0] if metrics["loss_history"] else float("inf")
    metrics["converged"] = metrics["final_loss"] < metrics["initial_loss"] * 0.5

    return metrics


def train_cab(framework: UnifiedDistillationFramework, dataloader, config: ExperimentConfig) -> dict:
    """Run CAB 2-stage training."""
    metrics = {
        "loss_history": [],
        "grad_norm_history": [],
        "token_history": [],
        "nan_count": 0,
        "inf_count": 0,
        "objective": "token"
    }

    print("CAB Stage 1: Bridge alignment (phi_B, phi_C only)")
    metrics = run_stage(framework, dataloader, config, stage=1,
                        token_budget=config.cab_stage1_tokens, lr=config.lr_stage12, metrics=metrics)

    print("CAB Stage 2: KL distillation (full model)")
    metrics = run_stage(framework, dataloader, config, stage=2,
                        token_budget=config.cab_stage2_tokens, lr=config.lr_stage12, metrics=metrics)

    metrics["final_loss"] = metrics["loss_history"][-1] if metrics["loss_history"] else float("inf")
    metrics["initial_loss"] = metrics["loss_history"][0] if metrics["loss_history"] else float("inf")
    metrics["converged"] = metrics["final_loss"] < metrics["initial_loss"] * 0.5

    return metrics


def main():
    config = ExperimentConfig()
    set_seed(config.seed)

    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    print("Loading tokenizer...")
    tokenizer = get_tokenizer(config)

    print("Loading teacher model (Phi-1.5)...")
    teacher = Teacher(config).to(device)

    print("Initializing student model (Phi-Mamba)...")
    student_mohawk = PhiMambaStudent(config).to(device).to(torch.bfloat16)
    init_student_from_teacher(student_mohawk, teacher)

    student_cab = PhiMambaStudent(config).to(device).to(torch.bfloat16)
    init_student_from_teacher(student_cab, teacher)

    print("Creating data loader...")
    dataloader = get_dataloader(config, tokenizer)

    print("\n" + "="*60)
    print("Training MOHAWK (matrix-level) objective")
    print("="*60)
    framework_mohawk = UnifiedDistillationFramework(teacher, student_mohawk, "matrix", config)
    mohawk_metrics = train_mohawk(framework_mohawk, dataloader, config)

    dataloader = get_dataloader(config, tokenizer)

    print("\n" + "="*60)
    print("Training CAB (token-level) objective")
    print("="*60)
    framework_cab = UnifiedDistillationFramework(teacher, student_cab, "token", config)
    cab_metrics = train_cab(framework_cab, dataloader, config)

    results = {
        "mohawk": mohawk_metrics,
        "cab": cab_metrics,
        "config": {
            "total_tokens": config.total_tokens,
            "batch_size": config.batch_size,
            "seq_len": config.seq_len,
            "seed": config.seed
        }
    }

    with open(os.path.join(config.output_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2, default=lambda x: str(x) if isinstance(x, (torch.Tensor, np.ndarray)) else x)

    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"MOHAWK: initial_loss={mohawk_metrics['initial_loss']:.4f}, final_loss={mohawk_metrics['final_loss']:.4f}, converged={mohawk_metrics['converged']}")
    print(f"CAB:    initial_loss={cab_metrics['initial_loss']:.4f}, final_loss={cab_metrics['final_loss']:.4f}, converged={cab_metrics['converged']}")
    print(f"NaN counts - MOHAWK: {mohawk_metrics['nan_count']}, CAB: {cab_metrics['nan_count']}")
    print(f"Inf counts - MOHAWK: {mohawk_metrics['inf_count']}, CAB: {cab_metrics['inf_count']}")

    gate_pass = (
        mohawk_metrics["converged"] and
        cab_metrics["converged"] and
        mohawk_metrics["nan_count"] == 0 and
        cab_metrics["nan_count"] == 0
    )
    print(f"\nGATE VERDICT: {'PASS' if gate_pass else 'FAIL'}")

    return results


if __name__ == "__main__":
    main()
