"""Load ContractEval dataset (JSONL format)."""
import json
from pathlib import Path


def load_contracteval(jsonl_path: str) -> dict[str, dict]:
    """Load ContractEval from JSONL file.

    Returns {task_id: task_dict} where each task has:
      task_id, entry_point, canonical_solution, canonical_solution_with_contract,
      contract, contract_violating_test, base_input, plus_input
    """
    tasks = {}
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            task = json.loads(line)
            task_id = task["task_id"]
            tasks[task_id] = task
    return tasks


def get_tasks_with_cvts(tasks: dict[str, dict]) -> dict[str, dict]:
    """Return only tasks that have contract-violating test inputs."""
    return {
        tid: t for tid, t in tasks.items()
        if t.get("contract_violating_test")
    }


def get_z3_tractable_ids(tasks: dict[str, dict]) -> set[str]:
    """Return task IDs that have non-empty contract (proxy for Z3-tractable tasks)."""
    return {
        tid for tid, t in tasks.items()
        if t.get("contract", "").strip()
    }
