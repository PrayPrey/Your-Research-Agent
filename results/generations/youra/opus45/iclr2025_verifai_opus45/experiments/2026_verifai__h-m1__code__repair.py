"""Repair pipeline for H-M1: Run granularity-controlled repair experiments."""

import json
import time
import os
from pathlib import Path
from tqdm import tqdm

from config import RepairConfig, ExperimentConfig, GRANULARITY_LEVELS, repair_config_to_experiment_config
from data import parse_error_info
from feedback import construct_repair_prompt
from executor import execute_and_verify
from model import CodeGenerator


def load_checkpoint(checkpoint_path: str) -> list[dict]:
    """Load partial results from checkpoint JSON.

    Args:
        checkpoint_path: Path to checkpoint file

    Returns:
        List of result dicts, or empty list if file missing
    """
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, "r") as f:
            return json.load(f)
    return []


def save_checkpoint(results: list[dict], checkpoint_path: str) -> None:
    """Persist current results to checkpoint file.

    Args:
        results: List of result dicts to save
        checkpoint_path: Path to checkpoint file
    """
    Path(checkpoint_path).parent.mkdir(parents=True, exist_ok=True)
    with open(checkpoint_path, "w") as f:
        json.dump(results, f, indent=2)


def run_repair_experiment(
    runtime_cases: list[dict],
    mbpp_index: dict[int, dict],
    generator: CodeGenerator,
    config: RepairConfig,
) -> list[dict]:
    """Run repair attempts for all runtime error cases across all granularity levels.

    For each (case, granularity) pair:
      1. Build repair prompt with specified granularity
      2. Generate repaired code via CodeGenerator
      3. Execute and verify (binary success)

    Args:
        runtime_cases: List of H-E1 runtime error cases
        mbpp_index: Dict mapping task_id to MBPP problem info
        generator: Loaded CodeGenerator instance
        config: RepairConfig with paths and settings

    Returns:
        List of result dicts: {task_id, granularity, repaired_code, success, execution_time}
    """
    # Load checkpoint for resume
    results = load_checkpoint(config.checkpoint_path)
    done_keys = {(r["task_id"], r["granularity"]) for r in results}

    total_attempts = len(runtime_cases) * len(GRANULARITY_LEVELS)
    completed = len(results)

    print(f"Starting repair experiment:")
    print(f"  Cases: {len(runtime_cases)}")
    print(f"  Granularity levels: {GRANULARITY_LEVELS}")
    print(f"  Total attempts: {total_attempts}")
    print(f"  Already completed: {completed}")
    print(f"  Remaining: {total_attempts - completed}")

    # Progress bar for remaining work
    pbar = tqdm(total=total_attempts, initial=completed, desc="Repair attempts")

    for case in runtime_cases:
        task_id = case["task_id"]
        task_info = mbpp_index.get(task_id)

        if task_info is None:
            print(f"Warning: Task {task_id} not found in MBPP index, skipping")
            continue

        # Parse error info from stderr
        error_info = parse_error_info(case.get("stderr") or "")
        buggy_code = case.get("generated_code", "")

        for granularity in GRANULARITY_LEVELS:
            # Skip if already done (checkpoint resume)
            if (task_id, granularity) in done_keys:
                continue

            # Construct repair prompt
            prompt = construct_repair_prompt(
                code=buggy_code,
                task_text=task_info["text"],
                error_info=error_info,
                granularity=granularity,
            )

            # Generate repair
            t0 = time.time()
            try:
                repaired_code = generator.generate(prompt)
            except Exception as e:
                print(f"Error generating repair for task {task_id} {granularity}: {e}")
                repaired_code = ""
            elapsed = time.time() - t0

            # Verify repair
            success = execute_and_verify(
                repaired_code,
                task_info["test_list"],
                timeout=config.execution_timeout,
            )

            # Record result
            results.append({
                "task_id": task_id,
                "granularity": granularity,
                "repaired_code": repaired_code,
                "success": success,
                "execution_time": elapsed,
            })
            pbar.update(1)

        # Save checkpoint after each case (5 results)
        save_checkpoint(results, config.checkpoint_path)

    pbar.close()
    print(f"Repair experiment completed: {len(results)} total results")

    return results
