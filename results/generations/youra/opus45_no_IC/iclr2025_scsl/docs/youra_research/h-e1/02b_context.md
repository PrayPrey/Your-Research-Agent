# Phase 2B Context: H-E1 (Onset Delay Existence)

**Date:** 2026-08-12
**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Gate:** MUST_WORK

---

## Hypothesis Statement

Under ERM training on Waterbirds, if we compute onset delay d_i = min{t : L_i(t) < 0.9*L_i(0)} for each sample, then minority-group samples have significantly higher d_i than majority-group samples, because simplicity bias causes majority samples to converge first.

## Rationale

This is the foundation hypothesis. If onset delay does not differ between groups, the entire mechanism is invalid. SPARE and LA-SSL provide indirect support but no direct measurement of onset delay as discriminative signal.

## Variables

- **IV:** Group membership (minority vs majority)
- **DV:** Onset delay d_i (epochs)
- **CV:** Architecture (ResNet-18), optimizer (SGD), dataset (Waterbirds)

## Experimental Setup

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (standard) | Canonical benchmark for spurious correlation with known group structure (waterbird/landbird × water/land background) |
| **Model** | ResNet-18 | Standard architecture for spurious correlation benchmarks, enables comparison with JTT, SPARE, DFR |

**Dataset Details:**
- Source: https://github.com/kohpangwei/group_DRO (Sagawa et al., 2019)
- Path: data/waterbirds/
- Size: 4795 train, 1199 val, 5794 test
- Spurious correlation: 95% (bird type ~ background)

**Model Details:**
- Type: CNN
- Source: torchvision.models.resnet18(pretrained=True)

## Verification Protocol

1. Train ResNet-18 on Waterbirds for 100 epochs, logging per-sample losses every epoch.
2. Compute d_i for all 4795 training samples.
3. At T_early=20, threshold samples by d_i > T_early.
4. Compute precision/recall vs ground-truth minority labels.
5. Perform Mann-Whitney U test on d_i distributions.

## Success Criteria (PoC)

- **Primary:** Precision > 0.5 AND Recall > 0.3 for minority detection
- **Secondary:** Mann-Whitney p < 0.05

## Failure Response

IF fails: ABANDON entire hypothesis (foundation failure)

## Dependencies

None (foundation hypothesis)

## Gate Condition

**Type:** MUST_WORK
**Criteria:** Precision > 0.5, Recall > 0.3
**Failure Action:** ABANDON verification

## Baseline Methods (for Phase 5)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| ERM | ~72% WGA | Waterbirds | Fails on minority groups |
| JTT | ~86% WGA | Waterbirds | Two-stage, binary signal |
| Group DRO | ~91% WGA | Waterbirds | Requires oracle group labels |

---

*Generated from Phase 2B Verification Plan*
