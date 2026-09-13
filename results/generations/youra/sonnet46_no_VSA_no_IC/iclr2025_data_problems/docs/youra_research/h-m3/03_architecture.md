---
hypothesis_id: H-M3
hypothesis_type: MECHANISM
date: 2026-08-20
author: yoon303b@gmail.com
phase: 3-architecture
---

# Architecture: H-M3 Panel OLS Regression

Applied: none (Archon KB similarity 0.41–0.42, diffusion model content only — no relevant patterns extracted)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: H-M2 implements `data_loader.py`, `evaluator.py`, `decontamination.py`, `reporter.py`, `config.py` — all directly reusable with extension. Key reuse points: `load_exposure_arrays`, `align_checkpoint_indices`, `apply_floor_filter`, `evaluate_checkpoint`/`batch_evaluate_model` (cache+fallback logic), `run_decontamination_audit`, `_to_serializable`. H-M2 covers MODEL_SIZES=["70m","1b","6.9b"]; H-M3 expands to all 16 model sizes. H-M2 tasks=["mmlu","hellaswag"]; H-M3 adds "arc_challenge","winogrande".

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_exposure_arrays | `from h_m2.src.data_loader import load_exposure_arrays` | `docs/youra_research/h-m2/code/src/data_loader.py` |
| align_checkpoint_indices | `from h_m2.src.data_loader import align_checkpoint_indices` | `docs/youra_research/h-m2/code/src/data_loader.py` |
| apply_floor_filter | `from h_m2.src.data_loader import apply_floor_filter` | `docs/youra_research/h-m2/code/src/data_loader.py` |
| evaluate_checkpoint | `from h_m2.src.evaluator import evaluate_checkpoint` | `docs/youra_research/h-m2/code/src/evaluator.py` |
| batch_evaluate_model | `from h_m2.src.evaluator import batch_evaluate_model` | `docs/youra_research/h-m2/code/src/evaluator.py` |
| load_fallback_scores | `from h_m2.src.evaluator import load_fallback_scores` | `docs/youra_research/h-m2/code/src/evaluator.py` |
| run_decontamination_audit | `from h_m2.src.decontamination import run_decontamination_audit` | `docs/youra_research/h-m2/code/src/decontamination.py` |
| _to_serializable | `from h_m2.src.reporter import _to_serializable` | `docs/youra_research/h-m2/code/src/reporter.py` |

**Verified from**: `docs/youra_research/h-m2/code/` (actual implementation)

**Note on reuse strategy**: Rather than importing cross-hypothesis, copy and extend the relevant functions into H-M3's own `src/` modules. This avoids path fragility and allows clean extension (e.g., adding arc_challenge/winogrande to TASKS, expanding MODEL_SIZES to all 16).

---

## File Organization

```
docs/youra_research/h-m3/
├── code/
│   ├── config.py              # all constants (extends H-M2 config)
│   ├── run_experiment.py      # orchestrator entry point
│   └── src/
│       ├── __init__.py
│       ├── data_loader.py     # reuse+extend H-M2; adds multi-model panel assembly
│       ├── evaluator.py       # reuse H-M2; adds arc_challenge+winogrande tasks
│       ├── panel_builder.py   # NEW: MultiIndex construction, VIF diagnostics
│       ├── panel_regression.py # NEW: PanelOLS fits (benchmark-specific + shared-β)
│       ├── hypothesis_tests.py # NEW: P1/P2 one-tailed, P3 LRT+FDR, P4 Spearman
│       ├── robustness.py      # NEW: permutation null, subgroup regression, R² decomp
│       ├── visualization.py   # reuse+extend H-M2; 6 new figures
│       ├── reporter.py        # reuse+extend H-M2; new output paths
│       └── decontamination.py # reuse H-M2 unchanged
├── figures/                   # fig1–fig6 PNG outputs
└── 03_architecture.md

results/h-m3/
├── eval_cache/{model_size}/step{N:07d}.json
├── vif_diagnostics.json
├── panel_results_{benchmark}.json
├── panel_results_shared_beta.json
├── lrt_results.json
├── robustness_results.json
├── panel_summary.json
└── gate_summary.json
```

