"""Test suite for dataset splitting."""
import pytest
from data.loader import TruthfulQALoader


def test_loader_init():
    """Verify TruthfulQALoader initializes with seed."""
    loader = TruthfulQALoader(seed=42)
    assert loader.seed == 42


def test_split_sizes():
    """Verify 40/60 split produces correct sizes."""
    loader = TruthfulQALoader(seed=42)
    cal, test = loader.load_and_split(cal_ratio=0.4)

    total = len(cal) + len(test)
    assert total == 817
    assert len(cal) == pytest.approx(327, abs=5)  # ~40%
    assert len(test) == pytest.approx(490, abs=5)  # ~60%


def test_split_reproducibility():
    """Verify seeded split is reproducible."""
    loader1 = TruthfulQALoader(seed=42)
    cal1, test1 = loader1.load_and_split(cal_ratio=0.4)

    loader2 = TruthfulQALoader(seed=42)
    cal2, test2 = loader2.load_and_split(cal_ratio=0.4)

    assert cal1[0]["question"] == cal2[0]["question"]
    assert test1[0]["question"] == test2[0]["question"]


def test_label_correctness():
    """Verify correctness labeling."""
    loader = TruthfulQALoader()

    # Correct answer
    label = loader.label_correctness(
        question="What is 2+2?",
        answer="The answer is four.",
        correct_answers=["four", "4"]
    )
    assert label == 0

    # Incorrect answer
    label = loader.label_correctness(
        question="What is 2+2?",
        answer="The answer is five.",
        correct_answers=["four", "4"]
    )
    assert label == 1
