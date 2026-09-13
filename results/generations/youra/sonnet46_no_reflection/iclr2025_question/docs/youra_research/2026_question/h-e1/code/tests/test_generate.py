"""Tests for generate.py — E3 + subtasks spec compliance."""
import os
import pickle
import sys
import tempfile

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from generate import GenerationResult, load_checkpoint, save_checkpoint


def test_generation_result_dataclass():
    r = GenerationResult(
        question_id="q1",
        prompt="What?",
        greedy_text="Answer",
        greedy_log_likelihood=-1.5,
        sampled_texts=["A", "B"],
        sampled_log_likelihoods=[-1.0, -2.0],
    )
    assert r.question_id == "q1"
    assert r.greedy_log_likelihood == -1.5
    assert len(r.sampled_texts) == 2
    assert r.hidden_states_last is None


def test_generation_result_hidden_states():
    hs = np.random.rand(32, 10, 4096).astype(np.float32)
    r = GenerationResult(
        question_id="q1",
        prompt="Q",
        greedy_text="A",
        greedy_log_likelihood=-1.0,
        sampled_texts=["a"],
        sampled_log_likelihoods=[-1.0],
        hidden_states_last=hs,
    )
    assert r.hidden_states_last is not None
    assert r.hidden_states_last.shape == (32, 10, 4096)


def test_save_load_checkpoint_roundtrip():
    results = [
        GenerationResult(
            question_id=f"q{i}",
            prompt=f"Question {i}?",
            greedy_text=f"Answer {i}",
            greedy_log_likelihood=-float(i),
            sampled_texts=[f"s{j}" for j in range(3)],
            sampled_log_likelihoods=[-float(j) for j in range(3)],
        )
        for i in range(5)
    ]
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
        ckpt_path = f.name
    try:
        save_checkpoint(results, ckpt_path)
        loaded = load_checkpoint(ckpt_path)
        assert loaded is not None
        assert len(loaded) == 5
        assert loaded[0].question_id == "q0"
        assert loaded[4].greedy_log_likelihood == -4.0
    finally:
        os.unlink(ckpt_path)


def test_load_checkpoint_missing_file():
    result = load_checkpoint("/tmp/nonexistent_checkpoint_xyz.pkl")
    assert result is None


def test_save_checkpoint_atomic(tmp_path):
    results = [GenerationResult("q1", "Q", "A", -1.0, ["a"], [-1.0])]
    ckpt_path = str(tmp_path / "test.pkl")
    save_checkpoint(results, ckpt_path)
    assert os.path.exists(ckpt_path)
    assert not os.path.exists(ckpt_path + ".tmp")
