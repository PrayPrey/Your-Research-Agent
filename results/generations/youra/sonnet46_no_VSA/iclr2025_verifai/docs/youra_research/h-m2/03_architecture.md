# Architecture: h-m2 — Contract Richness Stratification Analysis

**Applied**: standalone analysis pipeline pattern (no ML training)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**: H-M1 uses flat module layout — `data_loader.py`, `statistical_analysis.py`, `visualization.py`, `oracle_isolation.py`, `soundness_check.py`, `run_experiment.py`. H-M2 mirrors this flat structure. ContractEval data is loaded from a `.jsonl` file (not `.json`) at a path resolved relative to `__file__`. H-M1 results directory is `h-m1/code/results/` (not `h-m1/results/`).

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ContractEval loader | `from data_loader import load_contracteval` | `h-m1/code/data_loader.py` |
| bootstrap_ci | `from statistical_analysis import bootstrap_ci` | `h-m1/code/statistical_analysis.py` |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation)

**CRITICAL path note**: H-M1 per-task gap output is written by `statistical_analysis.save_results()`. Phase 4 must verify actual file path — likely `h-m1/code/results/per_task_oracle_gap.json`.

**ContractEval path**: H-M1 loads from a `.jsonl` file under `_archive/.../ContractEval/ContractEval.jsonl`. H-M2 `score_richness.py` must accept the same path or a separate `ContractEval/data/contracteval_tasks.json` from a fresh clone — configurable via constant.

---

## File Organization

```
h-m2/
  code/
    score_richness.py       # AST scoring
    analyze_correlation.py  # Spearman + Kruskal + ablations
    visualize.py            # 5 figures
    run_h_m2.py             # orchestrator
  results/
    h_m2_results.json
    richness_scores.csv
  figures/
    figure_gate_metrics.png
    figure_scatter.png
    figure_boxplot.png
    figure_heatmap.png
    figure_violin.png
```

---

## Modules

### RichnessScorer (`h-m2/code/score_richness.py`)

**Dependencies**: stdlib `ast`, `json`, `pathlib`, `pandas`, `dataclasses`

```python
from dataclasses import dataclass
from typing import List, Optional
import pandas as pd

H1_GAP_PATH: str  # constant: resolved relative to __file__
CONTRACTEVAL_PATH: str  # constant: resolved relative to __file__

@dataclass
class RichnessScore:
    task_id: str
    tier: int           # 1=simple, 2=structural, 3=relational, 4=compound
    score: float        # node_count + 3*has_quantifier + 2*has_relational
    has_quantifier: bool
    has_relational: bool
    node_count: int

def score_postcondition(assert_clauses: List[str]) -> tuple: ...
    # Returns (tier, score, has_quantifier, has_relational, node_count)
    # SyntaxError on malformed clause: skip clause, log warning

def build_richness_df(contracteval_path: Optional[str] = None) -> pd.DataFrame: ...
    # Returns DataFrame[task_id, tier, score, has_quantifier, has_relational, node_count]
    # shape == (364, 6), asserts all 4 tiers present

def load_gap_dict(gap_path: Optional[str] = None) -> dict: ...
    # Returns {task_id: float}, len == 364
    # Raises FileNotFoundError with "Run H-M1 first" if missing

def verify_mechanism_activated(richness_df: pd.DataFrame, gap_df: pd.DataFrame, results: dict) -> tuple: ...
    # Returns (passed: bool, indicators: dict)
    # Checks: richness_computed, all_tiers_present, gap_loaded, gradient_direction, spearman_computed
```

---

### CorrelationAnalyzer (`h-m2/code/analyze_correlation.py`)

**Dependencies**: `scipy.stats`, `numpy`, `pandas`, `score_richness.RichnessScore`

```python
from typing import dict
import pandas as pd
import numpy as np

def spearman_with_permutation(
    x: list, y: list,
    n_resamples: int = 9999,
    seed: int = 42
) -> dict: ...
    # Returns {rho, p_asymptotic, p_exact}
    # Uses scipy.stats.spearmanr(alternative='greater') + permutation_test(permutation_type='pairings')

def bootstrap_rho_ci(
    x: list, y: list,
    n_bootstrap: int = 10000,
    seed: int = 42
) -> tuple: ...
    # Returns (ci_lower, ci_upper)

def kruskal_wallis_tiers(richness_df: pd.DataFrame, gap_dict: dict) -> tuple: ...
    # Returns (KW_stat, KW_p)
    # Groups gap values by tier 1–4

def tier_means(richness_df: pd.DataFrame, gap_dict: dict) -> dict: ...
    # Returns {1: float, 2: float, 3: float, 4: float}

def run_ablations(richness_df: pd.DataFrame, gap_dict: dict, h1_results: dict) -> dict: ...
    # Ablation 1: discrete tier as IV
    # Ablation 2: per-model family rho (requires h1_results with per-model gaps)
    # Ablation 3: HumanEval+ (258) vs MBPP+ (106) subsets
    # Ablation 4: node_count only as IV
    # Returns dict keyed by ablation name

def run_full_analysis(richness_df: pd.DataFrame, gap_dict: dict, h1_results: dict) -> dict: ...
    # Runs primary test + KW + bootstrap CI + all ablations
    # Returns complete results dict matching h_m2_results.json schema
    # Flags FLAT_GRADIENT if rho < 0.15
```

