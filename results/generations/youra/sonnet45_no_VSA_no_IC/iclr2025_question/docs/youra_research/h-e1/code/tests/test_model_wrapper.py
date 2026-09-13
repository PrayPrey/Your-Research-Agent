"""Test suite for Llama wrapper (structure only, no model load)."""
import pytest
from models.llama_wrapper import LlamaWrapper


def test_llama_wrapper_import():
    """Verify LlamaWrapper class is importable."""
    assert LlamaWrapper is not None
    assert hasattr(LlamaWrapper, "generate")
    assert hasattr(LlamaWrapper, "enable_dropout")


def test_llama_wrapper_init_signature():
    """Verify init signature matches spec."""
    import inspect
    sig = inspect.signature(LlamaWrapper.__init__)
    params = list(sig.parameters.keys())
    assert "self" in params
    assert "model_id" in params
    assert "cache_dir" in params


def test_generate_signature():
    """Verify generate method signature."""
    import inspect
    sig = inspect.signature(LlamaWrapper.generate)
    params = list(sig.parameters.keys())
    assert "questions" in params
    assert "batch_size" in params
    assert "max_tokens" in params
    assert "temperature" in params
    assert "top_p" in params


# NOTE: Actual model loading test deferred to experiment execution
# (requires HF token for gated Llama-3.1-8B access)
