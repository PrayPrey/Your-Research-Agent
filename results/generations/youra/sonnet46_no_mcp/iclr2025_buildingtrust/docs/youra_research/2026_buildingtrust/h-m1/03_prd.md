# Product Requirements Document: H-M1
# Calibration-Hallucination Mechanistic Link (Capability-Independent)

**Hypothesis ID:** H-M1
**Type:** MECHANISM (INCREMENTAL — builds on H-E1)
**Date:** 2026-04-30
**Author:** Anonymous
**Phase:** 3 — Implementation Planning
**Gate:** MUST_WORK

---

## 1. Executive Summary

H-M1 investigates whether the strong calibration-hallucination correlation observed in H-E1 (ρ ≈ -0.758) survives MMLU capability control, establishing it as a mechanistic link rather than a capability artifact. The experiment reuses the H-E1 score matrix (N=30 LLMs × 8 metrics) and applies partial Spearman correlation analysis with BCa bootstrap confidence intervals. No new model evaluations are needed — this is a pure statistical analysis on precomputed data.

**Success Criterion:** partial ρ(ECE, TruthfulQA% | MMLU) magnitude ≥ 0.40, BCa 95% CI excluding zero.

---

## 2. Problem Statement

H-E1 demonstrated that ECE and TruthfulQA% are strongly correlated (ρ = -0.758) across N=30 LLMs. However, this could be a capability artifact: more capable models (high MMLU) may simultaneously have better calibration AND better truthfulness, with no direct mechanistic link between calibration and hallucination.

H-M1 tests:
1. **Construct validity**: Are ECE and Brier score internally consistent as calibration metrics? (ρ ≥ 0.30)
2. **Mechanism validity**: Does ECE-TruthfulQA% correlation survive MMLU control? (partial ρ ≥ 0.40)
3. **Discriminant validity**: Is this mechanism specific to epistemic reliability, not code generation? (partial ρ(ECE, HumanEval|MMLU) < 0.20)
4. **Decoding invariance**: Is the mechanism stable across greedy vs. T=0.7 decoding?

---

## 3. Functional Requirements

### FR-1: Score Matrix Loading
- Load H-E1 score matrix (N=30 × 8 columns) from `h-e1/` output
- Columns: model_id, ECE, Brier, TruthfulQA_pct, AdvGLUE_drop, ANLI_drop, MMLU_acc, HumanEval_pass1
- Load both greedy and T=0.7 versions (2 files)
- Validate: N=30 rows, all 8 columns present, no NaN in key columns

### FR-2: ECE-Brier Internal Consistency (Construct Validity)
- Compute Spearman ρ(ECE, Brier) using scipy.stats.spearmanr
- Compute BCa bootstrap 95% CI (10,000 resamples, seed=42)
- Threshold: ρ ≥ 0.30 (secondary criterion)
- Expected: ρ ≈ 0.80–0.95 (both from MMLU logits)

### FR-3: Partial Spearman Correlation — PRIMARY TEST
- Compute partial ρ(ECE, TruthfulQA_pct | MMLU_acc) using pingouin.partial_corr
- Method: Spearman (non-parametric, N=30)
- Covariate: MMLU_acc (continuous)
- Compute BCa bootstrap 95% CI (10,000 resamples, seed=42)
- **Primary gate**: |partial ρ| ≥ 0.40 AND BCa CI excludes zero

### FR-4: Confound Magnitude Assessment
- Compare raw ρ (from H-E1: ≈ -0.758) vs. partial ρ
- Compute survival_fraction = |partial_ρ| / |raw_ρ|
- Report: fraction of raw correlation explained by MMLU capability
- Threshold check: survival_fraction ≥ 0.50 (MMLU explains < 50%)

### FR-5: Discriminant Validity — HumanEval Control
- Compute partial ρ(ECE, HumanEval_pass1 | MMLU_acc) using pingouin.partial_corr
- Expected: |partial ρ| < 0.20 (code generation ≠ calibration mechanism)
- This validates epistemic reliability specificity

### FR-6: Decoding Invariance Check
- Repeat FR-3 on T=0.7 score matrix
- Expected: partial ρ(T=0.7) ≥ 0.30
- Compare greedy vs. T=0.7 partial ρ values

### FR-7: Visualization (5 figures)
- **Figure 1 (Mandatory)**: Gate metrics bar chart — partial ρ vs. threshold (0.40) with BCa CI
- **Figure 2**: Raw vs. partial ρ comparison (confound magnitude)
- **Figure 3**: ECE-Brier scatter plot (N=30, colored by model family)
- **Figure 4**: Discriminant validity comparison bar chart
- **Figure 5**: Decoding invariance scatter (greedy vs. T=0.7 partial ρ)
- Save all figures to `h-m1/figures/`

### FR-8: Results Export
- Save results dict to `h-m1/results/hm1_results.json`
- Include all metric values, CI bounds, pass/fail for each criterion
- Generate summary report `h-m1/04_validation.md`

---

## 4. Data Specification

### 4.1 Primary Data Source
**Type:** Reused from H-E1 (no new data collection)
- **File**: `h-e1/results/score_matrix.csv` (greedy decoding)
- **File**: `h-e1/results/score_matrix_t07.csv` (T=0.7 decoding)
- **Fallback**: Check `h-e1/code/` output directory if different naming

