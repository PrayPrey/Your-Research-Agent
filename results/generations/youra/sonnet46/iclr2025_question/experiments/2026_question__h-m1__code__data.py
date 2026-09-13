"""
data.py — Score loading + label loading (extends h-e1/data.py pattern)
H-M1: Load pre-computed NLI scores from h-e1 results + reload HaluEval labels
"""
import json
import logging
from dataclasses import dataclass
from typing import Dict, List

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TaskScores:
    task_name: str
    scores_nxt3: np.ndarray   # shape (N, 3): [P(contra), P(neutral), P(entail)]
    labels_n: np.ndarray      # shape (N,), binary {0, 1}
    n_examples: int            # expected 20000


def load_h_e1_scores(results_path: str) -> Dict[str, np.ndarray]:
    """Load pre-computed (N,3) score matrices from h-e1_results.json.

    Returns: {task_name: np.ndarray shape (N,3)}
    Raises FileNotFoundError with instructive message if missing.
    """
    try:
        with open(results_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"H-E1 results file not found at: {results_path}\n"
            "Please ensure H-E1 experiment has completed and results are saved.\n"
            "Expected path: h-e1/results/h-e1_results.json"
        )

    scores_dict: Dict[str, np.ndarray] = {}
    for task_name, scores_list in data.items():
        arr = np.array(scores_list, dtype=np.float32)
        if arr.ndim != 2 or arr.shape[1] != 3:
            raise ValueError(
                f"Expected shape (N, 3) for task '{task_name}', got {arr.shape}"
            )
        scores_dict[task_name] = arr
        logger.info(f"Loaded scores for '{task_name}': shape={arr.shape}")

    return scores_dict


def load_halueval_labels(task_name: str, config) -> np.ndarray:
    """Reload HaluEval labels using same interleaving logic as h-e1/data.py.

    Mirrors h-e1 load_task interleaving:
      - ds = load_dataset(halueval_hf_id, hf_config_names[task_name], split="data")
      - interleave right_response(label=0) and hallucinated_response(label=1) per example
      - balanced 50/50

    Returns: np.ndarray shape (N,), binary labels
    """
    from datasets import load_dataset

    hf_config = config.hf_config_names[task_name]
    logger.info(f"Loading HaluEval labels for '{task_name}' (config={hf_config})...")

    ds = load_dataset(config.halueval_hf_id, hf_config, split="data")

    # Interleave: right(label=0) and hallucinated(label=1) per raw example
    # This mirrors h-e1/data.py load_task() logic exactly
    labels = []
    for _ in ds:
        labels.append(0)  # right_response
        labels.append(1)  # hallucinated_response

    labels_arr = np.array(labels, dtype=np.int32)
    logger.info(f"Loaded {len(labels_arr)} labels for '{task_name}' (balanced 50/50)")
    return labels_arr


def load_task_data(
    task_name: str,
    scores_dict: Dict[str, np.ndarray],
    config,
) -> TaskScores:
    """Combine scores and labels for one task. Verifies N matches."""
    if task_name not in scores_dict:
        raise KeyError(f"Task '{task_name}' not found in scores_dict. Available: {list(scores_dict.keys())}")

    scores_nxt3 = scores_dict[task_name]
    labels_n = load_halueval_labels(task_name, config)

    if len(scores_nxt3) != len(labels_n):
        raise ValueError(
            f"Shape mismatch for task '{task_name}': "
            f"scores has {len(scores_nxt3)} rows, labels has {len(labels_n)} entries"
        )

    return TaskScores(
        task_name=task_name,
        scores_nxt3=scores_nxt3,
        labels_n=labels_n,
        n_examples=len(scores_nxt3),
    )


def load_all_tasks(config) -> List[TaskScores]:
    """Load all 3 tasks. Verifies shapes (20000, 3) per task."""
    scores_dict = load_h_e1_scores(config.h_e1_results_path)

    task_data_list = []
    for task_name in config.tasks:
        task_data = load_task_data(task_name, scores_dict, config)

        # Verify expected shape
        if task_data.scores_nxt3.shape != (20000, 3):
            logger.warning(
                f"Task '{task_name}' has unexpected shape: {task_data.scores_nxt3.shape} "
                f"(expected (20000, 3))"
            )

        task_data_list.append(task_data)
        logger.info(
            f"Task '{task_name}': {task_data.n_examples} examples, "
            f"scores shape={task_data.scores_nxt3.shape}"
        )

    return task_data_list
