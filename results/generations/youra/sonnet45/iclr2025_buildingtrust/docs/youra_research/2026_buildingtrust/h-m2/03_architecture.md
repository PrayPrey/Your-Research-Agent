# Architecture: H-M2
## DPO vs PPO/SFT Logit Delta Variance in Low-Margin Regions

**Hypothesis ID:** H-M2
**Type:** MECHANISM (INCREMENTAL — extends H-M1)
**Date:** 2026-03-17

Applied: H-M1 incremental extension pattern (cache reuse + new analysis module)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Read directly via file system (Serena project activation failed — no active project error)
**Analyzed Path**: `docs/youra_research/20260317_buildingtrust/h-m1/code/`
**Findings**: H-M1 uses flat module structure — config.py (constants + dataclass dicts), analysis_anisotropy.py (compute_logit_delta + eigendecomposition), visualization_anisotropy.py, main.py. Cache loaded from h-e1/cache/ via pickle. Pattern: BASE_DIR-relative path resolution.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| compute_logit_delta | `sys.path.insert + from analysis_anisotropy import compute_logit_delta` | `h-m1/code/analysis_anisotropy.py` |
| H-E1 cache | `pickle.load(open(...))` | `h-e1/cache/{pair_id}_{dataset}_test_logprobs.pkl` |

**Verified from**: `h-m1/code/analysis_anisotropy.py` and `h-m1/code/config.py` (actual implementation)

**Import path resolution** (matches H-M1 pattern):
```python
import sys, os
HM1_CODE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "h-m1", "code"))
sys.path.insert(0, HM1_CODE_DIR)
from analysis_anisotropy import compute_logit_delta
```

---

## File Organization

```
h-m2/
  code/
    config.py              # constants, paths, gate thresholds
    analysis_variance.py   # core variance computation + statistical tests
    visualize.py           # 5 required figures
    run_analysis.py        # main entry point
    tests/
      __init__.py
      test_analysis_variance.py
      test_config.py
  figures/                 # output: *.pdf + *.png
  cache/                   # output: quintile_variances_*.npy
  experiment_results.json  # output
  04_checkpoint.yaml       # phase 4 tracking
```

---

## Module Definitions

### Config (`h-m2/code/config.py`)

**Dependencies**: os (stdlib)

```python
import os

BASE_DIR: str                    # os.path.dirname(os.path.abspath(__file__))
HYPOTHESIS_DIR: str              # h-m2/
HM1_CODE_DIR: str                # h-m1/code/ (for compute_logit_delta import)
HE1_CACHE_DIR: str               # h-e1/cache/

MODEL_PAIRS: list[dict]          # [{"pair_id": "pair2", "method": "DPO"}, {"pair_id": "pair4", "method": "SFT"}]
DATASETS: list[dict]             # [{"name": "mmlu", "n": 14042}, {"name": "truthfulqa", "n": 817}, {"name": "arc", "n": 1172}]

FIGURES_DIR: str                 # h-m2/figures/
CACHE_OUT_DIR: str               # h-m2/cache/
RESULTS_PATH: str                # h-m2/experiment_results.json

SEED: int                        # 1
N_QUINTILES: int                 # 5
MIN_QUINTILE_N: int              # 100
N_BOOTSTRAP: int                 # 5000

GATE_THRESHOLDS: dict            # {"pvalue_max": 0.05, "variance_ratio_min": 1.0, "benchmarks_min": 2}
VIZ_CONFIG: dict                 # {"figsize": (10, 6), "dpi": 150, "save_formats": ["pdf", "png"]}
```

---

### AnalysisVariance (`h-m2/code/analysis_variance.py`)

**Dependencies**: config, compute_logit_delta (h-m1), numpy, scipy

