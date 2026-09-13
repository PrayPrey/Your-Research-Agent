"""Tests for scorer.py — SMCNLIScorer and SMCEmbedScorer spec compliance."""
import json
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scorer import SMCEmbedScorer, SMCNLIScorer


def make_mock_nli_scorer():
    """Return SMCNLIScorer with mocked model/tokenizer."""
    import torch
    scorer = SMCNLIScorer.__new__(SMCNLIScorer)
    scorer.device = "cpu"
    scorer.batch_size = 16
    scorer.max_length = 512
    scorer.tokenizer = MagicMock()
    scorer.model = MagicMock()
    scorer.model.eval.return_value = scorer.model

    # Default mock: return random logits
    def mock_model_call(**kwargs):
        n = kwargs.get("input_ids", None)
        batch_size = 16
        out = MagicMock()
        out.logits = torch.rand(batch_size, 3)
        return out

    scorer.model.side_effect = None
    scorer.model.return_value = MagicMock()
    scorer.model.return_value.logits = torch.rand(16, 3)
    scorer.tokenizer.return_value = MagicMock()
    return scorer


def test_smcnli_score_pairs_shape():
    """score_pairs returns ndarray of shape (num_pairs,)."""
    import torch
    scorer = make_mock_nli_scorer()
    n_pairs = 5
    scorer.model.return_value.logits = torch.rand(n_pairs, 3)

    premises = [f"p{i}" for i in range(n_pairs)]
    hypotheses = [f"h{i}" for i in range(n_pairs)]
    result = scorer.score_pairs(premises, hypotheses)
    assert isinstance(result, np.ndarray)
    assert result.shape == (n_pairs,)
    assert np.all(result >= 0.0) and np.all(result <= 1.0)


def test_smcnli_score_question_returns_float():
    """score_question returns float in [0, 1]."""
    import torch
    scorer = make_mock_nli_scorer()
    scorer.model.return_value.logits = torch.rand(16, 3)

    result = scorer.score_question("What is 2+2?", [f"answer{i}" for i in range(10)])
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_smcnli_score_all_length():
    """score_all returns list of same length as questions."""
    import torch
    scorer = make_mock_nli_scorer()
    scorer.model.return_value.logits = torch.rand(16, 3)

    with tempfile.TemporaryDirectory() as tmp:
        save = os.path.join(tmp, "nli.json")
        qs = [f"Q{i}?" for i in range(5)]
        samps = [[f"a{j}" for j in range(10)] for _ in range(5)]
        labels = [0, 1, 0, 1, 0]
        result = scorer.score_all(qs, samps, labels, save_path=save)
        assert len(result) == 5


def test_smcembed_score_returns_float():
    """SMCEmbedScorer.score returns float."""
    embed = SMCEmbedScorer.__new__(SMCEmbedScorer)
    mock_model = MagicMock()
    arr = np.random.rand(10, 768).astype(np.float32)
    # normalize
    arr = arr / np.linalg.norm(arr, axis=1, keepdims=True)
    mock_model.encode.return_value = arr
    embed.model = mock_model

    result = embed.score([f"s{i}" for i in range(10)])
    assert isinstance(result, float)
    assert -1.0 <= result <= 1.0


def test_smcembed_score_all_length():
    """SMCEmbedScorer.score_all returns list of correct length."""
    embed = SMCEmbedScorer.__new__(SMCEmbedScorer)
    mock_model = MagicMock()
    arr = np.random.rand(10, 768).astype(np.float32)
    arr = arr / np.linalg.norm(arr, axis=1, keepdims=True)
    mock_model.encode.return_value = arr
    embed.model = mock_model

    with tempfile.TemporaryDirectory() as tmp:
        save = os.path.join(tmp, "embed.json")
        samps = [[f"a{j}" for j in range(10)] for _ in range(5)]
        result = embed.score_all(samps, save_path=save)
        assert len(result) == 5
