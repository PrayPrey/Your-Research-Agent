# Product Requirements Document: H-E1

**Hypothesis:** Model Zoo Dataset Validity
**Date:** 2026-08-19
**Author:** PrayPrey
**Type:** EXISTENCE (Proof of Concept)

---

## 1. Executive Summary

Validate that the Model Zoos dataset (Schurholt et al. 2022) provides sufficient accuracy variance (σ > 10%) and consistent labels for downstream accuracy prediction experiments. This is a MUST_WORK gate check before proceeding with mechanism hypotheses.

---

## 2. Problem Statement

Before investing in complex weight embedding architectures, we must verify:
1. Model Zoo accuracy labels have meaningful variance (not all clustered around same value)
2. Labels are consistent and reliable for regression targets
3. Dataset scale is sufficient for statistical validity (minimum 500+ models)

**Gate Condition:** σ(accuracy) > 10%
**Fail Action:** STOP entire verification chain if gate fails

---

## 3. Functional Requirements

### FR-1: Dataset Loading
- Load Model Zoos CIFAR-10 subset accuracy labels
- Source: modelzoos.cc or HuggingFace mirror
- Extract test accuracy from metadata (weights not required for H-E1)
- Handle missing/corrupted entries gracefully

### FR-2: Statistical Analysis
- Compute descriptive statistics: mean, std, min, max
- Compute quartiles (Q1, Q2, Q3) and IQR
- Identify outliers using 1.5×IQR method
- Run Shapiro-Wilk normality test (on subset ≤5000)

### FR-3: Gate Validation
- Check σ(accuracy) > 10% threshold
- Return PASS/FAIL status
- Log all statistics for reproducibility

### FR-4: Visualization
- Histogram of accuracy distribution with annotations
- Box plot showing quartiles and outliers
- Gate comparison bar chart (σ vs threshold)

---

## 4. Data Specification

### 4.1 Primary Dataset

| Property | Value |
|----------|-------|
| **Name** | Model Zoos CIFAR-10 |
| **Source** | Schurholt et al. 2022 (NeurIPS D&B) |
| **Download** | modelzoos.cc OR HuggingFace |
| **Size** | ~5,000-10,000 models |
| **Required Fields** | test_accuracy |
| **Preprocessing** | Filter NaN, normalize to [0,100] |

### 4.2 Download Method

```python
# Option 1: HuggingFace (preferred)
from datasets import load_dataset
zoo = load_dataset("Konstantin-Scheffold/model-zoos", "cifar10")

# Option 2: Direct download
import requests
# Download from modelzoos.cc
```

**Note:** Auto-download dataset - no manual download task required.

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Analysis completes in < 60 seconds
- Memory usage < 4GB (accuracy labels only, no weights)

### NFR-2: Reproducibility
- All random seeds documented (N/A for deterministic analysis)
- Results logged with timestamps

### NFR-3: Portability
- Python 3.8+ compatible
- Works on Linux/macOS/Windows

---

## 6. Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| σ(accuracy) | > 10% | MUST_WORK |
| Sample count | ≥ 500 models | MUST_WORK |
| No systematic errors | Visual inspection | SHOULD_WORK |

---

## 7. Dependencies

### 7.1 Python Packages

```
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.5.0
datasets>=2.0.0  # HuggingFace datasets
torch>=1.10.0    # For .pt file loading fallback
pyyaml>=6.0
```

### 7.2 External References

- Paper: arxiv:2209.14764 (Model Zoos dataset)
- Paper: arxiv:2302.14040 (NFN using model zoos)
- Website: modelzoos.cc

---

## 8. Out of Scope

- Model weight analysis (deferred to H-M1+)
- Training new models
- Accuracy prediction (this only validates dataset)
- Cross-zoo comparison (optional enhancement)

---

## 9. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Dataset unavailable | High | Multiple download sources |
| Low variance | High | Pre-check before full pipeline |
| Label inconsistency | Medium | Cross-reference with paper |

---

## 10. Appendix: Phase 2C Traceability

| PRD Section | Phase 2C Source |
|-------------|-----------------|
| Gate condition | 02c: Gate Condition |
| Dataset spec | 02c: Dataset section |
| Success criteria | 02c: Evaluation section |
| Analysis code | 02c: Core Mechanism Implementation |
