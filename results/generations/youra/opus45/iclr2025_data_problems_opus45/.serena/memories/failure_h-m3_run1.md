# Phase 4 Failure Record: h-m3 (Run 1)

**Date:** 2026-03-24T15:45:00+00:00
**Hypothesis:** h-m3
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL
**Gate Type:** MUST_WORK

## Hypothesis Statement

Under gradient covariance concentration, if gradients align with dominant modes, then hidden representation diversity (PR, SGC) decreases, because weight updates become less varied and push representations toward common subspace.

## Performance Gap

| Metric | Expected | Actual | Gap |
|--------|----------|--------|-----|
| Pearson correlation (gradient rank vs PR) | r > 0.5 | r = -0.624 | OPPOSITE direction |
| PR decline | >= 15% | +13.67% (increased) | WRONG direction |
| SGC increase | >= 10% | -0.38% (stable) | No effect |
| Seed consistency | >= 3/4 positive | 0/4 positive | Complete failure |

## Failed Checks

- SC-1: Correlation r=-0.624 (expected >0.5)
- SC-2: PR increased 13.67% (expected decline)
- SC-3: SGC stable -0.38% (expected increase)
- SC-4: 0/4 seeds positive (expected 3/4)
- SC-5: Temporal mismatch

## Root Cause Analysis

- The mechanistic hypothesis about gradient concentration causing representation homogenization is fundamentally incorrect
- Data shows the OPPOSITE relationship with strong statistical significance (p=0.00113)
- Gradient rank does collapse (5.86 → ~2) as expected from h-m2
- But PR INCREASES (1.81 → 2.06) rather than decreases
- The causal chain h-m2 → h-m3 is broken: gradient concentration does NOT cause representation homogenization

## Lessons Learned

1. **Correlation direction matters**: A statistically significant correlation in the opposite direction is a stronger refutation than no correlation
2. **Mechanism chain breaks**: Even when upstream hypothesis (h-m2: entropy → gradient rank) is validated, downstream mechanism (h-m3: gradient rank → PR) may be invalid
3. **PR as metric**: Participation Ratio may not capture the type of representation change occurring during model collapse
4. **Alternative mechanisms**: The link from data entropy to model collapse may bypass gradient concentration entirely
5. **Consider inverse causality**: PR increase with gradient concentration suggests weights may diverge along random directions per sample

## Feedback for Next Phase

### Suggested Directions (for Phase 0)
- Reconsider the causal chain: h-m1 (entropy collapse) may directly cause perplexity increase without requiring representation homogenization
- Explore alternative metrics for representation degradation (not PR/SGC)
- Consider that "homogenization" may be the wrong framing - collapse may involve different dynamics

### What NOT To Do
- Do not assume gradient dynamics predict representation diversity
- Do not rely on PR/SGC as early warning signals without independent validation
- Do not assume upstream hypothesis validation guarantees downstream hypothesis

### What Showed Promise (from h-m1, h-m2)
- Data entropy collapse is robust (h-m1: 62% token entropy reduction)
- Gradient rank concentration is robust (h-m2: r=0.912 correlation)
- Both are statistically significant and consistent across seeds

## Cascade Effects

- **h-m4 BLOCKED**: Prerequisites h-m3 failed; cannot test "representation homogenization precedes perplexity increase"
- The overall main hypothesis pathway needs reconsideration

## Routing Decision

**Route to Phase 0**: This MUST_WORK failure indicates the proposed mechanism chain is fundamentally flawed. The research direction needs re-evaluation from the beginning.

---
*Failure recorded at: 2026-03-24T15:45:00+00:00*
*For cross-phase reference*