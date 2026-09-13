# Phase 2B Context: H-M1
# JIT-generated from 02b_verification_plan.md

---

## Hypothesis Info

**ID:** H-M1
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Status:** READY
**Prerequisites:** none (computationally independent)

**Statement:**
SimCLR trained with background-replacement augmentation (SimCLR-NoBackground) shows a spurious/task probe accuracy ratio at least 5% lower than SimCLR trained with standard augmentations (SimCLR-Original) on Waterbirds (p < 0.05, 5 seeds), with task probe accuracy remaining within 5% — confirming augmentation invariance as the causal mechanism for spurious feature encoding in contrastive SSL.

**Rationale:**
If augmentation invariance is the causal mechanism, then training SimCLR with an augmentation that explicitly removes background-text correlation (background replacement) should reduce spurious feature encoding. This is a causal intervention: we change only the augmentation while holding architecture, dataset, and training procedure constant.

**Success Criteria:**
- SimCLR-NoBackground spurious/task ratio < SimCLR-Original ratio (p < 0.05, difference ≥ 0.05)
- Task probe accuracy difference ≤ 0.05 (representation quality not degraded)

**Falsification:**
- No significant difference in ratios (p > 0.05)
- OR task probe accuracy drops > 5% for SimCLR-NoBackground (confounded)

---

## Experimental Setup

**Dataset:**
- Name: Waterbirds (CUB-200-2011 + Places365 backgrounds via WILDS)
- Type: standard
- Source: WILDS library (`wilds.get_dataset('waterbirds')`)
- Path: auto (WILDS download)
- Hypothesis Fit: Standard spurious correlation benchmark with explicit background/bird labels; background is the spurious attribute; background-replacement augmentation directly targets this spurious feature

**Background Pool for Augmentation:**
- Name: Places365
- Type: standard
- Source: `torchvision.datasets.Places365` or pre-downloaded
- Hypothesis Fit: Used to provide replacement backgrounds during SimCLR augmentation

**Model:**
- Name: ResNet-50 trained from scratch via SimCLR
- Type: custom (trained from scratch on Waterbirds train split)
- Source: train from scratch
- Hypothesis Fit: Same architecture as H-E1 checkpoints; contrastive SSL directly controls augmentation invariance; training from scratch allows full control over augmentation pipeline

---

## Baseline & Comparison Targets

**Baseline:** SimCLR-Original (standard augmentations: random crop 0.2–1.0, color jitter, gaussian blur, horizontal flip)
**Proposed:** SimCLR-NoBackground (same + background-replacement: randomly replace background region with sampled Places365 image before standard augmentations)

**Primary Metric:** spurious/task probe accuracy ratio (logistic regression linear probes on frozen features)
**Confound Metric:** task probe accuracy (must not drop > 5%)

---

## Phase 2B Planning Details

**Compute Estimate:** ~5 hrs (2 conditions × 5 seeds × ≥ 20 epochs SimCLR on Waterbirds, single GPU)
**Implementation Risk:** SimCLR-NoBackground poor representations on small dataset; mitigated by ≥ 20 epochs and task probe accuracy check
**Confound Control:** If task probe accuracy drops > 5%, report as "inconclusive"

**Gate Decision:**
- FAIL: Log; report mechanism as unconfirmed; continue to Phase 5 (SHOULD_WORK gate)
- PARTIAL: Log; continue

---

## Dependencies

- H-E1: No dependency (computationally independent, can run in parallel)
- H-E2: No dependency
- H-D1: No dependency
