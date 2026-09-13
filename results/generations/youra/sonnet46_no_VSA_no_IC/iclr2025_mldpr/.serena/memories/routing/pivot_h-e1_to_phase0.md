# Routing Decision: h-e1 → Phase 0

**Date:** 2026-08-21T08:41:30Z
**Hypothesis:** h-e1 (H-CoVReuse-v1)
**Reflection Outcome:** ROUTED_TO_PHASE_0
**Gate:** MUST_WORK FAIL

## Decision
h-e1 routed to Phase 0 (hypothesis redesign) after MUST_WORK gate FAIL.
Spearman rho = -0.2841 (negative — opposite of hypothesis direction).
High-reuse benchmarks show LOWER CoV, not higher (benchmark saturation effect).

## Next Action
Phase 0 brainstorm to redesign hypothesis. Suggested directions:
1. Invert: high-reuse → lower CoV (saturation/Goodhart)
2. Score-ceiling proximity as CoV predictor
3. Temporal CoV dynamics within a benchmark over publication years
