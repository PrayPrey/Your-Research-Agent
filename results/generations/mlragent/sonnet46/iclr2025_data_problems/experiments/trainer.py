"""Training loop for DynaMix experiments."""

import logging
import time
import numpy as np
import torch
import torch.nn.functional as F
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

from config import (BATCH_SIZE, SEQ_LEN, LEARNING_RATE, WEIGHT_DECAY,
                    MAX_STEPS, EVAL_INTERVAL, WARMUP_STEPS, DOMAINS, DEVICE)
from baselines import evaluate_model, compute_perplexity

logger = logging.getLogger(__name__)


def get_lr(step, max_lr, min_lr, warmup_steps, max_steps):
    """Cosine LR with linear warmup."""
    if step < warmup_steps:
        return max_lr * step / warmup_steps
    if step > max_steps:
        return min_lr
    decay_ratio = (step - warmup_steps) / (max_steps - warmup_steps)
    coeff = 0.5 * (1.0 + np.cos(np.pi * decay_ratio))
    return min_lr + coeff * (max_lr - min_lr)


def compute_domain_losses(model, dataset, batch_size=8, device=DEVICE):
    """Compute per-domain loss for SNR estimation."""
    domain_losses = []
    domain_snrs = []

    model.eval()
    with torch.no_grad():
        for domain in DOMAINS:
            batch = dataset.get_batch(domain, batch_size, device)
            x = batch[:, :-1]
            y = batch[:, 1:]

            # Per-sample losses
            logits, _ = model(x)
            per_sample_losses = []
            for i in range(len(batch)):
                loss_i = F.cross_entropy(logits[i], y[i])
                per_sample_losses.append(loss_i.item())

            mean_loss = np.mean(per_sample_losses)
            var_loss = np.var(per_sample_losses) + 1e-8
            snr = mean_loss**2 / var_loss

            domain_losses.append(mean_loss)
            domain_snrs.append(snr)

    model.train()
    return domain_losses, domain_snrs


def train_model(model, dataset, mixer, eval_data, max_steps=MAX_STEPS,
                eval_interval=EVAL_INTERVAL, device=DEVICE, run_name=""):
    """Train model with given mixer for max_steps steps.

    Returns:
        metrics: dict with training history
    """
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)

    train_losses = []
    eval_losses = {domain: [] for domain in DOMAINS}
    eval_steps = []
    mixture_log = []
    domain_eval_losses = []  # average eval loss over all domains

    step = 0
    start_time = time.time()

    # Initial evaluation
    eval_result = evaluate_model(model, eval_data, device)
    avg_eval_loss = np.mean(list(eval_result.values()))
    for domain in DOMAINS:
        if domain in eval_result:
            eval_losses[domain].append(eval_result[domain])
        else:
            eval_losses[domain].append(float('nan'))
    eval_steps.append(0)
    domain_eval_losses.append(avg_eval_loss)

    logger.info(f"[{run_name}] Step 0 | Avg Eval Loss: {avg_eval_loss:.4f}")

    # Compute initial domain losses for mixer
    domain_train_losses, domain_snrs = compute_domain_losses(model, dataset, device=device)

    while step < max_steps:
        # Get mixture weights
        if hasattr(mixer, 'get_weights'):
            if hasattr(mixer, 'snr_tracker'):
                # DynaMix
                weights = mixer.get_weights(eval_loss=avg_eval_loss)
                # Update SNR tracker
                for i, (dl, ds) in enumerate(zip(domain_train_losses, domain_snrs)):
                    mixer.snr_tracker.update(i, dl, max(ds * 0.1, 0.01))
            else:
                # Other mixers
                weights = mixer.get_weights(
                    domain_losses=domain_train_losses,
                    domain_snrs=domain_snrs
                )
        else:
            weights = np.ones(len(DOMAINS)) / len(DOMAINS)

        # Get mixed batch
        batch = dataset.get_mixed_batch(weights, BATCH_SIZE, device)
        x = batch[:, :-1]
        y = batch[:, 1:]

        # LR schedule
        lr = get_lr(step, LEARNING_RATE, LEARNING_RATE * 0.1, WARMUP_STEPS, max_steps)
        for param_group in optimizer.param_groups:
            param_group['lr'] = lr

        # Forward and backward
        model.train()
        _, loss = model(x, y)

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        train_losses.append(loss.item())
        mixture_log.append(weights.copy())

        step += 1

        # Update mixer with new losses
        if step % 20 == 0:
            domain_train_losses, domain_snrs = compute_domain_losses(
                model, dataset, batch_size=4, device=device
            )
            if hasattr(mixer, 'update'):
                mixer.update(domain_train_losses, snrs=domain_snrs)

        # Evaluation
        if step % eval_interval == 0 or step == max_steps:
            eval_result = evaluate_model(model, eval_data, device)
            avg_eval_loss = np.mean(list(eval_result.values()))
            domain_eval_losses.append(avg_eval_loss)

            for domain in DOMAINS:
                if domain in eval_result:
                    eval_losses[domain].append(eval_result[domain])
                else:
                    eval_losses[domain].append(float('nan'))
            eval_steps.append(step)

            elapsed = time.time() - start_time
            recent_train = np.mean(train_losses[-eval_interval:]) if len(train_losses) >= eval_interval else np.mean(train_losses)
            logger.info(
                f"[{run_name}] Step {step}/{max_steps} | "
                f"Train Loss: {recent_train:.4f} | "
                f"Eval Loss: {avg_eval_loss:.4f} | "
                f"Weights: {[f'{w:.2f}' for w in weights]} | "
                f"Elapsed: {elapsed:.1f}s"
            )

    # Compute smoothed train loss
    window = max(1, len(train_losses) // 20)
    smoothed_train = []
    for i in range(0, len(train_losses), window):
        smoothed_train.append(np.mean(train_losses[i:i+window]))

    metrics = {
        "train_losses": train_losses,
        "eval_losses": eval_losses,
        "eval_steps": eval_steps,
        "domain_eval_losses": domain_eval_losses,
        "mixture_log": [m.tolist() for m in mixture_log],
        "final_eval_loss": avg_eval_loss,
        "final_domain_losses": {d: eval_losses[d][-1] for d in DOMAINS if eval_losses[d]},
        "final_perplexity": {d: compute_perplexity(eval_losses[d][-1])
                             for d in DOMAINS if eval_losses[d] and not np.isnan(eval_losses[d][-1])},
    }

    return metrics
