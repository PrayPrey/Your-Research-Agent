# Architecture: H-M1 — Logit Delta Anisotropy Analysis

**Hypothesis ID:** H-M1
**Type:** MECHANISM (INCREMENTAL — extends H-E1)
**Date:** 2026-03-17

Applied: sequential-model-loading pattern (H-E1 validated)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns found from base code (direct file reads — Serena project not active)
**Analyzed Path:** `docs/youra_research/20260317_buildingtrust/h-e1/code/`
**Findings:** H-E1 has 5 modules — `config.py`, `data_loader.py`, `model_runner.py`, `analysis_pipeline.py`, `visualization.py`. Key APIs: `ModelRunner.extract_logprobs()` returns `np.ndarray [N, 4]`; `run_pair_extraction()` returns `{"mmlu": {"base": ndarray, "aligned": ndarray}, ...}`; `MCQDataLoader.format_prompt()` + `load_all_datasets()` are stable. All reused directly.

---

## File Organization

H-M1 code lives at `h-m1/code/`. H-E1 modules imported via `sys.path` insertion.

- `h-m1/code/config.py` — H-M1 config (model pairs, gate thresholds, paths)
- `h-m1/code/analysis_anisotropy.py` — NEW: delta computation + eigendecomposition
- `h-m1/code/visualization_anisotropy.py` — NEW: 5 anisotropy figures
- `h-m1/code/main.py` — H-M1 orchestrator
- `h-m1/cache/` — logit `.npy` files per pair/model/dataset
- `h-m1/figures/` — saved figure outputs
- `h-m1/experiment_results.json` — gate evaluation results

---

## Module Structure

### Config (`h-m1/code/config.py`)

**Dependencies:** none (stdlib only)

```python
import os

BASE_DIR: str        # h-m1/code/
HYPOTHESIS_DIR: str  # h-m1/

MODEL_PAIRS: list[dict]  # pair2, pair4, pair_new configs
# Each dict: {"pair_id": str, "base": str, "aligned": str, "method": str}

DATASETS: list[dict]  # mmlu, truthfulqa, arc — same as H-E1

CACHE_DIR: str        # h-m1/cache/
FIGURES_DIR: str      # h-m1/figures/
SEED: int             # 1

TORCH_DTYPE: str      # "float16"
DEVICE_MAP: str       # "auto"
BATCH_SIZE: int       # 1

GATE_THRESHOLDS: dict
# {"anisotropy_ratio_min": 1.0, "pvalue_max": 0.05, "families_min": 2}

VIZ_CONFIG: dict      # figsize, dpi, n_quintiles, save_formats
```

---

### AnisotropyAnalyzer (`h-m1/code/analysis_anisotropy.py`)

**Dependencies:** numpy, scipy.stats

```python
import numpy as np
from scipy import stats

def compute_logit_delta(
    base_logprobs: np.ndarray,    # [N, 4]
    aligned_logprobs: np.ndarray, # [N, 4]
) -> np.ndarray: ...              # returns delta [N, 4]

def compute_covariance_eigendecomposition(
    delta: np.ndarray,            # [N, 4]
) -> dict: ...
# returns: {"eigenvalues": ndarray[4], "eigenvectors": ndarray[4,4],
#           "cov_matrix": ndarray[4,4], "anisotropy_ratio": float}

def compute_anisotropy_significance(
    eigenvalues: np.ndarray,      # [4] descending
) -> dict: ...
# returns: {"t_stat": float, "p_value": float, "is_significant": bool}

def compute_decision_axis_projection(
    delta: np.ndarray,            # [N, 4]
    base_logprobs: np.ndarray,    # [N, 4]
) -> dict: ...
# returns: {"decision_axis_var": float, "orthogonal_vars": ndarray[3]}

def compute_margin_quintile_anisotropy(
    delta: np.ndarray,            # [N, 4]
    base_logprobs: np.ndarray,    # [N, 4]
    n_quintiles: int = 5,
) -> list[dict]: ...
# returns list of dicts per quintile: {"quintile": int, "anisotropy_ratio": float, "n_items": int}

def run_isotropic_sanity_check(n_items: int = 1000, seed: int = 1) -> dict: ...
# returns: {"anisotropy_ratio": float, "expected_approx_1": bool}

def run_anisotropy_analysis(
    pair_cfg: dict,
    datasets_logprobs: dict,      # {"mmlu": {"base": ndarray, "aligned": ndarray}, ...}
) -> dict: ...
# returns full per-pair anisotropy results dict

def evaluate_gate(
    all_pair_results: list[dict],
    gate_thresholds: dict,
) -> dict: ...
# returns: {"gate_result": str, "families_pass": int, "families_total": int, "pair_details": list}

def verify_mechanism_activated(
    pair_id: str,
    base_logprobs: np.ndarray,
    aligned_logprobs: np.ndarray,
    results: dict,
) -> tuple[bool, dict]: ...
# returns (activated: bool, indicators: dict)
```

