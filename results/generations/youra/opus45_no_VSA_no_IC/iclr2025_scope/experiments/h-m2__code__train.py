"""Training loop for single (model, rank, seed) run with SQuAD-v2 F1 evaluation."""
import os
import random
import numpy as np
import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup, default_data_collator
import evaluate

from config import TrainConfig, MODELS
from data import load_squad_v2, tokenize_squad
from model import load_base_model, load_tokenizer, apply_lora


def set_seed(seed: int) -> None:
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_one_run(
    model_id: str,
    rank: int,
    seed: int,
    cfg: TrainConfig,
    output_dir: str = "checkpoints",
    data_cache_dir: str | None = None,
) -> float:
    """Train LoRA adapter and return SQuAD-v2 F1 on full validation set."""
    set_seed(seed)
    os.makedirs(output_dir, exist_ok=True)

    tokenizer = load_tokenizer(model_id)
    dataset = load_squad_v2(cache_dir=data_cache_dir)
    tokenized = tokenize_squad(dataset, tokenizer, cfg.max_length)

    train_dataset = tokenized["train"]
    val_dataset = tokenized["validation"]

    train_loader = DataLoader(
        train_dataset,
        batch_size=cfg.batch_size,
        shuffle=True,
        collate_fn=default_data_collator,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=cfg.batch_size,
        shuffle=False,
        collate_fn=default_data_collator,
    )

    model = load_base_model(model_id)
    model = apply_lora(model, rank, alpha=2 * rank)
    model.print_trainable_parameters()

    optimizer = AdamW(model.parameters(), lr=cfg.lr)
    total_steps = len(train_loader) * cfg.epochs // cfg.grad_accum
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=cfg.warmup_steps,
        num_training_steps=total_steps,
    )

    device = next(model.parameters()).device
    model.train()

    for epoch in range(cfg.epochs):
        total_loss = 0
        optimizer.zero_grad()

        for step, batch in enumerate(train_loader):
            batch = {k: v.to(device) if hasattr(v, 'to') else v for k, v in batch.items() if k in ["input_ids", "attention_mask", "start_positions", "end_positions"]}
            outputs = model(**batch)
            loss = outputs.loss / cfg.grad_accum
            loss.backward()
            total_loss += outputs.loss.item()

            if (step + 1) % cfg.grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch + 1}/{cfg.epochs}, Loss: {avg_loss:.4f}")

        ckpt_path = os.path.join(output_dir, f"{model_id}_r{rank}_s{seed}_e{epoch}.pt")
        model.save_pretrained(ckpt_path)

    f1 = evaluate_squad_f1(model, val_loader, tokenizer, dataset["validation"], device)
    return f1


def evaluate_squad_f1(
    model,
    val_loader: DataLoader,
    tokenizer,
    val_dataset,
    device,
) -> float:
    """Compute SQuAD-v2 F1 using official evaluate library."""
    model.eval()
    all_start_logits = []
    all_end_logits = []
    all_example_ids = []

    with torch.no_grad():
        for batch in val_loader:
            input_batch = {k: v.to(device) for k, v in batch.items() if k in ["input_ids", "attention_mask"]}
            outputs = model(**input_batch)
            all_start_logits.extend(outputs.start_logits.cpu().numpy())
            all_end_logits.extend(outputs.end_logits.cpu().numpy())
            if "example_id" in batch:
                all_example_ids.extend(batch["example_id"])

    predictions = []
    references = []

    for idx, (start_logits, end_logits) in enumerate(zip(all_start_logits, all_end_logits)):
        start_idx = int(np.argmax(start_logits))
        end_idx = int(np.argmax(end_logits))

        if start_idx <= end_idx:
            answer_text = tokenizer.decode(
                val_loader.dataset[idx]["input_ids"][start_idx:end_idx + 1],
                skip_special_tokens=True,
            )
        else:
            answer_text = ""

        example_id = all_example_ids[idx] if all_example_ids else str(idx)

        no_answer_prob = float(start_logits[0] + end_logits[0])
        predictions.append({
            "id": example_id,
            "prediction_text": answer_text,
            "no_answer_probability": 1.0 / (1.0 + np.exp(-no_answer_prob)),
        })

        orig_example = val_dataset[idx]
        references.append({
            "id": example_id,
            "answers": orig_example["answers"],
        })

    squad_v2 = evaluate.load("squad_v2")
    result = squad_v2.compute(predictions=predictions, references=references)
    return result["f1"]


def compute_squad_f1(predictions: list[dict], references: list[dict]) -> float:
    """Wrapper for evaluate.load('squad_v2').compute()."""
    squad_v2 = evaluate.load("squad_v2")
    result = squad_v2.compute(predictions=predictions, references=references)
    return result["f1"]
