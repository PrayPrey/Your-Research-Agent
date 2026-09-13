# Architecture: H-M3
# Post-Breakpoint CoV Directional Skewness Analysis

**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Hypothesis:** H-M3 (MECHANISM / SHOULD_WORK)
**Gate:** ≥2 of 4 directional metrics pass (p < 0.10)

Applied: modular-pipeline pattern (data_loader → moments → tests → verifier → visualizer → main)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Analyzed actual H-M2 and H-E1 code via direct file reads (Serena project not activated)
**Analyzed Path**: `docs/youra_research/h-m2/code/`, `docs/youra_research/h-e1/code/`
**Findings**: H-M2 uses flat 5-module structure (`data_loader`, `analyzer`, `verifier`, `visualizer`, `main`). `data_loader.py` is fully reusable verbatim — `load_residual_cov` and `load_paper_count_star_idx` are exactly what H-M3 needs.

---

## File Structure

```
docs/youra_research/h-m3/code/
├── data_loader.py          # COPIED from H-M2 (no changes)
├── distributional_moments.py
├── directional_tests.py
├── verifier.py
├── visualization.py
├── results_output.py
├── main.py
├── tests/
│   └── test_h_m3.py
└── data/                   # symlink or copy of pwc_cov_computed.csv
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_residual_cov | `from data_loader import load_residual_cov` | `h-m2/code/data_loader.py` (copy to h-m3/code/) |
| load_paper_count_star_idx | `from data_loader import load_paper_count_star_idx` | `h-m2/code/data_loader.py` (copy to h-m3/code/) |

**Verified from**: `docs/youra_research/h-m2/code/data_loader.py` (actual implementation)
**H-E1 JSON path pattern**: `_H_E1_DIR / "experiment_results.json"` where `_H_E1_DIR = Path(__file__).parent.parent.parent / "h-e1"`
**CSV path pattern**: `docs/youra_research/h-m3/code/data/pwc_cov_computed.csv` (copy from H-E1 output)

---

## Module Definitions

### data_loader (`code/data_loader.py`)

**Dependencies**: numpy, pandas, (ruptures — fallback only)
**Source**: Copy verbatim from `h-m2/code/data_loader.py` — no modifications needed.

```python
def load_residual_cov(csv_path: Path) -> Tuple[np.ndarray, np.ndarray]: ...
    # returns (paper_counts, residual_cov) sorted ascending, validates N in [100,200]

def load_paper_count_star_idx(
    results_json_path: Path,
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
) -> int: ...
    # loads breakpoint_idx from H-E1 JSON; PELT fallback if absent
    # raises ValueError if idx at boundary or pre_segment < 3
```

---

### distributional_moments (`code/distributional_moments.py`)

**Dependencies**: numpy, scipy.stats

```python
from dataclasses import dataclass
from scipy.stats import describe as scipy_describe
import numpy as np

@dataclass
class SegmentMoments:
    n: int
    mean: float
    variance: float
    skewness: float
    kurtosis: float
    p10: float
    p25: float
    p75: float

def compute_moments(segment: np.ndarray) -> SegmentMoments: ...
    # scipy.stats.describe(segment, bias=False); np.percentile for tails
    # bias=False MANDATORY (adjusted Fisher-Pearson G1 for small N)

def compute_both_segments(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    breakpoint_idx: int,
) -> Tuple[SegmentMoments, np.ndarray, np.ndarray]: ...
    # splits pre/post, computes moments for each, returns (pre_moments, post_moments, pre_arr, post_arr)
    # logs n_pre, n_post; validates n_pre+n_post==len(residual_cov)
```

---

### directional_tests (`code/directional_tests.py`)

**Dependencies**: numpy, scipy.stats, distributional_moments.SegmentMoments

```python
from dataclasses import dataclass
from scipy.stats import permutation_test, mannwhitneyu, skew as scipy_skew
import numpy as np

@dataclass
class DirectionalTestResults:
    # Metric 1: skewness direction
    skew_pre: float
    skew_post: float
    metric1_pass: bool          # skew_post < skew_pre OR skew_post < 0

    # Metric 2: lower-tail concentration
    p10_pre: float
    p10_post: float
    metric2_pass: bool          # p10_post < p10_pre

    # Metric 3: permutation test on skewness difference
    perm_p_skew_diff: float
    metric3_pass: bool          # perm_p < 0.10

    # Metric 4: Mann-Whitney stochastic dominance
    mw_pvalue: float
    metric4_pass: bool          # mw_p < 0.10
    mw_statistic: float

def run_directional_tests(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    pre_moments: "SegmentMoments",
    post_moments: "SegmentMoments",
    n_resamples: int = 9999,
    random_state: int = 42,
    p_threshold: float = 0.10,
) -> DirectionalTestResults: ...
    # Metric 1: skew direction from moments (already computed, no recompute)
    # Metric 2: p10 comparison from moments
    # Metric 3: permutation_test with skew_diff_stat, alternative='two-sided', random_state=42
    # Metric 4: mannwhitneyu(pre, post, alternative='greater')
    # logs each metric result
```

---

### verifier (`code/verifier.py`)

**Dependencies**: directional_tests.DirectionalTestResults

```python
from dataclasses import dataclass
from directional_tests import DirectionalTestResults

@dataclass
class GateResult:
    metrics_passed: int
    gate_passed: bool           # metrics_passed >= 2
    gate_type: str              # "PASS" or "EXPLORE"
    verdict_message: str

def verify_directional_specificity(results: DirectionalTestResults) -> GateResult: ...
    # sums metric1..4 pass flags
    # gate_passed = metrics_passed >= 2
    # logs GATE: PASS/EXPLORE — N/4 directional metrics consistent with H1
    # on EXPLORE: logs scope limitation message
