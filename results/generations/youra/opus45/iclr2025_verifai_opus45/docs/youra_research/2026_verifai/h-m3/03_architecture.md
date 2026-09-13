# Architecture: H-M3 Non-Monotonicity Confirmation (G3 >= G4)

**Date:** 2026-03-30
**Hypothesis:** G4 (full trace) does not significantly outperform G3 (G4 <= G3 + 2%)
**Type:** MECHANISM (Statistical Reanalysis)
**Gate:** SHOULD_WORK

Applied: statistical-reanalysis-minimal-pipeline

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (Read-based analysis; Serena project activation attempted but fell back to direct file read)
**Analyzed Path**: `docs/youra_research/20260330_verifai/h-m1/code/`
**Findings**: H-M1 uses flat single-directory layout (`config.py`, `data.py`, `model.py`, `train.py`, `evaluate.py`, `analyze.py`, `feedback.py`, `executor.py`, `repair.py`). Results stored in `results/repair_results.json` with fields `task_id` (int), `granularity` (str: "G0"-"G4"), `success` (bool), `execution_time` (float). H-M3 reads this file directly — no model inference needed.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| repair_results.json | `json.load(open("../h-m1/code/results/repair_results.json"))` | `h-m1/code/results/repair_results.json` |
| RepairConfig | Not reused (H-M3 has own config) | `h-m1/code/config.py` |

**Verified from**: `h-m1/code/results/repair_results.json` (actual data)
**Key field names confirmed**: `task_id` (int), `granularity` ("G3"/"G4"), `success` (bool)

---

## File Organization

- `h-m3/code/`
  - `config.py` - paths, margin, alpha thresholds
  - `data_loader.py` - load and validate H-M1 results, extract paired outcomes
  - `statistics.py` - contingency table, McNemar, TOST, CI
  - `evaluate.py` - gate condition evaluation
  - `visualize.py` - all figure generation
  - `train.py` - orchestration entry point
  - `results/` - JSON/YAML output files
  - `figures/` - PNG outputs

---

## Module Definitions

### Config (`config.py`)

**Dependencies**: None

```python
from dataclasses import dataclass, field

H_M1_RESULTS_PATH: str = "../h-m1/code/results/repair_results.json"

@dataclass
class AnalysisConfig:
    h_m1_results_path: str = H_M1_RESULTS_PATH
    equivalence_margin: float = 0.02
    alpha: float = 0.05
    confidence: float = 0.95
    results_dir: str = "results"
    figures_dir: str = "figures"
    output_contingency: str = "results/contingency_table.json"
    output_stats: str = "results/statistical_tests.yaml"
    output_metrics: str = "results/metrics.yaml"
```

---

### DataLoader (`data_loader.py`)

**Dependencies**: config.py

```python
import json
import numpy as np
from pathlib import Path
from config import AnalysisConfig

def load_h_m1_results(path: str) -> list[dict]: ...
    # Returns: list of {task_id, granularity, success, ...}

def extract_paired_outcomes(
    results: list[dict]
) -> tuple[list[bool], list[bool], list[int]]:
    # Returns: (g3_outcomes, g4_outcomes, problem_ids)
    # Pairs by task_id; validates lengths match

def validate_data_integrity(
    g3_outcomes: list[bool],
    g4_outcomes: list[bool],
    problem_ids: list[int]
) -> dict:
    # Returns: {n_pairs, g3_count, g4_count, valid}
```

---

### Statistics (`statistics.py`)

**Dependencies**: config.py

```python
import numpy as np
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.proportion import (
    tost_proportions_2indep,
    confint_proportions_2indep,
)
import scipy.stats as stats

def build_contingency_table(
    g3: list[bool], g4: list[bool]
) -> np.ndarray:
    # 2x2 table: rows=G3, cols=G4

def run_mcnemar_test(table: np.ndarray) -> dict:
    # Returns: {statistic, pvalue, significant, interpretation}

def run_tost_equivalence(
    g3_successes: int, g3_total: int,
    g4_successes: int, g4_total: int,
    margin: float = 0.02
) -> dict:
    # Returns: {g3_rate, g4_rate, difference, p_lower, p_upper, tost_pvalue, equivalent, interpretation}

def compute_confidence_interval(
    g3_successes: int, g3_total: int,
    g4_successes: int, g4_total: int,
    confidence: float = 0.95
) -> dict:
    # Returns: {point_estimate, ci_lower, ci_upper, confidence, interpretation}
```

---

### Evaluate (`evaluate.py`)

**Dependencies**: statistics.py, config.py

