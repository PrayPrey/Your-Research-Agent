"""Pythia model loading with LoRA adapter application."""
import torch
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, PreTrainedModel
from peft import LoraConfig, get_peft_model, TaskType, PeftModel

from config import MODEL_HF_IDS


def load_base_model(model_id: str, device_map: str = "auto") -> PreTrainedModel:
    """Load Pythia model for QA with fp16 and gradient checkpointing."""
    hf_id = MODEL_HF_IDS.get(model_id, model_id)
    model = AutoModelForQuestionAnswering.from_pretrained(
        hf_id,
        torch_dtype=torch.float16,
        device_map=device_map,
        trust_remote_code=True,
    )
    model.gradient_checkpointing_enable()
    return model


def load_tokenizer(model_id: str) -> AutoTokenizer:
    """Load tokenizer for Pythia model."""
    hf_id = MODEL_HF_IDS.get(model_id, model_id)
    tokenizer = AutoTokenizer.from_pretrained(hf_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def apply_lora(
    model: PreTrainedModel,
    rank: int,
    alpha: int | None = None,
    dropout: float = 0.05,
    target_modules: list[str] | None = None,
) -> PeftModel:
    """Apply LoRA adapter to model with rsLoRA scaling (alpha = 2*rank)."""
    if alpha is None:
        alpha = 2 * rank
    if target_modules is None:
        target_modules = ["query_key_value"]

    lora_config = LoraConfig(
        r=rank,
        lora_alpha=alpha,
        target_modules=target_modules,
        lora_dropout=dropout,
        bias="none",
        task_type=TaskType.QUESTION_ANS,
    )
    return get_peft_model(model, lora_config)
