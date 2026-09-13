"""Training loop for H-E1"""

import os
import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import get_cosine_schedule_with_warmup, set_seed

from config import TRAIN_CONFIG, BENCHMARKS
from data import load_benchmark, format_for_causal_lm, get_benchmark_split


def train_one_benchmark(model, tokenizer, dataset, train_config, benchmark_name, output_dir):
    """Fine-tune model on a single benchmark."""
    set_seed(train_config["seed"])

    device = next(model.parameters()).device

    def collate_fn(batch):
        return {
            "input_ids": torch.stack([torch.tensor(x["input_ids"]) for x in batch]).to(device),
            "attention_mask": torch.stack([torch.tensor(x["attention_mask"]) for x in batch]).to(device),
            "labels": torch.stack([torch.tensor(x["labels"]) for x in batch]).to(device),
        }

    loader = DataLoader(
        dataset,
        batch_size=train_config["batch_size"],
        shuffle=True,
        collate_fn=collate_fn,
    )

    optimizer = AdamW(
        model.parameters(),
        lr=train_config["lr"],
        weight_decay=train_config["weight_decay"],
        betas=train_config["betas"],
    )

    total_steps = len(loader) * train_config["epochs"] // train_config["grad_accum"]
    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=train_config["warmup_steps"],
        num_training_steps=total_steps,
    )

    loss_curve = []
    model.train()

    for epoch in range(train_config["epochs"]):
        for i, batch in enumerate(loader):
            out = model(**batch)
            loss = out.loss / train_config["grad_accum"]
            loss.backward()

            if (i + 1) % train_config["grad_accum"] == 0:
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

            loss_curve.append(loss.item() * train_config["grad_accum"])

    checkpoint_path = os.path.join(output_dir, f"{benchmark_name}_checkpoint")
    os.makedirs(checkpoint_path, exist_ok=True)
    model.save_pretrained(checkpoint_path)

    return {"loss_curve": loss_curve, "checkpoint_path": checkpoint_path}


def run_all_training(model_fn, lora_config, tokenizer, tag, output_dir):
    """Train model on all benchmarks."""
    results = {}

    for name in BENCHMARKS.keys():
        print(f"\n{'='*50}")
        print(f"Training {tag} on {name}")
        print(f"{'='*50}")

        ds = load_benchmark(name)
        split = get_benchmark_split(name)
        train_ds = ds.get("train", ds.get(split))

        if train_ds is None:
            print(f"Warning: No training data for {name}, skipping")
            continue

        if len(train_ds) > 5000:
            train_ds = train_ds.select(range(5000))

        formatted_ds = format_for_causal_lm(train_ds, tokenizer)

        model = model_fn(lora_config)
        model_output_dir = os.path.join(output_dir, tag)
        os.makedirs(model_output_dir, exist_ok=True)

        results[name] = train_one_benchmark(
            model, tokenizer, formatted_ds, TRAIN_CONFIG, name, model_output_dir
        )

        del model
        torch.cuda.empty_cache()

    return results
