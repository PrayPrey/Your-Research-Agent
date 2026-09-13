# Limitation Record: h-m2 (Run 1)

**Date:** 2026-08-09T13:20:00Z
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

NTI does not provide discriminative signal on low-entropy subset. AUROC 0.5136 is near chance level, and 95% CI [0.4639, 0.5628] includes 0.50, meaning we cannot reject the null hypothesis that NTI performs at chance on confident predictions.

## Failed Checks

- AUROC 0.5136 < 0.55 threshold
- 95% CI lower bound 0.4639 < 0.50 requirement
- Cannot reject chance-level performance

## Partial Results

| Metric | Value |
|--------|-------|
| AUROC | 0.5136 |
| 95% CI | [0.4639, 0.5628] |
| Subset size | 1029 samples |
| H_L threshold | 0.0091 (25th percentile) |

## Experiment Summary

Tested whether NTI provides discriminative signal specifically on "confident but wrong" cases (low H_L < 25th percentile). The failure indicates trajectory instability does NOT reliably distinguish correct from incorrect responses when the model is confident. NTI's discriminative power (AUROC 0.5657 on full dataset from h-e1) appears driven primarily by high-entropy samples.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted.

Future research attempts should consider:
1. NTI may be complementary to entropy on high-entropy samples rather than low-entropy
2. Trajectory metrics correlate with overall uncertainty rather than providing orthogonal signal
3. Alternative approaches might focus on high-entropy subsets where NTI shows more promise

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, this limitation informs brainstorming
- **Phase 6 Discussion:** Limitation included in paper's Limitations section

---
*Limitation recorded at: 2026-08-09T13:20:00Z*
*For cross-phase reference*
