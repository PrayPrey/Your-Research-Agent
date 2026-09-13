# Logic: H-E1 — Epistemic Reliability as a Latent Dimension

**Hypothesis:** H-E1 (EXISTENCE / MUST_WORK)
**Date:** 2026-04-30

Applied: pipeline-stage-separation
Applied: evaluation-harness-subprocess-runner
Applied: bca-bootstrap-ci-pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## E-2: LM-Eval Evaluation Pipeline [Complexity: 16, Budget: 3 subtasks]

Applied: evaluation-harness-subprocess-runner

### API Signatures

```python
# run_eval.py

def get_batch_size(params_b: float) -> int:
    """Return batch size from BATCH_SIZE config dict keyed by param tier."""
    # params_b: float (e.g. 7.0, 13.0, 70.0)
    # returns: int batch size

def run_model_greedy(model: dict, output_dir: Path) -> bool:
    """Run lm-eval greedy decode for one model; return True on success.
    
    model: {"id": str, "hf_id": str, "params": float, "family": str}
    output_dir: Path — model-specific results subdirectory
    """
    # dtype=float16 for <40B; load_in_4bit=True for >=40B
    # CLI flags: --log_samples --seed 42 --tasks mmlu,truthfulqa_mc1,adv_glue,anli_r3,humaneval
    # Returns False on subprocess non-zero exit

def run_model_stochastic(model: dict, seed: int, output_dir: Path) -> bool:
    """Run lm-eval stochastic decode (T=0.7) for one model and seed.
    
    seed: int — one of [42, 123, 456]
    Returns True on success, False on failure.
    """
    # --gen_kwargs temperature=0.7,seed={seed}

def run_all_models(models: list[dict], results_dir: Path) -> dict[str, bool]:
    """Run greedy + 3 stochastic seeds for all models; return success map.
    
    Returns: {"model_id": True/False, ...} — greedy success per model
    Raises: SystemExit if successful_count < 25
    """
```

### Tensor Shapes

Not applicable — subprocess runner returns scalar bool/int, no tensors.

### Pseudo-code

Not required — straightforward subprocess loop with error catch.

### Error Handling

```python
# Per-model failure pattern:
try:
    success = run_model_greedy(model, out_dir)
except Exception as e:
    logger.error(f"Model {model['id']} failed: {e}")
    success = False
results[model["id"]] = success

# After all models:
n_ok = sum(results.values())
if n_ok < 25:
    sys.exit(f"ABORT: Only {n_ok}/30 models succeeded. Minimum 25 required.")
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-1 | greedy_stochastic_runners | Implement run_model_greedy + run_model_stochastic with 4-bit logic for >=40B |
| L-E2-2 | run_all_models | Implement run_all_models with per-model error handling and N>=25 validation |
| L-E2-3 | batch_size_gpu_guard | Implement get_batch_size lookup + subprocess GPU memory guard |

---

## E-5: Statistical Analysis [Complexity: 15, Budget: 3 subtasks]

Applied: bca-bootstrap-ci-pattern

### API Signatures

```python
# analysis.py

def compute_partial_corr_matrix(
    df: pd.DataFrame,
    indicators: list[str],  # 5 indicator names
    covar: str = "MMLU_acc"
) -> pd.DataFrame:
    """Compute all 10 partial Spearman ρ pairs; return long-form DataFrame.
    
    Returns: DataFrame columns=[x, y, rho, ci_low, ci_high, p_value], 10 rows
    """
    # Uses pg.partial_corr(data=df, x=x, y=y, covar=covar, method='spearman')
    # BCa CI appended via bca_bootstrap_ci()

def bca_bootstrap_ci(
    df: pd.DataFrame,
    x: str,
    y: str,
    covar: str,
    n_boot: int = 10000,
    alpha: float = 0.05
) -> tuple[float, float]:
    """BCa bootstrap CI for partial Spearman rho. Returns (ci_low, ci_high)."""

def run_factor_analysis(
    df: pd.DataFrame,
    indicators: list[str],
    n_factors: int = 1
) -> tuple[object, np.ndarray, float, float]:
    """Run FactorAnalyzer (ML, promax). Returns (fa, loadings, var_explained, kmo).
    
    loadings: np.ndarray shape [5, 1]
    var_explained: float (proportion)
    kmo: float (KMO adequacy)
    """
    # factor_analyzer.FactorAnalyzer(n_factors=n_factors, method='ml', rotation='promax')
    # fa.fit(df[indicators])
    # kmo via factor_analyzer.calculate_kmo(df[indicators])

