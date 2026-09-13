# Architecture: H-E1 — Epistemic Reliability as a Latent Dimension

**Hypothesis:** H-E1 (EXISTENCE / MUST_WORK)
**Date:** 2026-04-30
**Tier:** LIGHT (pure eval + stats, no model training)

Applied: pipeline-stage-separation
Applied: minimal-flat-structure

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis or existing codebase

---

## Module Overview

Five-stage linear pipeline:
- Stage 1: Run lm-evaluation-harness on N=30 models (greedy + stochastic)
- Stage 2: Extract ECE + Brier from MMLU `--log_samples` output
- Stage 3: Assemble N×6 score matrix; compute derived metrics (AdvGLUE drop, ANLI drop)
- Stage 4: Statistical analysis — partial Spearman ρ with BCa bootstrap, factor analysis, LOO regression
- Stage 5: Visualization + results JSON output

---

## File/Directory Structure

```
h-e1/code/
├── config.py           # model list, paths, hyperparameters
├── run_eval.py         # Stage 1: lm-eval subprocess runner
├── calibration.py      # Stage 2: ECE + Brier from lm-eval logits
├── score_matrix.py     # Stage 3: assemble N×6 pandas DataFrame
├── analysis.py         # Stage 4: partial corr, factor analysis, LOO
├── visualize.py        # Stage 5: all figures
├── report.py           # Stage 5b: write 04_results.json + 04_validation.md
└── main.py             # orchestrator: runs stages 1-5 sequentially

h-e1/
├── results/            # lm-eval JSON output (one dir per model)
├── figures/            # all saved plots
├── 04_results.json     # final results
└── 04_validation.md    # human-readable summary
```

---

## Module Descriptions

### Config (`code/config.py`)

**Dependencies**: none

```python
MODELS: list[dict]  # [{id, hf_id, params, family}, ...] — 30 entries
TASKS: list[str]    # ["mmlu", "truthfulqa_mc1", "adv_glue", "anli_r3", "humaneval"]
RESULTS_DIR: str
FIGURES_DIR: str
GREEDY_SEED: int    # 42
STOCHASTIC_SEEDS: list[int]  # [42, 123, 456]
ECE_BINS: int       # 10
N_BOOTSTRAP: int    # 10000
BATCH_SIZE: dict    # {"7B": 8, "13B": 8, "30B": 4, "40B": 4, "70B": 1}
INDICATORS: list[str]  # ["ECE","Brier","TruthfulQA_pct","AdvGLUE_drop","ANLI_drop"]
GATE_PAIRS: list[tuple]  # [("ECE","TruthfulQA_pct"), ("ECE","AdvGLUE_drop")]
GATE_THRESHOLD: float  # 0.40
```

---

### EvalRunner (`code/run_eval.py`)

**Dependencies**: config, subprocess, pathlib

```python
def run_model_greedy(model: dict, output_dir: Path) -> bool: ...
    # Calls lm_eval CLI; returns True on success, False on failure
    # Args: model_args dtype=float16 or load_in_4bit=True for 70B
    # Flags: --log_samples --seed 42 --tasks {TASKS}

def run_model_stochastic(model: dict, seed: int, output_dir: Path) -> bool: ...
    # As above but --gen_kwargs temperature=0.7,seed={seed}

def run_all_models(models: list[dict], results_dir: Path) -> dict[str, bool]: ...
    # Iterates all 30 models; runs greedy + 3 stochastic seeds
    # Returns success dict; continues on per-model failure
    # Validates >= 25 models succeeded

def get_batch_size(params_b: float) -> int: ...
    # Returns batch size from BATCH_SIZE config based on param count
```

---

### CalibrationExtractor (`code/calibration.py`)

**Dependencies**: config, netcal, numpy, json, glob, pathlib

