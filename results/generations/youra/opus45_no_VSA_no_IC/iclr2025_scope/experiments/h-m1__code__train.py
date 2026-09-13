"""Training loop with AdamW + warmup/cosine decay."""
import torch
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup
from peft import PeftModel
from config import TrainConfig, SEED, set_seed


def make_optimizer_and_scheduler(model: PeftModel, cfg: TrainConfig, num_training_steps: int):
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr)
    warmup_steps = int(num_training_steps * cfg.warmup_ratio)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=num_training_steps
    )
    return optimizer, scheduler


def train_step(model: PeftModel, batch: dict, device) -> float:
    input_ids = batch["input_ids"].to(device)
    attention_mask = batch["attention_mask"].to(device)

    labels = input_ids.clone()
    labels[:, :-1] = input_ids[:, 1:]
    labels[:, -1] = -100
    labels[attention_mask == 0] = -100

    outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
    loss = outputs.loss
    if torch.isnan(loss):
        return torch.tensor(0.0, device=device, requires_grad=True)
    return loss


def train_qa(
    model: PeftModel,
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg: TrainConfig,
    tokenizer,
    seed: int = SEED,
    patience: int = 2,
) -> tuple[PeftModel, dict]:
    set_seed(seed)
    device = next(model.parameters()).device

    num_steps = len(train_loader) * cfg.epochs // cfg.grad_accum
    optimizer, scheduler = make_optimizer_and_scheduler(model, cfg, num_steps)

    history = {"train_loss": [], "val_loss": []}
    best_loss = float("inf")
    no_improve = 0

    for epoch in range(cfg.epochs):
        model.train()
        epoch_loss = 0.0
        optimizer.zero_grad()

        for i, batch in enumerate(train_loader):
            loss = train_step(model, batch, device)
            loss = loss / cfg.grad_accum
            loss.backward()
            epoch_loss += loss.item() * cfg.grad_accum

            if (i + 1) % cfg.grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

        avg_train_loss = epoch_loss / len(train_loader)
        history["train_loss"].append(avg_train_loss)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch in val_loader:
                loss = train_step(model, batch, device)
                val_loss += loss.item()
        avg_val_loss = val_loss / len(val_loader)
        history["val_loss"].append(avg_val_loss)

        print(f"  Epoch {epoch+1}/{cfg.epochs}: train_loss={avg_train_loss:.4f}, val_loss={avg_val_loss:.4f}")

        if avg_val_loss < best_loss:
            best_loss = avg_val_loss
            no_improve = 0
        else:
            no_improve += 1

        if no_improve >= patience:
            print(f"  Early stopping at epoch {epoch+1}")
            break

    return model, history
