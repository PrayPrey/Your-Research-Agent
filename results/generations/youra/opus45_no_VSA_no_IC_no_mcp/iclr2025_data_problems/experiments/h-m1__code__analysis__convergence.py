"""Convergence analysis: steps-to-threshold, AUC, bootstrap comparison."""

import numpy as np

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LOSS_THRESHOLD, CHECKPOINT_TOKENS, BOOTSTRAP_N, BOOTSTRAP_PAIR


def steps_to_threshold(loss_history: list, threshold: float = None) -> float:
    """First step where loss < threshold, else inf."""
    if threshold is None:
        threshold = LOSS_THRESHOLD
    for entry in loss_history:
        if entry["loss"] < threshold:
            return entry["step"]
    return float("inf")


def convergence_auc(loss_history: list) -> float:
    """Trapezoidal AUC of loss curve (lower = faster convergence)."""
    tokens = np.array([d["tokens_seen"] for d in loss_history])
    losses = np.array([d["loss"] for d in loss_history])
    try:
        return float(np.trapezoid(losses, tokens))
    except AttributeError:
        return float(np.trapz(losses, tokens))


def loss_at_checkpoints(loss_history: list, token_checkpoints: list = None) -> dict:
    """Linear-interpolated loss at each token checkpoint."""
    if token_checkpoints is None:
        token_checkpoints = CHECKPOINT_TOKENS
    tokens = np.array([d["tokens_seen"] for d in loss_history])
    losses = np.array([d["loss"] for d in loss_history])
    return {tc: float(np.interp(tc, tokens, losses)) for tc in token_checkpoints}


def bootstrap_compare(values_a: list, values_b: list, n_boot: int = None, seed: int = 42) -> dict:
    """Bootstrap p-value (two-sided) + Cohen's d for mean difference."""
    if n_boot is None:
        n_boot = BOOTSTRAP_N

    rng = np.random.default_rng(seed)
    values_a = np.array(values_a)
    values_b = np.array(values_b)
    obs_diff = np.mean(values_a) - np.mean(values_b)

    boot_diffs = []
    for _ in range(n_boot):
        ra = rng.choice(values_a, size=len(values_a), replace=True)
        rb = rng.choice(values_b, size=len(values_b), replace=True)
        boot_diffs.append(np.mean(ra) - np.mean(rb))

    boot_diffs = np.array(boot_diffs)
    p_value = 2 * min((boot_diffs >= 0).mean(), (boot_diffs < 0).mean())
    pooled_std = np.sqrt((np.var(values_a, ddof=1) + np.var(values_b, ddof=1)) / 2)
    cohens_d = obs_diff / pooled_std if pooled_std > 0 else 0.0

    return {
        "p_value": float(p_value),
        "cohens_d": float(cohens_d),
        "mean_diff": float(obs_diff),
    }


def analyze_convergence(all_results: dict) -> dict:
    """Compute convergence metrics for all configs + pairwise comparison."""
    metrics = {}

    for config_id, r in all_results.items():
        lh = r["loss_history"]
        if not lh:
            continue
        metrics[config_id] = {
            "steps_to_threshold": steps_to_threshold(lh),
            "final_loss": lh[-1]["loss"],
            "convergence_auc": convergence_auc(lh),
            "loss_at_checkpoints": loss_at_checkpoints(lh),
        }

    # Pairwise: p50 (M1-C3) vs p0 (M1-C0)
    p50_id, p0_id = BOOTSTRAP_PAIR
    if p50_id in all_results and p0_id in all_results:
        p50_losses = [d["loss"] for d in all_results[p50_id]["loss_history"]]
        p0_losses = [d["loss"] for d in all_results[p0_id]["loss_history"]]
        metrics["p50_vs_p0"] = bootstrap_compare(p50_losses, p0_losses)

    return metrics
