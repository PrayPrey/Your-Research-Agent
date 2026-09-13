import csv
import math
import os
import sys
from typing import NamedTuple

import numpy as np
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainerCallback,
    TrainerState,
    TrainerControl,
    TrainingArguments,
)
from trl import GRPOTrainer, GRPOConfig as TRLGRPOConfig

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_H_E1_DIR = os.path.join(_THIS_DIR, "../../h-e1/code")

# h-m1 first (so HM1Config loads from here), h-e1 appended (so data/rewards/train load from there)
# h-m1/code/config.py exports GRPOConfig alias so h-e1 siblings resolve correctly
sys.path.insert(0, _THIS_DIR)
sys.path.append(_H_E1_DIR)

from config import HM1Config
from data import build_dataset
from rewards import make_reward_fn


class GradNormCallback(TrainerCallback):
    """Copy of h-e1 GradNormCallback (avoids circular import)."""

    def __init__(self, output_csv: str) -> None:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True) if os.path.dirname(output_csv) else None
        self._file = open(output_csv, "w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow(["global_step", "grad_norm", "mean_reward", "std_reward"])
        self._file.flush()

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is None:
            return
        grad_norm = logs.get("grad_norm", float("nan"))
        mean_r = float("nan")
        std_r = float("nan")
        for key, val in logs.items():
            if key.startswith("rewards/") and key.endswith("/mean"):
                mean_r = float(val)
            if key.startswith("rewards/") and key.endswith("/std"):
                std_r = float(val)
        if "reward" in logs and math.isnan(mean_r):
            mean_r = float(logs["reward"])
        self._writer.writerow([state.global_step, grad_norm, mean_r, std_r])
        self._file.flush()

    def __del__(self):
        try:
            self._file.close()
        except Exception:
            pass


class FractionPartialCallback(TrainerCallback):
    """Logs fraction of completions with reward in (0,1) — monitors ratio degeneracy."""

    def __init__(self, output_csv: str, alert_threshold: float = 0.05) -> None:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True) if os.path.dirname(output_csv) else None
        self._file = open(output_csv, "w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow(["global_step", "reward_mean", "reward_std", "fraction_partial", "grad_norm", "kl"])
        self._file.flush()
        self._alert_threshold = alert_threshold

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
        step = state.global_step
        grad_norm = logs.get("grad_norm", float("nan"))
        kl = logs.get("kl", float("nan"))

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
            std_r = float(logs.get("reward_std", float("nan")))

        rewards_list = logs.get("rewards", [])
        if rewards_list:
            partial = [r for r in rewards_list if 0.0 < float(r) < 1.0]
            fraction_partial = len(partial) / len(rewards_list)
        else:
            fraction_partial = float("nan")

        self._writer.writerow([step, mean_r, std_r, fraction_partial, grad_norm, kl])
        self._file.flush()

        if not math.isnan(fraction_partial) and fraction_partial < self._alert_threshold:
            print(f"⚠ Step {step}: fraction_partial={fraction_partial:.3f} < {self._alert_threshold} — ratio degeneracy?")

    def __del__(self):
        try:
            self._file.close()
        except Exception:
            pass


class TrainingResult(NamedTuple):
    condition: str
    checkpoint_paths: dict  # {step: checkpoint_dir_path}
    training_log_path: str
    final_step: int


def run_condition(
    condition: str,
    cfg: HM1Config,
    model_name: str,
) -> TrainingResult:
    """Train one reward condition (binary|ratio) for cfg.train_steps, saving at checkpoint_steps."""
    torch.manual_seed(cfg.seed)
    np.random.seed(cfg.seed)

    os.makedirs(cfg.output_dir, exist_ok=True)
    checkpoint_dir = os.path.join(cfg.output_dir, "checkpoints", condition)
    os.makedirs(checkpoint_dir, exist_ok=True)

    dtype = torch.bfloat16 if cfg.dtype == "bfloat16" else torch.float32

    print(f"[{condition}] Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"[{condition}] Loading model: {model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=True,
    )

    print(f"[{condition}] Building dataset...")
    dataset = build_dataset(cfg, tokenizer)

    grad_csv = os.path.join(cfg.output_dir, f"gradient_norms_{condition}.csv")
    frac_csv = os.path.join(cfg.output_dir, f"training_log_{condition}.csv")

    callbacks = [
        GradNormCallback(grad_csv),
        FractionPartialCallback(frac_csv, alert_threshold=cfg.fraction_partial_alert_threshold),
    ]

    # Use smallest checkpoint_step for TRL save_steps (we save at all checkpoint_steps)
    save_steps = min(cfg.checkpoint_steps)

    trl_cfg = TRLGRPOConfig(
        num_train_epochs=1,
        max_steps=cfg.train_steps,
        per_device_train_batch_size=1,
        gradient_checkpointing=True,
        num_generations=cfg.group_size,
        generation_batch_size=cfg.group_size,
        generation_kwargs={"max_new_tokens": cfg.max_new_tokens},
        temperature=cfg.temperature,
        learning_rate=cfg.learning_rate,
        weight_decay=0.01,
        warmup_steps=cfg.warmup_steps,
        epsilon=cfg.clip_ratio,
        beta=cfg.kl_beta,
        save_steps=save_steps,
        output_dir=checkpoint_dir,
        seed=cfg.seed,
        logging_steps=1,
        report_to="none",
        dataloader_num_workers=0,
    )

    reward_fn = make_reward_fn(condition)
    trainer = GRPOTrainer(
        model=model,
        args=trl_cfg,
        processing_class=tokenizer,
        train_dataset=dataset,
        reward_funcs=[reward_fn],
        callbacks=callbacks,
    )

    print(f"[{condition}] Training for {cfg.train_steps} steps...")
    trainer.train()
    print(f"[{condition}] Training complete.")

    # Collect checkpoint paths
    checkpoint_paths = {}
    for step in cfg.checkpoint_steps:
        path = os.path.join(checkpoint_dir, f"checkpoint-{step}")
        if os.path.exists(path):
            checkpoint_paths[step] = path
        else:
            print(f"⚠ Checkpoint at step {step} not found at {path}")

    return TrainingResult(
        condition=condition,
        checkpoint_paths=checkpoint_paths,
        training_log_path=frac_csv,
        final_step=cfg.train_steps,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=["binary", "ratio"], required=True)
    parser.add_argument("--config", default=None)
    parser.add_argument("--steps", type=int, default=None)
    args = parser.parse_args()

    sys.path.insert(0, os.path.dirname(__file__))
    from config import load_hm1_config

    cfg = load_hm1_config(args.config)
    if args.steps is not None:
        cfg.train_steps = args.steps
        cfg.checkpoint_steps = [s for s in cfg.checkpoint_steps if s <= args.steps]
        if not cfg.checkpoint_steps:
            cfg.checkpoint_steps = [args.steps]

    result = run_condition(args.condition, cfg, cfg.model_name)
    print(f"Done. Checkpoints: {result.checkpoint_paths}")
