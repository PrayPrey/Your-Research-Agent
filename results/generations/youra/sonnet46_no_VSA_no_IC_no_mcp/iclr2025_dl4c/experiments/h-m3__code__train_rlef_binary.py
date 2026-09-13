"""train_rlef_binary.py — H-M3: GRPO training with binary reward function."""
import json
import sys
from pathlib import Path

H_M3_CODE = Path(__file__).parent
H_E1_CODE = Path(__file__).parents[2] / "h-e1" / "code"
if str(H_M3_CODE) not in sys.path:
    sys.path.insert(0, str(H_M3_CODE))
if str(H_E1_CODE) not in sys.path:
    sys.path.insert(1, str(H_E1_CODE))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

from grpo_trainer import SimpleGRPOTrainer
from data_utils import load_apps_train
from reward_binary import binary_reward_fn, verify_reward_formulation_active
from config import H_M3_Config


def train_rlef_binary(cfg: H_M3_Config = None) -> str:
    """Train RLEF-Binary from scratch (or SFT checkpoint if available).

    Returns path to saved checkpoint.
    """
    if cfg is None:
        cfg = H_M3_Config()

    output_dir = Path(__file__).parent / cfg.binary_checkpoint_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    logs_dir = Path(__file__).parent / cfg.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)

    reward_log = str(logs_dir / "reward_monitoring_binary.jsonl")

    print(f"=" * 60)
    print(f"RLEF-Binary Training (H-M3)")
    print(f"  Model:       {cfg.model_name}")
    print(f"  Max steps:   {cfg.max_steps}")
    print(f"  G:           {cfg.num_generations}")
    print(f"  Reward:      binary (all-or-nothing)")
    print(f"  Output:      {output_dir}")
    print(f"=" * 60)

    # Load model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32

    # Use SFT checkpoint if available, else base model
    model_path = cfg.sft_checkpoint if Path(cfg.sft_checkpoint).exists() else cfg.model_name
    print(f"Loading model from: {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(
        model_path, trust_remote_code=True, use_fast=True
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=dtype,
        trust_remote_code=True,
        device_map="auto" if device == "cuda" else None,
    )

    ref_model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=dtype,
        trust_remote_code=True,
        device_map="auto" if device == "cuda" else None,
    )
    ref_model.eval()
    for p in ref_model.parameters():
        p.requires_grad = False

    # Load APPS dataset
    print("Loading APPS dataset...")
    ds_raw = load_dataset("codeparrot/apps", split="train", trust_remote_code=True)
    ds_raw = ds_raw.select(range(min(cfg.apps_n_samples, len(ds_raw))))

    # Format for RLEF (prompt + test_cases for reward)
    from data_utils import format_rlef_sample
    rlef_ds = ds_raw.map(format_rlef_sample, remove_columns=ds_raw.column_names)

    # Build monitoring callback to track fraction vs binary reward difference
    fraction_reward_log = []
    binary_reward_log = []

    def monitored_binary_reward_fn(completions, prompts, metadata, **kwargs):
        """Binary reward + monitoring for mechanism activation."""
        from reward import fraction_reward_fn as frac_fn
        b_rewards = binary_reward_fn(completions, prompts, metadata, **kwargs)
        f_rewards = frac_fn(completions, prompts, metadata, **kwargs)
        fraction_reward_log.extend(f_rewards)
        binary_reward_log.extend(b_rewards)
        return b_rewards

    trainer = SimpleGRPOTrainer(
        model=model,
        ref_model=ref_model,
        tokenizer=tokenizer,
        reward_fn=monitored_binary_reward_fn,
        dataset=rlef_ds,
        output_dir=str(output_dir),
        lr=cfg.lr,
        batch_size=cfg.batch_size,
        grad_accum=cfg.grad_accum,
        num_epochs=cfg.num_epochs,
        G=cfg.num_generations,
        beta=cfg.beta,
        max_new_tokens=cfg.max_new_tokens,
        temperature=cfg.temperature,
        seed=cfg.seed,
        logging_steps=cfg.logging_steps,
        reward_log_path=reward_log,
    )

    # Patch max_steps support into trainer
    original_train = trainer.train

    def train_with_max_steps():
        """Wrap training with max_steps limit."""
        import functools

        old_step = trainer.__class__._grpo_loss

        step_counter = [0]
        max_steps = cfg.max_steps

        # Monkey-patch to count steps
        checkpoint_path = str(output_dir)
        torch.manual_seed(cfg.seed)

        optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr)
        from torch.optim.lr_scheduler import CosineAnnealingLR
        import numpy as np
        scheduler = CosineAnnealingLR(optimizer, T_max=max_steps)

        global_step = 0
        model.train()

        indices = list(range(len(rlef_ds)))
        rng = np.random.default_rng(cfg.seed)
        rng.shuffle(indices)

        accum_loss = 0.0
        optimizer.zero_grad()

        for batch_start in range(0, len(indices), cfg.batch_size):
            if global_step >= max_steps:
                break

            batch_indices = indices[batch_start:batch_start + cfg.batch_size]

            for idx in batch_indices:
                sample = rlef_ds[idx]
                prompt = sample["prompt"]
                meta_item = {"test_cases": sample.get("test_cases", "[]")}

                enc = tokenizer(
                    prompt,
                    return_tensors="pt",
                    max_length=cfg.max_length,
                    truncation=True,
                ).to(trainer.device)
                prompt_ids = enc["input_ids"]

                completions = trainer._generate_completions(enc, cfg.num_generations)
                meta = [meta_item] * cfg.num_generations

                rewards = monitored_binary_reward_fn(
                    completions=completions,
                    prompts=[prompt] * cfg.num_generations,
                    metadata=meta,
                )

                loss = trainer._grpo_loss(prompt_ids, completions, rewards, meta)
                (loss / cfg.grad_accum).backward()
                accum_loss += loss.item()

            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            global_step += 1

            if global_step % cfg.logging_steps == 0:
                print(f"  Step {global_step}/{max_steps}: loss={accum_loss:.4f}, "
                      f"mean_binary={sum(binary_reward_log[-cfg.num_generations:]) / max(1, cfg.num_generations):.3f}")

                # Mechanism activation check
                if len(fraction_reward_log) >= cfg.verify_interval_steps:
                    activated, indicators = verify_reward_formulation_active(
                        fraction_reward_log[-100:],
                        binary_reward_log[-100:],
                    )
                    record = {
                        "step": global_step,
                        "loss": accum_loss,
                        "mechanism_activated": activated,
                        **indicators,
                    }
                    with open(reward_log, "a") as f:
                        f.write(json.dumps(record) + "\n")

                accum_loss = 0.0

        # Save checkpoint
        model.save_pretrained(checkpoint_path)
        tokenizer.save_pretrained(checkpoint_path)
        print(f"✓ RLEF-Binary saved: {checkpoint_path} (steps={global_step})")
        return checkpoint_path, fraction_reward_log, binary_reward_log

    return train_with_max_steps()


if __name__ == "__main__":
    cfg = H_M3_Config()
    checkpoint_path, frac_log, bin_log = train_rlef_binary(cfg)
    print(f"Training complete: {checkpoint_path}")
    print(f"Mean fraction reward (last 50): {sum(frac_log[-50:]) / max(1, len(frac_log[-50:])):.4f}")
    print(f"Mean binary reward  (last 50): {sum(bin_log[-50:]) / max(1, len(bin_log[-50:])):.4f}")
