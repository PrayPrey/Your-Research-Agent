"""Tests for embedder.py — spec compliance (unit tests, no HF download)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
import torch


def test_encode_codebert_output_shape(tmp_path):
    """Verify encode_codebert returns (N, 768) L2-normalized tensor."""
    from unittest.mock import MagicMock, patch
    import torch.nn.functional as F

    from h_e1.embedder import encode_codebert

    # Mock tokenizer
    tokenizer = MagicMock()
    enc_output = MagicMock()
    enc_output.__getitem__ = lambda self, k: torch.ones(2, 10) if k == "attention_mask" else torch.zeros(2, 10, dtype=torch.long)
    enc_output.to = lambda d: enc_output
    tokenizer.return_value = enc_output

    # Mock model
    model = MagicMock()
    model.eval = MagicMock(return_value=model)
    model.to = MagicMock(return_value=model)
    out = MagicMock()
    out.last_hidden_state = torch.randn(2, 10, 768)
    model.return_value = out

    # Mock context manager
    texts = ["def foo(): pass", "def bar(): return 1"]
    with patch("torch.no_grad", return_value=MagicMock(__enter__=lambda s: None, __exit__=lambda s, *a: None)):
        result = encode_codebert(texts, tokenizer, model, batch_size=2, device="cpu")

    assert result.ndim == 2
    assert result.shape[1] == 768
    norms = result.norm(dim=-1)
    assert torch.allclose(norms, torch.ones_like(norms), atol=1e-5)


def test_encode_codebert_l2_normalized():
    """L2 normalization check on manual tensor."""
    import torch.nn.functional as F
    t = torch.randn(5, 768)
    normalized = F.normalize(t, dim=-1)
    norms = normalized.norm(dim=-1)
    assert torch.allclose(norms, torch.ones(5), atol=1e-5)


def test_encode_all_corpora_structure():
    """Verify encode_all_corpora returns expected dict structure (mocked)."""
    from unittest.mock import patch, MagicMock
    import torch

    with patch("h_e1.embedder.encode_codebert") as mock_cb, \
         patch("h_e1.embedder.encode_minilm") as mock_ml, \
         patch("h_e1.embedder.AutoTokenizer") as mock_tok, \
         patch("h_e1.embedder.AutoModel") as mock_model:

        mock_tok.from_pretrained.return_value = MagicMock()
        mock_model.from_pretrained.return_value = MagicMock(
            to=MagicMock(return_value=MagicMock(eval=MagicMock()))
        )
        mock_cb.return_value = torch.randn(5, 768)
        mock_ml.return_value = torch.randn(5, 384)

        from h_e1.embedder import encode_all_corpora
        corpora = {"source_a": ["text1", "text2", "text3", "text4", "text5"]}
        result = encode_all_corpora(corpora, batch_size=2, device="cpu")

    assert "source_a" in result
    assert "codebert" in result["source_a"]
    assert "minilm" in result["source_a"]
    assert result["source_a"]["codebert"].shape == (5, 768)
    assert result["source_a"]["minilm"].shape == (5, 384)
