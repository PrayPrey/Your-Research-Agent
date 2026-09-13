"""
Load real CNN checkpoints from SANE ModelZoo (Schürholt et al. 2022, NeurIPS).
Source: HSG-AIML/SANE CIFAR-10 CNN sample zoo (public dataset, zenodo:13144018).
These are real CNN classifiers trained on CIFAR-10 with varying hyperparameters.
"""
import itertools
import json
import os
import random


def load_real_zoo(zoo_dir, tasks=None):
    """Load real zoo from pre-extracted SANE CNN checkpoints.

    zoo_dir should contain:
      - cifar10/cnn_seed*.pt (real checkpoints)
      - zoo_metadata.json
    Returns metadata: {task: [{path, acc, seed, task}, ...]}
    """
    if tasks is None:
        tasks = ['cifar10']

    meta_path = os.path.join(zoo_dir, 'zoo_metadata.json')
    if not os.path.exists(meta_path):
        raise FileNotFoundError(
            f"Real zoo metadata not found at {meta_path}. "
            "Download SANE CIFAR-10 CNN sample from zenodo:13144018 first."
        )

    with open(meta_path) as f:
        meta = json.load(f)

    # Filter to requested tasks
    filtered = {t: meta[t] for t in tasks if t in meta}

    # Verify files exist
    total = 0
    for task, models in filtered.items():
        existing = [m for m in models if os.path.exists(m['path'])]
        filtered[task] = existing
        total += len(existing)

    print(f"  Real zoo loaded: {total} CNN checkpoints from SANE ModelZoo (zenodo:13144018)")
    return filtered


def build_cnn_pairs(zoo_meta, min_pairs=500, seed=42, tasks=None):
    """Build same-task checkpoint pairs from real CNN zoo."""
    if tasks is None:
        tasks = list(zoo_meta.keys())

    rng = random.Random(seed)
    all_pairs = []

    for task in tasks:
        models = zoo_meta.get(task, [])
        for i, (ia, ib) in enumerate(itertools.combinations(range(len(models)), 2)):
            ma, mb = models[ia], models[ib]
            all_pairs.append({
                'pair_id': f'{task}_{i}',
                'task': task,
                'path_a': ma['path'],
                'path_b': mb['path'],
                'acc_a': ma.get('acc'),
                'acc_b': mb.get('acc'),
            })

    if len(all_pairs) > min_pairs * 3:
        per_task_target = min_pairs // max(len(tasks), 1) + 1
        sampled = []
        for task in tasks:
            task_pairs = [p for p in all_pairs if p['task'] == task]
            rng.shuffle(task_pairs)
            sampled.extend(task_pairs[:per_task_target])
        all_pairs = sampled

    rng.shuffle(all_pairs)
    for i, p in enumerate(all_pairs):
        p['pair_id'] = f"pair_{i:04d}"

    return all_pairs
