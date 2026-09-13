# Phase 4.5 Synthesis Results

Date: 2026-08-05
Research: Layer-Wise Logit-Lens UQ for Hallucination (v2) — H-LayerLensUQ-v2

## Key Outcomes
- Predictions supported: 0/4 directly tested (P1-P4 all INCONCLUSIVE — dependents h-m1/h-m2/h-m3/h-c1 BLOCKED, never ran); existence premise SUPPORTED 6/6 cells (HIGH confidence)
- Refined core statement: intermediate-layer logit-lens statistics are class-separable in all 6 model x dataset cells (selection-split corrected AUROC 0.6092-0.7011, winners at L28-31) and beat the within-sweep final-layer entropy baseline in all 6 (margins +0.0035 to +0.130); test-split rescue, transfer, and fusion remain unmeasured
- Main theoretical contribution: first training-free AUROC evidence for raw logit-lens per-layer uncertainty statistics as hallucination scores, incl. adjacent-layer KL as detection signal (dominant in 3/6 cells); plus methodological finding that cross-protocol numeric anchors are invalid (0.5186 vs 0.5928 same cell, direction transfers, magnitude does not)
- Critical limitation: all AUROCs selection-split, single seed, no CIs; locked test splits never evaluated (A4 unverified); mechanism step 3 (tuning-severity ordering) descriptively contradicted — llama3-instruct largest TriviaQA depth margin (+0.130)

## Lessons for Future Pipelines
- Provenance-audit any numeric anchor before adopting it as a halt gate; gate only on within-protocol quantities (A2-v2 pattern: identity-verified cache reuse + within-sweep baselines + descriptive-only cross-run reports)
- A MUST_WORK PARTIAL that consumes the loop budget can leave dependent hypotheses permanently unexecuted — the highest-value follow-ups (h-m1/h-m2/h-m3/h-c1) are zero-GPU from finalized caches in h-e1-v2/results/
- Selection-split winners to freeze for any test-split evaluation are recorded in 045_validated_hypothesis.md section 5.3

## Output
- 045_validated_hypothesis.md (single source for Phase 6; Phase 5 skipped by config)
- verification_state.yaml: synthesis_completed=true, 2026-08-05T11:14:32+00:00
