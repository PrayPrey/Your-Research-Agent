# Phase 2B Context: H-M3

**Generated:** 2026-08-19
**Hypothesis ID:** H-M3
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Hypothesis Statement

Second derivative d²WGA/dt² with 5-epoch smoothing detects crystallization as significant negative peak.

## Rationale

Tests the proposed measurement methodology. Critical for practical applicability. The second derivative of worst-group accuracy should show a significant negative peak at the crystallization point because acceleration in decline produces negative second derivative.

## Prerequisites

| Prerequisite | Status | Result |
|--------------|--------|--------|
| H-M2 | COMPLETED | PASS - Spurious probe accuracy maintained (0.9468 >= 0.9451), commitment confirmed |

## Variables

- **Independent:** Smoothing window size (3, 5, 7 epochs)
- **Dependent:** Detectability of crystallization peak (signal-to-noise ratio)
- **Controlled:** Benchmark dataset, architecture

## Experimental Setup

| Component | Selection | Source |
|-----------|-----------|--------|
| Dataset | Waterbirds, CelebA, ColoredMNIST | WILDS benchmark suite |
| Model | ResNet-50 | torchvision.models.resnet50(pretrained=True) |

## Verification Protocol

1. Compute d²WGA/dt² with window sizes 3, 5, 7 epochs
2. Measure peak signal-to-noise ratio for each window
3. Test sensitivity: Does 5-epoch window consistently detect peak?
4. Run across 5 random seeds per benchmark for statistical power
5. Report detection reliability (% of runs where peak is significant)

## Success Criteria (PoC)

- **Primary:** 5-epoch window detects significant peak in >80% of runs
- **Secondary:** Peak timing variance <5 epochs across seeds

## Gate Condition

**Type:** MUST_WORK
- Pass: Detection method validates with >80% reliability
- Fail: PIVOT to alternative window or detection method

## Failure Response

IF fails: PIVOT to alternative window or detection method

## Previous Context

H-M2 validated classifier commitment post-crystallization. Spurious feature probe accuracy maintained at 0.9468, confirming irreversibility. H-M3 now tests whether the proposed d²WGA/dt² method can reliably detect the crystallization point.

## Risks Affecting This Hypothesis

- **R2:** Detection method failure (CRITICAL) - second derivative may be too noisy
- **R3:** Smoothing window sensitivity (MEDIUM) - results may vary with window choice
