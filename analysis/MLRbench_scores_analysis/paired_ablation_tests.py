# -*- coding: utf-8 -*-
"""Paired tests for YouRA component-ablation Overall drops.

Cell = (backbone, task); cell score = mean of the four judges' Overall scores.
For each component, the drop is full YouRA minus the matching ablated run.
The script tests whether each component removal lowers Overall over the
30 matched cells (3 backbones x 10 tasks), then tests whether component
drop sizes differ from one another. Standard library only.
"""
import csv
import io
import json
import os
import random
from itertools import combinations
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
FULL_CSV = os.path.join(HERE, 'overall', 'table1_task_level_scores.csv')
ABLATION_ROOT = os.path.join(
    REPO, 'results', 'evaluations', 'mlrbench_overall_score', 'youra_ablation_study'
)
OUT = os.path.join(HERE, 'paired_ablation_tests_results.json')

BACKBONES = {
    'sonnet45': 'Sonnet 4.5',
    'opus45': 'Opus 4.5',
    'sonnet46': 'Sonnet 4.6',
}
COMPONENTS = {
    'no_mcp': 'MCP',
    'no_reflection': 'Reflection',
    'no_VSA': 'VSA',
    'no_IC': 'Independent Controller',
}
B = 100000


def holm_adjust(pairs):
    """Return Holm-adjusted p-values for [(name, p), ...]."""
    ordered = sorted(pairs, key=lambda x: x[1])
    out = {}
    running = 0.0
    m = len(ordered)
    for i, (name, p) in enumerate(ordered):
        adj = min(1.0, p * (m - i))
        running = max(running, adj)
        out[name] = running
    return out


def sign_test(diffs):
    pos = sum(1 for d in diffs if d > 1e-12)
    neg = sum(1 for d in diffs if d < -1e-12)
    ties = len(diffs) - pos - neg
    n = pos + neg
    k = min(pos, neg)
    p = min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0
    return pos, neg, ties, p


def perm_test(diffs, seed=42):
    rng = random.Random(seed)
    obs = abs(sum(diffs) / len(diffs))
    cnt = 0
    for _ in range(B):
        mean = sum(d if rng.random() < 0.5 else -d for d in diffs) / len(diffs)
        if abs(mean) >= obs - 1e-12:
            cnt += 1
    return cnt / B


def read_full_scores():
    full = {}
    with io.open(FULL_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['system'] == 'YouRA':
                full[(row['backbone'], row['task'])] = float(row['overall_task_mean'])
    return full


def read_ablation_lane(lane):
    acc = {}
    root = os.path.join(ABLATION_ROOT, lane)
    for dirpath, _, names in os.walk(root):
        for name in names:
            if not name.startswith('review_') or not name.endswith('.json'):
                continue
            if 'hallucination' in name:
                continue
            path = os.path.join(dirpath, name)
            data = json.load(io.open(path, encoding='utf-8'))
            overall = data['Overall']['score'] if isinstance(data['Overall'], dict) else data['Overall']
            task = os.path.basename(dirpath)
            acc.setdefault(task, []).append(float(overall))
    return {task: sum(vals) / len(vals) for task, vals in acc.items()}


def main():
    full = read_full_scores()
    drops = {component: {} for component in COMPONENTS}

    for bb_key, bb_name in BACKBONES.items():
        for component in COMPONENTS:
            lane = f'{bb_key}_{component}'
            for task, score in read_ablation_lane(lane).items():
                cell = (bb_name, task)
                if cell in full:
                    drops[component][cell] = full[cell] - score

    removal = {}
    for component, label in COMPONENTS.items():
        values = [drops[component][cell] for cell in sorted(drops[component])]
        pos, neg, ties, p_sign = sign_test(values)
        per_bb = {}
        for bb_name in BACKBONES.values():
            bb_values = [v for (bb, _), v in drops[component].items() if bb == bb_name]
            per_bb[bb_name] = sum(bb_values) / len(bb_values)
        removal[component] = {
            'label': label,
            'n': len(values),
            'mean_drop': sum(values) / len(values),
            'perm_p': perm_test(values),
            'wins_losses_ties': [pos, neg, ties],
            'sign_p': p_sign,
            'drop_by_backbone': per_bb,
        }
    removal_holm = holm_adjust([(c, r['perm_p']) for c, r in removal.items()])
    for component, p in removal_holm.items():
        removal[component]['holm_perm_p'] = p

    contrasts = {}
    for a, b in combinations(COMPONENTS, 2):
        common = sorted(set(drops[a]) & set(drops[b]))
        diffs = [drops[a][cell] - drops[b][cell] for cell in common]
        pos, neg, ties, p_sign = sign_test(diffs)
        key = f'{a}_minus_{b}'
        contrasts[key] = {
            'labels': [COMPONENTS[a], COMPONENTS[b]],
            'n': len(diffs),
            'mean_drop_difference': sum(diffs) / len(diffs),
            'perm_p': perm_test(diffs),
            'wins_losses_ties': [pos, neg, ties],
            'sign_p': p_sign,
        }
    contrast_holm = holm_adjust([(c, r['perm_p']) for c, r in contrasts.items()])
    for contrast, p in contrast_holm.items():
        contrasts[contrast]['holm_perm_p'] = p

    result = {'cells': 30, 'removal_tests': removal, 'drop_size_contrasts': contrasts}
    json.dump(result, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(result, ensure_ascii=False, indent=1))
    print('saved:', OUT)


if __name__ == '__main__':
    main()
