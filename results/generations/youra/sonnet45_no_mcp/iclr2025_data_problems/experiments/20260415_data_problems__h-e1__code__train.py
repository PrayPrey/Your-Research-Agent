"""
Training Loop with Curriculum Scheduling
Supports all 4 experimental conditions with gradient accumulation and mixed precision.
"""

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from pathlib import Path
import json
import time
import numpy as np
from typing import Optional

from config import TRAINING_CONFIG, DIVERSITY_SCORES, CURRICULUM_CONFIG, CHECKPOINT_PERCENTAGES
from data.curriculum_loader import CurriculumDataLoader
from data.pile_loader import load_pile_domains
from transformers import GPT2Tokenizer


def train_model(
    model: nn.Module,
    condition: str,
    scale: str,
    seed: int,
    output_dir: Path,
    smoke_test: bool = False
):
    """
    Train model with specified curriculum condition.

    Args:
        model: GPT2Model instance
        condition: One of ["static", "diversity_ranked", "reversed", "shuffled"]
        scale: "1B" or "7B"
        seed: Random seed
        output_dir: Directory to save checkpoints and logs
        smoke_test: If True, run quick smoke test instead of full training

    Returns:
        Dict with training metrics
    """
    device = next(model.parameters()).device
    config = TRAINING_CONFIG[scale]

    # Adjust for smoke test
    if smoke_test:
        total_steps = 10  # Just 10 steps for smoke test (very quick)
        max_samples_per_domain = 1000  # Limit samples for smoke test
        print(f"🔥 SMOKE TEST MODE: Running only {total_steps} steps with {max_samples_per_domain} samples per domain")
    else:
        total_steps = config["total_steps"]
        max_samples_per_domain = None  # Load full dataset

    # Load REAL datasets from The Pile
    print("Loading real datasets from The Pile (EleutherAI/pile-uncopyrighted)...")
    print("  Domains:", list(DIVERSITY_SCORES.keys()))

    # Initialize tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token

    try:
        # Load real Pile domains
        domain_data = load_pile_domains(
            domains=list(DIVERSITY_SCORES.keys()),
            max_samples_per_domain=max_samples_per_domain,
            streaming=True,  # Use streaming to avoid downloading full dataset
            tokenizer=tokenizer
        )
        print(f"✅ Successfully loaded {len(domain_data)} domains from The Pile")

        # Filter diversity scores to only include successfully loaded domains
        filtered_diversity_scores = {
            domain: score for domain, score in DIVERSITY_SCORES.items()
            if domain in domain_data
        }

        if len(filtered_diversity_scores) < 2:
            raise RuntimeError(f"Need at least 2 domains for curriculum learning, only loaded {len(filtered_diversity_scores)}")

        print(f"Using {len(filtered_diversity_scores)} domains: {list(filtered_diversity_scores.keys())}")

    except Exception as e:
        print(f"❌ ERROR: Failed to load real Pile dataset: {e}")
        print("   Please ensure you have internet connection and datasets library installed.")
        raise

    # Create curriculum data loader (use filtered diversity scores)
    data_loader = CurriculumDataLoader(
        domain_data=domain_data,
        diversity_scores=filtered_diversity_scores,  # Only use successfully loaded domains
        condition=condition,
        batch_size=2 if smoke_test else config["batch_size"],  # Smaller batch for smoke test
        total_steps=total_steps,
        sequence_length=2047,
        gaussian_width=CURRICULUM_CONFIG["gaussian_width"],
        min_weight=CURRICULUM_CONFIG["min_weight"],
        seed=seed
    )

    # Optimizer
    optimizer = AdamW(
        model.parameters(),
        lr=config["lr"],
        betas=config["betas"],
        weight_decay=config["weight_decay"]
    )

    # Learning rate scheduler
    scheduler = CosineAnnealingLR(
        optimizer,
        T_max=total_steps - config["warmup_steps"],
        eta_min=config["lr"] * config["min_lr_ratio"]
    )

    # Training loop
    model.train()
    training_log = []
    checkpoint_steps = [int(total_steps * pct) for pct in CHECKPOINT_PERCENTAGES]

    print(f"\nStarting training: {total_steps} steps")
    start_time = time.time()

    for step, batch in enumerate(data_loader):
        if step >= total_steps:
            break

        # Move batch to device
        input_ids = batch['input_ids'].to(device)
        labels = batch['labels'].to(device)

        # Forward pass
        loss, logits = model(input_ids, labels)

        # Backward pass
        loss.backward()

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), config["gradient_clip"])

        # Optimizer step
        optimizer.step()
        optimizer.zero_grad()

        # Learning rate warmup
        if step < config["warmup_steps"]:
            lr_scale = (step + 1) / config["warmup_steps"]
            for param_group in optimizer.param_groups:
                param_group['lr'] = config["lr"] * lr_scale
        else:
            scheduler.step()

        # Log metrics
        if step % 10 == 0:
            current_lr = optimizer.param_groups[0]['lr']
            training_log.append({
                "step": step,
                "loss": loss.item(),
                "lr": current_lr,
                "progress": step / total_steps
            })

            if step % 50 == 0:
                elapsed = time.time() - start_time
                steps_per_sec = (step + 1) / elapsed
                print(f"Step {step}/{total_steps} | Loss: {loss.item():.4f} | LR: {current_lr:.2e} | {steps_per_sec:.2f} steps/s")

        # Save checkpoints
        if step + 1 in checkpoint_steps:
            checkpoint_path = output_dir / f"checkpoint_step{step+1}.pt"
            torch.save({
                'step': step + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': loss.item(),
            }, checkpoint_path)
            print(f"✅ Checkpoint saved: {checkpoint_path}")

    # Final checkpoint
    final_checkpoint = output_dir / "checkpoint_final.pt"
    torch.save({
        'step': total_steps,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': training_log[-1]['loss'] if training_log else 0.0,
    }, final_checkpoint)

    # Save training log
    log_path = output_dir / "training_log.json"
    with open(log_path, "w") as f:
        json.dump(training_log, f, indent=2)

    elapsed_time = time.time() - start_time
    print(f"\n✅ Training completed in {elapsed_time:.2f}s")

    return {
        "total_steps": total_steps,
        "final_loss": training_log[-1]['loss'] if training_log else 0.0,
        "training_time": elapsed_time,
        "smoke_test": smoke_test
    }
