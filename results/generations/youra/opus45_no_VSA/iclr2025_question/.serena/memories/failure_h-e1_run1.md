# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-09T12:30:00+00:00
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** EFFECT_SIZE_INSUFFICIENT
**Gate Type:** MUST_WORK

## Hypothesis Statement

Residual entropy variance (Var(H - E[H|S,P])) is significantly higher for hallucinated responses than factual responses on TruthfulQA MC1, with effect size d >= 0.2

## Performance Gap

| Metric | Achieved | Required | Gap |
|--------|----------|----------|-----|
| Cohen's d | -0.035 | ≥0.2 | -0.235 (missing by 117%) |
| p-value | 0.456 | <0.05 | +0.406 (not significant) |
| CERV AUROC | 0.636 | >baseline | -0.034 vs baseline 0.670 |

## Key Findings

1. Cohen's d = -0.035, far below 0.2 threshold
2. p-value = 0.456, above 0.05 threshold (not statistically significant)
3. Variance ratio 2.95x exists but not statistically significant
4. Baseline AUROC (0.670) outperforms CERV (0.636)

## Root Cause Analysis

- Conditioning variables (token surprisal, prompt embedding cluster) do not capture hallucination-specific entropy patterns
- Residual variance may not distinguish hallucination from factual uncertainty
- Linear regression conditioning too simplistic for complex entropy-surprisal relationship
- TruthfulQA MC1 may not exhibit strong entropy signal differences between factual/hallucinated

## Lessons Learned

1. CERV approach (entropy residual variance after conditioning) shows no discriminative power for hallucination
2. Effect size negative suggests factual responses may have higher residual variance (opposite direction)
3. Need fundamentally different features or conditioning approach
4. Baseline (simple entropy/surprisal features) more effective than conditional residual approach

## Feedback for Phase 0

### What NOT To Do
- Don't pursue entropy residual variance as primary hallucination signal
- Don't use linear conditioning on surprisal/embedding for this task
- Don't expect TruthfulQA MC1 to show strong entropy-based hallucination signals

### Suggested Modifications
- Consider non-linear entropy-surprisal relationships
- Explore different uncertainty quantification methods (semantic entropy, token-level features)
- Consider multi-layer or attention-based features instead of output entropy

---
*For cross-phase reference*
*Written at: 2026-08-09T12:30:00+00:00*
