# Architecture: H-M1
# Pre-Breakpoint Residual CoV Variance Characterization

**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Hypothesis:** H-M1 (MECHANISM / INCREMENTAL — extends H-E1)

Applied: lightweight-script-module-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Files read directly (Serena project activation unavailable); actual code analyzed via Read tool
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 flat layout — bare module imports via sys.path injection in run_experiment.py. `evaluate.py` already defines `verify_mechanism_activated()`. H-M1 mirrors the same flat structure.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ols_detrend | `from pipeline import ols_detrend` | `h-e1/code/pipeline.py` |
| run_pelt_changepoint | `from pipeline import run_pelt_changepoint` | `h-e1/code/pipeline.py` |
| verify_mechanism_activated (H-E1) | reference only — H-M1 defines its own | `h-e1/code/evaluate.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

**Note**: H-M1 does NOT import H-E1 modules at runtime. It reads H-E1 outputs (CSV + JSON) as data files only. If paper_count_star_idx is absent from H-E1 JSON, data_loader.py recomputes it using ruptures directly (same parameters as H-E1: l2 model, BIC penalty).

---

## File Structure

- `docs/youra_research/h-m1/code/`
  - `data_loader.py` — load H-E1 CSV/JSON outputs, validate, recompute idx if missing
  - `analyzer.py` — segment split, global variance, F-test, Brown-Forsythe preview
  - `verifier.py` — verify_mechanism_activated() gate check
  - `visualizer.py` — 4 required figures
  - `main.py` — orchestrate pipeline, save results JSON
- `docs/youra_research/h-m1/figures/` — output figures
- `docs/youra_research/h-m1/experiment_results.json` — output metrics

---

## Module Definitions

### DataLoader (`code/data_loader.py`)

**Dependencies**: pandas, numpy, ruptures, pathlib

```python
import numpy as np
import pandas as pd
from pathlib import Path
from typing import tuple

