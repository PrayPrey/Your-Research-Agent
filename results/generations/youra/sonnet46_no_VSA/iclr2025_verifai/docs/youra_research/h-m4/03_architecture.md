# Architecture: H-M4 Cross-Model Contract-Satisfaction Statistical Analysis

**Applied**: flat function-based module pattern (consistent with H-M3/H-M1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code (H-M3)
**Analyzed Path**: `docs/youra_research/h-m3/code/`
**Findings**: H-M3 uses flat function-based modules (no classes except dataclasses), path constants via `Path(__file__).parent.parent`, consistent `run_experiment.py` + domain-specific runners pattern. H-M1 has `statistical_analysis.py` as precedent for stats logic.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_contracteval_tasks | `from h_m3.data_loader import load_contracteval_tasks` | `h-m3/code/data_loader.py:load_contracteval_tasks` |
| plot helpers | reference only — H-M4 has own visualization.py | `h-m3/code/visualization.py` |

**Verified from**: `docs/youra_research/h-m3/code/` (actual implementation)

**Note**: H-M4 reads H-M3 results as a CSV file path; no direct Python import of H-M3 modules required. ContractEval tasks already cloned from H-M1/H-M3 setup.

---

## File Organization

```
h-m4/code/
├── config.py           # constants: paths, model metadata, gate thresholds
├── data_loader.py      # load H-M3 CSV, EvalPlus scores, ContractEval metadata
├── analysis.py         # Kendall τ, MixedLM, ΔR², cross-model gap
├── visualization.py    # 5 required figures
├── run_experiment.py   # orchestrator: load → validate → analyze → save → plot
└── results/            # h_m4_results.json, analysis_summary.txt
figures/                # gate_metrics_bar.png, ranking_scatter.png, ...
```

---

## Module Interfaces

### config (`code/config.py`)

**Dependencies**: pathlib

```python
# Paths
H_M3_RESULTS_DIR: Path  # ../h-m3/results/
EXP_B_CSV: Path          # H_M3_RESULTS_DIR / "experiment_b_per_model_task_rates.csv"
CONTRACT_EVAL_JSON: Path # ../../data/ContractEval/data/contract_eval_tasks.json
RESULTS_DIR: Path        # ../results/
FIGURES_DIR: Path        # ../figures/

# Model metadata
MODEL_SIZES: dict[str, float]
MODEL_FAMILIES: dict[str, str]
PASS_AT_1_FALLBACK: dict[str, float]  # hardcoded from EvalPlus leaderboard

# Gate thresholds
TAU_THRESHOLD: float = 0.6
DELTA_R2_THRESHOLD: float = 0.10
GAP_THRESHOLD: float = 0.10
PVALUE_THRESHOLD: float = 0.05
SEED: int = 42
```

---

### data_loader (`code/data_loader.py`)

**Dependencies**: config, pandas, json, pathlib

```python
def load_exp_b_rates(csv_path: Path = None) -> pd.DataFrame:
    # Returns DataFrame: [model_id, task_id, contract_satisfaction_rate, n_programs, n_failing]
    # Fails early if < 3 model IDs present or > 50% NaN per model
    ...

def load_pass_at_1(use_evalplus_pkg: bool = True) -> dict[str, float]:
    # Returns {model_id: weighted_avg_pass@1} — tries evalplus package, falls back to PASS_AT_1_FALLBACK
    ...

def load_task_metadata(json_path: Path = None) -> dict[str, str]:
    # Returns {task_id: task_type} — "humaneval" or "mbpp"
    ...

def build_df_long(
    exp_b_df: pd.DataFrame,
    pass_at_1: dict[str, float],
    task_meta: dict[str, str],
) -> pd.DataFrame:
    # Merges exp_b_df with pass@1 scores and metadata
    # Adds columns: pass_at_1, log_size, model_family, task_type
    # Validates shape >= 1500 rows
    ...

def validate_inputs(exp_b_df: pd.DataFrame) -> None:
    # Raises ValueError with clear message if prerequisites not met
    ...
```

---

### analysis (`code/analysis.py`)

**Dependencies**: config, numpy, scipy.stats, statsmodels.formula.api, pandas, dataclasses

```python
@dataclass
class H_M4_Results:
    tau: float
    tau_pvalue: float
    spearman_rho: float
    spearman_pvalue: float
    delta_R2: float
    R2_full: float
    R2_reduced: float
    cross_model_gap: float
    gap_ci_low: float
    gap_ci_high: float
    best_model: str
    worst_model: str
    model_ranking_by_contract: list[str]
    model_ranking_by_pass: list[str]
    n_model_task_pairs: int
    gate_pass: bool
    gate_partial: bool
    # Subgroup results
    tau_humaneval: float
    tau_mbpp: float
    delta_R2_humaneval: float
    delta_R2_mbpp: float
    permutation_null: list[float]
    model_family_pvalue: float
    converged: bool
    fallback_ols: bool

def compute_kendall_tau(
    model_rates: pd.Series,
    pass_at_1: dict[str, float],
) -> tuple[float, float, list[float]]:
    # Returns (tau, exact_pvalue, null_distribution)
    # Uses permutation_type='pairings', variant='b'; all 5! permutations
    ...

def compute_spearman(
    model_rates: pd.Series,
    pass_at_1: dict[str, float],
) -> tuple[float, float]:
    ...

def fit_mixedlm(
    df_long: pd.DataFrame,
    formula: str,
    groups_col: str = "task_id",
    reml: bool = True,
) -> tuple[object, bool]:
    # Returns (fitted_model, converged); retries with lbfgs/bfgs if needed
    # Returns (ols_fallback, False) if MixedLM fails completely
    ...

def marginal_r2(fitted_model) -> float:
    # Nakagawa-Schielzeth: var(fitted) / (var(fitted) + re_var + residual_var)
    # Handles OLS fallback (no re_var)
    ...

def compute_delta_r2(df_long: pd.DataFrame) -> tuple[float, float, float, bool, bool]:
    # Returns (delta_R2, R2_full, R2_reduced, converged, fallback_ols)
    ...

def compute_cross_model_gap(
    exp_b_df: pd.DataFrame,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple[float, float, float, str, str]:
    # Returns (gap, ci_low, ci_high, best_model, worst_model)
    # Task-controlled: residual = rate - task_mean
    ...

def compute_model_family_pvalue(df_long: pd.DataFrame) -> float:
    # Permutation p-value for model_family coefficient significance
    ...

def verify_mechanism_activated(results: H_M4_Results) -> tuple[bool, dict]:
    ...

def run_analysis(
    exp_b_df: pd.DataFrame,
    df_long: pd.DataFrame,
    pass_at_1: dict[str, float],
) -> H_M4_Results:
    # Orchestrates all analysis steps; applies gate logic
    ...

def run_subgroup_analysis(
    exp_b_df: pd.DataFrame,
    df_long: pd.DataFrame,
    pass_at_1: dict[str, float],
    task_type: str,
) -> dict:
    # Runs tau + delta_R2 for one task_type stratum
    ...
```

---

### visualization (`code/visualization.py`)

**Dependencies**: config, analysis.H_M4_Results, matplotlib, seaborn, pandas, numpy

```python
def plot_gate_metrics_bar(results: H_M4_Results, save_path: Path = None) -> None:
    # Figure 1: bar chart of τ, ΔR², gap with threshold lines
    ...

def plot_ranking_scatter(
    model_rates: pd.Series,
    pass_at_1: dict[str, float],
    results: H_M4_Results,
    save_path: Path = None,
) -> None:
    # Figure 2: contract rate (y) vs pass@1* (x), model labels, τ annotated
    ...

def plot_cross_model_bar(
    exp_b_df: pd.DataFrame,
    pass_at_1: dict[str, float],
    save_path: Path = None,
) -> None:
    # Figure 3: per-model contract rate sorted; pass@1* rank on secondary axis
    ...

def plot_r2_decomposition(results: H_M4_Results, save_path: Path = None) -> None:
    # Figure 4: stacked bar — pass@1 variance, log_size, model_family ΔR², residual
    ...

def plot_permutation_null(results: H_M4_Results, save_path: Path = None) -> None:
    # Figure 5: histogram of null distribution; observed τ marked
    ...

def save_all_figures(
    results: H_M4_Results,
    exp_b_df: pd.DataFrame,
    df_long: pd.DataFrame,
    pass_at_1: dict[str, float],
    figures_dir: Path = None,
) -> None:
    ...
```

---

### run_experiment (`code/run_experiment.py`)

**Dependencies**: config, data_loader, analysis, visualization, json, pathlib

```python
RESULTS_DIR: Path
FIGURES_DIR: Path

def save_results(results: "H_M4_Results", results_dir: Path = None) -> None:
    # Writes h_m4_results.json + analysis_summary.txt
    ...

def main() -> None:
    # 1. load_exp_b_rates → validate_inputs
    # 2. load_pass_at_1 → load_task_metadata
    # 3. build_df_long
    # 4. run_analysis → verify_mechanism_activated
    # 5. save_results
    # 6. save_all_figures
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create directory structure, config.py with all constants, model metadata, gate thresholds, path resolution | 6 | 2+1+1+2 |
| A-2 | Data Loading | Implement data_loader.py: load H-M3 CSV, EvalPlus pass@1 (pkg + fallback), ContractEval metadata, build_df_long, validate_inputs | 9 | 2+2+2+3 |
| A-3 | Kendall τ + Permutation Test | compute_kendall_tau with exact permutation p-value (permutation_type='pairings', n=5, all 5!=120 perms), Spearman secondary | 11 | 2+2+4+3 |
| A-4 | Mixed-Effects Regression | fit_mixedlm with retry (lbfgs/bfgs fallback), OLS fallback if diverged; marginal_r2 (Nakagawa-Schielzeth); compute_delta_r2 full/reduced | 14 | 3+3+4+4 |
| A-5 | Cross-Model Gap + Family p-value | Task-controlled residual gap, bootstrap CI (n=1000, seed=42), model_family permutation p-value | 10 | 2+2+3+3 |
| A-6 | Subgroup Analysis | Repeat τ + ΔR² stratified by task_type (humaneval/mbpp); flag divergence > 0.2 | 8 | 2+2+2+2 |
| A-7 | Gate Logic + Verification | run_analysis orchestrator, verify_mechanism_activated, PASS/PARTIAL/FAIL logic | 7 | 2+2+1+2 |
| A-8 | Visualization | All 5 figures: gate_metrics_bar, ranking_scatter, cross_model_bar, r2_decomposition, permutation_null | 10 | 3+2+2+3 |
| A-9 | Results Persistence | save_results: h_m4_results.json + analysis_summary.txt; run_experiment.py main() orchestrator | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-2, A-3, A-5, A-6, A-8], Low(4-8): [A-1, A-7, A-9]