---

## Module Interfaces

### Config (`config.py`)

**Dependencies**: none

```python
MODEL_SIZES: list[str]          # all 16: ["70m","160m","410m","1b","1.4b","2.8b","6.9b","12b", + deduped]
MODEL_IDS: dict[str, str]       # EleutherAI/pythia-{size} + deduped variants
CHECKPOINT_STEPS: list[int]     # 154 steps (identical to H-M2)
PILE_DOMAINS: list[str]         # 22 domains (identical to H-M2)
FOCAL_DOMAINS: dict[str, str]   # {"wikipedia": "Wikipedia (en)", "books": "Books3"}
TASKS: dict[str, dict]          # extends H-M2: adds arc_challenge (25-shot), winogrande (5-shot)
FLOOR_THRESHOLD: float          # 0.30 (all-benchmark — reverted from H-M2's 0.20 per PRD)
MIN_VALID_CHECKPOINTS: int      # 100
SEED: int                       # 42
N_PERMUTATIONS: int             # 1000
VIF_THRESHOLD: float            # 10.0
PCA_VARIANCE_RETAINED: float    # 0.95
H_E1_EXPOSURE_DIR: str
RESULTS_DIR: str                # "results/h-m3"
EVAL_CACHE_DIR: str             # "results/h-m3/eval_cache"
FIGURES_DIR: str                # "docs/youra_research/h-m3/figures"
PYTHIA_REPO_DIR: str            # local clone of EleutherAI/pythia (for evals/ cache)
```

---

### DataLoader (`src/data_loader.py`)

**Dependencies**: config, numpy, pandas
**Reuse**: extends H-M2 `data_loader.py` — adds `build_full_panel_exposures`

```python
def load_exposure_arrays(model_size: str, base_dir: str = ...) -> np.ndarray: ...
    # returns (154, 22) — reuse H-M2 unchanged

def align_checkpoint_indices(
    exposure: np.ndarray, eval_steps: list[int], reference_steps: list[int] = None
) -> np.ndarray: ...
    # returns (T, 22) — reuse H-M2 unchanged

def verify_coverage(exposure: np.ndarray, model_size: str) -> None: ...
    # reuse H-M2 unchanged

def apply_floor_filter(
    exposure: np.ndarray,
    scores: dict[str, np.ndarray],
    threshold: float = ...,
    min_valid: int = ...,
) -> tuple[np.ndarray, dict[str, np.ndarray], np.ndarray]: ...
    # reuse H-M2 unchanged

def build_full_panel_exposures(
    model_sizes: list[str],
    base_dir: str = ...,
) -> dict[str, np.ndarray]: ...
    # NEW: loads all 16 models; returns {model_size: (154, 22)}

def check_books3_within_variance(
    exposures: dict[str, np.ndarray],
    threshold: float = 1e-6,
) -> dict[str, float]: ...
    # NEW: computes within-model variance for Books3 per model; raises if all < threshold
```

---

### Evaluator (`src/evaluator.py`)

**Dependencies**: config, lm_eval, json, pathlib
**Reuse**: extends H-M2 `evaluator.py` — adds arc_challenge, winogrande; load_scores_array extended to 4 tasks

```python
def is_cache_valid(cache_path: Path, required_tasks: list[str]) -> bool: ...
def load_cached_scores(cache_path: Path) -> dict[str, float]: ...

def evaluate_checkpoint(
    model_size: str,
    step: int,
    tasks: list[str] = None,
    device: str = "cuda",
    cache_dir: str = ...,
    batch_size: str = ...,
    dtype: str = ...,
) -> dict[str, float]: ...
    # reuse H-M2; TASKS config now includes all 4 benchmarks

def batch_evaluate_model(
    model_size: str,
    steps: list[int] = None,
    tasks: list[str] = None,
    device: str = "cuda",
) -> dict[int, dict[str, float]]: ...
    # reuse H-M2 unchanged

def load_scores_array(
    model_size: str, steps: list[int] = None
) -> dict[str, np.ndarray]: ...
    # extends H-M2: returns {mmlu, hellaswag, arc_challenge, winogrande} each (154,)

def load_fallback_scores(
    model_size: str, pythia_repo_dir: Path, steps: list[int] = None
) -> dict[int, dict[str, float]]: ...
    # reuse H-M2; extended to check arc_challenge + winogrande result files
```

