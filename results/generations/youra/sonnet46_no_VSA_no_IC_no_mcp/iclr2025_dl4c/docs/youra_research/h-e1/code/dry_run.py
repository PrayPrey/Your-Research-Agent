"""dry_run.py — Sanity check: 1 epoch, 1% data, SFT only (no full training)"""
import json
import sys
from pathlib import Path

import torch
import yaml
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, DataCollatorForSeq2Seq, Trainer, TrainingArguments

from data_utils import load_apps_train
from reward import fraction_reward_fn


def main(config_path="config.yaml"):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    for d in ["logs", cfg["paths"]["checkpoints_dir"]]:
        Path(d).mkdir(parents=True, exist_ok=True)

    model_name = cfg["model_name"]
    print(f"[DRY RUN] Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"[DRY RUN] Loading model: {model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True
    )

    print("[DRY RUN] Loading APPS (1% subset)...")
    full = load_apps_train(tokenizer)
    sft_ds = full["sft"]
    n_samples = max(10, len(sft_ds) // 100)
    sft_ds = sft_ds.select(range(n_samples))
    print(f"[DRY RUN] Subset size: {n_samples}")

    training_args = TrainingArguments(
        output_dir="checkpoints/dry_run",
        learning_rate=cfg["training"]["lr"],
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        num_train_epochs=1,
        max_steps=5,
        bf16=True,
        seed=0,
        logging_steps=1,
        save_strategy="no",
        report_to="none",
    )

    collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)
    trainer = Trainer(model=model, args=training_args, train_dataset=sft_ds, data_collator=collator)
    print("[DRY RUN] Running 5 training steps...")
    result = trainer.train()
    loss = result.training_loss
    print(f"[DRY RUN] ✓ SFT training steps OK. loss={loss:.4f}")

    # Verify reward function
    print("[DRY RUN] Testing reward function...")
    rlef_ds = full["rlef"]
    sample = rlef_ds[0]
    rewards = fraction_reward_fn(
        completions=["print('hello')"],
        prompts=[sample["prompt"]],
        metadata=[{"test_cases": sample["test_cases"]}],
    )
    print(f"[DRY RUN] ✓ Reward function OK. reward={rewards[0]:.3f}")

    # Verify analyze imports
    import numpy as np
    from analyze import bootstrap_ci, compute_deltas
    dummy = {k: np.array([0.3] * 100) for k in ["humaneval", "mbpp", "lcb_easy", "lcb_medium", "lcb_hard"]}
    dummy_sft = {k: np.array([0.25] * 100) for k in dummy}
    deltas = compute_deltas(dummy, dummy_sft)
    boot = bootstrap_ci(dummy, dummy_sft, n_boot=50, seed=42)
    print(f"[DRY RUN] ✓ Analysis OK. delta_ratio={deltas['delta_ratio']:.2f}")

    print("\n[DRY RUN] ✅ ALL CHECKS PASSED")
    metrics = {"loss": loss, "steps": 5, "reward_fn_ok": True, "analyze_ok": True}
    with open("logs/dry_run_metrics.json", "w") as f:
        json.dump(metrics, f)
    return metrics


if __name__ == "__main__":
    cfg = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    main(cfg)