### 4.2 Score Matrix Schema
```
N=30 rows × 8 columns:
- model_id (str): HuggingFace model identifier
- ECE (float): Expected Calibration Error, 10-bin, from MMLU logits [0,1]
- Brier (float): Brier score, from MMLU logits [0,2]
- TruthfulQA_pct (float): TruthfulQA MC1 accuracy [0,1]
- AdvGLUE_drop (float): standard_GLUE_acc - adversarial_GLUE_acc [0,1]
- ANLI_drop (float): ANLI_R1R2_acc - ANLI_R3_acc [0,1]
- MMLU_acc (float): Overall MMLU accuracy [0,1]
- HumanEval_pass1 (float): HumanEval pass@1 [0,1]
```

### 4.3 Benchmark Details (Already Evaluated in H-E1)
| Benchmark | Task in lm-eval | Questions | Role in H-M1 |
|-----------|----------------|-----------|--------------|
| MMLU | `mmlu` | 14,042 test | ECE/Brier source + CAPABILITY COVARIATE |
| TruthfulQA | `truthfulqa_mc1` | 817 test | Primary outcome (hallucination rate) |
| AdvGLUE | `adv_glue` | ~1,000 test | Secondary discriminant check |
| ANLI | `anli_r3` | 1,200 test | Secondary discriminant check |
| HumanEval | `humaneval` | 164 test | Discriminant validity NEGATIVE CONTROL |

**No new data collection required.** All evaluations completed in H-E1.

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Bootstrap seed: 42 (fixed for all BCa computations)
- Deterministic statistical analysis (no stochastic training)

### NFR-2: Performance
- No GPU required — purely CPU statistical analysis
- Estimated runtime: < 5 minutes
- Memory: < 1 GB

### NFR-3: Code Quality
- Python 3.10+ compatible
- Type-annotated function signatures
- Unit tests for all statistical functions (pytest)
- Minimum 3 real test assertions per test function

### NFR-4: Results Transparency
- All intermediate values logged (raw ρ, partial ρ, CI bounds)
- Pass/fail determination logged for each criterion
- Figures annotated with metric values

---

## 6. Success Criteria

### Primary Gate (MUST_WORK)
| Criterion | Threshold | Status |
|-----------|-----------|--------|
| partial ρ(ECE, TruthfulQA% \| MMLU) | ≥ 0.40 (magnitude) | Gate |
| BCa 95% CI | Excludes zero | Gate |

**Both must pass for MUST_WORK gate to be satisfied.**

### Secondary (Informative)
| Criterion | Threshold | Notes |
|-----------|-----------|-------|
| ρ(ECE, Brier) — construct validity | ≥ 0.30 | Expected ≥ 0.70 |
| Confound magnitude (MMLU explains) | < 50% of raw ρ | Survival ≥ 0.50 |
| Discriminant: partial ρ(ECE, HumanEval\|MMLU) | < 0.20 | Code ≠ calibration |
| Decoding invariance (T=0.7 partial ρ) | ≥ 0.30 | Pipeline independence |

### Expected Performance
- Raw ρ(ECE, TruthfulQA%): ≈ -0.758 (confirmed H-E1)
- Partial ρ after MMLU control: ≈ -0.55 to -0.70 (Phase 2B estimate)
- ρ(ECE, Brier): ≈ 0.80–0.95 (shared logit source)

---

## 7. Dependencies

### 7.1 Python Packages
```
pandas >= 2.0.0
pingouin >= 0.5.3
scipy >= 1.11.0
numpy >= 1.24.0
matplotlib >= 3.7.0
seaborn >= 0.12.0
pytest >= 7.0.0
```

### 7.2 Data Dependencies
- H-E1 Phase 4 output: score matrix (greedy + T=0.7)
- H-E1 Phase 4 validation: confirmed ρ(ECE,TruthfulQA%)=-0.758

### 7.3 Code Dependencies
- All statistical libraries from H-E1 environment (no new packages)

---

## 8. Constraints and Assumptions

### 8.1 Constraints
- H-M1 MUST use the exact same N=30 model population as H-E1 (controlled comparison)
- Bootstrap must use BCa method (not percentile) — N=30 is too small for percentile CI
- MMLU_acc is the ONLY covariate for capability control (specified in Phase 2B)

### 8.2 Key Assumptions
- **A1**: H-E1 score matrix is correctly computed and saved to disk
- **A2**: ECE and Brier both computed from MMLU logits → expected high internal consistency
- **A3**: MMLU capability confound is moderate (20–30% of raw correlation) per Phase 2B
- **A4**: pingouin.partial_corr correctly implements partial Spearman via rank transformation

---

## Appendix: Traceability to Phase 2C

| Requirement | Source in 02c_experiment_brief.md |
|-------------|----------------------------------|
| Score matrix reuse | §Dataset — "REUSED FROM H-E1" |
| partial ρ primary gate | §Evaluation — "Primary Success Criteria" |
| BCa bootstrap (10,000) | §Training Protocol — "Key Parameters" |
| Discriminant validity | §Evaluation — "Secondary Criteria" |
| Decoding invariance | §Evaluation — "Secondary Criteria" |
| 5 figures | §Visualization Requirements |
| No GPU required | §Training Protocol — "Compute Requirements" |
