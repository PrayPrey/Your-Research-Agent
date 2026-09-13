"""H-M2 Train Variants: Orchestrate 7 training runs (B1-B3, T1-T4)."""
import json
from pathlib import Path
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import PPOTrainer, PPOConfig as TRLPPOConfig

from config import ModelVariant, VARIANTS, build_config
from data import load_ultrafeedback, load_ifeval_split, sample_ppo_batch
from rewards import CombinedRewardModel, HelpfulnessRewardModel
from ifeval_signal import IFEvalRewardSignal


def build_reward_model(variant: ModelVariant, cfg, device: str) -> Optional[CombinedRewardModel]:
    """Build reward model per variant reward_mode."""
    if variant.reward_mode == "none":
        return None  # B1: SFT-only, no PPO

    if variant.reward_mode == "quality_only":
        # B3: use alpha=1.0 for helpfulness (UltraFeedback preference), beta=0.0
        return CombinedRewardModel(
            helpfulness_model_id=cfg.model.reward_model_id,
            alpha=1.0,
            beta=0.0,
            ifeval_soft_margin=cfg.reward.ifeval_soft_margin,
            device=device,
        )

    # helpfulness_only (B2) or combined (T1-T4)
    return CombinedRewardModel(
        helpfulness_model_id=cfg.model.reward_model_id,
        alpha=variant.alpha,
        beta=variant.beta,
        ifeval_soft_margin=cfg.reward.ifeval_soft_margin,
        device=device,
    )


def run_variant(
    variant: ModelVariant,
    ifeval_train,
    uf_data,
    output_dir: Path,
    max_steps: int = 100
) -> dict:
    """Train or load variant. Returns checkpoint path and history."""
    cfg = build_config(variant)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    variant_dir = output_dir / variant.name
    variant_dir.mkdir(parents=True, exist_ok=True)

    if not variant.train:
        # B1: SFT-only, just record base model path
        return {
            "variant": variant.name,
            "history": [],
            "checkpoint": cfg.model.base_model_id,
        }

    # Build tokenizer
    tokenizer = AutoTokenizer.from_pretrained(cfg.model.base_model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    # Load model
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
        log_with=None,
    )

    trainer = PPOTrainer(config=ppo_config, model=model, tokenizer=tokenizer)
    reward_model = build_reward_model(variant, cfg, device)

    history = []
    generation_kwargs = {
        "max_new_tokens": cfg.data.max_new_tokens,
        "do_sample": True,
        "temperature": 0.7,
        "pad_token_id": tokenizer.pad_token_id,
    }

    print(f"[{variant.name}] Training α={variant.alpha}, β={variant.beta}, mode={variant.reward_mode}")

    for step in range(max_steps):
        prompts, constraints = sample_ppo_batch(
            uf_data, ifeval_train,
            batch_size=cfg.ppo.batch_size,
            seed=cfg.ppo.seed + step
        )

        query_tensors = []
        for p in prompts:
            tokens = tokenizer.encode(p, return_tensors="pt", truncation=True,
                                      max_length=cfg.data.max_prompt_length)[0]
            query_tensors.append(tokens.to(trainer.model.device))

        response_tensors = trainer.generate(query_tensors, return_prompt=False, **generation_kwargs)
        responses = [tokenizer.decode(r, skip_special_tokens=True) for r in response_tensors]
        rewards = reward_model.compute_reward(prompts, responses, constraints)
        stats = trainer.step(query_tensors, response_tensors, rewards)

        if step % 10 == 0:
            kl = stats.get("objective/kl", stats.get("ppo/mean_kl", 0))
            reward_mean = sum(r.item() for r in rewards) / len(rewards)
            print(f"[{variant.name}] Step {step}: R={reward_mean:.3f}, KL={kl:.3f}")
            history.append({"step": step, "reward": reward_mean, "kl": kl})

    # Save checkpoint
    ckpt_path = variant_dir / "final"
    trainer.save_pretrained(str(ckpt_path))

    # Save history
    with open(variant_dir / "history.json", "w") as f:
        json.dump(history, f)

    return {
        "variant": variant.name,
        "history": history,
        "checkpoint": str(ckpt_path),
    }


def run_all(
    variants: list[ModelVariant],
    output_dir: Path,
    max_steps: int = 100
) -> dict[str, dict]:
    """Sequential execution of all variants with failure isolation."""
    uf_data = load_ultrafeedback(max_samples=5000)
    ifeval_train, _ = load_ifeval_split(seed=1)  # NFR-2: seed=1

    results = {}
    for variant in variants:
        try:
            result = run_variant(variant, ifeval_train, uf_data, output_dir, max_steps)
            results[variant.name] = result
        except Exception as e:
            print(f"[{variant.name}] FAILED: {e}")
            results[variant.name] = {"variant": variant.name, "error": str(e)}

    return results


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "outputs"
    results = run_all(VARIANTS, output_dir, max_steps=100)
    print(json.dumps({k: {"checkpoint": v.get("checkpoint"), "error": v.get("error")}
                      for k, v in results.items()}, indent=2))