```python
def load_mmlu_samples(model_results_path: Path) -> list[dict]: ...
    # Reads samples_mmlu*.jsonl from lm-eval --log_samples output

def compute_ece_brier(samples: list[dict], n_bins: int = 10) -> tuple[float, float]: ...
    # Extracts filtered_resps log-probs; normalizes to probs
    # Returns (ECE, Brier) scalars

def extract_calibration_for_model(model_id: str, results_dir: Path) -> dict[str, float]: ...
    # Returns {"ece_greedy": ..., "brier_greedy": ...,
    #          "ece_stochastic": ..., "brier_stochastic": ...}
    # Stochastic = average over 3 seeds
```

---

### ScoreMatrix (`code/score_matrix.py`)

**Dependencies**: config, calibration, pandas, json, pathlib

```python
def load_lmeval_summary(model_results_path: Path) -> dict: ...
    # Reads results_*.json from lm-eval output; returns task accuracies

def compute_adv_glue_drop(model_results_path: Path) -> float: ...
    # Returns standard_glue_acc - adversarial_glue_acc

def compute_anli_drop(model_results_path: Path) -> float: ...
    # Returns anli_r1r2_avg_acc - anli_r3_acc

def build_score_matrix(models: list[dict], results_dir: Path,
                        calibration_data: dict) -> pd.DataFrame: ...
    # Returns N×8 DataFrame: [model_id, ECE, Brier, TruthfulQA_pct,
    #                          AdvGLUE_drop, ANLI_drop, MMLU_acc, HumanEval_pass1]
    # Includes both greedy and stochastic variants

def validate_matrix(df: pd.DataFrame) -> bool: ...
    # Checks >= 25 rows, no NaN in gate columns
```

---

### StatAnalysis (`code/analysis.py`)

**Dependencies**: config, pandas, numpy, pingouin, factor_analyzer, scipy, sklearn

```python
def compute_partial_corr_matrix(df: pd.DataFrame, covar: str = "MMLU_acc") -> pd.DataFrame: ...
    # Returns DataFrame of (x, y, rho, ci_low, ci_high, p_value) for all pairs
    # Uses pg.partial_corr(..., method='spearman')

def bca_bootstrap_ci(df: pd.DataFrame, x: str, y: str,
                     covar: str, n_boot: int = 10000) -> tuple[float, float]: ...
    # BCa bootstrap; returns (ci_low, ci_high)

def run_factor_analysis(df: pd.DataFrame, indicators: list[str],
                        n_factors: int = 1) -> tuple: ...
    # Returns (FactorAnalyzer, loadings, variance_explained, kmo)
    # ML estimation, promax rotation

def compute_tucker_congruence(loadings_a: np.ndarray,
                               loadings_b: np.ndarray) -> float: ...
    # Wraps factor_analyzer.utils.calculate_tucker_congruence

def run_loo_logistic(df: pd.DataFrame, features: list[str],
                     target: str) -> dict: ...
    # LOO LogisticRegressionCV; returns {"auc": float, "auc_mmlu_only": float}

def evaluate_gates(corr_df: pd.DataFrame, gate_pairs: list[tuple],
                   threshold: float) -> dict: ...
    # Returns {"PASS": bool, "results": [{pair, rho, ci, passes}, ...]}
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: config, pandas, numpy, matplotlib, seaborn, pathlib

```python
def plot_gate_bar(corr_df: pd.DataFrame, gate_pairs: list[tuple],
                  threshold: float, out_dir: Path) -> None: ...
    # FR-7.1: partial ρ bar chart vs. 0.40 threshold with BCa CI error bars

def plot_corr_heatmap(corr_df: pd.DataFrame, out_dir: Path) -> None: ...
    # FR-7.2: 5×5 partial correlation heatmap with significance stars

def plot_factor_loadings(fa: object, indicators: list[str],
                          out_dir: Path) -> None: ...
    # FR-7.3: factor loadings bar chart

def plot_tucker_congruence(loadings_g: np.ndarray, loadings_s: np.ndarray,
                            congruence: float, indicators: list[str],
                            out_dir: Path) -> None: ...
    # FR-7.4: side-by-side loading plot with congruence annotation

