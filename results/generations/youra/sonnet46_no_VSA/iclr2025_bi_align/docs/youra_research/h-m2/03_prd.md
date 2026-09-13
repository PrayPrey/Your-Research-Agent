# Product Requirements Document: H-M2

**Version:** 1.0
**Date:** 2026-07-30
**Hypothesis:** H-M2 — Partial Spearman + Fisher Z Difference Test (MECHANISM)
**Status:** DRAFT

---

## 1. Executive Summary

H-M2 tests whether MMLU scale variation confounds the raw Spearman correlation between TruthfulQA MC2 and BBQ accuracy. Using the H-E1 joint dataset (N=297 open-weight LLMs, confirmed by H-M1), the experiment applies `pingouin.partial_corr(method='spearman', covar=['MMLU'])` and then performs a Fisher z difference test between `raw_rho` and `partial_rho`. Gate is satisfied if Fisher z p-value is computed (direction-agnostic: both p<0.05 and p≥0.05 are publishable outcomes). BCa 95% bootstrap CIs (N_bootstrap=5000, clustered by model family via org-prefix) provide an additional CI-overlap criterion.

This is a **purely statistical analysis** on cached data. No model training, no new data collection. Runtime: < 60 seconds on CPU (dominated by bootstrap iterations).

---

## 2. Problem Statement

H-M1 confirmed MMLU R²>0.05 for both TruthfulQA MC2 and BBQ accuracy, establishing MMLU as a valid scale covariate. H-M2 asks: does controlling for MMLU meaningfully change the TruthfulQA×BBQ correlation? If partial_rho ≠ raw_rho significantly (Fisher z p<0.05), MMLU confounds the raw co-movement — alignment benchmarks track scale, not independent safety. If p≥0.05 (null result), alignment co-movement is scale-independent — also a publishable, impactful finding.

**Gate condition:** Fisher z p-value is obtained (execution must succeed; result direction is both valid).

---

## 3. Functional Requirements

### FR-1: Data Loading
- Load H-E1 cached CSV: `docs/youra_research/h-e1/code/data/llm_leaderboard_v1/llm.csv`
- Required columns: `model_name`, `TruthfulQA_MC2`, `BBQ_accuracy`, `MMLU`
- Drop rows with any null in required columns
- Normalize `BBQ_accuracy` to [0, 100] if max ≤ 1.0 (stored as fraction)
- Extract model family: `df['family'] = df['model_name'].str.split('/').str[0]`
- Verify N ≥ 30 after cleaning (expected: N=297)

### FR-2: Raw Spearman Correlation (Baseline)
- Compute `raw_rho = scipy.stats.spearmanr(df['TruthfulQA_MC2'], df['BBQ_accuracy']).statistic`
- Compute `raw_p = scipy.stats.spearmanr(df['TruthfulQA_MC2'], df['BBQ_accuracy']).pvalue`
- Assert `abs(raw_rho) < 1.0` (arctanh domain guard)

### FR-3: Partial Spearman Correlation (Proposed)
- Compute via `pingouin.partial_corr(data=df, x='TruthfulQA_MC2', y='BBQ_accuracy', covar=['MMLU'], method='spearman')`
- Extract `partial_rho = result['r'][0]`, `partial_p = result['p_val'][0]`
- Assert `abs(partial_rho) < 1.0`
- Verify `abs(partial_rho - raw_rho) > 1e-6` (mechanism activation check)

### FR-4: Fisher Z Difference Test
- Apply same-sample formula (SE=sqrt(2/(N-3)), not independent-sample formula):
  - `z_raw = np.arctanh(raw_rho)`
  - `z_partial = np.arctanh(partial_rho)`
  - `z_diff = (z_raw - z_partial) / np.sqrt(2 / (N - 3))`
  - `p_value = 2 * (1 - scipy.stats.norm.cdf(abs(z_diff)))`
- Classify: `outcome = 'SIGNIFICANT' if p_value < 0.05 else 'NULL'`
- Log: `f"raw_rho={raw_rho:.4f}, partial_rho={partial_rho:.4f}, z_diff={z_diff:.4f}, p={p_value:.4f}"`

### FR-5: BCa Bootstrap Confidence Intervals
- Compute BCa 95% CI for `raw_rho` using `pingouin.compute_bootci(x, y, func='spearman', method='bca', paired=True, n_boot=5000, seed=42)`
- Compute BCa 95% CI for `partial_rho` using residual-based approach or `pg.compute_bootci` with partial correlation function
- Determine `ci_overlap_status`: overlapping if `ci_raw[0] <= ci_partial[1] and ci_partial[0] <= ci_raw[1]`
- Family-clustered robustness: compute weighted mean per-family Spearman rho (families with ≥3 members only)

### FR-6: Gate Evaluation
- Gate PASS: p-value is computed without error (direction-agnostic)
- Gate FAIL: execution error only (arctanh domain error, pingouin singular matrix, N<10)
- Log gate result with all metrics
- Outcome assigned: `SIGNIFICANT` (p<0.05 OR non-overlapping CIs) or `NULL` (p≥0.05 AND overlapping CIs)

