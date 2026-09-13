---
title: "Logic: h-e1 — Spurious/Task Probe Accuracy Ratio Study"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
date: 2026-08-26
author: yoon303b@gmail.com
---

# Logic: h-e1

Applied: Frozen-backbone linear probe pattern (Izmailov et al. NeurIPS 2022)
Applied: Bonferroni correction — p_corrected = p_raw * n_pairs
Applied: Cohen's d = (mean_A - mean_B) / pooled_std for effect size

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing src/ or code/ directory to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Patterns derived from reference repos documented in 02c_experiment_brief.md:
- izmailovpavel/spurious_feature_learning — probe train/eval protocol, group-balanced sampling
- facebookresearch/moco-v3 main_lincls.py — frozen hub model + no_grad feature extraction
- facebookresearch/dino — `dino_resnet50` 2048-dim feature extraction
- facebookresearch/barlowtwins — fc=Identity patch for 2048-dim output

Key logic patterns: (1) cache features before seed loop (features are seed-independent), (2) group-balanced sampling is seed-dependent (controls val split randomness), (3) Bonferroni = p_raw * 6, (4) Cohen's d with pooled std from 5-sample arrays.

---

## Subtasks

### E2: Model Loading & Feature Extraction (3 subtasks)

---

#### L-E2-1: Hub loading functions with fc=Identity patch and eval mode

**Signature:**
```python
def load_erm(device: str) -> torch.nn.Module: ...
def load_moco(device: str) -> torch.nn.Module: ...
def load_dino(device: str) -> torch.nn.Module: ...
def load_barlowtwins(device: str) -> torch.nn.Module: ...
```

**Tensor shapes:** Input: image batch (B, 3, 224, 224) → Output: features (B, 2048)

**Pseudo-code (ERM pattern, others analogous):**
```python
def load_erm(device):
    model = torchvision.models.resnet50(pretrained=True)
    model.fc = nn.Identity()          # expose 2048-dim avg pool output
    model = model.to(device).eval()
    for p in model.parameters():
        p.requires_grad = False
    return model
```

**BarlowTwins note:** Hub loads full model with projection head; replace `model.fc` with `nn.Identity()` after hub load.

**MoCo-v3 note:** Hub model exposes backbone directly — no fc replacement needed; verify output dim with a dummy forward.

**DINO note:** `dino_resnet50` outputs 2048-dim CLS token equivalent from global avg pool — no fc replacement needed.

**Asserts:**
```python
# Smoke test after load:
with torch.no_grad():
    dummy = torch.randn(2, 3, 224, 224).to(device)
    out = model(dummy)
    assert out.shape == (2, 2048), f"Expected (2,2048), got {out.shape}"
```

---

#### L-E2-2: extract_features() with batched no_grad, tensor concatenation, shape assertion

**Signature:**
```python
def extract_features(
    model: nn.Module,
    loader: DataLoader,
    device: str,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Returns:
        features:        (N, 2048) float32
        task_labels:     (N,)      int64  — bird species
        spurious_labels: (N,)      int64  — background
    """
```

**Tensor shapes:**
- Input per batch: `x: (B, 3, 224, 224)`, `y: (B,)`, `metadata: (B, M)`
- Output: `features: (N, 2048)`, `task_labels: (N,)`, `spurious_labels: (N,)`

**Pseudo-code:**
```python
def extract_features(model, loader, device):
    feats, task_lbls, spur_lbls = [], [], []
    model.eval()
    with torch.no_grad():
        for x, y, metadata in loader:
            f = model(x.to(device))           # (B, 2048)
            feats.append(f.cpu())
            task_lbls.append(y)
            spur_lbls.append(metadata[:, 0])  # background label
    features = torch.cat(feats)               # (N, 2048)
    assert features.shape[1] == 2048, f"Feature dim mismatch: {features.shape}"
    return features, torch.cat(task_lbls), torch.cat(spur_lbls)
```

**Edge cases:**
- `metadata[:, 0]` must be int (background group index 0=land, 1=water)
- Handle empty loader (assert `len(features) > 0`)

---

#### L-E2-3: Feature caching strategy

**Rationale:** Features are seed-independent (no augmentation, deterministic). Cache once per paradigm, reuse across all 5 seeds.

**Signature:**
```python
def get_or_extract_features(
    model: nn.Module,
    loader: DataLoader,
    device: str,
    cache_key: str,          # e.g. 'erm_test', 'moco_val'
    cache_dir: str = '/tmp/h-e1-cache/',
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
```

**Pseudo-code:**
```python
def get_or_extract_features(model, loader, device, cache_key, cache_dir):
    path = os.path.join(cache_dir, f"{cache_key}.pt")
    if os.path.exists(path):
        feats, task_lbls, spur_lbls = torch.load(path)
        return feats, task_lbls, spur_lbls
    feats, task_lbls, spur_lbls = extract_features(model, loader, device)
    os.makedirs(cache_dir, exist_ok=True)
    torch.save((feats, task_lbls, spur_lbls), path)
    return feats, task_lbls, spur_lbls
```