def plot_family_scatter(df: pd.DataFrame, out_dir: Path) -> None: ...
    # FR-7.5: ECE vs TruthfulQA_pct scatter colored by family

def plot_decoding_invariance(corr_greedy: pd.DataFrame,
                              corr_stochastic: pd.DataFrame,
                              out_dir: Path) -> None: ...
    # FR-7.6: greedy vs T=0.7 partial ρ scatter
```

---

### Reporter (`code/report.py`)

**Dependencies**: config, json, pathlib, datetime

```python
def write_results_json(score_matrix: pd.DataFrame, corr_results: pd.DataFrame,
                        factor_results: dict, gate_eval: dict,
                        out_path: Path) -> None: ...
    # Writes 04_results.json per FR-8.1

def write_validation_md(gate_eval: dict, corr_results: pd.DataFrame,
                         factor_results: dict, loo_results: dict,
                         out_path: Path) -> None: ...
    # Writes 04_validation.md per FR-8.2
```

---

### Main Orchestrator (`code/main.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # 1. run_eval.run_all_models(...)
    # 2. calibration.extract_calibration_for_model(...) for each model
    # 3. score_matrix.build_score_matrix(...)
    # 4. analysis.compute_partial_corr_matrix(...)
    #    analysis.bca_bootstrap_ci(...) for gate pairs
    #    analysis.run_factor_analysis(...) greedy + stochastic
    #    analysis.compute_tucker_congruence(...)
    #    analysis.run_loo_logistic(...)
    #    analysis.evaluate_gates(...)
    # 5. visualize.* (all 6 plots)
    # 6. report.write_results_json(...), report.write_validation_md(...)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Environment & Model Inventory | Setup project, install deps, verify 30 model HF IDs accessible, write config.py | 6 | 2+1+1+2 |
| E-2 | LM-Eval Evaluation Pipeline | Implement run_eval.py; run all 30 models greedy + 3 stochastic seeds; handle GPU memory, 4-bit for 70B | 16 | 3+4+4+5 |
| E-3 | Calibration Metric Extraction | Implement calibration.py; parse lm-eval jsonl logits; compute ECE + Brier via netcal | 10 | 3+3+2+2 |
| E-4 | Score Matrix Assembly | Implement score_matrix.py; assemble N×8 DataFrame; compute AdvGLUE drop and ANLI drop | 9 | 2+3+2+2 |
| E-5 | Statistical Analysis | Implement analysis.py; partial Spearman ρ, BCa bootstrap, factor analysis, Tucker congruence, LOO | 15 | 3+4+5+3 |
| E-6 | Visualization & Reporting | Implement visualize.py + report.py; all 6 figures; 04_results.json + 04_validation.md | 10 | 3+2+2+3 |

**Distribution**: High(14-17): [E-2, E-5], Medium(9-13): [E-3, E-4, E-6], Low(4-8): [E-1]

---

## External Dependencies

| Package | Version | Usage |
|---------|---------|-------|
| lm_eval | >=0.4.0 | benchmark evaluation (CLI) |
| transformers | >=4.36.0 | model loading (via lm-eval) |
| torch | >=2.0.0 | GPU inference |
| accelerate | >=0.24.0 | multi-GPU / device mapping |
| bitsandbytes | >=0.41.0 | 4-bit quantization for 70B |
| netcal | >=1.3.0 | ECE + Brier computation |
| pingouin | >=0.5.3 | partial_corr with Spearman |
| factor_analyzer | >=0.4.1 | FactorAnalyzer + Tucker congruence |
| scipy | >=1.11.0 | BCa bootstrap utilities |
| numpy | >=1.24.0 | numerical ops |
| pandas | >=2.0.0 | score matrix DataFrame |
| scikit-learn | >=1.3.0 | LogisticRegressionCV for LOO |
| matplotlib | >=3.7.0 | figure rendering |
| seaborn | >=0.12.0 | heatmap styling |
| pyyaml | >=6.0 | config / state file I/O |
