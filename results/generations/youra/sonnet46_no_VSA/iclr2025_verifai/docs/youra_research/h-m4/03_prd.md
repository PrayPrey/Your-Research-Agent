# Product Requirements Document: H-M4 Cross-Model Contract-Satisfaction Analysis

**Hypothesis ID:** H-M4
**Type:** MECHANISM (Statistical Analysis)
**Date:** 2026-08-03
**Gate:** SHOULD_WORK
**Base Hypothesis:** H-M3 (VALIDATED — mean adaptive contribution = 0.0999, Wilcoxon p = 2.64e-22)

---

## 1. Overview

H-M4 tests whether cross-model contract-satisfaction rate is orthogonal to pass@1⋆ across 5 LLM families. The experiment adds a statistical analysis layer on top of H-M3's per-model, per-task contract-failure rates (Experiment B). Success criteria: Kendall τ ≤ 0.6 (permutation p < 0.05) AND partial ΔR² ≥ 0.10 for model identity in mixed-effects regression, AND cross-model contract-strength gap ≥ 0.10 absolute between best/worst model families controlling for task difficulty.

**Key design principle:** H-M4 is a pure statistical analysis experiment — no new LLM evaluations, no new PBT runs. Primary input is the pre-computed H-M3 Experiment B per-model, per-task contract-satisfaction rates. The computation pipeline runs in < 5 minutes on a single CPU core.

**Continuation context:** H-M3 confirmed PBT finds additional violations (mean contribution = 0.0999, consistent across all 5 models, range 0.099–0.103). H-M4 asks: does contract-satisfaction rate under adaptive PBT vary orthogonally to EvalPlus pass@1⋆? Are there model families that satisfy contracts well but score lower on pass@1⋆, revealing a different quality axis?

---

## 2. Objectives

- **Primary:** Demonstrate Kendall τ ≤ 0.6 and partial ΔR² ≥ 0.10 for model identity in `contract_rate ~ pass@1⋆ + log(model_size) + C(model_family)` mixed-effects regression
- **Secondary:** Cross-model gap ≥ 0.10 absolute between best/worst model families controlling for task difficulty
- **Mechanism proof:** Show that model rankings by contract-satisfaction rate diverge non-trivially from rankings by pass@1⋆, establishing contract satisfaction as an orthogonal code quality dimension

---

## 3. Prerequisites

- H-M3 VALIDATED (gate satisfied):
  - `h-m3/results/experiment_b_per_model_task_rates.csv` — per (model, task) contract-satisfaction rate
  - Columns: `[model_id, task_id, contract_satisfaction_rate, n_programs, n_failing]`
  - Coverage: 17,226 joined triples from 18,200 (94.6%); all 5 model IDs confirmed present
- EvalPlus pass@1⋆ leaderboard data — published reference scores for all 5 target models
- ContractEval task metadata — task type stratification (HumanEval+, MBPP+)

---

## 4. Data Specification

### 4.1 Primary Input: H-M3 Experiment B Results

- **Source:** `h-m3/results/experiment_b_per_model_task_rates.csv`
- **Type:** Pre-computed artifact (no download needed)
- **Format:** CSV with columns `[model_id, task_id, contract_satisfaction_rate, n_programs, n_failing]`
- **Expected rows:** ~17,226 (model × task pairs with coverage ≥ 1 program)
- **Validation:** All 5 model IDs present; per-model row count ≥ 300 tasks (>80% of 364)

### 4.2 Secondary Input: EvalPlus pass@1⋆ Scores

- **Source:** EvalPlus leaderboard (evalplus.github.io/leaderboard) — published JSON or `evalplus` Python package
- **Type:** Published reference scores (no model inference required)
- **Format:** Dict `{model_id: pass@1_score}` for HumanEval+ and MBPP+
- **Reference values:**
  - `gpt-4o-mini`: HumanEval+ 83.5%, MBPP+ 72.2%
  - `deepseek-coder-v2-lite`: HumanEval+ 82.3%, MBPP+ 75.1%
  - `claude-3-haiku`: HumanEval+ ~73%, MBPP+ ~66% (estimated)
  - `codellama-34b`: HumanEval+ ~65%, MBPP+ ~60% (estimated)
  - `codellama-13b`: HumanEval+ ~58%, MBPP+ ~53% (estimated)
- **Loading:** `pip install evalplus; evalplus.get_model_scores()` OR manual JSON parse from leaderboard

### 4.3 Tertiary Input: ContractEval Task Metadata

