"""Tests for data loading module."""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from config import DataConfig
from data import C4DataModule


def test_data_module_initialization():
    """Test C4DataModule can be initialized."""
    data_module = C4DataModule(
        tokenizer_name="gpt2",
        seq_length=512,
        batch_size=32,
        streaming=True
    )
    assert data_module.tokenizer_name == "gpt2"
    assert data_module.seq_length == 512
    assert data_module.batch_size == 32


def test_tokenizer_preparation():
    """Test tokenizer is loaded correctly."""
    data_module = C4DataModule(
        tokenizer_name="gpt2",
        seq_length=512,
        batch_size=32
    )
    data_module.prepare_data()
    assert data_module.tokenizer is not None
    assert data_module.tokenizer.pad_token == data_module.tokenizer.eos_token


def test_data_config():
    """Test DataConfig has correct defaults."""
    config = DataConfig()
    assert config.dataset_name == "allenai/c4"
    assert config.subset == "en"
    assert config.seq_length == 512
    assert config.batch_size == 32
    assert config.streaming is True
