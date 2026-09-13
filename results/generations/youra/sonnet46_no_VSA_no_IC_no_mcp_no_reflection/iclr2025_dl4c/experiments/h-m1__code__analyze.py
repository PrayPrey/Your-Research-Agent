from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class BootstrapResult:
    mean_diff: float
    ci_lower: float
    ci_upper: float
    excludes_zero: bool


@dataclass
class MechanismResult:
    gate_satisfied: bool
    p1_humaneval_gap: float
    p1_ci_lower: float
    p1_satisfied: bool
    p2_policy_shift: bool
    p2_apps_allpass_ratio: float
    p2_apps_allpass_binary: float
    mechanism_confirmed: bool
    result: str  # "GATE_SATISFIED" | "GATE_FAILED"


def bootstrap_ci(
    values_a: List[float],
    values_b: List[float],
    n_bootstrap: int = 1000,
    ci_level: float = 0.95,
    seed: int = 42,
) -> BootstrapResult:
    """Paired bootstrap CI on mean(a) - mean(b)."""
    rng = np.random.default_rng(seed)
    a = np.array(values_a)
    b = np.array(values_b)
    n = len(a)

    boot_diffs = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        boot_diffs.append(a[idx].mean() - b[idx].mean())

    boot_diffs = np.array(boot_diffs)
    alpha = 1 - ci_level
    ci_lower = float(np.percentile(boot_diffs, 100 * alpha / 2))
    ci_upper = float(np.percentile(boot_diffs, 100 * (1 - alpha / 2)))
    mean_diff = float(a.mean() - b.mean())

    return BootstrapResult(
        mean_diff=mean_diff,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        excludes_zero=(ci_lower > 0),
    )


def verify_h_m1_mechanism(
    ratio_humaneval_pass1: float,
    binary_humaneval_pass1: float,
    ratio_apps_allpass: float,
    binary_apps_allpass: float,
    bootstrap_ci_lower: float,
    threshold_gap: float = 0.03,
) -> MechanismResult:
    """
    P1: HumanEval gap >= threshold AND CI lower > 0
    P2: ratio_apps_allpass <= binary_apps_allpass
    GATE = P1 AND P2
    """
    gap = ratio_humaneval_pass1 - binary_humaneval_pass1
    p1 = (gap >= threshold_gap) and (bootstrap_ci_lower > 0)
    p2 = ratio_apps_allpass <= binary_apps_allpass
    gate = p1 and p2

    return MechanismResult(
        gate_satisfied=gate,
        p1_humaneval_gap=gap,
        p1_ci_lower=bootstrap_ci_lower,
        p1_satisfied=p1,
        p2_policy_shift=p2,
        p2_apps_allpass_ratio=ratio_apps_allpass,
        p2_apps_allpass_binary=binary_apps_allpass,
        mechanism_confirmed=gate,
        result="GATE_SATISFIED" if gate else "GATE_FAILED",
    )


def check_ratio_degeneracy(rewards_per_group: List[float]) -> bool:
    """Returns True if ratio reward degenerated (all values 0.0 or 1.0)."""
    return all(r in (0.0, 1.0) for r in rewards_per_group)


def check_gradient_health(grad_norm: float, threshold: float = 10.0) -> bool:
    """Returns True if gradient norm is healthy."""
    return grad_norm < threshold


def compile_results(
    humaneval_curves: dict,
    mbpp_results: dict,
    apps_allpass: dict,
    per_problem_rates: dict,
    mechanism_result: MechanismResult,
    bootstrap_result: BootstrapResult,
) -> dict:
    """Merge all results into a single dict for JSON serialization."""
    return {
        "hypothesis": "H-M1",
        "checkpoint_results": {
            condition: {str(step): score for step, score in curves.items()}
            for condition, curves in humaneval_curves.items()
        },
        "final": {
            condition: {
                "humaneval_pass1": humaneval_curves[condition].get(1000, None),
                "mbpp_pass1": mbpp_results.get(condition),
                "apps_allpass_rate": apps_allpass.get(condition),
            }
            for condition in humaneval_curves
        },
        "per_problem_rates": {
            condition: rates for condition, rates in per_problem_rates.items()
        },
        "analysis": {
            "humaneval_gap": mechanism_result.p1_humaneval_gap,
            "bootstrap_ci_lower": bootstrap_result.ci_lower,
            "bootstrap_ci_upper": bootstrap_result.ci_upper,
            "ci_excludes_zero": bootstrap_result.excludes_zero,
            "p1_satisfied": mechanism_result.p1_satisfied,
            "p2_policy_shift": mechanism_result.p2_policy_shift,
            "gate_satisfied": mechanism_result.gate_satisfied,
            "result": mechanism_result.result,
        },
    }
