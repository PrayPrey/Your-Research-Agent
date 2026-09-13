"""train_rlef.py — E-4: RLEF-Fraction training with GRPO for H-E1

Uses custom SimpleGRPOTrainer (grpo_trainer.py) since TRL>=1.0 requires PyTorch>=2.6.
"""
import json
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainerCallback, TrainerControl, TrainerState

from data_utils import load_apps_train
from grpo_trainer import SimpleGRPOTrainer
from reward import fraction_reward_fn


class RewardMonitorCallback(TrainerCallback):
    """Log per-step fraction rewards by APPS difficulty to JSONL."""

    def __init__(self, log_path: str = "logs/reward_monitoring.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def on_step_end(
        self,
        args,
        state: TrainerState,
        control: TrainerControl,
        rewards=None,
        metadata=None,
        **kwargs,
    ) -> None:
        if rewards is None or metadata is None:
            return
        buckets = {"intro": [], "interview": [], "competition": []}
        for r, meta in zip(rewards, metadata):
            if isinstance(meta, dict):
                difficulty = meta.get("difficulty", "interview")
            else:
                difficulty = "interview"
            if difficulty in buckets:
                buckets[difficulty].append(float(r))

        def _mean(lst):
            return sum(lst) / len(lst) if lst else None

        record = {
            "step": state.global_step,
            "intro_reward": _mean(buckets["intro"]),
            "interview_reward": _mean(buckets["interview"]),
            "competition_reward": _mean(buckets["competition"]),
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record) + "\n")


def compute_gradient_steps(dataset_size: int, batch_size: int, grad_accum: int, epochs: int) -> int:
    """Total optimizer steps = floor(dataset_size / (batch_size * grad_accum)) * epochs."""
    return (dataset_size // (batch_size * grad_accum)) * epochs


def verify_matched_steps(sft_steps: int, rlef_steps: int) -> None:
    """Assert SFT and RLEF steps match within 5%."""
    if sft_steps == 0:
        return
    pct = abs(sft_steps - rlef_steps) / sft_steps
    if pct > 0.05:
        raise ValueError(f"Step mismatch too large: SFT={sft_steps}, RLEF={rlef_steps} ({pct:.1%})")
    if pct > 0:
        print(f"⚠ Step mismatch {abs(sft_steps-rlef_steps)} steps ({pct:.1%}) — acceptable for PoC")


def train(config: dict) -> str:
    """Run GRPO training with fraction_reward_fn. Returns checkpoint path."""
    Path("logs").mkdir(parents=True, exist_ok=True)
    Path(config["paths"]["checkpoints_dir"]).mkdir(parents=True, exist_ok=True)
    rlef_dir = f"{config['paths']['checkpoints_dir']}/rlef_fraction"
    Path(rlef_dir).mkdir(parents=True, exist_ok=True)

    model_name = config["model_name"]
    print(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading model: {model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True,
    )
    ref_model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True,
    )

    # Load data
    print("Loading APPS dataset for RLEF...")
    rlef_dataset = load_apps_train(tokenizer)["rlef"]
    print(f"RLEF dataset size: {len(rlef_dataset)}")

    # Read SFT steps from config_dump if available
    sft_steps = None
    try:
        with open("logs/config_dump.json") as f:
            dump = json.load(f)
        sft_steps = dump.get("gradient_steps")
    except Exception:
        pass

    rlef_steps = compute_gradient_steps(
        len(rlef_dataset),
        config["training"]["batch_size"],
        config["training"]["grad_accum"],
        config["training"]["epochs"],
    )
    if sft_steps is not None:
        verify_matched_steps(sft_steps, rlef_steps)
    print(f"RLEF gradient steps: {rlef_steps}")

    trainer = SimpleGRPOTrainer(
        model=model,
        ref_model=ref_model,
        tokenizer=tokenizer,
        reward_fn=fraction_reward_fn,
        dataset=rlef_dataset,
        output_dir=rlef_dir,
        lr=config["training"]["lr"],
        batch_size=config["training"]["batch_size"],
        grad_accum=config["training"]["grad_accum"],
        num_epochs=config["training"]["epochs"],
        G=config["grpo"]["num_generations"],
        beta=config["grpo"]["beta"],
        max_new_tokens=config["training"]["max_new_tokens"],
        temperature=config["grpo"]["temperature_rollout"],
        max_grad_norm=config["training"]["grad_clip"],
        seed=config["training"]["seed"],
        reward_log_path=config["logging"]["reward_monitoring"],
    )
    print("Starting RLEF-Fraction (GRPO) training...")
    trainer.train()
    print(f"✓ RLEF checkpoint saved: {rlef_dir}")
    return rlef_dir


if __name__ == "__main__":
    import yaml
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    train(cfg)
