"""Data loading for H-M4: Load H-E1 results and join with task texts."""

import sys
import json
from pathlib import Path

# Add h-e1/code to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-e1" / "code"))
from data import load_all_tasks


def load_e1_results(path: str = "../../h-e1/code/outputs/results.json") -> dict:
    """Load H-E1 results.json."""
    results_path = Path(__file__).parent / path
    with open(results_path) as f:
        return json.load(f)


def load_task_texts() -> dict:
    """Load task texts via h-e1 load_all_tasks(), indexed by task_id."""
    tasks = load_all_tasks()
    return {t["task_id"]: t for t in tasks}


def build_dataset(e1_results: dict, task_texts: dict) -> list:
    """Join per_task with task text on task_id."""
    records = []
    skipped = 0

    for row in e1_results["per_task"]:
        task = task_texts.get(row["task_id"])
        if task is None:
            skipped += 1
            continue
        records.append({
            "task_id": row["task_id"],
            "question": task["question"],
            "source_dataset": task["source_dataset"],
            "cluster_label": row["cluster_label"],
            "inversion_score": row["inversion_score"],
            "is_inverted": row["is_inverted"],
            "correct_logprob_norm": row["correct_logprob_norm"],
            "max_wrong_logprob_norm": row["max_wrong_logprob_norm"],
        })

    print(f"Joined {len(records)} tasks, skipped {skipped}")
    return records
