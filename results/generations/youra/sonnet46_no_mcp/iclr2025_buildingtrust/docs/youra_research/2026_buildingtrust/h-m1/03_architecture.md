# Architecture: H-M1

**Hypothesis**: Capability-independent calibration-hallucination mechanistic link
**Type**: MECHANISM
**Date**: 2026-04-30

Applied: BCa-bootstrap-partial-correlation pattern
Applied: incremental-hypothesis-statistical-pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260430_buildingtrust/h-e1/code/`
**Findings**: H-E1 uses flat module structure (config.py, score_matrix.py, analysis.py, visualize.py, report.py, main.py). `analysis.py` already implements `bca_bootstrap_ci`, `compute_partial_corr_matrix`, and `evaluate_gates` — all directly adaptable. Import paths are local (no package prefix). Score matrix saved as CSV in `h-e1/results/`.

---

## File Organization

- `h-m1/code/config.py` — H-M1 constants and paths
- `h-m1/code/data_loader.py` — load H-E1 score matrix
- `h-m1/code/analyzers.py` — all statistical tests (internal consistency, partial corr, discriminant, invariance)
- `h-m1/code/visualizer.py` — 5 figures
- `h-m1/code/reporter.py` — results JSON + validation MD
- `h-m1/code/main.py` — pipeline orchestration
- `h-m1/figures/` — output figures directory
- `h-m1/results/` — output JSON/MD directory

---

## Modules

### Config (`h-m1/code/config.py`)

**Dependencies**: none

```python
SCORE_MATRIX_PATH: str          # "h-e1/results/score_matrix.csv"
SCORE_MATRIX_T07_PATH: str      # "h-e1/results/score_matrix_t07.csv"
RESULTS_DIR: str                # "h-m1/results/"
FIGURES_DIR: str                # "h-m1/figures/"
N_BOOTSTRAP: int                # 10000
BOOTSTRAP_SEED: int             # 42
PRIMARY_X: str                  # "ECE"
PRIMARY_Y: str                  # "TruthfulQA_pct"
DISCRIMINANT_Y: str             # "HumanEval_pass1"
COVARIATE: str                  # "MMLU_acc"
INTERNAL_X: str                 # "ECE"
INTERNAL_Y: str                 # "Brier"
PRIMARY_THRESHOLD: float        # 0.40
INTERNAL_THRESHOLD: float       # 0.30
DISCRIMINANT_THRESHOLD: float   # 0.20
DECODING_INVARIANCE_THRESHOLD: float  # 0.30
FIGURE_DPI: int                 # 150
FIGURE_FORMAT: str              # "png"
FIGURE_NAMES: dict              # {fig_key: filename}
REQUIRED_COLS: list[str]        # ["ECE", "Brier", "TruthfulQA_pct", "MMLU_acc",
                                #  "HumanEval_pass1", "ANLI_drop", "model_id"]
MIN_MODELS: int                 # 25
```

---

### DataLoader (`h-m1/code/data_loader.py`)

**Dependencies**: config, pandas, pathlib

```python
def load_score_matrix(path: str) -> pd.DataFrame: ...
    # reads CSV; validates columns and row count >= MIN_MODELS
    # raises ValueError on schema mismatch or insufficient rows

def load_score_matrix_t07(path: str) -> pd.DataFrame: ...
    # same as above for T=0.7 variant
    # returns empty DataFrame if file not found (invariance test becomes optional)

def validate_schema(df: pd.DataFrame, required_cols: list[str]) -> bool: ...
    # checks all required_cols present and non-NaN for gate columns
```

---

### Analyzers (`h-m1/code/analyzers.py`)

**Dependencies**: config, scipy, pingouin, numpy, pandas

```python
def compute_internal_consistency(
    df: pd.DataFrame, x: str, y: str, n_boot: int, seed: int
) -> dict: ...
# Returns: {rho, pval, bca_ci_low, bca_ci_high, passes_threshold}

def compute_partial_corr_bca(
    df: pd.DataFrame, x: str, y: str, covar: str, n_boot: int, seed: int
) -> dict: ...
# Returns: {rho_partial, bca_ci_low, bca_ci_high, ci_excludes_zero, passes_threshold}

def compute_confound_magnitude(raw_rho: float, partial_rho: float) -> dict: ...
# Returns: {survival_fraction, confound_fraction, interpretation}

def compute_discriminant_validity(
    df: pd.DataFrame, x: str, y: str, covar: str, n_boot: int, seed: int
) -> dict: ...
# Returns: {rho_partial, bca_ci_low, bca_ci_high, passes_threshold}
# passes_threshold = abs(rho_partial) < DISCRIMINANT_THRESHOLD

def compute_decoding_invariance(
    df_greedy: pd.DataFrame, df_t07: pd.DataFrame,
    x: str, y: str, covar: str, n_boot: int, seed: int
) -> dict: ...
# Returns: {rho_greedy, rho_t07, passes_threshold, skipped}
# skipped=True if df_t07 is empty

def evaluate_gate(partial_result: dict, threshold: float) -> bool: ...
# True if abs(rho_partial) >= threshold AND ci_excludes_zero

def _bca_bootstrap_spearman(
    df: pd.DataFrame, x: str, y: str, n_boot: int, seed: int
) -> tuple[float, float]: ...
# BCa CI for unconditional spearmanr (adapted from h-e1/code/analysis.py::bca_bootstrap_ci)