---

### AnisotropyVisualizer (`h-m1/code/visualization_anisotropy.py`)

**Dependencies:** numpy, matplotlib, seaborn, sklearn.decomposition

```python
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

def plot_anisotropy_gate_metrics(
    all_pair_results: list[dict],
    gate_threshold: float,
    save_dir: str,
) -> None: ...
# Fig 1: bar chart anisotropy ratio per pair vs threshold r=1.0

def plot_eigenvalue_spectrum(
    all_pair_results: list[dict],
    save_dir: str,
) -> None: ...
# Fig 2: 4 eigenvalues per pair (flat=isotropic, spike=anisotropic)

def plot_delta_pca(
    delta: np.ndarray,             # [N, 4]
    base_logprobs: np.ndarray,     # [N, 4]
    pair_id: str,
    save_dir: str,
) -> None: ...
# Fig 3: 2D PCA scatter of delta, colored by margin quintile

def plot_anisotropy_by_quintile(
    quintile_results: list[dict],  # from compute_margin_quintile_anisotropy
    pair_id: str,
    save_dir: str,
) -> None: ...
# Fig 4: line chart r vs margin quintile (bridge to H-M2)

def plot_method_comparison(
    all_pair_results: list[dict],
    save_dir: str,
) -> None: ...
# Fig 5: box plots of per-item delta variance — decision vs orthogonal axes, by method

def save_all_figures(
    all_pair_results: list[dict],
    figures_dir: str,
) -> None: ...
# Calls all plot functions; handles per-pair and aggregate figures
```

---

### Main Orchestrator (`h-m1/code/main.py`)

**Dependencies:** config, analysis_anisotropy, visualization_anisotropy; h-e1/code via sys.path

