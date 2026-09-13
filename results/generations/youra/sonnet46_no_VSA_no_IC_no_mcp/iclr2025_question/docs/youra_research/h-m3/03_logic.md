---
hypothesis_id: h-m3
phase: logic
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Logic: H-M3 — SelfCheckGPT BERTScore Uncertainty Estimation

Applied: black-box consistency scorer pattern (selfcheckgpt single-sentence short-QA variant)

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (extending h-e1, h-m2)
**Status**: Serena MCP not available. API signatures read directly from actual code files.
**Analyzed Path**: `docs/youra_research/h-m2/code/evaluate.py`, `docs/youra_research/h-e1/code/data.py`
**Relevant Symbols**:
- `bootstrap_auroc(scores: list, labels: list, n_boot: int = 1000, seed: int = 42) -> tuple` — verified from h-m2/code/evaluate.py
- `load_h_e2v2_samples(samples_path: str = H_E2V2_CACHE) -> dict` — verified from h-e1/code/data.py; returns `{qid: {samples, log_probs, answer_aliases, greedy_answer, te_score, is_correct, question}}`

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-m2/code/evaluate.py (ACTUAL CODE)
def bootstrap_auroc(
    scores: list,
    labels: list,
    n_boot: int = 1000,
    seed: int = 42,
) -> tuple:
    """Returns (auroc: float, ci_lower: float, ci_upper: float)."""
    ...

# From: h-e1/code/data.py (ACTUAL CODE)
def load_h_e2v2_samples(samples_path: str = H_E2V2_CACHE) -> dict:
    """Returns {question_id: {samples: list[str], log_probs, answer_aliases,
    greedy_answer, te_score, is_correct, question}}."""
    ...
```

**Verified from**: actual code at `h-m2/code/evaluate.py` and `h-e1/code/data.py`

---

## A-3: SCG Computation [Complexity: 11, Budget: 2 subtasks]

Applied: black-box consistency scorer pattern

### Subtask L-3-1: SelfCheckBERTScore Initialization

```python
# scg.py
from selfcheckgpt.modeling_selfcheck import SelfCheckBERTScore

def init_selfcheck(rescale_with_baseline: bool = True) -> SelfCheckBERTScore:
    """Initialize SelfCheckBERTScore scorer."""
    return SelfCheckBERTScore(rescale_with_baseline=rescale_with_baseline)
```

### Subtask L-3-2: Per-question SCG uncertainty computation

```python
# scg.py
import numpy as np

def compute_scg_uncertainty(
    samples: list[str],
    selfcheck: SelfCheckBERTScore,
) -> float:
    """Compute SCG uncertainty for one question.
    samples[0] = primary answer, samples[1:] = stochastic passages.
    Returns float in [0,1]; higher = more uncertain."""
    primary = samples[0]           # str
    others = samples[1:]           # list[str], len K-1=9
    # sent_scores shape: (n_sentences,) = (1,) for short QA
    sent_scores = selfcheck.predict(
        sentences=[primary],
        sampled_passages=others,
    )
    return float(np.mean(sent_scores))


def compute_all_scg_scores(
    samples_map: dict,
    selfcheck: SelfCheckBERTScore,
) -> dict[str, float]:
    """Returns {qid: scg_uncertainty} for all N=98 questions."""
    scg_scores = {}
    for i, (qid, data) in enumerate(samples_map.items()):
        score = compute_scg_uncertainty(data["samples"], selfcheck)
        scg_scores[qid] = score
        print(f"[{i+1}/{len(samples_map)}] qid={qid} scg={score:.4f}")
    return scg_scores
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | init_selfcheck | SelfCheckBERTScore init wrapper |
| L-3-2 | compute_scg_uncertainty + compute_all_scg_scores | Single-sentence predict call, mean aggregation, per-question loop |

---

## A-5: AUROC Evaluation [Complexity: 10, Budget: 1 subtask]

Applied: Standard sklearn AUROC + sys.path injection pattern

