# -*- coding: utf-8 -*-
"""
Stage 2: reliability cross-evaluation, batch 2 — 20 more items per set (60 total).

- Never overlaps batch 1 (selection_*_30.json ids are excluded).
- Same stratification as batch 1: (method x backbone) balance.
    * base 2 items/cell (9 cells = 18) + 1 in each of 2 cells = 20 per set.
    * the extra cells rotate per set -> per set method 7/7/6, backbone 7/7/6,
      and 20/20/20 for both across the 60-item total.
- Secondary: even topic spread (2 per topic per set) and mixed True/False labels.
- Outputs (name-free): eval_gui_D1_anchor.html (setKey=d1),
                       selection_manifest_batch2.csv, selection_anchor_60_batch2.json

Anonymity: annotators are referenced only by set letter (A/B/C primaries, anchor
for the fourth); input files are matched by name-free globs.
"""
import io, os, re, json, csv, glob, hashlib, random
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 202  # different from batch 1 (42)
METHODS = ['ai_scientist_v2', 'youra', 'mlragent']       # m0, m1, m2
BACKBONES = ['opus45', 'sonnet45', 'sonnet46']           # b0, b1, b2
SETS = ['A', 'B', 'C']
PER_SET = 20

# Per-set extra cells (2 each). Designed so each method/backbone gets +2 in total.
EXTRA_CELLS = {
    'A': [('ai_scientist_v2', 'opus45'), ('youra', 'sonnet45')],
    'B': [('youra', 'sonnet46'),         ('mlragent', 'opus45')],
    'C': [('mlragent', 'sonnet45'),      ('ai_scientist_v2', 'sonnet46')],
}

def load_payload(letter):
    with io.open(os.path.join(HERE, f'eval_gui_{letter}.html'), encoding='utf-8') as f:
        html = f.read()
    m = re.search(r'<script id="appdata" type="application/json">(.*?)</script>', html, re.S)
    return json.loads(m.group(1)), html

def load_results(letter):
    """Load a primary annotator's labels via a name-free glob on the set letter."""
    hits = sorted(glob.glob(os.path.join(HERE, f'labels_{letter.lower()}_*.json')))
    if not hits:
        raise FileNotFoundError(f"no result file for set {letter} (labels_{letter.lower()}_*.json)")
    data = json.load(io.open(hits[0], encoding='utf-8'))
    return {f"{r['file']}#{r['idx']}": r['human_assessment'] for r in data['results']}

def load_batch1_ids():
    """Batch-1 ids to exclude, via a name-free glob (matches any *_30.json manifest)."""
    ids = set()
    for p in sorted(glob.glob(os.path.join(HERE, 'selection_*_30.json'))):
        for it in json.load(io.open(p, encoding='utf-8'))['items']:
            ids.add(it['id'])
    return ids

def cell_targets(letter):
    t = {(m, b): 2 for m in METHODS for b in BACKBONES}
    for cell in EXTRA_CELLS[letter]:
        t[cell] += 1
    return t

def sample_set(letter, payload, results, exclude_ids):
    items = []
    for it in payload['items']:
        if it['id'] in exclude_ids:   # exclude batch 1
            continue
        it = dict(it)
        it['_assess'] = results.get(it['id'])
        items.append(it)
    by_cell = defaultdict(list)
    for it in items:
        by_cell[(it['method'], it['backbone'])].append(it)

    rng = random.Random(f"{SEED}:{letter}")
    targets = cell_targets(letter)
    chosen, chosen_ids = [], set()
    topic_count, label_count = Counter(), {True: 0, False: 0, None: 0}

    cells = [(m, b) for m in METHODS for b in BACKBONES]
    rng.shuffle(cells)
    for cell in cells:
        for _ in range(targets[cell]):
            cand = [it for it in by_cell[cell] if it['id'] not in chosen_ids]

            def score(it):
                return (-topic_count[it['topic']],                                    # prefer less-used topic
                        1 if label_count[it['_assess']] <= label_count[not it['_assess']] else 0,
                        rng.random())
            pick = max(cand, key=score)
            chosen.append(pick); chosen_ids.add(pick['id'])
            topic_count[pick['topic']] += 1; label_count[pick['_assess']] += 1
    return chosen

