# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-08-08T08:10:00Z
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL
**Gate Type:** MUST_WORK

## Hypothesis Statement

Architecture family classification NMI exceeds permutation baseline with p < 0.05

## Performance Gap

| Metric | Observed | Threshold | Gap |
|--------|----------|-----------|-----|
| NMI | 0.514 | 0.529 (95th pct) | -0.015 |
| p-value | 0.153 | < 0.05 | +0.103 |

## Root Cause Analysis

- High baseline NMI: With 12 families for 42 models, random label-cluster associations already produce substantial NMI (mean 0.48)
- Limited statistical power: Small sample size (42 models) with many categories (12 families) reduces ability to detect true signal
- Heterogeneous "GPT" family: Grouping OPT, Pythia, MPT, Neo under "GPT" creates a large but architecturally diverse category, diluting family-specific patterns
- Architecture family labels at this granularity may be too coarse or too fine to capture performance-relevant distinctions

## Lessons Learned

1. Architecture family as currently defined does NOT predict benchmark score clustering
2. Multi-factor structure found in h-e1 may reflect training methodology rather than architecture
3. Need coarser categories (e.g., "transformer-decoder" vs "mixture-of-experts") or different mechanism
4. Sample size of 42 models with 12 categories is underpowered for NMI-based detection

## Feedback for Phase 2A

### Suggested Modifications
- Reformulate with coarser architecture categories (2-4 groups instead of 12)
- Test alternative mechanisms: training objective, parameter scale as continuous predictor
- Consider chat-tuning status as the mechanism variable instead of architecture family

### What NOT To Do
- Do not use fine-grained architecture family labels with small sample
- Do not expect architecture to predict performance without controlling for training methodology

### What Showed Promise
- Multi-factor structure confirmed in h-e1 (prerequisite passed)
- Clustering itself works; the architecture labels just don't predict it

---
*For cross-phase reference*
*Written at: 2026-08-08T08:10:00Z*
