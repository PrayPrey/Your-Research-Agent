"""Tests for difficulty_reward_callback.py — H-M2."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from difficulty_reward_callback import DifficultyRewardCallback, verify_mechanism_activated


def test_compute_fractions_empty():
    cb = DifficultyRewardCallback()
    fracs = cb.compute_fractions()
    assert fracs == {}, f"Expected empty dict, got {fracs}"


def test_accumulate_and_compute():
    cb = DifficultyRewardCallback()
    cb.bucket_indicators["competition"].extend([1.0, 0.0, 1.0, 1.0])
    cb.bucket_indicators["introductory"].extend([1.0, 1.0, 1.0])
    cb.bucket_indicators["interview"].extend([1.0, 0.0])
    fracs = cb.compute_fractions()
    assert abs(fracs["competition"] - 0.75) < 1e-6
    assert abs(fracs["introductory"] - 1.0) < 1e-6
    assert abs(fracs["interview"] - 0.5) < 1e-6


def test_gate_pass():
    cb = DifficultyRewardCallback()
    cb.bucket_indicators["competition"].extend([1.0] * 15 + [0.0] * 5)
    cb.bucket_indicators["introductory"].extend([1.0] * 20)
    cb.bucket_indicators["interview"].extend([1.0] * 12 + [0.0] * 8)
    passed, indicators = verify_mechanism_activated(cb)
    assert passed is True, f"Expected gate PASS, got indicators={indicators}"
    assert indicators["gate_passed"] is True


def test_gate_fail_low_fraction():
    cb = DifficultyRewardCallback()
    cb.bucket_indicators["competition"].extend([1.0] * 5 + [0.0] * 95)
    cb.bucket_indicators["introductory"].extend([1.0] * 50)
    cb.bucket_indicators["interview"].extend([1.0] * 30)
    passed, indicators = verify_mechanism_activated(cb)
    assert passed is False


def test_gate_fail_missing_bucket():
    cb = DifficultyRewardCallback()
    cb.bucket_indicators["introductory"].extend([1.0] * 10)
    cb.bucket_indicators["interview"].extend([1.0] * 10)
    # No competition bucket
    passed, indicators = verify_mechanism_activated(cb)
    assert passed is False


if __name__ == "__main__":
    test_compute_fractions_empty()
    test_accumulate_and_compute()
    test_gate_pass()
    test_gate_fail_low_fraction()
    test_gate_fail_missing_bucket()
    print("All callback tests passed")
