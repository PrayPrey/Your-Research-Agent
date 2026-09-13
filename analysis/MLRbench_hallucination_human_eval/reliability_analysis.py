# -*- coding: utf-8 -*-
"""
Inter-rater reliability analysis for the hallucination human evaluation.

An anchor annotator re-judged a stratified overlap of the items originally
labeled by three primary annotators (A, B, C): 10 items shared with each,
30 per completed batch. This script joins the anchor's labels with each
primary annotator's labels by item id (= file#idx) and reports, per pair and
pooled:
  - percent agreement
  - Cohen's kappa (two-rater, binary)
It also prints per-subgroup (method / backbone) agreement.

Anonymity: every annotator is referred to only by an anonymous label
(Annotator A/B/C, Anchor); input files are matched by set-letter globs and
carry no personal names.

Item ids such as 'results/evaluations/...#idx' are repository-root-relative
paths into results/evaluations/mlrbench_hallucination/. Labels are joined by
id only — those files are never opened — so this script runs from this
directory without further setup.

Inputs:
  PRIMARY_GLOBS : one results file per primary annotator (sets a / b / c)
  ANCHOR_GLOB   : anchor annotator results (set d), auto-merged across batches
  MANIFEST_GLOB : stratified-sampling manifests (batch 1 + 2) for subgroup dims
Output: console report + reliability_result.json (pooled n / agreement / kappa)
"""
import io, os, json, glob
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))

# Anonymous label -> input glob. Only the anonymous set letters a/b/c/d are
# used; no annotator names appear in filenames or code.
PRIMARY_GLOBS = [('Annotator A', 'labels_a_*.json'),
                 ('Annotator B', 'labels_b_*.json'),
                 ('Annotator C', 'labels_c_*.json')]
ANCHOR_GLOB = 'labels_d*.json'        # anchor annotator (set d), all batches merged
MANIFEST_GLOB = 'selection_*.json'    # stratified-sampling manifests (batch 1 + 2)

def load_map(pattern):
    """Merge every results file matching `pattern` into {id: human_assessment}."""
    m = {}
    for p in sorted(glob.glob(os.path.join(HERE, pattern))):
        data = json.load(io.open(p, encoding='utf-8'))
        for r in data['results']:
            m[f"{r['file']}#{r['idx']}"] = r['human_assessment']
    return m

def cohen_kappa(pairs):
    """pairs: list of (rater1_bool, rater2_bool). Returns (p_observed, kappa, n_agree)."""
    n = len(pairs)
    if n == 0:
        return None, None, None
    agree = sum(1 for a, b in pairs if a == b)
    po = agree / n
    p1t = sum(1 for a, _ in pairs if a) / n
    p2t = sum(1 for _, b in pairs if b) / n
    pe = p1t * p2t + (1 - p1t) * (1 - p2t)
    kappa = float('nan') if pe == 1 else (po - pe) / (1 - pe)
    return po, kappa, agree

def interpret(k):
    """Landis & Koch (1977) agreement bands."""
    if k != k:
        return 'undefined (one rater constant)'
    if k < 0:
        return 'poor (<0)'
    if k < .21:
        return 'slight (0.01-0.20)'
    if k < .41:
        return 'fair (0.21-0.40)'
    if k < .61:
        return 'moderate (0.41-0.60)'
    if k < .81:
        return 'substantial (0.61-0.80)'
    return 'almost perfect (0.81-1.00)'

def load_manifest():
    """Merge all sampling manifests into {id: item} for method/backbone lookup."""
    man = {}
    for p in sorted(glob.glob(os.path.join(HERE, MANIFEST_GLOB))):
        for it in json.load(io.open(p, encoding='utf-8'))['items']:
            man[it['id']] = it
    return man

def main():
    anchor = load_map(ANCHOR_GLOB)
    if not anchor:
        print(f"[waiting] no anchor results match '{ANCHOR_GLOB}' yet.\n"
              f" -> place the anchor annotator's exported JSON in this folder and rerun.")
        return
    manifest = load_manifest()
    print(f"Anchor items loaded (merged): {len(anchor)}\n")

    all_pairs = []
    for label, pattern in PRIMARY_GLOBS:
        omap = load_map(pattern)
        common = [i for i in anchor if i in omap]
        pairs = [(anchor[i], omap[i]) for i in common]
        all_pairs += pairs
        po, k, agree = cohen_kappa(pairs)
        print(f"[Anchor vs {label}]  n={len(pairs)}  agree={agree}/{len(pairs)}  "
              f"agreement={po*100:.1f}%  kappa={k:.3f}  -> {interpret(k)}")
        # Subgroup (method / backbone) agreement, if a manifest is available.
        if manifest:
            for dim in ('method', 'backbone'):
                sub, tot = Counter(), Counter()
                for i in common:
                    g = manifest.get(i, {}).get(dim, '?')
                    tot[g] += 1
                    sub[g] += (anchor[i] == omap[i])
                cells = "  ".join(f"{g}:{sub[g]}/{tot[g]}" for g in sorted(tot))
                print(f"      by {dim}: {cells}")

    po, k, agree = cohen_kappa(all_pairs)
    print(f"\n[POOLED {len(all_pairs)}]  agree={agree}/{len(all_pairs)}  "
          f"agreement={po*100:.1f}%  kappa={k:.3f}  -> {interpret(k)}")

    out = {'pooled': {'n': len(all_pairs), 'agreement': po, 'kappa': k}}
    with io.open(os.path.join(HERE, 'reliability_result.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nSaved: reliability_result.json")

if __name__ == '__main__':
    main()
