# Architecture: H-M1 — MMLU Scale Covariate Pre-Test

**Applied**: standard statistical pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 uses flat single-directory layout — `config.py` (dataclass config + yaml loader), `run_audit.py` (all logic in one file), figures written to a path from config. H-M1 mirrors this pattern exactly. No submodule structure needed.

---

## File Structure

- `docs/youra_research/h-m1/code/`
  - `config.py` — dataclass config (paths, thresholds, seed)
  - `analyze.py` — all analysis logic (load, correlate, gate, visualize, save)
  - `main.py` — entry point (load config, call analyze, print gate result)
  - `requirements.txt`
  - `results/` — JSON + TXT outputs (created at runtime)
- `docs/youra_research/h-m1/figures/` — 4 saved figures

---

## Modules

### Config (`config.py`)

**Dependencies**: stdlib only

```python
from dataclasses import dataclass

@dataclass
class AnalysisConfig:
    # Data
    data_path: str = "../../h-e1/code/data/llm_leaderboard_v1/llm.csv"
    required_cols: tuple = ("model_name", "TruthfulQA_MC2", "BBQ_accuracy", "MMLU")

    # Gate
    r2_threshold: float = 0.05
    n_min: int = 30

    # Output
    figures_dir: str = "../../../youra_research/h-m1/figures"
    results_dir: str = "./results"
    seed: int = 42
```

---

### Analyzer (`analyze.py`)

**Dependencies**: AnalysisConfig, scipy, pandas, numpy, matplotlib, seaborn

```python
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from config import AnalysisConfig

def load_data(cfg: AnalysisConfig) -> pd.DataFrame:
    """Load H-E1 CSV, drop nulls, normalize BBQ to [0,100]. Raises on N < cfg.n_min."""
    ...

def compute_correlations(df: pd.DataFrame) -> dict:
    """
    Returns:
        N, rho_mmlu_truthqa, R2_mmlu_truthqa, p_mmlu_truthqa,
        rho_mmlu_bbq, R2_mmlu_bbq, p_mmlu_bbq,
        raw_rho_truth_bbq, p_raw,
        gate_pass
    """
    ...

def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """Check all R² are non-NaN in [0,1], N>=30, gate_pass key exists."""
    ...

def plot_r2_bar(results: dict, cfg: AnalysisConfig) -> str:
    """Bar chart R²(MMLU×TruthfulQA) and R²(MMLU×BBQ) vs 0.05 threshold. Returns save path."""
    ...

def plot_scatter_mmlu_truthqa(df: pd.DataFrame, results: dict, cfg: AnalysisConfig) -> str:
    """Scatter MMLU vs TruthfulQA MC2, rho annotated. Returns save path."""
    ...

def plot_scatter_mmlu_bbq(df: pd.DataFrame, results: dict, cfg: AnalysisConfig) -> str:
    """Scatter MMLU vs BBQ accuracy, rho annotated. Returns save path."""
    ...

def plot_correlation_heatmap(df: pd.DataFrame, cfg: AnalysisConfig) -> str:
    """Spearman correlation heatmap for {MMLU, TruthfulQA_MC2, BBQ_accuracy}. Returns save path."""
    ...

def save_results(results: dict, cfg: AnalysisConfig) -> None:
    """Save results to h_m1_results.json and h_m1_summary.txt in cfg.results_dir."""
    ...

def run(cfg: AnalysisConfig) -> dict:
    """Orchestrate: load → correlate → verify → plot × 4 → save → return results."""
    ...
```

---

### Entry Point (`main.py`)

**Dependencies**: AnalysisConfig, run (from analyze)

```python
from config import AnalysisConfig
from analyze import run

def main() -> None:
    """Instantiate config, call run(), print gate result, exit 0/1."""
    ...

if __name__ == "__main__":
    main()
```

---

## External Dependencies (Base Hypothesis)

| Asset | Location | Usage |
|-------|----------|-------|
| H-E1 joint CSV | `docs/youra_research/h-e1/code/data/llm_leaderboard_v1/llm.csv` | Primary data input |
| H-E1 config pattern | `docs/youra_research/h-e1/code/config.py` | Dataclass + figures_dir pattern reused |
| H-E1 run pattern | `docs/youra_research/h-e1/code/run_audit.py` | Flat-file analysis structure reused |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create file structure, requirements.txt, config.py | 5 | 1+1+1+2 |
| A-2 | Data Loading | load_data(): read CSV, drop nulls, normalize BBQ, validate N≥30 | 7 | 2+1+2+2 |
| A-3 | Correlation Analysis | compute_correlations(): spearmanr for 3 pairs, R² computation, gate eval | 8 | 2+2+2+2 |
| A-4 | Mechanism Verification | verify_mechanism_activated(): NaN checks, range checks, key checks | 5 | 1+1+2+1 |
| A-5 | Visualization | 4 figures: bar chart, 2 scatters, heatmap — save to figures dir | 9 | 2+1+3+3 |
| A-6 | Results Persistence | save_results(): JSON + TXT to results dir | 5 | 1+1+1+2 |
| A-7 | Entry Point & Integration | main.py wiring, logging, exit codes, end-to-end smoke test | 7 | 1+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5], Low(4-8): [A-1, A-2, A-3, A-4, A-6, A-7]

---

## Data Flow

- `main.py` → `run(cfg)` in `analyze.py`
- `run` calls: `load_data` → `compute_correlations` → `verify_mechanism_activated` → `plot_*` × 4 → `save_results`
- All outputs: figures to `docs/youra_research/h-m1/figures/`, JSON+TXT to `code/results/`
- Gate result logged and returned; `main.py` exits 0 on gate PASS, 0 on publishable null, 1 on execution error