def compute_tucker_congruence(
    loadings_a: np.ndarray,  # [5, 1]
    loadings_b: np.ndarray   # [5, 1]
) -> float:
    """Compute Tucker's congruence coefficient. Returns scalar float."""
    # factor_analyzer.utils.calculate_tucker_congruence(loadings_a, loadings_b)

def run_loo_logistic(
    df: pd.DataFrame,
    features: list[str],     # ["ECE", "TruthfulQA_pct", "Brier"]
    target: str              # binary: top-quartile AdvGLUE failure
) -> dict:
    """LOO LogisticRegressionCV; returns AUC vs. MMLU-only baseline.
    
    Returns: {"auc": float, "auc_mmlu_only": float}
    """

def evaluate_gates(
    corr_df: pd.DataFrame,
    gate_pairs: list[tuple],  # [("ECE","TruthfulQA_pct"), ("ECE","AdvGLUE_drop")]
    threshold: float = 0.40
) -> dict:
    """Evaluate PASS/FAIL for each gate pair.
    
    Returns: {
        "PASS": bool,  # True if ALL pairs pass
        "results": [{"pair": tuple, "rho": float, "ci": tuple, "passes": bool}, ...]
    }
    """
```

### Data Schemas

```python
# corr_df schema (10 rows for C(5,2)=10 pairs):
# columns: x (str), y (str), rho (float64), ci_low (float64), ci_high (float64), p_value (float64)

# factor_results dict:
# {
#   "loadings": np.ndarray [5, 1],
#   "variance_explained": float,
#   "kmo": float,
#   "congruence": float   # greedy vs stochastic
# }

# gate_eval dict:
# {
#   "PASS": bool,
#   "results": [
#     {"pair": ("ECE","TruthfulQA_pct"), "rho": 0.52, "ci": (0.21, 0.74), "passes": True},
#     ...
#   ]
# }
```

### Pseudo-code for Complex Algorithms

**1. BCa Bootstrap CI:**
```
def bca_bootstrap_ci(df, x, y, covar, n_boot=10000, alpha=0.05):
    # Observed statistic
    rho_obs = pg.partial_corr(df, x, y, covar, method='spearman')['r'].values[0]
    
    # Bootstrap resamples
    boot_rhos = []
    for _ in range(n_boot):
        df_resample = df.sample(n=len(df), replace=True)
        r = pg.partial_corr(df_resample, x, y, covar, method='spearman')['r'].values[0]
        boot_rhos.append(r)
    boot_rhos = np.array(boot_rhos)
    
    # Bias correction z0
    z0 = norm.ppf(np.mean(boot_rhos < rho_obs))
    
    # Acceleration a via jackknife
    jack_rhos = []
    for i in range(len(df)):
        df_jack = df.drop(index=df.index[i])
        r = pg.partial_corr(df_jack, x, y, covar, method='spearman')['r'].values[0]
        jack_rhos.append(r)
    jack_mean = np.mean(jack_rhos)
    num = np.sum((jack_mean - jack_rhos)**3)
    den = 6 * np.sum((jack_mean - jack_rhos)**2)**1.5
    a = num / den if den != 0 else 0.0
    
    # BCa percentiles
    z_alpha = norm.ppf(alpha / 2)
    z_1malpha = norm.ppf(1 - alpha / 2)
    p_lo = norm.cdf(z0 + (z0 + z_alpha) / (1 - a*(z0 + z_alpha)))
    p_hi = norm.cdf(z0 + (z0 + z_1malpha) / (1 - a*(z0 + z_1malpha)))
    
    return (np.percentile(boot_rhos, 100*p_lo), np.percentile(boot_rhos, 100*p_hi))
```

**2. Factor Analysis Congruence (greedy vs. T=0.7):**
```
def compare_factor_stability(df_greedy, df_stochastic, indicators):
    fa_g, loadings_g, var_g, kmo_g = run_factor_analysis(df_greedy, indicators)
    fa_s, loadings_s, var_s, kmo_s = run_factor_analysis(df_stochastic, indicators)
    
    # Align sign: ensure dominant loading is positive in both
    if loadings_g[np.argmax(np.abs(loadings_g))] < 0:
        loadings_g = -loadings_g
    if loadings_s[np.argmax(np.abs(loadings_s))] < 0:
        loadings_s = -loadings_s
    
    congruence = compute_tucker_congruence(loadings_g, loadings_s)
    return congruence  # gate: >= 0.85
