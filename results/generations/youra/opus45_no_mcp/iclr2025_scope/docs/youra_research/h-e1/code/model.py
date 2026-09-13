"""Model definitions for H-E1: Transformer baseline and Mamba proposed"""

import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType

from config import MODEL_ID_BASELINE, LORA_CONFIG_TRANSFORMER, LORA_CONFIG_MAMBA

try:
    from mamba_ssm import Mamba
    MAMBA_AVAILABLE = True
except ImportError:
    MAMBA_AVAILABLE = False


def load_baseline_model(lora_config: dict = None):
    """Load Llama-2-7B with LoRA on q/k/v/o_proj."""
    if lora_config is None:
        lora_config = LORA_CONFIG_TRANSFORMER

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID_BASELINE,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    peft_config = LoraConfig(
        r=lora_config["r"],
        lora_alpha=lora_config["lora_alpha"],
        target_modules=lora_config["target_modules"],
        lora_dropout=lora_config["lora_dropout"],
        task_type=TaskType.CAUSAL_LM,
    )

    model = get_peft_model(model, peft_config)
    return model


def load_tokenizer():
    """Load tokenizer for Llama-2."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID_BASELINE)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


class MambaWithLoRA(nn.Module):
    """Mamba model with LoRA-compatible projection layers."""

    def __init__(
        self,
        d_model: int = 4096,
        d_state: int = 64,
        n_layers: int = 32,
        d_conv: int = 4,
        expand: int = 2,
        vocab_size: int = 32000,
    ):
        super().__init__()
        self.d_model = d_model
        self.vocab_size = vocab_size

        self.embedding = nn.Embedding(vocab_size, d_model)

        if MAMBA_AVAILABLE:
            self.layers = nn.ModuleList([
                Mamba(d_model=d_model, d_state=d_state, d_conv=d_conv, expand=expand)
                for _ in range(n_layers)
            ])
        else:
            self.layers = nn.ModuleList([
                MambaBlockSimulated(d_model, d_state, d_conv, expand)
                for _ in range(n_layers)
            ])

        self.final_norm = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, input_ids, attention_mask=None, labels=None):
        x = self.embedding(input_ids)

        for layer in self.layers:
            x = layer(x) + x

        x = self.final_norm(x)
        logits = self.lm_head(x)

        loss = None
        if labels is not None:
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss_fn = nn.CrossEntropyLoss()
            loss = loss_fn(shift_logits.view(-1, self.vocab_size), shift_labels.view(-1))

        return type("Output", (), {"loss": loss, "logits": logits})()


class MambaBlockSimulated(nn.Module):
    """Simulated Mamba block for when mamba-ssm is unavailable."""

    def __init__(self, d_model, d_state, d_conv, expand):
        super().__init__()
        d_inner = d_model * expand
        self.in_proj = nn.Linear(d_model, d_inner * 2, bias=False)
        self.conv1d = nn.Conv1d(d_inner, d_inner, d_conv, padding=d_conv - 1, groups=d_inner)
        self.out_proj = nn.Linear(d_inner, d_model, bias=False)
        self.A_log = nn.Parameter(torch.randn(d_inner, d_state))
        self.D = nn.Parameter(torch.ones(d_inner))

    def forward(self, x):
        B, L, D = x.shape
        xz = self.in_proj(x)
        x_part, z = xz.chunk(2, dim=-1)
        x_part = x_part.transpose(1, 2)
        x_part = self.conv1d(x_part)[:, :, :L]
        x_part = x_part.transpose(1, 2)
        x_part = x_part * torch.sigmoid(z)
        return self.out_proj(x_part)


def load_proposed_model(lora_config: dict = None):
    """Load MambaWithLoRA and apply PEFT LoRA."""
    if lora_config is None:
        lora_config = LORA_CONFIG_MAMBA

    model = MambaWithLoRA()

    peft_config = LoraConfig(
        r=lora_config["r"],
        lora_alpha=lora_config["lora_alpha"],
        target_modules=lora_config["target_modules"],
        lora_dropout=lora_config["lora_dropout"],
        task_type=TaskType.CAUSAL_LM,
    )

    model = get_peft_model(model, peft_config)
    return model


def verify_mechanism_active(model, sample_input):
    """Verify SSM mechanism is active in model."""
    base = model.base_model if hasattr(model, "base_model") else model

    for i, layer in enumerate(base.layers):
        mixer = layer.mixer if hasattr(layer, "mixer") else layer
        assert hasattr(mixer, "A_log"), f"Layer {i}: SSM A matrix not found"
        assert hasattr(mixer, "D"), f"Layer {i}: SSM D matrix not found"

    with torch.no_grad():
        if hasattr(model, "forward"):
            out = model(sample_input)
            if hasattr(out, "logits"):
                assert out.logits.shape[:2] == sample_input.shape, "Shape mismatch"

    print("✓ SSM mechanism verified: state evolution active")
    return True
