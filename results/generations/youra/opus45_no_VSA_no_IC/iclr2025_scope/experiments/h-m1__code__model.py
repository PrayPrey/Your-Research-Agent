"""Pythia model loading and LoRA adapter creation."""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from config import MODEL_HF_IDS, ModelLoadConfig, TrainConfig


def load_base_model(size: str, cfg: ModelLoadConfig = None) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
    cfg = cfg or ModelLoadConfig()
    model_id = MODEL_HF_IDS[size]
    dtype = torch.float16 if cfg.torch_dtype == "float16" else torch.float32

    tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=cfg.cache_dir)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map=cfg.device_map,
        cache_dir=cfg.cache_dir,
        trust_remote_code=cfg.trust_remote_code,
        attn_implementation="eager",
    )
    return model, tokenizer


def create_lora_model(base_model: PreTrainedModel, rank: int, train_cfg: TrainConfig = None) -> PeftModel:
    train_cfg = train_cfg or TrainConfig()
    config = LoraConfig(
        r=rank,
        lora_alpha=rank * train_cfg.lora_alpha_multiplier,
        target_modules=train_cfg.lora_target_modules,
        lora_dropout=train_cfg.lora_dropout,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    return get_peft_model(base_model, config)