```python
import sys, os, json, logging
from datetime import datetime

# sys.path.insert to reach h-e1/code modules
# from data_loader import load_all_datasets
# from model_runner import run_pair_extraction

from config import (MODEL_PAIRS, DATASETS, CACHE_DIR, FIGURES_DIR,
                    SEED, GATE_THRESHOLDS)
from analysis_anisotropy import run_anisotropy_analysis, evaluate_gate
from visualization_anisotropy import save_all_figures

def verify_tokenizer_compatibility(pair_cfg: dict, n_pilot: int = 100) -> bool: ...
# Loads tokenizer for base+aligned, checks token overlap for A/B/C/D option tokens

def save_results(results: dict, hypothesis_dir: str) -> str: ...
# Saves experiment_results.json to h-m1/

def print_gate_summary(results: dict) -> None: ...

def main() -> str: ...
# Full pipeline:
# 1. Load datasets (via h-e1 data_loader.load_all_datasets)
# 2. For each pair: tokenizer compat check; run_pair_extraction (h-e1); run_anisotropy_analysis
# 3. Isotropic sanity check
# 4. evaluate_gate
# 5. save_all_figures
# 6. save_results
# 7. print_gate_summary
# Returns gate_result string
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| MCQDataLoader | `from data_loader import MCQDataLoader` | `h-e1/code/data_loader.py` |
| load_all_datasets | `from data_loader import load_all_datasets` | `h-e1/code/data_loader.py` |
| ModelRunner | `from model_runner import ModelRunner` | `h-e1/code/model_runner.py` |
| run_pair_extraction | `from model_runner import run_pair_extraction` | `h-e1/code/model_runner.py` |

**Verified from:** `h-e1/code/` actual implementation.

**Import setup in main.py:**
```python
HE1_CODE = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code")
sys.path.insert(0, os.path.abspath(HE1_CODE))
```

**Key API signatures (verified):**
- `run_pair_extraction(pair_cfg, datasets, cache_dir, dataset_cfgs)` → `{"mmlu": {"base": ndarray[N,4], "aligned": ndarray[N,4]}, ...}`
- `load_all_datasets(dataset_cfgs)` → `{"mmlu": list[dict], "truthfulqa": list[dict], "arc": list[dict]}`
- `ModelRunner(model_id, torch_dtype, device_map)` + `.load()` / `.unload()`
- Cache path pattern from H-E1: `{cache_dir}/{pair_id}_{model_role}_{ds_name}.npy`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create h-m1/code/ structure, config.py with 3 pairs + gate thresholds, verify h-e1 import paths | 7 | Size:2 + Deps:2 + Algo:1 + Integ:2 |
| A-2 | Tokenizer Compatibility Check | Implement verify_tokenizer_compatibility() for pair_new pilot test (100 items), skip logic on mismatch | 8 | Size:2 + Deps:2 + Algo:2 + Integ:2 |
| A-3 | Logit Delta Computation | Implement compute_logit_delta(); integrate with run_pair_extraction output; save delta .npy files per pair | 9 | Size:2 + Deps:3 + Algo:2 + Integ:2 |
| A-4 | Covariance Eigendecomposition | Implement compute_covariance_eigendecomposition() + compute_anisotropy_significance(); np.linalg.eigh, eigenvalue validation | 12 | Size:3 + Deps:2 + Algo:4 + Integ:3 |
| A-5 | Secondary Analysis | compute_decision_axis_projection(), compute_margin_quintile_anisotropy(), run_isotropic_sanity_check() | 11 | Size:3 + Deps:2 + Algo:4 + Integ:2 |
| A-6 | Gate Evaluation | Implement evaluate_gate(): family count logic, paired t-test, PASS/FAIL logic for ≥2/3 families | 10 | Size:2 + Deps:2 + Algo:3 + Integ:3 |
| A-7 | run_anisotropy_analysis | Integrate delta+covariance+significance+secondary into single per-pair pipeline function | 10 | Size:3 + Deps:3 + Algo:2 + Integ:2 |
| A-8 | Mechanism Verification | Implement verify_mechanism_activated() with all 5 indicator checks; log activation per pair | 7 | Size:2 + Deps:2 + Algo:1 + Integ:2 |
| A-9 | Visualizations (Figs 1-3) | plot_anisotropy_gate_metrics, plot_eigenvalue_spectrum, plot_delta_pca | 11 | Size:3 + Deps:2 + Algo:3 + Integ:3 |
| A-10 | Visualizations (Figs 4-5) | plot_anisotropy_by_quintile, plot_method_comparison (DPO vs SFT vs PPO) | 9 | Size:3 + Deps:2 + Algo:2 + Integ:2 |
| A-11 | Main Orchestrator | Assemble full pipeline in main.py: dataset load → pair extraction → anisotropy → gate → figures → save | 13 | Size:3 + Deps:4 + Algo:2 + Integ:4 |
| A-12 | Results Serialization + Tests | save_results() to experiment_results.json; integration test with synthetic delta; validate output schema | 8 | Size:2 + Deps:2 + Algo:2 + Integ:2 |

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [A-4, A-5, A-6, A-7, A-9, A-10, A-11]
- Low (4-8): [A-1, A-2, A-3, A-8, A-12]

---

## Dependency Graph

```
config.py
    └── analysis_anisotropy.py
    └── visualization_anisotropy.py
    └── main.py

h-e1/code/data_loader.py  ──┐
h-e1/code/model_runner.py  ─┤── main.py
analysis_anisotropy.py ─────┤
visualization_anisotropy.py─┘
```

---

## Infrastructure Notes

- Conda env: `youra-h-e1` (Python 3.10, reuse)
- GPU: `CUDA_VISIBLE_DEVICES=0` (H100 NVL)
- Sequential loading: base → extract → save → unload → aligned → extract; never both in VRAM
- H-E1 cache reuse: if `h-e1/cache/{pair_id}_{role}_{ds}.npy` exists, `run_pair_extraction` loads from cache
- Seed: 1 (changed from H-E1 seed=42 — controlled as documented in PRD)
- Broken model IDs to skip: `allenai/tulu-2-ppo-7b` (404), `reciprocate/ppo_hh_pythia-1B` (tokenizer error)
