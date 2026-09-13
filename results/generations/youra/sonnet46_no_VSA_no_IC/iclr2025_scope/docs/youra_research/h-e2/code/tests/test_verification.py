"""Tests for verification.py — spec compliance (03_logic.md L-E5-1, L-E5-2)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import pytest
from swa_patch import make_sliding_window_causal_mask
from verification import validate_swa_mask, verify_swa_mechanism


class TestValidateSWAMask:
    def test_valid_mask_passes(self):
        mask = make_sliding_window_causal_mask(20, 5, torch.float32, torch.device("cpu"))
        validate_swa_mask(mask, window_size=5)  # should not raise

    def test_invalid_mask_raises_on_future(self):
        """Mask with future positions attended should fail."""
        bad_mask = torch.full((10, 10), float("-inf"))
        bad_mask[5, 6] = 0.0  # attending future
        bad_mask[5, 5] = 0.0  # diagonal ok
        with pytest.raises(AssertionError):
            validate_swa_mask(bad_mask, window_size=3)

    def test_window_512(self):
        """Standard h-e2 window size passes validation."""
        mask = make_sliding_window_causal_mask(600, 512, torch.float32, torch.device("cpu"))
        validate_swa_mask(mask, window_size=512)

    def test_empty_row_fails(self):
        mask = torch.full((5, 5), float("-inf"))
        with pytest.raises(AssertionError, match="no attended positions"):
            validate_swa_mask(mask, window_size=3)


class TestVerifySWAMechanism:
    def _make_patched_model(self, n_layers=4, window_size=3, target_layers=None):
        """Minimal mock model with SWA patches."""
        from swa_patch import patch_layer_with_swa

        class MockAttn:
            _swa_patched = False
            def forward(self, hidden_states, attention_mask=None, position_ids=None, **kwargs):
                return (hidden_states, None, None)

        class MockLayer:
            def __init__(self):
                self.self_attn = MockAttn()
            def register_forward_pre_hook(self, fn, with_kwargs=False):
                class Hook:
                    def remove(self): pass
                # Store hook for manual calling
                self._hook = fn
                return Hook()

        class MockModelInner:
            def __init__(self):
                self.layers = [MockLayer() for _ in range(n_layers)]

        class MockModel:
            def __init__(self, inner, target_layers, window_size):
                self.model = inner
                self._target = target_layers or []
                self._window = window_size

            def __call__(self, input_ids):
                pass  # no-op

            def parameters(self):
                return iter([torch.zeros(1)])

        inner = MockModelInner()
        if target_layers:
            for idx in target_layers:
                patch_layer_with_swa(inner.layers[idx], window_size=window_size)
        return MockModel(inner, target_layers, window_size)

    def test_seq_len_guard(self):
        """test_seq_len must be > window_size."""
        from verification import verify_swa_mechanism
        # Can't easily test the full hook path without real model,
        # but can test the guard
        with pytest.raises(AssertionError, match="must be > window_size"):
            class DummyModel:
                class model:
                    layers = []
                def parameters(self): return iter([torch.zeros(1)])
            verify_swa_mechanism(DummyModel(), [], window_size=512, test_seq_len=512)


class TestConfigImport:
    def test_config_importable(self):
        from config import ExperimentConfig
        cfg = ExperimentConfig()
        assert cfg.swa_k == 4
        assert cfg.swa_window_size == 512
        assert cfg.attn_implementation == "eager"
        assert cfg.eval_stride == cfg.swa_window_size  # stride == window_size constraint
