"""Tests for analyze_sft_loss.py — mock-based unit tests (no GPU needed)."""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_compute_per_example_loss_empty_solutions():
    """Returns None when solutions list is empty."""
    from unittest.mock import MagicMock
    from analyze_sft_loss import compute_per_example_loss

    model = MagicMock()
    tokenizer = MagicMock()
    tokenizer.return_value = {"input_ids": MagicMock(shape=(1, 100))}

    example = {"problem": "test", "solutions": "[]", "difficulty": "competition"}
    result = compute_per_example_loss(model, tokenizer, example, device="cpu")
    assert result is None


def test_compute_per_example_loss_invalid_solutions():
    """Returns None when solutions is unparseable."""
    from unittest.mock import MagicMock
    from analyze_sft_loss import compute_per_example_loss

    model = MagicMock()
    tokenizer = MagicMock()

    example = {"problem": "test", "solutions": "not-json", "difficulty": "competition"}
    result = compute_per_example_loss(model, tokenizer, example, device="cpu")
    assert result is None


def test_stratified_loss_output_has_buckets(tmp_path):
    """Output JSON has mean/std/count per bucket (mocked model)."""
    import json
    from unittest.mock import MagicMock, patch
    import torch

    output_path = str(tmp_path / "loss.json")

    # Mock model output with scalar loss
    mock_output = MagicMock()
    mock_output.loss = torch.tensor(1.5)

    mock_model = MagicMock()
    mock_model.return_value = mock_output

    # Mock tokenizer
    mock_tokenizer = MagicMock()
    mock_enc = {
        "input_ids": torch.ones(1, 10, dtype=torch.long),
        "attention_mask": torch.ones(1, 10),
    }
    mock_tokenizer.return_value = mock_enc
    mock_tokenizer.side_effect = None

    from analyze_sft_loss import compute_difficulty_stratified_loss

    # Minimal dataset mock
    fake_ds = [
        {"problem": "p1", "solutions": '["x=1"]', "difficulty": "introductory"},
        {"problem": "p2", "solutions": '["y=2"]', "difficulty": "competition"},
    ]

    with patch("analyze_sft_loss.load_model_and_tokenizer", return_value=(mock_model, mock_tokenizer)), \
         patch("analyze_sft_loss.load_dataset", return_value=fake_ds):
        result = compute_difficulty_stratified_loss(
            checkpoint_path="mock_ckpt",
            output_path=output_path,
            max_examples_per_bucket=1,
            device="cpu",
        )

    assert "introductory" in result
    assert "competition" in result
    for bucket in result.values():
        assert "mean" in bucket
        assert "std" in bucket
        assert "count" in bucket

    with open(output_path) as f:
        saved = json.load(f)
    assert "introductory" in saved
