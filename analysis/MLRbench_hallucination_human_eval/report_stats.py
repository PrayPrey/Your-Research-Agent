# -*- coding: utf-8 -*-
"""Compute every number for the n=90 reliability report and dump to JSON."""
import io, os, json, glob, math
from collections import Counter
from scipy.stats import fisher_exact, chi2_contingency

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report_stats.json')

def load_map(pattern):
    m = {}
    for p in sorted(glob.glob(os.path.join(HERE, pattern))):
        for r in json.load(io.open(p, encoding='utf-8'))['results']:
            m[f"{r['file']}#{r['idx']}"] = r['human_assessment']
    return m

def kstats(pairs):
    n = len(pairs)
    agree = sum(1 for a, b in pairs if a == b)
    po = agree / n
    p1 = sum(1 for a, _ in pairs if a) / n   # anchor True rate
    p2 = sum(1 for _, b in pairs if b) / n   # primary True rate
    pe = p1 * p2 + (1 - p1) * (1 - p2)
    k = (po - pe) / (1 - pe)
    se = math.sqrt(po * (1 - po) / n) / (1 - pe)
    return {'n': n, 'agree': agree, 'po': po, 'kappa': k,
            'ci_lo': k - 1.96 * se, 'ci_hi': k + 1.96 * se,
            'anchor_true': int(round(p1 * n)), 'primary_true': int(round(p2 * n))}

anchor1 = load_map('labels_d_*.json')    # batch 1 (30 items)
anchor2 = load_map('labels_d1_*.json')   # batch 2 (60 items)
anchor = dict(anchor1); anchor.update(anchor2)

prim = {}
for L, pat in [('A', 'labels_a_*.json'), ('B', 'labels_b_*.json'), ('C', 'labels_c_*.json')]:
    prim[L] = load_map(pat)

man = {}
for p in sorted(glob.glob(os.path.join(HERE, 'selection_*.json'))):
    for it in json.load(io.open(p, encoding='utf-8'))['items']:
        man[it['id']] = it

def rows_for(amap):
    out = []
    for L, om in prim.items():
        for i in amap:
            if i in om:
                m = man.get(i, {})
                out.append({'id': i, 'set': L, 'anchor': amap[i], 'primary': om[i],
                            'method': m.get('method', '?'), 'backbone': m.get('backbone', '?'),
                            'topic': m.get('topic', '?'), 'judge': m.get('judge', '?'),
                            'batch': 1 if i in anchor1 else 2})
    return out

rows = rows_for(anchor)
assert len(rows) == 90

R = {}
R['pooled'] = kstats([(r['anchor'], r['primary']) for r in rows])
R['batch1'] = kstats([(r['anchor'], r['primary']) for r in rows if r['batch'] == 1])
R['batch2'] = kstats([(r['anchor'], r['primary']) for r in rows if r['batch'] == 2])
R['pairs'] = {L: kstats([(r['anchor'], r['primary']) for r in rows if r['set'] == L]) for L in 'ABC'}

# subgroup agreement + composition of the 90
for dim in ('method', 'backbone'):
    d = {}
    for g in sorted(set(r[dim] for r in rows)):
        sub = [r for r in rows if r[dim] == g]
        d[g] = {'n': len(sub), 'agree': sum(1 for r in sub if r['anchor'] == r['primary'])}
    R[f'by_{dim}'] = d
R['youra_kappa'] = kstats([(r['anchor'], r['primary']) for r in rows if r['method'] == 'youra'])['kappa']

# composition: T/F by batch/set (primary labels), judge distribution among the 90
R['comp'] = {
    'primary_true_b1': sum(1 for r in rows if r['batch'] == 1 and r['primary']),
    'primary_true_b2': sum(1 for r in rows if r['batch'] == 2 and r['primary']),
    'judge_90': dict(Counter(r['judge'] for r in rows)),
}

# disagreements
dis = [r for r in rows if r['anchor'] != r['primary']]
R['dis'] = {
    'total': len(dis),
    'conservative': sum(1 for r in dis if r['primary'] and not r['anchor']),
    'liberal': sum(1 for r in dis if r['anchor'] and not r['primary']),
    'by_judge': dict(Counter(r['judge'] for r in dis)),
    'by_method': dict(Counter(r['method'] for r in dis)),
    'by_backbone': dict(Counter(r['backbone'] for r in dis)),
    'youra_dis': sum(1 for r in dis if r['method'] == 'youra'),
    'youra_dis_conservative': sum(1 for r in dis if r['method'] == 'youra' and r['primary'] and not r['anchor']),
    'list': [{'set': r['set'], 'batch': r['batch'], 'method': r['method'], 'backbone': r['backbone'],
              'topic': r['topic'].replace('iclr2025_', ''), 'judge': r['judge'],
              'primary': r['primary'], 'anchor': r['anchor']} for r in
             sorted(dis, key=lambda r: (r['batch'], r['set'], r['method']))],
}

# auxiliary stats
odds, pf = fisher_exact([[R['batch1']['agree'], R['batch1']['n'] - R['batch1']['agree']],
                         [R['batch2']['agree'], R['batch2']['n'] - R['batch2']['agree']]])
po = R['pooled']['po']
pi = (R['pooled']['anchor_true'] / 90 + R['pooled']['primary_true'] / 90) / 2
peg = 2 * pi * (1 - pi)
# agree/disagree x system: is auditor disagreement concentrated on any system?
_tab = [[R['by_method'][m]['agree'], R['by_method'][m]['n'] - R['by_method'][m]['agree']]
        for m in sorted(R['by_method'])]
chi2_m, p_m, dof_m, _ = chi2_contingency(_tab, correction=False)
R['aux'] = {'fisher_or': odds, 'fisher_p': pf, 'pabak': 2 * po - 1, 'ac1': (po - peg) / (1 - peg),
            'dis_by_method_chi2': chi2_m, 'dis_by_method_dof': int(dof_m), 'dis_by_method_p': p_m}

json.dump(R, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in R.items() if k != 'dis'}, ensure_ascii=False, indent=1))
print('\ndisagreements:', R['dis']['total'], '| conservative:', R['dis']['conservative'],
      '| by_judge:', R['dis']['by_judge'])
print('saved:', OUT)
