import json
import numpy as np
from datasets import load_dataset, Dataset
from config import H_M2Config


def load_variance_50_ids(profiling_json: str, k: int = 50) -> list:
    """Load top-k task_ids sorted by variance_i descending from H-E1 JSON."""
    with open(profiling_json) as f:
        data = json.load(f)

    # H-E1 JSON uses "top_ids" key (verified from actual file)
    if "top_ids" in data:
        ids = data["top_ids"][:k]
        return [int(x) for x in ids]

    # Fallback: recompute from problems dict
    problems = data.get("problems", {})
    sorted_ids = sorted(
        problems.keys(),
        key=lambda tid: problems[tid].get("variance_i", 0.0),
        reverse=True
    )
    return [int(tid) for tid in sorted_ids[:k]]


def load_random_50_ids(mbpp_train: Dataset, k: int = 50, seed: int = 42) -> list:
    """Sample k random task_ids from mbpp_train with fixed seed."""
    all_ids = [ex["task_id"] for ex in mbpp_train]
    rng = np.random.default_rng(seed)
    chosen = rng.choice(all_ids, size=k, replace=False)
    return [int(x) for x in chosen]


def build_subset(mbpp_train: Dataset, task_ids: list) -> Dataset:
    """Filter mbpp_train to rows with task_id in task_ids."""
    id_set = set(task_ids)
    subset = mbpp_train.filter(lambda x: x["task_id"] in id_set)
    assert len(subset) == len(task_ids), (
        f"Expected {len(task_ids)} problems, got {len(subset)}. "
        f"Some task_ids may not exist in the dataset split."
    )
    return subset


def load_mbpp_subsets(cfg: H_M2Config):
    """
    Load MBPP train split and build variance-50 and random-50 subsets.
    Returns: (variance_50_ds, random_50_ds, variance_50_ids, random_50_ids)
    """
    print(f"[dataset] Loading MBPP {cfg.mbpp_subset}/{cfg.mbpp_split}...")
    mbpp_train = load_dataset(cfg.mbpp_dataset_id, cfg.mbpp_subset, split=cfg.mbpp_split)
    print(f"[dataset] MBPP train: {len(mbpp_train)} problems")

    variance_50_ids = load_variance_50_ids(cfg.profiling_json, cfg.k)
    print(f"[dataset] Variance-50 IDs loaded: {len(variance_50_ids)} (top-{cfg.k} by variance_i)")

    random_50_ids = load_random_50_ids(mbpp_train, cfg.k, cfg.seed)
    print(f"[dataset] Random-50 IDs sampled: {len(random_50_ids)} (seed={cfg.seed})")

    variance_50_ds = build_subset(mbpp_train, variance_50_ids)
    random_50_ds = build_subset(mbpp_train, random_50_ids)

    print(f"[dataset] variance-50 subset: {len(variance_50_ds)} problems")
    print(f"[dataset] random-50 subset: {len(random_50_ds)} problems")

    return variance_50_ds, random_50_ds, variance_50_ids, random_50_ids
