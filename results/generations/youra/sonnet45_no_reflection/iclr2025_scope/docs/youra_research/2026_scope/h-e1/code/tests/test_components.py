"""
Test suite for models/components.py - Specification compliance tests
Tests LoRAExpert, LoRARouter, and CoordinationModule
"""
import pytest
import torch
from config import ModelConfig


def test_lora_expert_exists():
    """Test LoRAExpert class exists with required methods"""
    from models.components import LoRAExpert

    assert hasattr(LoRAExpert, '__init__')
    assert hasattr(LoRAExpert, 'forward')


def test_lora_expert_forward():
    """Test LoRAExpert forward pass"""
    from models.components import LoRAExpert

    hidden_dim = 512
    rank = 8
    alpha = 16
    batch_size = 4
    seq_len = 32

    expert = LoRAExpert(hidden_dim, rank, alpha)
    x = torch.randn(batch_size, seq_len, hidden_dim)

    output = expert(x)

    assert output.shape == x.shape  # [B, N, D]
    assert output.dtype == x.dtype


def test_lora_router_exists():
    """Test LoRARouter class exists"""
    from models.components import LoRARouter

    assert hasattr(LoRARouter, '__init__')
    assert hasattr(LoRARouter, 'forward')


def test_lora_router_forward():
    """Test LoRARouter forward pass returns indices and probs"""
    from models.components import LoRARouter

    hidden_dim = 512
    num_experts = 8
    top_k = 2
    batch_size = 4
    seq_len = 32

    router = LoRARouter(hidden_dim, num_experts, top_k)
    x = torch.randn(batch_size, seq_len, hidden_dim)

    expert_indices, expert_probs = router(x)

    # Should return top-k indices and probabilities
    assert expert_indices.shape[0] == batch_size
    assert expert_probs.shape[0] == batch_size
    assert expert_indices.shape[1] == top_k or expert_indices.shape[-1] == top_k
    assert expert_probs.shape[1] == top_k or expert_probs.shape[-1] == top_k


def test_coordination_module_exists():
    """Test CoordinationModule class exists"""
    from models.components import CoordinationModule

    assert hasattr(CoordinationModule, '__init__')
    assert hasattr(CoordinationModule, 'forward')
    assert hasattr(CoordinationModule, 'compute_alignment_loss')


def test_coordination_module_forward():
    """Test CoordinationModule forward pass"""
    from models.components import CoordinationModule

    config = ModelConfig(
        lora_rank=8,
        lora_alpha=16,
        num_lora_experts=8,
        top_k=2
    )

    module = CoordinationModule(config)

    batch_size = 4
    seq_len = 32
    hidden_dim = 4096
    num_moe_experts = 8

    hidden_states = torch.randn(batch_size, seq_len, hidden_dim)
    moe_expert_probs = torch.randn(batch_size, num_moe_experts).softmax(dim=-1)

    output, aux_loss = module(hidden_states, moe_expert_probs)

    assert output.shape == hidden_states.shape
    assert isinstance(aux_loss, torch.Tensor)
    assert aux_loss.ndim == 0  # scalar


def test_coordination_module_alignment_loss():
    """Test CoordinationModule compute_alignment_loss"""
    from models.components import CoordinationModule

    config = ModelConfig()
    module = CoordinationModule(config)

    batch_size = 4
    num_experts = 8

    lora_probs = torch.randn(batch_size, num_experts).softmax(dim=-1)
    moe_probs = torch.randn(batch_size, num_experts).softmax(dim=-1)
    task_weights = torch.rand(batch_size)

    loss = module.compute_alignment_loss(lora_probs, moe_probs, task_weights)

    assert isinstance(loss, torch.Tensor)
    assert loss.ndim == 0  # scalar
    assert loss >= 0  # KL divergence is non-negative
