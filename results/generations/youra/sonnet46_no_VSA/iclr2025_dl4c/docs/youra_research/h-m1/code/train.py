"""
H-E2: SFT Training Script
TRL SFTTrainer + DeepSpeed ZeRO-3, bf16, completion_only_loss.
Variable epochs per condition; 3 seeds; checkpoint save.
"""
import argparse
import random
import sys
from pathlib import Path

import numpy as np
import torch
from datasets import load_from_disk
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed as hf_set_seed
from trl import SFTConfig, SFTTrainer

# ── Constants ─────────────────────────────────────────────────────────────────
MODEL_ID = "deepseek-ai/deepseek-coder-1.3b-base"
CONDITIONS = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
SEEDS = [42, 123, 777]

# L-A2-1: Fixed hyperparameters
FIXED_HPARAMS = {
    "learning_rate": 2e-5,
    "lr_scheduler_type": "cosine",
    "warmup_ratio": 0.05,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "bf16": True,
    "max_length": 2048,
    "weight_decay": 0.01,
    "adam_beta1": 0.9,
    "adam_beta2": 0.95,
    "dataset_text_field": "text",
}

# L-A2-3: Variable epochs for token budget equalization
EPOCHS_PER_CONDITION = {
    "humaneval_only": 6,
    "mbpp_only": 3,
    "leetcode_only": 1,
    "equal_mix": 2,
}

# L-A2-4: Activation verification thresholds
BASE_HUMANEVAL = 0.15
BASE_MBPP = 0.45
IMPROVEMENT_THRESHOLD = 0.03  # +3 pp required on >= 1 benchmark
ACTIVATION_MARGIN = 0.03


# ── L-A2-3: Seed setting ──────────────────────────────────────────────────────
def set_all_seeds(seed: int) -> None:
    """Set all RNG sources for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    hf_set_seed(seed)


# ── L-A2-1: Model loading ─────────────────────────────────────────────────────
def load_model_and_tokenizer(model_id: str = MODEL_ID):
    """Load base model and tokenizer in bf16."""
    print(f"Loading model: {model_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        dtype=torch.bfloat16,
    )
    return model, tokenizer


# ── L-A2-4: SFT activation verification ─────────────────────────────────────
def verify_sft_activation(
    pass1_humaneval: float,
    pass1_mbpp: float,
    condition: str,
) -> bool:
    """Return True if SFT improved over base on >= 1 benchmark by IMPROVEMENT_THRESHOLD."""
    humaneval_ok = (pass1_humaneval - BASE_HUMANEVAL) >= IMPROVEMENT_THRESHOLD
    mbpp_ok = (pass1_mbpp - BASE_MBPP) >= IMPROVEMENT_THRESHOLD
    activated = humaneval_ok or mbpp_ok
    if not activated:
        print(
            f"[ABORT] condition={condition} failed activation check: "
            f"HumanEval={pass1_humaneval:.3f} (base={BASE_HUMANEVAL}), "
            f"MBPP={pass1_mbpp:.3f} (base={BASE_MBPP}). "
            "Check LR, dedup, or data formatting."
        )
    return activated


def quick_eval(checkpoint_dir: str, benchmark: str) -> float:
    """Run quick EvalPlus evaluation after training. Returns pass@1."""
    import json
    import subprocess
    result = subprocess.run(
        [
            sys.executable, "-m", "evalplus.evaluate",
            "--model", checkpoint_dir,
            "--dataset", benchmark,
            "--backend", "hf",
            "--greedy",
        ],
        capture_output=True, text=True
    )
    # Parse pass@1 from output
    for line in result.stdout.split("\n"):
        if "pass@1" in line.lower() or "pass_at_1" in line.lower():
            # Try to extract float
            parts = line.split(":")
            if len(parts) >= 2:
                try:
                    return float(parts[-1].strip().rstrip(",").rstrip("}"))
                except ValueError:
                    pass
    # Try to read result file
    result_files = list(Path(checkpoint_dir).parent.glob(f"*{benchmark}*.json"))
    if result_files:
        with open(result_files[0]) as f:
            data = json.load(f)
        if "pass@1" in data:
            return float(data["pass@1"])
    print(f"[WARN] Could not parse pass@1 for {benchmark} from: {result.stdout[-500:]}")
    return 0.0


# ── L-A2-1+2+3: Main SFT run ──────────────────────────────────────────────────
def run_sft(
    condition: str,
    seed: int,
    data_dir: str,
    output_dir: str,
    smoke: bool = False,
    skip_activation_check: bool = False,
) -> None:
    """Train one SFT run; saves checkpoint to output_dir/condition_{condition}_seed_{seed}."""
    set_all_seeds(seed)
    checkpoint_dir = f"{output_dir}/condition_{condition}_seed_{seed}"

    if Path(checkpoint_dir).exists():
        print(f"Checkpoint exists, skipping: {checkpoint_dir}")
        return

    print(f"\n{'='*60}")
    print(f"Training: condition={condition}, seed={seed}")
    print(f"Checkpoint: {checkpoint_dir}")
    print(f"{'='*60}")

    # Load dataset
    data_path = Path(data_dir) / condition
    if smoke:
        # For smoke test, use a tiny synthetic dataset
        from datasets import Dataset
        dataset = Dataset.from_dict({
            "text": [
                "# Complete the following Python function:\n"
                "def add(a, b):\n    \"\"\"Add two numbers.\"\"\"\n"
                "\n    return a + b\n"
            ] * 5
        })
    elif data_path.exists():
        dataset = load_from_disk(str(data_path))
    else:
        print(f"[ERROR] Data not found at {data_path}. Run prepare_data.py first.")
        sys.exit(1)

    print(f"Dataset: {len(dataset)} examples")

    model, tokenizer = load_model_and_tokenizer()

    # L-A2-1: SFTConfig construction; completion_only_loss=True replaces DataCollatorForCompletionOnlyLM
    num_epochs = 1 if smoke else EPOCHS_PER_CONDITION[condition]
    config = SFTConfig(
        output_dir=checkpoint_dir,
        num_train_epochs=num_epochs,
        seed=seed,
        save_strategy="no",      # save only at end
        logging_steps=10,
        report_to="none",
        max_steps=5 if smoke else -1,
        completion_only_loss=True,
        **FIXED_HPARAMS,
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

    # L-A2-4: Activation verification (only first seed to avoid overhead)
    if not smoke and not skip_activation_check and seed == SEEDS[0]:
        print(f"\nRunning activation verification for condition={condition}...")
        pass1_he = quick_eval(checkpoint_dir, "humaneval")
        pass1_mbpp = quick_eval(checkpoint_dir, "mbpp")
        activated = verify_sft_activation(pass1_he, pass1_mbpp, condition)
        if not activated:
            print(f"[WARN] Activation check failed for {condition}. Continuing anyway (multi-seed).")


def main():
    parser = argparse.ArgumentParser(description="H-E2 SFT Training")
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--data_dir", default="data/sft_sources")
    parser.add_argument("--output_dir", default="checkpoints")
    parser.add_argument("--smoke", action="store_true", help="Smoke test (5 steps only)")
    parser.add_argument("--skip_activation_check", action="store_true")
    args = parser.parse_args()

    run_sft(
        condition=args.condition,
        seed=args.seed,
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        smoke=args.smoke,
        skip_activation_check=args.skip_activation_check,
    )


if __name__ == "__main__":
    main()
