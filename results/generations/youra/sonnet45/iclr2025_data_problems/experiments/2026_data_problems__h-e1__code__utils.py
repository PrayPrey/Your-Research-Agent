"""
Utility functions for H-E1 pipeline.
Handles rate limiting, checkpointing, and logging.
"""
import json
import os
import time
import csv
from typing import Any, Callable, List, Optional


def exponential_backoff(
    func: Callable,
    *args,
    max_retries: int = 5,
    base_delay: float = 2.0,
    **kwargs,
) -> Any:
    """Call func(*args, **kwargs) with retry on exception. Raises after max_retries.

    Delays: 2, 4, 8, 16, 32 seconds before giving up.
    """
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            sleep_time = base_delay * (2 ** attempt)
            time.sleep(sleep_time)


def save_checkpoint(records: List[dict], checkpoint_path: str) -> None:
    """JSON dump records to checkpoint_path (overwrite). Non-serializable values are str()."""
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)

    def default_serializer(obj):
        return str(obj)

    with open(checkpoint_path, 'w') as f:
        json.dump(records, f, default=default_serializer)


def load_checkpoint(checkpoint_path: str) -> List[dict]:
    """Load checkpoint JSON. Returns [] if file not found."""
    if not os.path.exists(checkpoint_path):
        return []
    try:
        with open(checkpoint_path, 'r') as f:
            data = json.load(f)
        # Convert list to dict keyed by model_id if it's a list
        if isinstance(data, list):
            return {item['model_id']: item for item in data if 'model_id' in item}
        return data
    except (json.JSONDecodeError, KeyError):
        return {}


def log_dropout(model_id: str, stage: str, reason: str, log_path: str) -> None:
    """Append one row to dropout_log.csv (model_id, stage, reason)."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    file_exists = os.path.exists(log_path)
    with open(log_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['model_id', 'stage', 'reason'])
        writer.writerow([model_id, stage, reason])


def print_progress(stage: str, count: int, total: Optional[int] = None) -> None:
    """Print: '[stage] count/total' using print()."""
    if total is not None:
        print(f"[{stage}] {count}/{total}")
    else:
        print(f"[{stage}] {count}")