---

### PanelBuilder (`src/panel_builder.py`)

**Dependencies**: config, data_loader, evaluator, pandas, numpy, statsmodels, sklearn

```python
def construct_panel_dataframe(
    exposures: dict[str, np.ndarray],
    scores: dict[str, dict[str, np.ndarray]],
    steps: list[int] = None,
) -> pd.DataFrame: ...
    # builds MultiIndex (model_size, checkpoint) DataFrame; 2464 rows
    # columns: 22 domain fractions + 4 benchmark scores + log_params

def filter_floor_checkpoints(
    panel_df: pd.DataFrame,
    benchmarks: list[str],
    threshold: float = ...,
    min_valid: int = ...,
) -> pd.DataFrame: ...
    # drops rows where all benchmark scores < threshold; verifies >= 100 per entity

def drop_min_variance_domain(
    panel_df: pd.DataFrame, domain_cols: list[str]
) -> tuple[pd.DataFrame, list[str], str]: ...
    # drops 1 domain (min variance) to break sum-to-1; returns (df, remaining_cols, dropped_name)

def run_vif_diagnostics(
    panel_df: pd.DataFrame, domain_cols: list[str]
) -> tuple[pd.DataFrame, list[str], dict]: ...
    # computes VIF; applies PCA(n_components=0.95) if any VIF > 10
    # returns (df_with_regressors, regressor_cols, vif_report)
    # saves vif_diagnostics.json

def verify_panel_quality(
    panel_df: pd.DataFrame, domain_cols: list[str]
) -> dict[str, float]: ...
    # computes within-entity variance per domain; warns on low-variation domains
```

---

### PanelRegression (`src/panel_regression.py`)

**Dependencies**: config, pandas, numpy, linearmodels, statsmodels

```python
def fit_benchmark_specific_models(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    benchmarks: list[str],
) -> dict[str, object]: ...
    # fits PanelOLS.from_formula for each benchmark with EntityEffects
    # cov_type='clustered', cluster_entity=True
    # returns {benchmark: PanelOLSResults}

def fit_shared_beta_model(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    benchmarks: list[str],
) -> object: ...
    # stacks benchmarks long (9856 obs); fits OLS with benchmark dummies + model dummies
    # returns OLSResults for LRT comparison

def extract_coefficients(
    results: dict[str, object],
    domain_cols: list[str],
) -> pd.DataFrame: ...
    # returns DataFrame (domain_cols x benchmarks) of beta coefficients with SEs

def save_panel_results(
    results: dict[str, object],
    shared_result: object,
    out_dir: str,
) -> None: ...
    # saves panel_results_{b}.json and panel_results_shared_beta.json
```

---

### HypothesisTests (`src/hypothesis_tests.py`)

**Dependencies**: config, numpy, scipy, statsmodels, pandas

