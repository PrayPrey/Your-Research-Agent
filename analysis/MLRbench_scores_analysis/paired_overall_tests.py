# -*- coding: utf-8 -*-
"""Paired significance tests for Overall scores across the 30 matched cells.

Cell = (backbone, task); cell score = mean of the four judges' Overall scores.
All three systems share the same 30 cells (3 backbones x 10 tasks), so
YouRA-vs-baseline differences are tested with paired tests over cells:
a sign-flip permutation test on the mean difference (B=100,000, fixed seed)
and an exact two-sided sign test (ties excluded). Standard library only.
"""
import io, os, json, glob, random
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', 'results', 'evaluations', 'mlrbench_overall_score'))
OUT = os.path.join(HERE, 'paired_overall_tests_results.json')

SYSTEMS = ['youra', 'mlragent', 'ai_scientist_v2']
B = 100000

cells = {s: {} for s in SYSTEMS}
for s in SYSTEMS:
    acc = {}
    for p in glob.glob(os.path.join(ROOT, s, '*', '*', '*', 'review*.json')):
        parts = os.path.relpath(p, ROOT).split(os.sep)
        bb, task = parts[1], parts[3]
        d = json.load(io.open(p, encoding='utf-8'))
        acc.setdefault((bb, task), []).append(d['Overall']['score'])
    assert all(len(v) == 4 for v in acc.values()), s
    cells[s] = {c: sum(v) / 4 for c, v in acc.items()}

common = sorted(set(cells['youra']) & set(cells['mlragent']) & set(cells['ai_scientist_v2']))
assert len(common) == 30

rng = random.Random(42)
R = {'cells': len(common),
     'grand_mean': {s: sum(cells[s].values()) / 30 for s in SYSTEMS}}

def tests(a, b):
    diffs = [cells[a][c] - cells[b][c] for c in common]
    n = len(diffs)
    mean = sum(diffs) / n
    cnt = 0
    for _ in range(B):
        m = sum(d if rng.random() < 0.5 else -d for d in diffs) / n
        if abs(m) >= abs(mean) - 1e-12:
            cnt += 1
    pos = sum(1 for d in diffs if d > 0)
    neg = sum(1 for d in diffs if d < 0)
    m2 = pos + neg
    k = min(pos, neg)
    psign = min(1.0, 2 * sum(comb(m2, i) for i in range(k + 1)) / 2 ** m2)
    per_bb = {}
    for c, d in zip(common, diffs):
        per_bb.setdefault(c[0], []).append(d)
    return {'mean_diff': mean, 'perm_p': cnt / B,
            'wins': pos, 'losses': neg, 'ties': n - m2, 'sign_p': psign,
            'mean_diff_by_backbone': {bb: sum(v) / len(v) for bb, v in per_bb.items()}}

for a, b in [('youra', 'mlragent'), ('youra', 'ai_scientist_v2')]:
    R[f'{a}_vs_{b}'] = tests(a, b)

json.dump(R, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False, indent=1))
print('saved:', OUT)
