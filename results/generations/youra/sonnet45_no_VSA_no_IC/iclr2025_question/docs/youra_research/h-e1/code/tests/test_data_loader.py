"""Test suite for TruthfulQA data loading."""
import pytest
from datasets import load_dataset


def test_truthfulqa_dataset_loads():
    """Verify TruthfulQA dataset loads from cache."""
    ds = load_dataset(
        "truthfulqa/truthful_qa",
        "generation",
        cache_dir="/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_question/docs/youra_research/.data_cache/datasets/truthfulqa"
    )
    assert "validation" in ds
    assert len(ds["validation"]) == 817


def test_truthfulqa_split_exists():
    """Verify dataset contains expected split."""
    ds = load_dataset(
        "truthfulqa/truthful_qa",
        "generation",
        cache_dir="/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_question/docs/youra_research/.data_cache/datasets/truthfulqa"
    )
    sample = ds["validation"][0]
    assert "question" in sample
    assert "correct_answers" in sample
    assert "incorrect_answers" in sample