```python
import numpy as np
from scipy import stats
from typing import Optional

def load_h_e1_cache(
    pair_id: str,
    dataset: str,
    cache_dir: str,
) -> dict:
    """Returns dict with base_logprobs(N,4), aligned_logprobs(N,4), margin(N,), kl_div(N,)."""
    ...

def validate_cache(cache: dict, pair_id: str, dataset: str) -> None:
    """Raises ValueError on NaN, shape mismatch, or missing keys."""
    ...

def compute_quintile_labels(
    margin: np.ndarray,   # (N,)
    n_quintiles: int = 5,
) -> tuple[np.ndarray, np.ndarray]:
    """Returns (quintile_labels (N,) in [0..n_quintiles-1], boundaries (n_quintiles+1,))."""
    ...

def compute_variance_by_quintile(
    base_logprobs: np.ndarray,    # (N, 4)
    aligned_logprobs: np.ndarray, # (N, 4)
    margin: np.ndarray,           # (N,)
    kl_div: np.ndarray,           # (N,)
    n_quintiles: int = 5,
    kl_control: bool = True,
) -> dict:
    """
    Returns:
        quintile_variances: (n_quintiles,) KL-residualized delta variance per quintile
        quintile_counts: (n_quintiles,) item counts
        q1_residuals: (n_q1,) raw residuals for Q1 (used in t-test)
        kl_residualization_applied: bool
        boundaries: (n_quintiles+1,)
    """
    ...

def test_method_quintile_interaction(
    dpo_q1_residuals: np.ndarray,  # (n_dpo_q1,)
    sft_q1_residuals: np.ndarray,  # (n_sft_q1,)
    n_bootstrap: int = 5000,
    seed: int = 1,
) -> dict:
    """
    Returns:
        t_stat: float
        p_one_tailed: float
        cohens_d: float
        q1_variance_ratio: float
        bootstrap_ci: tuple[float, float]  # 95% CI on variance ratio
    """
    ...

def run_ablation_no_kl(
    base_logprobs: np.ndarray,
    aligned_logprobs: np.ndarray,
    margin: np.ndarray,
    kl_div: np.ndarray,
) -> dict:
    """Raw variance without KL residualization — ablation FR-5.2."""
    ...

def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """
    Checks: quintile_stratification_ok, variance_computed, kl_controlled, test_executed.
    Returns (all_pass: bool, indicators: dict).
    """
    ...

def run_isotropic_sanity_check(n: int = 1000, seed: int = 1) -> dict:
    """Gaussian delta control — expects flat quintile trend. Returns quintile_variances (5,)."""
    ...
```

---

### Visualize (`h-m2/code/visualize.py`)

**Dependencies**: config, numpy, matplotlib, seaborn

```python
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def plot_q1_variance_bar(
    results_per_dataset: dict,   # {dataset: {dpo_q1_var, sft_q1_var, p_one_tailed}}
    figures_dir: str,
) -> list[Path]:
    """Fig 1 (gate metric): bar chart DPO vs SFT Q1 variance with p-value annotation. FR-7.1."""
    ...

def plot_quintile_trend(
    quintile_data: dict,   # {dataset: {dpo: (5,), sft: (5,)}}
    figures_dir: str,
) -> list[Path]:
    """Fig 2: Q1-Q5 variance ratio line chart (DPO vs SFT) per dataset. FR-7.2."""
    ...

def plot_kl_scatter(
    scatter_data: dict,   # {pair_id: {kl_div: (N,), delta_var: (N,), quintile_labels: (N,)}}
    figures_dir: str,
) -> list[Path]:
    """Fig 3: delta_var vs kl_div colored by quintile. FR-7.3."""
    ...

def plot_benchmark_q1_grouped(
    benchmark_data: dict,   # {dataset: {dpo_q1_var, sft_q1_var, dpo_q1_std, sft_q1_std}}
    figures_dir: str,
) -> list[Path]:
    """Fig 4: grouped bar MMLU/TQA/ARC x DPO/SFT with error bars. FR-7.4."""
    ...

def plot_variance_ratio_heatmap(
    ratio_data: dict,   # {dataset: variance_ratio (5,)}
    figures_dir: str,
) -> list[Path]:
    """Fig 5: DPO/SFT variance ratio Q1-Q5 x dataset heatmap/line. FR-7.5."""
    ...

def save_figure(
    fig: plt.Figure,
    name: str,
    figures_dir: str,
    formats: list[str] = ("pdf", "png"),
) -> list[Path]: ...
```

---

### RunAnalysis (`h-m2/code/run_analysis.py`)

**Dependencies**: config, analysis_variance, visualize, json, logging

```python
import logging
from pathlib import Path

def setup_logging(hypothesis_dir: str) -> logging.Logger: ...

def load_all_caches(
    model_pairs: list[dict],
    datasets: list[dict],
    cache_dir: str,
) -> dict:
    """Returns nested dict: {pair_id: {dataset: cache_dict}}."""
    ...

def run_per_dataset_analysis(
    caches: dict,
    n_quintiles: int = 5,
    n_bootstrap: int = 5000,
    seed: int = 1,
) -> dict:
    """Runs compute_variance_by_quintile + test_method_quintile_interaction for all pairs x datasets."""
    ...

def evaluate_gate(results: dict) -> dict:
    """
    Applies cross-benchmark gate: significant (p < 0.05) on >= 2/3 datasets.
    Returns {"gate_pass": bool, "n_significant": int, "per_dataset": dict}.
    """
    ...

def save_results(results: dict, path: str) -> None: ...

def main() -> None:
    """Entry point: load caches → run analysis → visualize → evaluate gate → save results."""
    ...

if __name__ == "__main__":
    main()
```