**Note:** Cache full val features; group-balanced sub-sampling happens inside `compute_ratio()` per seed (after loading from cache).

---

### E4: Statistical Analysis & Gate (3 subtasks)

---

#### L-E4-1: pairwise_tests() — 6-pair loop, Bonferroni, Cohen's d

**Signature:**
```python
def pairwise_tests(
    ratios: dict[str, list[float]],   # {paradigm: [r_seed0, ..., r_seed4]}
    n_bonferroni: int = 6,
) -> list[dict]:
    """
    Returns list of 6 dicts:
    {
      'pair': 'erm_vs_moco',
      't': float,
      'p_raw': float,
      'p_bonf': float,
      'cohens_d': float,
      'mean_diff': float,
    }
    """
```

**Pseudo-code:**
```python
def pairwise_tests(ratios, n_bonferroni=6):
    from itertools import combinations
    from scipy import stats
    import numpy as np
    results = []
    paradigms = list(ratios.keys())
    for p1, p2 in combinations(paradigms, 2):
        a, b = np.array(ratios[p1]), np.array(ratios[p2])
        t, p_raw = stats.ttest_ind(a, b)
        p_bonf = min(p_raw * n_bonferroni, 1.0)
        # Cohen's d with pooled std
        pooled_std = np.sqrt((a.std(ddof=1)**2 + b.std(ddof=1)**2) / 2)
        d = (a.mean() - b.mean()) / pooled_std if pooled_std > 0 else 0.0
        results.append({
            'pair': f'{p1}_vs_{p2}',
            't': float(t), 'p_raw': float(p_raw),
            'p_bonf': float(p_bonf),
            'cohens_d': float(d),
            'mean_diff': float(abs(a.mean() - b.mean())),
        })
    return results
```

**Edge case:** `pooled_std == 0` (identical arrays) → d = 0.0.

---

#### L-E4-2: check_gate() — gate criterion with logging

**Signature:**
```python
def check_gate(
    pair_results: list[dict],
    alpha: float = 0.05,
    min_diff: float = 0.02,
) -> tuple[bool, list[dict]]:
    """
    Returns (gate_satisfied: bool, passing_pairs: list[dict])
    """
```

**Pseudo-code:**
```python
def check_gate(pair_results, alpha=0.05, min_diff=0.02):
    passing = []
    for r in pair_results:
        if r['p_bonf'] < alpha and r['mean_diff'] >= min_diff:
            passing.append(r)
            logging.info(
                f"GATE PASS: {r['pair']} p_bonf={r['p_bonf']:.4f} diff={r['mean_diff']:.4f}"
            )
    gate_ok = len(passing) > 0
    if not gate_ok:
        logging.warning("GATE FAIL: no pair meets p_bonf<0.05 AND diff>=0.02 — route to Phase 0")
    else:
        logging.info(f"GATE SATISFIED: {len(passing)} pair(s) pass")
    return gate_ok, passing
```

---

#### L-E4-3: export_results() — JSON stats export

**Signature:**
```python
def export_results(
    ratios: dict[str, list[float]],
    anova_result: tuple[float, float],
    pair_results: list[dict],
    gate_ok: bool,
    passing_pairs: list[dict],
    out_path: str,
) -> None:
```

**Pseudo-code:**
```python
def export_results(ratios, anova_result, pair_results, gate_ok, passing_pairs, out_path):
    import json, numpy as np
    f_stat, p_anova = anova_result
    summary = {p: {'mean': float(np.mean(v)), 'std': float(np.std(v, ddof=1))}
               for p, v in ratios.items()}
    payload = {
        'anova': {'f_stat': float(f_stat), 'p_value': float(p_anova)},
        'pairwise': pair_results,
        'summary': summary,
        'gate': {'satisfied': gate_ok, 'passing_pairs': [r['pair'] for r in passing_pairs]},
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(payload, f, indent=2)
```

---

### E3: Linear Probe + Ratio (3 subtasks)

---

#### L-E3-1: Group-balanced train split construction (seed-controlled)

**Signature:**
```python
def get_balanced_probe_indices(
    metadata_array: torch.Tensor,   # (N_val, M) — from WILDS val subset
    seed: int,
) -> np.ndarray:
    """
    Returns indices for group-balanced sample from val split.
    4 groups = {bird_label} x {background_label}.
    Samples min_group_count from each group.
    """
```

