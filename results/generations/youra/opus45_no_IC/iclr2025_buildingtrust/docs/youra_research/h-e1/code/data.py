"""Data loading and cluster assignment for TruthfulQA."""

from datasets import load_dataset
from config import DATASET_ID, CATEGORY_TO_CLUSTER, MIN_CLUSTER_SIZE


def load_truthfulqa_mc():
    """Load TruthfulQA with MC answers and categories merged."""
    mc_data = load_dataset(DATASET_ID, "multiple_choice", split="validation")
    gen_data = load_dataset(DATASET_ID, "generation", split="validation")

    question_to_category = {ex["question"]: ex["category"] for ex in gen_data}

    def add_category(example):
        cat = question_to_category.get(example["question"], "Misconceptions")
        return {"category": cat}

    dataset = mc_data.map(add_category)
    return dataset


def assign_clusters(dataset):
    """Add cluster_id column based on category mapping."""
    def map_cluster(example):
        category = example.get("category", "")
        for cat_key, cluster_id in CATEGORY_TO_CLUSTER.items():
            if cat_key.lower() in category.lower():
                return {"cluster_id": cluster_id}
        return {"cluster_id": 7}

    return dataset.map(map_cluster)


def validate_cluster_sizes(dataset, min_size=MIN_CLUSTER_SIZE):
    """Validate each cluster has minimum samples. Returns dict of cluster sizes."""
    cluster_counts = {}
    for i in range(1, 8):
        count = sum(1 for ex in dataset if ex["cluster_id"] == i)
        cluster_counts[i] = count
        if count < min_size:
            print(f"Warning: Cluster {i} has only {count} samples (min: {min_size})")
    return cluster_counts
