"""Compression wrappers: H2O eviction and quantization."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from config import MODEL_ID


def apply_quantization(model_id: str, quant: str | None):
    """Load model with optional quantization."""
    if quant == "int8":
        bnb_config = BitsAndBytesConfig(load_in_8bit=True)
    elif quant == "int4":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
        )
    else:
        bnb_config = None

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
        quantization_config=bnb_config,
        trust_remote_code=True,
    )
    return model


class H2OCache:
    """Heavy-Hitter Oracle KV cache eviction."""

    def __init__(self, retention: float = 0.8):
        self.retention = retention
        self.heavy_ratio = 0.5
        self.recent_ratio = 0.5
        self.accum_scores = {}

    def evict(self, past_key_values, attention_weights, layer_idx: int):
        """Evict KV entries based on heavy-hitter + recent window."""
        if past_key_values is None:
            return past_key_values

        keys, values = past_key_values[layer_idx]
        seq_len = keys.shape[2]
        budget = int(seq_len * self.retention)

        if seq_len <= budget:
            return past_key_values

        n_heavy = int(budget * self.heavy_ratio)
        n_recent = budget - n_heavy

        if layer_idx not in self.accum_scores:
            self.accum_scores[layer_idx] = torch.zeros(seq_len, device=keys.device)

        if attention_weights is not None:
            scores = attention_weights.sum(dim=(0, 1, 2))
            if len(scores) > len(self.accum_scores[layer_idx]):
                new_scores = torch.zeros(len(scores), device=keys.device)
                new_scores[:len(self.accum_scores[layer_idx])] = self.accum_scores[layer_idx]
                self.accum_scores[layer_idx] = new_scores
            self.accum_scores[layer_idx][:len(scores)] += scores

        scores = self.accum_scores[layer_idx][:seq_len - n_recent]
        heavy_idx = scores.topk(min(n_heavy, len(scores))).indices
        recent_idx = torch.arange(seq_len - n_recent, seq_len, device=keys.device)
        keep_idx = torch.cat([heavy_idx, recent_idx]).sort().values

        new_keys = keys[:, :, keep_idx, :]
        new_values = values[:, :, keep_idx, :]

        new_past = list(past_key_values)
        new_past[layer_idx] = (new_keys, new_values)
        return tuple(new_past)


def build_model_for_config(config: dict):
    """Build model with specified compression config."""
    model = apply_quantization(MODEL_ID, config.get("quantization"))
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    h2o_cache = None
    if config.get("method") == "h2o":
        h2o_cache = H2OCache(retention=config.get("retention", 0.8))

    return model, tokenizer, h2o_cache
