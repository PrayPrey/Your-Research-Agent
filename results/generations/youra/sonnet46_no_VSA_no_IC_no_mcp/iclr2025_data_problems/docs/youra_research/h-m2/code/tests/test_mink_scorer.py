"""Tests for min-k% scorer — spec compliance per 03_logic.md."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pytest

from mink_scorer import compute_mink_score, MinKScore, save_mink_scores, load_mink_scores


def test_compute_mink_score_basic():
    """compute_mink_score returns mean of lowest k% tokens."""
    probs = np.array([-5.0, -4.0, -3.0, -2.0, -1.0])  # 5 tokens
    result = compute_mink_score(probs, k=20)  # lowest 20% = 1 token = -5.0
    assert result == pytest.approx(-5.0, abs=1e-5)


def test_compute_mink_score_k40():
    """k=40% uses lowest 40% of tokens."""
    probs = np.array([-5.0, -4.0, -3.0, -2.0, -1.0])
    result = compute_mink_score(probs, k=40)  # lowest 40% = 2 tokens: -5.0, -4.0
    assert result == pytest.approx((-5.0 + -4.0) / 2, abs=1e-5)


def test_compute_mink_score_empty():
    """Empty array returns -inf."""
    result = compute_mink_score(np.array([]), k=20)
    assert result == float("-inf")


def test_compute_mink_score_k_count_min_1():
    """k_count is at least 1 even for very small k."""
    probs = np.array([-3.0, -2.0, -1.0])
    result = compute_mink_score(probs, k=1)  # 1% of 3 = 0 → clamped to 1
    assert result == pytest.approx(-3.0, abs=1e-5)


def test_higher_score_less_negative():
    """Higher (less negative) min-k% score means more memorized."""
    memorized_probs = np.array([-1.5, -1.2, -1.0, -0.8, -0.5])  # high probs
    not_memorized = np.array([-5.0, -4.5, -4.0, -3.5, -3.0])   # low probs
    assert compute_mink_score(memorized_probs, k=20) > compute_mink_score(not_memorized, k=20)


def test_mink_score_dataclass():
    """MinKScore stores multi-k scores dict."""
    score = MinKScore(item_id=0, benchmark="mmlu", model_key="pile_1b",
                      scores={10: -4.2, 20: -3.8, 40: -3.1})
    assert score.scores[20] == pytest.approx(-3.8)
    assert score.benchmark == "mmlu"


def test_save_load_roundtrip(tmp_path):
    """save_mink_scores + load_mink_scores roundtrip."""
    scores = [
        MinKScore(item_id=i, benchmark="mmlu", model_key="pile_1b",
                  scores={10: -4.0 + i * 0.1, 20: -3.5 + i * 0.1, 40: -3.0 + i * 0.1})
        for i in range(5)
    ]
    save_mink_scores(scores, "pile_1b", "mmlu", tmp_path)
    loaded = load_mink_scores("pile_1b", "mmlu", tmp_path)

    assert loaded is not None
    assert len(loaded) == 5
    assert loaded[0].item_id == 0
    assert loaded[0].scores[20] == pytest.approx(-3.5, abs=1e-5)


def test_load_missing_returns_none(tmp_path):
    """load_mink_scores returns None for missing file."""
    result = load_mink_scores("nonexistent_model", "mmlu", tmp_path)
    assert result is None


def test_save_atomic_write(tmp_path):
    """No .tmp file left after save."""
    scores = [MinKScore(item_id=0, benchmark="arc_challenge",
                        model_key="deduped_1b", scores={20: -3.0})]
    save_mink_scores(scores, "deduped_1b", "arc_challenge", tmp_path)
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert len(tmp_files) == 0
