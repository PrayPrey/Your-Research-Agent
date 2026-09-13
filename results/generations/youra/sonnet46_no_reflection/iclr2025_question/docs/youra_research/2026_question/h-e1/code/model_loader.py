import logging
from typing import Any, Tuple

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    BitsAndBytesConfig,
)

from config import ModelConfig

logger = logging.getLogger(__name__)


def load_llama_8b(cfg: ModelConfig) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load Llama-3-8B in bfloat16 with device_map=auto."""
    logger.info(f"Loading {cfg.hf_id} in bfloat16...")
    tokenizer = AutoTokenizer.from_pretrained(cfg.hf_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        cfg.hf_id,
        torch_dtype=torch.bfloat16,
        device_map=cfg.device_map,
    )
    model.eval()
    logger.info(f"Loaded {cfg.hf_id}")
    return model, tokenizer


def load_llama_70b(cfg: ModelConfig) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load Llama-3-70B with 8-bit bitsandbytes quantization."""
    logger.info(f"Loading {cfg.hf_id} with {cfg.quantization}-bit quantization...")
    tokenizer = AutoTokenizer.from_pretrained(cfg.hf_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if cfg.quantization == "8bit":
        bnb_config = BitsAndBytesConfig(load_in_8bit=True)
    elif cfg.quantization == "4bit":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_quant_type="nf4",
        )
    else:
        bnb_config = None

    model = AutoModelForCausalLM.from_pretrained(
        cfg.hf_id,
        quantization_config=bnb_config,
        device_map=cfg.device_map,
    )
    model.eval()
    logger.info(f"Loaded {cfg.hf_id}")
    return model, tokenizer


def load_deberta_nli() -> Tuple[AutoModelForSequenceClassification, AutoTokenizer]:
    """Load DeBERTa-large-mnli for NLI-based entailment scoring."""
    hf_id = "microsoft/deberta-large-mnli"
    logger.info(f"Loading {hf_id}...")
    tokenizer = AutoTokenizer.from_pretrained(hf_id)
    model = AutoModelForSequenceClassification.from_pretrained(hf_id)
    model.eval()
    if torch.cuda.is_available():
        model = model.cuda()
    logger.info(f"Loaded {hf_id}")
    return model, tokenizer


def get_model(model_key: str, cfg: ModelConfig) -> Tuple[Any, Any]:
    """Dispatcher: returns (model, tokenizer) for given model_key."""
    if model_key == "small":
        return load_llama_8b(cfg)
    elif model_key == "large":
        return load_llama_70b(cfg)
    elif model_key == "entailment":
        return load_deberta_nli()
    else:
        raise ValueError(f"Unknown model_key: {model_key}")
