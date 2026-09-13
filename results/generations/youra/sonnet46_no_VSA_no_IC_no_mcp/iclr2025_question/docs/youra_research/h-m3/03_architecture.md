---
hypothesis_id: h-m3
phase: architecture
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Architecture: H-M3 — SelfCheckGPT BERTScore Uncertainty Estimation

Applied: post-hoc-analysis-single-script pattern (no new inference, cache reuse, new uncertainty estimator)

## Codebase Analysis (Serena)

**Project Type**: green-field (new files in h-m3/code/)
**Status**: Serena MCP not available. h-m3 is green-field code — new files in h-m3/code/. External dependencies imported via relative path from h-e1/code/ and h-m2/code/.
**Analyzed Path**: N/A (Serena unavailable; h-m2/03_architecture.md used as reference for patterns)
**Findings**: h-m2 uses 5-file pattern: config.py, ablation.py, evaluate.py, visualize.py, run.py. h-m3 mirrors this structure, replacing ablation.py with scg.py. bootstrap_auroc() reused directly from h-m2/code/evaluate.py via sys.path injection.

---

## File Organization

```
docs/youra_research/h-m3/code/
  config.py     # fixed config dataclass
  scg.py        # SCG BERTScore computation + mechanism verification
  evaluate.py   # thin wrapper: imports bootstrap_auroc from h-m2, adds gate logic
  visualize.py  # 4 figures -> ../figures/
  run.py        # orchestration: load -> compute -> evaluate -> visualize -> save
docs/youra_research/h-m3/
  figures/      # auroc_comparison.png, scg_score_distribution.png,
                #   scg_vs_se_scatter.png, roc_curves.png
  results.json  # structured results output
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_h_e2v2_samples | `sys.path.insert(0, "../../h-e1/code"); from data import load_h_e2v2_samples` | `h-e1/code/data.py` |
| bootstrap_auroc | `sys.path.insert(0, "../../h-m2/code"); from evaluate import bootstrap_auroc` | `h-m2/code/evaluate.py` |
| h-e1 results | `json.load(open("../../h-e1/results.json"))` → `se_scores`, `te_scores`, `em_labels` | `h-e1/results.json` |

**Verified from**: h-m2/03_architecture.md patterns + h-e2-v2 cache path confirmed in 02c_experiment_brief.md

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
    n_questions: int = 98
    delta_auroc_gate: float = 0.03
    rescale_with_baseline: bool = True
    he1_code_dir: str = "../../h-e1/code"
    hm2_code_dir: str = "../../h-m2/code"
    he1_results_path: str = "../../h-e1/results.json"
    figures_dir: str = "../figures"
    results_path: str = "../results.json"
```

---

### SCG (`code/scg.py`)

**Dependencies**: Config, selfcheckgpt, numpy

```python
import numpy as np
from selfcheckgpt.modeling_selfcheck import SelfCheckBERTScore

def init_selfcheck(rescale_with_baseline: bool = True) -> SelfCheckBERTScore: ...

def compute_scg_uncertainty(
    samples: list[str],
    selfcheck: SelfCheckBERTScore,
) -> float:
    """
    Uses samples[0] as primary, samples[1:] as stochastic passages.
    Returns float in [0, 1]; higher = more uncertain.
    """
    ...

def compute_all_scg_scores(
    samples_map: dict,          # dict[qid -> {"samples": list[str], ...}]
    selfcheck: SelfCheckBERTScore,
) -> dict[str, float]:
    """Returns {qid: scg_uncertainty} for all questions. Logs per-question score."""
    ...

def verify_scg_mechanism(
    scg_scores: dict[str, float],
    em_labels: dict[str, int],
    se_auroc: float,
    bootstrap_auroc_fn,
) -> tuple[bool, dict, float]:
    """
    Checks 4 indicators: scores_in_range, scores_have_variance (std>0.01),
    auroc_computable (both labels present), auroc_not_random (auroc>0.45).
    Returns (activated: bool, indicators: dict, delta: float).
    """
    ...
```

---

### Evaluate (`code/evaluate.py`)

**Dependencies**: Config, numpy, sklearn; imports bootstrap_auroc from h-m2

```python
import sys

def load_bootstrap_auroc(hm2_code_dir: str):
    """sys.path inject h-m2/code, return bootstrap_auroc function."""
    ...

def compute_all_aurocs(
    scg_scores: dict[str, float],
    se_scores: dict[str, float],
    te_scores: dict[str, float],
    em_labels: dict[str, int],
    cfg: "Config",
) -> dict:
    """
    Returns dict with:
      auroc_scg, ci_scg, auroc_se, ci_se, auroc_te, ci_te,
      delta, gate_passed, scg_vs_te_advantage
    """
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, numpy, sklearn

```python
def plot_auroc_comparison(results: dict, out_path: str) -> None:
    """Bar chart: SCG vs SE vs TE AUROC with 95% CI error bars."""
    ...

