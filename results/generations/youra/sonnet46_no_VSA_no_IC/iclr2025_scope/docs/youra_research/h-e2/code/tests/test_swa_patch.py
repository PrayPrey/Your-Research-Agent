"""Tests for swa_patch.py — spec compliance (03_logic.md L-E3-1, L-E3-2)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import pytest
from swa_patch import make_sliding_window_causal_mask, patch_layer_with_swa, apply_entropy_guided_swa


class TestMakeSlidingWindowCausalMask:
    def test_shape(self):
        mask = make_sliding_window_causal_mask(10, 3, torch.float32, torch.device("cpu"))
        assert mask.shape == (10, 10)

    def test_dtype(self):
        mask = make_sliding_window_causal_mask(5, 3, torch.float32, torch.device("cpu"))
        assert mask.dtype == torch.float32

    def test_causal_diagonal(self):
        """Position i must attend to itself (diagonal must be 0.0)."""
        mask = make_sliding_window_causal_mask(8, 3, torch.float32, torch.device("cpu"))
        for i in range(8):
            assert mask[i, i].item() == 0.0

    def test_future_blocked(self):
        """Positions beyond i must be -inf."""
        mask = make_sliding_window_causal_mask(8, 3, torch.float32, torch.device("cpu"))
        for i in range(8):
            for j in range(i + 1, 8):
                assert mask[i, j].item() == float("-inf")

    def test_window_lower_bound(self):
        """Position i should NOT attend beyond i - window_size + 1."""
        window = 3
        mask = make_sliding_window_causal_mask(10, window, torch.float32, torch.device("cpu"))
        for i in range(window, 10):
            lower = i - window + 1
            for j in range(0, lower):
                assert mask[i, j].item() == float("-inf"), (
                    f"Row {i} attends to col {j} but lower bound is {lower}"
                )

    def test_window_attended(self):
        """All positions in [max(0, i-w+1), i] should be 0.0."""
        window = 3
        mask = make_sliding_window_causal_mask(10, window, torch.float32, torch.device("cpu"))
        for i in range(10):
            lower = max(0, i - window + 1)
            for j in range(lower, i + 1):
                assert mask[i, j].item() == 0.0

    def test_edge_single_token(self):
        mask = make_sliding_window_causal_mask(1, 512, torch.float32, torch.device("cpu"))
        assert mask.shape == (1, 1)
        assert mask[0, 0].item() == 0.0

    def test_window_larger_than_seq(self):
        """window >= seq_len should produce standard causal mask."""
        mask = make_sliding_window_causal_mask(5, 100, torch.float32, torch.device("cpu"))
        # All lower-triangular should be 0.0
        for i in range(5):
            for j in range(i + 1):
                assert mask[i, j].item() == 0.0


class TestPatchLayerWithSwa:
    def _make_mock_layer(self):
        """Minimal mock for a Llama decoder layer."""
        class MockAttn:
            _swa_patched = False
            def forward(self, hidden_states, attention_mask=None, position_ids=None, **kwargs):
                return (hidden_states, None, None)

        class MockLayer:
            def __init__(self):
                self.self_attn = MockAttn()

        return MockLayer()

    def test_patches_forward(self):
        layer = self._make_mock_layer()
        original = layer.self_attn.forward
        patch_layer_with_swa(layer, window_size=4)
        assert layer.self_attn.forward is not original

    def test_no_double_patch(self):
        layer = self._make_mock_layer()
        patch_layer_with_swa(layer, window_size=4)
        patched_once = layer.self_attn.forward
        patch_layer_with_swa(layer, window_size=4)
        assert layer.self_attn.forward is patched_once  # same object

    def test_swa_patched_flag(self):
        layer = self._make_mock_layer()
        patch_layer_with_swa(layer, window_size=4)
        assert getattr(layer.self_attn, "_swa_patched", False)


class TestApplyEntropyGuidedSwa:
    def _make_mock_model(self, n_layers=8):
        class MockAttn:
            _swa_patched = False
            def forward(self, hidden_states, attention_mask=None, position_ids=None, **kwargs):
                return (hidden_states, None, None)

        class MockLayer:
            def __init__(self):
                self.self_attn = MockAttn()

        class MockModel:
            def __init__(self):
                self.layers = [MockLayer() for _ in range(n_layers)]

        class MockLlama:
            def __init__(self):
                self.model = MockModel()

        return MockLlama()

    def test_returns_target_layers(self):
        model = self._make_mock_model()
        ranking = [3, 1, 5, 7, 0, 2, 4, 6]
        result = apply_entropy_guided_swa(model, ranking, k=3, window_size=4)
        assert result == [3, 1, 5]

    def test_patches_correct_layers(self):
        model = self._make_mock_model()
        ranking = [3, 1, 5, 7, 0, 2, 4, 6]
        target = apply_entropy_guided_swa(model, ranking, k=3, window_size=4)
        for idx in target:
            assert getattr(model.model.layers[idx].self_attn, "_swa_patched", False)

    def test_non_target_layers_untouched(self):
        model = self._make_mock_model()
        ranking = [3, 1, 5, 7, 0, 2, 4, 6]
        target = apply_entropy_guided_swa(model, ranking, k=3, window_size=4)
        for i in range(8):
            if i not in target:
                assert not getattr(model.model.layers[i].self_attn, "_swa_patched", False)

    def test_k_exceeds_ranking_raises(self):
        model = self._make_mock_model()
        ranking = [0, 1, 2]
        with pytest.raises(AssertionError):
            apply_entropy_guided_swa(model, ranking, k=5, window_size=4)
