# Architecture: H-M1
# Token Distribution Peakedness Analysis for Hallucination Detection

**Hypothesis:** H-M1 (MECHANISM)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Prerequisite:** H-E1 (COMPLETED, PASSED)

Applied: incremental-extension (reuse H-E1 inference/data pipeline, add peakedness + stats)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Analyzed via direct file reads (Serena project selection unavailable; used Read tool on actual code)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 `run_inference()` returns records with `logprobs: List[float]` key — directly consumable by H-M1 peakedness computation. `config.py` uses `BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` pattern for path resolution; H-M1 config replicates this pattern.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_model | `sys.path.insert(0, h_e1_code); from inference import load_model` | `h-e1/code/inference.py` |
| extract_token_logprobs | `from inference import extract_token_logprobs` | `h-e1/code/inference.py` |
| run_inference | `from inference import run_inference` | `h-e1/code/inference.py` |
| load_trivia_qa / load_nq | `from data_loader import load_trivia_qa, load_nq` | `h-e1/code/data_loader.py` |
| score_answer | `from data_loader import score_answer` | `h-e1/code/data_loader.py` |
| MODELS, MAX_NEW_TOKENS, SEED | `from config import MODELS, MAX_NEW_TOKENS, SEED` | `h-e1/code/config.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

**Key findings from H-E1 actual code:**
- `run_inference()` already attaches `record["logprobs"]` and `record["label"]` — direct reuse
- `config.py` has `DATASETS = ["trivia_qa", "nq", "truthful_qa"]` — NQ already supported
- `MAX_NEW_TOKENS = 30` (not 50 as in PRD spec) — use actual H-E1 value
- H-E1 results at `h-e1/results/` contain aggregation scores; raw records may need re-inference

---

## File Structure

```
h-m1/
  code/
    config.py           # H-M1 paths, thresholds, dataset list (no models dict — reuse H-E1)
    peakedness.py       # compute_peakedness, analyze_group_peakedness, test_peakedness_difference
    visualization.py    # 4 required figures
    run_experiment.py   # orchestration: load/infer → peakedness → stats → cache → figures
  results/              # peakedness_*.npz, results_summary.json
  figures/              # 4 figure files
  03_prd.md
  03_architecture.md    # this file
```

---

## Modules

### Config (`code/config.py`)

**Dependencies**: None (stdlib only)

```python
import os

H_E1_CODE_DIR: str   # absolute path to h-e1/code/
H_E1_RESULTS_DIR: str  # absolute path to h-e1/results/
RESULTS_DIR: str      # h-m1/results/
FIGURES_DIR: str      # h-m1/figures/

DATASETS: list[str] = ["trivia_qa", "nq"]   # recall-failure benchmarks only (no truthful_qa)
MODELS_TO_RUN: list[str] = ["llama2"]        # mistral optional
MAX_SAMPLES: dict[str, int]                  # {"trivia_qa": 2000, "nq": 2000}
P_VALUE_THRESHOLD: float = 0.05
SEED: int = 42
```

---

### Peakedness (`code/peakedness.py`)

**Dependencies**: numpy, scipy

```python
import numpy as np
from scipy.stats import mannwhitneyu
from typing import List, Dict

def compute_peakedness(token_logprobs: List[float]) -> float:
    """max(|logprobs|) / mean(|logprobs|); returns 1.0 on degenerate input."""
    ...

def analyze_group_peakedness(records: List[Dict]) -> Dict[str, List[float]]:
    """Split records by label (0=hallucinated, 1=correct), compute peakedness per group.
    
    Args:
        records: list of dicts with keys 'logprobs' (List[float]) and 'label' (int)
    Returns:
        {"hallucinated": [...], "correct": [...]}
    """
    ...

def test_peakedness_difference(
    hallucinated: List[float], correct: List[float]
) -> Dict:
    """Two-sided Mann-Whitney U test.
    
    Returns:
        {"statistic": float, "p_value": float, "direction": str,
         "mean_hallucinated": float, "mean_correct": float,
         "n_hallucinated": int, "n_correct": int}
    """
    ...
```

---

### Visualization (`code/visualization.py`)

**Dependencies**: matplotlib, seaborn, numpy, peakedness (for type hints)

```python
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict
import numpy as np

