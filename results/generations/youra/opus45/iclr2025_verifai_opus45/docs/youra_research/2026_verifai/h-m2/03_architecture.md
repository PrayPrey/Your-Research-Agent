# Architecture: H-M2 - G3 Superiority Over Minimal Feedback

**Date:** 2026-03-30
**Hypothesis Type:** MECHANISM (Post-hoc Statistical Analysis)
**Applied:** paired-comparison-analysis pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** patterns found from base code
**Analyzed Path:** `docs/youra_research/20260330_verifai/h-m1/code/`
**Findings:** H-M1 code has `repair_results.json` at `h-m1/results/repair_results.json`. Data format confirmed: list of records with `task_id`, `granularity` (G0-G4), `success` (bool), `repaired_code`, `execution_time`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| repair_results | `h-m1/results/repair_results.json` | `h-m1/results/repair_results.json` |
| repair_results (alt) | `h-m1/code/results/repair_results.json` | `h-m1/code/results/repair_results.json` |

**Verified from:** `docs/youra_research/20260330_verifai/h-m1/results/repair_results.json` (actual data)

**Data Schema (verified):**
```json
[
  {"task_id": 11, "granularity": "G0", "repaired_code": "...", "success": true, "execution_time": 1.72},
  ...
]
```

---

## File Organization

- `h-m2/code/`
  - `analyze.py` - main analysis entry point
  - `stats.py` - statistical tests (McNemar, rates, CI)
  - `visualize.py` - figure generation
  - `config.py` - paths and thresholds
  - `results/` - comparison_results.json, metrics.yaml
  - `figures/` - g0_vs_g3_comparison.png, contingency_heatmap.png, difference_ci.png, gate_summary.png

---

## Modules

### Config (`code/config.py`)

**Dependencies:** None

```python
from dataclasses import dataclass

@dataclass
class Config:
    h_m1_results_path: str = "../h-m1/results/repair_results.json"
    results_dir: str = "results"
    figures_dir: str = "figures"
    difference_threshold: float = 0.10   # 10 percentage points
    alpha: float = 0.05
    target_granularities: tuple = ("G0", "G3")
    expected_n_pairs: int = 304
```

---

### DataLoader (`code/analyze.py` - load section)

**Dependencies:** Config

```python
def load_paired_results(config: Config) -> tuple[list[int], list[int]]:
    """Load and pair G0/G3 outcomes from h-m1 results."""
    ...

def validate_paired_data(g0: list[int], g3: list[int], expected_n: int) -> None:
    """Assert paired structure and expected count."""
    ...
```

---

### StatisticalAnalysis (`code/stats.py`)

**Dependencies:** numpy, statsmodels, scipy

```python
import numpy as np
from statsmodels.stats.contingency_tables import mcnemar

def build_contingency_table(g0: list[int], g3: list[int]) -> np.ndarray: ...

def run_mcnemar_test(table: np.ndarray) -> dict:
    """Returns: statistic, pvalue, discordant_b, discordant_c, favors."""
    ...

def calculate_rates_and_difference(g0: list[int], g3: list[int]) -> dict:
    """Returns: g0_rate, g3_rate, difference, difference_pp, ci_lower_pp, ci_upper_pp."""
    ...

def evaluate_gate(rates: dict, mcnemar_result: dict, threshold: float) -> dict:
    """Returns: gate_passed, verdict, reason, difference_met, significant, favors_g3."""
    ...
```

---

### Visualizer (`code/visualize.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
def plot_comparison(rates: dict, output_dir: str) -> str: ...
def plot_contingency_heatmap(table: np.ndarray, output_dir: str) -> str: ...
def plot_difference_ci(rates: dict, output_dir: str) -> str: ...
def plot_gate_summary(rates: dict, gate: dict, output_dir: str) -> str: ...
```

---

### Analyze (entry point) (`code/analyze.py`)

**Dependencies:** Config, stats, visualize, json, yaml

```python
def main(config: Config) -> dict:
    """Orchestrate full analysis pipeline. Returns combined results dict."""
    ...

def save_results(results: dict, config: Config) -> None:
    """Save comparison_results.json and metrics.yaml."""
    ...

if __name__ == "__main__":
    cfg = Config()
    results = main(cfg)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create directory structure, config.py, verify h-m1 data path | 5 | 1+1+1+2 |
| A-2 | Data Loading | Load repair_results.json, extract paired G0/G3, validate 304 pairs | 7 | 2+1+2+2 |
| A-3 | Statistical Tests | McNemar's test, contingency table, rates + CI | 10 | 3+2+3+2 |
| A-4 | Gate Evaluation | Evaluate 10pp threshold + direction + significance | 7 | 2+2+2+1 |
| A-5 | Visualization | 4 figures: bar chart, heatmap, CI plot, gate summary | 9 | 2+1+3+3 |
| A-6 | Results Persistence | Save comparison_results.json, metrics.yaml | 6 | 2+1+1+2 |
| A-7 | Integration & Validation | End-to-end run, verify outputs, confirm pre-falsified result | 8 | 2+2+2+2 |

**Distribution:** VeryHigh(18-20): [] | High(14-17): [] | Medium(9-13): [A-3, A-5] | Low(4-8): [A-1, A-2, A-4, A-6, A-7]

---

## Data Flow

- `h-m1/results/repair_results.json`
  → `load_paired_results()` → `(g0_outcomes, g3_outcomes)` [304 pairs each]
  → `build_contingency_table()` → `2x2 np.ndarray`
  → `run_mcnemar_test()` → `{pvalue, favors, ...}`
  → `calculate_rates_and_difference()` → `{g0_rate=0.418, g3_rate=0.168, difference_pp=-25.0, ...}`
  → `evaluate_gate()` → `{gate_passed=False, verdict="FAIL", ...}`
  → `save_results()` + `visualize.*()` → `results/` + `figures/`

---

## Expected Outcome

Gate: **FAIL** (pre-falsified). G0 (41.8%) outperforms G3 (16.8%) by ~25pp, opposite of hypothesis direction. McNemar p expected << 0.05 favoring G0.
