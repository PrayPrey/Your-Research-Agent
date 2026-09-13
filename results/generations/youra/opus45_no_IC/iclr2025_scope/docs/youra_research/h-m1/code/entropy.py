"""H-M1: Entropy computation - Attention extraction and Shannon entropy."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import ModelConfig, EntropyConfig, DataConfig
from data import tokenize_probe


def load_model(config: ModelConfig = None) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load Llama-2-7B with output_attentions=True."""
    if config is None:
        config = ModelConfig()

    print(f"Loading model: {config.model_name}")

    model = AutoModelForCausalLM.from_pretrained(
        config.model_name,
        torch_dtype=torch.float16 if config.torch_dtype == "float16" else torch.float32,
        device_map=config.device_map,
        output_attentions=config.output_attentions,
    )
    tokenizer = AutoTokenizer.from_pretrained(config.model_name)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Model loaded on {model.device}")
    return model, tokenizer


def compute_attention_entropy(attention_weights: torch.Tensor, eps: float = 1e-10) -> torch.Tensor:
    """
    Compute Shannon entropy for attention distribution.

    Args:
        attention_weights: [B, H, S, S] (already softmaxed)
        eps: numerical stability epsilon
    Returns:
        entropy: [B, H] - entropy per head, averaged over query positions
    """
    # Convert to fp32 for numerical stability (fp16 causes log underflow)
    p = attention_weights.float()
    # Clamp to avoid log(0)
    p = torch.clamp(p, min=eps, max=1.0)
    log_p = torch.log(p)
    # Entropy per query position: -sum over keys
    entropy_per_query = -(p * log_p).sum(dim=-1)  # [B, H, S]
    # Average over query positions
    entropy = entropy_per_query.mean(dim=-1)  # [B, H]
    return entropy


def extract_task_entropy(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    samples: list[str],
    n_tokens: int = 100,
    entropy_config: EntropyConfig = None,
) -> torch.Tensor:
    """
    Extract attention entropy for task samples.

    Returns: [n_samples, 32, 32] (n_samples, layers, heads)
    """
    if entropy_config is None:
        entropy_config = EntropyConfig()

    all_entropies = []

    for text in samples:
        inputs = tokenize_probe(text, tokenizer, n_tokens)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)

        # outputs.attentions is tuple of (batch, heads, seq, seq) per layer
        sample_entropy = []
        for layer_attn in outputs.attentions:
            layer_entropy = compute_attention_entropy(layer_attn, entropy_config.eps)
            sample_entropy.append(layer_entropy.cpu())

        # Stack layers: [1, 32, 32] (batch=1, layers, heads)
        stacked = torch.stack(sample_entropy, dim=1)
        all_entropies.append(stacked)

    # Concatenate samples: [n_samples, 32, 32]
    return torch.cat(all_entropies, dim=0)


def verify_mechanism(model: AutoModelForCausalLM, sample_input: dict) -> bool:
    """Verify attention entropy extraction works correctly."""
    sample_input = {k: v.to(model.device) for k, v in sample_input.items()}
    outputs = model(**sample_input, output_attentions=True)

    # Check 1: Attentions returned
    assert outputs.attentions is not None, "FAIL: output_attentions not working"
    assert len(outputs.attentions) == 32, f"FAIL: Expected 32 layers, got {len(outputs.attentions)}"

    # Check 2: Attention shape correct
    attn = outputs.attentions[0]
    assert len(attn.shape) == 4, f"FAIL: Expected 4D tensor, got {attn.shape}"
    assert attn.shape[1] == 32, f"FAIL: Expected 32 heads, got {attn.shape[1]}"

    # Check 3: Entropy computable and finite
    entropy = compute_attention_entropy(attn)
    assert torch.isfinite(entropy).all(), "FAIL: Entropy contains inf/nan"
    assert entropy.min() >= 0, "FAIL: Negative entropy (impossible)"

    print("Mechanism verification PASSED")
    return True
