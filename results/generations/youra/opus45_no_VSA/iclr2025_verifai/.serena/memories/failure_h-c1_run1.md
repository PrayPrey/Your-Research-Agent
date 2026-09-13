# Phase 4 Failure Record: h-c1 (Run 1)

**Date:** 2026-08-09T17:45:00+09:00
**Hypothesis:** h-c1
**Run:** 1
**Final Status:** FAILED
**Failure Type:** MUST_WORK_GATE_NOT_MET
**Gate Type:** MUST_WORK

## Hypothesis Statement

Cascaded static→execution feedback yields ≥25% relative improvement in pass@1 over execution-only feedback on HumanEval (164) + MBPP (500) after 3 iterations.

## Performance Gap

| Metric | Achieved | Threshold | Gap |
|--------|----------|-----------|-----|
| Relative Improvement | 16.18% | ≥25% | -8.82pp |
| Baseline pass@1 | 0.7726 | - | - |
| Cascaded pass@1 | 0.8976 | - | - |

## Statistical Validation

- **P-value:** 8.38e-10 (statistically significant)
- **95% CI:** [11.19%, 21.93%]
- Improvement is REAL but INSUFFICIENT for threshold

## Root Cause Analysis

- 25% threshold was overly optimistic given literature (10-20% typical)
- H-M1 orthogonality (34.5% overlap) provides partial, not complete complementarity
- Diminishing returns after 3 iterations on hard errors
- Not all static errors are fixable via LLM feedback alone

## Lessons Learned

1. Literature alignment: 16% matches published self-repair gains (12-17%)
2. Threshold setting: Should have used 15-20% based on prior work
3. Orthogonality benefit is bounded by error fixability, not just detection

## Feedback for Phase 2A-Dialogue

### Suggested Modifications
- Lower threshold to ≥15% (empirically supported by this experiment)
- Or explore stronger static analyzers (beyond Pyright)
- Or add semantic-level analysis for deeper error diagnosis

### What NOT To Do
- Do not assume orthogonality translates linearly to improvement
- Do not set thresholds above literature baselines without justification

### What Showed Promise
- Mechanism confirmed working (664/664 problems)
- Ordering correct (static→exec) in all cases
- Per-dataset gains consistent (HumanEval +19.19%, MBPP +15.21%)

---
*Routing: Phase 2A-Dialogue for hypothesis revision*
*Written at: 2026-08-09T17:45:00+09:00*