# Product Requirements Document: h-m1

**Hypothesis:** DNSI correlates negatively with generalization gap (R > 0.4) across 4 benchmarks with ground truth (ImageNet-V2, CIFAR-10.2, ObjectNet, HANS)

**Date:** 2026-08-28
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## 1. Executive Summary

This experiment tests whether Dataset Novelty Saturation Index (DNSI) correlates with generalization gap across 4 benchmarks with measured ground-truth gaps. A negative correlation (R < -0.4) would indicate DNSI predicts how well models generalize beyond their training distribution.

---

## 2. Problem Statement

Machine learning practitioners lack principled metrics to predict generalization gap before deployment. DNSI measures dataset novelty saturation from SOTA progression curves. If DNSI correlates with generalization gap, it becomes a predictive indicator.

**Core Question:** Does DNSI (computed in h-e1) negatively correlate with generalization gap (R < -0.4)?

---

## 3. Functional Requirements

### FR-1: Load DNSI Values from h-e1
- Load DNSI values computed in prerequisite h-e1
- Required benchmarks: ImageNet, CIFAR-10, ObjectNet, HANS (via MNLI)
- Validate values in range [0, 2]

### FR-2: Load Ground Truth Gap Data
- ImageNet-V2 gap: ~12.5% (Recht et al. 2019)
- CIFAR-10.2 gap: ~4% (Recht et al. 2019)
- ObjectNet gap: ~42.5% (Barbu et al. 2019)
- HANS gap: ~40% (McCoy et al. 2019)

### FR-3: Correlation Analysis
- Compute Pearson correlation coefficient
- Compute Spearman rank correlation (more robust for n=4)
- Bootstrap confidence interval (10,000 resamples)

### FR-4: Visualization
- Scatter plot: DNSI vs Gap with regression line
- Bootstrap distribution histogram
- R value annotation with 95% CI

### FR-5: Hypothesis Testing
- Success: R < -0.4 (Pearson OR Spearman) AND negative correlation
- Failure: R > -0.2 OR positive correlation

---

## 4. Data Specification

### 4.1 Primary Dataset

**Name:** DNSI-Gap Correlation Dataset
**Source:** Aggregated from h-e1 outputs + published papers

| Benchmark | DNSI Source | Gap Source | Gap Value |
|-----------|-------------|------------|-----------|
| ImageNet | h-e1/code/data/pwc | Recht 2019 | 0.125 |
| CIFAR-10 | h-e1/code/data/pwc | Recht 2019 | 0.040 |
| ObjectNet | h-e1/code/data/pwc | Barbu 2019 | 0.425 |
| HANS | h-e1/code/data/pwc (MNLI) | McCoy 2019 | 0.400 |

**Loading:**
```python
# Gap data (hardcoded from papers)
gap_data = {
    "ImageNet": 0.125,
    "CIFAR-10": 0.040,
    "ObjectNet": 0.425,
    "HANS": 0.400
}

# DNSI from h-e1 results
dnsi_file = "../h-e1/code/results/dnsi_results.json"
```

### 4.2 No Additional Download Required

All data is either:
- Computed in h-e1 (DNSI values)
- Hardcoded from peer-reviewed papers (gap values)

---

## 5. Non-Functional Requirements

### NFR-1: Statistical Validity
- Bootstrap CI must exclude 0 for significance
- Report both Pearson and Spearman correlations

### NFR-2: Reproducibility
- Set random seed = 42 for bootstrap
- Store all intermediate results

### NFR-3: Small Sample Handling
- Frame as pilot study (n=4)
- Use rank-based methods for robustness

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Primary | R < -0.4 | Pearson OR Spearman |
| Direction | Negative | Sign of R |
| Significance | CI excludes 0 | 95% bootstrap CI |

**MUST_WORK Gate Failure:**
- R > -0.2 OR R > 0 → Hypothesis fails

---

## 7. Dependencies

### 7.1 Python Packages

```
numpy>=1.21.0
scipy>=1.7.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
```

### 7.2 Internal Dependencies

- h-e1 output: `h-e1/code/results/dnsi_results.json`

### 7.3 External References

- Recht et al. 2019: "Do ImageNet Classifiers Generalize to ImageNet?"
- Barbu et al. 2019: "ObjectNet: A large-scale bias-controlled dataset"
- McCoy et al. 2019: "Right for the Wrong Reasons"

---

## 8. Constraints

- n=4 benchmarks (statistical power limitation)
- Relies on h-e1 DNSI values being valid
- Gap values are literature-reported means

---

*Generated for Phase 3 Implementation Planning*
