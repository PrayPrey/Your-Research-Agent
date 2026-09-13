---
hypothesis_id: h-m2
phase: logic
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Logic: H-M2 — SE NLI Clustering Ablation Study

Applied: post-hoc-analysis-single-script pattern (Standard PyTorch / sklearn)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**:
- `load_or_recompute(he1_results_dir, he1_code_dir, samples_path, n, seed, nli_model_id, nli_device) -> dict`
- `compute_cluster_assignments(questions, samples_map, nli_pipeline) -> dict[qid -> {sample_idx: cluster_id}]`
- `compute_per_sample_te(questions, samples_map) -> dict[qid -> list[float]]`
- `verify_mechanism_activated(results, intra_var_threshold, min_passing, min_eligible) -> (bool, dict)`
- `compute_secondary_metrics(results, variance_thresholds) -> dict`
- `save_results(results, indicators, secondary, primary_pass, out_dir) -> None`

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-m1/code/cache_loader.py (ACTUAL CODE)
def load_or_recompute(
    he1_results_dir: str,
    he1_code_dir: str,
    samples_path: str = None,
    n: int = 98,
    seed: int = 42,
    nli_model_id: str = "cross-encoder/nli-deberta-v3-large",
    nli_device: int = 0,
) -> dict:
    """Returns dict: questions, samples_map, per_sample_te, cluster_assignments, correctness, se_scores"""

def compute_cluster_assignments(
    questions: list,
    samples_map: dict,
    nli_pipeline,
) -> dict:
    """Returns dict[qid -> {sample_idx: cluster_id}]"""

# From: h-m1/code/evaluate.py (ACTUAL CODE)
def verify_mechanism_activated(
    results: list,
    intra_var_threshold: float = 0.1,
    min_passing: int = 15,
    min_eligible: int = 20,
) -> tuple:
    """Returns (primary_pass: bool, indicators: dict)"""
    # NOTE: H-M2 defines its own verify_mechanism_activated with different signature
```

**Verified from**: `h-m1/code/cache_loader.py`, `h-m1/code/evaluate.py`, `h-m1/code/run.py`

---

## A-2: Cache Loading [Complexity: 10, Budget: 2 subtasks]

Applied: Standard PyTorch / sys.path injection (same as H-M1 pattern)

### API Signatures

```python
# run.py

def load_artifacts(cfg: "Config") -> tuple[list, dict, dict, list[int]]:
    """Load questions, samples, cluster_assignments, em_labels from H-M1/H-E1 cache.
    Returns (questions, samples_map, cluster_assignments, em_labels)."""
    ...
```

### Pseudo-code

```
1. inject h-m1/code into sys.path
2. from cache_loader import load_or_recompute
3. data = load_or_recompute(
       he1_results_dir=cfg.he1_results_dir,
       he1_code_dir=cfg.he1_code_dir,
       n=cfg.n_questions,
       seed=cfg.seed,
       nli_model_id=cfg.nli_model_name,
       nli_device=0,
   )
4. questions = data["questions"]
5. samples_map = data["samples_map"]
6. cluster_assignments = data["cluster_assignments"]   # dict[qid -> {idx: cid}]
7. em_labels = [int(c) for c in data["correctness"]]  # list[int] len 98

# Validation assertions (subtask L-2-2)
8. assert len(questions) == 98
9. assert len(em_labels) == 98
10. assert set(em_labels) <= {0, 1}
11. assert all(qid in cluster_assignments for qid in [q["question_id"] for q in questions])
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Artifact loading protocol | load_artifacts() body: sys.path inject, call load_or_recompute, extract fields |
| L-2-2 | Validation assertions | Assert N=98, em_labels binary, all qids present in cluster_assignments |

---

## A-3: Ablation Module [Complexity: 9, Budget: 2 subtasks]

Applied: Standard math / collections.Counter

### API Signatures

```python
# ablation.py

import math
from collections import Counter

def compute_se_from_ids(cluster_ids: list[int], K: int) -> float:
    """Entropy over cluster distribution. cluster_ids: [K] -> float in [0, log(K)]"""
    ...

def within_cluster_fraction(cluster_ids: list[int], K: int) -> float:
    """(log(K) - SE_clustered) / log(K). Returns float in [0, 1]."""
    ...

def compute_ablation_scores(
    cluster_assignments: dict,       # dict[qid -> {sample_idx: cluster_id}]
    question_ids: list[str],
    K: int = 10,
) -> tuple[list[float], list[float], list[float]]:
    """Returns (se_clustered, within_fracs, cluster_counts). Each list len = len(question_ids)."""
    ...
```

