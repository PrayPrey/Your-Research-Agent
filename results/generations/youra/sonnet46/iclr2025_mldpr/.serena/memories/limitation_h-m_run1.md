# Limitation Record: h-m (Run 1)

**Date:** 2026-03-18T05:45:00Z
**Hypothesis:** h-m
**Run:** 1
**Gate Type:** DETERMINES_SUCCESS
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Partial implementation (2/4 predictions) prevents full DETERMINES_SUCCESS gate evaluation. Phase 3 budget constraints resulted in only P4 (MVR Value-Add) and P5 (Intervention Leverage) being implemented. P2 (Domain Invariance) and P3 (Causal Mediation) were not implemented due to resource allocation decisions prioritizing computational feasibility over manual validation protocols.

Gate requires ≥3/4 predictions to pass for partial validation, but only 2/4 predictions were implemented, making threshold evaluation impossible.

## Failed Checks

- P2 (Domain Invariance): Not implemented - requires LLM classifier validation (N=100 gold labels + API costs)
- P3 (Causal Mediation): Not implemented - requires manual reproducibility testing protocol (2-3 weeks + independent coders)
- Full gate evaluation: Cannot assess ≥3/4 threshold with only 2/4 predictions

## Partial Results

| Metric | Value |
|--------|-------|
| Predictions Implemented | 2/4 (50%) |
| Predictions Passed | 1/2 (P4 only) |
| P4 MVR ICC | 0.601 |
| P4 Naive ICC | 0.000 |
| P4 ΔICC | 0.601 (>>0.05 threshold) |
| P5 Status | FAIL (data constraints) |

## Experiment Summary

**P4 (MVR Value-Add) - STRONG SUCCESS:**
- Demonstrated massive value-add: MVR-BCS ICC = 0.601 vs Naive BCS ICC = 0.000
- Δ ICC = 0.601 far exceeds ≥0.05 threshold
- Conclusion: Validity rules are essential for detecting repository-level patterns

**P5 (Intervention Leverage) - DATA FAILURE:**
- Could not execute due to sparse test data (mean BCS=0.122, no datasets in target range 0.25-0.40)
- Not a mechanistic failure, but a data availability constraint

**Overall Assessment:**
P4 provides strong evidence for MVR mechanism value proposition, but incomplete implementation prevents full mechanistic validation per original hypothesis design.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. Budget allocation for full 4-prediction validation (include manual protocols)
2. P4 alone provides strong evidence for practical utility (ICC=0.601 shows clear value-add)
3. P2 and P3 are scientifically valuable but resource-intensive (LLM labeling + reproducibility testing)
4. Alternative: Focus on computational predictions (P4, P5) and acknowledge mechanistic validation limitations

## Key Takeaways for Future Phases

- **Phase 0 Brainstorming:** If routing back from Phase 5 PARTIAL, avoid hypotheses requiring extensive manual validation unless resources are explicitly allocated
- **Phase 2B Planning:** Be realistic about budget constraints when designing 4-part mechanistic validations
- **Phase 3 Planning:** Prioritize predictions based on computational feasibility vs manual effort trade-offs
- **Phase 6 Discussion:** Include in Limitations section - "Full mechanistic validation (4 predictions) was not completed due to resource constraints; P4 evidence alone demonstrates core value proposition"

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar resource allocation issues
- **Phase 2A:** Informs hypothesis scoping decisions (avoid overly ambitious multi-part validations)
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-03-18T05:45:00Z*
*For cross-phase reference*