# Product Requirements Document: H-M1

**Hypothesis:** Calibration moderates the truthfulness-robustness correlation: low-ECE (well-calibrated) models show significantly stronger correlation than high-ECE models (Fisher z-test p < 0.05).

**Date:** 2026-08-28
**Type:** MECHANISM
**Prerequisites:** H-E1 (VALIDATED)

---

## 1. Problem Statement

H-E1 established a strong positive partial correlation (r=0.8028) between TruthfulQA MC1 accuracy and AdvGLUE robustness. H-M1 investigates whether **calibration quality (ECE)** explains this correlation—specifically, whether well-calibrated models exhibit stronger truthfulness-robustness coupling.

## 2. Goals

| Goal | Success Metric |
|------|----------------|
| Compute ECE for all 14 models | ECE scores from MMLU logits |
| Test ECE-metric correlations | r < -0.2, p < 0.10 for both |
| Tertile moderation test | Fisher z p < 0.05, low_r > high_r |

## 3. Scope

### In Scope
- ECE computation from MMLU confidence/accuracy
- Partial correlation: ECE vs TruthfulQA (controlling size)
- Partial correlation: ECE vs AdvGLUE (controlling size)
- Tertile stratification by ECE
- Fisher z-test comparing within-tertile correlations

### Out of Scope
- Temperature scaling or calibration improvement
- New model evaluations beyond ECE
- Alternative calibration metrics (MCE, Brier)

## 4. Requirements

### 4.1 Data Requirements

| Requirement | Specification |
|-------------|---------------|
| MMLU evaluation | Full validation set (~14k samples) |
| Model logits | Confidence scores for ECE |
| Cached scores | Reuse h-e1/code/results/ |

### 4.2 Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-1 | Compute 15-bin ECE from model confidence/accuracy |
| FR-2 | Reuse partial_corr() from h-e1/code/analysis.py |
| FR-3 | Implement Fisher z-test for correlation comparison |
| FR-4 | Split models into ECE tertiles |
| FR-5 | Generate required visualizations |

### 4.3 Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| Reproducibility | Fixed seed (42), deterministic binning |
| Compatibility | Python 3.8+, scipy, numpy |
| Code reuse | Import from h-e1 where possible |

## 5. Dependencies

| Dependency | Source | Status |
|------------|--------|--------|
| TruthfulQA scores | h-e1/code/results/ | Cached |
| AdvGLUE scores | h-e1/code/results/ | Cached |
| log_params | h-e1/code/results/ | Cached |
| partial_corr() | h-e1/code/analysis.py | Available |

## 6. Deliverables

1. `h-m1/code/ece.py` - ECE computation
2. `h-m1/code/analysis.py` - Correlation + Fisher z-test
3. `h-m1/code/main.py` - Orchestration script
4. `h-m1/code/results/` - ECE scores, correlations
5. `h-m1/figures/` - Required visualizations
6. `h-m1/04_validation.md` - Results report

## 7. Success Criteria (Gate Conditions)

| Condition | Threshold |
|-----------|-----------|
| ECE vs TruthfulQA | r < -0.2, p < 0.10 |
| ECE vs AdvGLUE | r < -0.2, p < 0.10 |
| Moderation test | Fisher z p < 0.05 |
| Direction check | low_ECE_r > high_ECE_r |

---

*Generated from 02c_experiment_brief.md*
