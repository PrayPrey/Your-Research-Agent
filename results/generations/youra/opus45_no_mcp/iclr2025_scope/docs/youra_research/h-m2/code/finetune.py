"""Fine-tuning for H-M2: Per-task LoRA fine-tuning"""

import os
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import LinearLR, SequentialLR
from tqdm import tqdm
from peft import LoraConfig, get_peft_model

from config import LORA_CONFIG, TRAIN_CONFIG
from data import load_task_loader
from model import load_proposed_model


def finetune_on_task(task_name: str, tokenizer, train_config: dict = None, output_dir: str = None):
    """
    LoRA-finetunes load_proposed_model() on task_name for train_config['epochs'].
    Returns {'model': nn.Module, 'loss_curve': list[float], 'checkpoint_path': str}
    """
    cfg = train_config or TRAIN_CONFIG
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "checkpoints")
    os.makedirs(output_dir, exist_ok=True)

    torch.manual_seed(cfg["seed"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    vocab_size = ((tokenizer.vocab_size + 127) // 128) * 128
    base_model = load_proposed_model(vocab_size=vocab_size, d_model=512, n_layers=4)

    peft_cfg = LoraConfig(
        r=LORA_CONFIG["r"],
        lora_alpha=LORA_CONFIG["lora_alpha"],
        target_modules=LORA_CONFIG["target_modules"],
        lora_dropout=LORA_CONFIG["lora_dropout"],
        bias="none",
    )
    model = get_peft_model(base_model, peft_cfg)
    model = model.to(device)

    loader = load_task_loader(task_name, tokenizer, max_length=cfg["max_length"], batch_size=cfg["batch_size"])

    optimizer = AdamW(model.parameters(), lr=cfg["lr"])

    total_steps = len(loader) * cfg["epochs"]
    warmup_steps = int(total_steps * cfg["warmup_pct"])

    warmup_scheduler = LinearLR(optimizer, start_factor=0.1, end_factor=1.0, total_iters=warmup_steps)
    decay_scheduler = LinearLR(optimizer, start_factor=1.0, end_factor=0.1, total_iters=total_steps - warmup_steps)
    scheduler = SequentialLR(optimizer, [warmup_scheduler, decay_scheduler], milestones=[warmup_steps])

    loss_curve = []
    model.train()

    for epoch in range(cfg["epochs"]):
        epoch_loss = 0.0
        steps = 0
        pbar = tqdm(loader, desc=f"Epoch {epoch+1}/{cfg['epochs']} [{task_name}]")

        for batch in pbar:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            attention_mask = batch.get("attention_mask")
            if attention_mask is not None:
                attention_mask = attention_mask.to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss

            loss.backward()

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

            epoch_loss += loss.item()
            steps += 1
            pbar.set_postfix({"loss": f"{loss.item():.4f}"})

        avg_loss = epoch_loss / max(steps, 1)
        loss_curve.append(avg_loss)
        print(f"  Epoch {epoch+1} avg loss: {avg_loss:.4f}")

    checkpoint_path = os.path.join(output_dir, f"{task_name}_checkpoint.pt")
    torch.save(model.state_dict(), checkpoint_path)
    print(f"  Saved checkpoint: {checkpoint_path}")

    return {
        "model": model,
        "loss_curve": loss_curve,
        "checkpoint_path": checkpoint_path,
    }
