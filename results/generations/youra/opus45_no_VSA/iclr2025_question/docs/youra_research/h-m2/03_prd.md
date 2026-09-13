# Product Requirements Document: h-m2

**Date:** 2026-08-09
**Hypothesis:** On low-entropy subset (H_L < 25th percentile), trajectory metrics achieve AUROC > 0.55 with 95% CI LB > 0.50
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Overview

Evaluate whether NTI (Normalized Trajectory Instability) provides discriminative signal for hallucination detection specifically on low-entropy samples where output entropy alone fails.

**Prerequisites:** h-e1 (VALIDATED - Mean AUROC 0.5657)

---

## Goals

1. Filter TruthfulQA MC1 to low-entropy subset (H_L < 25th percentile, ~204 samples)
2. Compute AUROC of NTI on filtered subset
3. Compute 95% bootstrap CI
4. Verify AUROC > 0.55 and CI LB > 0.50

---

## Technical Requirements

### Data Requirements
- **Input:** h-e1 computed features (H_L, NTI, labels) for 817 TruthfulQA samples
- **Processing:** Filter to H_L < 25th percentile
- **Output:** AUROC with 95% CI on ~204 low-entropy samples

### Computational Requirements
- **GPU:** Not required (evaluation only)
- **Memory:** <4GB (NumPy/sklearn operations)
- **Runtime:** <5 minutes

### Dependencies
- numpy, scipy, sklearn (already installed from h-e1)
- matplotlib for visualization

---

## Success Criteria

| Metric | Target | Falsification |
|--------|--------|---------------|
| AUROC | > 0.55 | - |
| 95% CI LB | > 0.50 | CI includes 0.50 |

---

## Deliverables

1. `run_h_m2.py` - Main experiment script
2. `figures/auroc_comparison.png` - Gate metrics visualization
3. `04_validation.md` - Results report

---

## Constraints

- Reuse h-e1 feature files (no recomputation)
- Single seed (42) for reproducibility
- 1000 bootstrap iterations for CI

---

## Out of Scope

- New feature extraction (use h-e1 outputs)
- Model training (evaluation only)
- Multi-seed evaluation (single seed sufficient for CI)
