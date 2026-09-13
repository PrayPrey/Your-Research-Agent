"""H-M3 Model Loading - Teacher (Phi-1.5) and Student (Mamba) with AttentionBridge"""
import torch
from torch import nn, Tensor
from typing import Tuple, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import ExperimentConfig

def load_teacher(config: ExperimentConfig) -> Tuple[nn.Module, AutoTokenizer]:
    """Load Phi-1.5 teacher model with attention output enabled."""
    tokenizer = AutoTokenizer.from_pretrained(config.teacher_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype = torch.bfloat16 if config.dtype == "bfloat16" else torch.float16
    model = AutoModelForCausalLM.from_pretrained(
        config.teacher_name,
        torch_dtype=dtype,
        trust_remote_code=True,
        device_map="auto",
    )
    model.eval()
    return model, tokenizer

def load_student_base(config: ExperimentConfig) -> nn.Module:
    """Load fresh Mamba student base model using HuggingFace transformers."""
    dtype = torch.bfloat16 if config.dtype == "bfloat16" else torch.float16
    from transformers import MambaForCausalLM
    model = MambaForCausalLM.from_pretrained(
        config.student_base_name,
        torch_dtype=dtype,
        device_map="auto",
    )
    return model

def get_student_dim(model: nn.Module) -> int:
    """Get hidden dimension from model config."""
    if hasattr(model, 'config'):
        if hasattr(model.config, 'hidden_size'):
            return model.config.hidden_size
        if hasattr(model.config, 'd_model'):
            return model.config.d_model
    return 2048

class AttentionBridge(nn.Module):
    """MLP bridge: teacher Q/K -> student B/C target space."""
    def __init__(self, d_model: int, hidden_dim: int = None):
        super().__init__()
        hidden_dim = hidden_dim or d_model * 2
        self.q_to_b = nn.Sequential(
            nn.Linear(d_model, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, d_model)
        )
        self.k_to_c = nn.Sequential(
            nn.Linear(d_model, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, d_model)
        )

    def forward(self, q: Tensor, k: Tensor) -> Tuple[Tensor, Tensor]:
        """q,k: [B, N, D] -> (b_target, c_target): [B, N, D]"""
        return self.q_to_b(q), self.k_to_c(k)
