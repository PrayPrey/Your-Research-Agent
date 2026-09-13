"""Model loading and PPO trainer setup using PPOv2."""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from trl import PPOv2Config, PPOv2Trainer, AutoModelForCausalLMWithValueHead
from datasets import Dataset

from config import ExperimentConfig


def load_model_and_tokenizer(cfg: ExperimentConfig):
    dtype = torch.bfloat16 if cfg.torch_dtype == "bfloat16" else torch.float32

    model = AutoModelForCausalLMWithValueHead.from_pretrained(
        cfg.model_id,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=True
    )

    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    return model, tokenizer


def build_ppo_config(cfg: ExperimentConfig) -> PPOv2Config:
    return PPOv2Config(
        learning_rate=cfg.learning_rate,
        per_device_train_batch_size=cfg.batch_size,
        num_ppo_epochs=cfg.ppo_epochs,
        init_kl_coef=cfg.init_kl_coef,
        output_dir=cfg.checkpoint_dir,
        log_with=None,
    )