```

**3. LOO AUC with MMLU-only baseline:**
```
def run_loo_logistic(df, features, target):
    # Binarize target: top-quartile AdvGLUE failure
    q75 = df["AdvGLUE_drop"].quantile(0.75)
    y = (df["AdvGLUE_drop"] >= q75).astype(int).values
    
    loo = LeaveOneOut()
    
    # Full model
    X_full = df[features].values
    scores_full = cross_val_score(
        LogisticRegressionCV(cv=5, max_iter=1000), X_full, y,
        cv=loo, scoring="roc_auc"
    )
    
    # MMLU-only baseline
    X_mmlu = df[["MMLU_acc"]].values
    scores_mmlu = cross_val_score(
        LogisticRegressionCV(cv=5, max_iter=1000), X_mmlu, y,
        cv=loo, scoring="roc_auc"
    )
    
    return {"auc": np.mean(scores_full), "auc_mmlu_only": np.mean(scores_mmlu)}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E5-1 | partial_corr_bca | Implement compute_partial_corr_matrix (10 pairs) + bca_bootstrap_ci |
| L-E5-2 | factor_analysis | Implement run_factor_analysis + compute_tucker_congruence with sign alignment |
| L-E5-3 | loo_gates | Implement run_loo_logistic (target binarization, LOO AUC) + evaluate_gates PASS/FAIL |

---

## E-3: Calibration Metric Extraction [Complexity: 10, Budget: 1 subtask]

Applied: pipeline-stage-separation

### API Signatures

```python
# calibration.py

def load_mmlu_samples(model_results_path: Path) -> list[dict]:
    """Read samples_mmlu*.jsonl from lm-eval --log_samples output.
    
    model_results_path: Path to model's results directory
    Returns: list of sample dicts with keys: filtered_resps, target, doc
    """
    # glob: model_results_path / "samples_mmlu*.jsonl"
    # Each line is JSON; concatenate all subjects

def compute_ece_brier(
    samples: list[dict],
    n_bins: int = 10
) -> tuple[float, float]:
    """Extract logits from filtered_resps, compute ECE and Brier score.
    
    Returns: (ece: float, brier: float)
    """
    # filtered_resps: list of [[log_prob, is_greedy], ...] per choice
    # Extract log_probs for 4 answer tokens; softmax → probs
    # confidence = max(probs); correctness = int(argmax==target)
    # ECE: netcal.metrics.ECE(n_bins=n_bins).measure(confidences, correctness)
    # Brier: mean((confidence - correctness)**2)

def extract_calibration_for_model(
    model_id: str,
    results_dir: Path
) -> dict[str, float]:
    """Compute ECE+Brier for greedy and stochastic (avg 3 seeds).
    
    Returns: {
        "ece_greedy": float, "brier_greedy": float,
        "ece_stochastic": float, "brier_stochastic": float
    }
    Raises: FileNotFoundError if no jsonl found for model.
    """
```

### Key Data Schema

```python
# lm-eval sample JSON (relevant fields):
{
    "doc": {"question": str, "choices": list[str], "answer": int},
    "target": int,                    # correct answer index (0-3)
    "filtered_resps": [               # one entry per choice
        [log_prob: float, is_greedy: bool],
        ...
    ]
}

# From filtered_resps → probs:
# log_probs = [r[0] for r in filtered_resps]  # shape: [4]
# probs = softmax(log_probs)                  # shape: [4]
# confidence = max(probs)
# correctness = int(argmax(probs) == target)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-1 | ece_brier_extraction | Implement compute_ece_brier — logit extraction from lm-eval jsonl, netcal ECE, Brier |

---

## Supporting Module Signatures (Low-complexity, non-Logic-Agent tasks)

These are included for Phase 4 Coder reference; no subtask budget consumed.

```python
# score_matrix.py

def load_lmeval_summary(model_results_path: Path) -> dict:
    """Read results_*.json; return {task: accuracy} dict."""

def compute_adv_glue_drop(model_results_path: Path) -> float:
    """Return standard_glue_acc - adversarial_glue_acc."""