### Subtask L-5-1: compute_all_aurocs with gate logic

```python
# evaluate.py
import sys
import numpy as np

def load_bootstrap_auroc(hm2_code_dir: str):
    """Inject h-m2/code into sys.path, return bootstrap_auroc function."""
    if hm2_code_dir not in sys.path:
        sys.path.insert(0, hm2_code_dir)
    from evaluate import bootstrap_auroc
    return bootstrap_auroc


def compute_all_aurocs(
    scg_scores: dict[str, float],
    se_scores: dict[str, float],
    te_scores: dict[str, float],
    em_labels: dict[str, int],
    cfg: "Config",
) -> dict:
    """Compute AUROC + 95% CI for SCG, SE, TE; apply gate logic.
    Returns dict with all metrics."""
    bootstrap_auroc = load_bootstrap_auroc(cfg.hm2_code_dir)

    qids = list(scg_scores.keys())
    labels = [em_labels[q] for q in qids]      # list[int] len 98
    scg_list = [scg_scores[q] for q in qids]   # list[float]
    se_list  = [se_scores[q]  for q in qids]
    te_list  = [te_scores[q]  for q in qids]

    auroc_scg, ci_scg_lo, ci_scg_hi = bootstrap_auroc(scg_list, labels, cfg.n_bootstrap, cfg.seed)
    auroc_se,  ci_se_lo,  ci_se_hi  = bootstrap_auroc(se_list,  labels, cfg.n_bootstrap, cfg.seed)
    auroc_te,  ci_te_lo,  ci_te_hi  = bootstrap_auroc(te_list,  labels, cfg.n_bootstrap, cfg.seed)

    delta = abs(auroc_scg - auroc_se)
    gate_passed = delta <= cfg.delta_auroc_gate   # 0.03
    scg_vs_te_advantage = auroc_scg - auroc_te

    return {
        "auroc_scg": auroc_scg,
        "ci_scg": [ci_scg_lo, ci_scg_hi],
        "auroc_se": auroc_se,
        "ci_se": [ci_se_lo, ci_se_hi],
        "auroc_te": auroc_te,
        "ci_te": [ci_te_lo, ci_te_hi],
        "delta": delta,
        "gate_passed": gate_passed,
        "scg_vs_te_advantage": scg_vs_te_advantage,
    }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_all_aurocs | sys.path inject h-m2, run bootstrap for SCG/SE/TE, delta + gate |

---

## A-2: Artifact Loading [Complexity: 9, Budget: 1 subtask]

Applied: sys.path injection pattern (same as h-m1/h-m2)

### Subtask L-2-1: load_artifacts

```python
# run.py
import sys, json

def load_artifacts(cfg: "Config") -> tuple[dict, dict, dict, dict]:
    """Load samples_map, se_scores, te_scores, em_labels.
    Returns (samples_map, se_scores, te_scores, em_labels) — all keyed by question_id."""
    # Inject h-e1/code for load_h_e2v2_samples
    if cfg.he1_code_dir not in sys.path:
        sys.path.insert(0, cfg.he1_code_dir)
    from data import load_h_e2v2_samples
    samples_map = load_h_e2v2_samples()  # {qid: {samples: list[str], ...}}

    # Load pre-computed SE/TE scores and EM labels from h-e1/results.json
    with open(cfg.he1_results_path) as f:
        he1 = json.load(f)
    se_scores  = he1["se_scores"]   # {qid: float}
    te_scores  = he1["te_scores"]   # {qid: float}
    em_labels  = he1["em_labels"]   # {qid: int}  0/1

    # Validation
    assert len(samples_map) == cfg.n_questions, f"Expected {cfg.n_questions} questions"
    assert all(len(v["samples"]) == cfg.K for v in samples_map.values()), "Expected K=10 samples per question"
    assert set(em_labels.values()) <= {0, 1}, "em_labels must be binary"
    assert set(samples_map.keys()) == set(se_scores.keys()), "qid mismatch se_scores"
    assert set(samples_map.keys()) == set(te_scores.keys()), "qid mismatch te_scores"

    return samples_map, se_scores, te_scores, em_labels
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_artifacts | sys.path inject h-e1, load samples_map, load se/te/em from he1 results.json, 5 asserts |