---

### Visualizer (`h-m2/code/visualize.py`)

**Dependencies**: `matplotlib`, `seaborn`, `pandas`, `numpy`, `pathlib`

```python
from pathlib import Path
import pandas as pd

FIGURES_DIR: Path  # constant

def plot_gate_metrics(rho: float, threshold: float, p_value: float, out_dir: Path) -> None: ...
    # Bar chart: achieved rho vs threshold 0.30, p-value annotated

def plot_scatter(richness_df: pd.DataFrame, gap_dict: dict, rho: float, out_dir: Path) -> None: ...
    # Scatter: richness score (x) vs gap (y), colored by tier, rho annotated

def plot_boxplot(richness_df: pd.DataFrame, gap_dict: dict, out_dir: Path) -> None: ...
    # Box plot: gap distribution per tier 1–4

def plot_heatmap(richness_df: pd.DataFrame, h1_per_model_gaps: dict, out_dir: Path) -> None: ...
    # Heatmap: task richness tier x model family

def plot_violin(richness_df: pd.DataFrame, h1_contract_unique_mass: dict, out_dir: Path) -> None: ...
    # Violin: contract-unique failure mass by richness tier

def save_all(richness_df: pd.DataFrame, gap_dict: dict, results: dict, h1_results: dict, out_dir: Path) -> None: ...
    # Calls all 5 plot functions; single entry point for orchestrator
```

---

### Orchestrator (`h-m2/code/run_h_m2.py`)

**Dependencies**: `score_richness`, `analyze_correlation`, `visualize`, `json`, `pathlib`, `pandas`

```python
import sys
import json
from pathlib import Path

CODE_DIR: Path
ROOT: Path
RESULTS_DIR: Path
FIGURES_DIR: Path

def save_results(results: dict, richness_df, results_dir: Path) -> None: ...
    # Writes h_m2_results.json and richness_scores.csv

def main() -> None: ...
    # 1. load_gap_dict() — fail early if missing
    # 2. build_richness_df() — validate shape and tier coverage
    # 3. run_full_analysis()
    # 4. verify_mechanism_activated()
    # 5. save_all() figures
    # 6. save_results()
    # 7. Print gate result: PASS / FAIL / FLAT_GRADIENT
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | File structure, path constants, verify H-M1 output exists | 5 | 1+1+1+2 |
| A-2 | Data Loading | `load_gap_dict` + `build_richness_df` from ContractEval JSONL | 8 | 2+2+2+2 |
| A-3 | AST Scoring | `score_postcondition`: node walk, quantifier/relational detection, tier assignment, error handling | 10 | 3+1+4+2 |
| A-4 | Primary Stats | `spearman_with_permutation` + `bootstrap_rho_ci` + `kruskal_wallis_tiers` | 12 | 2+2+5+3 |
| A-5 | Ablation Studies | `run_ablations`: 4 ablations (tier discrete, per-model, subset, node-count-only) | 11 | 2+3+4+2 |
| A-6 | Mechanism Verification | `verify_mechanism_activated` + `tier_means` + gradient check | 7 | 2+2+2+1 |
| A-7 | Visualization | 5 figures: gate bar, scatter, boxplot, heatmap, violin | 10 | 2+2+3+3 |
| A-8 | Orchestration + Output | `run_h_m2.py` main, JSON + CSV output, FLAT_GRADIENT flag | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-5, A-7], Low(4-8): [A-1, A-2, A-6, A-8]

---

## Notes for Phase 4

- ContractEval actual format is `.jsonl` (multi-object JSON stream, see H-M1 `load_contracteval`). The `contract_assertions` field name must be confirmed against the actual file — H-M1 uses `test` field for CVT inputs. Phase 4 should print available keys on first load.
- H-M1 results dir is `h-m1/code/results/` — confirm `per_task_oracle_gap.json` path with `save_results` in `h-m1/code/statistical_analysis.py`.
- Per-model gaps for Ablation 2 require `AggregatedStats.by_model` from H-M1 results JSON.
- `scipy.stats.permutation_test` requires `scipy >= 1.7.0`; no new installs needed per NFR-3.
