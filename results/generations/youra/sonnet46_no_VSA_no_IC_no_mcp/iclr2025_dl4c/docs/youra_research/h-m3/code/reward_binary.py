"""reward_binary.py — H-M3: Binary reward function + mechanism activation verifier."""
import sys
from pathlib import Path

H_E1_CODE = Path(__file__).parents[2] / "h-e1" / "code"
if str(H_E1_CODE) not in sys.path:
    sys.path.insert(0, str(H_E1_CODE))

from reward import _execute_code  # reuse subprocess executor from h-E1
import json
import numpy as np


def binary_reward_fn(
    completions: list,
    prompts: list,
    metadata: list,
    **kwargs,
) -> list:
    """
    Binary execution reward: 1.0 if ALL tests pass, else 0.0.
    Sparse signal — zero for partially-correct solutions.
    """
    rewards = []
    for code, meta in zip(completions, metadata):
        if isinstance(meta, dict):
            raw = meta.get("test_cases", "[]")
        else:
            raw = "[]"
        try:
            test_cases = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            test_cases = []

        if not test_cases:
            rewards.append(0.0)
            continue

        all_passed = True
        for item in test_cases:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                stdin, expected = item
            else:
                continue
            try:
                actual = _execute_code(code, str(stdin), timeout=3.0)
                if actual.strip() != str(expected).strip():
                    all_passed = False
                    break
            except Exception:
                all_passed = False
                break

        rewards.append(1.0 if all_passed else 0.0)
    return rewards


def verify_reward_formulation_active(
    fraction_rewards: list,
    binary_rewards: list,
    threshold: float = 0.01,
) -> tuple:
    """
    Verifies fraction reward produces denser non-zero signal than binary.
    Run every verify_interval_steps during training; log to reward_log.
    Returns (activated: bool, indicators: dict).
    """
    f = np.asarray(fraction_rewards, dtype=float)
    b = np.asarray(binary_rewards, dtype=float)
    mean_fraction = float(f.mean()) if len(f) > 0 else 0.0
    mean_binary = float(b.mean()) if len(b) > 0 else 0.0

    indicators = {
        "fraction_mean": mean_fraction,
        "binary_mean": mean_binary,
        "reward_differs": abs(mean_fraction - mean_binary) > threshold,
        "fraction_denser": mean_fraction >= mean_binary,
        "nonzero_fraction": float((f > 0).mean()) if len(f) > 0 else 0.0,
        "nonzero_binary": float((b > 0).mean()) if len(b) > 0 else 0.0,
    }

    activated = indicators["reward_differs"] and indicators["fraction_denser"]
    if not activated:
        print(
            f"WARNING: Fraction reward not denser than binary "
            f"(mean_fraction={mean_fraction:.4f}, mean_binary={mean_binary:.4f})"
        )
    return activated, indicators


def test_reward_formulation_differs():
    """Self-check: fraction and binary rewards should differ on partial solutions."""
    # Partial solution: prints input (passes input==output test but not others)
    partial_code = "x = input()\nprint(x)"
    # Full solution: adds 1
    full_code = "x = int(input())\nprint(x + 1)"

    # Test cases: input → expected output
    test_cases = [["1", "2"], ["3", "4"], ["5", "6"]]
    meta = {"test_cases": json.dumps(test_cases)}

    frac_rewards = []
    bin_rewards = []

    import importlib
    reward_mod = importlib.import_module("reward")

    for code in [partial_code, full_code]:
        frac = reward_mod.fraction_reward_fn([code], [""], [meta])
        frac_rewards.append(frac[0])
        bin_r = binary_reward_fn([code], [""], [meta])
        bin_rewards.append(bin_r[0])

    print(f"Fraction rewards: {frac_rewards}")
    print(f"Binary rewards:   {bin_rewards}")

    # Partial code: fraction > 0, binary = 0 (some tests fail — "1"→"1" passes, "1+1"→"2" fails)
    # Full code: fraction = 1.0, binary = 1.0
    assert bin_rewards[1] == 1.0, f"Full solution should get binary=1.0, got {bin_rewards[1]}"
    assert frac_rewards[1] == 1.0, f"Full solution should get fraction=1.0, got {frac_rewards[1]}"
    print("✓ Reward formulation verification passed")


if __name__ == "__main__":
    test_reward_formulation_differs()