```python
def test_p1_p2(
    results: dict[str, object],
    focal_domains: dict[str, str],
    domain_cols: list[str],
) -> dict: ...
    # P1: one-tailed test beta_wiki > beta_books for MMLU
    # P2: one-tailed test beta_books > beta_wiki for HellaSwag
    # Fisher z-test on coefficient difference / pooled clustered SE
    # returns {p1_direction, p1_pvalue, p2_direction, p2_pvalue}

def run_lrt_all_pairs(
    panel_df: pd.DataFrame,
    benchmark_results: dict[str, object],
    domain_cols: list[str],
    benchmarks: list[str],
) -> dict: ...
    # computes LRT for all 6 pairwise benchmark comparisons
    # lr_stat = 2*(LL_b1 + LL_b2 - LL_shared_pair)
    # returns {pair_key: {lr_stat, df, p_value}}

def apply_fdr_correction(lrt_results: dict) -> dict: ...
    # Benjamini-Hochberg on 6 p-values via statsmodels multipletests
    # returns lrt_results enriched with {q_value, reject}

def test_p4_spearman(
    coef_small: pd.Series, coef_large: pd.Series
) -> dict: ...
    # Spearman rho of domain coefficient rankings: small vs large subgroup
    # returns {rho, p_value, passes_gate}
```

---

### Robustness (`src/robustness.py`)

**Dependencies**: config, numpy, pandas, linearmodels, scipy

```python
def run_permutation_null(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    focal_domains: dict[str, str],
    n_permutations: int = ...,
    seed: int = ...,
) -> dict: ...
    # shuffles domain labels 1000 times (numpy vectorized, not per-loop)
    # builds null distribution of |beta_wiki - beta_books| for MMLU and HellaSwag
    # returns {mmlu_null: np.ndarray(1000,), hellaswag_null: np.ndarray(1000,),
    #          mmlu_empirical_p, hellaswag_empirical_p}

def run_subgroup_regressions(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    benchmarks: list[str],
    small_sizes: list[str],
    large_sizes: list[str],
) -> dict: ...
    # separate PanelOLS fits for small (70m-410m) vs large (1b-12b)
    # returns {small: {b: coefficients}, large: {b: coefficients}}

def run_r2_decomposition(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    benchmarks: list[str],
) -> dict: ...
    # fits domain-only, scale-only (log_params), full models
    # returns {benchmark: {domain_only_r2, scale_only_r2, full_r2}}
```

---

### Visualization (`src/visualization.py`)

**Dependencies**: config, matplotlib, seaborn, numpy, pandas
**Reuse**: extends H-M2 visualization — new figure suite

```python
def plot_gate_metrics_bar(
    coef_df: pd.DataFrame, se_df: pd.DataFrame, out_path: str
) -> None: ...
    # fig1: beta_wiki + beta_books per benchmark, 95% CI error bars (MANDATORY)

def plot_domain_coefficient_heatmap(
    coef_df: pd.DataFrame, out_path: str
) -> None: ...
    # fig2: 22 domains x 4 benchmarks, color = beta magnitude

def plot_directional_scatter(
    coef_df: pd.DataFrame, out_path: str
) -> None: ...
    # fig3: beta_wiki vs beta_books per benchmark, diagonal line

def plot_r2_decomposition(
    r2_results: dict, out_path: str
) -> None: ...
    # fig4: domain-only, scale-only, full R²_within per benchmark

def plot_permutation_null(
    perm_results: dict, observed: dict, out_path: str
) -> None: ...
    # fig5: histogram of permuted |beta_wiki - beta_books| vs observed (P1 and P2)

def plot_subgroup_robustness(
    subgroup_results: dict, out_path: str
) -> None: ...
    # fig6: beta_wiki and beta_books for small vs large model subgroups
```

---

### Reporter (`src/reporter.py`)

**Dependencies**: config, json, pathlib
**Reuse**: extends H-M2 `reporter.py` — reuse `_to_serializable`

```python
def _to_serializable(obj) -> object: ...
    # reuse H-M2 unchanged

def save_panel_summary(
    benchmark_results: dict,
    coef_df: pd.DataFrame,
    out_path: str,
) -> None: ...

def save_gate_summary(
    p1_result: dict, p2_result: dict, p3_result: dict, p4_result: dict,
    out_path: str,
) -> None: ...

def save_lrt_results(lrt_results: dict, out_path: str) -> None: ...

def save_robustness_results(robustness: dict, out_path: str) -> None: ...

def write_results_summary(
    gate: dict, coef_df: pd.DataFrame, lrt: dict, robustness: dict,
    out_path: str,
) -> None: ...
    # writes docs/youra_research/h-m3/04_results_summary.md
```

