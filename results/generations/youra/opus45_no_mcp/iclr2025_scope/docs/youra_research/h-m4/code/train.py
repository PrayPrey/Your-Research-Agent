"""Training for H-M4: LoRA fine-tuning for both architectures"""

import os
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import LinearLR, SequentialLR
from tqdm import tqdm
from peft import LoraConfig, get_peft_model

from config import LORA_CONFIG_TRANSFORMER, LORA_CONFIG_MAMBA, TRAIN_CONFIG, CHECKPOINTS_DIR
from model import load_baseline_model, load_proposed_model


def finetune_model(model_type: str, task_name: str, tokenizer, loader, train_config: dict = None, output_dir: str = None):
    """
    LoRA-finetunes model on task.
    model_type: "transformer" or "mamba"
    Returns {'model': nn.Module, 'loss_curve': list[float], 'checkpoint_path': str}
    """
    cfg = train_config or TRAIN_CONFIG
    if output_dir is None:
        output_dir = CHECKPOINTS_DIR
    os.makedirs(output_dir, exist_ok=True)

    torch.manual_seed(cfg["seed"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    vocab_size = ((tokenizer.vocab_size + 127) // 128) * 128

    if model_type == "transformer":
        base_model = load_baseline_model(vocab_size=vocab_size)
        lora_cfg = LORA_CONFIG_TRANSFORMER
    else:
        base_model = load_proposed_model(vocab_size=vocab_size)
        lora_cfg = LORA_CONFIG_MAMBA

    peft_cfg = LoraConfig(
        r=lora_cfg["r"],
        lora_alpha=lora_cfg["lora_alpha"],
        target_modules=lora_cfg["target_modules"],
        lora_dropout=lora_cfg["lora_dropout"],
        bias="none",
    )
    model = get_peft_model(base_model, peft_cfg)
    model = model.to(device)

    optimizer = AdamW(model.parameters(), lr=cfg["lr"], weight_decay=cfg.get("weight_decay", 0.01))

    total_steps = len(loader) * cfg["epochs"]
    warmup_steps = int(total_steps * cfg["warmup_pct"])

    warmup_scheduler = LinearLR(optimizer, start_factor=0.1, end_factor=1.0, total_iters=max(warmup_steps, 1))
    decay_scheduler = LinearLR(optimizer, start_factor=1.0, end_factor=0.1, total_iters=max(total_steps - warmup_steps, 1))
    scheduler = SequentialLR(optimizer, [warmup_scheduler, decay_scheduler], milestones=[warmup_steps])

    loss_curve = []
    model.train()

    for epoch in range(cfg["epochs"]):
        epoch_loss = 0.0
        steps = 0
        pbar = tqdm(loader, desc=f"Epoch {epoch+1}/{cfg['epochs']} [{model_type}/{task_name}]")

        for batch in pbar:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            attention_mask = batch.get("attention_mask")
            if attention_mask is not None:
                attention_mask = attention_mask.to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss

            loss.backward()

            if cfg.get("grad_clip"):
                torch.nn.utils.clip_grad_norm_(model.parameters(), cfg["grad_clip"])

            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

            epoch_loss += loss.item()
            steps += 1
            pbar.set_postfix({"loss": f"{loss.item():.4f}"})

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        avg_loss = epoch_loss / max(steps, 1)
        loss_curve.append(avg_loss)
        print(f"  {model_type}/{task_name} Epoch {epoch+1} avg loss: {avg_loss:.4f}")

    checkpoint_path = os.path.join(output_dir, f"{model_type}_{task_name}_checkpoint.pt")
    torch.save(model.state_dict(), checkpoint_path)
    print(f"  Saved checkpoint: {checkpoint_path}")

    return {
        "model": model,
        "loss_curve": loss_curve,
        "checkpoint_path": checkpoint_path,
    }


def run_all_training(tokenizer, benchmark_suite, train_config=None):
    """Train both architectures on all tasks. Returns {(arch, task): result}"""
    results = {}

    for model_type in ["transformer", "mamba"]:
        for task_name, task_info in benchmark_suite.items():
            print(f"\n{'='*50}")
            print(f"Training {model_type} on {task_name}")
            print(f"{'='*50}")

            try:
                result = finetune_model(
                    model_type=model_type,
                    task_name=task_name,
                    tokenizer=tokenizer,
                    loader=task_info["loader"],
                    train_config=train_config,
                )
                results[(model_type, task_name)] = result
            except Exception as e:
                print(f"  Error training {model_type}/{task_name}: {e}")
                results[(model_type, task_name)] = None

    return results