### Pseudo-code

```
# compute_se_from_ids (subtask L-3-1)
counts = Counter(cluster_ids)  # {cid: count}
probs = [c / K for c in counts.values()]
se = -sum(p * math.log(p + 1e-10) for p in probs)
return se  # float in [0, log(K)]

# within_cluster_fraction (subtask L-3-1)
log_K = math.log(K)
se = compute_se_from_ids(cluster_ids, K)
return (log_K - se) / log_K  # float in [0, 1]

# compute_ablation_scores (subtask L-3-2)
se_clustered, within_fracs, cluster_counts = [], [], []
for qid in question_ids:
    assignment = cluster_assignments[qid]  # {idx: cid}
    cids = list(assignment.values())       # list[int] len K
    se = compute_se_from_ids(cids, K)
    frac = within_cluster_fraction(cids, K)
    n_unique = len(set(cids))
    se_clustered.append(se)
    within_fracs.append(frac)
    cluster_counts.append(float(n_unique))
assert all(0 <= f <= 1 for f in within_fracs)
return se_clustered, within_fracs, cluster_counts
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | SE from cluster IDs | compute_se_from_ids + within_cluster_fraction implementations |
| L-3-2 | Aggregate scores | compute_ablation_scores: loop over questions, collect se/frac/count lists |

---

## A-4: AUROC Evaluation [Complexity: 12, Budget: 2 subtasks]

Applied: sklearn roc_auc_score + numpy stratified bootstrap

### API Signatures

```python
# evaluate.py

import numpy as np
from sklearn.metrics import roc_auc_score

