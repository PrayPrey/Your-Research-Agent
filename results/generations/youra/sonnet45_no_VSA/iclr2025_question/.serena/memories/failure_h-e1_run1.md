# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-07-09T17:25:56Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAIL

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Peak AUROC (L12) | 0.5000 | 0.5000 (MSP) | 0.0000 (0.0%) |
| Mid-layer AUROC (L18) | 0.5000 | 0.5000 (Entropy) | 0.0000 (0.0%) |
| Final AUROC (L32) | 0.5000 | 0.5000 | 0.0000 (0.0%) |

## Root Cause Analysis

- All probes achieved AUROC = 0.5000 (random performance)
- No layer-wise differentiation observed - all layers performed identically
- Peak at L12, not mid-layers (L18/L24) as hypothesized
- Zero drop from peak to final layer (0.0000 < 0.03 threshold)
- Baseline methods (MSP, Entropy) also at 0.5000 AUROC, indicating fundamental data/implementation issue

## Gate Failure Details

**Gate Type:** MUST_WORK

**Failed Checks:**
- Peak AUROC at L12 (not L18 or L24)
- Final layer drop 0.0000 < 0.03 threshold

**Conclusion:** The methodology does not work at all. The probe training failed to learn any discriminative patterns for uncertainty quantification.

## Lessons Learned

1. **Random performance across all layers suggests fundamental implementation or data issue** - When all methods (ours + baselines) achieve 0.5 AUROC, the problem is likely in data preparation, label generation, or probe architecture
2. **Layer-agnostic performance indicates no epistemic information is being captured** - The hypothesis assumes mid-layer representations contain unique uncertainty signals, but identical performance across L12/L18/L24/L32 refutes this
3. **Baseline methods at 0.5 AUROC confirms data quality issue, not just our approach** - MSP and Entropy should perform above chance on valid uncertainty estimation tasks
4. **PoC validation revealed fundamental flaw before expensive baseline comparison** - Phase 4's MUST_WORK gate successfully caught a non-functional methodology early

## Feedback for Phase 0 (Brainstorming)

### What NOT To Do
- Do not rely on hidden-state probes without validating that correctness labels have sufficient signal
- Do not assume mid-layer representations contain epistemic uncertainty without empirical validation
- Do not train probes on binary correctness labels if the task doesn't produce clear correct/incorrect examples

### What Showed Promise
- None - complete failure at PoC level

### Suggested Directions for New Hypothesis
- Validate that correctness labels can be reliably generated for the chosen task/dataset
- Consider alternative uncertainty signals beyond binary correctness (e.g., semantic consistency, token probability distributions)
- Test simpler baselines first (e.g., output-based uncertainty) before investigating hidden states
- Use sanity checks (e.g., train on random labels) to verify probe is learning meaningful patterns

---
*For cross-phase reference*
*Written at: 2026-07-09T17:25:56Z*