def plot_scg_score_distribution(
    scg_scores: dict[str, float],
    em_labels: dict[str, int],
    out_path: str,
) -> None:
    """Distribution of SCG scores split by EM correct/incorrect."""
    ...

def plot_scg_vs_se_scatter(
    scg_scores: dict[str, float],
    se_scores: dict[str, float],
    out_path: str,
) -> None:
    """Scatter: SCG score vs SE score per question."""
    ...

def plot_roc_curves(
    scg_scores: dict[str, float],
    se_scores: dict[str, float],
    te_scores: dict[str, float],
    em_labels: dict[str, int],
    out_path: str,
) -> None:
    """ROC curves for SCG, SE, TE on same axes."""
    ...

def generate_all_figures(
    scg_scores: dict,
    se_scores: dict,
    te_scores: dict,
    em_labels: dict,
    results: dict,
    figures_dir: str,
) -> None: ...
```

---

### Run (`code/run.py`)

**Dependencies**: all modules above; h-e1 data; h-m2 evaluate

```python
import sys, os, json
from config import Config
from scg import init_selfcheck, compute_all_scg_scores, verify_scg_mechanism
from evaluate import load_bootstrap_auroc, compute_all_aurocs
from visualize import generate_all_figures

def load_artifacts(cfg: Config) -> tuple:
    """
    Injects h-e1/code sys.path, loads samples_map via load_h_e2v2_samples().
    Loads se_scores, te_scores, em_labels from h-e1/results.json.
    Asserts N=98, K=10 per question, binary labels.
    Returns (samples_map, se_scores, te_scores, em_labels).
    """
    ...

def save_results(results: dict, path: str) -> None: ...

def main() -> None:
    """
    1. load_artifacts -> samples_map, se_scores, te_scores, em_labels
    2. init_selfcheck
    3. compute_all_scg_scores -> scg_scores
    4. load_bootstrap_auroc from h-m2
    5. verify_scg_mechanism -> activated, indicators, delta
    6. compute_all_aurocs -> results dict
    7. generate_all_figures -> figures/
    8. save_results -> results.json
    9. print gate verdict
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Data Flow

```
h-e2-v2 cache (interim_cache.jsonl)
  -> load_h_e2v2_samples() [via h-e1/code/data.py]
  -> samples_map {qid: {samples: [K strings], ...}}
        |
        v
h-e1/results.json -> se_scores, te_scores, em_labels
        |
        v
init_selfcheck() -> SelfCheckBERTScore(rescale_with_baseline=True)
        |
        v
compute_all_scg_scores(samples_map, selfcheck) -> scg_scores {qid: float}
        |
        v
verify_scg_mechanism(scg_scores, em_labels, se_auroc, bootstrap_auroc_fn)
        |
        v
compute_all_aurocs(scg, se, te, em_labels) -> results dict
        |
        +-> generate_all_figures() -> figures/*.png
        +-> save_results() -> results.json
```

---

## Epic Tasks

| ID | Task | Description | Files | Complexity | Breakdown |
|----|------|-------------|-------|------------|-----------|
| A-1 | Project setup | Create file structure, config.py, verify external paths, figures/ dir | config.py | 5 | 1+1+1+2 |
| A-2 | Artifact loading | load_artifacts() in run.py: inject h-e1 sys.path, load samples_map, se/te scores, em_labels; assert N=98, K=10 | run.py | 9 | 2+3+2+2 |
| A-3 | SCG computation | scg.py: init_selfcheck, compute_scg_uncertainty (single-sentence QA), compute_all_scg_scores with per-question logging | scg.py | 11 | 3+2+3+3 |
| A-4 | Mechanism verification | verify_scg_mechanism(): 4 indicators, activation logging, delta computation | scg.py | 8 | 2+2+2+2 |
| A-5 | AUROC evaluation | evaluate.py: load_bootstrap_auroc from h-m2, compute_all_aurocs (scg/se/te), gate logic, secondary metric | evaluate.py | 10 | 2+3+3+2 |
| A-6 | Visualization | 4 figures: bar AUROC comparison, SCG distribution, scatter scg-vs-se, ROC curves | visualize.py | 11 | 2+2+4+3 |
| A-7 | Orchestration + results | run.py main(), save_results() to results.json, end-to-end integration, gate verdict print | run.py | 9 | 2+2+3+2 |
| A-8 | Smoke test | Verify run completes, results.json valid, figures exist, gate verdict printed | run.py | 5 | 1+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-5, A-6, A-7], Low(4-8): [A-1, A-4, A-8]