---

## A-7: Orchestration [Complexity: 9, Budget: 1 subtask]

### Subtask L-7-1: main() orchestration flow

```python
# run.py

def save_results(results: dict, path: str) -> None:
    """Write results dict to JSON."""
    import os, json
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
```

Pseudo-code for `main()`:

```
1. cfg = Config()

2. samples_map, se_scores, te_scores, em_labels = load_artifacts(cfg)
   # samples_map: {qid: {samples: [K=10 str], ...}}

3. selfcheck = init_selfcheck(cfg.rescale_with_baseline)
   # SelfCheckBERTScore(rescale_with_baseline=True)

4. scg_scores = compute_all_scg_scores(samples_map, selfcheck)
   # {qid: float} all in [0,1]

5. bootstrap_auroc_fn = load_bootstrap_auroc(cfg.hm2_code_dir)

6. # Mechanism verification (uses point AUROC for quick check)
   from sklearn.metrics import roc_auc_score
   qids = list(scg_scores.keys())
   labels_list = [em_labels[q] for q in qids]
   scg_list = [scg_scores[q] for q in qids]
   se_auroc_point, _, _ = bootstrap_auroc_fn(
       [se_scores[q] for q in qids], labels_list, n_boot=100, seed=42
   )
   activated, indicators, delta_mech = verify_scg_mechanism(
       scg_scores, em_labels, se_auroc_point, bootstrap_auroc_fn
   )
   print(f"[Mechanism] activated={activated} indicators={indicators} delta={delta_mech:.4f}")

7. results = compute_all_aurocs(scg_scores, se_scores, te_scores, em_labels, cfg)

8. results["scg_scores"] = scg_scores
   results["se_scores"] = se_scores
   results["te_scores"] = te_scores
   results["em_labels"] = em_labels
   results["mechanism_indicators"] = indicators
   results["mechanism_activated"] = activated

9. generate_all_figures(scg_scores, se_scores, te_scores, em_labels, results, cfg.figures_dir)

10. save_results(results, cfg.results_path)

11. verdict = "PASS" if results["gate_passed"] else "FAIL"
    print(f"[Gate] delta={results['delta']:.4f} threshold=0.03 -> {verdict}")
    print(f"[AUROC] SCG={results['auroc_scg']:.4f} SE={results['auroc_se']:.4f} "
          f"TE={results['auroc_te']:.4f} SCG_vs_TE={results['scg_vs_te_advantage']:+.4f}")
```

**results.json schema** (all top-level keys):
```
{
  "scg_scores":           {qid: float},
  "se_scores":            {qid: float},
  "te_scores":            {qid: float},
  "em_labels":            {qid: int},
  "auroc_scg":            float,
  "ci_scg":               [float, float],
  "auroc_se":             float,
  "ci_se":                [float, float],
  "auroc_te":             float,
  "ci_te":                [float, float],
  "delta":                float,
  "gate_passed":          bool,
  "scg_vs_te_advantage":  float,
  "mechanism_indicators": {str: bool},
  "mechanism_activated":  bool
}
```

**Gate verdict print format**:
```
[Gate] delta=0.0312 threshold=0.03 -> FAIL
[AUROC] SCG=0.5421 SE=0.5733 TE=0.4987 SCG_vs_TE=+0.0434
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | main() + save_results | Full orchestration pseudo-code, results.json schema, gate verdict format |

---

## Budget Summary

| Epic | Subtasks Used | Budget |
|------|--------------|--------|
| A-3 | 2 | 2 |
| A-5 | 1 | 1 |
| A-2 | 1 | 1 |
| A-7 | 1 | 1 |
| **Total** | **5** | **5** |