---

### Decontamination (`src/decontamination.py`)

**Dependencies**: config, datasets, nltk
**Reuse**: H-M2 `decontamination.py` unchanged — copy verbatim; extends scope to arc_challenge + winogrande if needed

```python
# Reuse H-M2 exactly — DecontaminationReport dataclass, build_ngram_set,
# compute_overlap_rate, run_decontamination_audit signatures unchanged
```

---

### Orchestrator (`run_experiment.py`)

**Dependencies**: all src modules, logging, argparse

```python
def main(args: argparse.Namespace) -> None: ...
    # Phase 1: load H-E1 exposures for all 16 models; check Books3 within-variance
    # Phase 2: evaluate benchmarks (cache-first, fallback to lm-eval)
    # Phase 3: construct panel + VIF + floor filter
    # Phase 4: fit benchmark-specific + shared-beta PanelOLS
    # Phase 5: P1/P2/P3/P4 hypothesis tests
    # Phase 6: robustness (permutation null, subgroup, R²)
    # Phase 7: generate 6 figures
    # Phase 8: write results JSON + markdown summary

if __name__ == "__main__": ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + Project Setup | Extend H-M2 config to 16 models + 4 tasks; create directory structure | 5 | 1+1+1+2 |
| A-2 | DataLoader Extension | Copy H-M2 data_loader; add build_full_panel_exposures + check_books3_within_variance | 7 | 2+2+2+1 |
| A-3 | Evaluator Extension | Copy H-M2 evaluator; add arc_challenge+winogrande; extend load_scores_array | 8 | 2+2+2+2 |
| A-4 | Panel Builder | NEW module: MultiIndex construction, floor filter, drop-domain, VIF/PCA diagnostics | 13 | 3+3+4+3 |
| A-5 | Panel Regression | NEW module: 4× PanelOLS (benchmark-specific) + shared-β OLS fit; save results | 14 | 4+3+4+3 |
| A-6 | Hypothesis Tests | NEW module: P1/P2 one-tailed Fisher z, P3 LRT 6-pairs + FDR, P4 Spearman | 15 | 4+3+4+4 |
| A-7 | Robustness Analysis | NEW module: permutation null (numpy vectorized), subgroup regressions, R² decomp | 16 | 4+3+5+4 |
| A-8 | Visualization | 6 figures; extend H-M2 visualization; colorblind-safe palette, 300 DPI | 10 | 2+2+3+3 |
| A-9 | Reporter | Extend H-M2 reporter; new save_* functions + results_summary.md template | 6 | 2+1+1+2 |
| A-10 | Orchestrator + Integration | run_experiment.py; wire all phases; argparse; logging; resume support | 12 | 2+4+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5, A-6, A-7], Medium(9-13): [A-4, A-8, A-10], Low(4-8): [A-1, A-2, A-3, A-9]

---

## Key Implementation Notes for Coder

- `load_scores_array` in H-M2 hardcodes `mmlu_scores` and `hellaswag_scores` lists — refactor to iterate over `config.TASKS` keys when extending to 4 benchmarks.
- H-M2 `FLOOR_THRESHOLD = 0.20` (lowered for 70m MMLU). PRD specifies 0.30 for H-M3 (all-benchmark check, not per-benchmark). Verify 70m survives filter — if not, keep 0.20 consistent with H-M2 rationale.
- `fit_shared_beta_model`: linearmodels does not natively stack multi-outcome panels. Use statsmodels OLS with benchmark dummies + model-size dummies (16 dummies) as the fallback specified in FR-6.3. Extract log-likelihood from `OLSResults.llf`.
- Permutation null: permute `domain_cols` column labels in panel_df (not rows), refit only the two focal-domain coefficients per shuffle. Use `np.random.default_rng(seed=42)`.
- `cluster_entity=True` requires N≥ ~10 clusters for reliable inference — N=16 model sizes is borderline; document this.