def load_residual_cov(csv_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load pwc_cov_computed.csv; return (paper_counts, residual_cov) sorted by paper_count asc.
    Raises ValueError if N != 111."""
    ...

def load_paper_count_star_idx(
    results_json_path: Path,
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
) -> int:
    """Load paper_count_star_idx from H-E1 experiment_results.json.
    If key absent, recompute via ruptures PELT (l2, BIC) on residual_cov.
    Raises ValueError if idx not in (0, 111)."""
    ...
```

---

### Analyzer (`code/analyzer.py`)

**Dependencies**: numpy, scipy

```python
import numpy as np
from scipy import stats
from typing import TypedDict

class AnalysisResults(TypedDict):
    n_pre: int
    n_post: int
    global_variance: float
    global_mean: float
    pre_variance: float
    pre_mean: float
    post_variance: float
    post_mean: float
    F_stat: float
    p_one_tailed: float
    variance_ratio_pre_global: float
    pre_mean_positive: bool
    bf_stat: float
    bf_p: float
    gate_passed: bool

def compute_global_variance(residual_cov: np.ndarray) -> tuple[float, float]:
    """Return (global_variance, global_mean) for full N=111 series."""
    ...

def split_segments(
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Split residual_cov at idx; return (pre, post). Raises if len(pre) < 3."""
    ...

def run_f_test(
    pre: np.ndarray,
    global_var: float,
    n_total: int,
) -> tuple[float, float, float]:
    """One-sample F-test: pre_var / global_var ~ F(n_pre-1, n_total-1).
    Return (F_stat, p_one_tailed, variance_ratio_pre_global)."""
    ...

def run_brown_forsythe(pre: np.ndarray, post: np.ndarray) -> tuple[float, float]:
    """scipy.stats.levene(pre, post, center='median'). Return (bf_stat, bf_p)."""
    ...

def analyze(residual_cov: np.ndarray, paper_count_star_idx: int) -> AnalysisResults:
    """Full analysis pipeline. Returns AnalysisResults dict."""
    ...
```

---

### Verifier (`code/verifier.py`)

**Dependencies**: analyzer (AnalysisResults type)

```python
from analyzer import AnalysisResults
from typing import tuple

def verify_mechanism_activated(
    results: AnalysisResults,
) -> tuple[bool, dict[str, bool]]:
    """Gate check: p_one_tailed < 0.10 AND variance_ratio_pre_global > 1.0.
    Returns (activated, indicators) where indicators has keys:
    pre_var_computed, global_var_computed, ratio_above_one,
    f_stat_computed, p_value_computed."""
    ...
```

---

### Visualizer (`code/visualizer.py`)

**Dependencies**: matplotlib, seaborn, numpy, pathlib

```python
import numpy as np
from pathlib import Path

def plot_variance_bar(
    global_var: float,
    pre_var: float,
    post_var: float,
    p_one_tailed: float,
    out_dir: Path,
) -> Path:
    """Bar chart: global_var vs pre_var vs post_var with F-test p annotation.
    Saves fig01_variance_bar.png. Returns path."""
    ...

def plot_scatter_with_breakpoint(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
    out_dir: Path,
) -> Path:
    """Scatter residual_CoV vs paper_count, vertical line at breakpoint,
    colored pre (blue) / post (red). Saves fig02_scatter.png."""
    ...

def plot_kde_overlay(
    pre: np.ndarray,
    post: np.ndarray,
    residual_cov: np.ndarray,
    out_dir: Path,
) -> Path:
    """KDE of pre / post / full-series. Saves fig03_kde.png."""
    ...

def plot_boxplot(
    pre: np.ndarray,
    post: np.ndarray,
    residual_cov: np.ndarray,
    out_dir: Path,
) -> Path:
    """Box plots: pre / post / full-series. Saves fig04_boxplot.png."""
    ...

def save_all_figures(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
    results: dict,
    out_dir: Path,
) -> list[Path]:
    """Call all 4 plot functions. Return list of saved paths."""
    ...
```

---

### Main (`code/main.py`)

**Dependencies**: data_loader, analyzer, verifier, visualizer, json, pathlib

```python
import sys
import json
from pathlib import Path

def main() -> int:
    """Orchestrate: load → analyze → verify → visualize → save JSON.
    Returns 0 on PASS, 1 on FAIL gate, 2 on early-fail."""
    ...

if __name__ == "__main__":
    sys.exit(main())
```

---

## Data Flow

- `data_loader.load_residual_cov` → `(paper_counts, residual_cov)`
- `data_loader.load_paper_count_star_idx` → `paper_count_star_idx`
- `analyzer.analyze` → `AnalysisResults`
- `verifier.verify_mechanism_activated` → `(gate_passed, indicators)`
- `visualizer.save_all_figures` → 4 PNGs in `figures/`
- `json.dump(results)` → `experiment_results.json`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create code/ dir, main.py skeleton, sys.path injection pattern (mirror H-E1) | 5 | 1+1+1+2 |
| A-2 | Data Loader | load_residual_cov + load_paper_count_star_idx with fallback PELT recompute + validation guards | 11 | 2+2+4+3 |
| A-3 | Analyzer — Segment Split & Global Variance | split_segments, compute_global_variance, segment stat computations | 8 | 2+1+3+2 |
| A-4 | Analyzer — F-Test & Brown-Forsythe | run_f_test (one-sample F, one-tailed), run_brown_forsythe, analyze() orchestration | 10 | 2+2+4+2 |
| A-5 | Verifier | verify_mechanism_activated gate logic + indicators dict | 6 | 1+2+2+1 |
| A-6 | Visualizer | 4 figure functions + save_all_figures wrapper | 10 | 2+2+3+3 |
| A-7 | Main Orchestrator & JSON Output | main() pipeline, experiment_results.json write, gate pass/fail stdout | 7 | 1+3+1+2 |
| A-8 | Integration Test | Single end-to-end smoke test: mock H-E1 CSV/JSON, assert gate fields present | 6 | 1+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-6], Low(4-8): [A-1, A-3, A-5, A-7, A-8]
