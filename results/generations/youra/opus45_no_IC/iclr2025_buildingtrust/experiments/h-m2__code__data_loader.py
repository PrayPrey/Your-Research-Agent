"""Data loading and logit collection for H-M2 temperature scaling."""

import sys
from pathlib import Path
import numpy as np
from tqdm import tqdm

# Add h-e1 path for data/model imports (append, don't insert at 0)
_he1_path = str(Path(__file__).parent.parent.parent / "h-e1" / "code")
if _he1_path not in sys.path:
    sys.path.append(_he1_path)
from data import load_truthfulqa_mc, assign_clusters, validate_cluster_sizes
from model import score_choices
from config import N_FOLDS, MIN_SAMPLES_PER_FOLD, SEED


def collect_logits_by_cluster(dataset, model, tokenizer, device):
    """Run score_choices over dataset; group raw scores+labels by cluster_id.

    Returns:
        logits_by_cluster: dict[int, list[np.ndarray]] - ragged logits per question
        labels_by_cluster: dict[int, list[int]] - correct choice index per question
    """
    logits_by_cluster = {i: [] for i in range(1, 8)}
    labels_by_cluster = {i: [] for i in range(1, 8)}

    for row in tqdm(dataset, desc="Collecting logits"):
        cluster_id = row["cluster_id"]
        choices = row["mc1_targets"]["choices"]
        labels_list = row["mc1_targets"]["labels"]
        label = labels_list.index(1)

        scores = score_choices(model, tokenizer, row["question"], choices, device)
        logits_by_cluster[cluster_id].append(np.array(scores, dtype=np.float64))
        labels_by_cluster[cluster_id].append(label)

    return logits_by_cluster, labels_by_cluster


def pad_and_stack_cluster(logits_list, labels_list):
    """Pad ragged [n_choices_i] logit vectors to [N, max_choices] with -inf; stack labels [N]."""
    if not logits_list:
        return np.array([]), np.array([])

    max_choices = max(len(l) for l in logits_list)
    N = len(logits_list)

    padded = np.full((N, max_choices), -np.inf, dtype=np.float64)
    for i, logits in enumerate(logits_list):
        padded[i, :len(logits)] = logits

    return padded, np.array(labels_list, dtype=np.int64)


def stratified_kfold_splits(labels_by_cluster, n_folds=N_FOLDS, seed=SEED):
    """Per-cluster shuffled index split into n_folds groups (80/20 each fold).

    Returns:
        dict[int, list[tuple[np.ndarray, np.ndarray]]] - {cluster_id: [(train_idx, val_idx), ...]}
    """
    splits_by_cluster = {}

    for cluster_id, labels in labels_by_cluster.items():
        N = len(labels)
        if N == 0:
            splits_by_cluster[cluster_id] = []
            continue

        rng = np.random.RandomState(seed)
        idx = rng.permutation(N)
        fold_size = N // n_folds

        folds = []
        for k in range(n_folds):
            val_start = k * fold_size
            val_end = val_start + fold_size if k < n_folds - 1 else N
            val_idx = idx[val_start:val_end]
            train_idx = np.setdiff1d(idx, val_idx)

            if len(train_idx) < MIN_SAMPLES_PER_FOLD:
                print(f"Warning: Cluster {cluster_id} fold {k} train size {len(train_idx)} < {MIN_SAMPLES_PER_FOLD}")

            folds.append((train_idx, val_idx))

        splits_by_cluster[cluster_id] = folds

    return splits_by_cluster