def plot_bar_comparison(
    group_data: Dict[str, Dict[str, List[float]]],  # {dataset: {group: [peakedness]}}
    save_path: str,
) -> None:
    """Bar chart: mean peakedness ± 95% CI, hallucinated vs correct, by dataset. MANDATORY gate figure."""
    ...

def plot_kde_distributions(
    group_data: Dict[str, List[float]],  # {"hallucinated": [...], "correct": [...]}
    dataset_name: str,
    save_path: str,
) -> None:
    """Overlapping KDE plots per dataset."""
    ...

def plot_scatter_auroc(
    peakedness: List[float],
    auroc_scores: List[float],
    labels: List[int],
    save_path: str,
) -> None:
    """Peakedness ratio vs H-E1 AUROC score per sample."""
    ...

def plot_boxplot(
    group_data: Dict[str, Dict[str, List[float]]],  # {dataset: {group: [peakedness]}}
    save_path: str,
) -> None:
    """Boxplot: peakedness by (dataset, label) — 4 boxes."""
    ...

def save_all_figures(
    all_results: Dict,  # full experiment results structure
    figures_dir: str,
) -> None:
    """Generate and save all 4 required figures."""
    ...
```

---

### Run Experiment (`code/run_experiment.py`)

**Dependencies**: config, peakedness, visualization, H-E1 inference/data_loader (via sys.path)

```python
import sys
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional

def load_or_run_inference(
    dataset_name: str,
    model_key: str,
    cache_path: str,
) -> List[Dict]:
    """Path A: load cached H-E1 raw records; Path B: re-run via H-E1 run_inference().
    
    Returns list of dicts with 'logprobs' and 'label' keys.
    """
    ...

def run_dataset(
    dataset_name: str,
    model_key: str,
    results_dir: str,
) -> Dict:
    """Run full peakedness analysis for one (dataset, model) pair.
    
    Returns stats dict from test_peakedness_difference + group peakedness arrays.
    """
    ...

def save_results(
    all_results: Dict,
    results_dir: str,
) -> None:
    """Cache peakedness arrays to .npz and summary to results_summary.json."""
    ...

def main() -> None:
    """Orchestrate: for each (model, dataset) → infer → peakedness → stats → cache → figures."""
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | H-M1 config.py + directory init + H-E1 sys.path wiring | 5 | 1+1+1+2 |
| A-2 | Peakedness Core | compute_peakedness + analyze_group_peakedness (with edge cases) | 7 | 2+1+2+2 |
| A-3 | Statistical Test | test_peakedness_difference (Mann-Whitney U, direction, summary dict) | 6 | 1+2+2+1 |
| A-4 | Data / Inference Path | load_or_run_inference: check H-E1 cache → fallback re-run via H-E1 modules | 12 | 2+4+3+3 |
| A-5 | Results Caching | save peakedness arrays to .npz + results_summary.json | 5 | 1+1+1+2 |
| A-6 | Visualization | All 4 figures: bar (gate), KDE, scatter, boxplot | 10 | 2+2+3+3 |
| A-7 | Experiment Orchestration | run_dataset + main loop over (model × dataset) | 9 | 2+3+2+2 |
| A-8 | Gate Validation | Verify p < 0.05 criterion met; print pass/fail summary | 5 | 1+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-6, A-7], Low(4-8): [A-1, A-2, A-3, A-5, A-8]

---

## Data Flow

- `run_experiment.py` calls `load_or_run_inference()` per (model, dataset)
  - Path A: load H-E1 `.npz` raw records if `logprobs` key present
  - Path B: import H-E1 `run_inference()` via `sys.path.insert(0, H_E1_CODE_DIR)`
- Records (with `logprobs`, `label`) passed to `analyze_group_peakedness()` → `test_peakedness_difference()`
- Stats + arrays passed to `save_results()` → `.npz` + `results_summary.json`
- Stats + arrays passed to `save_all_figures()` → 4 PNGs in `h-m1/figures/`

## Gate Check Logic

```python
gate_pass = any(
    result["p_value"] < P_VALUE_THRESHOLD
    for result in all_results.values()
)
```

Any one significant (model, dataset) pair → PASS, direction documented regardless.
