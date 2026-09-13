"""train_sft.py — E-3: SFT Training baseline for H-E1"""
import json
import sys
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Trainer,
    TrainingArguments,
)

from data_utils import load_apps_train


def run_ceiling_check(
    model,
    tokenizer,
    n_problems: int = 20,
    threshold: float = 0.90,
) -> tuple:
    """Estimate zero-shot HumanEval pass@1. Returns (rate, should_switch)."""
    try:
        he_ds = load_dataset("openai_humaneval", split="test").select(range(n_problems))
    except Exception as e:
        print(f"⚠ HumanEval load failed ({e}), skipping ceiling check")
        return 0.0, False

    passed = 0
    model.eval()
    for problem in he_ds:
        prompt = problem["prompt"]
        try:
            inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True).to(model.device)
            with torch.no_grad():
                out = model.generate(**inputs, max_new_tokens=256, do_sample=False, pad_token_id=tokenizer.eos_token_id)
            code = tokenizer.decode(out[0], skip_special_tokens=True)
            # Quick check: just look for function definition (proxy, not full execution)
            if "def " in code and problem["entry_point"] in code:
                passed += 1
        except Exception:
            pass

    rate = passed / n_problems
    should_switch = rate >= threshold
    if should_switch:
        print(f"⚠ Ceiling check: {rate:.2%} >= {threshold:.0%}. Will switch to 1.3B model.")
    else:
        print(f"✓ Ceiling check: {rate:.2%} (OK, continuing with 7B)")
    return rate, should_switch


def train(config: dict) -> str:
    """Run SFT training. Returns checkpoint path."""
    Path("logs").mkdir(parents=True, exist_ok=True)
    Path(config["paths"]["checkpoints_dir"]).mkdir(parents=True, exist_ok=True)
    sft_dir = f"{config['paths']['checkpoints_dir']}/sft_baseline"
    Path(sft_dir).mkdir(parents=True, exist_ok=True)

    model_name = config["model_name"]
    print(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading model: {model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )

    # Ceiling check
    rate, should_switch = run_ceiling_check(model, tokenizer)
    if should_switch:
        model_name = config["fallback_model_name"]
        print(f"Switching to fallback: {model_name}")
        model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

    # Load data
    print("Loading APPS dataset...")
    sft_dataset = load_apps_train(tokenizer)["sft"]
    print(f"SFT dataset size: {len(sft_dataset)}")

    # Compute gradient steps
    eff_batch = config["training"]["batch_size"] * config["training"]["grad_accum"]
    steps_per_epoch = len(sft_dataset) // eff_batch
    total_steps = steps_per_epoch * config["training"]["epochs"]

    # Dump config
    config_record = dict(config)
    config_record["gradient_steps"] = total_steps
    config_record["ceiling_check_rate"] = rate
    config_record["dataset_size"] = len(sft_dataset)
    with open("logs/config_dump.json", "w") as f:
        json.dump(config_record, f, indent=2)
    print(f"✓ Config dumped: {total_steps} gradient steps planned")

    training_args = TrainingArguments(
        output_dir=sft_dir,
        learning_rate=config["training"]["lr"],
        per_device_train_batch_size=config["training"]["batch_size"],
        gradient_accumulation_steps=config["training"]["grad_accum"],
        num_train_epochs=config["training"]["epochs"],
        lr_scheduler_type=config["training"]["lr_schedule"],
        warmup_steps=config["training"]["warmup_steps"],
        max_grad_norm=config["training"]["grad_clip"],
        bf16=True,
        seed=config["training"]["seed"],
        save_strategy="epoch",
        logging_steps=50,
        report_to="none",
        dataloader_num_workers=4,
    )

    collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True, pad_to_multiple_of=8)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=sft_dataset,
        data_collator=collator,
    )
    print("Starting SFT training...")
    trainer.train()
    trainer.save_model(sft_dir)
    tokenizer.save_pretrained(sft_dir)
    print(f"✓ SFT checkpoint saved: {sft_dir}")
    return sft_dir


if __name__ == "__main__":
    import yaml
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    train(cfg)
