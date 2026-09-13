"""Data loader for H-M3: Load H-E1 execution results."""

import json
import os
from typing import Dict, List, Tuple

from config import ExperimentConfig


def load_he1_results(config: ExperimentConfig) -> Tuple[List[dict], List[dict]]:
    """Load H-E1 execution results from rl/dpo_execution_results.json.

    Args:
        config: Experiment configuration with paths

    Returns:
        (rl_results, dpo_results) - lists of execution result dicts
        Each dict: {task_id, model, sample_idx, completion, error_trace, status}
    """
    rl_path = os.path.join(config.he1_results_dir, "rl_execution_results.json")
    dpo_path = os.path.join(config.he1_results_dir, "dpo_execution_results.json")

    # Validate paths exist
    if not os.path.exists(rl_path):
        raise FileNotFoundError(f"RL results not found: {rl_path}")
    if not os.path.exists(dpo_path):
        raise FileNotFoundError(f"DPO results not found: {dpo_path}")

    with open(rl_path, "r") as f:
        rl_results = json.load(f)

    with open(dpo_path, "r") as f:
        dpo_results = json.load(f)

    print(f"Loaded {len(rl_results)} RL samples, {len(dpo_results)} DPO samples")

    return rl_results, dpo_results


def extract_failures(results: List[dict]) -> List[dict]:
    """Filter to failed samples only (status == 'fail').

    Args:
        results: List of execution result dicts

    Returns:
        Filtered list containing only failures
    """
    failures = [r for r in results if r.get("status") == "fail"]
    return failures


def load_he1_metrics(config: ExperimentConfig) -> dict:
    """Load H-E1 metrics.json for validation comparison.

    Args:
        config: Experiment configuration with paths

    Returns:
        Dict of H-E1 metrics (chi2, cramers_v, etc.)
    """
    metrics_path = os.path.join(config.he1_results_dir, "metrics.json")

    if not os.path.exists(metrics_path):
        raise FileNotFoundError(f"H-E1 metrics not found: {metrics_path}")

    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    return metrics


def validate_data_integrity(
    rl_failures: List[dict],
    dpo_failures: List[dict],
    config: ExperimentConfig,
) -> bool:
    """Validate loaded data matches expected H-E1 counts.

    Args:
        rl_failures: RL failure samples
        dpo_failures: DPO failure samples
        config: Configuration with expected counts

    Returns:
        True if counts match expectations
    """
    rl_count = len(rl_failures)
    dpo_count = len(dpo_failures)

    rl_match = rl_count == config.expected_rl_failures
    dpo_match = dpo_count == config.expected_dpo_failures

    if not rl_match:
        print(f"WARNING: RL failures {rl_count} != expected {config.expected_rl_failures}")
    if not dpo_match:
        print(f"WARNING: DPO failures {dpo_count} != expected {config.expected_dpo_failures}")

    return rl_match and dpo_match
