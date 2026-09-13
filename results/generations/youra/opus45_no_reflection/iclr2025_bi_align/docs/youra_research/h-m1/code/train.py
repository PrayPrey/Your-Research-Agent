"""Training loop with stability monitoring."""
import json
import torch
from torch.optim import AdamW
from torch.optim.lr_scheduler import LRScheduler
from transformers import get_cosine_schedule_with_warmup
from tqdm import tqdm
from config import CONFIG
from models import compute_logps
from bidpo_loss import compute_bidpo_loss


def check_stability(loss_dict: dict) -> bool:
    return all(
        not (torch.isnan(torch.tensor(v)) or torch.isinf(torch.tensor(v)))
        for v in loss_dict.values()
    )


def train_loop(
    policy_model,
    reference_model,
    dataloader,
    optimizer: AdamW,
    scheduler: LRScheduler,
    tokenizer,
) -> dict:
    history = {
        "steps": [],
        "dpo_loss": [],
        "agency_loss": [],
        "total_loss": [],
        "grad_norm": [],
        "lr": [],
    }

    step = 0
    optimizer.zero_grad()
    pad_token_id = tokenizer.pad_token_id
    best_loss = float("inf")
    nan_count = 0

    total_steps = len(dataloader) * CONFIG.epochs
    pbar = tqdm(total=total_steps, desc="Training")

    for epoch in range(CONFIG.epochs):
        for i, batch in enumerate(dataloader):
            chosen_ids = batch["chosen_input_ids"].to(policy_model.device)
            chosen_mask = batch["chosen_attention_mask"].to(policy_model.device)
            rejected_ids = batch["rejected_input_ids"].to(policy_model.device)
            rejected_mask = batch["rejected_attention_mask"].to(policy_model.device)
            chosen_scores = batch["chosen_collab_score"].to(policy_model.device)
            rejected_scores = batch["rejected_collab_score"].to(policy_model.device)

            policy_chosen_lp = compute_logps(policy_model, chosen_ids, chosen_mask, pad_token_id)
            policy_rejected_lp = compute_logps(policy_model, rejected_ids, rejected_mask, pad_token_id)

            with torch.no_grad():
                ref_chosen_lp = compute_logps(reference_model, chosen_ids, chosen_mask, pad_token_id)
                ref_rejected_lp = compute_logps(reference_model, rejected_ids, rejected_mask, pad_token_id)

            loss, loss_dict = compute_bidpo_loss(
                policy_chosen_lp, policy_rejected_lp,
                ref_chosen_lp, ref_rejected_lp,
                chosen_scores, rejected_scores,
                CONFIG.beta, CONFIG.lambda_agency,
            )

            if not check_stability(loss_dict):
                nan_count += 1
                with open(f"{CONFIG.output_dir}/debug_info.json", "w") as f:
                    json.dump({"step": step, "loss_dict": loss_dict, "batch_idx": i}, f)
                raise RuntimeError(f"NaN/Inf detected at step {step}: {loss_dict}")

            (loss / CONFIG.grad_accum_steps).backward()

            if (i + 1) % CONFIG.grad_accum_steps == 0:
                grad_norm = torch.nn.utils.clip_grad_norm_(
                    policy_model.parameters(), CONFIG.grad_clip_norm
                )
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                step += 1

                if step % CONFIG.log_interval == 0:
                    history["steps"].append(step)
                    history["dpo_loss"].append(loss_dict["dpo_loss"])
                    history["agency_loss"].append(loss_dict["agency_loss"])
                    history["total_loss"].append(loss_dict["total_loss"])
                    history["grad_norm"].append(grad_norm.item() if hasattr(grad_norm, 'item') else grad_norm)
                    history["lr"].append(scheduler.get_last_lr()[0])

                    if loss_dict["total_loss"] < best_loss:
                        best_loss = loss_dict["total_loss"]
                        save_checkpoint(policy_model, f"{CONFIG.output_dir}/best.pt", is_best=True)

                    pbar.set_postfix({
                        "loss": f"{loss_dict['total_loss']:.4f}",
                        "dpo": f"{loss_dict['dpo_loss']:.4f}",
                        "agency": f"{loss_dict['agency_loss']:.4f}",
                    })

            pbar.update(1)

    pbar.close()
    history["nan_count"] = nan_count
    history["final_step"] = step
    return history


def save_checkpoint(model, path: str, is_best: bool = False) -> None:
    torch.save(model.state_dict(), path)


def get_scheduler(optimizer, num_training_steps: int):
    warmup_steps = int(num_training_steps * CONFIG.warmup_ratio)
    return get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=num_training_steps,
    )
