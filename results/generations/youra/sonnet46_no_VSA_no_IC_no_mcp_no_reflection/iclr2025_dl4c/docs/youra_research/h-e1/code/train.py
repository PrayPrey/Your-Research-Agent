import argparse
import csv
import math
import os
import sys
import torch
import numpy as np
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainerCallback,
    TrainerState,
    TrainerControl,
    TrainingArguments,
)
from trl import GRPOTrainer, GRPOConfig as TRLGRPOConfig

# Add code dir to path for sibling imports
sys.path.insert(0, os.path.dirname(__file__))
from config import GRPOConfig, load_config, save_config
from data import build_dataset
from rewards import make_reward_fn


class GradNormCallback(TrainerCallback):
    def __init__(self, output_csv: str) -> None:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True) if os.path.dirname(output_csv) else None
        self._file = open(output_csv, "w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow(["global_step", "grad_norm", "mean_reward", "std_reward"])
        self._file.flush()

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        logs: dict = None,
        **kwargs,
    ) -> None:
        if logs is None:
            return
        grad_norm = logs.get("grad_norm", float("nan"))
        # reward mean/std from trl log keys: rewards/<fn_name>/mean, rewards/<fn_name>/std
        mean_r = float("nan")
        std_r = float("nan")
        for key, val in logs.items():
            if key.startswith("rewards/") and key.endswith("/mean"):
                mean_r = float(val)
            if key.startswith("rewards/") and key.endswith("/std"):
                std_r = float(val)
        if "reward" in logs and math.isnan(mean_r):
            mean_r = float(logs["reward"])
        if "reward_std" in logs and math.isnan(std_r):
            std_r = float(logs["reward_std"])

        step = state.global_step
        self._writer.writerow([step, grad_norm, mean_r, std_r])
        self._file.flush()

    def __del__(self):
        try:
            self._file.close()
        except Exception:
            pass


def build_trainer(
    cfg: GRPOConfig,
    condition: str,
    model,
    tokenizer,
    dataset,
) -> GRPOTrainer:
    """condition: 'binary' | 'ratio'. Wires reward_fn, GradNormCallback, checkpoint saving."""
    output_csv = os.path.join(cfg.output_dir, f"gradient_norms_{condition}.csv")
    checkpoint_dir = os.path.join(cfg.output_dir, "checkpoints", condition)

    trl_cfg = TRLGRPOConfig(
        num_train_epochs=1,
        max_steps=cfg.train_steps,
        per_device_train_batch_size=1,
        gradient_checkpointing=True,
        num_generations=cfg.group_size,
        generation_batch_size=cfg.group_size,  # must be divisible by num_generations
        generation_kwargs={"max_new_tokens": cfg.max_new_tokens},
        temperature=cfg.temperature,
        learning_rate=cfg.learning_rate,
        weight_decay=0.01,
        warmup_steps=cfg.warmup_steps,
        epsilon=cfg.clip_ratio,
        beta=cfg.kl_beta,
        save_steps=cfg.checkpoint_step,
        output_dir=checkpoint_dir,
        seed=cfg.seed,
        logging_steps=1,
        report_to="none",
        dataloader_num_workers=0,
    )

    reward_fn = make_reward_fn(condition)
    callback = GradNormCallback(output_csv)

    trainer = GRPOTrainer(
        model=model,
        args=trl_cfg,
        processing_class=tokenizer,
        train_dataset=dataset,
        reward_funcs=[reward_fn],
        callbacks=[callback],
    )
    return trainer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=["binary", "ratio"], required=True)
    parser.add_argument("--config", default=None, help="Path to config YAML")
    parser.add_argument("--steps", type=int, default=None, help="Override train_steps")
    args = parser.parse_args()

    cfg = load_config(args.config)
    cfg.reward_mode = args.condition
    if args.steps is not None:
        cfg.train_steps = args.steps

    os.makedirs(cfg.output_dir, exist_ok=True)
    save_config(cfg, os.path.join("configs", f"experiment_config_{args.condition}.yaml"))

    torch.manual_seed(cfg.seed)
    np.random.seed(cfg.seed)

    dtype = torch.bfloat16 if cfg.dtype == "bfloat16" else torch.float32

    print(f"Loading tokenizer: {cfg.model_name}")
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading model: {cfg.model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_name,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=True,
    )

    print("Building dataset...")
    dataset = build_dataset(cfg, tokenizer)
    print(f"Dataset size: {len(dataset)}")

    print(f"Building trainer (condition={args.condition})...")
    trainer = build_trainer(cfg, args.condition, model, tokenizer, dataset)

    print(f"Starting training: {cfg.train_steps} steps, condition={args.condition}")
    trainer.train()
    print(f"Training complete. Condition={args.condition}")


if __name__ == "__main__":
    main()