def _bca_bootstrap_partial(
    df: pd.DataFrame, x: str, y: str, covar: str, n_boot: int, seed: int
) -> tuple[float, float]: ...
# BCa CI for pg.partial_corr — direct adaptation of H-E1 bca_bootstrap_ci
```

---

### Visualizer (`h-m1/code/visualizer.py`)

**Dependencies**: config, matplotlib, seaborn, pandas, pathlib

```python
def plot_gate_bar(
    partial_result: dict, threshold: float, figures_dir: Path
) -> Path: ...
# Fig 1: bar chart partial ρ(ECE, TruthfulQA% | MMLU) vs threshold, BCa CI error bar, pass/fail annotation

def plot_raw_vs_partial(
    raw_rho: float, partial_rho: float, confound_result: dict, figures_dir: Path
) -> Path: ...
# Fig 2: side-by-side bars raw ρ vs partial ρ, survival_fraction annotation

def plot_ece_brier_scatter(
    df: pd.DataFrame, internal_result: dict, figures_dir: Path
) -> Path: ...
# Fig 3: scatter ECE vs Brier, N=30 points colored by model family, ρ annotated

def plot_discriminant_validity(
    primary_result: dict, discriminant_result: dict, figures_dir: Path
) -> Path: ...
# Fig 4: grouped bar partial ρ(ECE, TruthfulQA% | MMLU) vs partial ρ(ECE, HumanEval | MMLU)

def plot_decoding_invariance(
    invariance_result: dict, figures_dir: Path
) -> Path: ...
# Fig 5: scatter greedy partial ρ vs T=0.7 partial ρ; H-M1 point highlighted; skipped if invariance_result['skipped']
```

---

### Reporter (`h-m1/code/reporter.py`)

**Dependencies**: config, json, pathlib

```python
def write_results_json(
    internal_result: dict,
    primary_result: dict,
    confound_result: dict,
    discriminant_result: dict,
    invariance_result: dict,
    gate_pass: bool,
    output_path: Path,
) -> None: ...
# Writes h-m1/04_results.json with all results and pass/fail flags

def write_validation_md(
    internal_result: dict,
    primary_result: dict,
    confound_result: dict,
    discriminant_result: dict,
    invariance_result: dict,
    gate_pass: bool,
    output_path: Path,
) -> None: ...
# Writes h-m1/04_validation.md with criterion table (threshold, observed, pass/fail)
```

---

### Main (`h-m1/code/main.py`)

**Dependencies**: all modules above

```python
def main() -> dict: ...
# Returns gate_eval dict with PASS bool and all results
# Pipeline: load_score_matrix → validate_schema → run_analyses → generate_figures → write_reports
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Greedy score matrix (CSV) | `pd.read_csv(SCORE_MATRIX_PATH)` | `h-e1/results/score_matrix.csv` |
| T=0.7 score matrix (CSV) | `pd.read_csv(SCORE_MATRIX_T07_PATH)` | `h-e1/results/score_matrix_t07.csv` |
| BCa bootstrap pattern | adapted inline in analyzers.py | `h-e1/code/analysis.py::bca_bootstrap_ci` |

**Verified from**: `h-e1/code/` actual implementation.
**Note**: H-M1 reads H-E1 CSV outputs only — no Python module imports from h-e1/code/.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create h-m1/code/ structure, config.py with all constants, verify H-E1 score matrix path | 5 | 1+1+1+2 |
| A-2 | Data Loader | Implement data_loader.py: load_score_matrix, load_score_matrix_t07, validate_schema | 7 | 2+1+1+3 |
| A-3 | BCa Bootstrap Core | Implement _bca_bootstrap_spearman and _bca_bootstrap_partial in analyzers.py (seed-controlled, adapted from H-E1) | 10 | 2+2+4+2 |
| A-4 | Internal Consistency Analyzer | Implement compute_internal_consistency: ECE-Brier Spearman ρ with BCa CI | 7 | 2+2+2+1 |
| A-5 | Partial Correlation Analyzer | Implement compute_partial_corr_bca, compute_confound_magnitude, evaluate_gate — primary H-M1 gate test | 11 | 2+3+4+2 |
| A-6 | Discriminant + Invariance Analyzers | Implement compute_discriminant_validity and compute_decoding_invariance | 9 | 2+2+3+2 |
| A-7 | Visualization Figs 1-3 | Implement plot_gate_bar, plot_raw_vs_partial, plot_ece_brier_scatter | 10 | 2+2+3+3 |
| A-8 | Visualization Figs 4-5 | Implement plot_discriminant_validity, plot_decoding_invariance | 8 | 2+2+2+2 |
| A-9 | Reporter | Implement write_results_json and write_validation_md with all criterion pass/fail | 8 | 2+1+2+3 |
| A-10 | Main Pipeline Integration | Implement main.py orchestration, end-to-end run, gate logging | 10 | 2+3+2+3 |
| A-11 | Validation + Gate Check | Run full pipeline, verify partial ρ(ECE, TruthfulQA% \| MMLU) ≥ 0.40, BCa CI excludes zero | 9 | 1+2+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-5, A-6, A-7, A-10, A-11], Low(4-8): [A-1, A-2, A-4, A-8, A-9]