**Pseudo-code:**
```python
def get_balanced_probe_indices(metadata_array, seed):
    import numpy as np
    rng = np.random.default_rng(seed)
    # metadata_array[:, 0] = background (spurious), metadata_array[:, 1] = bird (task)
    # group_id = 2 * task_label + spurious_label  →  4 groups: 0,1,2,3
    task_lbls = metadata_array[:, 1].numpy()
    spur_lbls = metadata_array[:, 0].numpy()
    group_ids = 2 * task_lbls + spur_lbls   # 0..3
    groups = [np.where(group_ids == g)[0] for g in range(4)]
    min_count = min(len(g) for g in groups)
    assert min_count > 0, "Empty group in val split"
    chosen = [rng.choice(g, size=min_count, replace=False) for g in groups]
    return np.concatenate(chosen)
```

**Tensor shapes:** `metadata_array: (N_val, M)` → `indices: (4 * min_count,)`

---

#### L-E3-2: compute_ratio() — full per-(paradigm, seed) pipeline

**Signature:**
```python
def compute_ratio(
    feats_val: torch.Tensor,         # (N_val, 2048) — cached val features
    task_lbls_val: torch.Tensor,     # (N_val,)
    spur_lbls_val: torch.Tensor,     # (N_val,)
    metadata_val: torch.Tensor,      # (N_val, M) for group-balanced split
    feats_test: torch.Tensor,        # (N_test, 2048) — cached test features
    task_lbls_test: torch.Tensor,    # (N_test,)
    spur_lbls_test: torch.Tensor,    # (N_test,)
    seed: int,
    paradigm: str,
) -> dict:
    """
    Returns {'ratio': float, 'spurious_acc': float, 'task_acc': float}
    """
```

**Pseudo-code:**
```python
def compute_ratio(feats_val, task_lbls_val, spur_lbls_val, metadata_val,
                  feats_test, task_lbls_test, spur_lbls_test, seed, paradigm):
    idx = get_balanced_probe_indices(metadata_val, seed)
    X_tr = feats_val[idx].numpy()
    y_task_tr = task_lbls_val[idx].numpy()
    y_spur_tr = spur_lbls_val[idx].numpy()
    X_te = feats_test.numpy()
    clf_task = train_probe(X_tr, y_task_tr)
    clf_spur = train_probe(X_tr, y_spur_tr)
    acc_task = eval_probe(clf_task, X_te, task_lbls_test.numpy())
    acc_spur = eval_probe(clf_spur, X_te, spur_lbls_test.numpy())
    assert acc_task > 0.5 and acc_spur > 0.5, "Probe below chance baseline"
    ratio = acc_spur / acc_task
    logging.info(f"Paradigm={paradigm}, seed={seed}, spurious_acc={acc_spur:.3f}, "
                 f"task_acc={acc_task:.3f}, ratio={ratio:.4f}")
    return {'ratio': ratio, 'spurious_acc': acc_spur, 'task_acc': acc_task}
```

---

#### L-E3-3: Seed control and logging protocol

**Specification:**

Seed scope: controls only probe train split randomness (group-balanced val sampling). Feature extraction is deterministic (no augmentation, eval mode) — no seed needed there.

```python
def set_seeds(seed: int) -> None:
    """Set numpy seed for reproducible group-balanced sampling."""
    import numpy as np
    np.random.seed(seed)         # legacy API for sklearn compatibility
    # torch seed not strictly needed (no stochastic ops in probe path)
    # but set for completeness
    torch.manual_seed(seed)
```

**Logging protocol:**
```python
import logging
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
# Per probe-run log line (from compute_ratio):
# "Paradigm={paradigm}, seed={seed}, spurious_acc={:.3f}, task_acc={:.3f}, ratio={:.4f}"
# Gate result:
# "GATE SATISFIED: {pair} p_bonf={:.4f} diff={:.4f}"  OR
# "GATE FAIL: no pair meets criteria — route to Phase 0"
```

**Total runs accounting:**
- 4 paradigms × 5 seeds = 20 `compute_ratio()` calls
- Each call: 2 probe fits (task + spurious) → 40 LogisticRegression fits total
- All logged with paradigm + seed identifiers

---

## Summary

| Subtask | Epic | Lines of code est. | Key dependency |
|---|---|---|---|
| L-E2-1 | E2 | ~20 | torchvision, torch.hub |
| L-E2-2 | E2 | ~15 | torch.no_grad |
| L-E2-3 | E2 | ~15 | torch.save/load |
| L-E4-1 | E4 | ~20 | scipy.stats, itertools |
| L-E4-2 | E4 | ~15 | logging |
| L-E4-3 | E4 | ~15 | json |
| L-E3-1 | E3 | ~15 | numpy.random |
| L-E3-2 | E3 | ~20 | sklearn, probe_utils |
| L-E3-3 | E3 | ~10 | logging, numpy |

**Total subtasks: 9** — within LIGHT tier budget (15 total = 6 epics + 9 subtasks ✅)