```

---

### visualization (`code/visualization.py`)

**Dependencies**: numpy, matplotlib, seaborn, distributional_moments.SegmentMoments, directional_tests.DirectionalTestResults

```python
from pathlib import Path
import numpy as np

def plot_gate_metrics(
    results: "DirectionalTestResults",
    gate: "GateResult",
    figures_dir: Path,
) -> Path: ...
    # MANDATORY: bar chart — skew pre/post + p10 pre/post + perm_p + mw_p
    # pass/fail coloring; metrics_passed annotation

def plot_histogram_overlay(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    pre_moments: "SegmentMoments",
    post_moments: "SegmentMoments",
    figures_dir: Path,
) -> Path: ...
    # semi-transparent histograms + KDE overlay; vertical lines at p10

def plot_moments_table(
    pre_moments: "SegmentMoments",
    post_moments: "SegmentMoments",
    figures_dir: Path,
) -> Path: ...
    # matplotlib table: mean, variance, skewness, kurtosis side-by-side

def plot_ecdf(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    pre_moments: "SegmentMoments",
    post_moments: "SegmentMoments",
    figures_dir: Path,
) -> Path: ...
    # empirical CDF, shaded lower-tail region p10-p25

def plot_qq(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    figures_dir: Path,
) -> Path: ...
    # pre vs post quantile-quantile plot

def save_all_figures(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    pre_moments: "SegmentMoments",
    post_moments: "SegmentMoments",
    results: "DirectionalTestResults",
    gate: "GateResult",
    figures_dir: Path,
) -> list[Path]: ...
    # calls all 5 plot functions, returns list of saved paths
```

---

### results_output (`code/results_output.py`)

**Dependencies**: json, pathlib, distributional_moments, directional_tests, verifier

```python
from pathlib import Path

def build_results_dict(
    pre_moments: "SegmentMoments",
    post_moments: "SegmentMoments",
    test_results: "DirectionalTestResults",
    gate: "GateResult",
    figure_paths: list[Path],
) -> dict: ...
    # assembles FR-11.2 JSON schema:
    # {n_pre, n_post, skew_pre, skew_post, kurt_pre, kurt_post,
    #  p10_pre, p10_post, perm_p_skew_diff, mw_pvalue,
    #  metric1_pass..metric4_pass, metrics_passed, gate_passed, gate_type}

def save_results(results_dict: dict, output_path: Path) -> None: ...
    # json.dump with indent=2; prints gate verdict to stdout
```

---

### main (`code/main.py`)

**Dependencies**: all modules above

```python
from pathlib import Path
import sys

_CODE_DIR = Path(__file__).parent
_H_M3_DIR = _CODE_DIR.parent
_H_E1_DIR = _H_M3_DIR.parent / "h-e1"

CSV_PATH = _CODE_DIR / "data" / "pwc_cov_computed.csv"
H_E1_JSON = _H_E1_DIR / "experiment_results.json"
RESULTS_PATH = _H_M3_DIR / "experiment_results.json"
FIGURES_DIR = _H_M3_DIR / "figures"

def main() -> int: ...
    # 1. load_residual_cov(CSV_PATH)
    # 2. load_paper_count_star_idx(H_E1_JSON, paper_counts, residual_cov)
    # 3. compute_both_segments(paper_counts, residual_cov, breakpoint_idx)
    # 4. run_directional_tests(pre_arr, post_arr, pre_moments, post_moments)
    # 5. verify_directional_specificity(test_results)
    # 6. save_all_figures(..., FIGURES_DIR)
    # 7. save_results(build_results_dict(...), RESULTS_PATH)
    # returns 0 if gate_passed else 1
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup project structure | Copy data_loader from H-M2, create dirs, copy CSV data | 6 | 2+1+1+2 |
| A-2 | Implement distributional_moments.py | SegmentMoments dataclass, compute_moments, compute_both_segments with split logic | 9 | 2+2+3+2 |
| A-3 | Implement directional_tests.py | All 4 metrics: skew direction, p10, permutation_test, mannwhitneyu | 13 | 3+3+4+3 |
| A-4 | Implement verifier.py | GateResult, verify_directional_specificity, ≥2/4 gate logic | 6 | 1+2+2+1 |
| A-5 | Implement visualization.py | 5 figures: gate_metrics, histogram_overlay, moments_table, ecdf, qq | 14 | 3+2+4+5 |
| A-6 | Implement results_output.py | build_results_dict, save_results, JSON schema per FR-11.2 | 7 | 2+2+2+1 |
| A-7 | Implement main.py | Wire all modules, path constants, error handling, return code | 8 | 2+3+2+1 |
| A-8 | Write tests/test_h_m3.py | Unit tests for moments, tests (known inputs), gate pass/fail, JSON schema | 10 | 2+2+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-3, A-8], Low(4-8): [A-1, A-2, A-4, A-6, A-7]

---

## Data Flow

- `data_loader` → `(paper_counts, residual_cov, breakpoint_idx)`
- `distributional_moments` → `(pre_moments, post_moments, pre_arr, post_arr)`
- `directional_tests` → `DirectionalTestResults` (4 metrics)
- `verifier` → `GateResult`
- `visualization` → `list[Path]` (5 figure files)
- `results_output` → `experiment_results.json`

## Key Constants

| Name | Value | Source |
|------|-------|--------|
| N_EXPECTED | 111 | H-E1 validated |
| P_THRESHOLD | 0.10 | SHOULD_WORK gate |
| METRICS_GATE | 2 | ≥2 of 4 required |
| N_RESAMPLES | 9999 | permutation_test |
| RANDOM_STATE | 42 | reproducibility |
| SKEW_BIAS | False | adjusted G1 for small N |