```python
from config import AnalysisConfig

def evaluate_gate_condition(
    g3_rate: float,
    g4_rate: float,
    mcnemar_pvalue: float,
    margin: float = 0.02
) -> dict:
    # Returns: {g3_rate, g4_rate, difference, within_margin, gate_passed, reason}

def save_results(
    contingency_table,
    mcnemar_result: dict,
    tost_result: dict,
    ci_result: dict,
    gate_result: dict,
    cfg: AnalysisConfig
) -> None:
    # Saves contingency_table.json, statistical_tests.yaml, metrics.yaml
```

---

### Visualize (`visualize.py`)

**Dependencies**: config.py

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from config import AnalysisConfig

def plot_gate_comparison(
    g3_rate: float, g4_rate: float,
    margin: float, output_path: str
) -> None:
    # Bar chart: G3 vs G4 with margin threshold line (MANDATORY)

def plot_contingency_heatmap(
    table: np.ndarray, output_path: str
) -> None:
    # 2x2 heatmap of paired outcomes

def plot_confidence_interval(
    ci_result: dict, output_path: str
) -> None:
    # Point estimate + 95% CI for G4-G3 difference

def plot_granularity_curve(
    results: list[dict], output_path: str
) -> None:
    # G0-G4 success rates showing non-monotonic pattern from H-M1

def generate_all_figures(
    g3_rate: float, g4_rate: float,
    table: "np.ndarray",
    ci_result: dict,
    results: list[dict],
    cfg: AnalysisConfig
) -> None: ...
```

---

### Train / Orchestrator (`train.py`)

**Dependencies**: config.py, data_loader.py, statistics.py, evaluate.py, visualize.py

```python
from config import AnalysisConfig
from data_loader import load_h_m1_results, extract_paired_outcomes, validate_data_integrity
from statistics import (
    build_contingency_table, run_mcnemar_test,
    run_tost_equivalence, compute_confidence_interval
)
from evaluate import evaluate_gate_condition, save_results
from visualize import generate_all_figures

def run_analysis(cfg: AnalysisConfig) -> dict:
    # Full pipeline: load -> extract -> stats -> gate -> save -> visualize
    # Returns gate_result dict

if __name__ == "__main__":
    cfg = AnalysisConfig()
    result = run_analysis(cfg)
    print(f"Gate: {'PASS' if result['gate_passed'] else 'FAIL'} — {result['reason']}")
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create h-m3/code/ structure, config.py, verify H-M1 data path | 5 | 1+1+1+2 |
| A-2 | Data Loader | Implement load_h_m1_results, extract_paired_outcomes, validate_data_integrity | 7 | 2+1+2+2 |
| A-3 | Contingency Table | Build 2x2 table from paired boolean outcomes, validate marginals | 6 | 2+1+2+1 |
| A-4 | McNemar's Test | run_mcnemar_test using statsmodels exact binomial, format results | 7 | 2+2+2+1 |
| A-5 | TOST Equivalence | run_tost_equivalence with 2% margin, both one-sided p-values | 9 | 2+2+3+2 |
| A-6 | Confidence Interval | compute_confidence_interval for G4-G3 difference, CI bounds | 7 | 2+1+2+2 |
| A-7 | Gate Evaluation | evaluate_gate_condition logic + save_results to JSON/YAML | 8 | 2+2+2+2 |
| A-8 | Visualizations | All 4 figures: gate comparison, heatmap, CI plot, granularity curve | 9 | 3+1+2+3 |
| A-9 | Orchestration | train.py pipeline wiring + end-to-end run + logging | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5, A-8], Low(4-8): [A-1, A-2, A-3, A-4, A-6, A-7, A-9]

---

## Output Files

| File | Content |
|------|---------|
| `results/contingency_table.json` | 2x2 table as nested list + cell labels |
| `results/statistical_tests.yaml` | McNemar, TOST, CI results with timestamps |
| `results/metrics.yaml` | Gate evaluation, g3_rate, g4_rate, difference |
| `figures/gate_comparison.png` | MANDATORY: bar chart with 2% margin line |
| `figures/contingency_heatmap.png` | 2x2 paired outcome matrix |
| `figures/confidence_interval.png` | 95% CI for G4-G3 difference |
| `figures/granularity_curve.png` | G0-G4 success rates (non-monotonic pattern) |

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| scipy | >=1.10.0 | stats.norm for TOST z-tests |
| statsmodels | >=0.14.0 | mcnemar, tost_proportions_2indep |
| numpy | >=1.24.0 | array operations |
| matplotlib | >=3.7.0 | figure generation |
| seaborn | >=0.12.0 | heatmap |
| pyyaml | >=6.0 | results persistence |
