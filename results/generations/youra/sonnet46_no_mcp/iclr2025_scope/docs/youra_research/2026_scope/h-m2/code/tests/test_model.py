import os
import sys
import pytest
import torch
import torch.nn as nn

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from model import (
    H2OEvictionAwareAttention, set_h2o_budget, verify_budget_applied,
    load_model_for_sweep, set_h2o_training_mode,
)


class MockH2OAttn(nn.Module):
    def __init__(self):
        super().__init__()
        self.kv_budget_ratio = 0.5

    def forward(self, x):
        return x


class MockModelWithH2O(nn.Module):
    def __init__(self, n=3):
        super().__init__()
        self.layers = nn.ModuleList([MockH2OAttn() for _ in range(n)])

    def forward(self, x):
        return x


def make_mock_model_with_h2o(n=3):
    """Create a model with H2OEvictionAwareAttention-compatible mock modules."""
    model = MockModelWithH2O(n)
    # Patch isinstance check by making layers actual H2OEvictionAwareAttention instances
    # For unit test: use the real class by wrapping
    return model


def test_set_h2o_budget_attribute_assignment():
    """set_h2o_budget sets kv_budget_ratio on all H2OEvictionAwareAttention instances.
    GPT-2 proxy doesn't support H2O injection (LLaMA/Mistral only) — skip if no wrappers.
    """
    from config import get_default_config
    cfg = get_default_config()
    eviction_spec = next((a for a in cfg.adapters if a.adapter_type == "eviction-aware"), None)
    if eviction_spec is None:
        pytest.skip("No eviction-aware adapter available")

    model, _ = load_model_for_sweep(
        model_name=eviction_spec.model_name,
        adapter_path=eviction_spec.adapter_path,
        adapter_type=eviction_spec.adapter_type,
        initial_budget=0.5,
    )

    h2o_count = sum(1 for m in model.modules() if isinstance(m, H2OEvictionAwareAttention))
    if h2o_count == 0:
        pytest.skip("GPT-2 proxy: inject_h2o_wrappers only supports LLaMA/Mistral attention classes")

    set_h2o_budget(model, 0.25)
    assert verify_budget_applied(model, 0.25), "Budget 0.25 not applied"

    set_h2o_budget(model, 0.75)
    assert verify_budget_applied(model, 0.75), "Budget 0.75 not applied"
    assert not verify_budget_applied(model, 0.25), "Old budget should not match"


def test_verify_budget_applied_false_on_mismatch():
    """verify_budget_applied returns False when ratio doesn't match."""
    from config import get_default_config
    cfg = get_default_config()
    eviction_spec = next((a for a in cfg.adapters if a.adapter_type == "eviction-aware"), None)
    if eviction_spec is None:
        pytest.skip("No eviction-aware adapter available")

    model, _ = load_model_for_sweep(
        model_name=eviction_spec.model_name,
        adapter_path=eviction_spec.adapter_path,
        adapter_type=eviction_spec.adapter_type,
        initial_budget=0.5,
    )

    h2o_count = sum(1 for m in model.modules() if isinstance(m, H2OEvictionAwareAttention))
    if h2o_count == 0:
        pytest.skip("GPT-2 proxy: no H2O wrappers to test mismatch on")

    set_h2o_budget(model, 0.5)
    assert not verify_budget_applied(model, 0.99)


def test_load_model_for_sweep_returns_eval_mode():
    """load_model_for_sweep returns model in eval mode."""
    from config import get_default_config
    cfg = get_default_config()
    spec = cfg.adapters[0]

    model, tokenizer = load_model_for_sweep(
        model_name=spec.model_name,
        adapter_path=spec.adapter_path,
        adapter_type=spec.adapter_type,
    )
    assert not model.training, "Model should be in eval mode"
    assert tokenizer is not None
    assert tokenizer.pad_token is not None


def test_set_h2o_budget_raises_for_sequential():
    """set_h2o_budget raises ValueError when no H2O wrappers (sequential model)."""
    from config import get_default_config
    cfg = get_default_config()
    seq_spec = next((a for a in cfg.adapters if a.adapter_type == "sequential"), None)
    if seq_spec is None:
        pytest.skip("No sequential adapter available")

    model, _ = load_model_for_sweep(
        model_name=seq_spec.model_name,
        adapter_path=seq_spec.adapter_path,
        adapter_type=seq_spec.adapter_type,
    )
    # Sequential model has no H2O wrappers
    h2o_count = sum(1 for m in model.modules() if isinstance(m, H2OEvictionAwareAttention))
    if h2o_count == 0:
        with pytest.raises(ValueError, match="No H2OEvictionAwareAttention"):
            set_h2o_budget(model, 0.5)
    else:
        pytest.skip("Sequential model unexpectedly has H2O wrappers")
