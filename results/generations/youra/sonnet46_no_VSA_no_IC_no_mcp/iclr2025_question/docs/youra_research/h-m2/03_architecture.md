---
hypothesis_id: h-m2
phase: architecture
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Architecture: H-M2 — SE NLI Clustering Ablation Study

Applied: post-hoc-analysis-single-script pattern (no new inference, cache reuse)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**: H-M1 has 5 files — `cache_loader.py`, `analysis.py`, `evaluate.py`, `visualize.py`, `run.py`. Cache loading imports h-e1 code via sys.path injection. Cluster assignments returned as `dict[qid -> {sample_idx: cluster_id}]`. AUROC not in H-M1 evaluate.py (H-M1 is variance-based); H-M2 needs new AUROC logic.

---

## File Organization

```
docs/youra_research/h-m2/code/
  ablation.py       # get_semantic_ids_ablated + within_cluster_fraction
  evaluate.py       # bootstrap_auroc, verify_mechanism_activated, gate check
  visualize.py      # 4 figures → ../figures/
  run.py            # orchestration: load → compute → evaluate → visualize → save
  config.py         # single fixed config dataclass
docs/youra_research/h-m2/
  figures/          # 4 output figures
  results.json      # structured results output
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| cache_loader | `sys.path` inject + `from cache_loader import compute_cluster_assignments, compute_per_sample_te` | `h-m1/code/cache_loader.py` |
| load_h_e2v2_samples | `from data import load_h_e2v2_samples, get_pilot_questions` (via h-e1 path) | `h-e1/code/data.py` (injected via h-m1 cache_loader pattern) |
| get_semantic_ids | `from compute_se import get_semantic_ids, load_nli_model` (via h-e1 path) | `h-e1/code/compute_se.py` |

**Verified from**: `docs/youra_research/h-m1/code/cache_loader.py` (actual implementation — uses sys.path injection to h-e1)

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class Config:
    K: int = 10
    seed: int = 42
    n_bootstrap: int = 1000
    entailment_threshold: float = 0.5
    nli_model_name: str = "cross-encoder/nli-deberta-v3-large"
    he1_code_dir: str = "../../h-e1/code"
    hm1_code_dir: str = "../../h-m1/code"
    figures_dir: str = "../figures"
    results_path: str = "../results.json"
    n_questions: int = 98
    paraphrase_subset_size: int = 20
    delta_auroc_gate: float = 0.03
```

---

### Ablation (`code/ablation.py`)

**Dependencies**: Config; imports `get_semantic_ids` from h-e1 (via sys.path)

```python
import math
from collections import Counter

def get_semantic_ids_ablated(strings_list: list[str]) -> list[int]:
    """Identity clustering: each sample = own cluster. Returns list[int] len K."""
    ...

def compute_se_from_ids(cluster_ids: list[int], K: int) -> float:
    """Entropy over cluster distribution. Returns float in [0, log(K)]."""
    ...

def within_cluster_fraction(cluster_ids: list[int], K: int) -> float:
    """(log(K) - SE_clustered) / log(K). Returns float in [0, 1]."""
    ...

def compute_ablation_scores(
    cluster_assignments: dict,       # dict[qid -> {sample_idx: cluster_id}]
    question_ids: list[str],
    K: int = 10,
) -> tuple[list[float], list[float], list[float]]:
    """
    Returns (se_clustered, within_fracs, mean_cluster_counts) for all questions.
    se_clustered: standard SE from cached cluster IDs
    within_fracs: within-cluster entropy fraction (ablated predictor)
    mean_cluster_counts: cluster count per question
    """
    ...
```

---

### Evaluate (`code/evaluate.py`)

**Dependencies**: Config, numpy, sklearn

