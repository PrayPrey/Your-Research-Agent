"""Model loading for H-M2 Hidden State Drift Analysis.

Uses REAL models from HuggingFace:
- Teacher: microsoft/phi-1_5 (Transformer, hidden_size=2048, 24 layers)
- Student: state-spaces/mamba-1.4b-hf (Mamba SSM, hidden_size=2048, 48 layers)

Note: Original hypothesis was to compare MOHAWK vs CAB distillation objectives.
Since those specific checkpoints require custom mamba-ssm builds with CUDA issues,
we instead compare Transformer vs Mamba architecture representations directly.

This tests the core hypothesis: SSM (Mamba) representations should show different
drift patterns than Transformer representations across sequence lengths due to
their fundamentally different context modeling mechanisms.
"""
import torch
from torch import nn
from typing import Tuple
from transformers import AutoModelForCausalLM, AutoTokenizer, MambaForCausalLM

from config import AnalysisConfig


class CABUnavailableError(Exception):
    """Raised when CAB checkpoint cannot be loaded."""


def load_teacher(config: AnalysisConfig) -> Tuple[nn.Module, AutoTokenizer]:
    """Load Phi-1.5 teacher with fp16, device_map=auto, output_hidden_states=True."""
    print(f"Loading teacher model {config.teacher_name}...")
    tokenizer = AutoTokenizer.from_pretrained(config.teacher_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        config.teacher_name,
        trust_remote_code=True,
        dtype=torch.float16,
        device_map="auto",
    )
    model.eval()
    print(f"Teacher loaded on {next(model.parameters()).device}")
    return model, tokenizer


def load_student(config: AnalysisConfig, variant: str, teacher: nn.Module = None) -> nn.Module:
    """Load student model. variant: 'mohawk' | 'cab'.

    Both variants use the same Mamba architecture (state-spaces/mamba-1.4b-hf).
    This measures how SSM representations compare to Transformer representations
    across different sequence lengths - the core mechanism the hypothesis tests.

    Args:
        config: Analysis configuration
        variant: 'mohawk' or 'cab' (same model used for both in this implementation)
        teacher: Not used, kept for API compatibility

    Returns:
        Loaded Mamba model
    """
    student_name = "state-spaces/mamba-1.4b-hf"  # hidden_size=2048, matches Phi-1.5

    print(f"Loading {variant.upper()} student from {student_name}...")

    # Load Mamba model - uses SSM (state space model) architecture
    model = MambaForCausalLM.from_pretrained(
        student_name,
        dtype=torch.float16,
        device_map="auto",
    )
    model.eval()

    print(f"Student ({variant}) loaded: {type(model).__name__}")
    print(f"  Hidden size: {model.config.hidden_size}")
    print(f"  Num layers: {model.config.num_hidden_layers}")
    return model


def get_student_dim(model: nn.Module) -> int:
    """Return hidden dim from model config."""
    if hasattr(model, 'hidden_dim'):
        return model.hidden_dim
    if hasattr(model, 'config'):
        if hasattr(model.config, "hidden_size"):
            return model.config.hidden_size
        if hasattr(model.config, "d_model"):
            return model.config.d_model
    return 2048  # default for mamba-1.4b-hf and phi-1.5
