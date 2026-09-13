# Architecture: H-M1
# Partial Spearman Correlation — BBQ Fairness Cross-Split Predictive Validity

**Date:** 2026-08-20
**Hypothesis Type:** MECHANISM (PoC statistical analysis)
**Applied:** minimal-statistical-analysis pattern (no neural modules)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from H-E1 actual code (file structure via glob)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 exports `paper_scores.load_paper_scores()` returning `{source: {model: {metric: float}}}`. `config.CANONICAL_MAP` and `config.MMLU_SCORES` exist as dicts. H-M1 imports these directly — no reimplementation.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_paper_scores | `from ..h_e1.code.paper_scores import load_paper_scores` | `h-e1/code/paper_scores.py` |
| CANONICAL_MAP | `from ..h_e1.code.config import CANONICAL_MAP` | `h-e1/code/config.py` |
| MMLU_SCORES | `from ..h_e1.code.paper_scores import MMLU_SCORES` | `h-e1/code/paper_scores.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

> Note: H-M1 code lives at `docs/youra_research/h-m1/code/`. Import paths assume the `docs/youra_research/` directory is on sys.path, or use direct file path loading.

---

## File Structure

- `h-m1/code/config.py` — constants, gate thresholds, paths
- `h-m1/code/data.py` — assemble score DataFrame from H-E1 data + Winogrande
- `h-m1/code/analysis.py` — raw Spearman ρ, partial Spearman ρ, sensitivity, gate check
- `h-m1/code/visualize.py` — all 5 required figures
- `h-m1/code/run_experiment.py` — entry point; calls data → analysis → visualize → report
- `h-m1/data/` — output CSV (h_m1_scores.csv)
- `h-m1/figures/` — output PNGs
- `h-m1/results/` — results JSON

---

## Module Definitions

### Config (`h-m1/code/config.py`)

**Dependencies**: none

```python
from pathlib import Path

GATE_RHO: float = 0.4
GATE_P: float = 0.05
N_COMMON_MIN: int = 10
RANDOM_SEED: int = 1

# Winogrande scores for sensitivity analysis (from Open LLM Leaderboard)
WINOGRANDE_SCORES: dict[str, float] = { ... }  # populated in file

_HERE = Path(__file__).parent.parent
DATA_DIR = _HERE / "data"
FIGURES_DIR = _HERE / "figures"
RESULTS_DIR = _HERE / "results"
```

---

### DataAssembler (`h-m1/code/data.py`)

**Dependencies**: `h-e1/code/paper_scores.py`, `h-e1/code/config.py`, `config.py`

```python
import pandas as pd

def build_score_dataframe() -> pd.DataFrame:
    """
    Returns DataFrame columns: [model_name, bbq_disambig, bbq_ambig, mmlu, winogrande]
    Rows: N_common models with all scores present.
    Logs model name mappings and N_common.
    Saves to DATA_DIR/h_m1_scores.csv.
    """
    ...

def verify_n_common(df: pd.DataFrame, min_n: int = 10) -> int:
    """Assert len(df) >= min_n, return N_common."""
    ...
```

---

### StatAnalysis (`h-m1/code/analysis.py`)

**Dependencies**: `data.py`, `config.py`, `pingouin`, `scipy`

```python
import pandas as pd

def compute_raw_spearman(df: pd.DataFrame) -> dict:
    """
    scipy.stats.spearmanr on bbq_disambig × bbq_ambig.
    Returns: {raw_rho, raw_p, n}
    """
    ...

def compute_partial_spearman(df: pd.DataFrame, covar: str = "mmlu") -> dict:
    """
    pingouin.partial_corr(x='bbq_disambig', y='bbq_ambig', covar=[covar],
                          method='spearman', alternative='greater')
    Returns: {partial_rho, p_value, ci95, n, covar}
    """
    ...

def evaluate_gate(partial_rho: float, p_value: float) -> bool:
    """Return partial_rho > GATE_RHO and p_value < GATE_P."""
    ...

def run_full_analysis(df: pd.DataFrame) -> dict:
    """
    Runs raw + partial (MMLU) + partial (Winogrande) + gate check.
    Asserts mechanism verification conditions.
    Returns consolidated results dict. Saves to RESULTS_DIR/results.json.
    """
    ...
```

---

### Visualizer (`h-m1/code/visualize.py`)

**Dependencies**: `analysis.py`, `matplotlib`, `seaborn`

```python
import pandas as pd

def plot_gate_metrics(results: dict, save_dir) -> None:
    """Bar chart: partial_rho vs raw_rho, CI error bars, gate threshold line.
    Saves: figures/gate_metrics_comparison.png"""
    ...

def plot_rank_scatter(df: pd.DataFrame, results: dict, save_dir) -> None:
    """BBQ-Disambig rank vs BBQ-Ambig rank, model labels, correlation line.
    Saves: figures/rank_scatter_bbq.png"""
    ...

def plot_sensitivity(results: dict, save_dir) -> None:
    """Bar chart: rho_mmlu vs rho_winogrande.
    Saves: figures/sensitivity_comparison.png"""
    ...

def plot_score_distributions(df: pd.DataFrame, save_dir) -> None:
    """Box plots: bbq_disambig + bbq_ambig across models.
    Saves: figures/score_distributions.png"""
    ...

def plot_mmlu_vs_fairness(df: pd.DataFrame, save_dir) -> None:
    """MMLU rank vs BBQ-Disambig rank scatter.
    Saves: figures/mmlu_vs_fairness.png"""
    ...

def generate_all_figures(df: pd.DataFrame, results: dict, save_dir) -> None:
    """Call all five plot functions."""
    ...
```

---

### RunExperiment (`h-m1/code/run_experiment.py`)

**Dependencies**: `data.py`, `analysis.py`, `visualize.py`, `config.py`

```python
def main() -> None:
    """
    1. build_score_dataframe()
    2. verify_n_common()
    3. run_full_analysis()
    4. generate_all_figures()
    5. Print gate result: PASS / FAIL + partial_rho, p_value
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Create config.py with gates, paths, WINOGRANDE_SCORES dict | 5 | 1+1+1+2 |
| A-2 | Data Assembly | build_score_dataframe() importing H-E1 paper_scores + MMLU + Winogrande; inner join; CSV save | 12 | 3+3+3+3 |
| A-3 | Raw Spearman | compute_raw_spearman() via scipy; baseline metric | 5 | 1+2+1+1 |
| A-4 | Partial Spearman | compute_partial_spearman() via pingouin; one-tailed; mechanism verification asserts | 10 | 2+2+4+2 |
| A-5 | Gate + Sensitivity | evaluate_gate(), run_full_analysis() with Winogrande repeat; results JSON | 9 | 2+2+3+2 |
| A-6 | Visualization | All 5 figures (gate bar, rank scatter, sensitivity, distributions, MMLU scatter) | 13 | 3+2+4+4 |
| A-7 | Entry Point & Test | run_experiment.py main(); self-check assert on known synthetic 5-row DataFrame | 8 | 1+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-5, A-6], Low(4-8): [A-1, A-3, A-7]

---

## Data Flow

- `paper_scores.load_paper_scores()` + `WINOGRANDE_SCORES` → `build_score_dataframe()` → `h_m1_scores.csv`
- DataFrame → `run_full_analysis()` → `{raw_rho, partial_rho, p_value, gate_pass, ...}` → `results.json`
- DataFrame + results → `generate_all_figures()` → `figures/*.png`

---

## Dependencies (pip)

```
pingouin==0.6.1
scipy>=1.11
pandas>=1.5
numpy>=1.24
matplotlib>=3.7
seaborn>=0.12
```
