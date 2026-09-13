"""
Data loading for H-E1 EXISTENCE PoC.
Loads HaluEval (pminervini/HaluEval) subsets and constructs binary labels
by interleaving right (label=0) and hallucinated (label=1) responses.
"""
import logging
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from datasets import load_dataset

from config import ExperimentConfig

logger = logging.getLogger(__name__)


@dataclass
class TaskData:
    """Per-task data container."""
    task_name: str
    premises: List[str]
    hypotheses: List[str]
    labels: np.ndarray  # shape (N,), binary {0, 1}
    n_examples: int


def load_task(task_name: str, config: ExperimentConfig) -> TaskData:
    """
    Load a single HaluEval task and construct binary-labeled pairs.

    HaluEval dataset structure:
        Each example has: premise_field, right_response_field, hallucinated_response_field
        We create 2N pairs: N non-hallucinated (label=0) + N hallucinated (label=1)

    Args:
        task_name: one of 'dialogue', 'qa', 'summarization'
        config: ExperimentConfig

    Returns:
        TaskData with 2N examples (labels balanced 50/50)
    """
    hf_config = config.hf_config_names[task_name]
    premise_col = config.premise_fields[task_name]
    right_col = config.hypothesis_right_fields[task_name]
    hall_col = config.hypothesis_hall_fields[task_name]

    logger.info(f"Loading HaluEval task='{task_name}' config='{hf_config}'...")
    ds = load_dataset(config.halueval_hf_id, hf_config, split="data")
    n_raw = len(ds)
    logger.info(f"  Loaded {n_raw} raw examples. Columns: {ds.column_names}")

    # Extract columns
    premises_raw: List[str] = ds[premise_col]
    right_responses: List[str] = ds[right_col]
    hall_responses: List[str] = ds[hall_col]

    # Construct interleaved binary dataset:
    # [right_0, hall_0, right_1, hall_1, ...] with labels [0, 1, 0, 1, ...]
    premises: List[str] = []
    hypotheses: List[str] = []
    labels_list: List[int] = []

    for p, r, h in zip(premises_raw, right_responses, hall_responses):
        # Non-hallucinated pair (label=0)
        premises.append(str(p))
        hypotheses.append(str(r))
        labels_list.append(0)
        # Hallucinated pair (label=1)
        premises.append(str(p))
        hypotheses.append(str(h))
        labels_list.append(1)

    labels = np.array(labels_list, dtype=np.int32)
    n_total = len(labels)
    n_pos = int((labels == 1).sum())
    n_neg = int((labels == 0).sum())

    logger.info(
        f"  Task '{task_name}': {n_total} pairs "
        f"(hallucinated={n_pos}, non-hallucinated={n_neg})"
    )
    assert abs(n_pos - n_neg) <= 1, f"Label imbalance: pos={n_pos}, neg={n_neg}"

    return TaskData(
        task_name=task_name,
        premises=premises,
        hypotheses=hypotheses,
        labels=labels,
        n_examples=n_total,
    )


def load_all_tasks(config: ExperimentConfig) -> List[TaskData]:
    """
    Load all 3 HaluEval tasks.

    Returns:
        List of 3 TaskData objects (dialogue, qa, summarization)
    """
    task_data_list = []
    for task_name in config.tasks:
        td = load_task(task_name, config)
        task_data_list.append(td)

    logger.info(
        f"Loaded {len(task_data_list)} tasks: "
        + ", ".join(f"{td.task_name}({td.n_examples})" for td in task_data_list)
    )
    return task_data_list
