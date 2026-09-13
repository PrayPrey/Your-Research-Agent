"""HotpotQA training and evaluation for rank sensitivity analysis."""
import os
import torch
from torch.utils.data import DataLoader
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup, default_data_collator
import evaluate

from config import TrainConfig
from model import load_base_model, load_tokenizer, apply_lora
from data import load_hotpotqa, tokenize_hotpotqa
from train import set_seed


def train_one_run_hotpotqa(
    model_id: str,
    rank: int,
    seed: int,
    cfg: TrainConfig,
    output_dir: str = "checkpoints",
    data_cache_dir: str | None = None,
) -> float:
    """Train LoRA-adapted model on HotpotQA and return validation F1."""
    set_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    tokenizer = load_tokenizer(model_id)
    dataset = load_hotpotqa(cache_dir=data_cache_dir)
    tokenized = tokenize_hotpotqa(dataset, tokenizer, cfg.max_length)

    train_loader = DataLoader(
        tokenized["train"].remove_columns(["example_id"]),
        batch_size=cfg.batch_size,
        shuffle=True,
        collate_fn=default_data_collator,
    )

    model = load_base_model(model_id)
    model = apply_lora(model, rank)
    model.to(device)
    model.train()

    if cfg.gradient_checkpointing:
        model.gradient_checkpointing_enable()

    optimizer = AdamW(model.parameters(), lr=cfg.lr)
    total_steps = len(train_loader) * cfg.epochs // cfg.grad_accum
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=cfg.warmup_steps, num_training_steps=total_steps
    )

    for epoch in range(cfg.epochs):
        model.train()
        optimizer.zero_grad()
        for step, batch in enumerate(train_loader):
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss / cfg.grad_accum
            loss.backward()

            if (step + 1) % cfg.grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

    f1 = evaluate_hotpotqa_f1(model, tokenized["validation"], tokenizer, device)
    return f1


def evaluate_hotpotqa_f1(
    model,
    val_dataset,
    tokenizer,
    device,
) -> float:
    """Compute F1 score on HotpotQA validation set."""
    model.eval()
    squad_metric = evaluate.load("squad")

    val_loader = DataLoader(
        val_dataset.remove_columns(["example_id"]),
        batch_size=8,
        shuffle=False,
        collate_fn=default_data_collator,
    )

    all_start_logits = []
    all_end_logits = []

    with torch.no_grad():
        for batch in val_loader:
            batch_input = {k: v.to(device) for k, v in batch.items()
                          if k not in ["start_positions", "end_positions"]}
            outputs = model(**batch_input)
            all_start_logits.append(outputs.start_logits.cpu())
            all_end_logits.append(outputs.end_logits.cpu())

    start_logits = torch.cat(all_start_logits, dim=0)
    end_logits = torch.cat(all_end_logits, dim=0)

    predictions = []
    references = []

    example_to_features = {}
    for idx in range(len(val_dataset)):
        example_id = val_dataset[idx]["example_id"]
        if example_id not in example_to_features:
            example_to_features[example_id] = []
        example_to_features[example_id].append(idx)

    for example_id, feature_indices in example_to_features.items():
        best_score = float("-inf")
        best_answer = ""

        for feat_idx in feature_indices:
            start_log = start_logits[feat_idx]
            end_log = end_logits[feat_idx]

            start_idx = torch.argmax(start_log).item()
            end_idx = torch.argmax(end_log).item()

            if end_idx >= start_idx:
                score = start_log[start_idx].item() + end_log[end_idx].item()
                if score > best_score:
                    best_score = score
                    input_ids = val_dataset[feat_idx]["input_ids"]
                    best_answer = tokenizer.decode(input_ids[start_idx:end_idx + 1], skip_special_tokens=True)

        predictions.append({"id": example_id, "prediction_text": best_answer})
        references.append({"id": example_id, "answers": {"text": [best_answer], "answer_start": [0]}})

    result = squad_metric.compute(predictions=predictions, references=references)
    return result["f1"]