def main():
    b1 = load_batch1_ids()
    all_chosen = []
    for letter in SETS:
        payload, _ = load_payload(letter)
        results = load_results(letter)
        chosen = sample_set(letter, payload, results, b1)
        for it in chosen:
            it['_src_set'] = letter
            it['_src_evaluator'] = f'Annotator {letter}'
        all_chosen.extend(chosen)
        mc = Counter(it['method'] for it in chosen); bc = Counter(it['backbone'] for it in chosen)
        lc = Counter(it['_assess'] for it in chosen); tc = Counter(it['topic'] for it in chosen)
        print(f"[SET {letter}] n={len(chosen)} method={{ai:{mc['ai_scientist_v2']},yo:{mc['youra']},ml:{mc['mlragent']}}} "
              f"backbone={{op:{bc['opus45']},s45:{bc['sonnet45']},s46:{bc['sonnet46']}}} "
              f"T/F={lc.get(True,0)}/{lc.get(False,0)} items_per_topic={sorted(set(tc.values()))}")

    # Checks: zero overlap with batch 1, zero internal duplicates.
    ids = [it['id'] for it in all_chosen]
    print(f"\n[TOTAL 60] method={dict(Counter(it['method'] for it in all_chosen))} "
          f"backbone={dict(Counter(it['backbone'] for it in all_chosen))}")
    print(f"  overlap with batch 1: {len(set(ids)&b1)} (must be 0) / "
          f"internal duplicates: {len(ids)-len(set(ids))} (must be 0)")

    # manifest
    with io.open(os.path.join(HERE, 'selection_manifest_batch2.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['order', 'src_set', 'src_evaluator', 'id', 'method', 'backbone', 'judge', 'topic', 'original_assessment'])
        for i, it in enumerate(all_chosen, 1):
            w.writerow([i, it['_src_set'], it['_src_evaluator'], it['id'], it['method'], it['backbone'], it['judge'], it['topic'], it['_assess']])
    meta = [{'order': i + 1, 'src_set': it['_src_set'], 'src_evaluator': it['_src_evaluator'], 'id': it['id'],
             'file': it['file'], 'idx': it['idx'], 'method': it['method'], 'backbone': it['backbone'],
             'judge': it['judge'], 'topic': it['topic'], 'original_assessment': it['_assess']} for i, it in enumerate(all_chosen)]
    with io.open(os.path.join(HERE, 'selection_anchor_60_batch2.json'), 'w', encoding='utf-8') as f:
        json.dump({'count': len(meta), 'seed': SEED, 'batch': 2, 'items': meta}, f, ensure_ascii=False, indent=2)

    # GUI (reuse A template, swap payload + strip the AI overall-assessment field)
    _, template = load_payload('A')
    clean = [{k: v for k, v in it.items() if not k.startswith('_')} for it in all_chosen]
    bh = hashlib.md5((''.join(sorted(ids))).encode()).hexdigest()[:8]
    new_payload = {'buildId': f'split_d1_60i_{bh}', 'setLabel': 'Set D-1 · reliability cross-evaluation, additional 60 items (anchor)',
                   'setKey': 'd1', 'items': clean}
    new_json = json.dumps(new_payload, ensure_ascii=False)
    new_html = re.sub(r'<script id="appdata" type="application/json">.*?</script>',
                      lambda m: '<script id="appdata" type="application/json">' + new_json + '</script>',
                      template, count=1, flags=re.S)
    new_html = re.sub(r'\s*<div class="field"><div class="lab">AI judge overall assessment / confidence for this paper</div>.*?</div></div>',
                      '', new_html, count=1, flags=re.S)
    with io.open(os.path.join(HERE, 'eval_gui_D1_anchor.html'), 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"\nCreated: eval_gui_D1_anchor.html (buildId=split_d1_60i_{bh}, items={len(clean)}, setKey=d1)")
    print("Created: selection_manifest_batch2.csv, selection_anchor_60_batch2.json")

if __name__ == '__main__':
    main()
