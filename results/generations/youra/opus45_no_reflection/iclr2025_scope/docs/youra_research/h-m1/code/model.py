"""Model loading and attention extraction for H-M1."""
import torch
from torch import nn, Tensor
from typing import Dict, List, Tuple
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import AnalysisConfig

def load_model_and_tokenizer(config: AnalysisConfig) -> Tuple[nn.Module, "AutoTokenizer"]:
    """Load Phi-1.5 with fp16, device_map=auto, output_attentions=True."""
    print(f"Loading model {config.model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(config.model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        config.model_name,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="auto",
        output_attentions=True,
    )
    model.eval()
    print(f"Model loaded on {next(model.parameters()).device}")
    return model, tokenizer

def extract_attentions(model: nn.Module, tokens: dict, middle_layers: List[int]) -> Dict[int, Tensor]:
    """Forward pass with output_attentions=True, return {layer_idx: attn [1,H,S,S]}."""
    device = next(model.parameters()).device
    tokens = {k: v.to(device) for k, v in tokens.items()}

    with torch.no_grad():
        outputs = model(**tokens, output_attentions=True)

    return {i: outputs.attentions[i].cpu() for i in middle_layers}

def verify_attention_valid(attn: Tensor) -> None:
    """Assert attention is finite and non-negative."""
    assert torch.isfinite(attn).all(), "Non-finite values in attention"
    assert (attn >= 0).all(), "Negative attention values"