- **Source:** `data/ContractEval/data/contract_eval_tasks.json` (cloned in H-M1/H-M3)
- **Purpose:** Task type stratification for subgroup analysis (HumanEval+ vs. MBPP+)
- **Loading:** JSON read; 364 tasks with type labels

### 4.4 Model Metadata (Hardcoded Constants)

```python
MODEL_SIZES = {
    "gpt-4o-mini":             8e9,   # estimated (OpenAI undisclosed)
    "claude-3-haiku":          7e9,   # estimated (Anthropic undisclosed)
    "deepseek-coder-v2-lite": 16e9,   # published
    "codellama-13b":          13e9,
    "codellama-34b":          34e9,
}
MODEL_FAMILIES = {
    "gpt-4o-mini":            "closed_openai",
    "claude-3-haiku":         "closed_anthropic",
    "deepseek-coder-v2-lite": "open_deepseek",
    "codellama-13b":          "open_meta",
    "codellama-34b":          "open_meta",
}
```

---

## 5. Functional Requirements

### FR-1: Data Loading and Validation

- Load `h-m3/results/experiment_b_per_model_task_rates.csv` via `pandas.read_csv`
- Validate: all 5 model IDs present; no model has < 300 task rows; NaN rate < 5% per model
- Load EvalPlus pass@1⋆ scores for all 5 models (HumanEval+ and MBPP+ separately)
- Compute weighted average pass@1⋆ per model (weighted by task count in dataset)
- Load ContractEval task metadata for type labels
- Fail early if H-M3 CSV missing or < 3 models with complete coverage

### FR-2: Per-Model Aggregation

- Compute per-model mean contract-satisfaction rate across all tasks
- Compute per-task-type (HumanEval+, MBPP+) mean contract-satisfaction rate per model
- Build `df_long` format: rows are (model × task) pairs; columns include `contract_sat_rate`, `pass_at_1`, `log_size`, `model_family`, `task_id`, `task_type`
- Validate `df_long.shape[0] >= 1500` (5 models × 300+ tasks)

### FR-3: Kendall τ Ranking Correlation (Primary Gate Metric 1)

- Compute Kendall τ-b between per-model mean contract-satisfaction rate and per-model pass@1⋆
- Use `scipy.stats.kendalltau` with `variant='b'` (handles ties)
- Compute exact permutation p-value via `scipy.stats.permutation_test` with `permutation_type='pairings'` (mandatory for n=5)
- Report: τ, two-sided permutation p-value, all 5! = 120 permutation null distribution values
- Secondary: Spearman ρ via `scipy.stats.spearmanr` for robustness check

### FR-4: Partial ΔR² via Mixed-Effects Regression (Primary Gate Metric 2)

- Fit full model: `contract_sat_rate ~ pass_at_1 + log_size + C(model_family)`, task as random intercept, using `statsmodels.formula.api.mixedlm` with `reml=True`
- Fit reduced model: `contract_sat_rate ~ pass_at_1 + log_size`, same grouping
- Compute marginal R² for both using Nakagawa-Schielzeth formula:
  - `R²_m = var(fitted_values) / (var(fitted_values) + re_var + residual_var)`
- Compute `ΔR² = R²_m(full) - R²_m(reduced)` — partial ΔR² for model family fixed effect
- Handle convergence failures: retry with `method=['lbfgs', 'bfgs']`; fallback to OLS if still fails; log fallback

### FR-5: Cross-Model Gap Analysis (Secondary Gate Metric)

- Compute per-task mean contract-satisfaction rate across all models
- Compute per-model residual rate: `model_mean(contract_sat_rate - task_mean(contract_sat_rate))`
- Cross-model gap = `max(residual_rate) - min(residual_rate)` across 5 models
- Report: gap value, best model, worst model, confidence interval via bootstrap (n=1000, seed=42)

### FR-6: Permutation Test for Model Family Coefficient

- Use `scipy.stats` to compute permutation p-value for the model family coefficient in the full mixed-effects model
- This provides statistical significance for ΔR² interpretation

### FR-7: Subgroup Analysis

- Repeat FR-3, FR-4, FR-5 stratified by task type (HumanEval+ tasks only; MBPP+ tasks only)
- Report τ and ΔR² for each stratum
- Flag if results diverge substantially across strata (> 0.2 absolute difference in τ)

### FR-8: Mechanism Activation Verification

- Call `verify_mechanism_activated(results)` before reporting gate outcomes
- Check: τ computed (not NaN), ΔR² computed, n_model_task_pairs ≥ 1500, cross-model variance > 0.001
- Fail if mechanism activation check fails — report which indicator failed