---

### Tests (`h-m2/code/tests/test_analysis_variance.py`)

**Dependencies**: analysis_variance, numpy, pytest

```python
def test_compute_quintile_labels_uniform_distribution(): ...
def test_compute_quintile_labels_min_n_check(): ...
def test_compute_variance_by_quintile_shape(): ...
def test_compute_variance_by_quintile_kl_residualization(): ...
def test_compute_variance_by_quintile_no_kl_control(): ...
def test_test_method_quintile_interaction_returns_keys(): ...
def test_test_method_quintile_interaction_one_tailed(): ...
def test_verify_mechanism_activated_all_pass(): ...
def test_verify_mechanism_activated_missing_key(): ...
def test_run_isotropic_sanity_flat_trend(): ...
def test_load_h_e1_cache_missing_file_raises(): ...
def test_validate_cache_nan_raises(): ...
def test_bootstrap_ci_shape(): ...
def test_cohens_d_direction(): ...
def test_quintile_count_skip_below_min(): ...
```

---

## Data Flow

- `run_analysis.py:main` calls `load_all_caches` → 6 pickle files loaded
- Per pair x dataset: `compute_variance_by_quintile` → `(5,)` variances + Q1 residuals
- Cross-pair: `test_method_quintile_interaction(dpo_q1_residuals, sft_q1_residuals)` → stats dict
- Ablation: `run_ablation_no_kl` → raw variance comparison
- `evaluate_gate` applies 2/3 benchmark criterion
- `visualize.*` → 5 figures to `h-m2/figures/`
- `save_results` → `experiment_results.json`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | File structure, config.py, test scaffolding, path resolution for HM1 import | 6 | 1+1+2+2 |
| A-2 | Cache Loading | load_h_e1_cache, validate_cache, error handling for missing/NaN/shape | 8 | 2+2+2+2 |
| A-3 | Quintile Stratification | compute_quintile_labels, z-score margin, min-N check, boundary computation | 9 | 2+2+3+2 |
| A-4 | KL-Residualized Variance | compute_variance_by_quintile: delta→delta_var→OLS residualization→per-quintile var | 13 | 3+3+4+3 |
| A-5 | Statistical Testing | test_method_quintile_interaction: Welch's t (one-tailed), Cohen's d, bootstrap CI | 14 | 3+3+4+4 |
| A-6 | Ablation Variants | no-KL control, isotropic sanity check, per-dataset separation | 10 | 2+2+3+3 |
| A-7 | Mechanism Verification | verify_mechanism_activated, FR-6 logging (shapes, counts, KL flag) | 7 | 2+2+2+1 |
| A-8 | Gate Evaluation | evaluate_gate: 2/3 benchmark criterion, PASS/FAIL JSON output | 7 | 2+2+2+1 |
| A-9 | Visualization | 5 figures (bar, line, scatter, grouped bar, heatmap) → pdf+png | 14 | 3+2+4+5 |
| A-10 | Main Entry Point | run_analysis.py: orchestrate all modules, structured logging, checkpoint write | 10 | 2+3+3+2 |
| A-11 | Unit Tests | 15 test functions covering all core functions + edge cases | 11 | 3+2+3+3 |
| A-12 | Integration & Validation | End-to-end run on real cache data, results JSON verification, gate check | 12 | 3+3+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5, A-9], Medium(9-13): [A-4, A-6, A-10, A-11, A-12], Low(4-8): [A-1, A-2, A-3, A-7, A-8]

**Total task complexity**: 121 (12 epics, within FULL tier 30-task budget at ~10 subtasks/epic)

---

## Key Interfaces Summary

| Function | Input | Output |
|----------|-------|--------|
| `load_h_e1_cache` | pair_id, dataset, cache_dir | dict with 5 arrays |
| `compute_variance_by_quintile` | (N,4)x2 + (N,)x2 | quintile_variances(5,), q1_residuals(n,) |
| `test_method_quintile_interaction` | q1_residuals x2 | t_stat, p_one_tailed, cohens_d, ratio, CI |
| `verify_mechanism_activated` | results dict | (bool, indicators dict) |
| `evaluate_gate` | all_results dict | gate_pass bool, n_significant, per_dataset |

---

*Generated by Phase 3 Architecture Agent — H-M2 MECHANISM INCREMENTAL*
*Base hypothesis code verified from h-m1/code/ (actual implementation)*
*Archon KB: domain mismatch (diffusion content only) — no applicable patterns*