def bootstrap_auroc(
    scores: list[float],
    labels: list[int],
    n_boot: int = 1000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Stratified bootstrap AUROC. Returns (auroc, ci_lower, ci_upper)."""
    ...

def compute_delta_auroc(
    se_clustered: list[float],
    within_fracs: list[float],
    em_labels: list[int],
    cfg: "Config",
) -> dict:
    """Returns dict: auroc_clustered, ci_clustered, auroc_ablated, ci_ablated,
    delta_auroc, gate_pass, gate_verdict."""
    ...

def verify_mechanism_activated(results: dict) -> tuple[bool, bool, dict]:
    """Checks 4 indicators. Returns (gate_pass, mechanism_active, indicators)."""
    ...
```

### Pseudo-code

```
# bootstrap_auroc (subtask L-4-1)
rng = np.random.default_rng(seed)
scores_arr = np.array(scores)
labels_arr = np.array(labels)
pos_idx = np.where(labels_arr == 1)[0]
neg_idx = np.where(labels_arr == 0)[0]
point_auroc = roc_auc_score(labels_arr, scores_arr)
boot_aurocs = []
for _ in range(n_boot):
    bi = np.concatenate([
        rng.choice(pos_idx, len(pos_idx), replace=True),
        rng.choice(neg_idx, len(neg_idx), replace=True),
    ])
    boot_aurocs.append(roc_auc_score(labels_arr[bi], scores_arr[bi]))
ci_lower, ci_upper = np.percentile(boot_aurocs, [2.5, 97.5])
return (point_auroc, float(ci_lower), float(ci_upper))

# compute_delta_auroc (subtask L-4-2)
auroc_c, ci_c_lo, ci_c_hi = bootstrap_auroc(se_clustered, em_labels, cfg.n_bootstrap, cfg.seed)
auroc_a, ci_a_lo, ci_a_hi = bootstrap_auroc(within_fracs, em_labels, cfg.n_bootstrap, cfg.seed)
delta = auroc_c - auroc_a
gate_pass = delta >= cfg.delta_auroc_gate
verdict = "PASS" if gate_pass else ("PARTIAL" if delta >= 0.01 else "FAIL")
return {
    "auroc_clustered": auroc_c,
    "ci_clustered": [ci_c_lo, ci_c_hi],
    "auroc_ablated": auroc_a,
    "ci_ablated": [ci_a_lo, ci_a_hi],
    "delta_auroc": delta,
    "gate_pass": gate_pass,
    "gate_verdict": verdict,
}

# verify_mechanism_activated (subtask L-4-2)
indicators = {
    "clustering_reduces_n": results["mean_cluster_count"] < 10.0,
    "entropy_saving_nonzero": results["mean_within_cluster_fraction"] > 0.0,
    "auroc_delta_positive": results["delta_auroc"] > 0.0,
    "delta_meets_gate": results["gate_pass"],
}
mechanism_active = all(indicators.values())
gate_pass = indicators["delta_meets_gate"]
return (gate_pass, mechanism_active, indicators)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Bootstrap AUROC | bootstrap_auroc: stratified resample, 95% CI via percentile |
| L-4-2 | Delta + gate | compute_delta_auroc + verify_mechanism_activated implementations |

---

## A-7: Visualization [Complexity: 10, Budget: 2 subtasks]

Applied: Standard matplotlib

### API Signatures

```python
# visualize.py

import matplotlib.pyplot as plt
import os

def plot_auroc_comparison(results: dict, out_path: str) -> None:
    """Bar chart: AUROC_clustered vs AUROC_ablated with 95% CI error bars."""
    ...

def plot_within_cluster_scatter(
    within_fracs: list[float],
    question_ids: list[str],
    subset_ids: list[str],
    out_path: str,
) -> None:
    """Scatter: within-cluster fraction vs question index; subset highlighted."""
    ...

def plot_cluster_count_histogram(cluster_counts: list[float], out_path: str) -> None:
    """Histogram: cluster count distribution N=98."""
    ...

def plot_se_boxplot(
    se_clustered: list[float],
    within_fracs: list[float],
    out_path: str,
) -> None:
    """Box plot: SE (clustered) and within-cluster fraction side-by-side."""
    ...

def generate_all_figures(
    results: dict,
    se_clustered: list[float],
    within_fracs: list[float],
    cluster_counts: list[float],
    question_ids: list[str],
    subset_ids: list[str],
    figures_dir: str,
) -> None:
    """Calls all 4 plot functions, saves to figures_dir."""
    ...
```

### Pseudo-code

```
# plot_auroc_comparison (subtask L-7-1)
fig, ax = plt.subplots()
labels = ["SE_clustered", "Ablated"]
aurocs = [results["auroc_clustered"], results["auroc_ablated"]]
ci_lo = [results["ci_clustered"][0], results["ci_ablated"][0]]
ci_hi = [results["ci_clustered"][1], results["ci_ablated"][1]]
yerr = [[a - lo for a, lo in zip(aurocs, ci_lo)],
        [hi - a for a, hi in zip(aurocs, ci_hi)]]
ax.bar(labels, aurocs, yerr=yerr, capsize=5)
ax.set_ylabel("AUROC"); ax.set_title(f"ΔAUROC={results['delta_auroc']:.4f}")
fig.savefig(out_path, dpi=150, bbox_inches="tight"); plt.close(fig)

# plot_within_cluster_scatter + histogram + boxplot (subtask L-7-2)
# scatter: x=range(N), y=within_fracs; color subset_ids differently
# histogram: ax.hist(cluster_counts, bins=range(1,12))
# boxplot: ax.boxplot([se_clustered, within_fracs], labels=["SE_clustered", "within_frac"])

# generate_all_figures
os.makedirs(figures_dir, exist_ok=True)
plot_auroc_comparison(results, os.path.join(figures_dir, "auroc_comparison.png"))
plot_within_cluster_scatter(within_fracs, question_ids, subset_ids,
                            os.path.join(figures_dir, "within_cluster_scatter.png"))
plot_cluster_count_histogram(cluster_counts, os.path.join(figures_dir, "cluster_count_hist.png"))
plot_se_boxplot(se_clustered, within_fracs, os.path.join(figures_dir, "se_boxplot.png"))
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Bar chart | plot_auroc_comparison with CI error bars |
| L-7-2 | Scatter + histogram + boxplot | 3 remaining figures + generate_all_figures orchestrator |

---

## Budget Summary

| Epic | Subtasks Used | Budget |
|------|--------------|--------|
| A-2 | 2 | 2 |
| A-3 | 2 | 2 |
| A-4 | 2 | 2 |
| A-7 | 2 | 2 |
| **Total** | **8** | **8** |
