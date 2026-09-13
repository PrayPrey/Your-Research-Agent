"""
A-5/A-6: 1.3B SFT + RLEF-Fraction training.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

from config import H_M4_Config, H_E1_CODE, BENCHMARK_ORDER

# sys.path injection for h-e1 code
if str(H_E1_CODE) not in sys.path:
    sys.path.insert(0, str(H_E1_CODE))


# ---------------------------------------------------------------------------
# RewardMonitorCallback
# ---------------------------------------------------------------------------

class RewardMonitorCallback:
    def __init__(self, log_dir: str, interval: int = 50):
        os.makedirs(log_dir, exist_ok=True)
        self.log_path = f"{log_dir}/reward_monitoring.jsonl"
        self.interval = interval

    def on_step_end(self, step: int, rewards=None, **kwargs):
        if step % self.interval != 0 or rewards is None:
            return
        activated, stats = verify_fraction_reward_active(rewards)
        record = {"step": step, **stats}
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record) + "\n")
        if not activated:
            print(f"WARNING [Step {step}]: fraction reward not activated "
                  f"(mean={stats['mean_reward']:.4f}, nonzero={stats['nonzero_fraction']:.3f})")


def verify_fraction_reward_active(rewards: list, threshold: float = 0.01) -> tuple:
    arr = np.array(rewards, dtype=float)
    mean_reward = float(arr.mean()) if len(arr) > 0 else 0.0
    nonzero_fraction = float((arr > 0).mean()) if len(arr) > 0 else 0.0
    activated = mean_reward > threshold and nonzero_fraction > 0.05
    stats = {
        "mean_reward": mean_reward,
        "nonzero_fraction": nonzero_fraction,
        "max_reward": float(arr.max()) if len(arr) > 0 else 0.0,
        "activated": activated,
    }
    return activated, stats


# ---------------------------------------------------------------------------
# A-5: SFT 1.3B
# ---------------------------------------------------------------------------

def train_sft_1_3b(cfg: H_M4_Config) -> str:
    """SFT fine-tune DeepSeek-Coder-1.3B-base on APPS train split."""
    from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
    from datasets import load_dataset

    sft = cfg.sft_1b3
    torch.manual_seed(sft.seed)

    print(f"[SFT-1.3B] Loading model: {sft.model_name}")
    tokenizer = AutoTokenizer.from_pretrained(sft.model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        sft.model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

    print("[SFT-1.3B] Loading APPS dataset...")
    dataset = load_dataset("codeparrot/apps", split="train")

    def has_solution(example):
        try:
            sols = json.loads(example["solutions"])
            return len(sols) > 0 and len(sols[0].strip()) > 0
        except Exception:
            return False

    dataset = dataset.filter(has_solution)
    print(f"[SFT-1.3B] {len(dataset)} problems with solutions")

    def tokenize_fn(examples):
        texts = []
        for q, s_str in zip(examples["question"], examples["solutions"]):
            try:
                first_sol = json.loads(s_str)[0]
            except Exception:
                first_sol = ""
            texts.append(f"### Problem:\n{q}\n\n### Solution:\n{first_sol}")
        enc = tokenizer(texts, truncation=True, max_length=sft.max_length,
                        padding="max_length", return_tensors="pt")
        labels = enc["input_ids"].clone()
        labels[enc["attention_mask"] == 0] = -100
        enc["labels"] = labels
        return enc

    tokenized = dataset.map(tokenize_fn, batched=True, remove_columns=dataset.column_names,
                            num_proc=4)

    sft_dir = cfg.paths.sft_1_3b_dir
    os.makedirs(sft_dir, exist_ok=True)

    args = TrainingArguments(
        output_dir=sft_dir,
        num_train_epochs=sft.epochs,
        per_device_train_batch_size=sft.batch_size,
        gradient_accumulation_steps=sft.grad_accum,
        learning_rate=sft.lr,
        warmup_steps=100,
        lr_scheduler_type=sft.lr_schedule,
        bf16=True,
        save_strategy="steps",
        save_steps=500,
        seed=sft.seed,
        logging_steps=50,
        report_to="none",
        dataloader_num_workers=4,
    )
    trainer = Trainer(model=model, args=args, train_dataset=tokenized)
    trainer.train()

    final_dir = sft_dir + "/final"
    trainer.save_model(final_dir)
    print(f"[SFT-1.3B] Saved to {final_dir}")
    return final_dir


# ---------------------------------------------------------------------------
# A-6: RLEF-Fraction 1.3B
# ---------------------------------------------------------------------------

def train_rlef_1_3b(cfg: H_M4_Config, sft_checkpoint: str) -> str:
    """GRPO fine-tune 1.3B SFT checkpoint with fraction_reward_fn."""
    from trl import GRPOConfig as TRLGRPOConfig, GRPOTrainer
    from datasets import load_dataset
    from reward import fraction_reward_fn  # from h-e1/code

    sft = cfg.sft_1b3
    torch.manual_seed(sft.seed)

    print(f"[RLEF-1.3B] Loading APPS dataset for GRPO...")
    dataset = load_dataset("codeparrot/apps", split="train")

    def prepare_for_grpo(examples):
        prompts, metadatas = [], []
        for q, io_str in zip(examples["question"], examples["input_output"]):
            prompts.append(f"### Problem:\n{q}\n\n### Solution:\n")
            try:
                io = json.loads(io_str)
                test_cases = list(zip(io.get("inputs", []), io.get("outputs", [])))
                test_cases_json = json.dumps(test_cases)
            except Exception:
                test_cases_json = "[]"
            metadatas.append({"test_cases": test_cases_json})
        return {"prompt": prompts, "metadata": metadatas}

    grpo_dataset = dataset.map(prepare_for_grpo, batched=True,
                               remove_columns=dataset.column_names, num_proc=4)

    rlef_dir = cfg.paths.rlef_1_3b_dir
    os.makedirs(rlef_dir, exist_ok=True)
    os.makedirs(cfg.paths.logs_dir, exist_ok=True)

    training_args = TRLGRPOConfig(
        output_dir=rlef_dir,
        num_train_epochs=sft.epochs,
        per_device_train_batch_size=4,  # smaller for GRPO memory
        gradient_accumulation_steps=8,
        learning_rate=1e-5,
        warmup_steps=100,
        lr_scheduler_type=sft.lr_schedule,
        num_generations=sft.num_generations,
        max_completion_length=1024,
        bf16=True,
        seed=sft.seed,
        save_steps=500,
        logging_steps=50,
        report_to="none",
    )

    trainer = GRPOTrainer(
        model=sft_checkpoint,
        reward_funcs=[fraction_reward_fn],
        args=training_args,
        train_dataset=grpo_dataset,
    )

    monitor = RewardMonitorCallback(log_dir=cfg.paths.logs_dir, interval=50)
    trainer.add_callback(monitor)
    trainer.train()

    final_dir = rlef_dir + "/final"
    trainer.save_model(final_dir)
    print(f"[RLEF-1.3B] Saved to {final_dir}")
    return final_dir


# ---------------------------------------------------------------------------
# A-6-4: Checkpoint validation
# ---------------------------------------------------------------------------

def validate_rlef_checkpoint(checkpoint_path: str, min_mean_reward: float = 0.05,
                              reward_log_path: str = None) -> bool:
    if reward_log_path and Path(reward_log_path).exists():
        records = []
        with open(reward_log_path) as f:
            for line in f:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass
        if records:
            final_10 = records[-10:]
            mean_final = np.mean([r.get("mean_reward", 0.0) for r in final_10])
            print(f"[Checkpoint Validation] Final 10-step mean reward: {mean_final:.4f}")
            return mean_final > min_mean_reward

    checkpoint_dir = Path(checkpoint_path)
    exists = checkpoint_dir.exists() and any(checkpoint_dir.iterdir())
    print(f"[Checkpoint Validation] Directory check: {'PASS' if exists else 'FAIL'}")
    return exists
