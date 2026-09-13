# -*- coding: utf-8 -*-
"""Precision-corrected hallucination counts per system + pairwise bootstrap tests.

Corrected estimate = (total automated flags, union over 4 judges at instance
level, 30 papers per system) x (human-validated per-system precision, n=90).
Pairwise p-values: bootstrap over the 30 papers (with replacement) plus
binomial resampling of the precision, B=20000, seed=42.
"""
import io, os, json, glob, random
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', 'results', 'evaluations', 'mlrbench_hallucination'))
OUT = os.path.join(HERE, 'corrected_counts_results.json')

PREC = {'youra': (68, 90), 'mlragent': (70, 90), 'ai_scientist_v2': (65, 90)}

per_paper = defaultdict(Counter)  # method -> (backbone, topic) -> flag count
for m in PREC:
    for p in sorted(glob.glob(os.path.join(ROOT, m, '*', '*', '*', 'review_hallucination*.json'))):
        parts = os.path.relpath(p, ROOT).split(os.sep)
        bb, topic = parts[1], parts[3]
        d = json.load(io.open(p, encoding='utf-8'))
        per_paper[m][(bb, topic)] += len(d.get('hallucinations') or [])

R = {}
for m in PREC:
    v = list(per_paper[m].values())
    assert len(v) == 30, (m, len(v))
    k, n = PREC[m]
    tot = sum(v)
    R[m] = {'papers': 30, 'flags': tot, 'precision': k / n,
            'corrected': tot * k / n, 'corrected_per_paper': tot * k / n / 30}

rng = random.Random(42)
B = 20000

def draw(m):
    v = [per_paper[m][key] for key in sorted(per_paper[m])]
    k, n = PREC[m]
    tot = sum(rng.choice(v) for _ in range(30))
    ph = sum(1 for _ in range(n) if rng.random() < k / n) / n
    return tot * ph

pairs = [('youra', 'mlragent'), ('youra', 'ai_scientist_v2'), ('ai_scientist_v2', 'mlragent')]
diffs = {p: [] for p in pairs}
for _ in range(B):
    d = {m: draw(m) for m in PREC}
    for a, c in pairs:
        diffs[(a, c)].append(d[a] - d[c])

R['pairwise'] = {}
for (a, c), ds in diffs.items():
    ds.sort()
    p2 = 2 * min(sum(1 for x in ds if x >= 0) / B, sum(1 for x in ds if x <= 0) / B)
    R['pairwise'][f'{a}_vs_{c}'] = {'mean_diff': sum(ds) / B,
                                    'ci95': [ds[int(0.025 * B)], ds[int(0.975 * B)]],
                                    'p_two_sided': p2}

json.dump(R, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False, indent=1))
print('saved:', OUT)
