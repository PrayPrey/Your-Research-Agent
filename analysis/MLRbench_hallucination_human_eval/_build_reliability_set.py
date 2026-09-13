# -*- coding: utf-8 -*-
"""
Stage 1: build the inter-rater reliability cross-evaluation set (batch 1).

- Reads the embedded payloads (90 items each) of the primary annotators' GUIs
  (eval_gui_A/B/C.html) and their result files, and selects 10 items from each
  set (30 total) by stratified sampling.
- Stratification: one item from each of the 9 (method x backbone) cells + 1 extra
  = 10 items per set.
    * per set: method 3/3/4, backbone 3/3/4 (as balanced as possible)
    * the extra cell rotates across sets, so the 30-item total is fully balanced:
      method 10/10/10, backbone 10/10/10.
- Secondary goals: topic diversity + True/False label balance (so kappa is meaningful).
- Outputs (name-free, so no annotator identity is embedded):
    eval_gui_D_anchor.html   (30-item blind GUI for the anchor annotator; reuses the A template)
    selection_manifest.csv   (provenance/conditions/original label of the 30 items)
    selection_anchor_30.json (metadata of the 30 items)
- Deterministic (fixed seed): rerunning yields the same 30 items.

Anonymity: annotators are referenced only by set letter (A/B/C for primaries,
D/"anchor" for the fourth). Input result files are matched by name-free glob.
"""
import io, os, re, json, csv, glob, hashlib, random
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 42
METHODS = ['ai_scientist_v2', 'youra', 'mlragent']
BACKBONES = ['opus45', 'sonnet45', 'sonnet46']
SETS = ['A', 'B', 'C']   # primary annotator set letters (anonymous)

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

def pick_from_cell(cands, used_topics, label_count, rng):
    """Within a cell, prefer a new topic and the under-represented label."""
    def score(it):
        new_topic = 0 if it['topic'] in used_topics else 1
        lbl = it['_assess']
        other = (not lbl)
        lab_pref = 1 if label_count[lbl] <= label_count[other] else 0
        return (new_topic, lab_pref, rng.random())
    return max(cands, key=score)

def sample_set(letter, payload, results, extra_cell):
    items = []
    for it in payload['items']:
        it = dict(it)
        it['_assess'] = results.get(it['id'])
        items.append(it)
    by_cell = defaultdict(list)
    for it in items:
        by_cell[(it['method'], it['backbone'])].append(it)

    rng = random.Random(f"{SEED}:{letter}")
    chosen, chosen_ids = [], set()
    used_topics, label_count = set(), {True: 0, False: 0, None: 0}

    cells = [(m, b) for m in METHODS for b in BACKBONES]
    rng.shuffle(cells)
    # one item from each of the 9 cells
    for cell in cells:
        cands = [it for it in by_cell[cell] if it['id'] not in chosen_ids]
        pick = pick_from_cell(cands, used_topics, label_count, rng)
        chosen.append(pick); chosen_ids.add(pick['id'])
        used_topics.add(pick['topic']); label_count[pick['_assess']] += 1
    # 10th item: one more from the designated extra cell
    cands = [it for it in by_cell[extra_cell] if it['id'] not in chosen_ids]
    pick = pick_from_cell(cands, used_topics, label_count, rng)
    chosen.append(pick); chosen_ids.add(pick['id'])
    return chosen

def main():
    all_chosen = []
    for s_idx, letter in enumerate(SETS):
        payload, _ = load_payload(letter)
        results = load_results(letter)
        extra_cell = (METHODS[s_idx], BACKBONES[s_idx])   # rotate per set -> balanced total
        chosen = sample_set(letter, payload, results, extra_cell)
        for it in chosen:
            it['_src_set'] = letter
            it['_src_evaluator'] = f'Annotator {letter}'
        all_chosen.extend(chosen)
        mc = Counter(it['method'] for it in chosen)
        bc = Counter(it['backbone'] for it in chosen)
        lc = Counter(it['_assess'] for it in chosen)
        tc = len(set(it['topic'] for it in chosen))
        print(f"[SET {letter}] n={len(chosen)}  method={dict(mc)}  backbone={dict(bc)}  "
              f"label(T/F)={lc.get(True,0)}/{lc.get(False,0)}  distinct_topics={tc}")

    print("\n[TOTAL 30]",
          "method=", dict(Counter(it['method'] for it in all_chosen)),
          " backbone=", dict(Counter(it['backbone'] for it in all_chosen)),
          " label(T/F)=", f"{sum(1 for it in all_chosen if it['_assess'] is True)}/"
                          f"{sum(1 for it in all_chosen if it['_assess'] is False)}")

    # ---- manifest CSV (includes original label, for analysis) ----
    with io.open(os.path.join(HERE, 'selection_manifest.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['order', 'src_set', 'src_evaluator', 'id', 'method', 'backbone', 'judge', 'topic', 'original_assessment'])
        for i, it in enumerate(all_chosen, 1):
            w.writerow([i, it['_src_set'], it['_src_evaluator'], it['id'],
                        it['method'], it['backbone'], it['judge'], it['topic'], it['_assess']])

    # ---- selection metadata JSON ----
    meta = [{'order': i + 1, 'src_set': it['_src_set'], 'src_evaluator': it['_src_evaluator'],
             'id': it['id'], 'file': it['file'], 'idx': it['idx'], 'method': it['method'],
             'backbone': it['backbone'], 'judge': it['judge'], 'topic': it['topic'],
             'original_assessment': it['_assess']} for i, it in enumerate(all_chosen)]
    with io.open(os.path.join(HERE, 'selection_anchor_30.json'), 'w', encoding='utf-8') as f:
        json.dump({'count': len(meta), 'seed': SEED, 'items': meta}, f, ensure_ascii=False, indent=2)

    # ---- anchor GUI (reuse the A template, swap the payload only) ----
    _, template = load_payload('A')
    clean_items = []
    for it in all_chosen:
        d = {k: v for k, v in it.items() if not k.startswith('_')}
        clean_items.append(d)   # no human_assessment -> keeps the anchor blind
    build_hash = hashlib.md5((''.join(sorted(it['id'] for it in all_chosen))).encode()).hexdigest()[:8]
    new_payload = {'buildId': f'split_d_30i_{build_hash}',
                   'setLabel': 'Set D · reliability cross-evaluation (anchor)',
                   'setKey': 'd', 'items': clean_items}
    new_json = json.dumps(new_payload, ensure_ascii=False)
    new_html = re.sub(r'<script id="appdata" type="application/json">.*?</script>',
                      lambda m: '<script id="appdata" type="application/json">' + new_json + '</script>',
                      template, count=1, flags=re.S)
    # Remove the "AI judge overall assessment / confidence" field so the anchor
    # re-evaluation is not biased by the AI's own verdict.
    new_html = re.sub(r'\s*<div class="field"><div class="lab">AI judge overall assessment / confidence for this paper</div>.*?</div></div>',
                      '', new_html, count=1, flags=re.S)
    with io.open(os.path.join(HERE, 'eval_gui_D_anchor.html'), 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"\nCreated: eval_gui_D_anchor.html  (buildId=split_d_30i_{build_hash}, items={len(clean_items)})")
    print("Created: selection_manifest.csv, selection_anchor_30.json")

if __name__ == '__main__':
    main()
