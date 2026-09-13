import numpy as np
import torch
from torch import Tensor
from datasets import load_dataset
from sklearn.model_selection import train_test_split
from typing import Optional
import os

TASKS = ["boolq", "cb", "copa", "rte", "wic", "wsc"]


def load_superglue_data(tasks: list[str] = TASKS, max_samples_per_task: Optional[int] = None):
    """Load SuperGLUE tasks and return texts with task labels."""
    all_texts = []
    all_task_ids = []

    for task_idx, task in enumerate(tasks):
        ds = load_dataset("super_glue", task, trust_remote_code=True)

        if "train" in ds:
            split_data = ds["train"]
        elif "validation" in ds:
            split_data = ds["validation"]
        else:
            continue

        texts = []
        for ex in split_data:
            if task == "boolq":
                texts.append(f"{ex['question']} {ex['passage'][:200]}")
            elif task == "cb":
                texts.append(f"{ex['premise']} {ex['hypothesis']}")
            elif task == "copa":
                texts.append(f"{ex['premise']} {ex['choice1']} {ex['choice2']}")
            elif task == "rte":
                texts.append(f"{ex['premise']} {ex['hypothesis']}")
            elif task == "wic":
                texts.append(f"{ex['word']} {ex['sentence1']} {ex['sentence2']}")
            elif task == "wsc":
                text = ex.get("text", "")
                if not text:
                    span1 = ex.get("span1_text", "")
                    span2 = ex.get("span2_text", "")
                    text = f"{span1} {span2}"
                texts.append(text)

        if max_samples_per_task:
            texts = texts[:max_samples_per_task]

        all_texts.extend(texts)
        all_task_ids.extend([task_idx] * len(texts))

    return all_texts, np.array(all_task_ids)


def generate_synthetic_cluster_labels(task_ids: np.ndarray, num_clusters: int = 8, noise_ratio: float = 0.2, seed: int = 42) -> np.ndarray:
    """Generate cluster labels with controlled correlation to task IDs."""
    rng = np.random.RandomState(seed)
    n = len(task_ids)
    num_tasks = len(np.unique(task_ids))

    cluster_labels = (task_ids % num_clusters).copy()

    noise_mask = rng.random(n) < noise_ratio
    cluster_labels[noise_mask] = rng.randint(0, num_clusters, size=noise_mask.sum())

    return cluster_labels


def load_cluster_assignments(cluster_path: str) -> np.ndarray:
    """Load H-E1 cluster assignments from file."""
    if os.path.exists(cluster_path):
        return np.load(cluster_path)
    return None


def split_data(texts: list[str], task_ids: np.ndarray, cluster_labels: np.ndarray,
               train_ratio: float = 0.7, val_ratio: float = 0.15, seed: int = 42):
    """Split data into train/val/test with stratification."""
    n = len(texts)
    indices = np.arange(n)

    train_idx, temp_idx = train_test_split(
        indices, train_size=train_ratio, random_state=seed, stratify=task_ids
    )

    val_size = val_ratio / (1 - train_ratio)
    val_idx, test_idx = train_test_split(
        temp_idx, train_size=val_size, random_state=seed, stratify=task_ids[temp_idx]
    )

    return {
        "train": {"texts": [texts[i] for i in train_idx],
                  "task_ids": task_ids[train_idx],
                  "cluster_labels": cluster_labels[train_idx]},
        "val": {"texts": [texts[i] for i in val_idx],
                "task_ids": task_ids[val_idx],
                "cluster_labels": cluster_labels[val_idx]},
        "test": {"texts": [texts[i] for i in test_idx],
                 "task_ids": task_ids[test_idx],
                 "cluster_labels": cluster_labels[test_idx]},
    }
