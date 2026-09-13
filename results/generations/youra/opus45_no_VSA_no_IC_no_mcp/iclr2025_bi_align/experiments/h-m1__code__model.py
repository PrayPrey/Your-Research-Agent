"""Model setup for H-M1 reward model."""
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from peft import get_peft_model


def load_tokenizer(cfg):
    """Load tokenizer with proper pad token setup."""
    tokenizer = AutoTokenizer.from_pretrained(cfg.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    tokenizer.padding_side = "right"
    return tokenizer


def build_reward_model(cfg, use_lora: bool = True):
    """Build Llama-2-7B reward model with optional LoRA."""
    from config import get_peft_config

    use_bf16 = cfg.bf16 and torch.cuda.is_available()
    model = AutoModelForSequenceClassification.from_pretrained(
        cfg.base_model,
        num_labels=1,
        torch_dtype=torch.bfloat16 if use_bf16 else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    model.config.pad_token_id = model.config.eos_token_id

    if use_lora:
        peft_config = get_peft_config(cfg)
        model = get_peft_model(model, peft_config)
        model.print_trainable_parameters()

    if cfg.gradient_checkpointing:
        model.gradient_checkpointing_enable()

    return model


def get_reward(model, tokenizer, text: str, device: str) -> float:
    """Get scalar reward for a single text sequence."""
    model.eval()
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding="max_length",
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    return outputs.logits.squeeze().item()
