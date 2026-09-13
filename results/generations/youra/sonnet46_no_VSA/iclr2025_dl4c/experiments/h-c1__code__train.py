"""
H-C1: SFT Training Script
Adapts H-E2 train.py for 7B scale.
Key deltas: MODEL_ID → 7B, attn_implementation=flash_attention_2,
no activation check (SHOULD_WORK gate), device_map=None for DeepSpeed.
"""
import argparse
import random
import sys
from pathlib import Path

import numpy as np
import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed as hf_set_seed
from trl import SFTConfig, SFTTrainer

from config import (
    MODEL_ID, CONDITIONS, SEEDS, FIXED_HPARAMS, EPOCHS_PER_CONDITION,
    CHECKPOINT_DIR, H_E2_DATASETS_DIR, LORA_ENABLED, LORA_CONFIG,
)
from data_loader import load_condition_dataset


def set_all_seeds(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    hf_set_seed(seed)


def load_model_and_tokenizer(model_id: str = MODEL_ID, use_lora: bool = False):
    """Load 7B model in bf16 with Flash Attention 2."""
    print(f"Loading model: {model_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # device_map=None: DeepSpeed ZeRO-3 handles device placement
    # Flash Attention 2 preferred for memory efficiency; fall back if not installed
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
            attn_implementation="flash_attention_2",
        )
    except (ImportError, ValueError):
        print("[WARN] flash_attention_2 unavailable; falling back to default attention")
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
        )

    if use_lora or LORA_ENABLED:
        from peft import LoraConfig as PeftLoraConfig, get_peft_model, TaskType
        peft_config = PeftLoraConfig(
            r=LORA_CONFIG["r"],
            lora_alpha=LORA_CONFIG["lora_alpha"],
            target_modules=LORA_CONFIG["target_modules"],
            lora_dropout=LORA_CONFIG["lora_dropout"],
            bias=LORA_CONFIG["bias"],
            task_type=TaskType.CAUSAL_LM,
        )
        model = get_peft_model(model, peft_config)
        model.print_trainable_parameters()
        print("[INFO] LoRA enabled — note this changes fine-tuning regime vs H-E2 full FT")

    return model, tokenizer


def run_sft(
    condition: str,
    seed: int,
    output_dir: str = CHECKPOINT_DIR,
    data_dir: str = H_E2_DATASETS_DIR,
    smoke: bool = False,
    use_lora: bool = False,
) -> str:
    """Train one SFT run; return checkpoint path."""
    set_all_seeds(seed)
    checkpoint_dir = f"{output_dir}/condition_{condition}_seed_{seed}"

    if Path(checkpoint_dir).exists() and not smoke:
        print(f"Checkpoint exists, skipping: {checkpoint_dir}")
        return checkpoint_dir

    print(f"\n{'='*60}")
    print(f"H-C1 Training: condition={condition}, seed={seed}, model={MODEL_ID}")
    print(f"Checkpoint: {checkpoint_dir}")
    print(f"{'='*60}")

    if smoke:
        dataset = Dataset.from_dict({
            "text": [
                "# Complete the following Python function:\n"
                "def add(a, b):\n    \"\"\"Add two numbers.\"\"\"\n"
                "\n    return a + b\n"
            ] * 5
        })
    else:
        dataset = load_condition_dataset(condition, data_dir)

    print(f"Dataset: {len(dataset)} examples")

    # Smoke: use a tiny model to avoid downloading 7B weights
    actual_model_id = "gpt2" if smoke else MODEL_ID
    model, tokenizer = load_model_and_tokenizer(model_id=actual_model_id, use_lora=use_lora)

    num_epochs = 1 if smoke else EPOCHS_PER_CONDITION[condition]
    # Smoke runs on CPU without bf16 to validate code paths without GPU
    import copy
    hparams = copy.copy(FIXED_HPARAMS)
    if smoke:
        hparams["bf16"] = False

    config = SFTConfig(
        output_dir=checkpoint_dir,
        num_train_epochs=num_epochs,
        seed=seed,
        save_strategy="no",
        logging_steps=10,
        report_to="none",
        max_steps=5 if smoke else -1,
        completion_only_loss=True,
        **hparams,
    )

    trainer = SFTTrainer(
        model=model,
        args=config,
        train_dataset=dataset,
    )

    trainer.train()
    trainer.save_model(checkpoint_dir)
    tokenizer.save_pretrained(checkpoint_dir)
    print(f"Saved checkpoint: {checkpoint_dir}")
    return checkpoint_dir


def run_all_training(
    output_dir: str = CHECKPOINT_DIR,
    data_dir: str = H_E2_DATASETS_DIR,
    use_lora: bool = False,
    skip_existing: bool = True,
) -> dict:
    """Train all 12 runs. Returns {f'{condition}_seed{seed}': checkpoint_path}."""
    checkpoint_map = {}
    for condition in CONDITIONS:
        for seed in SEEDS:
            key = f"{condition}_seed{seed}"
            ckpt = f"{output_dir}/condition_{condition}_seed_{seed}"
            if skip_existing and Path(ckpt).exists():
                print(f"Skipping (exists): {ckpt}")
                checkpoint_map[key] = ckpt
                continue
            path = run_sft(condition, seed, output_dir, data_dir, use_lora=use_lora)
            checkpoint_map[key] = path
    return checkpoint_map


def main():
    parser = argparse.ArgumentParser(description="H-C1 SFT Training (7B)")
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output_dir", default=CHECKPOINT_DIR)
    parser.add_argument("--data_dir", default=H_E2_DATASETS_DIR)
    parser.add_argument("--smoke", action="store_true", help="Smoke test (5 steps, synthetic data)")
    parser.add_argument("--lora", action="store_true", help="Use LoRA (OOM fallback)")
    args = parser.parse_args()

    run_sft(
        condition=args.condition,
        seed=args.seed,
        output_dir=args.output_dir,
        data_dir=args.data_dir,
        smoke=args.smoke,
        use_lora=args.lora,
    )


if __name__ == "__main__":
    main()