```python
import numpy as np
from sklearn.metrics import roc_auc_score

def bootstrap_auroc(
    scores: list[float],
    labels: list[int],
    n_boot: int = 1000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Returns (auroc, ci_lower, ci_upper) using stratified bootstrap."""
    ...

def compute_delta_auroc(
    se_clustered: list[float],
    within_fracs: list[float],
    em_labels: list[int],
    cfg: "Config",
) -> dict:
    """
    Returns dict with keys:
      auroc_clustered, ci_clustered,
      auroc_ablated, ci_ablated,
      delta_auroc, gate_pass, gate_verdict
    """
    ...

def compute_secondary_metrics(
    within_fracs: list[float],
    cluster_assignments: dict,
    paraphrase_subset_ids: list[str],
) -> dict:
    """
    Returns dict with:
      mean_within_cluster_fraction,
      entailment_coclustering_rate (on 20-q subset),
      mean_cluster_count
    """
    ...

def verify_mechanism_activated(results: dict) -> tuple[bool, bool, dict]:
    """
    Checks clustering_reduces_n, entropy_saving_nonzero,
    auroc_delta_positive, delta_meets_gate.
    Returns (gate_pass, mechanism_active, indicators).
    """
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, results dict

```python
def plot_auroc_comparison(
    results: dict,
    out_path: str,
) -> None:
    """Bar chart: AUROC_clustered vs AUROC_ablated with 95% CI error bars."""
    ...

def plot_within_cluster_scatter(
    within_fracs: list[float],
    question_ids: list[str],
    subset_ids: list[str],
    out_path: str,
) -> None:
    """Scatter: within-cluster fraction vs question index (20-q subset highlighted)."""
    ...

def plot_cluster_count_histogram(
    cluster_counts: list[float],
    out_path: str,
) -> None:
    """Histogram: cluster count distribution N=98."""
    ...

def plot_se_boxplot(
    se_clustered: list[float],
    within_fracs: list[float],
    out_path: str,
) -> None:
    """Box plot: SE entropy per question (clustered) and ablated proxy."""
    ...

def generate_all_figures(
    results: dict,
    se_clustered: list[float],
    within_fracs: list[float],
    cluster_counts: list[float],
    question_ids: list[str],
    subset_ids: list[str],
    figures_dir: str,
) -> None: ...
```

---

### Run (`code/run.py`)

**Dependencies**: all modules above; h-m1 cache_loader; h-e1 data/compute_se

```python
import sys, os, json
from config import Config
from ablation import compute_ablation_scores
from evaluate import compute_delta_auroc, compute_secondary_metrics, verify_mechanism_activated
from visualize import generate_all_figures

def load_artifacts(cfg: Config) -> tuple:
    """
    Returns (questions, samples_map, cluster_assignments, em_labels).
    Imports h-m1 cache_loader pattern; injects h-e1 sys.path.
    Asserts N=98 questions loaded.
    """
    ...

def get_paraphrase_subset(
    questions: list,
    cluster_assignments: dict,
    n: int = 20,
) -> list[str]:
    """Returns first n question_ids with >=1 multi-member cluster."""
    ...

def save_results(results: dict, path: str) -> None: ...

def main() -> None:
    """
    1. Load artifacts
    2. compute_ablation_scores → se_clustered, within_fracs, cluster_counts
    3. compute_delta_auroc → AUROC comparison
    4. compute_secondary_metrics
    5. verify_mechanism_activated → gate verdict
    6. generate_all_figures
    7. save_results
    8. print gate verdict
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project setup | Create file structure, config.py, verify h-m1/h-e1 paths | 5 | 1+1+1+2 |
| A-2 | Cache loading | Adapt h-m1 cache_loader pattern in run.py; load samples, cluster_ids, em_labels; assert N=98 | 10 | 2+3+2+3 |
| A-3 | Ablation module | Implement ablation.py: compute_se_from_ids, within_cluster_fraction, compute_ablation_scores | 9 | 2+2+3+2 |
| A-4 | AUROC evaluation | bootstrap_auroc, compute_delta_auroc, gate check logic | 12 | 3+3+3+3 |
| A-5 | Secondary/tertiary metrics | compute_secondary_metrics (mean fraction, co-clustering rate, cluster count) | 9 | 2+2+3+2 |
| A-6 | Mechanism verification | verify_mechanism_activated, indicator logging, gate verdict print | 7 | 2+2+2+1 |
| A-7 | Visualization | 4 figures (bar, scatter, histogram, boxplot) → figures/ | 10 | 2+2+3+3 |
| A-8 | Orchestration + results | run.py main(), results.json save, end-to-end smoke test | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4, A-5, A-7, A-8], Low(4-8): [A-1, A-6]

**Total subtasks estimate**: 8 epics × avg 4 subtasks = ~30 subtasks (within FULL tier budget)
