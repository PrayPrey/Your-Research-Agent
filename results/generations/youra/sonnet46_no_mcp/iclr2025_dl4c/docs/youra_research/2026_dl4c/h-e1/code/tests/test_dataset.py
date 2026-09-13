"""Tests for data/dataset.py spec compliance."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import MagicMock
from data.dataset import (
    CurriculumDataset, UniformDataset, EasyOnlyDataset,
    HardOnlyDataset, get_dataset
)


def make_mock_dataset(n=10, start=0):
    """Create a mock HuggingFace dataset."""
    items = [{"input_ids": [start + i], "prompt": f"problem {i}"} for i in range(n)]
    ds = MagicMock()
    ds.__len__ = MagicMock(return_value=n)
    ds.__getitem__ = MagicMock(side_effect=lambda idx: items[idx % n])
    return ds


def test_curriculum_dataset_starts_easy():
    easy = make_mock_dataset(10, start=0)
    hard = make_mock_dataset(10, start=100)
    ds = CurriculumDataset(easy, hard, curriculum_step=2500)
    assert ds.active_data is easy


def test_curriculum_dataset_switches_at_step():
    easy = make_mock_dataset(10, start=0)
    hard = make_mock_dataset(10, start=100)
    ds = CurriculumDataset(easy, hard, curriculum_step=2500)
    ds.set_step(2499)
    assert ds.active_data is easy
    ds.set_step(2500)
    assert ds.active_data is hard


def test_curriculum_dataset_no_double_switch():
    easy = make_mock_dataset(10, start=0)
    hard = make_mock_dataset(10, start=100)
    ds = CurriculumDataset(easy, hard, curriculum_step=2500)
    ds.set_step(2500)
    ds.set_step(3000)
    assert ds.active_data is hard


def test_curriculum_dataset_len_and_getitem():
    easy = make_mock_dataset(10)
    hard = make_mock_dataset(5)
    ds = CurriculumDataset(easy, hard, curriculum_step=2500)
    assert len(ds) == 10
    item = ds[0]
    assert isinstance(item, dict)


def test_uniform_dataset():
    full = make_mock_dataset(20)
    ds = UniformDataset(full)
    assert len(ds) == 20
    item = ds[0]
    assert isinstance(item, dict)


def test_easy_only_dataset():
    easy = make_mock_dataset(15)
    ds = EasyOnlyDataset(easy)
    assert len(ds) == 15


def test_hard_only_dataset():
    hard = make_mock_dataset(8)
    ds = HardOnlyDataset(hard)
    assert len(ds) == 8


def test_get_dataset_factory():
    easy = make_mock_dataset(10)
    hard = make_mock_dataset(5)
    full = make_mock_dataset(20)

    assert isinstance(get_dataset("curriculum", easy, hard, full), CurriculumDataset)
    assert isinstance(get_dataset("uniform", easy, hard, full), UniformDataset)
    assert isinstance(get_dataset("easy_only", easy, hard, full), EasyOnlyDataset)
    assert isinstance(get_dataset("hard_only", easy, hard, full), HardOnlyDataset)


def test_get_dataset_invalid_condition():
    easy = make_mock_dataset(5)
    hard = make_mock_dataset(5)
    full = make_mock_dataset(10)
    with pytest.raises(ValueError):
        get_dataset("invalid", easy, hard, full)
