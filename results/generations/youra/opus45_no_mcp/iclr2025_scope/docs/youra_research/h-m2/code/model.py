"""Model definitions for H-M2: MambaWithLoRA (standalone)"""

import torch
import torch.nn as nn
from transformers import AutoTokenizer
from peft import LoraConfig, get_peft_model

from config import LORA_CONFIG, MODEL_ID

try:
    from mamba_ssm import Mamba
    MAMBA_AVAILABLE = True
except ImportError:
    MAMBA_AVAILABLE = False


class MambaConfig:
    model_type = "mamba"
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


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
        self.config = MambaConfig(
            d_model=d_model, d_state=d_state, n_layers=n_layers,
            d_conv=d_conv, expand=expand, vocab_size=vocab_size, model_type="mamba"
        )

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


def load_proposed_model(vocab_size=50304, d_model=1024, n_layers=8):
    """Load MambaWithLoRA (no LoRA applied yet - for finetune.py to add)."""
    model = MambaWithLoRA(d_model=d_model, d_state=16, n_layers=n_layers, vocab_size=vocab_size)
    return model


def load_tokenizer():
    """Load tokenizer for Mamba/Llama."""
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer
