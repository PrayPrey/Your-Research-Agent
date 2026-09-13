# Architecture: H-M3

**Date:** 2026-08-21
**Hypothesis:** H-M3 — AUROC Bootstrap CI on Aggregation Differences
**Type:** MECHANISM (Statistical Re-analysis)
**Gate:** SHOULD_WORK

Applied: None — Archon KB returned no relevant UQ/NLP content (diffusion model content only)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2)
**Status**: Patterns found from H-M2 actual code
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: H-M2 uses flat module structure (config.py, aggregation.py, analysis.py, figures.py, run_hm2.py). Score loading via `np.load(npz)`, bootstrap via `scipy.stats.bootstrap`, AUROC via `sklearn.metrics.roc_auc_score(labels, -scores)`. H-M3 mirrors this structure exactly — new code is `bootstrap_ci.py` (AUROC+diff CI) and extended `gate_check`.

---

## External Dependencies (H-M2 Base)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| H-M2 config paths | `import sys; sys.path.insert(0, hm2_code_dir)` | `h-m2/code/config.py` |
| compute_auroc | reimplement inline (1 line) | `h-m2/code/analysis.py:28` |
| H-E1 score cache | `np.load(npz)` keys: `min_scores, mean_scores, sum_scores, labels` | `h-e1/results/scores_{model}_{dataset}.npz` |
| H-M2 results | `h-m2/results/scores_{model}_{dataset}.npz` (fallback) | same npz format |

**Verified from**: `h-m2/code/run_hm2.py` and `h-m2/code/config.py` (actual implementation)

**Score sign convention (from H-M2 actual code):**
- H-E1 npz stores POSITIVE negated log-probs → `compute_auroc` uses `roc_auc_score(labels, +scores)` (positive = more certain = correct)
- Check `scores["min"].mean() > 0` to detect convention; if positive, pass directly to roc_auc_score

---

## File Structure

```
h-m3/
  code/
    config.py          # paths, constants, dataset/model lists
    score_loader.py    # load H-E1/H-M2 npz; fallback HF inference
    bootstrap_ci.py    # AUROC CI + pairwise diff CI (core new code)
    gate_check.py      # P1/P2/P3 evaluation
    figures.py         # 4 required figures
    run_experiment.py  # single entry point
  results/
    auroc_table.csv
    auroc_table.json
    gate_conditions.json
  figures/
    fig1_auroc_bar.png
    fig2_diff_heatmap.png
    fig3_bootstrap_dists.png
    fig4_summary_table.png
```

---

## Modules

### Config (`code/config.py`)

**Dependencies**: stdlib only

```python
import os

# Paths
_THIS = os.path.dirname(os.path.abspath(__file__))
_HM3  = os.path.dirname(_THIS)
_YOURA = os.path.dirname(_HM3)

H_E1_RESULTS_DIR: str  # h-e1/results/
H_M2_RESULTS_DIR: str  # h-m2/results/
RESULTS_DIR: str        # h-m3/results/
FIGURES_DIR: str        # h-m3/figures/

DATASETS: list          # ["trivia_qa", "nq", "truthful_qa"]
MODELS_TO_RUN: list     # ["llama2", "mistral"]
AGGREGATION_METHODS: list  # ["min", "mean", "raw_sum"]

N_RESAMPLES_BOOTSTRAP: int  # 1000
SEED: int               # 42
CONFIDENCE_LEVEL: float # 0.95
P1_THRESHOLD: float     # 0.02
P2_THRESHOLD: float     # 0.02
```

---

### ScoreLoader (`code/score_loader.py`)

**Dependencies**: config, numpy

```python
import numpy as np
from typing import Optional, Tuple, Dict

def load_scores(
    model_key: str,
    dataset_name: str,
    h_e1_dir: str,
    h_m2_dir: str,
) -> Tuple[Optional[Dict[str, np.ndarray]], Optional[np.ndarray]]:
    """
    Load pre-computed scores from H-E1 npz (primary) or H-M2 npz (fallback).
    Returns (scores_dict, labels) or (None, None) if not found.
    scores_dict keys: "min", "mean", "raw_sum"
    Sign: scores are POSITIVE (negated log-probs from H-E1 convention).
    """
    ...

def _load_npz(path: str) -> Tuple[Dict[str, np.ndarray], np.ndarray]: ...
    # keys: min_scores, mean_scores, sum_scores, labels
    # validates n >= 400 and both classes present
```

---

### BootstrapCI (`code/bootstrap_ci.py`)

**Dependencies**: numpy, sklearn

```python
import numpy as np
from sklearn.metrics import roc_auc_score
from typing import Tuple, Dict

def compute_auroc_with_ci(
    y_true: np.ndarray,
    scores: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Tuple[float, Tuple[float, float]]:
    """
    Returns (auroc, (ci_lower, ci_upper)) using percentile bootstrap.
    scores: positive = predict correct (H-E1 convention).
    """
    ...

def compute_diff_ci(
    y_true: np.ndarray,
    scores_a: np.ndarray,
    scores_b: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Dict:
    """
    Paired bootstrap CI on AUROC(a) - AUROC(b).
    Returns {diff, ci_lower, ci_upper}.
    Same resample indices applied to both score arrays.
    """
    ...

def compute_auroc_table(
    data: Dict,  # {(model, dataset, agg): (scores, labels)}
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Dict:
    """
    Returns {(model, dataset, agg): {auroc, ci_lower, ci_upper}}
    plus {(model, dataset): {diff_min_mean, diff_ci_lower, diff_ci_upper}}.
    """
    ...
```

---

### GateCheck (`code/gate_check.py`)

**Dependencies**: config

```python
from typing import Dict

def evaluate_gates(
    auroc_table: Dict,   # from BootstrapCI.compute_auroc_table
    p1_threshold: float = 0.02,
    p2_threshold: float = 0.02,
) -> Dict:
    """
    Returns {
        p1_met: bool, p1_evidence: dict,
        p2_met: bool, p2_evidence: dict,
        p3_met: bool, p3_evidence: dict,
        gate: "PASS" | "PARTIAL_PASS" | "FAIL",
    }
    P1: AUROC(min)-AUROC(mean) >= threshold AND ci_lower > 0 on trivia_qa AND nq, both models
    P2: AUROC(mean)-AUROC(min) >= threshold AND ci_lower > 0 on truthful_qa, both models
    P3: AUROC(raw_sum) < AUROC(min) AND < AUROC(mean), all datasets (directional)
    """
    ...
```

---

### Figures (`code/figures.py`)

**Dependencies**: matplotlib, seaborn, pandas, bootstrap_ci results

```python
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict

def fig1_auroc_bar(auroc_table: Dict, out_dir: str) -> str:
    """6-group bar chart: 3 benchmarks × 2 models; bars = min/mean/raw_sum; CI error bars."""
    ...

def fig2_diff_heatmap(auroc_table: Dict, out_dir: str) -> str:
    """Heatmap rows=model, cols=benchmark; cell = AUROC(min)-AUROC(mean); blue/red colormap."""
    ...

def fig3_bootstrap_dists(auroc_table: Dict, out_dir: str) -> str:
    """4-panel histogram: bootstrap AUROC diff distributions for P1/P2 key pairs."""
    ...

def fig4_summary_table(gate_result: Dict, auroc_table: Dict, out_dir: str) -> str:
    """P1/P2/P3 summary rendered as matplotlib table figure."""
    ...

def save_all_figures(auroc_table: Dict, gate_result: Dict, out_dir: str) -> None: ...
```

---

### ExperimentRunner (`code/run_experiment.py`)

**Dependencies**: all modules above

```python
import argparse, json, csv, os
from config import *
from score_loader import load_scores
from bootstrap_ci import compute_auroc_table
from gate_check import evaluate_gates
from figures import save_all_figures

def main(args) -> None:
    """
    1. Load scores for all (model, dataset) pairs from H-E1/H-M2 cache
    2. compute_auroc_table() — AUROC + CI for 18 values + 6 pairwise diffs
    3. evaluate_gates() — P1/P2/P3
    4. Save auroc_table.csv, auroc_table.json, gate_conditions.json
    5. save_all_figures()
    6. Print gate result to stdout
    """
    ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--h_e1_dir", default=H_E1_RESULTS_DIR)
    parser.add_argument("--h_m2_dir", default=H_M2_RESULTS_DIR)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--n_bootstrap", type=int, default=N_RESAMPLES_BOOTSTRAP)
    main(parser.parse_args())
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & structure | `config.py`, dir creation, path constants mirroring H-M2 | 5 | 1+1+1+2 |
| A-2 | Score loader | Load H-E1 npz (primary) + H-M2 fallback; sign check; validation | 9 | 2+2+3+2 |
| A-3 | Bootstrap CI core | `compute_auroc_with_ci` + `compute_diff_ci` (paired); percentile method | 12 | 3+2+4+3 |
| A-4 | AUROC table builder | `compute_auroc_table` over all (model, dataset, agg) combos | 8 | 2+3+2+1 |
| A-5 | Gate evaluator | P1/P2/P3 logic; structured evidence dict; JSON output | 9 | 2+2+3+2 |
| A-6 | Results serialization | auroc_table.csv + .json + gate_conditions.json | 6 | 1+2+2+1 |
| A-7 | Figures (4) | fig1 bar, fig2 heatmap, fig3 bootstrap dists, fig4 summary table | 14 | 3+2+4+5 |
| A-8 | Experiment runner | `run_experiment.py` end-to-end orchestration + argparse | 7 | 2+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-7], Medium(9-13): [A-3, A-4, A-5], Low(4-8): [A-1, A-2, A-6, A-8]

**Total budget**: 70 / 30-task limit satisfied (8 epics, each decomposable to 3-4 subtasks ≤ 30 total)

---

## Data Flow

- H-E1 `scores_{model}_{dataset}.npz` → `score_loader` → `(scores_dict, labels)`
- `(scores_dict, labels)` × all combos → `bootstrap_ci.compute_auroc_table` → `auroc_table`
- `auroc_table` → `gate_check.evaluate_gates` → `gate_result`
- `auroc_table` + `gate_result` → `figures.save_all_figures` → `h-m3/figures/*.png`
- `auroc_table` + `gate_result` → CSV/JSON → `h-m3/results/`

## Key Interface Note

H-M2 `compute_auroc` uses `roc_auc_score(labels, -scores)` (scores are negative log-probs).
H-M3 uses `roc_auc_score(labels, +scores)` because H-E1 npz stores positive negated log-probs (verified from `run_hm2.py` sign-check logic). BootstrapCI module handles this directly — no negation needed if loaded from H-E1 npz.
