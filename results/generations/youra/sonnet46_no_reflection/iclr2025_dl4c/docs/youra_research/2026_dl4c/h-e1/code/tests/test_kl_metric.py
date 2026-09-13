import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from kl_metric import load_checkpoint_kl_log, save_kl_log, match_checkpoints


def test_load_kl_log_empty_when_missing(tmp_path):
    result = load_checkpoint_kl_log(str(tmp_path))
    assert result == []


def test_save_and_load_kl_log(tmp_path):
    log = [{"step": 100, "kl_divergence": 0.5}, {"step": 200, "kl_divergence": 0.3}]
    save_kl_log(str(tmp_path), log)
    loaded = load_checkpoint_kl_log(str(tmp_path))
    assert loaded == log


def test_match_checkpoints_finds_match():
    grpo_log = [{"step": 100, "kl_divergence": 0.5}, {"step": 200, "kl_divergence": 1.0}]
    dpo_log = [{"step": 100, "kl_divergence": 0.52}, {"step": 200, "kl_divergence": 2.0}]
    matched = match_checkpoints(grpo_log, dpo_log, tolerance=0.05)
    assert len(matched) >= 1
    assert matched[0]["grpo_step"] == 100
    assert matched[0]["dpo_step"] == 100


def test_match_checkpoints_no_match():
    grpo_log = [{"step": 100, "kl_divergence": 0.5}]
    dpo_log = [{"step": 100, "kl_divergence": 2.0}]
    matched = match_checkpoints(grpo_log, dpo_log, tolerance=0.05)
    assert matched == []


def test_match_checkpoints_empty_logs():
    assert match_checkpoints([], [], tolerance=0.05) == []
    assert match_checkpoints([{"step": 1, "kl_divergence": 0.5}], [], tolerance=0.05) == []


def test_match_checkpoints_returns_correct_fields():
    grpo_log = [{"step": 50, "kl_divergence": 0.3}]
    dpo_log = [{"step": 75, "kl_divergence": 0.32}]
    matched = match_checkpoints(grpo_log, dpo_log, tolerance=0.05)
    assert len(matched) == 1
    m = matched[0]
    assert "grpo_step" in m
    assert "dpo_step" in m
    assert "kl_grpo" in m
    assert "kl_dpo" in m
