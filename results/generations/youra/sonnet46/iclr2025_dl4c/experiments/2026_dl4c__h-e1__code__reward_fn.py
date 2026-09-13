"""Reward functions for h-e1 prescreening: R_ratio, R_binary, S_term."""
import logging
from execution_sandbox import run_against_test_cases

logger = logging.getLogger(__name__)


def compute_r_ratio(tests_passed: int, T: int) -> float:
    """Compute ratio reward: tests_passed / T."""
    if T <= 0:
        return 0.0
    return tests_passed / T


def compute_r_binary(tests_passed: int, T: int) -> float:
    """Compute binary reward: 1.0 if all tests passed, 0.0 otherwise."""
    return float(tests_passed == T)


def compute_group_rewards(
    rollouts: list[str],
    test_cases: list[dict],
    reward_type: str = "ratio",
    timeout: float = 5.0,
) -> list[float]:
    """Compute reward scalars for one problem group (k rollouts).

    Args:
        rollouts: list of k code strings.
        test_cases: list of dicts with 'input' and 'output' keys.
        reward_type: "ratio" for R_ratio, "binary" for R_binary.
        timeout: seconds per test case.

    Returns:
        list of k reward floats.
    """
    T = len(test_cases)
    rewards = []
    for code in rollouts:
        tests_passed = run_against_test_cases(code, test_cases, timeout=timeout)
        if reward_type == "ratio":
            rewards.append(compute_r_ratio(tests_passed, T))
        elif reward_type == "binary":
            rewards.append(compute_r_binary(tests_passed, T))
        else:
            raise ValueError(f"Unknown reward_type: {reward_type}. Use 'ratio' or 'binary'.")
    return rewards


def compute_s_term(rollouts: list[str], test_cases: list[dict], timeout: float = 5.0) -> float:
    """Compute S_term: fraction of rollouts where tests_passed >= 1.

    Args:
        rollouts: list of k code strings.
        test_cases: list of dicts with 'input' and 'output' keys.
        timeout: seconds per test case.

    Returns:
        fraction in [0, 1].
    """
    if not rollouts:
        return 0.0
    k_pass = 0
    for code in rollouts:
        tests_passed = run_against_test_cases(code, test_cases, timeout=timeout)
        if tests_passed >= 1:
            k_pass += 1
    return k_pass / len(rollouts)
