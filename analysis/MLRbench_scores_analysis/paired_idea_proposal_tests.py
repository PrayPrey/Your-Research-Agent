# -*- coding: utf-8 -*-
"""Paired tests for Idea/Proposal-stage scores, YouRA vs MLR-Agent.

Unit = task within a (stage, backbone) block; each score is the single
Gemini 3 Pro judge's rubric score. Differences are tested with a sign-flip
permutation test on the mean (B=20,000, fixed seed), Holm-corrected within
each block. Standard library only.
"""
import io, os, json, glob, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', 'results', 'evaluations', 'mlrbench_idea_proposal_score'))
OUT = os.path.join(HERE, 'paired_idea_proposal_tests_results.json')

SYSTEMS = {'youra': 'YouRA', 'mlragent': 'MLRBench'}
STAGES = ['idea', 'proposal']
BACKBONES = ['sonnet45', 'opus45']
B = 20000


def load(system, stage, bb):
    run = glob.glob(os.path.join(ROOT, SYSTEMS[system], stage, f'*{bb}_{stage}'))[0]
    out = {}
    for f in glob.glob(os.path.join(run, '*', stage, '*.json')):
        task = os.path.basename(os.path.dirname(os.path.dirname(f)))
        d = json.load(io.open(f, encoding='utf-8'))
        out[task] = {k: float(v['score']) for k, v in d.items() if isinstance(v, dict) and 'score' in v}
    return out


def mean_sd(xs):
    n = len(xs)
    m = sum(xs) / n
    sd = (sum((x - m) ** 2 for x in xs) / (n - 1)) ** 0.5 if n > 1 else 0.0
    return m, sd


def perm_p(diffs, rng):
    n = len(diffs)
    obs = sum(diffs) / n
    cnt = 0
    for _ in range(B):
        m = sum(d if rng.random() < 0.5 else -d for d in diffs) / n
        if abs(m) >= abs(obs) - 1e-12:
            cnt += 1
    return (cnt + 1) / (B + 1)


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj = [0.0] * len(pvals)
    running = 0.0
    m = len(pvals)
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * pvals[i])
        adj[i] = min(1.0, running)
    return adj


rng = random.Random(42)
R = {}
for stage in STAGES:
    for bb in BACKBONES:
        Y = load('youra', stage, bb)
        M = load('mlragent', stage, bb)
        common = sorted(set(Y) & set(M))
        metrics = [k for k in next(iter(Y.values()))]
        block = {'n_youra': len(Y), 'n_mlragent': len(M), 'n_paired': len(common), 'metrics': {}}
        pv = []
        for met in metrics:
            y = [Y[t][met] for t in Y if met in Y[t]]
            x = [M[t][met] for t in M if met in M[t]]
            diffs = [Y[t][met] - M[t][met] for t in common if met in Y[t] and met in M[t]]
            ym, ysd = mean_sd(y)
            xm, xsd = mean_sd(x)
            p = perm_p(diffs, rng)
            pv.append(p)
            block['metrics'][met] = {
                'youra_mean': ym, 'youra_sd': ysd,
                'mlragent_mean': xm, 'mlragent_sd': xsd,
                'paired_mean_diff': sum(diffs) / len(diffs),
                'wins': sum(1 for d in diffs if d > 0),
                'losses': sum(1 for d in diffs if d < 0),
                'perm_p': p,
            }
        for met, padj in zip(metrics, holm(pv)):
            block['metrics'][met]['holm_p'] = padj
        R[f'{stage}_{bb}'] = block

json.dump(R, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for key, block in R.items():
    print(f"== {key}")
    for met, v in block['metrics'].items():
        flag = '*' if v['holm_p'] < 0.05 else ''
        print(f"  {met:18s} YouRA {v['youra_mean']:.2f}±{v['youra_sd']:.2f}  MLR-Agent {v['mlragent_mean']:.2f}±{v['mlragent_sd']:.2f}  "
              f"diff {v['paired_mean_diff']:+.2f}  perm_p {v['perm_p']:.3f}  holm_p {v['holm_p']:.3f} {flag}")
print('saved:', OUT)