### FR-9: Visualization

- **Required figure:** Bar chart with τ (threshold line 0.6), ΔR² (threshold line 0.10), cross-model gap (threshold line 0.10)
- **Figure 2:** Scatter plot of per-model contract-satisfaction rate (y) vs. pass@1⋆ (x); model labels annotated; τ and regression line shown
- **Figure 3:** Per-model mean contract-satisfaction rate sorted by contract rate; pass@1⋆ rank as secondary axis
- **Figure 4:** Partial R² decomposition stacked bar (pass@1⋆ variance, log_size variance, model_family ΔR², residual)
- **Figure 5:** Permutation null distribution histogram for τ; observed τ marked
- All figures saved to `h-m4/figures/` as PNG (300 dpi)

### FR-10: Results Reporting

- Generate `h-m4/results/h_m4_results.json` with all gate metrics, intermediate values, and model rankings
- Generate `h-m4/results/analysis_summary.txt` with human-readable summary
- Log all intermediate computation steps with values

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility

- All random operations seeded with 42 (bootstrap, any permutation sampling)
- Results must be identical across runs on same input data

### NFR-2: Performance

- Total runtime < 5 minutes on single CPU core
- MixedLM fit expected < 30 seconds per model

### NFR-3: Fail-Fast Behavior

- Fail immediately if H-M3 CSV missing or incomplete (< 3 models)
- Log clear error messages for each failure mode (missing data, convergence failure, insufficient variance)

### NFR-4: Fallback Handling

- MixedLM convergence failure → retry with alternate optimizer → fallback to OLS
- EvalPlus data unavailable → use hardcoded reference scores from Phase 2C
- Model count < 5 → proceed with available models; note limitation in results

---

## 7. Dependencies

### 7.1 Python Packages

```
scipy>=1.10.0          # kendalltau, permutation_test, spearmanr
statsmodels>=0.14.0    # mixedlm, ols
pandas>=2.0.0          # data manipulation
numpy>=1.24.0          # variance computation, log
matplotlib>=3.7.0      # visualization
seaborn>=0.12.0        # statistical plot aesthetics
evalplus>=0.3.0        # pass@1* score loading (optional; fallback: hardcoded)
```

### 7.2 External Data Sources

- `h-m3/results/experiment_b_per_model_task_rates.csv` — local H-M3 artifact
- EvalPlus leaderboard JSON — `pip install evalplus` or manual download
- ContractEval task metadata — already cloned from H-M1/H-M3 setup (`data/ContractEval/`)

### 7.3 External Repositories (Reference Only)

- SciPy docs: `scipy.stats.kendalltau`, `scipy.stats.permutation_test`
- statsmodels docs: `statsmodels.formula.api.mixedlm`
- Nakagawa & Schielzeth (2013): marginal R² formula

---

## 8. Success Criteria

| Metric | Gate | Threshold | Status |
|--------|------|-----------|--------|
| Kendall τ ≤ 0.6 | Primary | τ ≤ 0.6 AND permutation p < 0.05 | TBD |
| Partial ΔR² ≥ 0.10 | Primary | ΔR² ≥ 0.10 for model identity | TBD |
| Cross-model gap | Secondary | ≥ 0.10 absolute task-controlled gap | TBD |
| Spearman ρ ≤ 0.7 | Secondary | Consistent with τ | TBD |

**Gate logic:**
- PASS: τ ≤ 0.6 AND ΔR² ≥ 0.10 AND τ_pvalue < 0.05
- PARTIAL: one of {τ ≤ 0.6, ΔR² ≥ 0.10} met
- FAIL: τ ≥ 0.8 AND ΔR² < 0.05 → reframe as negative result (contracts replicate pass@k rankings)

---

## 9. Output Artifacts

| Artifact | Path | Contents |
|----------|------|----------|
| Results JSON | `h-m4/results/h_m4_results.json` | All gate metrics, rankings, raw values |
| Summary text | `h-m4/results/analysis_summary.txt` | Human-readable gate outcome |
| Figure 1 | `h-m4/figures/gate_metrics_bar.png` | τ, ΔR², gap vs. thresholds |
| Figure 2 | `h-m4/figures/ranking_scatter.png` | Contract rate vs. pass@1* scatter |
| Figure 3 | `h-m4/figures/cross_model_bar.png` | Per-model contract rate sorted |
| Figure 4 | `h-m4/figures/r2_decomposition.png` | R² variance decomposition |
| Figure 5 | `h-m4/figures/permutation_null.png` | Permutation null distribution |