def compute_anli_drop(model_results_path: Path) -> float:
    """Return anli_r1r2_avg_acc - anli_r3_acc."""

def build_score_matrix(
    models: list[dict],
    results_dir: Path,
    calibration_data: dict  # {model_id: {ece_greedy, brier_greedy, ...}}
) -> pd.DataFrame:
    """Assemble N×8 DataFrame.
    
    columns: [model_id, ECE, Brier, TruthfulQA_pct, AdvGLUE_drop, ANLI_drop, MMLU_acc, HumanEval_pass1]
    dtype: float64 (except model_id: str)
    """

def validate_matrix(df: pd.DataFrame) -> bool:
    """Return True if len(df) >= 25 and no NaN in gate columns."""
    # gate columns: ["ECE", "TruthfulQA_pct", "AdvGLUE_drop"]


# visualize.py

def plot_gate_bar(corr_df: pd.DataFrame, gate_pairs: list[tuple],
                  threshold: float, out_dir: Path) -> None:
    """FR-7.1: bar chart of partial rho vs 0.40 threshold with BCa CI error bars."""

def plot_corr_heatmap(corr_df: pd.DataFrame, out_dir: Path) -> None:
    """FR-7.2: 5×5 partial correlation heatmap with significance stars."""

def plot_factor_loadings(fa: object, indicators: list[str], out_dir: Path) -> None:
    """FR-7.3: factor loadings bar chart."""

def plot_tucker_congruence(loadings_g: np.ndarray, loadings_s: np.ndarray,
                            congruence: float, indicators: list[str],
                            out_dir: Path) -> None:
    """FR-7.4: side-by-side loadings with congruence annotation."""

def plot_family_scatter(df: pd.DataFrame, out_dir: Path) -> None:
    """FR-7.5: ECE vs TruthfulQA_pct scatter colored by family."""

def plot_decoding_invariance(corr_greedy: pd.DataFrame,
                              corr_stochastic: pd.DataFrame,
                              out_dir: Path) -> None:
    """FR-7.6: greedy vs T=0.7 partial rho scatter."""


# report.py

def write_results_json(
    score_matrix: pd.DataFrame,
    corr_results: pd.DataFrame,
    factor_results: dict,
    gate_eval: dict,
    out_path: Path
) -> None:
    """Write 04_results.json with score matrix, corr matrix, factor results, gate PASS/FAIL."""

def write_validation_md(
    gate_eval: dict,
    corr_results: pd.DataFrame,
    factor_results: dict,
    loo_results: dict,
    out_path: Path
) -> None:
    """Write 04_validation.md human-readable summary."""


# main.py

def main() -> None:
    """Orchestrate pipeline stages 1-5 sequentially."""
    # Stage 1: run_eval.run_all_models(MODELS, RESULTS_DIR)
    # Stage 2: calibration.extract_calibration_for_model(...) for each model
    # Stage 3: score_matrix.build_score_matrix(...) + validate_matrix(...)
    # Stage 4: analysis.compute_partial_corr_matrix(...)
    #          analysis.bca_bootstrap_ci(...) for gate pairs
    #          analysis.run_factor_analysis(...) greedy + stochastic
    #          analysis.compute_tucker_congruence(...)
    #          analysis.run_loo_logistic(...)
    #          analysis.evaluate_gates(...)
    # Stage 5: visualize.* (all 6 plots)
    #          report.write_results_json(...), report.write_validation_md(...)
```

---

## Subtask Summary [7/7 budget used]

| ID | Epic | Subtask | Description |
|----|------|---------|-------------|
| L-E2-1 | E-2 | greedy_stochastic_runners | run_model_greedy + run_model_stochastic with 4-bit handling |
| L-E2-2 | E-2 | run_all_models | per-model error handling, N>=25 validation |
| L-E2-3 | E-2 | batch_size_gpu_guard | get_batch_size lookup + GPU memory guard |
| L-E5-1 | E-5 | partial_corr_bca | compute_partial_corr_matrix (10 pairs) + bca_bootstrap_ci |
| L-E5-2 | E-5 | factor_analysis | run_factor_analysis + compute_tucker_congruence |
| L-E5-3 | E-5 | loo_gates | run_loo_logistic + evaluate_gates PASS/FAIL |
| L-E3-1 | E-3 | ece_brier_extraction | compute_ece_brier from lm-eval jsonl logits |
