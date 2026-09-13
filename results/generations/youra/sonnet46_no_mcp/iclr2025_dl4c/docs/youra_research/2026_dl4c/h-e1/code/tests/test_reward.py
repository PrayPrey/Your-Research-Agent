"""Tests for training/reward.py spec compliance."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from training.reward import run_unit_tests, execution_reward_fn, compute_reward_density


def test_compute_reward_density_nonzero_std():
    # Mixed rewards -> non-zero std -> density = 1.0
    rewards = [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0]
    assert compute_reward_density(rewards) == 1.0


def test_compute_reward_density_zero_std():
    # All zeros -> std = 0 -> density = 0.0
    rewards = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    assert compute_reward_density(rewards) == 0.0


def test_compute_reward_density_all_ones():
    # All ones -> std = 0 -> density = 0.0
    rewards = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    assert compute_reward_density(rewards) == 0.0


def test_compute_reward_density_empty():
    assert compute_reward_density([]) == 0.0


def test_compute_reward_density_single():
    assert compute_reward_density([1.0]) == 0.0


def test_run_unit_tests_no_tests():
    result = run_unit_tests("x = 1", [])
    assert result is False


def test_execution_reward_fn_returns_list():
    rewards = execution_reward_fn(
        completions=["x = 1", "y = 2"],
        prompts=["problem 1", "problem 2"],
        examples=[{}, {}],
    )
    assert isinstance(rewards, list)
    assert len(rewards) == 2
    assert all(r in (0.0, 1.0) for r in rewards)


def test_execution_reward_fn_length_matches():
    completions = ["code1", "code2", "code3"]
    prompts = ["p1", "p2", "p3"]
    rewards = execution_reward_fn(completions, prompts, examples=[{}, {}, {}])
    assert len(rewards) == len(completions)