### FR-7: Visualization
- **Required:** Grouped bar chart: raw_rho vs partial_rho with BCa 95% CI error bars; annotated with Fisher z p-value; color-coded by significance (green=SIGNIFICANT, orange=NULL)
- **Additional:** Scatter plot TruthfulQA MC2 vs BBQ accuracy with MMLU as color gradient (N=297)
- **Additional:** Bootstrap distribution histogram for raw_rho and partial_rho overlaid (shows CI overlap)
- **Additional:** Per-family bar chart of Spearman rho values (robustness check vs Llama-family dominance)
- **Additional:** Number-line CI comparison: z_raw and z_partial with 95% CIs
- Save all figures to `docs/youra_research/h-m2/figures/`

### FR-8: Results Persistence
- Save results dict to `docs/youra_research/h-m2/code/results/h_m2_results.json`
- Save summary to `docs/youra_research/h-m2/code/results/h_m2_summary.txt`

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | Open LLM Leaderboard v1 × lighteval/bbq_helm joint dataset |
| Source | H-E1 cached output (reused from H-M1) |
| Cache path | `docs/youra_research/h-e1/code/data/llm_leaderboard_v1/llm.csv` |
| Format | CSV |
| N (expected) | 297 complete rows (post H-E1 fuzzy join, confirmed H-M1) |
| Columns used | `model_name`, `TruthfulQA_MC2` (0-100), `BBQ_accuracy` (0-1 or 0-100), `MMLU` (0-100) |
| Download required | NO — reuse H-E1 cache |

### 4.2 Column Notes
- `model_name`: String, used for family label extraction (org-prefix before `/`)
- `TruthfulQA_MC2`: Multiple-choice accuracy, scale 0-100
- `BBQ_accuracy`: May be stored as 0-1 fraction; normalize to 0-100
- `MMLU`: Average accuracy across 57 subjects, scale 0-100
- `family`: Derived column, org prefix (e.g., `meta-llama`, `mistralai`)

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Runtime < 60 seconds on CPU (dominated by N_bootstrap=5000 iterations)
- No GPU required

### NFR-2: Reproducibility
- Fixed seed: `seed=42` for all bootstrap operations
- All library versions pinned in requirements

### NFR-3: Correctness
- Use `pingouin.partial_corr(method='spearman')` with inverse-covariance method (v0.4.0+)
- Use same-sample Fisher z SE formula: `SE = sqrt(2/(N-3))` — NOT the independent-sample formula
- BCa bootstrap, NOT percentile bootstrap (non-symmetric CI assumption satisfied by rank correlation)

### NFR-4: Failure Handling
- `|rho| = 1.0` exactly → FAIL with `arctanh domain error` message
- pingouin singular matrix warning → check zero-variance columns before call
- N < 10 per family → skip per-family rho for that family (not a hard failure)
- Missing `BBQ_accuracy` column → FAIL with message

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Computation succeeded | No NaN/error | results dict all fields populated |
| Fisher z p-value obtained | p_value is float in [0,1] | not NaN, not exception |
| Mechanism activated | \|partial_rho - raw_rho\| > 1e-6 | asserted in code |
| BCa CIs computed | ci_raw and ci_partial are 2-tuples | not None |
| Gate PASS | Execution succeeds | gate_pass == True |
| SIGNIFICANT outcome | p<0.05 OR non-overlapping CIs | outcome = 'SIGNIFICANT' |
| NULL outcome | p≥0.05 AND overlapping CIs | outcome = 'NULL' (also valid) |
| Figures generated | 5 figures saved | file existence check |
| Results saved | JSON + TXT | file existence check |

---

## 7. Dependencies

### 7.1 Python Packages

```
scipy>=1.10.0
pingouin>=0.5.0
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
```

### 7.2 External Data Dependencies
- H-E1 cached CSV must exist at `docs/youra_research/h-e1/code/data/llm_leaderboard_v1/llm.csv`
- H-M1 must be VALIDATED (prerequisite: MMLU confirmed as valid covariate)
- No additional downloads required

### 7.3 Reference Implementations
- pingouin: raphaelvallat/pingouin — `partial_corr(method='spearman')` (inverse-covariance, v0.4.0+)
- psinger/CorrelationStats — Fisher z formula for same-sample comparison
- scipy.stats.bootstrap — BCa bootstrap CI (fallback/cross-validation)
- pingouin.compute_bootci — Primary BCa bootstrap for Spearman CI

---

## 8. Out of Scope
- New fuzzy joins or data collection (H-E1 cache reused)
- Structural characterization of partial Spearman (that is H-M3)
- Model training or fine-tuning
- Pearson correlation (Spearman only per H-M1 design)
- Independent-sample Fisher z (this is a same-sample comparison)

---

## 9. Ablation Variants

### Ablation A: Non-clustered vs Clustered BCa CI
- **Primary:** Clustered bootstrap (resample model families, collect all rows per family)
- **Fallback:** `pingouin.compute_bootci` (non-clustered) if clustered implementation fails
- Both variants compute the same metric; difference is in CI width

### Ablation B: Weighted vs Unweighted Family Rho
- **Primary:** Unweighted per-family Spearman rho (robustness check)
- **Secondary:** Family-size-weighted mean Spearman rho (Llama dominance correction)

---

*Source: 02c_experiment_brief.md (2026-07-30)*
*Pipeline position: H-E1 VALIDATED → H-M1 VALIDATED → **H-M2** → H-M3 (if SIGNIFICANT)*
