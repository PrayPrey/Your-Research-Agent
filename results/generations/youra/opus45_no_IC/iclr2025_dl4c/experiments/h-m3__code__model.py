"""Model loading and PPO trainer setup."""

import torch
from typing import Tuple, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import PPOConfig, PPOTrainer, AutoModelForCausalLMWithValueHead


def load_policy_model(
    model_id: str = "meta-llama/CodeLlama-7b-Instruct-hf",
    torch_dtype: str = "float16"
) -> Tuple:
    """
    Load policy model and tokenizer.

    Args:
        model_id: HuggingFace model identifier
        torch_dtype: Data type for model weights

    Returns:
        (model, tokenizer) tuple
    """
    dtype = torch.float16 if torch_dtype == "float16" else torch.float32

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLMWithValueHead.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=True,
    )

    return model, tokenizer


def build_ppo_config(
    lr: float = 3e-6,
    batch_size: int = 64,
    mini_batch_size: int = 16,
    gradient_accumulation_steps: int = 4,
    ppo_epochs: int = 4,
    seed: int = 1,
    log_dir: str = "logs",
) -> PPOConfig:
    """Build PPO training configuration."""
    return PPOConfig(
        learning_rate=lr,
        batch_size=batch_size,
        mini_batch_size=mini_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        ppo_epochs=ppo_epochs,
        seed=seed,
        log_with="tensorboard",
        project_kwargs={"logging_dir": log_dir},
    )


def build_ppo_trainer(
    model,
    tokenizer,
    ppo_config: Optional[PPOConfig] = None,
    ref_model = None,
) -> PPOTrainer:
    """
    Build PPO trainer instance.

    Args:
        model: Policy model with value head
        tokenizer: Tokenizer
        ppo_config: PPO configuration
        ref_model: Reference model (optional, defaults to copy of model)

    Returns:
        PPOTrainer instance
    """
    if ppo_config is None:
        ppo_config = build_ppo_config()

    trainer = PPOTrainer(
        config=ppo_config,
        model=model,
        ref_model=ref_model,
        tokenizer=tokenizer,
    )

    return trainer
