"""H-M1 PPO Training: Combined reward optimization."""
import os
import json
import math
from datetime import datetime
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import PPOTrainer, PPOConfig as TRLPPOConfig
from trl.core import LengthSampler

from config import ExperimentConfig
from data import load_ultrafeedback, load_ifeval_split, sample_ppo_batch
from rewards import CombinedRewardModel


class TrainingDivergenceError(Exception):
    """Raised when KL divergence exceeds safety threshold."""
    pass


def build_ppo_trainer(cfg: ExperimentConfig):
    """Build PPO trainer with policy and reference models."""
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(cfg.model.base_model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    # Load policy model
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model.base_model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )

    # TRL PPO config
    ppo_config = TRLPPOConfig(
        learning_rate=cfg.ppo.learning_rate,
        batch_size=cfg.ppo.batch_size,
        mini_batch_size=cfg.ppo.mini_batch_size,
        gradient_accumulation_steps=cfg.ppo.gradient_accumulation_steps,
        ppo_epochs=cfg.ppo.ppo_epochs,
        init_kl_coef=cfg.ppo.kl_coeff,
        cliprange=cfg.ppo.clip_range,
        cliprange_value=cfg.ppo.value_clip_range,
        seed=cfg.ppo.seed,
        log_with=None,  # manual logging
    )

    trainer = PPOTrainer(
        config=ppo_config,
        model=model,
        tokenizer=tokenizer,
    )

    return trainer, tokenizer


def run_training(cfg: ExperimentConfig, output_dir: Path):
    """Main PPO training loop."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir = output_dir / "checkpoints"
    ckpt_dir.mkdir(exist_ok=True)

    # Load data
    print("Loading datasets...")
    uf_ds = load_ultrafeedback(max_samples=10000)  # subset for PoC
    ifeval_train, ifeval_test = load_ifeval_split()
    print(f"UltraFeedback: {len(uf_ds)}, IFEval train: {len(ifeval_train)}, test: {len(ifeval_test)}")

    # Build trainer
    print("Building PPO trainer...")
    trainer, tokenizer = build_ppo_trainer(cfg)

    # Build reward model
    print("Loading reward model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    reward_model = CombinedRewardModel(
        helpfulness_model_id=cfg.model.reward_model_id,
        alpha=cfg.reward.alpha,
        beta=cfg.reward.beta,
        ifeval_soft_margin=cfg.reward.ifeval_soft_margin,
        device=device,
    )

    # Training history
    history = []
    generation_kwargs = {
        "max_new_tokens": cfg.data.max_new_tokens,
        "do_sample": True,
        "temperature": 0.7,
        "pad_token_id": tokenizer.pad_token_id,
    }

    print(f"Starting PPO training for {cfg.ppo.total_steps} steps...")
    print(f"Alpha={cfg.reward.alpha}, Beta={cfg.reward.beta}")

    for step in range(cfg.ppo.total_steps):
        # Sample batch
        prompts, constraints = sample_ppo_batch(
            uf_ds, ifeval_train,
            batch_size=cfg.ppo.batch_size,
            seed=cfg.ppo.seed + step
        )

        # Tokenize queries
        query_tensors = []
        for p in prompts:
            tokens = tokenizer.encode(p, return_tensors="pt", truncation=True,
                                      max_length=cfg.data.max_prompt_length)[0]
            query_tensors.append(tokens.to(trainer.model.device))

        # Generate responses
        response_tensors = trainer.generate(
            query_tensors,
            return_prompt=False,
            **generation_kwargs
        )

        # Decode responses
        responses = [tokenizer.decode(r, skip_special_tokens=True) for r in response_tensors]

        # Compute rewards
        rewards = reward_model.compute_reward(prompts, responses, constraints)

        # PPO step
        stats = trainer.step(query_tensors, response_tensors, rewards)

        # Check stability
        policy_loss = stats.get("ppo/loss/policy", stats.get("ppo/policy_loss", 0))
        kl = stats.get("objective/kl", stats.get("ppo/mean_kl", 0))

        if math.isnan(policy_loss) or math.isinf(policy_loss):
            raise TrainingDivergenceError(f"NaN/Inf loss at step {step}")

        if kl > 10.0:
            raise TrainingDivergenceError(f"KL divergence {kl:.2f} > 10.0 at step {step}")

        # Log metrics
        if step % cfg.logging.log_interval == 0:
            log_entry = {
                "step": step,
                "reward/mean": sum(r.item() for r in rewards) / len(rewards),
                "reward/helpfulness": reward_model.last_helpfulness,
                "reward/controllability": reward_model.last_ifeval,
                "objective/kl": kl,
                "ppo/policy_loss": policy_loss,
                "ppo/value_loss": stats.get("ppo/loss/value", stats.get("ppo/value_loss", 0)),
            }
            history.append(log_entry)
            print(f"Step {step}: R={log_entry['reward/mean']:.3f} "
                  f"(H={log_entry['reward/helpfulness']:.3f}, I={log_entry['reward/controllability']:.3f}) "
                  f"KL={kl:.3f}")

        # Checkpoint
        if step > 0 and step % cfg.logging.checkpoint_interval == 0:
            ckpt_path = ckpt_dir / f"step_{step}"
            trainer.save_pretrained(str(ckpt_path))
            print(f"Checkpoint saved: {ckpt_path}")

    # Final checkpoint
    final_ckpt = ckpt_dir / f"step_{cfg.ppo.total_steps}"
    trainer.save_pretrained(str(final_ckpt))

    # Save history
    history_path = output_dir / "training_history.json"
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

    print(f"Training complete. History saved to {history_path}")
    return history, ifeval_test


if __name__ == "__main__":
    cfg = ExperimentConfig()
    output_dir = Path(__file__).parent / "outputs"
    run_training(cfg, output_dir)
