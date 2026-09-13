"""Build MLP checkpoint pairs from the synthetic zoo."""
import itertools
import json
import os
import random


def build_mlp_pairs(zoo_meta, min_pairs=500, seed=42, tasks=None):
    """
    Build same-task same-architecture pairs from zoo metadata.

    zoo_meta: {task: [{path, acc, seed, task}, ...]}
    Returns list of {pair_id, task, path_a, path_b, acc_a, acc_b}
    """
    if tasks is None:
        tasks = list(zoo_meta.keys())

    rng = random.Random(seed)
    all_pairs = []

    for task in tasks:
        models = zoo_meta.get(task, [])
        combos = list(itertools.combinations(range(len(models)), 2))
        for i, (ia, ib) in enumerate(combos):
            ma, mb = models[ia], models[ib]
            all_pairs.append({
                'pair_id': f'{task}_{i}',
                'task': task,
                'path_a': ma['path'],
                'path_b': mb['path'],
                'acc_a': ma.get('acc'),
                'acc_b': mb.get('acc'),
            })

    # Stratified sample to min_pairs across tasks if we have more than enough
    if len(all_pairs) > min_pairs * 3:
        # Sample proportionally per task
        per_task_target = min_pairs // len(tasks) + 1
        sampled = []
        for task in tasks:
            task_pairs = [p for p in all_pairs if p['task'] == task]
            rng.shuffle(task_pairs)
            sampled.extend(task_pairs[:per_task_target])
        all_pairs = sampled

    rng.shuffle(all_pairs)
    # Reassign pair_ids after shuffle
    for i, p in enumerate(all_pairs):
        p['pair_id'] = f"pair_{i:04d}"

    return all_pairs


def save_pairs(pairs, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(pairs, f, indent=2)


def load_pairs(json_path):
    with open(json_path) as f:
        return json.load(f)
