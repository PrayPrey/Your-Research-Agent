# Product Requirements Document: H-M1

**Version:** 1.0
**Date:** 2026-07-30
**Hypothesis:** H-M1 — MMLU as Scale Covariate Pre-Test (MECHANISM)
**Status:** DRAFT

---

## 1. Executive Summary

H-M1 verifies that MMLU score is a valid scale covariate before partial Spearman analysis in H-M2. The experiment computes Spearman R²(MMLU, TruthfulQA MC2) and R²(MMLU, BBQ accuracy) on the H-E1 joint dataset (N=297 open-weight LLMs). Both must exceed 0.05 for the MUST_WORK gate to pass. If either fails, MMLU is orthogonal to alignment benchmarks — a publishable null result that terminates H-M2.

This is a **purely statistical analysis** on cached data. No model training, no new data collection. Runtime: < 1 second on CPU.

---

## 2. Problem Statement

H-M2 (partial Spearman: rho(TruthfulQA, BBQ) controlling for MMLU) is only valid if MMLU is actually correlated with both TruthfulQA and BBQ. H-M1 pre-tests this assumption by measuring R² = rho² for both pairs. If MMLU does not correlate with either benchmark, controlling for it is meaningless and H-M2 must be redesigned.

**Gate condition:** R²(MMLU, TruthfulQA MC2) > 0.05 AND R²(MMLU, BBQ accuracy) > 0.05

---

## 3. Functional Requirements

### FR-1: Data Loading
- Load H-E1 cached CSV: `docs/youra_research/h-e1/code/data/llm_leaderboard_v1/llm.csv`
- Required columns: `model_name`, `TruthfulQA_MC2`, `BBQ_accuracy`, `MMLU`
- Drop rows with any null in required columns
- Normalize `BBQ_accuracy` to [0, 100] if max ≤ 1.0 (stored as fraction)
- Verify N ≥ 30 after cleaning (expected: N=297)

### FR-2: Primary Correlation Analysis
- Compute `rho_mmlu_truthqa = scipy.stats.spearmanr(df['MMLU'], df['TruthfulQA_MC2']).statistic`
- Compute `R2_mmlu_truthqa = rho_mmlu_truthqa ** 2`
- Compute `rho_mmlu_bbq = scipy.stats.spearmanr(df['MMLU'], df['BBQ_accuracy']).statistic`
- Compute `R2_mmlu_bbq = rho_mmlu_bbq ** 2`
- Compute p-values for both correlations

### FR-3: Gate Evaluation
- Evaluate: `gate_pass = (R2_mmlu_truthqa > 0.05) and (R2_mmlu_bbq > 0.05)`
- Log: `"H-M1 gate: MMLU R²(TruthfulQA)={val:.3f}, R²(BBQ)={val:.3f} — PASS/FAIL"`

### FR-4: Baseline Raw Correlation
- Compute `raw_rho_truth_bbq = scipy.stats.spearmanr(df['TruthfulQA_MC2'], df['BBQ_accuracy']).statistic`
- This is the unadjusted correlation — input for H-M2 Fisher z difference test

### FR-5: Mechanism Activation Verification
- Verify all R² values are non-NaN floats in [0, 1]
- Verify gate_pass field exists in results dict
- Verify N ≥ 30

### FR-6: Visualization
- **Required:** Bar chart comparing R²(MMLU×TruthfulQA) and R²(MMLU×BBQ) against 0.05 threshold line
- **Additional:** Scatter plot MMLU vs TruthfulQA MC2 (N=297, rho annotated)
- **Additional:** Scatter plot MMLU vs BBQ accuracy (N=297, rho annotated)
- **Additional:** Correlation heatmap {MMLU, TruthfulQA MC2, BBQ accuracy}
- Save all figures to `docs/youra_research/h-m1/figures/`

### FR-7: Results Persistence
- Save results dict to `docs/youra_research/h-m1/code/results/h_m1_results.json`
- Save results summary to `docs/youra_research/h-m1/code/results/h_m1_summary.txt`

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | Open LLM Leaderboard v1 × lighteval/bbq_helm joint dataset |
| Source | H-E1 cached output |
| Cache path | `docs/youra_research/h-e1/code/data/llm_leaderboard_v1/llm.csv` |
| Format | CSV |
| N (expected) | 297 complete rows (post H-E1 fuzzy join) |
| Columns used | `TruthfulQA_MC2` (0-100), `BBQ_accuracy` (0-1 or 0-100), `MMLU` (0-100) |
| Download required | NO — reuse H-E1 cache |

### 4.2 Column Notes

- `TruthfulQA_MC2`: Multiple-choice accuracy, scale 0-100
- `BBQ_accuracy`: May be stored as 0-1 fraction; normalize to 0-100
- `MMLU`: Average accuracy across 57 subjects, scale 0-100

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Runtime < 5 seconds on CPU (N=297 rows, trivial computation)
- No GPU required

### NFR-2: Reproducibility
- Fixed seed: `np.random.seed(42)` for any bootstrap operations
- All library versions pinned in requirements

### NFR-3: Correctness
- Use `scipy.stats.spearmanr` (handles ties via rank averaging)
- Do NOT use Pearson correlation
- R² = rho², not r² from linear regression

### NFR-4: Failure Handling
- `NaN` in R² → FAIL with message ("BBQ column all-same or N too small")
- N < 30 after dropna() → FAIL with message
- Missing `BBQ_accuracy` column → FAIL with message (H-E1 cache may use ARC proxy)

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Computation succeeded | No NaN/error | indicators dict all True |
| Gate PASS | R²(MMLU,TruthfulQA) > 0.05 AND R²(MMLU,BBQ) > 0.05 | gate_pass == True |
| N valid | N ≥ 30 | len(df) after dropna |
| Figures generated | 4 figures saved | file existence check |
| Results saved | JSON + TXT | file existence check |

**Note on gate failure:** R² ≤ 0.05 is a valid scientific result (publishable null), not a code failure. Gate FAIL = MMLU orthogonal to alignment benchmarks → skip H-M2.

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
- No additional downloads required

### 7.3 Reference Repositories

- pingouin: https://github.com/raphaelvallat/pingouin (partial_corr API reference for H-M2)
- scipy: https://github.com/scipy/scipy (spearmanr, bootstrap)

---

## 8. Out of Scope

- Partial Spearman correlation (that is H-M2)
- Fisher z difference test (that is H-M2)
- Model training or fine-tuning
- New data collection or fuzzy join
- Cluster-stratified bootstrap (H-M2 only)

---

## 9. Ablation Variants

No ablation variants required for H-M1 (single statistical pre-test). The only branching is gate pass/fail, which determines whether H-M2 proceeds.

---

*Source: 02c_experiment_brief.md (2026-07-30)*
*Pipeline position: H-E1 VALIDATED → **H-M1** → H-M2 (if gate passes)*
