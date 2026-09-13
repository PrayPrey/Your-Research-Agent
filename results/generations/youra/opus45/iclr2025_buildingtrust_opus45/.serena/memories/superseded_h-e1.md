# Superseded Hypothesis Record

**Date:** 2026-03-23T07:15:00Z
**Hypothesis:** h-e1
**Superseded By:** h-e1-v2
**Status:** SUPERSEDED

## Supersede Reason

LLM self-assessment determined incompatibility with dependent hypotheses. While the interface and data flow are compatible, the behavioral assumptions are invalid and recovery via minor changes is not possible.

**Key Finding:** R² = 0.877 means 87.7% of entropy variance is explained by confounds (Δp_max, H₀, Δtokens). Downstream hypotheses (especially h-m4) assume ε̂_H has meaningful independent variance, but this assumption is compromised.

## Compatibility Assessment

| Factor | Result | Explanation |
|--------|--------|-------------|
| Interface Compatible | Yes | ε̂_H signal computed and available as output |
| Data Flow Valid | Yes | Data artifacts generated with correct shapes (N=14,042) |
| Behavioral Valid | **No** | Downstream hypotheses assume ε̂_H independence, but R²=0.877 compromises this |
| Recovery Possible | **No** | Scientific finding about phenomenon, not code bug - requires hypothesis refinement |

**Decision:** SUPERSEDED (not SELF_MODIFY)

## Cascade Effects

The following hypotheses were marked CASCADE_SUPERSEDED:

- h-m1 (MECHANISM): CoT prompting → coherent reasoning tokens
- h-m2 (MECHANISM): Attention incorporates reasoning → distribution differs from 0-shot
- h-m3 (MECHANISM): Attention reshapes distribution → H_rest changes
- h-m4 (MECHANISM): ε̂_H added to model → MSE decreases ≥5%
- h-c1 (CONDITION): Fixed stage-two model generalizes across model sizes

These will be re-evaluated when h-e1-v2 is ready.

## Partial Results Preserved

| Metric | Value | Notes |
|--------|-------|-------|
| R² | 0.877 | GAM explains 87.7% of variance |
| Var(ε̂_H) | 0.00793 | Residual variance (CI excludes 0) |
| CI | [0.00771, 0.00815] | 95% bootstrap confidence interval |
| N | 14,042 | MMLU test samples |
| CI Gate | PASS | Existence confirmed |
| R² Gate | FAIL | Independence compromised |

## Scientific Insights for Phase 2A-Dialogue

1. **Existence is confirmed:** The residualized entropy signal ε̂_H exists and has non-trivial variance
2. **Independence claim needs revision:** The hypothesis framed ε̂_H as "independent of" confounds, but they explain 87.7% of variance
3. **Potential refinements:**
   - Reframe as "partially independent" or "residual after controlling for"
   - Investigate interaction terms between confounds
   - Consider alternative residualization approaches (e.g., orthogonalization)
   - Test if high R² is model-specific (try Llama-2, other Mistral variants)
4. **The 12.3% unexplained variance may still be meaningful** - need to reframe hypothesis to focus on this residual

## Timeline

1. Original hypothesis: h-e1 (EXISTENCE)
2. Phase 4 validation: PARTIAL (CI gate PASS, R² gate FAIL)
3. Step 6b reflection: LLM self-assessment
4. Decision: SUPERSEDED (behavioral assumptions invalid, recovery not possible)
5. New direction: h-e1-v2 → Phase 2A-Dialogue

---
*Superseded at: 2026-03-23T07:15:00Z*
*For cross-phase reference in Phase 2A-Dialogue*
